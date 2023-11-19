from infinipy.stateblock import StateBlock
from infinipy.statement import Statement, CompositeStatement, RelationalStatement, CompositeRelationalStatement
from infinipy.content.statements import bigger_than, equals_to, has_attribute, is_true
from infinipy.affordance import Affordance
from infinipy.transformer import Transformer, CompositeTransformer, RelationalTransformer, CompositeRelationalTransformer
import random
import time
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
#define logic for picking up treasure
#source conditions
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

def create_map_with_room(characters, map_size, room_size):
    walls = []
    floors = []
    door_x, door_y = room_size - 1, room_size - 2
    for y in range(map_size):
        for x in range(map_size):
            if x == 0 or y == 0 or x == map_size - 1 or y == map_size - 1:
                walls.append(WallBlock(id=f"wall_{x}_{y}", owner_id="environment", name="Wall", position=(x, y, 0),
                                       reach=0, hitpoints=100, size="medium", blocks_move=True, blocks_los=True))
            elif (x < room_size and y < room_size) and (x == room_size - 1 or y == room_size - 1) and not (x == door_x and y == door_y):
                walls.append(WallBlock(id=f"wall_{x}_{y}", owner_id="environment", name="Wall", position=(x, y, 0),
                                       reach=0, hitpoints=100, size="medium", blocks_move=True, blocks_los=True))
            else:
                floors.append(FloorBlock(id=f"floor_{x}_{y}", owner_id="environment", name="Floor", position=(x, y, 0),
                                         reach=0, hitpoints=100, size="medium", blocks_move=False, blocks_los=False))

    treasures = [TreasureBlock(id="treasure_1", owner_id="environment", name="Treasure", position=(door_x, door_y, 0),
                               reach=0, hitpoints=100, size="small", blocks_move=False, blocks_los=False, can_be_stored=True)]

    for character in characters:
        if any(wall.position == character.position for wall in walls):
            valid_floor = next((floor for floor in floors if floor.position not in (wall.position for wall in walls)), None)
            if valid_floor:
                character.position = valid_floor.position

    return characters, walls, floors, treasures

def display_grid(characters, floors, walls, treasures, map_size):
    grid = [[' ' for _ in range(map_size)] for _ in range(map_size)]
    for block in floors + walls:
        x, y, _ = block.position
        grid[y][x] = '.' if isinstance(block, FloorBlock) else '#'
    for treasure in treasures:
        x, y, _ = treasure.position
        grid[y][x] = 'T'
    for character in characters:
        x, y, _ = character.position
        grid[y][x] = 'C'
    for row in grid:
        print(' '.join(row))
    #print summary of character inventory
    for character in characters:
        print(f"{character.name} has {len(character.inventory)} items in inventory")

# Create the room layout
map_size = 20
room_size = 5
characters = [CharacterBlock(id="char1", owner_id="player", name="Character", position=(1, 1, 0),
                             reach=1, hitpoints=100, size="small", blocks_move=False, 
                             blocks_los=False, can_store=True, can_move=True)]
characters, walls, floors, treasures = create_map_with_room(characters, map_size, room_size)
display_grid(characters, floors, walls, treasures, map_size)

def simulate_movement(steps, character, floors, walls, treasures):
    for step in range(steps):
        print(f"\nStep {step + 1}:")

        # Check for treasures that can be picked up
        reachable_treasures = [treasure for treasure in treasures if pick_up_affordance.is_applicable(character, treasure)]
        if reachable_treasures:
            chosen_treasure = random.choice(reachable_treasures)
            print(f"Character picks up {chosen_treasure.name} at {chosen_treasure.position}")
            pick_up_affordance.apply(character, chosen_treasure)
            treasures.remove(chosen_treasure)  # Remove the picked up treasure from the game
        else:
            # Move to a random floor tile if no treasure is picked up
            reachable_floors = [floor for floor in floors if move_to_affordance.is_applicable(character, floor)]
            if reachable_floors:
                chosen_floor = random.choice(reachable_floors)
                print(f"Character moves to {chosen_floor.position}")
                move_to_affordance.apply(character, chosen_floor)
            else:
                print("No reachable floors or treasures.")

        display_grid(characters, floors, walls, treasures, map_size)
        time.sleep(0.5)

# Run the simulation
simulate_movement(50, characters[0], floors, walls, treasures)
