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

    RENDER_ORDER = [FloorBlock, WallBlock, TreasureBlock, CharacterBlock]
    # RENDER_ORDER = [TreasureBlock, CharacterBlock]
    def __init__(self, grid_map: GridMap, tile_size=24, background_image_path=None, grid_alpha=50, highlight_alpha=50):
        # ... [rest of the existing __init__ code]
        self.grid_alpha = grid_alpha  # Transparency for the gridmap
        self.highlight_alpha = highlight_alpha  # Transparency for the highlights
        self.TILE_SIZE = tile_size
        self.grid_map = grid_map
        self.sprite_gen = SpriteGenerator(self.TILE_SIZE)
        self.camera = Camera()
        self.screen = pygame.display.set_mode((1600, 1200))
        self.active_source = None
        self.active_target = None
        # Calculate the grid size in pixels
        grid_width = grid_map.width * self.TILE_SIZE
        grid_height = grid_map.height * self.TILE_SIZE
        self.current_casted_cells = []
        print(f"Grid size: {grid_width} x {grid_height}")
        

        
        # Load and scale the background image to the grid size
        if background_image_path:
            self.background_image = pygame.image.load(background_image_path)
            self.background_image = pygame.transform.scale(self.background_image, (800, 800))
        else:
            self.background_image = None

        # Initialize the fog of war
        self.fog_of_war_surface = pygame.Surface((800, 800), pygame.SRCALPHA)
        self.fog_of_war_surface.fill((0, 0, 0, 255))  # Opaque fog
        self.revealed_cells = set()  # Keep track of cells that have been revealed
        self.visited_cells = set() # Keep track of cells that have been visited

    def update_fog_of_war(self, shadowcast_cells):
        # Reset fog for all cells to either opaque or grayed out if they were previously revealed
        for cell in self.revealed_cells:
            cell_2d = cell[:2]
            if cell_2d not in shadowcast_cells:
                # Apply a gray overlay to previously revealed cells
                self.fog_of_war_surface.fill((128, 128, 128, 128), (cell[0] * self.TILE_SIZE, cell[1] * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE))
            else:
                # Clear the fog for currently visible cells
                self.fog_of_war_surface.fill((0, 0, 0, 0), (cell[0] * self.TILE_SIZE, cell[1] * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE))

        # Update revealed cells with current shadowcast cells
        for cell in shadowcast_cells:
            cell_2d = cell[:2]
            self.revealed_cells.add(cell_2d)
            # Clear the fog for currently visible cells
            self.fog_of_war_surface.fill((0, 0, 0, 0), (cell[0] * self.TILE_SIZE, cell[1] * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE))


    def clear_fog_at(self, position):
        # Clear the fog by making the cell completely transparent
        self.fog_of_war_surface.fill((0, 0, 0, 0), (position[0] * self.TILE_SIZE, position[1] * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE))

  
    def calculate_screen_position(self, grid_x, grid_y):
        start_x = int(self.camera.pos[0] / self.TILE_SIZE)
        start_y = int(self.camera.pos[1] / self.TILE_SIZE)
        draw_x = (grid_x - start_x) * self.TILE_SIZE
        draw_y = (grid_y - start_y) * self.TILE_SIZE
        return draw_x, draw_y

    def draw_transparent_rect(self, position, color, alpha=None):
        if alpha is None:
            alpha = self.highlight_alpha
        if self.is_on_screen(*position):
            draw_x, draw_y = self.calculate_screen_position(*position)
            transparent_surface = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
            transparent_color = color + (alpha,)
            transparent_surface.fill(transparent_color)
            self.screen.blit(transparent_surface, (draw_x, draw_y))

    def render_grid_map(self):
        # The grid surface will no longer have a global alpha set.
        # Instead, each sprite will handle its own transparency.
        start_x = int(self.camera.pos[0] / self.TILE_SIZE) 
        start_y = int(self.camera.pos[1] / self.TILE_SIZE)
        
        for entity_type in Renderer.RENDER_ORDER:
            for entity in self.grid_map.get_all_entities():
                if isinstance(entity, entity_type) and (entity.position[:2]) in self.current_casted_cells:
                    x, y = entity.position[:2]
                    if self.is_on_screen(x, y):
                        sprite = self.sprite_gen.get_sprite(entity)
                        # Ensure your sprites have an alpha channel and are not drawn with a black background.
                        draw_x, draw_y = self.calculate_screen_position(x, y)
                        self.screen.blit(sprite, (draw_x, draw_y))  # Blit directly onto the screen.


    def render_source_target(self):
        if self.active_source:
            self.draw_transparent_rect(self.active_source, (153, 255, 153))  # Light green color

        if self.active_target:
            self.draw_transparent_rect(self.active_target, (204, 153, 255))  # Light purple color

    def render_a_star_path(self):
        if self.active_source and self.active_target:
            source_position = self.active_source + (0,)
            target_position = self.active_target + (0,)
            path = self.grid_map.a_star(source_position, target_position)
            if path:
                for position3d in path:
                    position2d = position3d[:2]
                    self.draw_transparent_rect(position2d, (255, 255, 0))  # Yellow color for the path
    
    def render_shadowcast(self):
            if self.active_source:
                shadowcast_origin = self.active_source + (0,)
                shadowcast_cells = self.grid_map.shadow_casting(shadowcast_origin, max_radius=10)
                self.current_casted_cells = [cell[:2] for cell in shadowcast_cells]
                self.update_fog_of_war(shadowcast_cells)
                # self.current_casted_cells = []
                # # Highlight each cell in shadowcast
                # for cell in shadowcast_cells:
                #     cell_2d = cell[:2]  # Remove the Z axis
                #     self.current_casted_cells.append(cell_2d)
                #     self.draw_transparent_rect(cell_2d, (0, 0, 255))  # Transparent blue color

    def render(self):
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill((128, 128, 128))
        self.render_grid_map()
        self.render_source_target()
        
        self.render_a_star_path()
        self.render_shadowcast()
        # Blit the fog of war last, so it's on top of everything else
        self.screen.blit(self.fog_of_war_surface, (0, 0))
        self.render_mouse_info()
        pygame.display.flip()

    def is_on_screen(self, x, y):
        start_x = int(self.camera.pos[0] / self.TILE_SIZE) 
        end_x = start_x + (self.screen.get_width() / self.TILE_SIZE) + 1
        start_y = int(self.camera.pos[1] / self.TILE_SIZE)
        end_y = start_y + (self.screen.get_height() / self.TILE_SIZE) + 1
        return start_x <= x < end_x and start_y <= y < end_y

    def get_grid_coordinates(self, pixel_x, pixel_y):
        grid_x = (pixel_x + self.camera.pos[0]) // self.TILE_SIZE
        grid_y = (pixel_y + self.camera.pos[1]) // self.TILE_SIZE
        return grid_x, grid_y

    def render_mouse_info(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x, grid_y = self.get_grid_coordinates(mouse_x, mouse_y)
        font = pygame.font.Font(None, 24)
        info_text = font.render(f'Mouse: ({mouse_x}, {mouse_y}), Grid: ({grid_x}, {grid_y})', True, (255, 255, 255))
        self.screen.blit(info_text, (10, 10))
        entities_at_pos = self.grid_map.get_entities_at_position((grid_x, grid_y, 0))
        y_offset = 30
        for entity in entities_at_pos:
            entity_info = f"{entity.__class__.__name__}, Name: {entity.name}"
            entity_text = font.render(entity_info, True, (255, 255, 255))
            self.screen.blit(entity_text, (10, 10 + y_offset))
            y_offset += 20
        if self.active_source:
            source_text = font.render(f"Source: {self.active_source}", True, (255, 255, 255))
            self.screen.blit(source_text, (10, 10 + y_offset))
            y_offset += 20
        if self.active_target:
            target_text = font.render(f"Target: {self.active_target}", True, (255, 255, 255))
            self.screen.blit(target_text, (10, 10 + y_offset))
        #display the total number of cells
        y_offset += 20
        total_cells_text = font.render(f"Total cells: {self.grid_map.width * self.grid_map.height}", True, (255, 255, 255))
        self.screen.blit(total_cells_text, (10, 10 + y_offset))
        #display the number of visited cells and number of seen
        #and number of seen but not visited
        y_offset += 20
        visited_text = font.render(f"Visited: {len(self.visited_cells)}", True, (255, 255, 255))
        self.screen.blit(visited_text, (10, 10 + y_offset))
        y_offset += 20
        seen_text = font.render(f"Seen: {len(self.revealed_cells)}", True, (255, 255, 255))
        self.screen.blit(seen_text, (10, 10 + y_offset))
        y_offset += 20
        seen_unvisited_text = font.render(f"Seen but not visited: {len(self.get_seen_unvisited_cells())}", True, (255, 255, 255))
        self.screen.blit(seen_unvisited_text, (10, 10 + y_offset))
    def get_seen_unvisited_cells(self):
        """Returns the cells that have been seen but not visited."""
        return self.revealed_cells - self.visited_cells
    def set_active_source_from_grid(self, source_grid_cord):
        self.active_source = source_grid_cord
        self.visited_cells.add(self.active_source)

    def set_active_source(self, source_mouse_cord):
        self.active_source = self.get_grid_coordinates(*source_mouse_cord)
        self.visited_cells.add(self.active_source)
    
    def set_active_target(self, target_mouse_cord):
        self.active_target = self.get_grid_coordinates(*target_mouse_cord)
    
    def set_active_target_from_grid(self, target_grid_cord):
        self.active_target = target_grid_cord
    
    def reset_active_source(self):
        self.active_source = None
    
    def reset_active_target(self):
        self.active_target = None
