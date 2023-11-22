import pygame
from infinipy.gridmap import GridMap
from map import create_map_with_gridmap
from renderer import Renderer
from entities import CharacterBlock, FloorBlock, TreasureBlock, WallBlock

grid_map = GridMap()
renderer = Renderer(grid_map)
characters = [CharacterBlock(id="char1", owner_id="player", name="Character", position=(10, 10, 0),
                             reach=1, hitpoints=100, size="small", blocks_move=False, 
                             blocks_los=False, can_store=True, can_move=True)]


player = characters[0]
grid_map = create_map_with_gridmap(grid_map, 70, 5, characters) 


running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                print("moving   up")
                
                renderer.camera.move((0, -32))
            elif event.key == pygame.K_s:
                renderer.camera.move((0, 32))
            elif event.key == pygame.K_a:
                renderer.camera.move((-32, 0))
            elif event.key == pygame.K_d:
                renderer.camera.move((32, 0))
                
        renderer.render()
        
pygame.quit()