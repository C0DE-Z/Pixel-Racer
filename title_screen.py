import pygame

class TitleScreen:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        
        # Colors - Easy to customize
        self.bg_color = (0, 0, 0)
        self.text_color = (255, 255, 255)
        self.highlight_color = (255, 0, 0)
        
        # Text content - Easy to modify
        self.title_text = "PIXEL RACER"
        self.start_text = "Press SPACE to Start"
        self.controls = [
            "Controls:",
            "WASD - Drive",
            "SPACE - Drift",
            "SHIFT/CTRL - Gear shift",
            "R - Reset position",
            "H - Debug mode"
        ]

    def draw(self):
        self.screen.fill(self.bg_color)
        
        # Draw title
        title_surface = self.font.render(self.title_text, True, self.text_color)
        title_rect = title_surface.get_rect(center=(self.width//2, self.height//3))
        self.screen.blit(title_surface, title_rect)
        
        # Draw start prompt
        start_surface = self.small_font.render(self.start_text, True, self.text_color)
        start_rect = start_surface.get_rect(center=(self.width//2, self.height//2))
        self.screen.blit(start_surface, start_rect)
        
        # Draw controls
        for i, control in enumerate(self.controls):
            control_surface = self.small_font.render(control, True, self.text_color)
            control_rect = control_surface.get_rect(
                center=(self.width//2, self.height//2 + 50 + i * 30)
            )
            self.screen.blit(control_surface, control_rect)

    def update(self):
        # Add any animations or updates here
        pass

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            return True
        return False
