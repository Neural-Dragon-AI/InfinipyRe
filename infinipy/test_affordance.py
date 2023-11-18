# Assuming necessary imports from your previous scripts
# StateBlock, Statement, CompositeStatement, RelationalStatement, 
# CompositeRelationalStatement, Transformer, CompositeTransformer, Affordance
from typing import Callable, List, Tuple, Union
from affordance import Affordance
from stateblock import StateBlock
from statement import Statement, CompositeStatement, RelationalStatement, CompositeRelationalStatement
from transformer import Transformer

# Assuming necessary imports and class definitions are already in place
def is_within_reach(source: StateBlock, target: StateBlock, source_variable: str, target_variable: str) -> bool:
    # Retrieve positions based on the provided variable names (assuming these are 'position')
    source_position = getattr(source, source_variable)
    target_position = getattr(target, target_variable)

    # Calculate the distance between the source and target
    dx = source_position[0] - target_position[0]
    dy = source_position[1] - target_position[1]
    distance = (dx**2 + dy**2)**0.5

    # Check if the target is within the source's reach
    return distance <= source.reach
# Define StateBlock instances
warrior = StateBlock(
    id="1", owner_id="player1", name="Warrior", position=(1, 1, 0), reach=2, hitpoints=80,
    size="medium", blocks_move=True, blocks_los=False, can_store=False, 
    can_be_stored=False, can_act=True, can_move=True, can_be_moved=False
)

dragon = StateBlock(
    id="2", owner_id="npc1", name="Dragon", position=(5, 5, 0), reach=3, hitpoints=200,
    size="very large", blocks_move=True, blocks_los=True, can_store=False, 
    can_be_stored=False, can_act=True, can_move=True, can_be_moved=False
)

treasure_chest = StateBlock(
    id="3", owner_id="npc2", name="Treasure Chest", position=(2, 1, 0), reach=0, hitpoints=0,
    size="small", blocks_move=False, blocks_los=False, can_store=True, 
    can_be_stored=True, can_act=False, can_move=False, can_be_moved=True
)

# Define Statements
low_hitpoints = Statement("Low Hitpoints", int, "Checks if hitpoints are below 100", lambda x: x < 100)
composite_low_hitpoints = CompositeStatement([(low_hitpoints, "hitpoints", 'AND')])

# Define Relational Statements
within_reach_statement = RelationalStatement(
    "Within Reach",
    "Checks if the target is within reach of the source based on their positions",
    is_within_reach
)
composite_within_reach = CompositeRelationalStatement([(within_reach_statement,"position","position", 'AND')])

# Define Transformers
heal = Transformer("Heal", lambda block: setattr(block, "hitpoints", block.hitpoints + 50))
open_chest = Transformer("Open Chest", lambda block: setattr(block, "size", "opened"))

# Define Affordances
open_treasure_chest = Affordance(
    "Open Treasure Chest",
    [(composite_within_reach, 'source')],
    [(open_chest, 'target')]
)

dragon_self_heal = Affordance(
    "Dragon Self Heal",
    [(composite_low_hitpoints, 'source')],
    [(heal, 'source')]
)

# Testing Statements
print("Warrior low hitpoints:", low_hitpoints(warrior, "hitpoints"))

# Testing Composite Statements
print("Warrior low hitpoints (Composite):", composite_low_hitpoints(warrior))

# Testing Relational and Composite Relational Statements
# Testing Relational and Composite Relational Statements
print("Warrior within reach of treasure chest:", within_reach_statement(warrior, treasure_chest, "position", "position"))
print("Dragon within reach of warrior (Composite):", composite_within_reach(dragon, warrior))


# Testing Affordances
print("Treasure chest state:", treasure_chest.size)
print("Can warrior open treasure chest:", open_treasure_chest.is_applicable(warrior, treasure_chest))
if open_treasure_chest.is_applicable(warrior, treasure_chest):
    open_treasure_chest.apply(warrior, treasure_chest)
    print("Treasure chest state:", treasure_chest.size)

print("Can dragon heal itself:", dragon_self_heal.is_applicable(dragon, dragon))
if dragon_self_heal.is_applicable(dragon, dragon):
    dragon_self_heal.apply(dragon, dragon)
    print("Dragon hitpoints after self-healing:", dragon.hitpoints)
