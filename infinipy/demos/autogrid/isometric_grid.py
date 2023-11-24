import pygame
import sys
import os

# Define a function to create an isometric grid
def draw_isometric_grid(surface, tile_size, offset_x, offset_y, angle,num_tiles_x=10, num_tiles_y=10):
    # Constants
    cos_angle = pygame.math.Vector2(1, 0).rotate(angle).x
    sin_angle = pygame.math.Vector2(1, 0).rotate(angle).y

    # Colors
    line_color = (255, 255, 255)  # White color for the grid lines

    # Get the surface dimensions
    width, height = surface.get_size()

    # # Calculate the number of tiles to be drawn
    # num_tiles_x = width // tile_size + 2
    # num_tiles_y = height // tile_size + 2

    # Draw the grid
    for y in range(-1, num_tiles_y):
        for x in range(-1, num_tiles_x):
            # Calculate the base points for the tile
            base_x = x * tile_size
            base_y = y * tile_size

            # Calculate the isometric projection
            iso_x = (base_x - base_y) * cos_angle
            iso_y = (base_x + base_y) * sin_angle / 2

            # Apply the offset
            final_x = iso_x + offset_x
            final_y = iso_y + offset_y

            # Points of the isometric tile
            points = [
                (final_x, final_y),
                (final_x + tile_size * cos_angle, final_y + tile_size * sin_angle / 2),
                (final_x, final_y + tile_size * sin_angle),
                (final_x - tile_size * cos_angle, final_y + tile_size * sin_angle / 2),
            ]

            # Draw the tile
            pygame.draw.polygon(surface, line_color, points, 1)  # The '1' specifies the line thickness

# Initialize pygame
pygame.init()

# Set up the display
pygame.display.set_caption("Isometric Grid with Background")
window_size = (800, 600)
screen = pygame.display.set_mode(window_size)

# Load the background image
try:
    background_image = pygame.image.load(r'C:\Users\Tommaso\Documents\Dev\InfinipyRe\infinipy\demos\map.png')
    background_image = pygame.transform.scale(background_image, window_size)
except pygame.error as e:
    print(f'Could not load image: {e}')
    sys.exit()
# Default grid parameters
tile_size = 50
offset_x = window_size[0] // 2
offset_y = window_size[1] // 2
angle = 45
width, height = screen.get_size()
num_tiles_x = width // tile_size + 2
num_tiles_y = height // tile_size + 2

def handle_event(event,running, tile_size, offset_x, offset_y, angle,num_tiles_x, num_tiles_y):
    if event.type == pygame.QUIT:
            running = False
    
    # Handle key events for changing grid parameters
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            tile_size += 5
        elif event.key == pygame.K_DOWN:
            tile_size -= 5
        elif event.key == pygame.K_LEFT:
            angle -= 5
        elif event.key == pygame.K_RIGHT:
            angle += 5
        elif event.key == pygame.K_w:
            offset_y -= 5
        elif event.key == pygame.K_s:
            offset_y += 5
        elif event.key == pygame.K_a:
            offset_x -= 5
        elif event.key == pygame.K_d:
                offset_x += 5
        elif event.key == pygame.K_1:
            num_tiles_x += 1
        elif event.key == pygame.K_2:
            num_tiles_x -= 1
        elif event.key == pygame.K_3:
            num_tiles_y += 1
        elif event.key == pygame.K_4:
            num_tiles_y -= 1

    return tile_size, offset_x, offset_y, angle, running,num_tiles_x, num_tiles_y


# Main loop
running = True
while running:
    for event in pygame.event.get():
        tile_size, offset_x, offset_y, angle, running,num_tiles_x, num_tiles_y = handle_event(event, running, tile_size, offset_x, offset_y, angle,num_tiles_x, num_tiles_y)
        
    screen.blit(background_image, (0, 0))
    # Redraw the grid with updated parameters
    draw_isometric_grid(screen, tile_size, offset_x, offset_y, angle,num_tiles_x, num_tiles_y)

    # Update the display
    pygame.display.flip()

# Quit pygame
pygame.quit()
sys.exit()
