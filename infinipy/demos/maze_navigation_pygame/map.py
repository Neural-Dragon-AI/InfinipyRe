from infinipy.gridmap import GridMap
from entities import CharacterBlock, FloorBlock, TreasureBlock, WallBlock
from typing import List, Tuple, Optional

def create_map_with_gridmap(grid_map: GridMap, map_size: int, room_size: int, characters: List[CharacterBlock]) -> Tuple[List[WallBlock], List[FloorBlock], List[TreasureBlock]]:
    walls = []
    floors = []
    door_x, door_y = room_size - 1, room_size - 2
    for y in range(map_size):
        for x in range(map_size):
            if x == 0 or y == 0 or x == map_size - 1 or y == map_size - 1:
                wall = WallBlock(id=f"wall_{x}_{y}", owner_id="environment", name="Wall", position=(x, y, 0),
                                 reach=0, hitpoints=100, size="medium", blocks_move=True, blocks_los=True)
                walls.append(wall)
                grid_map.add_entity(wall, (x, y, 0))
            elif (x < room_size and y < room_size) and (x == room_size - 1 or y == room_size - 1) and not (x == door_x and y == door_y):
                wall = WallBlock(id=f"wall_{x}_{y}", owner_id="environment", name="Wall", position=(x, y, 0),
                                 reach=0, hitpoints=100, size="medium", blocks_move=True, blocks_los=True)
                walls.append(wall)
                grid_map.add_entity(wall, (x, y, 0))
            else:
                floor = FloorBlock(id=f"floor_{x}_{y}", owner_id="environment", name="Floor", position=(x, y, 0),
                                   reach=0, hitpoints=100, size="medium", blocks_move=False, blocks_los=False)
                floors.append(floor)
                grid_map.add_entity(floor, (x, y, 0))

    treasures = [TreasureBlock(id="treasure_1", owner_id="environment", name="Treasure", position=(door_x, door_y, 0),
                               reach=0, hitpoints=100, size="small", blocks_move=False, blocks_los=False, can_be_stored=True)]
    for treasure in treasures:
        grid_map.add_entity(treasure, treasure.position)

    for character in characters:
        grid_map.add_entity(character, character.position)

    return grid_map