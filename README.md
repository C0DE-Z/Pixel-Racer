<div align="center">
  <img src="./assests/Banner.png" alt="Pixel Racer Banner" width="800"/>
</div>

# Pixel Racer

A top-down racing game built with Python and Pygame featuring procedurally generated tracks, realistic car physics, and manual transmission mechanics.

Warning: This game isn't supposed to look the best - it's more of a showcase for track generation practice!

## How to Play

1. Install Python 3.x from [python.org](https://python.org)
2. Install Pygame by running:
   ```bash
   pip install pygame
   ```
3. Download or clone this repository
4. Run the game:
   ```bash
   python main.py
   ```

## Game Flow
1. Click the Play button on the title screen
2. In the track selection screen:
   - Click "Load Track" to select an existing track
   - Click "New Track" to generate a random track
3. Complete 3 laps to win!
4. Press ESC to return to track selection

## Controls

### Driving
- W - Accelerate
- S - Brake/Reverse
- A/D - Turn left/right
- SPACE - Drift (hold)

### Transmission
- LEFT SHIFT - Shift up gear
- LEFT CTRL - Shift down gear

### Game Controls
- R - Reset car position
- ESC - Return to track selection
- H - Toggle debug mode

## Gear System

The car features a 5-speed transmission with realistic gear ratios:
- 1st Gear: 0-25 MPH
- 2nd Gear: 20-45 MPH
- 3rd Gear: 40-65 MPH
- 4th Gear: 60-85 MPH
- 5th Gear: 80-120 MPH

## Credits

- Music:
  - Title Screen: Ghostoru
  - In-Game: xlh__nick
- SFX: Original creations
- Art: Original pixel art

## Development

Feel free to fork, create issues, or contribute! This is my first Pygame creation and Python game with pixel art.