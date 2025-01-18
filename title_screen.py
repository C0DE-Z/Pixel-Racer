import pygame
import os

# Title Screen UI See main.py 

class TitleScreen:
    def __init__(self, screen, width, height): # Constructor to store all variables
        try:
            pygame.mixer.init()
            music_path = './assests/music/title_screen.mp3'
            
            self.TitleScreenMusic = pygame.mixer.Sound(music_path)
            self.TitleScreenMusic.set_volume(0.2)
            self.is_music_playing = False
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading title screen music: {e}")
            self.TitleScreenMusic = None
            
        # Varibles 
        self.screen = screen
        self.banner = pygame.image.load ('./assests/Banner.png')
        self.play = pygame.image.load("./assests/play.png")
        self.play_rect = None  # Store the play button rect for click detection
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        self.bg_color = (255, 255,255)
        self.text_color = (0, 0, 0)
        self.highlight_color = (255, 0, 0)
        self.title_text = "PIXEL RACER"
        self.start_text = "Press SPACE to Start"
        self.controls = [
            "Controls:",
            "WASD - Drive",
            "SPACE - Drift",
            "Shift - Gear Up",
            "Ctrl - Gear Down",
            "R - Respawn Car",
            "ESC - Pause",
            "H - Debug mode"
            
        ]

    def draw(self):
        self.screen.fill(self.bg_color)
        
        # Draw title
        
        

        pygame.transform.scale(self.banner, (16, 16)) 
        bannar_rect = self.banner.get_rect(center=(self.width//2, self.height//4))
        self.screen.blit(self.banner, bannar_rect)
        # Draw start prompt
        
        pygame.transform.scale(self.play, (128, 128))
        self.play_rect = self.play.get_rect(center=(self.width//2, self.height//2))
        self.screen.blit(self.play, self.play_rect)
        
        # Draw controls
        for i, control in enumerate(self.controls):
            control_surface = self.small_font.render(control, True, self.text_color)
            control_rect = control_surface.get_rect(
                center=(self.width//4, self.height//2 + 50 + i * 30)
            )
            self.screen.blit(control_surface, control_rect)
            
        # Play music
        if self.TitleScreenMusic is not None and not self.is_music_playing:
            try:
                self.TitleScreenMusic.play(-1) # loop
                self.is_music_playing = True
            except pygame.error as e:
                print(f"Error playing title screen music: {e}")

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            # Check if click is within play button rect
            if self.play_rect and self.play_rect.collidepoint(event.pos):
                if self.TitleScreenMusic is not None:
                    self.TitleScreenMusic.fadeout(250)
                    pygame.time.wait(1000)
                    pygame.mixer.stop()
                    self.TitleScreenMusic.stop()
                return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            # stop and fade out music when leaving title screen
            if self.TitleScreenMusic is not None:
                self.TitleScreenMusic.fadeout(250)  
                pygame.time.wait(1000)  
                pygame.mixer.stop()  
                self.TitleScreenMusic.stop() 
            return True
        return False
