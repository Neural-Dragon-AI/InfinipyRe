import random
from typing import Dict, List
from infinipy.stateblock import StateBlock
from collections import defaultdict
import pygame
import os
current_file_path = os.path.dirname(os.path.abspath(__file__))
sprites_folder = os.path.join(current_file_path, 'assets', 'sprites')
character_path = os.path.join(sprites_folder, 'character_agent.png')
floor_path = os.path.join(sprites_folder, 'floor.png')
storage_path = os.path.join(sprites_folder, 'storage.png')
wall_path = os.path.join(sprites_folder, 'wall.png')

class SpriteGenerator:
    SPRITE_MAP = {
        "CharacterBlock": [pygame.image.load(character_path)], 
        "FloorBlock": [pygame.image.load(floor_path)],
        "TreasureBlock": [pygame.image.load(storage_path)],
        "WallBlock": [pygame.image.load(wall_path)]
    }

    def __init__(self, tile_size):
        self.tile_size = tile_size
        self.used_sprites = defaultdict(list)
        self.resized_sprites = self.resize_sprites()

    def resize_sprites(self):
        resized = {}
        for entity_type, sprites in self.SPRITE_MAP.items():
            resized[entity_type] = [pygame.transform.scale(sprite, (self.tile_size, self.tile_size)) for sprite in sprites]
        return resized

    def get_sprite(self, entity: StateBlock) -> pygame.Surface:
        entity_type = type(entity).__name__  
        available_sprites = self.resized_sprites.get(entity_type, [])
        
        if not available_sprites:
            raise ValueError(f"No sprites defined for {entity_type}")

        sprite = random.choice(available_sprites)
        self.used_sprites[entity_type].append(sprite)

        return sprite