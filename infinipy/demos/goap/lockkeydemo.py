from infinipy.stateblock import StateBlock
import uuid
from copy import deepcopy

from infinipy.statement import Statement,CompositeStatement

from typing import List, Optional, Dict, Any, Union, Tuple
from infinipy.options import Option
from infinipy.worldstatement import WorldStatement
from dataclasses import dataclass, fields
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
    position=(0, 0),  # Position of the key in the environment
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
    position=(0, 0),  # Position of the door in the environment
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
    position=(0, 0),  # Position of the character in the environment
)
entities = [door, doorkey, character]

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
                            prerequisites= [CompositeStatement([(statements["HasKey"],False)])
                                            ,CompositeStatement([(statements["IsPickable"],True)]),
                                            CompositeStatement([(statements["HasInventorySpace"],True)]),],
                            consequences= [CompositeStatement([(statements["IsPickable"],False)]),
                                           CompositeStatement([(statements["HasKey"],True)])],
                            source_block= character,
                            target_block= doorkey)
drop_key_action = Action(name= "character_drop_key",
                            prerequisites= [CompositeStatement([(statements["HasKey"],True)]),
                                            CompositeStatement([(statements["IsPickable"],False)])
                                            ],
                            consequences= [CompositeStatement([(statements["IsPickable"],True)]),
                                           CompositeStatement([(statements["HasKey"],False)]),
                                           CompositeStatement([(statements["HasInventorySpace"],True)])]
                                           ,
                                           
                            source_block= character,
                            target_block= doorkey)
actions = [open_door_action,close_door_action,lock_door_action,unlock_door_action,pick_key_action,drop_key_action]


statement_tuples=[(CompositeStatement([(statements["IsOpen"],False), (statements["IsLocked"],True)]),None,door.id),
                  (CompositeStatement([(statements["IsPickable"],True)]),None,doorkey.id),
                  (CompositeStatement([(statements["HasInventorySpace"],True)]),character.id,None),
                  (CompositeStatement([(statements["HasKey"],False)]),character.id,None)]
starting_state = WorldStatement(statement_tuples)
goal = CompositeStatement([(statements["IsOpen"],True),])
goal_state = WorldStatement([(goal,None,door.id)])



def create_demo():
    return entities, statements, actions, (starting_state,goal_state)