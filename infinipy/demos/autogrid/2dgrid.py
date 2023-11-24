import pygame
import sys
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width, screen_height = 800, 600

# Load the background image
background_image = pygame.image.load(r'C:\Users\Tommaso\Documents\Dev\InfinipyRe\infinipy\demos\autogrid\2dbattlemap.png')
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

# Application state
state = {
    'grid_params': {
        'tile_size': 40,
        'grid_width': 20,  # Adjust as necessary for the image size
        'grid_height': 20,  # Adjust as necessary for the image size
        'offset_x': 0,
        'offset_y': 0,
    },
    'active_note': None,
    'mouse_dragging': False,
    'last_drag_time': 0,
    'tile_notes': {},
    'notes': {
        pygame.K_1: 'floor',
        pygame.K_2: 'wall',
        pygame.K_3: 'rubbles',
        pygame.K_4: 'void',
        pygame.K_0: None
    }
}

# Create the screen
screen = pygame.display.set_mode((screen_width, screen_height))

# Colors with alpha for semi-transparent annotation
colors = {
    'floor': (0, 255, 0, 128),  # Green with alpha
    'wall': (255, 0, 0, 128),   # Red with alpha
    'rubbles': (0, 0, 255, 128), # Blue with alpha
    'void': (255, 255, 0, 128),  # Yellow with alpha
    'default': (255, 255, 255, 128)  # White with alpha for non-labeled tiles
}

# Function to draw the grid and annotations with transparency
# Function to draw the grid and annotations with transparency
def draw_grid_and_annotations(state):
    params = state['grid_params']
    surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    tile_size = params['tile_size']
    # Adjust the starting position of the grid to account for the grid lines
    start_x = params['offset_x'] + 1
    start_y = params['offset_y'] + 1
    
    # Draw the annotations with transparency
    for row in range(params['grid_height']):
        for col in range(params['grid_width']):
            x = col * tile_size + start_x
            y = row * tile_size + start_y
            rect = pygame.Rect(x, y, tile_size - 1, tile_size - 1)  # Subtract 1 to account for the grid line
            notes = state['tile_notes'].get((col, row), set())
            if notes:
                note_color = colors.get(list(notes)[-1], colors['default'])
                pygame.draw.rect(surface, note_color, rect)

    # Draw the grid lines
    # Vertical lines
    for col in range(params['grid_width'] + 1):
        x = col * tile_size + start_x
        pygame.draw.line(surface, (255, 255, 255, 255), (x - 1, start_y), (x - 1, params['grid_height'] * tile_size + start_y))

    # Horizontal lines
    for row in range(params['grid_height'] + 1):
        y = row * tile_size + start_y
        pygame.draw.line(surface, (255, 255, 255, 255), (start_x, y - 1), (params['grid_width'] * tile_size + start_x, y - 1))

    # Blit the background and the surface with annotations and grid lines
    screen.blit(background_image, (0, 0))
    screen.blit(surface, (0, 0))


# Function to display grid information and notes
def display_info(state, mouse_pos):
    white = (255, 255, 255)
    font = pygame.font.SysFont(None, 24)
    params = state['grid_params']
    grid_info = font.render(f'Position: ({params["offset_x"]}, {params["offset_y"]}), Size: {params["tile_size"]}px, Grid: {params["grid_width"]}x{params["grid_height"]}', True, white)
    screen.blit(grid_info, (screen_width - grid_info.get_width() - 10, 10))

    # Display the active note
    active_note = state['active_note']
    active_note_text = f'Active Note: {active_note}' if active_note else 'Active Note: None'
    active_note_info = font.render(active_note_text, True, white)
    screen.blit(active_note_info, (screen_width - active_note_info.get_width() - 10, 35))

    # Display notes for the tile under the mouse cursor
    col = (mouse_pos[0] - params['offset_x']) // params['tile_size']
    row = (mouse_pos[1] - params['offset_y']) // params['tile_size']
    if 0 <= col < params['grid_width'] and 0 <= row < params['grid_height']:
        tile_note = state['tile_notes'].get((col, row), set())
        note_text = ', '.join(tile_note) if tile_note else 'None'
        note_info = font.render(f'Notes: {note_text}', True, white)
        screen.blit(note_info, (10, 10))

# Function to handle key inputs
def handle_keys(event, state):
    if event.type == pygame.KEYDOWN:
        if event.key in state['notes']:
            state['active_note'] = state['notes'][event.key]
        elif event.key == pygame.K_LEFT:
            state['grid_params']['offset_x'] += 5
        elif event.key == pygame.K_RIGHT:
            state['grid_params']['offset_x'] -= 5
        elif event.key == pygame.K_UP:
            state['grid_params']['offset_y'] += 5
        elif event.key == pygame.K_DOWN:
            state['grid_params']['offset_y'] -= 5
        elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
            state['grid_params']['tile_size'] += 1
        elif event.key == pygame.K_MINUS and state['grid_params']['tile_size'] > 1:
            state['grid_params']['tile_size'] -= 1
        elif event.key == pygame.K_w:
            state['grid_params']['grid_height'] += 1
        elif event.key == pygame.K_s and state['grid_params']['grid_height'] > 1:
            state['grid_params']['grid_height'] -= 1
        elif event.key == pygame.K_a:
            state['grid_params']['grid_width'] += 1
        elif event.key == pygame.K_d and state['grid_params']['grid_width'] > 1:
            state['grid_params']['grid_width'] -= 1

# Function to handle mouse dragging
def handle_mouse_dragging(mouse_pos, state):
    current_time = time.time()
    if current_time - state['last_drag_time'] > 0.1:  # 0.1 second threshold for dragging
        col = (mouse_pos[0] - state['grid_params']['offset_x']) // state['grid_params']['tile_size']
        row = (mouse_pos[1] - state['grid_params']['offset_y']) // state['grid_params']['tile_size']
        if 0 <= col < state['grid_params']['grid_width'] and 0 <= row < state['grid_params']['grid_height']:
            if state['active_note']:
                if (col, row) not in state['tile_notes']:
                    state['tile_notes'][(col, row)] = set()
                state['tile_notes'][(col, row)].add(state['active_note'])
        state['last_drag_time'] = current_time

# Main loop
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            state['mouse_dragging'] = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Left click released
            state['mouse_dragging'] = False
        
        # Handle key inputs
        handle_keys(event, state)

    if state['mouse_dragging']:
        handle_mouse_dragging(mouse_pos, state)

    # Drawing
    draw_grid_and_annotations(state)
    display_info(state, mouse_pos)
    pygame.display.flip()  # Update the display

pygame.quit()