import pygame

class WinScreen:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        
        self.bg_color = (0, 0, 0)
        self.text_color = (255, 215, 0)

    def draw(self, final_time):
        self.screen.fill(self.bg_color)
        title = self.font.render("TRACK COMPLETE!", True, self.text_color)
        time_text = self.small_font.render(f"Time: {final_time:.2f}s", True, self.text_color)
        replay_text = self.small_font.render("Press SPACE to replay / Press N for new track", True, self.text_color)
        
        title_rect = title.get_rect(center=(self.width//2, self.height//3))
        time_rect = time_text.get_rect(center=(self.width//2, self.height//2))
        replay_rect = replay_text.get_rect(center=(self.width//2, self.height//2 + 50))
        
        self.screen.blit(title, title_rect)
        self.screen.blit(time_text, time_rect)
        self.screen.blit(replay_text, replay_rect)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return "replay"
            elif event.key == pygame.K_n:
                return "new"
        return None
