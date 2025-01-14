import pygame
import sys
import math
from road import Road  

pygame.init()

WIDTH, HEIGHT = 1000, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Racer")

grass_texture = pygame.image.load('./assests/grass.png') 
grass_texture = pygame.transform.scale(grass_texture, (64, 64))  # Adjust size as needed

WORLD_SIZE = 5000
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

# After creating world surface, add:
try:
    print("Initializing road system...")
    road = Road(WORLD_SIZE)
    print("Road system initialized")
except Exception as e:
    print(f"Failed to create road: {e}")
    sys.exit(1)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LSHIFT and current_gear < max_gears:
                current_gear += 1
            elif event.key == pygame.K_LCTRL and current_gear > 1:
                current_gear -= 1

    keys = pygame.key.get_pressed()
    
    gear_acceleration = car_acceleration * gear_ratios[current_gear]
    current_max_speed = car_max_speed * gear_ratios[current_gear]

    # Calculate dynamic rotation speed based on velocity
    speed_factor = abs(car_velocity) / car_max_speed
    current_rotation_speed = car_base_rotation_speed / (1 + speed_factor * 2)
    current_rotation_speed = max(current_rotation_speed, car_min_rotation_speed)

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

    # Clear screen with solid color first
    screen.fill((34, 139, 34))  # Forest green background
    
    # Draw world and road in correct order
    screen.blit(world, (-camera_x, -camera_y))
    road.draw(screen, camera_x, camera_y)
    
    # Draw car last
    screen_car_x = car_x - camera_x
    screen_car_y = car_y - camera_y
    rotated_car, rotated_rect = rot_center(car_image, car_angle + 90, screen_car_x, screen_car_y)
    screen.blit(rotated_car, rotated_rect)

    speed_text = font.render(f"{int(calculate_mph(car_velocity))} MPH", True, (255, 255, 255))
    gear_text = font.render(f"GEAR: {current_gear}", True, (255, 255, 255))
    screen.blit(speed_text, (10, 10))
    screen.blit(gear_text, (10, 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()