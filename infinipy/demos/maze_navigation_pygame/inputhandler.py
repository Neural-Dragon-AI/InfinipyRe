import pygame
from renderer import Renderer
from typing import List, Optional
from infinipy.stateblock import StateBlock
from infinipy.gridmap import GridMap

class InputHandler:
    def __init__(self, renderer: Renderer):
        self.renderer = renderer

    def handle_events(self, events: List[pygame.event.Event], active_entity: Optional[StateBlock] = None , gridmap: Optional[GridMap] = None):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.handle_keyboard(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse(event)
                if active_entity:
                    self.handle_mouse_entity_event(event, active_entity, gridmap)

    def handle_keyboard(self, event: pygame.event.Event):
        # Handle keyboard inputs
        if event.key == pygame.K_w:
            self.renderer.camera.move((0, -32))
        elif event.key == pygame.K_s:
            self.renderer.camera.move((0, 32))
        elif event.key == pygame.K_a:
            self.renderer.camera.move((-32, 0))
        elif event.key == pygame.K_d:
            self.renderer.camera.move((32, 0))

    def handle_mouse(self, event: pygame.event.Event):
        mouse_pos = pygame.mouse.get_pos()

        if event.button == 1:  # Left click
            current_source = self.renderer.get_grid_coordinates(*mouse_pos)
            if current_source  in self.renderer.revealed_cells:
                
                if self.renderer.active_source == current_source:
                    self.renderer.reset_active_source()
                else:
                    self.renderer.set_active_source(mouse_pos)

        elif event.button == 3:  # Right click
            current_target = self.renderer.get_grid_coordinates(*mouse_pos)
            if self.renderer.active_target == current_target:
                self.renderer.reset_active_target()
            else:
                self.renderer.set_active_target(mouse_pos)
    
    def handle_mouse_entity_event(self, event: pygame.event.Event, active_entity: StateBlock, gridmap: GridMap):
        mouse_pos = pygame.mouse.get_pos()
        if event.button == 1:
            pos2d = self.renderer.get_grid_coordinates(*mouse_pos)
            posd3d = pos2d + (0,)
            gridmap.move_entity(active_entity, posd3d)