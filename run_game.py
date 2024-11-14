import pygame
from matching_game import ScienceGame

try:
    pygame.init()
    game = ScienceGame()
    game.run()
except ImportError:
    print("Please install pygame: pip3 install pygame")
except Exception as e:
    print(f"Error: {e}")
finally:
    pygame.quit()



