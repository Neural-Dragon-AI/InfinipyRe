import random
from typing import Dict, List
from infinipy.stateblock import StateBlock
from collections import defaultdict
import pygame

class SpriteGenerator:

    SPRITE_MAP = {
        "CharacterBlock": [ pygame.image.load(r"C:\Users\Tommaso\Documents\Dev\InfinipyRe\infinipy\demos\maze_navigation_pygame\assets\sprites\character_agent.png")], 
        "FloorBlock": [pygame.image.load(r"C:\Users\Tommaso\Documents\Dev\InfinipyRe\infinipy\demos\maze_navigation_pygame\assets\sprites\floor.png")],
        "TreasureBlock": [pygame.image.load(r"C:\Users\Tommaso\Documents\Dev\InfinipyRe\infinipy\demos\maze_navigation_pygame\assets\sprites\storage.png")],
        "WallBlock": [pygame.image.load(r"C:\Users\Tommaso\Documents\Dev\InfinipyRe\infinipy\demos\maze_navigation_pygame\assets\sprites\wall.png")]
    }

    def __init__(self):
        self.used_sprites = defaultdict(list)

    def get_sprite(self, entity: StateBlock) -> str:
        entity_type = type(entity).__name__  
        available_sprites = self.SPRITE_MAP.get(entity_type, [])
        
        if not available_sprites:
            raise ValueError(f"No sprites defined for {entity_type}")

        sprite = random.choice(available_sprites)
        
        self.used_sprites[entity_type].append(sprite)

        return sprite