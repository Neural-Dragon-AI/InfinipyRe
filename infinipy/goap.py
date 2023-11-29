from typing import List, Dict
import copy
from infinipy.stateblock import StateBlock
import uuid

from infinipy.statement import Statement,CompositeStatement
from infinipy.transformer import Transformer,CompositeTransformer
from infinipy.affordance import Affordance
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union, Tuple

class GOAPPlanner:
    """
    A class for Goal-Oriented Action Planning (GOAP) in a state-based system.

    Attributes:
        affordances (List[Affordance]): A list of all possible affordances (actions) in the system.
        prerequisites (Dict[str, Statement]): A mapping from statement names to Statement objects, representing prerequisites for affordances.
    """

    def __init__(self, affordances: List[Affordance]):
        """
        Initialize the GOAPPlanner with affordances and their prerequisites.

        Args:
            affordances (List[Affordance]): The list of all affordances in the system.
            prerequisites (Dict[str, Statement]): The mapping of statement names to Statement objects.
        """
        self.affordances = affordances
        self.prerequisites = self.extract_prerequisites(affordances)
        self.convert_dict={"AND": True, "AND NOT":False}
        self.planning_steps = []

    def update_planning_step(self, message: str):
        """
        Update the planning steps with a new message.

        Args:
            message (str): The message to add to the planning steps.
        """
        self.planning_steps.append(message)

    def get_and_clear_planning_steps(self) -> List[str]:
        """
        Retrieve and clear the planning steps.

        Returns:
            List[str]: The list of planning steps.
        """
        steps = self.planning_steps[:]
        self.planning_steps = []
        return steps    

    def extract_prerequisites(self, affordances: List[Affordance]) -> Dict[str, Statement]:
        """
        Extract prerequisites from a list of affordances.

        This method goes through each affordance and collects its prerequisites. It creates a dictionary
        mapping each prerequisite's name to the corresponding Statement object.

        Args:
            affordances (List[Affordance]): A list of affordances from which prerequisites are to be extracted.

        Returns:
            Dict[str, Statement]: A dictionary mapping the names of prerequisites to their corresponding Statement objects.
        """
        prerequisites = {}
        for affordance in affordances:
            for prerequisite in affordance.prerequisites:
                prerequisites[prerequisite.name] = prerequisite
                #each of htis is a composite statement so we now loop through the substatements and add all of them to the prerequisites
                for substatement in prerequisite.conditions:
                    #add the statement to the prerequisites
                    #pack the statement and condition into a composite statement
                    compstat = CompositeStatement([substatement])
                    prerequisites[compstat.name] = compstat
                    prerequisites[substatement[0].name] = substatement[0]
         
                 
        return prerequisites
    
    def get_filtered_subgoals(self,goal: Union[Tuple[CompositeStatement,bool],Tuple[Statement,bool]],entity: StateBlock) -> List[Tuple[Statement,bool]]:
         # currently only taking the first true_dict would be worth to explore the full list in some proper examples
        goal_dict_raw= goal[0].force_true(entity)[0]
        goal_dict = copy.deepcopy(goal_dict_raw)
        
        #selects the subset of goa that are not true right now
        for substatement in goal_dict_raw["sub_statements"]:
            print(substatement["statement"],substatement["result"])
            if substatement["result"] == self.prerequisites[substatement["statement"]].apply(entity)[1]["result"]:
                #pop the substatement if it is already true
                print(f"removing the statement {substatement['statement']} from the goal because it is  {substatement['result']} and it needs to be {self.prerequisites[substatement['statement']].apply(entity)[1]['result']} in order to apply the action {goal[0].name}")
                goal_dict["sub_statements"].remove(substatement)
            else:
                print(f"the statement {substatement['statement']} is {self.prerequisites[substatement['statement']].apply(entity)[1]['result']}  , but it needs to be {substatement['result']} in order to apply the action {goal[0].name}")
        print(len(goal_dict_raw["sub_statements"]),len(goal_dict["sub_statements"]))
        return goal_dict


    def find_terminal_affordances(self, goal: Union[Tuple[CompositeStatement,bool],Tuple[Statement,bool]], entity: StateBlock) -> List[Affordance]:
        """
        Find affordances that can directly or indirectly achieve the specified goal.

        Args:
            goal (CompositeStatement): The goal statement to be achieved as a composite statement or a statement and boolean value.
            entity: The entity over which the final goal is specified

        Returns:
            List[Affordance]: A list of affordances that can achieve the goal.
        """
        terminal_affordances = []
        partial_affordances = []
        goal_dict = self.get_filtered_subgoals(goal,entity)
        num_substatements = len(goal_dict["sub_statements"])
        #create a set of all the substatements in the goal dict
        matched_substatements_set = set()
        for affordance in self.affordances:
                num_matching_substatements = 0
                matching_substatemtents = []
                                
                # print(f"the goal {goal[0].name} is a composite statement")
                #the goals is a composite statement, same as the consequence object of the affordance so we can directly check if the goal is achieved
                #first loop is for the different composite transformers of the affordance 
                # the second loop is for the different transformers of each composite transformer
                # the third loops are the different consequences of each transformer
                # the fourth loop is for the different substatements of each consequence (should not be necessary if goal is a composite statement)
                transformations_dict_list = affordance.force_consequence_true(entity)
                for composite_transformer in transformations_dict_list:
                    for transformer in composite_transformer:
                        for consequence in transformer:
                            #tries to match the whole composite statement with the conseuquence
                            if consequence["name"] == goal[0].name and consequence["result"] == goal[1]:
                                print(consequence["name"],goal[0].name,num_substatements)
                                terminal_affordances.append((affordance,num_substatements))
                            else:
                                print("triny to match substatements")
                                #tries to match the substatements of the composite statement with the substatements of the consequence
                                for substatement in consequence["sub_statements"]:
                                    for goal_substatement in goal_dict["sub_statements"]:
                                    
                                        if substatement["statement"] == goal_substatement["statement"] and substatement["result"] == goal_substatement["result"]:
                                            num_matching_substatements += 1
                                            matching_substatemtents.append(substatement)
                                            matched_substatements_set.add(substatement["statement"])
                if num_matching_substatements == num_substatements:
                    terminal_affordances.append((affordance,num_substatements)) 
                    print("found a terminal affordance",affordance.name)
                    
                elif num_matching_substatements > 0:
                    partial_affordances.append((affordance,num_matching_substatements))
                    print("found a partial affordance",affordance.name)
                    for substatement in matching_substatemtents:
                        print(f"the follwoing substatemtens match {substatement}")
        if len(matched_substatements_set) < num_substatements and len(terminal_affordances) == 0:
            print("the goal is not achievable")
            return [],[]    
                                                                
        return terminal_affordances,partial_affordances
    


    def find_subgoals_for_affordance(self, affordance: Affordance, entity: StateBlock) -> List[str]:
        """
        Identify subgoals that need to be achieved to make an action applicable.

        Args:
            action (Affordance): The affordance whose applicability needs to be checked.
            StateBlock (StateBlock): The StateBlock object representing the current state.

        Returns:
            List[str]: A list of names of subgoal statements.
        """
        subgoals = []
        why_not_applicable = affordance.why_not_applicable(entity)
        for reason in why_not_applicable:
            subgoals.append(reason[0])
        return subgoals

    def is_goal_achieved(self, goal: Union[Tuple[CompositeStatement,bool],Tuple[Statement,bool]], entity: StateBlock) -> bool:
        """
        Check if the goal is achieved for the given StateBlock state.

        Args:
            goal (CompositeStatement): The goal to be checked.
            StateBlock (StateBlock): The StateBlock object representing the current state.

        Returns:
            bool: True if the goal is achieved, False otherwise.
        """
        return goal[0].apply(entity)["result"] == goal[1]

    

    def achieve_goal(self, goal: Union[Tuple[CompositeStatement, bool], Tuple[Statement, bool]], entity: StateBlock, applied_actions: List[Affordance] = [], depth: int = 0) -> List[Affordance]:
        """
        Recursively achieve the specified goal using terminal affordances.

        Args:
            goal (Union[Tuple[CompositeStatement, bool], Tuple[Statement, bool]]): The goal or subgoal to be achieved.
            entity (StateBlock): The entity on which the goal is being applied.
            applied_actions (List[Affordance]): Accumulator for actions applied in the process of achieving the goal.
            depth (int): Depth of recursion to prevent infinite loops.

        Returns:
            List[Affordance]: A sequence of affordances that achieve the goal.
        """
        if depth > 10:  # Avoid infinite recursion
            return applied_actions

        # Check if the goal is already achieved
        if self.is_goal_achieved(goal, entity):
            return applied_actions

        # Find terminal affordances that can achieve the goal
        terminal_affordances, _ = self.find_terminal_affordances(goal, entity)
        for affordance, _ in terminal_affordances:
            # Apply the affordance and update the entity's state
            affordance.apply(entity)
            applied_actions.append(affordance)
            
            # Check if the goal is achieved after applying the affordance
            if self.is_goal_achieved(goal, entity):
                return applied_actions
            
            # Otherwise, find the next subgoals and recurse
            next_subgoals = self.find_subgoals_for_affordance(affordance, entity)
            for subgoal_name in next_subgoals:
                subgoal_statement = self.prerequisites[subgoal_name]
                result = self.achieve_goal((subgoal_statement, True), entity, applied_actions, depth + 1)
                if self.is_goal_achieved(goal, entity):
                    return result

        return applied_actions
