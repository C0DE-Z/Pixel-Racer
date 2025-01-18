import pygame
import random
import math
import json

# Creates the randomly made tracks for the car to drive on, and the start position of the car
class Road:
    def __init__(self, world_size, test_mode=False):
        self.world_size = world_size
        self.tile_size = 256 * 1.5
        self.road_surface = pygame.Surface((world_size, world_size), pygame.SRCALPHA)
        self.start_position = None
        self.finish_position = None
        self.track_pieces = {}
        try:
            print("Loading road assets...")
            self.straight = pygame.image.load('./assests/road_Straight.png')
            self.corner = pygame.image.load('./assests/road_Corner.png')
            self.tjunction = pygame.image.load('./assests/road_T.png')
            self.crossroad = pygame.image.load('./assests/road_Cross.png')
            self.finish = pygame.image.load('./assests/finish_line.png')
            
            self.corner_flip_x = pygame.transform.flip(self.corner, 1, 0)
            self.corner_flip_y = pygame.transform.flip(self.corner, 0, 1)
            self.corner_flip_xy = pygame.transform.flip(self.corner, 1, 1)
            
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

        # Add music initialization
        try:
            self.track_music = pygame.mixer.Sound('./assests/music/voxels.mp3')
            self.track_music.set_volume(0.2)
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading track music: {e}")
            self.track_music = None

        print("Generating road layout...")
        self.load_config()
        if test_mode:
            from road_test_map import generate_test_track
            test_track = generate_test_track()
            self.load_saved_track(test_track)
        elif not self.load_saved_track():
            self.generate_road()
        print("Road generation complete")
    
    def load_config(self):
        try:
            with open('./assests/road_config.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print("Config not found, using defaults")
            self.config = {
                "corner_rotations": {
                    "up_right": 0, "right_down": 90,
                    "down_left": 180, "left_up": 270,
                    "right_up": 0, "down_right": 90,
                    "left_down": 180, "up_left": 270
                },
                "corner_flips": {
                    "up_right": False, "right_down": False,
                    "down_left": False, "left_up": False,
                    "right_up": True, "down_right": True,
                    "left_down": True, "up_left": True
                }
            }
            self.save_config()
 
    def save_config(self):
        with open('./assests/road_config.json', 'w') as f:
            json.dump(self.config, f, indent=4)

    def adjust_rotation(self, corner_type, amount):
        self.config["corner_rotations"][corner_type] = \
            (self.config["corner_rotations"][corner_type] + amount) % 360
        self.save_config()
        self.generate_road()

    def toggle_flip(self, corner_type):
        self.config["corner_flips"][corner_type] = \
            not self.config["corner_flips"][corner_type]
        self.save_config()
        self.generate_road()

    def is_valid_track(self, track_points, start_x, start_y):
        def neighbors(cell):
            x, y = cell
            for nx, ny in [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]:
                if (nx, ny) in track_set:
                    yield (nx, ny)

        if len(track_points) < 10:
            return False

        track_set = set(track_points)
        visited = set()
        queue = [track_points[0]]
        while queue:
            current = queue.pop(0)
            visited.add(current)
            for n in neighbors(current):
                if n not in visited:
                    queue.append(n)

        if len(visited) != len(track_points):
            return False

        end_x, end_y = track_points[-1]
        dist_to_start = abs(end_x - start_x) + abs(end_y - start_y)
        
        if dist_to_start > 2:
            return False
        
        return True

    def generate_road(self):
        self.road_surface.fill((0, 0, 0, 0))
        grid_size = self.world_size // self.tile_size
        max_attempts = math.inf  # Limit the number of attempts (for testing)
        attempts = 0

        while attempts < max_attempts:
            try:
                track_points = []
                self.occupied_cells = set()
                
                start_x = grid_size // 4 + 5
                start_y = grid_size // 4 + 5
                current_x = start_x
                current_y = start_y
                
                num_segments = random.randint(10, 15)  # Increase the number of segments
                direction = random.randint(0, 3)
                
                for _ in range(num_segments):
                    segment_length = random.randint(3, 8)  # Shorten segment lengths
                    for _ in range(segment_length):
                        track_points.append((current_x, current_y))
                        if direction == 0:
                            current_y -= 1
                        elif direction == 1:
                            current_x += 1
                        elif direction == 2:
                            current_y += 1
                        else:
                            current_x -= 1
                        
                        if not (0 <= current_x < grid_size and 0 <= current_y < grid_size):
                            raise ValueError("Track went off screen")
                    
                    # Increase the likelihood of turns
                    turn_choice = random.choices([-1, 0, 1], weights=[3, 1, 3])[0]
                    direction = (direction + turn_choice) % 4
                
                if not self.connect_to_start(track_points, start_x, start_y, current_x, current_y):
                    print(f"Failed to connect track to start, attempt {attempts + 1}")
                    attempts += 1
                    continue

                if not self.is_valid_track(track_points, start_x, start_y):
                    #print(f"Invalid track generated, attempt {attempts + 1}")
                    attempts += 1
                    continue

                self.place_track_pieces(track_points)
                # Only save track when generating new one, not when loading
                self.store_valid_track(track_points)
                print(f"Valid track generated after {attempts + 1} attempts")
                
                # Stop any existing music before playing new track music
                pygame.mixer.stop()
                if self.track_music is not None:
                    self.track_music.play(-1)  # Loop indefinitely
                return True

            except ValueError as e:
                #print(f"Track generation failed: {e}")
                attempts += 1
                continue

        print(f"Failed to generate valid track after {max_attempts} attempts")
        return False

    def connect_to_start(self, track_points, start_x, start_y, current_x, current_y):
        max_connect_attempts = 50
        attempt = 0
        
        while attempt < max_connect_attempts:
            if abs(current_x - start_x) <= 1 and abs(current_y - start_y) <= 1:
                if (current_x, current_y) != (start_x, start_y):
                    track_points.append((start_x, start_y))
                return True
                
            next_x, next_y = current_x, current_y
            
            if abs(current_x - start_x) > 0 and abs(current_y - start_y) > 0:
                test_x = current_x + (-1 if current_x > start_x else 1)
                test_y = current_y + (-1 if current_y > start_y else 1)
                if (test_x, test_y) not in self.occupied_cells:
                    next_x, next_y = test_x, test_y
            elif abs(current_x - start_x) > abs(current_y - start_y):
                next_x += -1 if current_x > start_x else 1
            else:
                next_y += -1 if current_y > start_y else 1
                
            if (next_x, next_y) not in self.occupied_cells:
                track_points.append((next_x, next_y))
                self.occupied_cells.add((next_x, next_y))
                current_x, current_y = next_x, next_y
            else:
                attempt += 1

        raise ValueError("Unable to connect track to start")

    def place_track_pieces(self, track_points):
        self.start_position = (track_points[0][0] * self.tile_size + self.tile_size // 2,
                             track_points[0][1] * self.tile_size + self.tile_size // 2)

        self.finish_position = (track_points[-1][0] * self.tile_size + self.tile_size // 2,
                              track_points[-1][1] * self.tile_size + self.tile_size // 2)

        last_direction = None
        self.track_pieces = {}
        for i in range(len(track_points)):
            x, y = track_points[i]
            next_x, next_y = track_points[(i + 1) % len(track_points)]
            
            pixel_x = x * self.tile_size
            pixel_y = y * self.tile_size

            if i == len(track_points) - 1:
                rotation = 90 if current_direction in [0, 2] else 0
                rotated_finish = pygame.transform.rotate(self.finish, rotation)
                self.road_surface.blit(rotated_finish, (pixel_x, pixel_y))
                self.track_pieces[(pixel_x, pixel_y)] = {
                    'type': 'finish',
                    'direction': 'finish',
                    'rotation': rotation
                }
            
            if next_x > x:
                current_direction = 1
            elif next_x < x:
                current_direction = 3
            elif next_y > y:
                current_direction = 0
            else:
                current_direction = 2

            if last_direction is not None and last_direction != current_direction:
                direction_map = {
                    (0, 1): "up_right",
                    (1, 2): "right_down",
                    (2, 3): "down_left",
                    (3, 0): "left_up",
                    (1, 0): "right_up",
                    (2, 1): "down_right",
                    (3, 2): "left_down",
                    (0, 3): "up_left"
                }

                corner_type = direction_map.get((last_direction, current_direction), "up_right")
                use_flip = self.config["corner_flips"][corner_type]
                rotation = self.config["corner_rotations"][corner_type]
                
                corner_img = self.corner_flip_x if use_flip else self.corner
                rotated_corner = pygame.transform.rotate(corner_img, rotation)
                self.road_surface.blit(rotated_corner, (pixel_x, pixel_y))
                self.track_pieces[(pixel_x, pixel_y)] = {
                    'type': 'corner',
                    'direction': corner_type,
                    'rotation': rotation,
                    'flipped': use_flip
                }
            else:
                rotation = 90 if current_direction in [1, 3] else 0
                rotated_straight = pygame.transform.rotate(self.straight, rotation)
                self.road_surface.blit(rotated_straight, (pixel_x, pixel_y))
                self.track_pieces[(pixel_x, pixel_y)] = {
                    'type': 'straight',
                    'direction': 'straight',
                    'rotation': rotation,
                    'flipped': False
                }
            
            last_direction = current_direction

    def draw(self, screen, camera_x, camera_y, car_x=None, car_y=None):
        if self.is_debug_visible() and car_x is not None and car_y is not None:
            nearest = self.get_nearest_piece(car_x, car_y)
            if nearest:
                pos, piece = nearest
                pygame.draw.rect(self.road_surface, (255, 255, 0, 128),
                                 (pos[0], pos[1], self.tile_size, self.tile_size), 2)
                # display piece type and rotation
                piece_info = f"{piece['direction']} ({piece['rotation']}°)"
                font = pygame.font.Font(None, 24)
                piece_text = font.render(piece_info, True, (255, 255, 255))
                screen.blit(piece_text, (pos[0] - camera_x, pos[1] - camera_y - 20))

        screen.blit(self.road_surface, (-camera_x, -camera_y))

    # Check if the car has crossed the finish line
    def check_finish_line(self, car_x, car_y):
        if self.finish_position:
            finish_x, finish_y = self.finish_position
            distance = math.sqrt((car_x - finish_x)**2 + (car_y - finish_y)**2)
            return distance < self.tile_size // 2
        return False
    # Get the closest track piece to the car used for dev tools 
    def get_nearest_piece(self, car_x, car_y):
        nearest = None
        min_dist = float('inf')
        
        for pos, piece in self.track_pieces.items():
            dist = ((car_x - pos[0])**2 + (car_y - pos[1])**2)**0.5
            if dist < min_dist and dist < self.tile_size * 1.5:
                min_dist = dist
                nearest = (pos, piece)
        
        return nearest

    def rotate_piece_at_position(self, pos, amount):
        if pos in self.track_pieces:
            piece = self.track_pieces[pos]
            if piece['type'] == 'corner':
                piece['rotation'] = (piece['rotation'] + amount) % 360
                rotated_corner = pygame.transform.rotate(self.corner, piece['rotation'])
                self.road_surface.blit(rotated_corner, pos)
            else:
                piece['rotation'] = (piece['rotation'] + amount) % 180
                rotated_straight = pygame.transform.rotate(self.straight, piece['rotation'])
                self.road_surface.blit(rotated_straight, pos)

    def toggle_debug(self):
        if not hasattr(self, 'debug'):
            self.debug = False
        self.debug = not self.debug
        return self.debug

    def is_debug_visible(self):
        return getattr(self, 'debug', False)

    def is_on_track(self, x, y):
        cell_x = int(x // self.tile_size) * self.tile_size
        cell_y = int(y // self.tile_size) * self.tile_size
        if (cell_x, cell_y) not in self.track_pieces:
            return False

        center_x = cell_x + self.tile_size / 2
        center_y = cell_y + self.tile_size / 2
        dx = x - center_x
        dy = y - center_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        return distance <= (self.tile_size * 0.6)

    def store_valid_track(self, track_points):
        import time
        import os
        os.makedirs('./assests/tracks', exist_ok=True)
        
        track_data = {
            "start_position": [self.start_position[0] / self.tile_size, self.start_position[1] / self.tile_size],
            "finish_position": [self.finish_position[0] / self.tile_size, self.finish_position[1] / self.tile_size],
            "track_pieces": [
                {
                    "position": [x, y],
                    "type": self.track_pieces[(x * self.tile_size, y * self.tile_size)]['type'],
                    "direction": self.track_pieces[(x * self.tile_size, y * self.tile_size)]['direction'],
                    "rotation": self.track_pieces[(x * self.tile_size, y * self.tile_size)]['rotation'],
                    "flipped": self.track_pieces[(x * self.tile_size, y * self.tile_size)]['flipped']
                }
                for x, y in track_points
            ]
        }
        
        filename = f"./assests/tracks/track_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(track_data, f, indent=4)
        print(f"Saved track to {filename}")

    def load_saved_track(self, filename=None):
        if filename is None:
            return False
        try:
            with open(filename, 'r') as f:
                track_data = json.load(f)
            
            self.road_surface.fill((0, 0, 0, 0))
            self.track_pieces = {}
            
            # Load all pieces first
            pieces_to_load = track_data["track_pieces"]
            # Ensure finish piece is loaded last
            pieces_to_load.sort(key=lambda x: x["type"] != "finish")
            
            for piece in pieces_to_load:
                x, y = piece["position"]
                pixel_x = x * self.tile_size
                pixel_y = y * self.tile_size
                piece_type = piece["type"]
                rotation = piece["rotation"]
                flipped = piece.get("flipped", False)
                direction = piece.get("direction", piece_type)
                
                if piece_type == "straight":
                    rotated_piece = pygame.transform.rotate(self.straight, rotation)
                elif piece_type == "corner":
                    corner_img = self.corner_flip_x if flipped else self.corner
                    rotated_piece = pygame.transform.rotate(corner_img, rotation)
                elif piece_type == "finish":
                    rotated_piece = pygame.transform.rotate(self.finish, rotation)
                else:
                    continue
                
                self.road_surface.blit(rotated_piece, (pixel_x, pixel_y))
                self.track_pieces[(pixel_x, pixel_y)] = {
                    'type': piece_type,
                    'direction': direction,
                    'rotation': rotation,
                    'flipped': flipped
                }

            # Set positions after loading all pieces
            self.start_position = (track_data["start_position"][0] * self.tile_size, 
                                 track_data["start_position"][1] * self.tile_size)
            self.finish_position = (track_data["finish_position"][0] * self.tile_size, 
                                  track_data["finish_position"][1] * self.tile_size)

            pygame.mixer.stop()
            if self.track_music is not None:
                self.track_music.play(-1)
            return True
        except (FileNotFoundError, IndexError, json.JSONDecodeError) as e:
            print(f"Error loading track: {e}")
            return False

