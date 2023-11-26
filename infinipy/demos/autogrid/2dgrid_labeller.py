import json
import pygame
import time
from popup import Popup, Button, LabelManager
import os

GRID_AREA_WIDTH = 800
LABEL_AREA_WIDTH = 400
screen_width = GRID_AREA_WIDTH + LABEL_AREA_WIDTH
screen_height = 800

class GridManager:
    def __init__(self, width, height, tile_size, image_name, output_path):
        self.grid_width = width
        self.grid_height = height
        self.tile_size = tile_size
        self.offset_x = 0
        self.offset_y = 0
        self.tile_notes = {}
        self.image_name = image_name
        self.active_note = None  # New attribute to keep track of the active note
        self.output_path = output_path

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

    def save_to_json(self, label_manager: LabelManager):
        print(f"Saving grid to JSON file {self.image_name}_grid.json")
        file_name = f"{self.image_name}_grid.json"
        #merge filename with output path
        file_name = os.path.join(self.output_path,file_name)
        save_data = {
            'tile_notes': {str(key): list(value) for key, value in self.tile_notes.items()},
            'grid_width': self.grid_width,
            'grid_height': self.grid_height,
            'tile_size': self.tile_size,
            'offset_x': self.offset_x,
            'offset_y': self.offset_y,
            'labels': label_manager.get_saved_labels()  # Get saved labels from LabelManager
        }
        with open(file_name, 'w') as f:
            json.dump(save_data, f)

    def load_from_json(self, label_manager: LabelManager):
        file_name = f"{self.image_name}_grid.json"
        #merge filename with output path
        file_name = os.path.join(self.output_path,file_name)
        try:
            with open(file_name, 'r') as f:
                loaded_data = json.load(f)
            
            self.tile_notes = {tuple(map(int, key.strip('()').split(','))): set(value) for key, value in loaded_data['tile_notes'].items()}
            self.grid_width = loaded_data['grid_width']
            self.grid_height = loaded_data['grid_height']
            self.tile_size = loaded_data['tile_size']
            self.offset_x = loaded_data['offset_x']
            self.offset_y = loaded_data['offset_y']
            
            # Load labels and update LabelManager
            if 'labels' in loaded_data:
                label_manager.set_saved_labels(loaded_data['labels'])
        except FileNotFoundError:
            print("Saved grid file not found.")

class KeyBindings:
    def __init__(self, grid_manager, label_manager):
        self.grid_manager = grid_manager
        self.label_manager = label_manager
        self.notes = {pygame.K_1: None, pygame.K_2: None, pygame.K_3: None, pygame.K_4: None, pygame.K_5: None}

    def update_bindings(self):
        labels = self.label_manager.get_labels()
        for i, label in enumerate(labels[:5]):
            self.notes[pygame.K_1 + i] = label

    def handle_key_event(self, event, mouse_pos):
        if not mouse_pos:
            return
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

    def handle_save_load(self, event, label_manager):
        if event.key == pygame.K_F5:
            self.grid_manager.save_to_json(label_manager)
        elif event.key == pygame.K_F8:
            print("Loading grid from JSON file...")
            self.grid_manager.load_from_json(label_manager)

    def handle_mouse_legend(self, mouse_pos, label_manager: LabelManager):
        for label, hitbox in label_manager.label_hitboxes.items():
            if hitbox.collidepoint(mouse_pos):
                # Do something with the clicked label
                self.grid_manager.active_note = label
                print(f"Label '{label}' was clicked")

    def get_grid_position(self, mouse_pos):
        col = (mouse_pos[0] - self.grid_manager.offset_x) // self.grid_manager.tile_size
        row = (mouse_pos[1] - self.grid_manager.offset_y) // self.grid_manager.tile_size
        return col, row


class Renderer:
    def __init__(self, screen, grid_manager, label_manager):
        self.screen = screen
        self.grid_manager = grid_manager
        self.label_manager = label_manager
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
        colors = self.label_manager.get_colors()

        for i, note in enumerate(tile_notes):
            note_color = colors.get(note, (255, 255, 255, 128))  # Default color if note not found
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
        if not mouse_pos:
            return
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

#    background_image = pygame.image.load(r'C:\Users\Tommaso\Documents\Dev\InfinipyRe\infinipy\demos\autogrid\2dbattlemap.png')

def main():
    pygame.init()
    mouse_dragging = False
    last_drag_time = 0
    drag_interval = 0.1  # Time interval for dragging
    # Use double buffering for smoother updates
    screen = pygame.display.set_mode((GRID_AREA_WIDTH+LABEL_AREA_WIDTH, screen_height), pygame.HWSURFACE | pygame.DOUBLEBUF)
    current_path = os.path.dirname(__file__)
    output_path = os.path.join(current_path, 'outs')
    folder_name = 'maps'
    image_name = 'topdowndungeon.png'
    image_path = os.path.join(current_path, folder_name,image_name)
    # screen = pygame.display.set_mode((GRID_AREA_WIDTH + LABEL_AREA_WIDTH, screen_height))
    background_image = pygame.image.load(image_path)
    background_image = pygame.transform.scale(background_image, (GRID_AREA_WIDTH, screen_height))
    print(f"Image size: {background_image.get_size()}")

    grid_manager = GridManager(20, 20, 40, image_name,output_path)
    label_manager = LabelManager(screen,
                                 button_area=(GRID_AREA_WIDTH + 10, 10, 180, 30),
                                 popup_area=(GRID_AREA_WIDTH + 10, 50, 180, 30),    
                                 color_box_area=(GRID_AREA_WIDTH + 10, 90, 32, 32),
                                 legend_area=(GRID_AREA_WIDTH + 10, 130, 180, screen_height - 130))
    key_bindings = KeyBindings(grid_manager, label_manager)
    renderer = Renderer(screen, grid_manager, label_manager)

    running = True
    while running:
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()
        adjusted_mouse_pos = None  # Declare the variable outside the loop
        
        # Determine if the mouse is in the grid area or label area
        if mouse_pos[0] < GRID_AREA_WIDTH:
            adjusted_mouse_pos = (mouse_pos[0], mouse_pos[1])
            grid_mouse_pos = adjusted_mouse_pos
        else:
            grid_mouse_pos = None
        label_mouse_pos = mouse_pos if mouse_pos[0] >= GRID_AREA_WIDTH else None

        for event in events:
            if event.type == pygame.QUIT:
                running = False

            # Handle key events and mouse drags only in the grid area
            if grid_mouse_pos and event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.KEYDOWN]:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_dragging = True
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    mouse_dragging = False
                elif event.type == pygame.KEYDOWN:
                    key_bindings.handle_key_event(event, grid_mouse_pos)
                    key_bindings.update_bindings()
                    if event.key in [pygame.K_F5, pygame.K_F8]:
                        key_bindings.handle_save_load(event, label_manager)
       
                
            # Handle label manager events in the label area
            if label_mouse_pos and event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.KEYDOWN]:
                label_manager.handle_events(events)
                #update the gridmanger with active label
                key_bindings.handle_mouse_legend(mouse_pos, label_manager)


        # Drawing
        
        screen.blit(background_image, (0, 0))
        if mouse_dragging and time.time() - last_drag_time > drag_interval:
            if grid_mouse_pos:
                grid_manager.handle_mouse_dragging(grid_mouse_pos)
                last_drag_time = time.time()

        renderer.draw_grid_and_annotations()

      
        screen.fill((0, 0, 0), (GRID_AREA_WIDTH + 10, 50, 280, 30))
        label_manager.draw()  # Draw in the label area
        if grid_mouse_pos:
            renderer.display_info(grid_mouse_pos)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
