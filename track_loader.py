import pygame
import os
import json

class TrackLoader:
    def __init__(self, screen, width, height): # Constructor to store all variables
        
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        
        self.bg_color = (0, 0, 0)
        self.text_color = (255, 215, 0)
        self.tracks_dir = './assests/tracks'
        self.tracks = self.load_tracks()
        self.selected_track = 0
        
        self.moveCursor = './assests/sfx/select.wav'
        self.moveCursorSound = pygame.mixer.Sound(self.moveCursor)
    # Functoin to get all tracks
    def load_tracks(self):
        track_files = []
        try:
            if not os.path.exists(self.tracks_dir):
                raise FileNotFoundError(f"Tracks directory '{self.tracks_dir}' does not exist.")
            track_files = [f for f in os.listdir(self.tracks_dir) if f.endswith('.json')]
        except Exception as e:
            print(f"Error loading tracks: {e}")
        return track_files


    def draw(self):
        self.screen.fill(self.bg_color)
        title = self.font.render("Track Loader", True, self.text_color)
        title_rect = title.get_rect(center=(self.width // 2, self.height // 6))
        self.screen.blit(title, title_rect)

        if self.tracks:
            for i, track in enumerate(self.tracks):
                color = self.text_color if i != self.selected_track else (255, 0, 0)
                track_text = self.small_font.render(track, True, color)
                track_rect = track_text.get_rect(center=(self.width // 2, self.height // 3 + i * 40))
                self.screen.blit(track_text, track_rect)
        else:
            no_tracks_text = self.small_font.render("No tracks available", True, self.text_color)
            no_tracks_rect = no_tracks_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(no_tracks_text, no_tracks_rect)

        instructions = self.small_font.render("Press ENTER to load / N for new track", True, self.text_color)
        instructions_rect = instructions.get_rect(center=(self.width // 2, self.height - 50))
        self.screen.blit(instructions, instructions_rect)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_track = (self.selected_track - 1) % len(self.tracks)
                self.moveCursorSound.play()
            elif event.key == pygame.K_DOWN:
                self.selected_track = (self.selected_track + 1) % len(self.tracks)
                # Play sound
                self.moveCursorSound.play()
            elif event.key == pygame.K_RETURN and self.tracks:
                return "load", self.tracks[self.selected_track]
            elif event.key == pygame.K_n:
                return "new", None
        return None, None
