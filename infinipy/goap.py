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
from copy import deepcopy
from infinipy.actions import Action
from infinipy.options import Option
from infinipy.worldstatement import WorldStatement


def print_conditions(cond_dict : dict, with_key = False):
    for key,value in cond_dict.items():
        if with_key:
            print(key)
        print(value.name)


class GOAP:
    def __init__(self, actions: List[Action]):
        """
        Initializes the GOAP class with a list of actions.
        
        :param actions: List of actions.
        """
        self.actions = actions
        self.terminal_world = None
        self.foward_solutions = []
        self.backward_solutions= []
    
    def forward_solve(self, start_state: WorldStatement, goal_state: WorldStatement):
        """
        Finds a solution to reach the goal state from the start state.
        
        :param start_state: Starting WorldStatement.
        :param goal_state: Goal WorldStatement to achieve.
        """
        self.recursive_solve(start_state, goal_state)

    def backward_solve(self, start_state: WorldStatement, goal_state: WorldStatement):
        """
        Finds a backward solution from the current end state to a goal starting state.
        
        :param end_state: Current WorldStatement.
        :param goal_state: Goal WorldStatement to achieve.
        
        """

        # current_option = Option(starting_dict=goal_state.conditions)
        # available_actions = goal_state.available_actions(self.actions, reverse=True)
        # print(f"Starting with the following available actions: {[action.name for action in available_actions]}")
        current_option = Option(starting_consequences=goal_state)
        self.backward_recursive_solve(current_option, start_state,goal_state,[], visited_states=[goal_state])
    
    def recursive_solve(self,
                    current_state: WorldStatement, 
                    goal_state: WorldStatement, 
                    current_path: List[Action] = [],
                    visited_states: List[WorldStatement] = [],):
        """
        Recursive function to find a solution to reach the goal state.
        
        :param current_state: Current WorldStatement.
        :param available_actions: List of available actions.
        :param goal_state: Goal WorldStatement to achieve.
        :param current_path: List of actions taken so far.
        """
        # Base case: Check if the goal is achieved
        if goal_state.is_validated_by(current_state):
            print("Solution found:", " -> ".join([action.name for action in current_path]))
            self.foward_solutions.append(current_path)
            self.terminal_world = current_state
            return True
        actions_pre_statements = [WorldStatement.from_dict(action.pre_dict) for action in self.actions]
        # find actions whose actions pre_statements is not falsified by the current state
        available_actions = [action for action,pre_statement in zip(self.actions,actions_pre_statements) if not current_state.falsifies(pre_statement)]
         
        # Recursive step: Try each available action
        for action in available_actions:
            print("Trying action:", action.name)
            new_option = Option(starting_consequences=current_state)
            new_option.append(action)
            new_world = new_option.global_consequences
            if any([visited_state.validates(new_world) for visited_state in visited_states]):
                continue
            
            # Recurse with the updated state and path
            if self.recursive_solve(new_world,
                                     goal_state, 
                                     current_path + [action], 
                                     visited_states + [new_world]):
                
                return True

        # Return False if no solution found in this path
        return False
    
    def backward_recursive_solve(self,
        current_option: Option, 
        start_state: WorldStatement,
        goal_state:WorldStatement, 
        current_path: List[Action] = [],
        visited_states: List[WorldStatement] = [],
        max_depth: int = 10,  # Default maximum depth
      
    ):
        """
        Recursive function to find a backward solution from the goal_state to the start_state.

        :param current_option: Current Option with actions.
        :param available_actions: List of available actions.
        :param goal_state: Goal WorldStatement to achieve.
        :param current_path: List of actions taken so far in reverse order.
        :param max_depth: Maximum depth of recursion allowed.
        """
        # Check if maximum recursion depth is reached
        if max_depth <= 0:
            print("Maximum recursion depth reached.")
            return False

        # Base case: Check if the global prerequisites of the current option are satisfied by the start state
        # global_prerequisites = WorldStatement.from_dict(current_option.global_prerequisites)
        # global_consequences = WorldStatement.from_dict(current_option.global_consequences)
        global_pre = current_option.global_prerequisites
        global_con = current_option.global_consequences
        
        if start_state.validates(global_pre):
            current_path = [action for action in reversed(current_option.actions)]
            print("Backward solution found:", " <- ".join([action.name for action in reversed(current_path)]))
            print(max_depth)
            self.backward_solutions.append([current_path])
            return False
        
 
        
        #available actionsa are actions that do not falsify the global prerequisites
        available_actions = [action for action in self.actions if not WorldStatement.from_dict(action.con_dict).falsifies(global_pre)]
        #availabe actions are actions that validate the global prerequisites
        # available_actions = [action for action in self.actions if WorldStatement.from_dict(action.con_dict).validates(global_pre)]
        # Recursive step: Try each available action that does not prevent arriving to the global_pre
        for action in available_actions:
            # print("Trying action:", action.name)
            new_option = copy.deepcopy(current_option)
            new_option.prepend(action)
            new_pre = new_option.global_prerequisites
            new_con = new_option.global_consequences
            if any([visited_state.validates(new_pre) for visited_state in visited_states]):
                continue

            

            if self.backward_recursive_solve(new_option, start_state,goal_state, current_path, visited_states + [new_pre, new_con], max_depth - 1):
                return False

        # Return False if no solution found in this path
        return False


