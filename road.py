import pygame
import random
import math

class Road:
    def __init__(self, world_size):
        self.world_size = world_size
        self.tile_size = 256  # Reduced from 256 * 2
        self.road_surface = pygame.Surface((world_size, world_size), pygame.SRCALPHA)
        
        try:
            print("Loading road assets...")
            self.straight = pygame.image.load('./assests/road_Straight.png')
            self.corner = pygame.image.load('./assests/road_Corner.png')
            self.tjunction = pygame.image.load('./assests/road_T.png')
            self.crossroad = pygame.image.load('./assests/road_Cross.png')
            
            self.straight = pygame.transform.scale(self.straight, (self.tile_size, self.tile_size))
            self.corner = pygame.transform.scale(self.corner, (self.tile_size, self.tile_size))
            self.tjunction = pygame.transform.scale(self.tjunction, (self.tile_size, self.tile_size))
            self.crossroad = pygame.transform.scale(self.crossroad, (self.tile_size, self.tile_size))
            print("Road assets loaded and scaled")
            
        except Exception as e:
            print(f"Error loading road assets: {e}")
            raise

        print("Generating road layout...")
        self.generate_road()
        print("Road generation complete")
    
    def generate_road(self):
        grid_size = self.world_size // self.tile_size
        start_x = grid_size // 3  # Adjusted starting position
        start_y = grid_size // 3
        
        # Track configuration
        min_straight = 10  # Reduced for smaller track
        max_straight = 40
        track_points = []
        current_x = start_x
        current_y = start_y
        direction = 1  # Start going right
        
        for _ in range(8):  # 8 major segments
            straight_length = random.randint(min_straight, max_straight)
            for _ in range(straight_length):
                if direction == 0:  # Up
                    current_y -= 1
                elif direction == 1:  # Right
                    current_x += 1
                elif direction == 2:  # Down
                    current_y += 1
                else:  # Left
                    current_x -= 1
                track_points.append((current_x, current_y))
            
            track_points.append((current_x, current_y))
            direction = (direction + 1) % 4
        
        while current_x > start_x:
            current_x -= 1
            track_points.append((current_x, current_y))
        while current_y > start_y:
            current_y -= 1
            track_points.append((current_x, current_y))
        
        # Place track pieces
        last_direction = None
        for i in range(len(track_points)):
            x, y = track_points[i]
            next_x, next_y = track_points[(i + 1) % len(track_points)]
            
            # Calculate direction
            if next_x > x:
                current_direction = 1  # Right
            elif next_x < x:
                current_direction = 3  # Left
            elif next_y > y:
                current_direction = 0  # Up
            else:
                current_direction = 2  # Down
            
            pixel_x = x * self.tile_size
            pixel_y = y * self.tile_size
            
            if last_direction is not None and last_direction != current_direction:
                # Calculate corner rotation based on direction change
                corner_rotations = {
                    (0, 1): 0,    # Up to Right
                    (1, 2): 90,   # Right to Down
                    (2, 3): 180,  # Down to Left
                    (3, 0): 270,  # Left to Up
                }
                rotation = corner_rotations.get((last_direction, current_direction), 0)
                rotated_corner = pygame.transform.rotate(self.corner, rotation)
                self.road_surface.blit(rotated_corner, (pixel_x, pixel_y))
            else:
                # Rotate straight pieces: 90° for vertical, 0° for horizontal
                rotation = 90 if current_direction in [0, 2] else 0
                rotated_straight = pygame.transform.rotate(self.straight, rotation)
                self.road_surface.blit(rotated_straight, (pixel_x, pixel_y))
            
            last_direction = current_direction

    def draw(self, screen, camera_x, camera_y):
        # Add debug rectangle to show road surface bounds
        pygame.draw.rect(self.road_surface, (255, 0, 0, 128), (0, 0, 100, 100))  # Debug rectangle
        screen.blit(self.road_surface, (-camera_x, -camera_y))
