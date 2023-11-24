import json
import pygame
import time

class GridManager:
    def __init__(self, width, height, tile_size, image_name):
        self.grid_width = width
        self.grid_height = height
        self.tile_size = tile_size
        self.offset_x = 0
        self.offset_y = 0
        self.tile_notes = {}
        self.image_name = image_name
        self.active_note = None  # New attribute to keep track of the active note

    def handle_mouse_dragging(self, mouse_pos):
        current_time = time.time()
        col = (mouse_pos[0] - self.offset_x) // self.tile_size
        row = (mouse_pos[1] - self.offset_y) // self.tile_size
        if 0 <= col < self.grid_width and 0 <= row < self.grid_height:
            if self.active_note:
                if (col, row) not in self.tile_notes:
                    self.tile_notes[(col, row)] = set()
                self.tile_notes[(col, row)].add(self.active_note)

    def adjust_grid(self, width_change=0, height_change=0, tile_size_change=0):
        self.grid_width += width_change
        self.grid_height += height_change
        self.tile_size += tile_size_change

        # Ensure tile size remains valid
        self.tile_size = max(1, self.tile_size)

    def adjust_offset(self, x_change=0, y_change=0):
        self.offset_x += x_change
        self.offset_y += y_change

    def add_annotation(self, col, row, note):
        if (col, row) not in self.tile_notes:
            self.tile_notes[(col, row)] = set()
        self.tile_notes[(col, row)].add(note)

    def remove_annotations(self, col, row):
        self.tile_notes.pop((col, row), None)

    def save_to_json(self):
        file_name = f"{self.image_name}_grid.json"
        # Convert tuple keys to strings and set values to lists
        save_data = {str(key): list(value) for key, value in self.tile_notes.items()}
        with open(file_name, 'w') as f:
            json.dump(save_data, f)



    def load_from_json(self):
        file_name = f"{self.image_name}_grid.json"
        try:
            with open(file_name, 'r') as f:
                loaded_data = json.load(f)
            # Convert string keys back to tuples and list values back to sets
            self.tile_notes = {tuple(map(int, key.strip('()').split(','))): set(value) for key, value in loaded_data.items()}
        except FileNotFoundError:
            print("Saved grid file not found.")



class KeyBindings:
    def __init__(self, grid_manager):
        self.grid_manager = grid_manager
        self.active_note = None
        self.notes = {
            pygame.K_1: 'floor',
            pygame.K_2: 'wall',
            pygame.K_3: 'rubbles',
            pygame.K_4: 'void',
            pygame.K_0: None
        }

    def handle_key_event(self, event, mouse_pos):
        
        if event.key in self.notes:
            self.grid_manager.active_note = self.notes[event.key] 
        elif event.key == pygame.K_LEFT:
            self.grid_manager.adjust_offset(x_change=5)
        elif event.key == pygame.K_RIGHT:
            self.grid_manager.adjust_offset(x_change=-5)
        elif event.key == pygame.K_UP:
            self.grid_manager.adjust_offset(y_change=5)
        elif event.key == pygame.K_DOWN:
            self.grid_manager.adjust_offset(y_change=-5)
        elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
            self.grid_manager.adjust_grid(tile_size_change=1)
        elif event.key == pygame.K_MINUS:
            self.grid_manager.adjust_grid(tile_size_change=-1)
        elif event.key == pygame.K_w:
            self.grid_manager.adjust_grid(height_change=1)
        elif event.key == pygame.K_s:
            self.grid_manager.adjust_grid(height_change=-1)
        elif event.key == pygame.K_a:
            self.grid_manager.adjust_grid(width_change=1)
        elif event.key == pygame.K_d:
            self.grid_manager.adjust_grid(width_change=-1)
        elif event.key == pygame.K_r:
            if event.key == pygame.K_r:
                col, row = self.get_grid_position(mouse_pos)
                self.grid_manager.remove_annotations(col, row)

        elif event.key == pygame.K_F5:
            self.grid_manager.save_to_json()
        elif event.key == pygame.K_F8:
            print("Loading grid from JSON file...")
            self.grid_manager.load_from_json()
    
    def get_grid_position(self, mouse_pos):
        col = (mouse_pos[0] - self.grid_manager.offset_x) // self.grid_manager.tile_size
        row = (mouse_pos[1] - self.grid_manager.offset_y) // self.grid_manager.tile_size
        return col, row

import pygame

class Renderer:
    def __init__(self, screen, grid_manager):
        self.screen = screen
        self.grid_manager = grid_manager
        self.colors = {
            'floor': (0, 255, 0, 128),
            'wall': (255, 0, 0, 128),
            'rubbles': (0, 0, 255, 128),
            'void': (255, 255, 0, 128),
            'default': (255, 255, 255, 128)
        }
        self.font = pygame.font.SysFont(None, 24)

    def draw_grid_and_annotations(self):
        surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)

        for row in range(self.grid_manager.grid_height):
            for col in range(self.grid_manager.grid_width):
                x = col * self.grid_manager.tile_size + self.grid_manager.offset_x
                y = row * self.grid_manager.tile_size + self.grid_manager.offset_y
                tile_notes = self.grid_manager.tile_notes.get((col, row), set())
                rect = pygame.Rect(x, y, self.grid_manager.tile_size, self.grid_manager.tile_size)
                if tile_notes:
                    self.draw_multi_color_tile(surface, x, y, tile_notes)
                else:
                    rect = pygame.Rect(x, y, self.grid_manager.tile_size, self.grid_manager.tile_size)
                    # pygame.draw.rect(surface, self.colors['default'], rect)
                    continue  

        # Draw the grid lines
        self.draw_grid_lines(surface)

        self.screen.blit(surface, (0, 0))

    def draw_multi_color_tile(self, surface, x, y, tile_notes):
        note_count = len(tile_notes)
        segment_height = self.grid_manager.tile_size // note_count

        for i, note in enumerate(tile_notes):
            note_color = self.colors.get(note, self.colors['default'])
            rect = pygame.Rect(x, y + i * segment_height, self.grid_manager.tile_size, segment_height)
            pygame.draw.rect(surface, note_color, rect)

    def draw_grid_lines(self, surface):
        for col in range(self.grid_manager.grid_width + 1):
            x = col * self.grid_manager.tile_size + self.grid_manager.offset_x
            pygame.draw.line(surface, (255, 255, 255, 255), (x, self.grid_manager.offset_y), (x, self.grid_manager.grid_height * self.grid_manager.tile_size + self.grid_manager.offset_y))

        for row in range(self.grid_manager.grid_height + 1):
            y = row * self.grid_manager.tile_size + self.grid_manager.offset_y
            pygame.draw.line(surface, (255, 255, 255, 255), (self.grid_manager.offset_x, y), (self.grid_manager.grid_width * self.grid_manager.tile_size + self.grid_manager.offset_x, y))


    def display_info(self, mouse_pos):
        col = (mouse_pos[0] - self.grid_manager.offset_x) // self.grid_manager.tile_size
        row = (mouse_pos[1] - self.grid_manager.offset_y) // self.grid_manager.tile_size

        # Display the currently active note
        active_note_text = f'Active Note: {self.grid_manager.active_note if self.grid_manager.active_note else "None"}'
        active_note_info = self.font.render(active_note_text, True, (255, 255, 255))
        self.screen.blit(active_note_info, (10, 55))

        # Display the grid information
        grid_info = self.font.render(f'Grid: {self.grid_manager.grid_width}x{self.grid_manager.grid_height}, Tile: {self.grid_manager.tile_size}px', True, (255, 255, 255))
        self.screen.blit(grid_info, (10, 10))

        # Display the position and note information for the tile under the mouse cursor
        if 0 <= col < self.grid_manager.grid_width and 0 <= row < self.grid_manager.grid_height:
            notes = self.grid_manager.tile_notes.get((col, row), set())
            note_info = self.font.render(f'Pos: ({col}, {row}), Notes: {", ".join(notes) if notes else "None"}', True, (255, 255, 255))
            self.screen.blit(note_info, (10, 35))

def main():
    pygame.init()
    mouse_dragging = False
    last_drag_time = 0
    drag_interval = 0.1  # Time interval for dragging
    # Set up the screen and background image
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    background_image = pygame.image.load(r'C:\Users\Tommaso\Documents\Dev\InfinipyRe\infinipy\demos\autogrid\2dbattlemap.png')
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

    # Initialize the classes
    grid_manager = GridManager(20, 20, 40, '2dbattlemap.png')
    key_bindings = KeyBindings(grid_manager)
    renderer = Renderer(screen, grid_manager)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                mouse_dragging = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Left click released
                mouse_dragging = False
            elif event.type == pygame.KEYDOWN:
                key_bindings.handle_key_event(event, mouse_pos)

        if mouse_dragging and time.time() - last_drag_time > drag_interval:
            grid_manager.handle_mouse_dragging(mouse_pos)
            last_drag_time = time.time()
      
         

        # Drawing
        screen.blit(background_image, (0, 0))
        renderer.draw_grid_and_annotations()
        renderer.display_info(mouse_pos)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
