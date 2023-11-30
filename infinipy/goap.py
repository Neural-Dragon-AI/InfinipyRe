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
from infinipy.goap_logger import GOAPLogger

class GOAPPlanner:
    def __init__(self, affordances: List[Affordance]):
        self.affordances = affordances
        self.ongoing_plans = {}  # Initialize the ongoing plans dictionary
        self.logger = GOAPLogger()  # Initialize the logger
        self.prerequisites = self.extract_prerequisites(affordances)
        

    def extract_prerequisites(self, affordances: List[Affordance]) -> Dict[str, Statement]:
        prerequisites = {}
        total_prerequisites = 0
        for affordance in affordances:
            for prerequisite in affordance.prerequisites:
                prerequisites[prerequisite.name] = prerequisite
                total_prerequisites += 1
                for substatement in prerequisite.conditions:
                    compstat = CompositeStatement([substatement])
                    prerequisites[compstat.name] = compstat
                    prerequisites[substatement[0].name] = substatement[0]
                    total_prerequisites += 1
                    self.logger.log_create_composite_statement(affordance.name, prerequisite.name, compstat.name)

        self.logger.log_extract_prerequisites(len(affordances), total_prerequisites)
        return prerequisites

    def get_filtered_subgoals(self, goal: Union[Tuple[CompositeStatement, bool], Tuple[Statement, bool]], entity: StateBlock) -> List[Tuple[Statement, bool]]:
        goal_dict_raw = goal[0].force_true(entity)[0]
        goal_dict = copy.deepcopy(goal_dict_raw)

        satisfied_subgoals = []
        target_subgoals = []

        for substatement in goal_dict_raw["sub_statements"]:
            current_result = self.prerequisites[substatement["statement"]].apply(entity)[1]["result"]
            if substatement["result"] == current_result:
                goal_dict["sub_statements"].remove(substatement)
                satisfied_subgoals.append(substatement["statement"])
            else:
                target_subgoals.append(substatement["statement"])

        self.logger.log_filtered_subgoals(goal[0].name, entity, satisfied_subgoals, target_subgoals)
        return goal_dict
    
    def find_terminal_affordances(self, goal: Union[Tuple[CompositeStatement, bool], Tuple[Statement, bool]], entity: StateBlock) -> List[Tuple[List[Tuple[Affordance, int]], List[Tuple[Affordance, int]]]]:

        terminal_affordances = []
        partial_affordances = []
        goal_dict = self.get_filtered_subgoals(goal, entity)
        num_substatements = len(goal_dict["sub_statements"])
        matched_substatements_set = set()

        for affordance in self.affordances:
            num_matching_substatements = 0
            matching_substatements = []

            transformations_dict_list = affordance.force_consequence_true(entity)
            for composite_transformer in transformations_dict_list:
                for transformer in composite_transformer:
                    for consequence in transformer:
                        if consequence["name"] == goal[0].name and consequence["result"] == goal[1]:
                            terminal_affordances.append((affordance, num_substatements))
                            # Log each terminal affordance match
                            self.logger.log_terminal_affordances(goal[0].name, entity, [affordance], [])
                        else:
                            for substatement in consequence["sub_statements"]:
                                for goal_substatement in goal_dict["sub_statements"]:
                                    if substatement["statement"] == goal_substatement["statement"] and substatement["result"] == goal_substatement["result"]:
                                        num_matching_substatements += 1
                                        matching_substatements.append(substatement)
                                        matched_substatements_set.add(substatement["statement"])

            if num_matching_substatements == num_substatements:
                terminal_affordances.append((affordance, num_substatements))
                # Log the complete terminal affordance found
                self.logger.log_terminal_affordances(goal[0].name, entity, [affordance], [])
            elif num_matching_substatements > 0:
                partial_affordances.append((affordance, num_matching_substatements))
                # Log the partial affordance found
                self.logger.log_terminal_affordances(goal[0].name, entity, [], [affordance])

        if len(matched_substatements_set) < num_substatements and len(terminal_affordances) == 0:
            # Log when a goal is not achievable
            self.logger.log_terminal_affordances(goal[0].name, entity, [], [])

        return terminal_affordances, partial_affordances

    def find_subgoals_for_affordance(self, affordance: Affordance, entity: StateBlock) -> List[str]:
        subgoals = []
        why_not_applicable = affordance.why_not_applicable(entity)

        # Replace the initial logging call with the specialized logger method
        self.logger.log_evaluating_affordance_applicability(affordance.name, entity.name)

        for reason in why_not_applicable:
            subgoals.append(reason[0])
            # Replace the logging call for each subgoal identification
            self.logger.log_identifying_subgoal_for_affordance(affordance.name, reason[0], entity.name)

        return subgoals

    def is_goal_achieved(self, goal: Union[Tuple[CompositeStatement, bool], Tuple[Statement, bool]], entity: StateBlock) -> bool:
        goal_achieved = goal[0].apply(entity)["result"] == goal[1]

        # Use the specialized logging method for goal achievement evaluation
        self.logger.log_goal_achieved(goal[0].name, entity, goal_achieved)

        return goal_achieved


    def achieve_goal(self, goal: Union[Tuple[CompositeStatement, bool], Tuple[Statement, bool]], entity: StateBlock, applied_actions: List[Affordance] = [], depth: int = 0, plan_id=None) -> List[Affordance]:
        if plan_id is None:
            plan_id = uuid.uuid4()  # Generate a unique ID for the plan
            self.ongoing_plans[plan_id] = []  # Initialize the plan entry

        if depth > 10:  # Avoid infinite recursion
            self.logger.log_recursion_limit_reached(goal[0].name, depth, entity)
            return applied_actions

        self.logger.log_achieve_goal_start(goal[0].name, entity, depth)
        if self.is_goal_achieved(goal, entity):
            self.logger.log_goal_already_achieved(goal[0].name, entity, depth)
            return applied_actions

        terminal_affordances, partial_affordances = self.find_terminal_affordances(goal, entity)
        for affordance_tuple in terminal_affordances + partial_affordances:
            affordance = affordance_tuple[0]
            if affordance not in self.ongoing_plans[plan_id]:  # Check if affordance is not already applied in this plan
                self.ongoing_plans[plan_id].append(affordance)
                applied_actions.append(affordance)
                self.logger.log_applying_affordance(affordance, entity, depth)

                if affordance.is_applicable(entity):  # Check if the affordance achieves the goal
                    self.logger.log_goal_achieved(goal[0].name, entity, True)
                    return applied_actions
                else:
                    next_subgoals = self.find_subgoals_for_affordance(affordance, entity)
                    for subgoal_name in next_subgoals:
                        subgoal_statement = self.prerequisites[subgoal_name]
                        result = self.achieve_goal((subgoal_statement, True), entity, applied_actions, depth + 1, plan_id)
                        if affordance.is_applicable(entity):  # Check again after subgoals
                            return result

        self.logger.log_achieve_goal_end(goal[0].name, entity, depth, applied_actions)
        return applied_actions
    
    def print_reasoning(self):
        self.logger.print_plan()

    


