from typing import List, Dict
import copy
from infinipy.stateblock import StateBlock
import uuid

from infinipy.statement import Statement,CompositeStatement
from infinipy.transformer import Transformer,CompositeTransformer
from infinipy.affordance import Affordance
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union, Tuple
from datetime import datetime

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
        self.planning_log = []
        self.prerequisites = self.extract_prerequisites(affordances)
        self.convert_dict={"AND": True, "AND NOT":False}
        self.state_transition_log = []
        
        
    def log(self, step: str, details: Dict[str, Any], result: Optional[Any] = None):
        """
        Log information about a step in the planning process.

        Args:
            step (str): Description of the planning step.
            details (Dict[str, Any]): Detailed information about the step.
            result (Optional[Any]): The outcome or result of the step, if applicable.
        """
        log_entry = {
            'timestamp': datetime.now(),
            'step': step,
            'details': details,
            'result': result
        }
        self.planning_log.append(log_entry)

   

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
        total_prerequisites = 0
        for affordance in affordances:
            for prerequisite in affordance.prerequisites:
                prerequisites[prerequisite.name] = prerequisite
                total_prerequisites += 1
                # Each of this is a composite statement so we now loop through the substatements and add all of them to the prerequisites
                for substatement in prerequisite.conditions:
                    # Add the statement to the prerequisites
                    # Pack the statement and condition into a composite statement
                    compstat = CompositeStatement([substatement])
                    prerequisites[compstat.name] = compstat
                    prerequisites[substatement[0].name] = substatement[0]
                    total_prerequisites += 1
                    # Log the creation of a Composite version of a single statement
                    self.log("Creating Composite Statement", {"affordance": affordance.name, "prerequisite": prerequisite.name, "composite_statement": compstat.name})

        # Log the total count of affordances and prerequisites
        self.log("Extracting Prerequisites", {"total_affordances": len(affordances), "total_prerequisites": total_prerequisites})
        
        return prerequisites
    
    def get_filtered_subgoals(self, goal: Union[Tuple[CompositeStatement, bool], Tuple[Statement, bool]], entity: StateBlock) -> List[Tuple[Statement, bool]]:
        # Currently only taking the first true_dict, but in more complex cases, the full list might be explored
        goal_dict_raw = goal[0].force_true(entity)[0]
        goal_dict = copy.deepcopy(goal_dict_raw)

        satisfied_subgoals = []
        target_subgoals = []

        # Selects the subset of goal that are not true right now
        for substatement in goal_dict_raw["sub_statements"]:
            current_result = self.prerequisites[substatement["statement"]].apply(entity)[1]["result"]
            if substatement["result"] == current_result:
                # Remove the substatement if it is already true
                goal_dict["sub_statements"].remove(substatement)
                satisfied_subgoals.append(substatement["statement"])
            else:
                target_subgoals.append(substatement["statement"])

        # Log the current goal, satisfied constraints, and target subgoals
        self.log("Filtering Subgoals", {
            "current_goal": goal[0].name,
            "satisfied_subgoals": satisfied_subgoals,
            "target_subgoals": target_subgoals,
            "entity_name": entity.name
        })

        return goal_dict



    def find_terminal_affordances(self, goal: Union[Tuple[CompositeStatement, bool], Tuple[Statement, bool]], entity: StateBlock) -> List[Affordance]:
        terminal_affordances = []
        partial_affordances = []
        goal_dict = self.get_filtered_subgoals(goal, entity)
        num_substatements = len(goal_dict["sub_statements"])
        matched_substatements_set = set()

        # Log the initial state and goal
        self.log("Finding Terminal Affordances", {"entity_name": entity.name, "goal": goal[0].name, "goal_state": goal[1]})

        for affordance in self.affordances:
            num_matching_substatements = 0
            matching_substatements = []

            transformations_dict_list = affordance.force_consequence_true(entity)
            for composite_transformer in transformations_dict_list:
                for transformer in composite_transformer:
                    for consequence in transformer:
                        if consequence["name"] == goal[0].name and consequence["result"] == goal[1]:
                            terminal_affordances.append((affordance, num_substatements))
                            self.log("Terminal Affordance Match", {
                                "affordance": affordance.name, 
                                "consequence_matched": consequence["name"], 
                                "num_substatements_matched": num_substatements,
                                "entity_name": entity.name
                            })
                        else:
                            for substatement in consequence["sub_statements"]:
                                for goal_substatement in goal_dict["sub_statements"]:
                                    if substatement["statement"] == goal_substatement["statement"] and substatement["result"] == goal_substatement["result"]:
                                        num_matching_substatements += 1
                                        matching_substatements.append(substatement)
                                        matched_substatements_set.add(substatement["statement"])

            if num_matching_substatements == num_substatements:
                terminal_affordances.append((affordance, num_substatements))
                self.log("Complete Terminal Affordance Found", {"affordance": affordance.name, "matched_substatements": matching_substatements, "entity_name": entity.name})
            elif num_matching_substatements > 0:
                partial_affordances.append((affordance, num_matching_substatements))
                self.log("Partial Affordance Found", {"affordance": affordance.name, "matched_substatements": matching_substatements, "entity_name": entity.name})

        if len(matched_substatements_set) < num_substatements and len(terminal_affordances) == 0:
            self.log("Goal Not Achievable", {"goal": goal[0].name, "entity_name": entity.name})

        return terminal_affordances, partial_affordances

    


    def find_subgoals_for_affordance(self, affordance: Affordance, entity: StateBlock) -> List[str]:
        subgoals = []
        why_not_applicable = affordance.why_not_applicable(entity)

        # Log the initial state and the affordance being evaluated
        self.log("Evaluating Affordance Applicability", {"affordance": affordance.name, "entity_name": entity.name})

        for reason in why_not_applicable:
            subgoals.append(reason[0])
            # Log each reason why the affordance is not applicable
            self.log("Identifying Subgoal for Affordance", {
                "affordance": affordance.name, 
                "reason": reason, 
                "subgoal_identified": reason[0],
                "entity_name": entity.name
            })

        return subgoals


    def is_goal_achieved(self, goal: Union[Tuple[CompositeStatement, bool], Tuple[Statement, bool]], entity: StateBlock) -> bool:
        goal_achieved = goal[0].apply(entity)["result"] == goal[1]

        # Log the goal evaluation process
        self.log("Evaluating Goal Achievement", {
            "goal": goal[0].name, 
            "desired_state": goal[1], 
            "entity_name": entity.name,
            "goal_achieved": goal_achieved,
            "entity_name": entity.name

        })

        return goal_achieved


    def achieve_goal(self, goal: Union[Tuple[CompositeStatement, bool], Tuple[Statement, bool]], entity: StateBlock, applied_actions: List[Affordance] = [], depth: int = 0) -> List[Affordance]:
        if depth > 10:  # Avoid infinite recursion
            self.log("Recursion Limit Reached", {"goal": goal[0].name, "depth": depth, "entity_name": entity.name})
            return applied_actions

        # Log the start of a new recursion level
        self.log("Achieving Goal - Recursion Start", {"goal": goal[0].name, "depth": depth,"entity_name": entity.name})

        if self.is_goal_achieved(goal, entity):
            self.log("Goal Already Achieved", {"goal": goal[0].name, "depth": depth, "entity_name": entity.name})
            return applied_actions

        terminal_affordances, _ = self.find_terminal_affordances(goal, entity)
        for affordance, _ in terminal_affordances:
            affordance.apply(entity)
            applied_actions.append(affordance)

            # Log the application of an affordance
            self.log("Applying Affordance", {"affordance": affordance.name, "depth": depth, "entity_name": entity.name})

            if self.is_goal_achieved(goal, entity):
                self.log("Goal Achieved", {"goal": goal[0].name, "depth": depth, "entity_name": entity.name})
                return applied_actions

            next_subgoals = self.find_subgoals_for_affordance(affordance, entity)
            for subgoal_name in next_subgoals:
                subgoal_statement = self.prerequisites[subgoal_name]
                result = self.achieve_goal((subgoal_statement, True), entity, applied_actions, depth + 1)
                if self.is_goal_achieved(goal, entity):
                    return result

        # Log the end of a recursion level if no affordance achieved the goal
        self.log("Achieving Goal - Recursion End", {"goal": goal[0].name, "depth": depth, "entity_name": entity.name, "applied_actions": [a.name for a in applied_actions]})
        
        return applied_actions
    
    def print_reasoning(self):
        """
        Print an advanced and detailed report of the planning process, utilizing the knowledge of the algorithm and log data.
        """
        report = ["GOAP Planning Process Report\n", "="*50 + "\n"]

        for log_entry in self.planning_log:
            timestamp = log_entry['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            step = log_entry['step']
            details = log_entry['details']

            entry = f"Time: {timestamp}\nStep: {step}\n"

            # Extracting relevant information based on the step
            if step == "Creating Composite Statement":
                entry += f"Affordance: {details['affordance']}, Prerequisite: {details['prerequisite']}, Composite Statement Created: {details['composite_statement']}\n"

            elif step == "Extracting Prerequisites":
                entry += f"Total Affordances Analyzed: {details['total_affordances']}, Total Prerequisites Extracted: {details['total_prerequisites']}\n"

            elif step == "Filtering Subgoals":
                entry += f"Goal: {details['current_goal']}, Satisfied Subgoals: {', '.join(details['satisfied_subgoals'])}, Target Subgoals: {', '.join(details['target_subgoals'])}, Entity: {details['entity_name']}\n"

            elif step == "Finding Terminal Affordances":
                entry += f"Entity: {details['entity_name']}, Goal: {details['goal']}, Goal State: {details['goal_state']}\n"

            elif step == "Evaluating Affordance Applicability":
                entry += f"Affordance: {details['affordance']}, Entity: {details['entity_name']}\n"

            elif step == "Identifying Subgoal for Affordance":
                entry += f"Affordance: {details['affordance']}, Reason for Non-Applicability: {details['reason']}, Subgoal Identified: {details['subgoal_identified']}, Entity: {details['entity_name']}\n"

            elif step == "Evaluating Goal Achievement":
                goal_achieved_str = 'Yes' if details['goal_achieved'] else 'No'
                entry += f"Goal: {details['goal']}, Desired State: {details['desired_state']}, Entity: {details['entity_name']}, Goal Achieved: {goal_achieved_str}\n"

            elif step == "Achieving Goal - Recursion Start" or step == "Achieving Goal - Recursion End":
                entry += f"Goal: {details['goal']}, Recursion Depth: {details['depth']}, Entity: {details['entity_name']}\n"

            elif step == "Recursion Limit Reached":
                entry += f"Goal: {details['goal']}, Depth: {details['depth']}, Entity: {details['entity_name']}\n"

            # Adding a separator for readability
            entry += "-"*50 + "\n"
            report.append(entry)
        # Adding the final plan summary
        final_plan_summary = ["\nFinal Plan Summary\n", "="*30 + "\n"]
        if self.planning_log:
            last_log = self.planning_log[-1]
            if last_log['step'].startswith("Achieving Goal - Recursion End"):
                details = last_log['details']
                final_goal = details['goal']
                actions_taken = [log['details']['affordance'] for log in self.planning_log if log['step'] == "Applying Affordance"]
                actions_taken.reverse()

                final_plan_summary.append(f"Goal: {final_goal}\n")
                final_plan_summary.append(f"Target Entity: {details['entity_name']}\n")
                final_plan_summary.append("Actions Taken to Achieve Goal:\n")
                for action in actions_taken:
                    final_plan_summary.append(f" - {action}\n")
            else:
                final_plan_summary.append("The goal was not achieved within the planning process.\n")

        # Append the final plan summary to the report
        report += final_plan_summary
        full_report = '\n'.join(report)
        print(full_report)

