from infinipy.stateblock import StateBlock
import uuid

from infinipy.statement import Statement,CompositeStatement
from infinipy.transformer import Transformer,CompositeTransformer
from infinipy.affordance import Affordance
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union, Tuple
from infinipy.options import Option
from infinipy.worldstatement import WorldStatement
from infinipy.actions import Action



@dataclass
class Door(StateBlock):
    is_open: bool = False  # Attribute to indicate if the door is open
    is_locked: bool = False  # Attribute to indicate if the door is locked
    def __init__(self, key_id: str,is_open:bool,is_locked:bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_id = key_id  # Identifier of the key that can open the door
        self.is_open = is_open
        self.is_locked = is_locked

    def __post_init__(self):
        super().__post_init__()  # Call the post-init of StateBlock
        # Additional initialization can be added here if needed
doorkey = StateBlock(
    id=str(uuid.uuid4()),
    owner_id="key_owner",  # Identifier of the key's owner or location
    name="Key",
    blocks_move=False,  # A key doesn't block movement
    blocks_los=False,  # A key doesn't block line of sight
    can_store=True,
    can_be_stored=False,
    can_act=True,
    can_move=False,
    can_be_moved=True,
    position=(0, 0, 0),  # Position of the key in the environment
)

door = Door(
    id=str(uuid.uuid4()),
    owner_id="door_owner",  # Identifier of the door's owner or location
    name="Door",
    blocks_move=True,  # A closed door blocks movement
    blocks_los=False,  # A door doesn't generally block line of sight
    can_store=False,
    can_be_stored=False,
    can_act=False,
    can_move=False,
    can_be_moved=False,
    position=(0, 0, 0),  # Position of the door in the environment
    is_open=False,  # Custom attribute indicating if the door is open
    is_locked=True,  # Custom attribute indicating if the door is locked
    key_id=doorkey.id,  # Custom attribute indicating the key that can open the door
)

character = StateBlock(
    id=str(uuid.uuid4()),
    owner_id="character_owner",  # Identifier of the character's owner or location
    name="Character",
    blocks_move=True,  # A character blocks movement
    blocks_los=True,  # A character blocks line of sight
    can_store=True,
    can_be_stored=False,
    can_act=True,
    can_move=True,
    can_be_moved=False,
    position=(0, 0, 0),  # Position of the character in the environment
)

#boolean conditions of the entities 

def is_open_condition(door: StateBlock):
    return door.is_open
def is_locked_condition(door: StateBlock):
    return door.is_locked

def has_key_condition(character: StateBlock):
    key_id = doorkey.id
    for item in character.inventory:
        if item.id == key_id:
            return True
    return False
    

def is_pickable(key: StateBlock):
    return key.can_be_moved

def can_pick(chararacter:StateBlock):
    return chararacter.can_store

def has_inventory_space(character: StateBlock):
    return len(character.inventory) < character.inventory_size


#statements corresponding

statements = {
    "IsOpen": Statement(
    name="IsOpen",
    description="is open",
    callable=is_open_condition,
    usage="target"
    ),
    "IsLocked": Statement(
    name="IsLocked",
    description="is locked",
    callable=is_locked_condition,
    usage="target"),
    "HasKey": Statement(
    name="HasKey",
    description="has key",
    callable=has_key_condition,
    usage="source"),
    "IsPickable": Statement(
    name="IsPickable",
    description="is pickable",
    callable=is_pickable,
    usage="target"),
    "CanPick": Statement(
    name="CanPick",
    description="can pick",
    callable=can_pick,
    usage="source"),
    "HasInventorySpace": Statement(
    name="HasInventorySpace",
    description="has inventory space",
    callable=has_inventory_space,
    usage="source"),
}

open_door_action = Action(name= "character_open_door",
                          prerequisites= [CompositeStatement([(statements["IsOpen"],False), 
                                                              (statements["IsLocked"],False)])],
                          consequences= [CompositeStatement([(statements["IsOpen"],True)])],
                          source_block= character,
                          target_block= door)

close_door_action = Action(name= "character_close_door",
                            prerequisites= [CompositeStatement([(statements["IsOpen"],True),
                                                                 (statements["IsLocked"],False)])],
                            consequences= [CompositeStatement([(statements["IsOpen"],False)])],
                            source_block= character,
                            target_block= door)

lock_door_action = Action(name= "character_lock_door",
                            prerequisites= [CompositeStatement([(statements["IsLocked"],False)]),
                                            CompositeStatement([(statements["HasKey"],True)])],
                            consequences= [CompositeStatement([(statements["IsLocked"],True)]),],
                            source_block= character,
                            target_block= door)

unlock_door_action = Action(name= "character_unlock_door",
                            prerequisites= [CompositeStatement([(statements["IsLocked"],True)]),
                                            CompositeStatement([(statements["HasKey"],True)])],
                            consequences= [CompositeStatement([(statements["IsLocked"],False)])],
                            source_block= character,
                            target_block= door)
pick_key_action = Action(name= "character_pick_key",
                            prerequisites= [CompositeStatement([(statements["IsPickable"],True)]),
                                            CompositeStatement([(statements["HasInventorySpace"],True)])],
                            consequences= [CompositeStatement([(statements["IsPickable"],False)]),
                                           CompositeStatement([(statements["HasKey"],True)])],
                            source_block= character,
                            target_block= doorkey)
actions = [open_door_action,close_door_action,lock_door_action,unlock_door_action,pick_key_action]


def get_forward_solution():
    option = Option()
    option.append(pick_key_action)
    option.append(unlock_door_action)
    option.append(open_door_action)
    return option
def get_backward_solution():
    backward_option = Option()
    backward_option.prepend(open_door_action)
    backward_option.prepend(unlock_door_action)
    backward_option.prepend(pick_key_action)
    return backward_option


#starting statements
#the door is closed and locked
#the key is pickable
#the character has inventory space


statement_tuples=[(CompositeStatement([(statements["IsOpen"],False), (statements["IsLocked"],True)]),None,door.id),
                  (CompositeStatement([(statements["IsPickable"],True)]),None,doorkey.id),
                  (CompositeStatement([(statements["HasInventorySpace"],True)]),character.id,None),
                  (CompositeStatement([(statements["HasKey"],False)]),character.id,None)]
starting_state = WorldStatement(statement_tuples)
goal = CompositeStatement([(statements["IsOpen"],True)])
goal_state = WorldStatement([(goal,None,door.id)])


forward_solution = get_forward_solution()
backward_solution = get_backward_solution()


forward_consequences_state = WorldStatement.from_dict(forward_solution.global_consequences)
forward_prerequisites_state = WorldStatement.from_dict(forward_solution.global_prerequisites)
backward_consequences_state = WorldStatement.from_dict(backward_solution.global_consequences)
backward_prerequisites_state = WorldStatement.from_dict(backward_solution.global_prerequisites)


print(forward_consequences_state.validates(goal_state) and starting_state.validates(forward_prerequisites_state))

print(backward_consequences_state.validates(goal_state) and starting_state.validates(backward_prerequisites_state))


from copy import deepcopy

def print_conditions(cond_dict : dict, with_key = False):
    for key,value in cond_dict.items():
        if with_key:
            print(key)
        print(value.name)

def recursive_solve(current_state: WorldStatement, 
                    available_actions: List[Action], 
                    goal_state: WorldStatement, 
                    current_path: List[Action] = []):
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
        new_available_actions = new_world.available_actions(actions)
        
        # Recurse with the updated state and path
        if recursive_solve(new_world, new_available_actions, goal_state, current_path + [action]):
            return True

    # Return False if no solution found in this path
    return False


def backward_recursive_solve(
    current_option: Option, 
    available_actions: List[Action], 
    goal_state: WorldStatement, 
    current_path: List[Action] = [],
    visited_states: List[WorldStatement] = [],
    max_depth: int = 10  # Default maximum depth
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
    
    if len(current_path) > 0 and goal_state.validates(global_prerequisites):
        print("Backward solution found:", " <- ".join([action.name for action in reversed(current_path)]))
        return True

    # Recursive step: Try each available action that leads to the current state
    for action in available_actions:
        print("Trying action:", action.name)
        new_option = deepcopy(current_option)
        new_option.prepend(action)
        new_world = WorldStatement.from_dict(new_option.global_prerequisites)
        if any([visited_state.validates(new_world) for visited_state in visited_states]):
            print(f"the state  has already been visited")
            print_conditions(new_world.conditions)
            continue
                
        new_available_actions = new_world.available_actions(actions, reverse=True)  # Get actions leading to this state
        print("New available actions:", [action.name for action in new_available_actions])
        print("Current path:", " <- ".join([action.name for action in reversed(current_path)]))
        if backward_recursive_solve(new_option, new_available_actions, goal_state, [action] + current_path, visited_states + [new_world], max_depth - 1):
            return True

    # Return False if no solution found in this path
    return False


    # Initial call to the backward recursive function
current_option = Option(starting_dict=goal_state.conditions)
actions = goal_state.available_actions(actions, reverse=True)
backward_recursive_solve(current_option, actions, starting_state)

from infinipy.goap import GOAP
goap = GOAP(actions)
goap.backward_solve(starting_state, goal_state)