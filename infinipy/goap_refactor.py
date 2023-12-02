from typing import List, Dict
import copy
from infinipy.stateblock import StateBlock
import uuid

from infinipy.statement import Statement,CompositeStatement
from infinipy.transformer import Transformer,CompositeTransformer
from infinipy.affordance import Affordance
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union, Tuple, Set
from datetime import datetime
from infinipy.goap_logger import GOAPLogger
from itertools import combinations
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
        print(goal[0].force_true(entity))
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
    

    def find_terminal_affordances(self, goal: Union[Tuple[CompositeStatement, bool], Tuple[Statement, bool]], entity: StateBlock) -> Tuple[List[Tuple[Affordance, int]], List[List[Affordance]]]:
        terminal_affordances: List[Tuple[Affordance, int]] = []
        partial_affordances: List[Affordance] = []
        

        goal_dict = self.get_filtered_subgoals(goal, entity)
        goal_substatements = set(stmt["statement"] for stmt in goal_dict["sub_statements"])

        for affordance in self.affordances:
            consequence_substatements = set()
            transformations_dict_list = affordance.force_consequence_true(entity)
            for composite_transformer in transformations_dict_list:
                for transformer in composite_transformer:
                    for consequence in transformer:
                        consequence_substatements |= set(substmt["statement"] for substmt in consequence["sub_statements"] if "sub_statements" in consequence)

            if consequence_substatements == goal_substatements:
                terminal_affordances.append((affordance, len(goal_substatements)))
            elif consequence_substatements:
                partial_affordances.append(affordance)

        valid_partial_combinations = self.find_partial_affordances(partial_affordances, goal_substatements, entity)

        # Logging
        self.logger.log_partial_affordance_found([aff.name for aff in partial_affordances])
        self.logger.log_combined_partial_affordances([[aff.name for aff in combo] for combo in valid_partial_combinations])

        return terminal_affordances, valid_partial_combinations
    
    def find_partial_affordances(self, partial_affordances: List[Affordance], goal_substatements: Set[str], entity: StateBlock) -> List[List[Affordance]]:
        valid_partial_combinations = []

        # Iterate through all possible combination lengths
        for i in range(1, len(partial_affordances) + 1):
            # Generate combinations of partial affordances
            for combo in combinations(partial_affordances, i):
                combined_substatements = set()

                # Collect sub-statements from all affordances in the combination
                for aff in combo:
                    aff_consequences = aff.force_consequence_true(entity)
                    for consequence_list in aff_consequences:
                        for consequence_dict in consequence_list:
                            if "sub_statements" in consequence_dict:
                                combined_substatements |= set(substmt["statement"] for substmt in consequence_dict["sub_statements"])

                # Check if the combination covers all goal sub-statements
                if combined_substatements == goal_substatements:
                    valid_partial_combinations.append(list(combo))

        return valid_partial_combinations

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
            plan_id = uuid.uuid4()
            self.ongoing_plans[plan_id] = []

        if depth > 10:
            self.logger.log_recursion_limit_reached(goal[0].name, depth, entity)
            return applied_actions

        self.logger.log_achieve_goal_start(goal[0].name, entity, depth)
        if self.is_goal_achieved(goal, entity):
            self.logger.log_goal_already_achieved(goal[0].name, entity, depth)
            return applied_actions

        terminal_affordances, partial_affordance_combinations = self.find_terminal_affordances(goal, entity)

        # Try terminal affordances first
        for affordance, _ in terminal_affordances:
            if self.try_apply_affordance(affordance, goal, entity, applied_actions, depth, plan_id):
                return applied_actions

        # Try combinations of partial affordances
        for partial_combo in partial_affordance_combinations:
            combo_result = self.try_apply_affordance_combination(partial_combo, goal, entity, applied_actions, depth, plan_id)
            if combo_result is not None:
                return combo_result

        self.logger.log_achieve_goal_end(goal[0].name, entity, depth, applied_actions)
        return applied_actions

    def try_apply_affordance(self, affordance: Affordance, goal: Union[Tuple[CompositeStatement, bool], Tuple[Statement, bool]], entity: StateBlock, applied_actions: List[Affordance], depth: int, plan_id) -> bool:
        if affordance not in self.ongoing_plans[plan_id]:
            self.ongoing_plans[plan_id].append(affordance)
            applied_actions.append(affordance)
            self.logger.log_applying_affordance(affordance, entity, depth)
            if not affordance.is_applicable(entity):
                for subgoal_name in self.find_subgoals_for_affordance(affordance, entity):
                    subgoal_statement = self.prerequisites[subgoal_name]
                    if not self.achieve_goal((subgoal_statement, True), entity, applied_actions, depth + 1, plan_id):
                        return False
            return self.is_goal_achieved(goal, entity)
        return False

    def try_apply_affordance_combination(self, partial_combo: List[Affordance], goal: Union[Tuple[CompositeStatement, bool], Tuple[Statement, bool]], entity: StateBlock, applied_actions: List[Affordance], depth: int, plan_id) -> Optional[List[Affordance]]:
        combo_actions = []
        for affordance in partial_combo:
            if not self.try_apply_affordance(affordance, goal, entity, combo_actions, depth, plan_id):
                # If any affordance in the combination fails, revert the applied actions
                for a in combo_actions:
                    self.ongoing_plans[plan_id].remove(a)
                return None
        if self.is_goal_achieved(goal, entity):
            applied_actions.extend(combo_actions)  # Add successful combo actions to applied actions
            return applied_actions
        return None
    
    def print_reasoning(self):
        self.logger.print_plan()

    


