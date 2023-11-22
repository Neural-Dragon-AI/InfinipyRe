import pygame
from infinipy.gridmap import GridMap
from sprites import SpriteGenerator
from entities import CharacterBlock, FloorBlock, TreasureBlock, WallBlock

class Camera:
    def __init__(self, pos=(0,0)):
        self.pos = list(pos) 
        
    def move(self, offset):
        self.pos[0] += offset[0]
        self.pos[1] += offset[1]

class Renderer:

    TILE_SIZE = 24
    RENDER_ORDER = [FloorBlock, WallBlock, TreasureBlock,CharacterBlock]

    def __init__(self, grid_map: GridMap):
        self.grid_map = grid_map
        self.sprite_gen = SpriteGenerator()
        self.camera = Camera()
        self.screen = pygame.display.set_mode((800, 600))

    def render(self):
        self.screen.fill((0,0,0))
        
        start_x = int(self.camera.pos[0] / Renderer.TILE_SIZE) 
        start_y = int(self.camera.pos[1] / Renderer.TILE_SIZE)
        
        for entity_type in Renderer.RENDER_ORDER:
            for entity in self.grid_map.get_all_entities():
                if isinstance(entity, entity_type):
                    x, y = entity.position[:2]
                    if self.is_on_screen(x, y):
                        sprite = self.sprite_gen.get_sprite(entity)
                        draw_x = (x - start_x) * Renderer.TILE_SIZE
                        draw_y = (y - start_y) * Renderer.TILE_SIZE  
                        self.screen.blit(sprite, (draw_x, draw_y))

        pygame.display.flip()

    def is_on_screen(self, x, y):
        start_x = int(self.camera.pos[0] / Renderer.TILE_SIZE) 
        end_x = start_x + (self.screen.get_width() / Renderer.TILE_SIZE) + 1
        
        start_y = int(self.camera.pos[1] / Renderer.TILE_SIZE)
        end_y = start_y + (self.screen.get_height() / Renderer.TILE_SIZE) + 1
        
        return start_x <= x < end_x and start_y <= y < end_y