import pygame
import sys
import random
import math
import os
from src.constants import *
from src.sprites import *
from src.game import *

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Farm Galaxy")
clock = pygame.time.Clock()

FONT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "fonts", "SpaceMono-Regular.ttf")
FONT_BOLD_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "fonts", "SpaceMono-Bold.ttf")

if os.path.exists(FONT_PATH):
    font_tiny = pygame.font.Font(FONT_PATH, 11)
    font_small = pygame.font.Font(FONT_PATH, 14)
    font_med = pygame.font.Font(FONT_PATH, 18)
    font_large = pygame.font.Font(FONT_PATH, 24)
    font_bold = pygame.font.Font(FONT_BOLD_PATH, 18) if os.path.exists(FONT_BOLD_PATH) else pygame.font.Font(FONT_PATH, 18)
else:
    font_tiny = pygame.font.SysFont("monospace", 12)
    font_small = pygame.font.SysFont("monospace", 14)
    font_med = pygame.font.SysFont("monospace", 18)
    font_large = pygame.font.SysFont("monospace", 24)
    font_bold = font_med

# The single shared game instance. Created once; mutated in place
# (load_game/add_item) so the reference stays valid for `import *`.
game = GameState()

def draw_text(surf, text, x, y, color=WHITE, font=font_small, center=False):
    img = font.render(text, True, color)
    if center:
        x -= img.get_width() // 2
        y -= img.get_height() // 2
    surf.blit(img, (x, y))

def blend_colors(c1, c2, alpha):
    return (
        int(c1[0] * (1 - alpha) + c2[0] * alpha),
        int(c1[1] * (1 - alpha) + c2[1] * alpha),
        int(c1[2] * (1 - alpha) + c2[2] * alpha),
    )

def draw_overlay_backdrop(target_alpha=180):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(game.overlay_alpha)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    if game.overlay_alpha < target_alpha:
        game.overlay_target_alpha = target_alpha

