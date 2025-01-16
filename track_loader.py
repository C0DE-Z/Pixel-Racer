import pygame

class TrackLoader:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        
        self.bg_color = (0, 0, 0)
        self.text_color = (255, 215, 0)

    def draw(self):
        self.screen.fill(self.bg_color)
        title = self.font.render("Track Loader", True, self.text_color)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return "replay"
            elif event.key == pygame.K_n:
                return "new"
        return None
