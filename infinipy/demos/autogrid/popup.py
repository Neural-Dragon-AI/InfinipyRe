import pygame

class Button:
    def __init__(self, x, y, width, height, text='', color=(0, 200, 0), font_size=32):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, font_size)
        self.clicked = False

    def draw(self, screen):
        # Draw button and text
        pygame.draw.rect(screen, self.color, self.rect)
        text_img = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_img.get_rect(center=self.rect.center)
        screen.blit(text_img, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.clicked = not self.clicked  # Toggle the clicked state
        return self.clicked
    
class Popup:
    def __init__(self, screen, input_box_area, color_box_area, color_options=None, font_size=32):
        self.screen = screen
        self.active = False
        self.input_box = pygame.Rect(*input_box_area)
        self.color_box_area = color_box_area  # This is a starting position and size for color boxes
        self.input_text = ''
        self.color_options = color_options if color_options else [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
        self.selected_color_index = 0
        self.used_colors = set()
        self.font = pygame.font.Font(None, font_size)

    def disable_used_colors(self, used_colors):
        self.used_colors = set(used_colors)

    def handle_event(self, event):
        if not self.active:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Calculate the position of the color box hitboxes based on color_box_area
            x, y, box_width, box_height = self.color_box_area
            for i, color in enumerate(self.color_options):
                # Use the same logic as in the draw method for positioning
                color_box = pygame.Rect(x + i * (box_width + 5), y, box_width, box_height)
                if color_box.collidepoint(event.pos) and color not in self.used_colors:
                    self.selected_color_index = i
                    # Capture the selected color and return the label text along with the selected color
                    color = self.color_options[self.selected_color_index]
                    label_text = self.input_text
                    self.input_text = ''  # Clear the input text
                    self.active = False  # Close the popup
                    return label_text, color

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                # # When Enter is pressed, deactivate the popup and clear the input text
                # self.active = False
                # label_text = self.input_text
                # self.input_text = ''  # Clear the input text for next input
                # color = self.color_options[self.selected_color_index]
                # return label_text, color
                pass
            elif event.key == pygame.K_BACKSPACE:
                # Remove the last character in the input text
                self.input_text = self.input_text[:-1]
            else:
                # Add the new character to the input text
                self.input_text += event.unicode

    def draw(self):
        # Draw the input box and text
        txt_surface = self.font.render(self.input_text, True, (255, 255, 255))
        width = max(200, txt_surface.get_width() + 10)
        self.input_box.w = width
        pygame.draw.rect(self.screen, (255, 255, 255), self.input_box, 2)
        self.screen.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 5))

        # Draw color options with disabled colors grayed out
        x, y, box_width, box_height = self.color_box_area
        for i, color in enumerate(self.color_options):
            color_box = pygame.Rect(x + i * (box_width + 5), y, box_width, box_height)
            color_to_draw = (128, 128, 128) if color in self.used_colors else color
            pygame.draw.rect(self.screen, color_to_draw, color_box)


class LabelManager:
    def __init__(self, screen, button_area=None, popup_area=None, color_box_area=None, legend_area=None, color_options=None, font_size=32):
        self.screen = screen
        # Default areas if not provided
        default_button_area = (screen.get_width() - 250, 50, 200, 50)
        default_popup_area = (screen.get_width() - 300, 150, 140, 32)
        default_color_box_area = (screen.get_width() - 300, 200, 32, 32)  # Example default starting position and size for color boxes
        default_legend_area = (10, 200, screen.get_width() - 20, screen.get_height() - 200)
        
        # Initialize Popup and Button with the given or default areas
        self.popup = Popup(screen, popup_area or default_popup_area, color_box_area or default_color_box_area, color_options, font_size)
        self.button = Button(*(button_area or default_button_area), text='Add Label', color=(0, 200, 0), font_size=font_size)
        self.legend_area = legend_area or default_legend_area
        self.saved_labels = {}
        self.font = pygame.font.Font(None, font_size)
        self.label_hitboxes = {}

    def get_saved_labels(self):
        return self.saved_labels
    
    def set_saved_labels(self, labels):
        # Convert color lists to tuples
        converted_labels = {label: tuple(color) for label, color in labels.items()}
        self.saved_labels = converted_labels

        # Now pass the converted label colors to disable_used_colors
        color_tuples = [tuple(color) for color in self.saved_labels.values()]
        self.popup.disable_used_colors(color_tuples)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP and self.button.rect.collidepoint(event.pos):
                # Toggle the popup on button click
                self.popup.active = not self.popup.active
                if not self.popup.active:
                    # Clear the input text if we are closing the popup
                    self.popup.input_text = ''
                # No need to check the result if we're closing the popup
                continue

            if self.popup.active:
                popup_result = self.popup.handle_event(event)
                if popup_result:
                    self.add_label(*popup_result)
    def add_label(self, label_name, color):
        if label_name and label_name not in self.saved_labels:
            self.saved_labels[label_name] = color
            self.popup.disable_used_colors(self.saved_labels.values())
            self.popup.active = False

    def toggle_popup(self):
        if self.popup.active:
            self.popup.active = False
            self.popup.input_text = ''
        else:
            self.popup.active = True

    def draw(self):
        self.button.draw(self.screen)
        self.draw_legend()
        if self.popup.active:
            self.popup.draw()

    def draw_legend(self):
        x, y, width, _ = self.legend_area
        self.label_hitboxes = {}  # Reset the hitboxes each time the legend is drawn
        for label, color in self.saved_labels.items():
            text_img = self.font.render(f"{label}", True, (0, 0, 0), color)
            text_rect = text_img.get_rect(topleft=(x, y))
            self.screen.blit(text_img, text_rect)
            self.label_hitboxes[label] = text_rect
            y += text_img.get_height() + 5  # Adjust y position for the next item
    def get_labels(self):
        # Return a list of label names
        return list(self.saved_labels.keys())
    
    def get_colors(self):
        # Return a dictionary of label colors
        return self.saved_labels

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    label_manager = LabelManager(screen)

    running = True
    while running:
        # We fill the screen once, so we don't do it again unless needed
        screen.fill((30, 30, 30))
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        label_manager.handle_events(events)

        # Drawing operations
        label_manager.draw()

        # Update the display only once per frame
        pygame.display.flip()
        clock.tick(60)  # Limit the frame rate to 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()


