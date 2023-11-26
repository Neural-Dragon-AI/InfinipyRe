from infinipy.gridmap import GridMap
from infinipy.stateblock import StateBlock
from infinipy.affordance import Affordance
import random
import time
from infinipy.gridmap import GridMap
from typing import List, Tuple, Optional
import json
from entities import CharacterBlock, FloorBlock, TreasureBlock, WallBlock

# class CharacterBlock(StateBlock):
#     def __init__(self, *args, can_store=True, can_move=True, can_be_stored=False, can_act=True, can_be_moved=True, **kwargs):
#         super().__init__(*args, can_store=can_store, can_move=can_move, can_be_stored=can_be_stored, can_act=can_act, can_be_moved=can_be_moved, **kwargs)

# class FloorBlock(StateBlock):
#     def __init__(self, *args, can_store=False, can_move=False, can_be_stored=False, can_act=False, can_be_moved=False, **kwargs):
#         super().__init__(*args, can_store=can_store, can_move=can_move, can_be_stored=can_be_stored, can_act=can_act, can_be_moved=can_be_moved, **kwargs)

# class WallBlock(StateBlock):
#     def __init__(self, *args, can_store=False, can_move=False, can_be_stored=False, can_act=False, can_be_moved=False, **kwargs):
#         super().__init__(*args, can_store=can_store, can_move=can_move, can_be_stored=can_be_stored, can_act=can_act, can_be_moved=can_be_moved, **kwargs)

# class TreasureBlock(StateBlock):
#     def __init__(self, *args, can_store=False, can_move=False, can_be_stored=True, can_act=False, can_be_moved=False, **kwargs):
#         super().__init__(*args, can_store=can_store, can_move=can_move, can_be_stored=can_be_stored, can_act=can_act, can_be_moved=can_be_moved, **kwargs)





def load_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def initialize_gridmap(input_dict, entity_mapping, default_class=None):
    # Extracting tile notes and labels from the input dictionary
    tile_notes = input_dict['tile_notes']
    labels = input_dict['labels']
      
    #get the map size from the input dict
    map_width = input_dict['grid_width']
    map_height = input_dict['grid_height']
    grid_map = GridMap(map_size=(map_width,map_height))

    # Iterate over all possible positions
    for y in range(input_dict['grid_height']):
        for x in range(input_dict['grid_width']):
            position = (x, y)
            position_str = f"({x}, {y})"
            
            # Check if there are notes for the current position
            if position_str in tile_notes:
                note_list = tile_notes[position_str]
                for note in note_list:
                    label_color = labels[note]
                    entity_class = entity_mapping.get(note)

                    # Create an entity if a mapping exists
                    if entity_class:
                        entity = entity_class(
                            id=f"{note}_{x}_{y}",
                            owner_id="environment", 
                            name=note.capitalize(), 
                            position=(x, y, 0),
                            reach=0, 
                            hitpoints=100, 
                            size="medium", 
                            blocks_move=(note == 'wall'),
                            blocks_los=(note == 'wall')
                        )
                        grid_map.add_entity(entity, (x, y, 0))
            elif default_class:
                # Create default entity for empty tiles
                entity = default_class(
                    id=f"default_{x}_{y}",
                    owner_id="environment", 
                    name="Default", 
                    position=(x, y, 0),
                    reach=0, 
                    hitpoints=100, 
                    size="medium", 
                    blocks_move=False, 
                    blocks_los=False
                )
                grid_map.add_entity(entity, (x, y, 0))
    tile_size = input_dict['tile_size']
    return grid_map,tile_size


def create_map_from_json(
        path = r"C:\Users\Tommaso\Documents\Dev\InfinipyRe\infinipy\demos\autogrid\outs\topdowndungeon.png_grid.json", 
        entity_mapping =  {
            "wall": WallBlock,
            "floor": FloorBlock,
            # Add other mappings as needed
        }):


    # Path to the JSON file
    json_file_path = path

    # Load the input dictionary from JSON file
    input_dict = load_json_file(json_file_path)

    # Initialize the grid map with a default class for empty tiles
    grid_map, tile_size = initialize_gridmap(input_dict, entity_mapping, default_class=FloorBlock)
    print(f"GridMap initialized with {len(grid_map.entities.values())} entities and {len(grid_map.entities.keys())} tiles, with a tile size of {tile_size}")
    return grid_map,tile_size
# Entity mapping with direct incorporation for 'wall' and 'floor'

def main():
    grid_map,tile_size = create_map_from_json()

if __name__ == "__main__":
    main()
    
        
    