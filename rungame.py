#!/usr/bin/env python3
import pygame
from matching_game import ScienceGame

try:
    # Initialize pygame
    pygame.init()
    
    # Start the game
    game = ScienceGame()
    game.run()
    
except ImportError:
    print("Please install pygame: pip3 install pygame")
except Exception as e:
    print(f"Error: {e}")
finally:
    pygame.quit()