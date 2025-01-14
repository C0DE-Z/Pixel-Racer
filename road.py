import pygame
import random

class Road:
    def __init__(self, world_size):
        self.world_size = world_size
        self.tile_size = 128  # Size of road tiles
        self.road_surface = pygame.Surface((world_size, world_size), pygame.SRCALPHA)
        
        # Load road tiles
        self.straight = pygame.image.load('./assests/road_straight.png')
        self.curve = pygame.image.load('./assests/road_curve.png')
        self.intersection = pygame.image.load('./assests/road_intersection.png')
        
        # Scale road tiles
        self.straight = pygame.transform.scale(self.straight, (self.tile_size, self.tile_size))
        self.curve = pygame.transform.scale(self.curve, (self.tile_size, self.tile_size))
        self.intersection = pygame.transform.scale(self.intersection, (self.tile_size, self.tile_size))
        
        self.generate_road()
    
    def generate_road(self):
        grid_size = self.world_size // self.tile_size
        current_x = grid_size // 2
        current_y = grid_size // 2
        direction = 0  # 0: up, 1: right, 2: down, 3: left
        
        for _ in range(100):  # Generate 100 road pieces
            # Place road piece
            x = current_x * self.tile_size
            y = current_y * self.tile_size
            
            if random.random() < 0.2:  # 20% chance to turn
                # Place curve and change direction
                rotated_curve = pygame.transform.rotate(self.curve, direction * 90)
                self.road_surface.blit(rotated_curve, (x, y))
                direction = (direction + 1) % 4
            else:
                # Place straight road
                rotated_straight = pygame.transform.rotate(self.straight, direction * 90)
                self.road_surface.blit(rotated_straight, (x, y))
            
            # Move to next position
            if direction == 0:
                current_y -= 1
            elif direction == 1:
                current_x += 1
            elif direction == 2:
                current_y += 1
            else:
                current_x -= 1
            
            # Keep within bounds
            current_x = max(0, min(current_x, grid_size - 1))
            current_y = max(0, min(current_y, grid_size - 1))
    
    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.road_surface, (-camera_x, -camera_y))
