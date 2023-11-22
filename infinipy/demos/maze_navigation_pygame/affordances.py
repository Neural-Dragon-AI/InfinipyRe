from infinipy.stateblock import StateBlock
from infinipy.statement import Statement, CompositeStatement, RelationalStatement, CompositeRelationalStatement
from infinipy.affordance import Affordance
from infinipy.transformer import Transformer, CompositeTransformer, RelationalTransformer, CompositeRelationalTransformer
import random
import time
from infinipy.content.statements import bigger_than, equals_to, has_attribute, is_true
from infinipy.gridmap import GridMap
from typing import List, Tuple, Optional

## movement logic 
def euclidean_distance(source: StateBlock, target: StateBlock) -> bool:
    source_position = source.position
    target_position = target.position
    dx = source_position[0] - target_position[0]
    dy = source_position[1] - target_position[1]
    distance = (dx**2 + dy**2)**0.5
    return distance <= source.reach

within_reach_statement = RelationalStatement(
    "Within Reach",
    "Checks if the target is within reach of the source based on their positions",
    euclidean_distance
)

def move(source: StateBlock, target: StateBlock):
    source.position = target.position

movement_transformer = RelationalTransformer("Movement Transformation", move)

move_to_affordance = Affordance(
    name="MoveTo",
    prerequisites=[(within_reach_statement, 'source')],
    consequences=[(movement_transformer, 'source')]
)
## pick up logic
# #source conditions
def has_inventory_space(source: StateBlock):
    if len(source.inventory) < source.inventory_size:
        return True

has_inventory_statement = Statement("Has Inventory Space", list, "Checks if the source has inventory space", has_inventory_space)
has_inventory_attribute = has_attribute("inventory")

can_store = CompositeStatement([(has_inventory_attribute, 'AND'), (has_inventory_statement, 'AND')])
#target conditions
is_pickable = CompositeStatement([(has_attribute("can_be_stored"), 'AND'), (is_true("can_be_stored"), 'AND')])
#effect definition
def pick_up(source: StateBlock, target: StateBlock):
    source.add_to_inventory(target)

pick_up_transformer = RelationalTransformer("Pick Up Transformation", pick_up)

pick_up_affordance = Affordance(
    name="PickUp",
    prerequisites=[(is_pickable, 'target'), (can_store, 'source'),
                   (within_reach_statement, 'source')],
    consequences=[(pick_up_transformer, 'source')]
)