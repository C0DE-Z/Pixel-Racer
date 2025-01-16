import pygame
import sys
import math
from road import Road  
from title_screen import TitleScreen
from win_screen import WinScreen

pygame.init()

WIDTH, HEIGHT = 1000, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Racer")

grass_texture = pygame.image.load('./assests/grass.png') 
grass_texture = pygame.transform.scale(grass_texture, (64, 64))  # Adjust size as needed

WORLD_SIZE = 10000
world = pygame.Surface((WORLD_SIZE, WORLD_SIZE))

# Fill world with tiled grass texture
for x in range(0, WORLD_SIZE, grass_texture.get_width()):
    for y in range(0, WORLD_SIZE, grass_texture.get_height()):
        world.blit(grass_texture, (x, y))

# Camera offset
camera_x = 0
camera_y = 0

car_image = pygame.image.load('./assests/car1.png')
car_image = pygame.transform.scale(car_image, (car_image.get_width() * 2, car_image.get_height() * 2))
original_car = car_image
car_rect = car_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))

car_angle = 0
car_velocity = 0
car_acceleration = 0.1
car_max_speed = 12
car_friction = 0.98
car_rotation_speed = 3.5
car_drift_factor = 0.95
car_grip = 0.92  

car_base_rotation_speed = 4.0  # Base rotation speed at low velocities
car_min_rotation_speed = 0.3   # Minimum rotation speed at max velocity

car_x = float(car_rect.centerx)
car_y = float(car_rect.centery)

current_gear = 1
max_gears = 5
gear_ratios = {1: 0.16, 2: 0.39, 3: 0.51, 4: 0.61, 5: 1.0}
car_lateral_velocity = 0   

font = pygame.font.Font(None, 36)

# Add after other car variables
gear_shift_cooldown = 0
gear_shift_delay = 15  # frames
gear_efficiency_ranges = {
    1: (0, 25),      # MPH ranges for each gear
    2: (20, 45),
    3: (40, 65),
    4: (60, 85),
    5: (80, 120)
}
downshift_speed_retention = 0.85  # Retain 85% of speed when downshifting

# Add after other variables
lap_count = 0
last_finish_check = False
finish_line_cooldown = 0

# Add after other variables
current_corner_type = "up_right"
corner_types = ["up_right", "right_down", "down_left", "left_up",
                "right_up", "down_right", "left_down", "up_left"]

MENU = 0
PLAYING = 1
WIN_SCREEN = 2  # Add new state

game_state = MENU
title_screen = TitleScreen(screen, WIDTH, HEIGHT)
win_screen = WinScreen(screen, WIDTH, HEIGHT)

lap_count = 0
LAPS_TO_COMPLETE = 3
race_start_time = None
final_time = 0.0

def calculate_mph(velocity):
    return abs(velocity * 20)  

def handle_drift(velocity, lateral_velocity, angle, grip, drift_input):
    if drift_input:
        grip *= 0.4  
        lateral_velocity *= 1.2  # Increase side slip
        
    # Apply grip to lateral velocity with momentum preservation
    lateral_velocity *= grip
    
    # Calculate total velocity vector
    total_velocity = math.sqrt(velocity**2 + lateral_velocity**2)
    
    # Limit total velocity with drift consideration
    max_speed_with_drift = car_max_speed * (0.8 if drift_input else 1.0)
    if total_velocity > max_speed_with_drift:
        ratio = max_speed_with_drift / total_velocity
        velocity *= ratio
        lateral_velocity *= ratio
    
    return velocity, lateral_velocity

def rot_center(image, angle, x, y):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(center = (x, y)).center)
    return rotated_image, new_rect

running = True
clock = pygame.time.Clock()

try:
    print("Starting road system...")
    road = Road(WORLD_SIZE)
    # Set initial car position to track start
    car_x, car_y = road.start_position
    car_rect.center = road.start_position
    # Ensure the car faces the correct direction
    if road.track_pieces.get((car_x, car_y)):
        piece = road.track_pieces[(car_x, car_y)]
        if piece['type'] == 'straight':
            car_angle = piece['rotation']
        elif piece['type'] == 'corner':
            car_angle = piece['rotation'] + 90
    print("Road system finished")
except Exception as e:
    print(f"Failed to create road: {e}")
    sys.exit(1)

while running:
    if game_state == MENU:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_state = PLAYING

        title_screen.draw()
        pygame.display.flip()
        clock.tick(60)
        continue
    
    elif game_state == WIN_SCREEN:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                action = win_screen.handle_input(event)
                if action == "replay":
                    lap_count = 0
                    race_start_time = None
                    car_x, car_y = road.start_position
                    car_rect.center = road.start_position
                    car_velocity = 0
                    game_state = PLAYING
                elif action == "new":
                    lap_count = 0
                    race_start_time = None
                    road.generate_road()
                    car_x, car_y = road.start_position
                    car_rect.center = road.start_position
                    car_velocity = 0
                    game_state = PLAYING
        
        win_screen.draw(final_time)
        pygame.display.flip()
        clock.tick(60)
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LSHIFT and current_gear < max_gears and gear_shift_cooldown <= 0:
                current_speed_mph = calculate_mph(car_velocity)
                min_speed_for_shift = gear_efficiency_ranges[current_gear][1] * 0.8
                
                if current_speed_mph >= min_speed_for_shift:
                    current_gear += 1
                    gear_shift_cooldown = gear_shift_delay
                    print(f"Shifted up to gear {current_gear}")
                else:
                    print(f"Speed too low for upshift: {current_speed_mph} MPH")
                    
            elif event.key == pygame.K_LCTRL and current_gear > 1 and gear_shift_cooldown <= 0:
                car_velocity *= downshift_speed_retention
                current_gear -= 1
                gear_shift_cooldown = gear_shift_delay
                print(f"Shifted down to gear {current_gear}")

            # Corner rotation controls
            if event.key == pygame.K_TAB:
                # Cycle through corner types
                current_index = corner_types.index(current_corner_type)
                current_corner_type = corner_types[(current_index + 1) % len(corner_types)]
            elif event.key == pygame.K_LEFT:
                road.adjust_rotation(current_corner_type, -90)
            elif event.key == pygame.K_RIGHT:
                road.adjust_rotation(current_corner_type, 90)
            elif event.key == pygame.K_f:
                road.toggle_flip(current_corner_type)
            elif event.key == pygame.K_h:
                if road.toggle_debug():
                    print("Debug mode enabled")
                else:
                    print("Debug mode disabled")

    # Update gear shift cooldown
    if gear_shift_cooldown > 0:
        gear_shift_cooldown -= 1

    keys = pygame.key.get_pressed()
    
    gear_acceleration = car_acceleration * gear_ratios[current_gear]
    current_max_speed = car_max_speed * gear_ratios[current_gear]

    speed_factor = abs(car_velocity) / car_max_speed
    current_rotation_speed = car_base_rotation_speed / (1 + speed_factor * 2)
    current_rotation_speed = max(current_rotation_speed, car_min_rotation_speed)

    if keys[pygame.K_ESCAPE]:
        game_running = False
    if keys[pygame.K_r]:
        car_x, car_y = road.start_position
        car_rect.center = road.start_position
        car_velocity = 0
        car_angle = 0
        lap_count = 0
        
    if keys[pygame.K_q] and road.is_debug_visible():
        # Redraw the map 
        road.generate_road()

    if keys[pygame.K_a] and car_velocity != 0:
        car_angle += current_rotation_speed
        drift_multiplier = 0.3 if keys[pygame.K_SPACE] else 0.1
        car_lateral_velocity += current_rotation_speed * drift_multiplier
    if keys[pygame.K_d] and car_velocity != 0:
        car_angle -= current_rotation_speed
        drift_multiplier = 0.3 if keys[pygame.K_SPACE] else 0.1
        car_lateral_velocity -= current_rotation_speed * drift_multiplier

    if keys[pygame.K_SPACE]:
        car_velocity *= 0.98
        current_rotation_speed *= 1.2
    if keys[pygame.K_w]:
        car_velocity = min(car_velocity + gear_acceleration, current_max_speed)
    elif keys[pygame.K_s]:
        car_velocity = max(car_velocity - gear_acceleration, -current_max_speed * 0.5)
    else:
        car_velocity *= car_friction

    car_velocity, car_lateral_velocity = handle_drift(
        car_velocity, car_lateral_velocity, car_angle, 
        car_grip, keys[pygame.K_SPACE]
    )

    # Get current gear efficiency
    min_speed, max_speed = gear_efficiency_ranges[current_gear]
    current_speed_mph = calculate_mph(car_velocity)
    
    # Apply gear efficiency to acceleration
    gear_efficiency = 1.0
    if current_speed_mph < min_speed:
        gear_efficiency = 0.5  # Engine struggling at too low speed
    elif current_speed_mph > max_speed:
        gear_efficiency = 0.7  # Engine straining at too high speed
        
    # Apply gear efficiency to acceleration
    gear_acceleration = car_acceleration * gear_ratios[current_gear] * gear_efficiency

    # Update position with drift physics
    angle_rad = math.radians(car_angle)
    car_x += (car_velocity * math.cos(angle_rad) - car_lateral_velocity * math.sin(angle_rad))
    car_y -= (car_velocity * math.sin(angle_rad) + car_lateral_velocity * math.cos(angle_rad))

    # Keep car within world bounds (not screen bounds)
    car_x = max(0, min(car_x, WORLD_SIZE))
    car_y = max(0, min(car_y, WORLD_SIZE))

    car_rect.centerx = int(car_x)
    car_rect.centery = int(car_y)

    # Update camera to follow car
    camera_x = car_x - WIDTH // 2
    camera_y = car_y - HEIGHT // 2

    # Keep camera within world bounds
    camera_x = max(0, min(camera_x, WORLD_SIZE - WIDTH))
    camera_y = max(0, min(camera_y, WORLD_SIZE - HEIGHT))

    # Start the race timer when player first moves
    if race_start_time is None and abs(car_velocity) > 0.1:
        race_start_time = pygame.time.get_ticks()

    # Check finish line crossing with cooldown
    if finish_line_cooldown > 0:
        finish_line_cooldown -= 1
    else:
        crossed_finish = road.check_finish_line(car_x, car_y)
        if crossed_finish and not last_finish_check:
            lap_count += 1
            finish_line_cooldown = 60
            print(f"Lap {lap_count} completed!")
            if lap_count >= LAPS_TO_COMPLETE:
                # Calculate final time
                if race_start_time:
                    final_time = (pygame.time.get_ticks() - race_start_time) / 1000.0
                game_state = WIN_SCREEN
        last_finish_check = crossed_finish

    # Apply extra friction when off track
    if not road.is_on_track(car_x, car_y):
        car_velocity *= 0.97

    # Clear screen with solid color first
    screen.fill((34, 139, 34))  # Forest green background
    
    # Draw world and road in correct order
    screen.blit(world, (-camera_x, -camera_y))
    road.draw(screen, camera_x, camera_y, car_x, car_y)
    
    # Draw car last
    screen_car_x = car_x - camera_x
    screen_car_y = car_y - camera_y
    rotated_car, rotated_rect = rot_center(car_image, car_angle + 90, screen_car_x, screen_car_y)
    screen.blit(rotated_car, rotated_rect)

    speed_text = font.render(f"{int(calculate_mph(car_velocity))} MPH", True, (255, 255, 255))
    gear_text = font.render(f"GEAR: {current_gear}", True, (255, 255, 255))
    screen.blit(speed_text, (10, 10))
    screen.blit(gear_text, (10, 50))

    # Add lap counter to display
    lap_text = font.render(f"LAP: {lap_count}", True, (255, 255, 255))
    screen.blit(lap_text, (10, 90))

    # Add to UI rendering
    if road.is_debug_visible():
        corner_text = font.render(f"Corner: {current_corner_type}", True, (255, 255, 255))
        screen.blit(corner_text, (10, 130))

    # Replace the road piece rotation controls section with:
    nearest = road.get_nearest_piece(car_x, car_y)
    if nearest and (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
        pos, piece = nearest
        rotation_amount = 90 if keys[pygame.K_RIGHT] else -90
        road.rotate_piece_at_position(pos, rotation_amount)
            
    # Add to UI rendering
    if race_start_time:  # Show ongoing race time
        current_race_time = (pygame.time.get_ticks() - race_start_time) / 1000.0
        time_text = font.render(f"Time: {current_race_time:.1f}s", True, (255, 255, 255))
        screen.blit(time_text, (10, 210))

    # Show "Nearby" text only if debug is active
    if road.is_debug_visible():
        nearest = road.get_nearest_piece(car_x, car_y)
        if nearest:
            pos, piece = nearest
            piece_type = piece['type'].capitalize()
            piece_text = font.render(f"Nearby: {piece_type}", True, (255, 255, 255))
            screen.blit(piece_text, (10, 170))

    pygame.display.flip()
    clock.tick(60)
   

pygame.quit()
sys.exit()