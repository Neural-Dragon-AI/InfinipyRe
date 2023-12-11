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
        self.solutions= []
    
    def forward_solve(self, start_state: WorldStatement, goal_state: WorldStatement):
        """
        Finds a solution to reach the goal state from the start state.
        
        :param start_state: Starting WorldStatement.
        :param goal_state: Goal WorldStatement to achieve.
        """
        available_actions = start_state.available_actions(self.actions)
        self.recursive_solve(start_state, available_actions, goal_state)

    def backward_solve(self, end_state: WorldStatement, goal_state: WorldStatement):
        """
        Finds a backward solution from the current end state to a goal starting state.
        
        :param end_state: Current WorldStatement.
        :param goal_state: Goal WorldStatement to achieve.
        
        """

        current_option = Option(starting_dict=end_state.conditions)
        available_actions = end_state.available_actions(self.actions, reverse=True)
        self.backward_recursive_solve(current_option, available_actions, goal_state,end_state,[], visited_states=[end_state])
    
    def recursive_solve(self,current_state: WorldStatement, 
                    available_actions: List[Action], 
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
            return True

        # Recursive step: Try each available action
        for action in available_actions:
            print("Trying action:", action.name)
            new_option = Option(starting_dict=deepcopy(current_state.conditions))
            new_option.append(action)
            new_world = WorldStatement.from_dict(new_option.global_consequences)
            if any([visited_state.is_falsified_by(new_world) for visited_state in visited_states]):
                continue
            new_available_actions = new_world.available_actions(self.actions)
            
            # Recurse with the updated state and path
            if self.recursive_solve(new_world, new_available_actions, goal_state, current_path + [action], visited_states + [new_world]):
                self.terminal_world = new_world
                return True

        # Return False if no solution found in this path
        return False
    def backward_recursive_solve(self,
        current_option: Option, 
        available_actions: List[Action], 
        goal_state: WorldStatement,
        start_state:WorldStatement, 
        current_path: List[Action] = [],
        visited_states: List[WorldStatement] = [],
        max_depth: int = 10,  # Default maximum depth
      
    ):
        """
        Recursive function to find a backward solution from the current end state to a goal starting state.

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

        # Base case: Check if the global prerequisites of the current option satisfy the goal state
        global_prerequisites = WorldStatement.from_dict(current_option.global_prerequisites)
        global_consequences = WorldStatement.from_dict(current_option.global_consequences)
        if len(current_path) > 0 and goal_state.validates(global_prerequisites):
            print("Backward solution found:", " <- ".join([action.name for action in reversed(current_path)]))
            self.solutions.append(current_path)
            return False

        # Recursive step: Try each available action that leads to the current state
        for action in available_actions:
            print("Trying action:", action.name)
            new_option = deepcopy(current_option)
            new_option.prepend(action)
            new_world = WorldStatement.from_dict(new_option.global_prerequisites)
            if new_world.falsifies(global_consequences):
                print("State falsifies global consequences")
                print_conditions(new_world.conditions)
                continue
            if any([visited_state.validates(new_world) for visited_state in visited_states]):
                print("State already visited")
                print_conditions(new_world.conditions)
                continue
        
                    
            new_available_actions = new_world.available_actions(self.actions, reverse=True)  # Get actions leading to this state
            print("New available actions:", [action.name for action in new_available_actions])
            current_path = [action] + current_path
            print("Current path:", " <- ".join([action.name for action in reversed(current_path)]))
            if self.backward_recursive_solve(new_option, new_available_actions, goal_state,start_state, current_path, visited_states + [new_world], max_depth - 1):
                return True

        # Return False if no solution found in this path
        return False


