import pygame
from infinipy.gridmap import GridMap
from map import create_map_with_gridmap
from renderer import Renderer
from entities import CharacterBlock, FloorBlock, TreasureBlock, WallBlock
from grid_from_dict import load_json_file, create_map_from_json
from inputhandler import InputHandler
import os
import random

class NPC:
    def __init__(self, character_entity:CharacterBlock, renderer: Renderer):
        self.character = character_entity
        self.renderer = renderer
        self.current_path = []
        self.not_pathable = set()

    def choose_random_destination(self):
        seen_unvisited = self.renderer.get_seen_unvisited_cells() - self.not_pathable
        if not seen_unvisited:
            return None
        return random.choice(list(seen_unvisited))

    def compute_path(self, grid_map, destination):
        path = grid_map.a_star(self.character.position, destination + (0,))
        if path:  # Path is found
            self.current_path = path
        else:  # No path to destination
            self.not_pathable.add(destination)
            self.choose_new_destination(grid_map)

    def move_along_path(self, grid_map: GridMap):
        if self.current_path:
            next_step = self.current_path.pop(0)
            grid_map.move_entity(self.character, next_step)
            self.renderer.set_active_source_from_grid(next_step[:2])  # Update renderer's source position
            if not self.current_path:  # Check if the destination is reached
                self.choose_new_destination(grid_map)

    def choose_new_destination(self, grid_map):
        destination = self.choose_random_destination()
        if destination:
            self.compute_path(grid_map, destination)
            #add the destination to the renderer's active target
            self.renderer.set_active_target_from_grid(destination[:2])

    def update(self, grid_map):
        if not self.current_path:
            self.choose_new_destination(grid_map)
        self.move_along_path(grid_map)


pygame.init()
pygame.font.init()
# renderer = Renderer(grid_map)
player = CharacterBlock(id="char1", owner_id="player", name="Character", position=(21, 39, 0),
                             reach=1, hitpoints=100, size="small", blocks_move=False, 
                             blocks_los=False, can_store=True, can_move=True)


tile_size = 24
grid_map,tile_size = create_map_from_json()
grid_map.add_entity(player, player.position)
current_path = os.path.dirname(__file__)
folder_name = 'maps'
image_name = 'topdowndungeon.png'
image_path = os.path.join(current_path, folder_name,image_name)
renderer = Renderer(grid_map,tile_size = tile_size, background_image_path=image_path)
input_handler = InputHandler(renderer)
npc = NPC(player, renderer)
renderer.active_source=player.position[:2]
running = True
npg_go = False
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            npg_go = not npg_go
            
    input_handler.handle_events(events, player, grid_map)          
    renderer.render()
    if npg_go:
        npc.update(grid_map)
        
pygame.quit()