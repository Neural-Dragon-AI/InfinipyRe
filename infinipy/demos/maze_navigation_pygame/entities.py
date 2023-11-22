from infinipy.stateblock import StateBlock
from infinipy.statement import Statement, CompositeStatement, RelationalStatement, CompositeRelationalStatement
from infinipy.affordance import Affordance
from infinipy.transformer import Transformer, CompositeTransformer, RelationalTransformer, CompositeRelationalTransformer
import random
import time
from infinipy.content.statements import bigger_than, equals_to, has_attribute, is_true
from infinipy.gridmap import GridMap
from typing import List, Tuple, Optional

class CharacterBlock(StateBlock):
    def __init__(self, *args, can_store=True, can_move=True, can_be_stored=False, can_act=True, can_be_moved=True, **kwargs):
        super().__init__(*args, can_store=can_store, can_move=can_move, can_be_stored=can_be_stored, can_act=can_act, can_be_moved=can_be_moved, **kwargs)

class FloorBlock(StateBlock):
    def __init__(self, *args, can_store=False, can_move=False, can_be_stored=False, can_act=False, can_be_moved=False, **kwargs):
        super().__init__(*args, can_store=can_store, can_move=can_move, can_be_stored=can_be_stored, can_act=can_act, can_be_moved=can_be_moved, **kwargs)

class WallBlock(StateBlock):
    def __init__(self, *args, can_store=False, can_move=False, can_be_stored=False, can_act=False, can_be_moved=False, **kwargs):
        super().__init__(*args, can_store=can_store, can_move=can_move, can_be_stored=can_be_stored, can_act=can_act, can_be_moved=can_be_moved, **kwargs)

class TreasureBlock(StateBlock):
    def __init__(self, *args, can_store=False, can_move=False, can_be_stored=True, can_act=False, can_be_moved=False, **kwargs):
        super().__init__(*args, can_store=can_store, can_move=can_move, can_be_stored=can_be_stored, can_act=can_act, can_be_moved=can_be_moved, **kwargs)

