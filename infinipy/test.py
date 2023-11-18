from stateblock import StateBlock
from statement import Statement, CompositeStatement, bigger_than, equals_to, RelationalStatement, CompositeRelationalStatement
from transformer import Transformer, CompositeTransformer

# Example D&D inspired StateBlock instances
warrior = StateBlock(
    id="1", owner_id="player1", name="Warrior", position=(0, 0, 0), reach=10, hitpoints=100, 
    size="medium", blocks_move=True, blocks_los=False, can_store=False, 
    can_be_stored=False, can_act=True, can_move=True, can_be_moved=False
)

dragon = StateBlock(
    id="2", owner_id="npc1", name="Dragon", position=(10, 10, 0), reach=99, hitpoints=300,
    size="very large", blocks_move=True, blocks_los=True, can_store=True, 
    can_be_stored=False, can_act=True, can_move=True, can_be_moved=True
)

treasure_chest = StateBlock(
    id="3", owner_id="npc2", name="Treasure Chest", position=(5, 5, 0), reach=0, hitpoints=50,
    size="small", blocks_move=False, blocks_los=False, can_store=True, 
    can_be_stored=True, can_act=False, can_move=False, can_be_moved=True
)

# Creating conditions
high_hitpoints = bigger_than(150)
is_large = equals_to("large")
can_be_moved_condition = equals_to(True)

# Composite condition example
# Checking if an entity has high hitpoints and can be moved
high_hp_and_movable = CompositeStatement([
    (high_hitpoints, "hitpoints", 'AND'), 
    (can_be_moved_condition, "can_be_moved", 'AND')
])


# Applying conditions to StateBlock instances
print("Warrior has high hitpoints:", high_hitpoints.apply(warrior, "hitpoints"))
print("Dragon is large:", is_large.apply(dragon, "size"))
print("Treasure chest can be moved:", can_be_moved_condition.apply(treasure_chest, "can_be_moved"))
# Applying the composite condition to the dragon StateBlock
print("Dragon has high hitpoints and can be moved:", high_hp_and_movable(dragon))

# Transformer functions
def increase_hitpoints(state_block: StateBlock, amount: int):
    state_block.hitpoints += amount

def change_size(state_block: StateBlock, new_size: str):
    state_block.size = new_size

# Create Transformer instances
heal_transformer = Transformer("Heal", lambda sb: increase_hitpoints(sb, 50))
size_change_transformer = Transformer("Size Change", lambda sb: change_size(sb, "small"))

# Composite transformer
composite_transformer = CompositeTransformer([heal_transformer, size_change_transformer])

# Apply transformers to StateBlock instances
print(f"Warrior hitpoints before healing: {warrior.hitpoints}, size: {warrior.size}")
composite_transformer(warrior)
print(f"Dragon hitpoints before healing: {dragon.hitpoints}, size: {dragon.size}")
composite_transformer(dragon)
print(f"Treasure chest hitpoints before healing: {treasure_chest.hitpoints}, size: {treasure_chest.size}")
composite_transformer(treasure_chest)

# Checking the results
print(f"Warrior hitpoints after healing: {warrior.hitpoints}, size: {warrior.size}")
print(f"Dragon hitpoints after healing: {dragon.hitpoints}, size: {dragon.size}")
print(f"Treasure chest hitpoints after healing: {treasure_chest.hitpoints}, size: {treasure_chest.size}")


# Define a relational statement for checking if the target is within reach of the source
def is_within_reach(source: StateBlock, target: StateBlock) -> bool:
    dx = source.position[0] - target.position[0]
    dy = source.position[1] - target.position[1]
    distance = (dx**2 + dy**2)**0.5
    return distance <= source.reach

within_reach_statement = RelationalStatement(
    "Within Reach",
    "Checks if the target is within reach of the source",
    is_within_reach
)

# Define a composite relational statement
composite_relational_statement = CompositeRelationalStatement([
    (within_reach_statement, 'AND'), 
    (RelationalStatement("Has High Hitpoints", "Target has high hitpoints", lambda s, t: t.hitpoints > 150), 'AND')
])

# Testing relational statements
print(f"Is dragon within reach of warrior: {within_reach_statement.apply(warrior, dragon)}")
print(f"Is the warrior within reach of the dragon: {within_reach_statement.apply(dragon, warrior)}")
print(f"Is treasure chest within reach of warrior: {within_reach_statement.apply(warrior, treasure_chest)}")
print(f"Is treasure chest within reach of warrior and does it have high hitpoints: {composite_relational_statement.apply(warrior, treasure_chest)}")
