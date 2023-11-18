#we have 3 type of entity character, floor and wall, the floor has an affordance called move_to which changes the position of the source to the floor position, it require the source to be in reach of the target  and have the can_move attribute, there can not be both floor and walls at the same position of course. At each turn the character with reach 1 should know which floors it can move to (by checking the prerequisite for all floors) and move to a random floor tile

from stateblock import StateBlock
from statement import Statement, CompositeStatement, RelationalStatement, CompositeRelationalStatement, equals_to
from affordance import Affordance
from transformer import Transformer, CompositeTransformer, RelationalTransformer
import random

class CharacterBlock(StateBlock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class FloorBlock(StateBlock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class WallBlock(StateBlock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



def create_map_with_room(characters, map_size, room_size):
    walls = []
    floors = []

    # Adjust the door position one slot up from the bottom right corner
    door_x, door_y = room_size - 1, room_size - 2

    # Create the walls and floors for the map
    for y in range(map_size):
        for x in range(map_size):
            # Map boundary walls
            if x == 0 or y == 0 or x == map_size - 1 or y == map_size - 1:
                walls.append(WallBlock(id=f"wall_{x}_{y}", owner_id="environment", name="Wall", position=(x, y, 0),
                                       reach=0, hitpoints=100, size="medium", blocks_move=True, 
                                       blocks_los=True, can_store=False, can_be_stored=False, 
                                       can_act=False, can_move=False, can_be_moved=False))
            # Room walls, excluding the door
            elif (x < room_size and y < room_size) and (x == room_size - 1 or y == room_size - 1) and not (x == door_x and y == door_y):
                walls.append(WallBlock(id=f"wall_{x}_{y}", owner_id="environment", name="Wall", position=(x, y, 0),
                                       reach=0, hitpoints=100, size="medium", blocks_move=True, 
                                       blocks_los=True, can_store=False, can_be_stored=False, 
                                       can_act=False, can_move=False, can_be_moved=False))
            # Floor everywhere else
            else:
                floors.append(FloorBlock(id=f"floor_{x}_{y}", owner_id="environment", name="Floor", position=(x, y, 0),
                                         reach=0, hitpoints=100, size="medium", blocks_move=False, 
                                         blocks_los=False, can_store=False, can_be_stored=False, 
                                         can_act=False, can_move=False, can_be_moved=False))

    # Update character positions if necessary to ensure they're not in a wall
    for character in characters:
        if any(wall.position == character.position for wall in walls):
            # If the character is inside a wall, move to a valid floor position
            valid_floor = next((floor for floor in floors if floor.position not in (wall.position for wall in walls)), None)
            if valid_floor:
                character.position = valid_floor.position

    return characters, walls, floors



def display_grid(characters, floors, walls, room_size):
    grid = [[' ' for _ in range(room_size)] for _ in range(room_size)]

    # Place walls and floors on the grid
    for block in floors + walls:
        x, y, _ = block.position
        if isinstance(block, FloorBlock):
            grid[y][x] = '.'  # Representing floor with '.'
        elif isinstance(block, WallBlock):
            grid[y][x] = '#'  # Representing wall with '#'

    # Place characters on the grid
    for character in characters:
        x, y, _ = character.position
        grid[y][x] = 'C'  # Representing character with 'C'

    # Print the grid
    for row in grid:
        print(' '.join(row))




# Assuming necessary imports and class definitions are already in place
def euclidean_distance(source: StateBlock, target: StateBlock, source_variable: str, target_variable: str) -> bool:
    # Retrieve positions based on the provided variable names (assuming these are 'position')
    source_position = getattr(source, source_variable)
    target_position = getattr(target, target_variable)

    # Calculate the distance between the source and target
    dx = source_position[0] - target_position[0]
    dy = source_position[1] - target_position[1]
    distance = (dx**2 + dy**2)**0.5

    # Check if the target is within the source's reach
    return distance <= source.reach

# Define Relational Statements
within_reach_statement = RelationalStatement(
    "Within Reach",
    "Checks if the target is within reach of the source based on their positions",
    euclidean_distance
)
composite_within_reach = CompositeRelationalStatement([(within_reach_statement,"position","position", 'AND')])

def move(source: StateBlock, target: StateBlock):
    """
    Sets the source's position to the target's position.

    :param source: The StateBlock representing the source of the action.
    :param target: The StateBlock representing the target of the action.
    """
    source.position = target.position
movement_transformer = RelationalTransformer("Movement Transformation", move)
# Define the MoveTo affordance
move_to_affordance = Affordance(
    name="MoveTo",
    prerequisites=[(composite_within_reach, 'source')],
    consequences=[(movement_transformer, 'source')]
)


# Create the room layout
map_size = 20
room_size = 5
characters = [CharacterBlock(id="char1", owner_id="player", name="Character", position=(1, 1, 0),
                             reach=1, hitpoints=100, size="small", blocks_move=False, 
                             blocks_los=False, can_store=False, can_be_stored=False, 
                             can_act=True, can_move=True, can_be_moved=False)]
# Test the function
characters, walls, floors = create_map_with_room(characters, map_size=map_size, room_size=room_size)
display_grid(characters, floors, walls, map_size)

def simulate_movement(steps, character, floors, walls):
    for step in range(steps):
        print(f"\nStep {step + 1}:")

        # Find all floors that the character can move to
        reachable_floors = [floor for floor in floors if move_to_affordance.is_applicable(character, floor)]

        # Choose a random floor tile from the reachable ones
        if reachable_floors:
            chosen_floor = random.choice(reachable_floors)
            print(f"Character moves to {chosen_floor.position}")
            move_to_affordance.apply(character, chosen_floor)
        else:
            print("No reachable floors.")

        # Display the updated grid
        display_grid([character], floors, walls, map_size)

# Run the simulation for 10 steps
simulate_movement(10, characters[0], floors, walls)

# # Test the display function
# display_grid(characters, floors, walls, room_size)

# # Affordance for moving
# def can_move_to(source_block: CharacterBlock, target_block: FloorBlock) -> bool:
#     return (abs(source_block.position[0] - target_block.position[0]) <= source_block.reach and
#             abs(source_block.position[1] - target_block.position[1]) <= source_block.reach and
#             all(wall.position != target_block.position for wall in walls))

# def move_transformer(source_block: CharacterBlock, target_block: FloorBlock):
#     source_block.position = target_block.position

# # Adjusted the CompositeStatement creation
# move_to = Affordance(
#     name="MoveTo",
#     prerequisites=[
#         (CompositeStatement([
#             (Statement("CanMoveTo", CharacterBlock, "Check if character can move to floor", can_move_to), 'position', 'AND')
#         ]), "source")
#     ],
#     consequences=[(Transformer("Move", move_transformer), "source")]
# )

# # Simulation loop
# for turn in range(10):
#     print(f"--- Turn {turn + 1} ---")
#     character = characters[0]
#     accessible_floors = [floor for floor in floors if can_move_to(character, floor)]
    
#     if accessible_floors:
#         target_floor = random.choice(accessible_floors)
#         move_to.apply(character, target_floor)
#         print(f"Character moved to {character.position}")
#     else:
#         print("Character cannot move.")

# # Final position of the character
# print(f"Final position of the character: {character.position}")
