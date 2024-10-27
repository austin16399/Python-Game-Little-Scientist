import pygame
import random
import time
import math
from dataclasses import dataclass
from typing import Tuple, Optional, Set

@dataclass

class GameState:
    level: int = 1
    score: int = 0
    matches_found: int = 0
    selected_tile: Optional[Tuple[int, int]] = None
    start_time: float = time.time()
    message: str = "Little Scientists: Match Adventure Quest!"
    matched_pairs: Set[Tuple[int, int]] = None
    game_complete: bool = False
    
    def __post_init__(self):
        self.matched_pairs = set()

class Tile:
    def __init__(self, color, rect, symbol=None):
        self.color = color
        self.rect = rect
        self.symbol = symbol
        self.flip_progress = 0
        self.is_flipping = False
        self.revealed = False
        self.flip_start_time = 0
        self.matched = False
        self.flip_duration = 0.3

    def update_flip(self, current_time):
        if self.is_flipping:
            progress = min((current_time - self.flip_start_time) / self.flip_duration, 1)
            self.flip_progress = progress
            if progress >= 1:
                self.is_flipping = False
                self.revealed = not self.revealed
                return True
        return False

    def start_flip(self, current_time):
        self.is_flipping = True
        self.flip_start_time = current_time

class ScienceGame:
    # Level 1 colors (simpler)
    LEVEL1_COLORS = [
        (142, 68, 173),   # Purple
        (41, 128, 185),   # Blue
        (39, 174, 96),    # Green
        (230, 126, 34),   # Orange
        (192, 57, 43),    # Red
        (142, 142, 142),  # Silver
        (241, 196, 15),   # Yellow
        (46, 204, 113),   # Emerald
    ]

    # Level 2 colors (more complex)
    LEVEL2_COLORS = [
        (155, 89, 182),   # Purple
        (52, 152, 219),   # Blue
        (26, 188, 156),   # Turquoise
        (241, 196, 15),   # Yellow
        (230, 126, 34),   # Orange
        (231, 76, 60),    # Red
        (149, 165, 166),  # Gray
        (211, 84, 0),     # Dark Orange
        (41, 128, 185),   # Light Blue
        (22, 160, 133),   # Green
        (192, 57, 43),    # Dark Red
        (142, 68, 173),   # Dark Purple
        (39, 174, 96)     # Light Green
    ]

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Science Night Memory Lab")
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        self.state = GameState()
        self.tiles = {}
        self.bubbles = self.create_bubbles()
        self.waiting_for_reset = False
        self.reset_start_time = 0
        self.transition_active = False
        self.transition_start_time = 0
        self.setup_level()

    def create_bubbles(self):
        return [[random.randint(0, 800), random.randint(0, 600), 
                 random.randint(5, 15), random.uniform(0.5, 2)] 
                for _ in range(15)]

    def setup_level(self):
        self.grid_size = 4 if self.state.level == 1 else 5
        self.tile_size = 90 if self.state.level == 1 else 75
        self.margin = (800 - self.grid_size * self.tile_size) // 2
        
        colors = (self.LEVEL1_COLORS if self.state.level == 1 else self.LEVEL2_COLORS)
        needed_pairs = (self.grid_size * self.grid_size) // 2
        color_pairs = colors[:needed_pairs] * 2
        random.shuffle(color_pairs)
        
        self.tiles.clear()
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                rect = pygame.Rect(
                    self.margin + col * self.tile_size,
                    120 + row * self.tile_size,
                    self.tile_size - 6,
                    self.tile_size - 6
                )
                idx = row * self.grid_size + col
                self.tiles[(row, col)] = Tile(color_pairs[idx], rect)

    def start_next_level(self):
        self.state.level += 1
        self.state.matches_found = 0
        self.state.matched_pairs.clear()
        self.state.selected_tile = None
        self.state.message = f"Starting Level {self.state.level}! More complex molecules ahead!"
        self.setup_level()
        self.transition_active = False
        self.transition_start_time = 0

    def show_transition_screen(self, text1, text2):
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(200)
        overlay.fill((20, 30, 40))
        
        msg1 = self.title_font.render(text1, True, (100, 200, 255))
        msg2 = self.font.render(text2, True, (255, 255, 255))
        
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(msg1, ((800 - msg1.get_width()) // 2, 250))
        self.screen.blit(msg2, ((800 - msg2.get_width()) // 2, 320))
        pygame.display.flip()

    def handle_click(self, pos, current_time):
        if self.waiting_for_reset or self.transition_active:
            return

        x, y = pos
        row = (y - 120) // self.tile_size
        col = (x - self.margin) // self.tile_size
        
        if not (0 <= row < self.grid_size and 0 <= col < self.grid_size):
            return
            
        tile = self.tiles[(row, col)]
        if tile.revealed or tile.is_flipping or tile.matched:
            return

        tile.start_flip(current_time)
        
        if not self.state.selected_tile:
            self.state.selected_tile = (row, col)
        else:
            prev_row, prev_col = self.state.selected_tile
            prev_tile = self.tiles[(prev_row, prev_col)]
            
            if tile.color == prev_tile.color:
                tile.matched = prev_tile.matched = True
                self.state.matched_pairs.update([(prev_row, prev_col), (row, col)])
                self.state.matches_found += 1
                self.state.score += 10 * self.state.level
                messages = self.SCIENCE_MESSAGES if self.state.level == 1 else self.LEVEL2_MESSAGES
                self.state.message = random.choice(messages)
            else:
                self.waiting_for_reset = True
                self.reset_start_time = current_time
            
            self.state.selected_tile = None

    def update_tiles(self, current_time):
        if self.waiting_for_reset and current_time - self.reset_start_time > 1:
            for tile in self.tiles.values():
                if tile.revealed and not tile.matched:
                    tile.start_flip(current_time)
            self.waiting_for_reset = False

        for tile in self.tiles.values():
            tile.update_flip(current_time)

    def update_bubbles(self):
        for bubble in self.bubbles:
            bubble[1] -= bubble[3]
            if bubble[1] < -20:
                bubble[1] = 620
                bubble[0] = random.randint(0, 800)

    def draw_laboratory_ui(self, current_time):
        self.screen.fill((20, 30, 40))
        
        for bubble in self.bubbles:
            pygame.draw.circle(self.screen, (100, 200, 255, 128), 
                             (int(bubble[0]), int(bubble[1])), bubble[2], 1)

        pygame.draw.rect(self.screen, (30, 40, 50), (0, 0, 800, 90))
        pygame.draw.line(self.screen, (50, 150, 200), (0, 90), (800, 90), 2)
        
        stats = [
            f"TIME: {current_time - self.state.start_time:.1f}s",
            f"LEVEL: {self.state.level}",
            f"SCORE: {self.state.score}"
        ]
        
        for i, text in enumerate(stats):
            surface = self.font.render(text, True, (100, 200, 255))
            self.screen.blit(surface, (20 + i * 270, 30))

        msg_surface = self.font.render(self.state.message, True, (255, 255, 255))
        self.screen.blit(msg_surface, 
                        ((800 - msg_surface.get_width()) // 2, 550))

    def draw_tile(self, tile: Tile):
        if tile.is_flipping:
            scale = abs(math.cos(tile.flip_progress * math.pi))
            scaled_width = tile.rect.width * scale
            x_offset = (tile.rect.width - scaled_width) / 2
            scaled_rect = pygame.Rect(
                tile.rect.x + x_offset,
                tile.rect.y,
                scaled_width,
                tile.rect.height
            )
            color = tile.color if tile.flip_progress >= 0.5 else (60, 80, 100)
            pygame.draw.rect(self.screen, color, scaled_rect, border_radius=10)
            
            if scale > 0.1:
                if tile.flip_progress >= 0.5:
                    for radius in (10, 20):
                        pygame.draw.circle(self.screen, (255, 255, 255, 128), 
                                        scaled_rect.center, int(radius * scale), 1)
                else:
                    for offset in range(0, 21, 10):
                        pygame.draw.circle(self.screen, (100, 150, 200), 
                                        scaled_rect.center, int(offset * scale), 1)
        else:
            if tile.revealed:
                pygame.draw.rect(self.screen, tile.color, tile.rect, border_radius=10)
                for radius in (10, 20):
                    pygame.draw.circle(self.screen, (255, 255, 255, 128), 
                                    tile.rect.center, radius, 1)
            else:
                pygame.draw.rect(self.screen, (60, 80, 100), tile.rect, border_radius=10)
                pygame.draw.rect(self.screen, (80, 100, 120), tile.rect, 2, border_radius=10)
                for offset in range(0, 21, 10):
                    pygame.draw.circle(self.screen, (100, 150, 200), 
                                    tile.rect.center, offset, 1)

    def run(self):
        clock = pygame.time.Clock()
        
        while not self.state.game_complete:
            current_time = time.time()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos, current_time)

            self.update_tiles(current_time)
            self.update_bubbles()
            
            
            # Handle level completion and transitions
            required_matches = (self.grid_size * self.grid_size) // 2
            if self.state.matches_found == required_matches:
                if not self.transition_active:
                    self.transition_active = True
                    self.transition_start_time = current_time
                    if self.state.level == 1:
                        self.show_transition_screen(
                            "EXPERIMENT 1 COMPLETE!",
                            "Preparing Level 2... More complex molecules ahead!"
                        )
                    else:
                        self.show_transition_screen(
                            "CONGRATULATIONS! ALL EXPERIMENTS COMPLETE!",
                            f"Final Score: {self.state.score} - Time: {current_time - self.state.start_time:.1f}s"
                        )
                
                # Wait for 2 seconds before proceeding
                if current_time - self.transition_start_time >= 2:
                    if self.state.level == 1:
                        self.start_next_level()
                    else:
                        self.state.game_complete = True
                        break
                continue  # Skip regular drawing during transition

            self.draw_laboratory_ui(current_time)
            for tile in self.tiles.values():
                self.draw_tile(tile)

            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    ScienceGame().run()