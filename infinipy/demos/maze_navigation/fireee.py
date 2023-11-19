
from infinipy.stateblock import StateBlock
from infinipy.statement import Statement, CompositeStatement, RelationalStatement, CompositeRelationalStatement
from infinipy.content.statements import bigger_than, equals_to, has_attribute, is_true
from infinipy.affordance import Affordance
from infinipy.transformer import Transformer, CompositeTransformer, RelationalTransformer, CompositeRelationalTransformer
import random
import time

class BurnableCharacterBlock(StateBlock):
    def __init__(self, *args, can_store=True, can_move=True, can_be_stored=False, can_act=True, can_be_moved=True, **kwargs):
        super().__init__(*args, can_store=can_store, can_move=can_move, can_be_stored=can_be_stored, can_act=can_act, can_be_moved=can_be_moved, **kwargs)
        self.burning = False
        self.wet = False


class BurnableFloorBlock(StateBlock):
    def __init__(self, *args, can_store=False, can_move=False, can_be_stored=False, can_act=False, can_be_moved=False, **kwargs):
        super().__init__(*args, can_store=can_store, can_move=can_move, can_be_stored=can_be_stored, can_act=can_act, can_be_moved=can_be_moved, **kwargs)
        self.burning = False
        self.wet = False


# target conditions
def not_wet(source: StateBlock):
    return not source.wet
can_be_burnt_statement = Statement("Can Be Burnt", bool, "Checks if the source can be burnt", not_wet)

#source conditions
def is_burning(source: StateBlock):
    return source.burning
can_burn_things_statement = Statement("Can Burn Things", bool, "Checks if the source can burn things", is_burning)

#relational conditions
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

#define the system mechanics for burning
def burn (source: StateBlock):
    source.burning = True

burning_transformer = RelationalTransformer("Burning Transformation", burn)

burn_affordance = Affordance(
    name="Burn",
    prerequisites=[(can_be_burnt_statement, 'target'), (can_burn_things_statement, 'source')
                   , (within_reach_statement, 'source')],
    consequences=[(burning_transformer, 'target')]
)

