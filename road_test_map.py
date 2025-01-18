import json
import pygame
import math

def generate_test_track():
    """Generate a test track with all possible road pieces"""
    track_data = {
        "start_position": [5, 5],
        "finish_position": [5, 6],
        "track_pieces": [
            # First row: Straight pieces
            {"position": [5, 5], "type": "straight", "direction": "straight", "rotation": 0, "flipped": False},
            {"position": [6, 5], "type": "straight", "direction": "straight", "rotation": 90, "flipped": False},
            
            # Second row: Basic corners
            {"position": [4, 6], "type": "corner", "direction": "up_right", "rotation": 0, "flipped": False},
            {"position": [5, 6], "type": "corner", "direction": "right_down", "rotation": 90, "flipped": False},
            {"position": [6, 6], "type": "corner", "direction": "down_left", "rotation": 180, "flipped": False},
            {"position": [7, 6], "type": "corner", "direction": "left_up", "rotation": 270, "flipped": False},
            
            # Third row: Flipped corners
            {"position": [4, 7], "type": "corner", "direction": "right_up", "rotation": 180, "flipped": True},
            {"position": [5, 7], "type": "corner", "direction": "down_right", "rotation": 270, "flipped": True},
            {"position": [6, 7], "type": "corner", "direction": "left_down", "rotation": 0, "flipped": True},
            {"position": [7, 7], "type": "corner", "direction": "up_left", "rotation": 90, "flipped": True},
            
            # Finish line
            {"position": [5, 8], "type": "finish", "direction": "finish", "rotation": 0, "flipped": False}
        ]
    }
    
    # Save the test track
    with open('./assests/tracks/test_track.json', 'w') as f:
        json.dump(track_data, f, indent=4)
    
    return './assests/tracks/test_track.json'
