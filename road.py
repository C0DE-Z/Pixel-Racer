import pygame
import random
import math
# Creates the randomly made tracks for the car to drive on, and the start position of the car
class Road:
    def __init__(self, world_size):
        self.world_size = world_size
        self.tile_size = 256  # Reduced from 256 * 2
        self.road_surface = pygame.Surface((world_size, world_size), pygame.SRCALPHA)
        self.start_position = None  # Add this line
        self.finish_position = None  # Add this line
        
        try:
            print("Loading road assets...")
            # Create Normal assests from folder 
            self.straight = pygame.image.load('./assests/road_Straight.png')
            self.corner = pygame.image.load('./assests/road_Corner.png')
            self.tjunction = pygame.image.load('./assests/road_T.png')
            self.crossroad = pygame.image.load('./assests/road_Cross.png')
            self.finish = pygame.image.load('./assests/finish_line.png')
            
            # Create flipped versions
            self.corner_flip_x = pygame.transform.flip(self.corner, True, False)
            self.corner_flip_y = pygame.transform.flip(self.corner, False, True)
            self.corner_flip_xy = pygame.transform.flip(self.corner, True, True)
            
            # Scale all versions
            self.straight = pygame.transform.scale(self.straight, (self.tile_size, self.tile_size))
            self.corner = pygame.transform.scale(self.corner, (self.tile_size, self.tile_size))
            self.corner_flip_x = pygame.transform.scale(self.corner_flip_x, (self.tile_size, self.tile_size))
            self.corner_flip_y = pygame.transform.scale(self.corner_flip_y, (self.tile_size, self.tile_size))
            self.corner_flip_xy = pygame.transform.scale(self.corner_flip_xy, (self.tile_size, self.tile_size))
            self.tjunction = pygame.transform.scale(self.tjunction, (self.tile_size, self.tile_size))
            self.crossroad = pygame.transform.scale(self.crossroad, (self.tile_size, self.tile_size))
            self.finish = pygame.transform.scale(self.finish, (self.tile_size, self.tile_size))
            print("Road assets loaded and scaled")
            
        except Exception as e:
            print(f"Error loading road assets: {e}")
            raise

        print("Generating road layout...")
        self.generate_road()
        print("Road generation complete")
    
    def generate_road(self):
        grid_size = self.world_size // self.tile_size
        start_x = grid_size // 3
        start_y = grid_size // 3
        
        # Store start position in pixels
        self.start_position = (start_x * self.tile_size + self.tile_size // 2,
                             start_y * self.tile_size + self.tile_size // 2)
        
        min_straight = 5  
        max_straight = 15
        track_points = []
        current_x = start_x
        current_y = start_y
        direction = 1  
        
        initial_x = current_x
        initial_y = current_y
        
        # Generate main track segments
        for segment in range(4):  # Reduced to 4 
            straight_length = random.randint(min_straight, max_straight)
            for _ in range(straight_length):
                track_points.append((current_x, current_y))
                if direction == 0:    # Up
                    current_y -= 1
                elif direction == 1:  # Right
                    current_x += 1
                elif direction == 2:  # Down
                    current_y += 1
                else:                # Left
                    current_x -= 1
            
            direction = (direction + 1) % 4
        
        # Connect back to start 
        while current_x != initial_x or current_y != initial_y:
            track_points.append((current_x, current_y))
            if current_x > initial_x:
                current_x -= 1
            elif current_x < initial_x:
                current_x += 1
            elif current_y > initial_y:
                current_y -= 1
            elif current_y < initial_y:
                current_y += 1

        # Store finish line position (last straight piece before connecting back)
        self.finish_position = (track_points[-1][0] * self.tile_size + self.tile_size // 2,
                              track_points[-1][1] * self.tile_size + self.tile_size // 2)

        # Place track pieces with corrected rotations
        last_direction = None
        for i in range(len(track_points)):
            x, y = track_points[i]
            next_x, next_y = track_points[(i + 1) % len(track_points)]
            
            pixel_x = x * self.tile_size
            pixel_y = y * self.tile_size

            # Add finish line at the last piece before loop closure
            if i == len(track_points) - 1:
                rotation = 90 if current_direction in [0, 2] else 0
                rotated_finish = pygame.transform.rotate(self.finish, rotation)
                self.road_surface.blit(rotated_finish, (pixel_x, pixel_y))
            
            # Calculate current direction
            if next_x > x:
                current_direction = 1  # Right
            elif next_x < x:
                current_direction = 3  # Left
            elif next_y > y:
                current_direction = 0  # Up
            else:
                current_direction = 2  # Down

            if last_direction is not None and last_direction != current_direction:
                # Updated corner rotations with flips ()
                corner_configs = {
                    (0, 1): (self.corner, 0),         # Up to Right
                    (1, 2): (self.corner_flip_x, 90), # Right to Down
                    (2, 3): (self.corner_flip_y, 90), # Down to Left
                    (3, 0): (self.corner_flip_xy, 0), # Left to Up
                    (1, 0): (self.corner_flip_y, 90), # Right to Up
                    (2, 1): (self.corner_flip_xy, 180), # Down to Right
                    (3, 2): (self.corner, 0),         # Left to Down
                    (0, 3): (self.corner_flip_x, 270) # Up to Left
                }
                
                if (last_direction, current_direction) in corner_configs:
                    corner_img, rotation = corner_configs[(last_direction, current_direction)]
                    rotated_corner = pygame.transform.rotate(corner_img, rotation)
                    self.road_surface.blit(rotated_corner, (pixel_x, pixel_y))

            else:
                # Straight pieces
                rotation = 0 if current_direction in [0, 2] else 90
                rotated_straight = pygame.transform.rotate(self.straight, rotation)
                self.road_surface.blit(rotated_straight, (pixel_x, pixel_y))
            
            last_direction = current_direction

    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.road_surface, (-camera_x, -camera_y))

    def check_finish_line(self, car_x, car_y):
        if self.finish_position:
            # Check if car is within finish line area
            finish_x, finish_y = self.finish_position
            distance = math.sqrt((car_x - finish_x)**2 + (car_y - finish_y)**2)
            return distance < self.tile_size // 2
        return False
