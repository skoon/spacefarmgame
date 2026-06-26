import pygame
import random
import math
import os
from src.constants import *

SPRITE_CACHE = {}

# === Sprite Sheet System ===
SPRITE_SHEETS = {}

def load_sprite_sheet(path):
    full = os.path.join("assets", path)
    if path not in SPRITE_SHEETS:
        SPRITE_SHEETS[path] = pygame.image.load(full).convert_alpha()
    return SPRITE_SHEETS[path]

def get_sheet_frame(sheet, col, row, cell_w, cell_h):
    key = f"frame_{sheet}_{col}_{row}_{cell_w}_{cell_h}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    sheet_surf = load_sprite_sheet(sheet)
    frame = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
    frame.blit(sheet_surf, (0, 0), (col * cell_w, row * cell_h, cell_w, cell_h))
    SPRITE_CACHE[key] = frame
    return frame

SHEET_ASTRO = "astro_256_shaded.png"
SHEET_ASTRO_PD = "astro_256_pixeldata.png"
SHEET_NPC = {"zara": "npc_zara_256.png", "nova": "npc_nova_256.png", "zoop": "npc_zoop_256.png",
             "glimmer": "npc_glimmer_256.png", "rigby": "npc_rigby_256.png"}
SHEET_BOT = {"water_bot": "bot_water_bot_256.png", "sprout_bot": "bot_sprout_bot_256.png",
             "harvest_bot": "bot_harvest_bot_256.png"}
SHEET_BUILDING = {"bar": "building_bar_384.png",
                   "house": "building_house_384.png", "player_house": "building_player_house_384.png"}

# Frame layout maps: (direction, state) -> (col, row)
# User must edit these when PNG sprite sheets are reorganized.
ASTRO_FRAME_MAP = {
    "down":  (2, 0),  # col 2, row 0
    "left":  (2, 1),
    "right": (2, 2),
    "up":    (2, 3),
}
NPC_FRAME_MAP = {
    "down":  (1, 0),
    "left":  (3, 0),
    "right": (4, 0),
    "up":    (2, 0),
}
BUILDING_FRAME_MAP = {
    "default": (1, 1),
}

# === 16-bit Palette System (M15) ===
PALETTE = {
    "skin": [(255, 200, 170), (235, 180, 150), (200, 150, 120)],
    "suit_white": [(240, 242, 245), (210, 215, 220), (180, 185, 190)],
    "visor_blue": [(80, 200, 255), (50, 160, 220), (20, 100, 180)],
    "metal_gray": [(200, 200, 200), (160, 160, 160), (120, 120, 120)],
    "suit_brown": [(120, 80, 40), (100, 65, 35), (80, 50, 25)],
    "grass_green": [(50, 130, 50), (60, 140, 60), (70, 150, 70), (40, 180, 40)],
    "soil_brown": [(100, 68, 40), (90, 58, 30), (80, 48, 20)],
    "water_blue": [(60, 100, 180), (50, 80, 140), (100, 150, 255)],
    "helmet_light": [(180, 200, 220), (160, 180, 200), (200, 200, 220)],
    "crop_green": [(40, 180, 40), (60, 200, 60), (30, 150, 30)],
}

def blit_sprite(surf, pixels, x, y, palette_map, shade=0):
    for row_idx, row in enumerate(pixels):
        for col_idx, ch in enumerate(row):
            if ch == ' ':
                continue
            color_key = palette_map.get(ch)
            if color_key:
                colors = PALETTE.get(color_key)
                if colors:
                    idx = min(shade, len(colors) - 1)
                    c = colors[idx]
                    surf.set_at((x + col_idx, y + row_idx), c)

# === Player Animation System (M16) ===

_ASTRO_PM = {
    'W': "suit_white", 'B': "visor_blue", 'Y': "helmet_light",
    'R': "suit_brown", 'G': "metal_gray", 'S': "skin",
}

_ASTRO_BASE = {
    "down": [
        "    WWWW    ",
        "   WBBBBW   ",
        "  WBBBBBBW  ",
        "  WBYBBYBW  ",
        "  WBBBBBBW  ",
        "   WBBBBW   ",
        "    WWWW    ",
        "   WWWWWW   ",
        "   WGGGGW   ",
        "  WWRRRRWW  ",
        "  W  WW  W  ",
    ],
    "up": [
        "    WWWW    ",
        "   WBBBBW   ",
        "  WBYBBYBW  ",
        "  WBBBBBBW  ",
        "   WBBBBW   ",
        "    WWWW    ",
        "   WWWWWW   ",
        "   WGGGGW   ",
        "  WWRRRRWW  ",
        "  W  WW  W  ",
    ],
    "left": [
        "   WWWW    ",
        "  WBBBBW   ",
        " WBBBBBBW  ",
        " WBYBBYBW  ",
        " WBBBBBBW  ",
        "  WBBBBW   ",
        "   WWWW    ",
        "  WWWWWW   ",
        "  WGGGGW   ",
        " WWRRRRWW  ",
        " W  WW  W  ",
    ],
    "right": [
        "    WWWW   ",
        "   WBBBBW  ",
        "  WBBBBBBW ",
        "  WBYBBYBW ",
        "  WBBBBBBW ",
        "   WBBBBW  ",
        "    WWWW   ",
        "   WWWWWW  ",
        "   WGGGGW  ",
        "  WWRRRRWW ",
        "  W  WW  W ",
    ],
}

# Walk stride overrides: {direction: {row_index: new_row_string, ...}}
_ASTRO_WALK_STRIDE = {
    "down":  {7: "  WWWWWWWW  ", 9: "  WWR  RWW  "},
    "up":    {6: "  WWWWWWWW  ", 8: "  WWR  RWW  "},
    "left":  {7: " WWWWWWWW  ", 9: " WWR  RWW  "},
    "right": {7: "  WWWWWWWW ", 9: "  WWR  RWW "},
}

# Tool pixel additions: {tool_index: {direction: [(x, y, char), ...]}}
_ASTRO_TOOL_PIXELS = {
    0: {  # hoe
        "down":  [(11, 7, 'R'), (11, 8, 'R'), (12, 8, 'R'), (12, 9, 'R')],
        "up":    [(11, 6, 'R'), (11, 7, 'R'), (12, 7, 'R'), (12, 8, 'R')],
        "left":  [(0, 6, 'R'), (0, 7, 'R'), (1, 7, 'R'), (1, 8, 'R')],
        "right": [(11, 6, 'R'), (11, 7, 'R'), (10, 7, 'R'), (10, 8, 'R')],
    },
    1: {  # watering can
        "down":  [(10, 6, 'B'), (11, 6, 'B'), (10, 7, 'B'), (11, 7, 'B'), (12, 7, 'B')],
        "up":    [(10, 5, 'B'), (11, 5, 'B'), (10, 6, 'B'), (11, 6, 'B'), (12, 6, 'B')],
        "left":  [(0, 5, 'B'), (1, 5, 'B'), (0, 6, 'B'), (1, 6, 'B'), (2, 6, 'B')],
        "right": [(10, 5, 'B'), (9, 5, 'B'), (10, 6, 'B'), (9, 6, 'B'), (8, 6, 'B')],
    },
    2: {  # scythe
        "down":  [(10, 5, 'G'), (11, 5, 'G'), (11, 6, 'G'), (12, 6, 'G'), (13, 6, 'G')],
        "up":    [(10, 4, 'G'), (11, 4, 'G'), (11, 5, 'G'), (12, 5, 'G'), (13, 5, 'G')],
        "left":  [(0, 4, 'G'), (1, 4, 'G'), (1, 5, 'G'), (2, 5, 'G'), (3, 5, 'G')],
        "right": [(10, 4, 'G'), (9, 4, 'G'), (9, 5, 'G'), (8, 5, 'G'), (7, 5, 'G')],
    },
}

def _build_astro_surf(direction, state, frame):
    base = list(_ASTRO_BASE[direction])
    pm = _ASTRO_PM

    if state == "walk" and frame in (1, 3):
        overrides = _ASTRO_WALK_STRIDE.get(direction, {})
        for row_idx, new_row in overrides.items():
            if row_idx < len(base):
                base[row_idx] = new_row

    elif state == "idle" and frame == 1:
        for i in range(len(base)):
            if 'Y' in base[i]:
                base[i] = base[i].replace('Y', 'B')
                break

    elif state == "tool":
        tool_idx = frame
        tool_px = _ASTRO_TOOL_PIXELS.get(tool_idx, {}).get(direction, [])
        for x, y, ch in tool_px:
            color_key = pm.get(ch)
            if color_key:
                row = list(base[y]) if y < len(base) else []
                while len(row) <= x:
                    row.append(' ')
                row[x] = ch
                base[y] = ''.join(row)

    key = f"astro_{state}_{direction}_{frame}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]

    s = make_surface(TILE_SIZE, TILE_SIZE)
    max_w = max(len(r) for r in base)
    h = len(base)
    ox = (TILE_SIZE - max_w * 2) // 2
    oy = (TILE_SIZE - h * 2) // 2
    if state == "walk" and frame in (1, 3):
        oy += 1
    for dy, row in enumerate(base):
        for dx, ch in enumerate(row):
            c = pm.get(ch)
            if c:
                colors = PALETTE[c]
                color = colors[0]
                sx, sy = ox + dx * 2, oy + dy * 2
                s.set_at((sx, sy), color)
                s.set_at((sx + 1, sy), color)
                s.set_at((sx, sy + 1), color)
                s.set_at((sx + 1, sy + 1), color)
    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

def get_astronaut_animated(direction="down", state="idle", frame=0):
    key = f"astro_anim_{direction}_{state}_{frame}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    base = get_astronaut_surf(direction)
    s = base.copy()
    if state == "walk" and frame in (1, 3):
        pass
    elif state == "idle" and frame == 1:
        set_pixel(s, 12, 4, (180, 220, 255))
        set_pixel(s, 13, 4, (180, 220, 255))
        set_pixel(s, 17, 4, (180, 220, 255))
        set_pixel(s, 18, 4, (180, 220, 255))
    elif state == "tool":
        if direction == "down":
            if frame == 0:
                draw_box(s, 24, 14, 6, 3, (160, 130, 80), True)
                draw_box(s, 26, 10, 2, 4, (120, 100, 60), True)
            elif frame == 1:
                draw_box(s, 24, 10, 4, 6, (60, 120, 200), True)
                draw_box(s, 22, 14, 2, 4, (100, 130, 180), True)
            elif frame == 2:
                draw_box(s, 24, 8, 2, 10, (140, 140, 140), True)
                draw_box(s, 23, 14, 4, 3, (160, 160, 160), True)
    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

def get_astronaut_v2(direction="down"):
    return get_astronaut_animated(direction, "idle", 0)

def make_surface(w, h, color=None):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    if color:
        s.fill(color)
    return s

def scale_to_fill(surf, target_w, target_h):
    w, h = surf.get_size()
    min_x, min_y = w, h
    max_x, max_y = -1, -1
    for y in range(h):
        for x in range(w):
            if surf.get_at((x, y))[3] > 0:
                if x < min_x: min_x = x
                if y < min_y: min_y = y
                if x > max_x: max_x = x
                if y > max_y: max_y = y
    if max_x < 0:
        return pygame.transform.scale(surf, (target_w, target_h))
    cw = max_x - min_x + 1
    ch = max_y - min_y + 1
    cropped = surf.subsurface((min_x, min_y, cw, ch))
    return pygame.transform.scale(cropped, (target_w, target_h))

def set_pixel(surf, x, y, color):
    if 0 <= x < surf.get_width() and 0 <= y < surf.get_height():
        surf.set_at((x, y), color)

def hline(surf, x, y, w, color):
    for dx in range(w):
        set_pixel(surf, x + dx, y, color)

def vline(surf, x, y, h, color):
    for dy in range(h):
        set_pixel(surf, x, y + dy, color)

def draw_box(surf, x, y, w, h, color, fill=True):
    if fill:
        for dy in range(h):
            for dx in range(w):
                set_pixel(surf, x + dx, y + dy, color)
    else:
        for dx in range(w):
            set_pixel(surf, x + dx, y, color)
            set_pixel(surf, x + dx, y + h - 1, color)
        for dy in range(h):
            set_pixel(surf, x, y + dy, color)
            set_pixel(surf, x + w - 1, y + dy, color)

def get_astronaut_surf(direction="down"):
    key = f"astro_{direction}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    s = make_surface(TILE_SIZE, TILE_SIZE)
    # Legs
    if direction == "down":
        leg_color = (60, 80, 120)
        draw_box(s, 10, 22, 4, 8, SUIT_WHITE, True)
        draw_box(s, 18, 22, 4, 8, SUIT_WHITE, True)
        # Boots
        draw_box(s, 9, 28, 6, 4, (80, 80, 100), True)
        draw_box(s, 17, 28, 6, 4, (80, 80, 100), True)
        # Body
        draw_box(s, 8, 10, 16, 14, SUIT_WHITE, True)
        # Belt
        draw_box(s, 8, 20, 16, 3, (60, 60, 80), True)
        draw_box(s, 14, 20, 4, 3, GOLD, True)
        # Arms
        draw_box(s, 4, 12, 5, 8, SUIT_WHITE, True)
        draw_box(s, 23, 12, 5, 8, SUIT_WHITE, True)
        # Gloves
        draw_box(s, 4, 18, 5, 4, (80, 80, 100), True)
        draw_box(s, 23, 18, 5, 4, (80, 80, 100), True)
        # Helmet
        draw_box(s, 8, 1, 16, 10, HELMET_LIGHT, True)
        # Visor
        draw_box(s, 10, 3, 12, 6, VISOR_BLUE, True)
        # Visor shine
        draw_box(s, 12, 4, 4, 2, (180, 220, 255), True)
        # Antenna
        set_pixel(s, 16, 0, HELMET_LIGHT)
        set_pixel(s, 16, 0, (200, 200, 220))
        set_pixel(s, 16, 0, RED)
    elif direction == "up":
        draw_box(s, 10, 22, 4, 8, SUIT_WHITE, True)
        draw_box(s, 18, 22, 4, 8, SUIT_WHITE, True)
        draw_box(s, 9, 28, 6, 4, (80, 80, 100), True)
        draw_box(s, 17, 28, 6, 4, (80, 80, 100), True)
        draw_box(s, 8, 10, 16, 14, SUIT_WHITE, True)
        draw_box(s, 8, 20, 16, 3, (60, 60, 80), True)
        draw_box(s, 14, 20, 4, 3, GOLD, True)
        draw_box(s, 4, 12, 5, 8, SUIT_WHITE, True)
        draw_box(s, 23, 12, 5, 8, SUIT_WHITE, True)
        draw_box(s, 4, 18, 5, 4, (80, 80, 100), True)
        draw_box(s, 23, 18, 5, 4, (80, 80, 100), True)
        draw_box(s, 8, 1, 16, 10, HELMET_LIGHT, True)
        draw_box(s, 10, 3, 12, 6, (60, 100, 150), True)
    elif direction == "left":
        s = make_surface(TILE_SIZE, TILE_SIZE)
        draw_box(s, 12, 22, 4, 8, SUIT_WHITE, True)
        draw_box(s, 18, 22, 4, 8, SUIT_WHITE, True)
        draw_box(s, 11, 28, 6, 4, (80, 80, 100), True)
        draw_box(s, 17, 28, 6, 4, (80, 80, 100), True)
        draw_box(s, 6, 10, 16, 14, SUIT_WHITE, True)
        draw_box(s, 6, 20, 16, 3, (60, 60, 80), True)
        draw_box(s, 4, 12, 5, 8, SUIT_WHITE, True)
        draw_box(s, 22, 12, 5, 8, SUIT_WHITE, True)
        draw_box(s, 4, 18, 4, 4, (80, 80, 100), True)
        draw_box(s, 23, 18, 4, 4, (80, 80, 100), True)
        draw_box(s, 6, 1, 16, 10, HELMET_LIGHT, True)
        draw_box(s, 6, 3, 14, 6, VISOR_BLUE, True)
        draw_box(s, 8, 4, 4, 2, (180, 220, 255), True)
    elif direction == "right":
        s = make_surface(TILE_SIZE, TILE_SIZE)
        draw_box(s, 10, 22, 4, 8, SUIT_WHITE, True)
        draw_box(s, 16, 22, 4, 8, SUIT_WHITE, True)
        draw_box(s, 9, 28, 6, 4, (80, 80, 100), True)
        draw_box(s, 15, 28, 6, 4, (80, 80, 100), True)
        draw_box(s, 10, 10, 16, 14, SUIT_WHITE, True)
        draw_box(s, 10, 20, 16, 3, (60, 60, 80), True)
        draw_box(s, 4, 12, 5, 8, SUIT_WHITE, True)
        draw_box(s, 22, 12, 5, 8, SUIT_WHITE, True)
        draw_box(s, 4, 18, 4, 4, (80, 80, 100), True)
        draw_box(s, 23, 18, 4, 4, (80, 80, 100), True)
        draw_box(s, 10, 1, 16, 10, HELMET_LIGHT, True)
        draw_box(s, 12, 3, 14, 6, VISOR_BLUE, True)
        draw_box(s, 20, 4, 4, 2, (180, 220, 255), True)
    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

def get_npc_surf(npc_id, color1, color2):
    key = f"npc_{npc_id}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    s = get_npc_v2(npc_id, color1, color2)
    SPRITE_CACHE[key] = s
    return s

def get_npc_v2(npc_id, color1, color2, direction="down", frame=0):
    key = f"npcv2_{npc_id}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    s = None
    sheet_32_path = os.path.join("assets", f"npc_{npc_id}_32.png")
    if os.path.exists(sheet_32_path):
        raw = pygame.image.load(sheet_32_path).convert_alpha()
        s = scale_to_fill(raw, 32, 64)
    else:
        sheet_name = SHEET_NPC.get(npc_id)
        if sheet_name and os.path.exists(os.path.join("assets", sheet_name)):
            col_offset, row = NPC_FRAME_MAP.get(direction, (1, 0))
            s = get_sheet_frame(sheet_name, col_offset + frame, row, 32, 64).copy()
    if s is None:
        s = make_surface(TILE_SIZE, TILE_SIZE * 2)
    c1, c2 = color1, color2
    dark = tuple(max(0, x - 60) for x in c1)
    light = tuple(min(255, x + 40) for x in c1)
    skin = (255, 200, 170)
    eye_w = (220, 220, 240)
    eye_p = (40, 40, 60)

    if npc_id == "zara":
        # Zenorian shopkeeper — apron, antennae
        hline(s, 10, 0, 4, c2)
        hline(s, 11, 1, 2, c2)
        draw_box(s, 6, 2, 20, 10, c1, True)
        draw_box(s, 8, 4, 4, 3, eye_w, True)
        draw_box(s, 18, 4, 4, 3, eye_w, True)
        set_pixel(s, 10, 5, eye_p)
        set_pixel(s, 20, 5, eye_p)
        set_pixel(s, 14, 8, c2)
        draw_box(s, 4, 12, 24, 14, c1, True)
        draw_box(s, 4, 13, 24, 3, c2, True)
        draw_box(s, 8, 16, 16, 4, light, True)
        draw_box(s, 8, 20, 16, 1, c2, True)
        draw_box(s, 8, 22, 4, 4, c2, True)
        draw_box(s, 20, 22, 4, 4, c2, True)
        draw_box(s, 10, 22, 4, 4, dark, True)
        draw_box(s, 18, 22, 4, 4, dark, True)
        draw_box(s, 10, 26, 12, 6, c1, True)
        draw_box(s, 12, 26, 8, 6, dark, True)
        draw_box(s, 10, 30, 12, 2, c2, True)

    elif npc_id == "blip":
        # Floatan bartender — jellyfish bell, floating
        draw_box(s, 4, 12, 24, 4, c1, True)
        draw_box(s, 2, 16, 28, 10, c1, True)
        draw_box(s, 4, 26, 24, 6, light, True)
        draw_box(s, 8, 4, 16, 8, c1, True)
        draw_box(s, 10, 6, 4, 3, eye_w, True)
        draw_box(s, 18, 6, 4, 3, eye_w, True)
        set_pixel(s, 12, 7, eye_p)
        set_pixel(s, 20, 7, eye_p)
        hline(s, 13, 10, 6, c2)
        # Tendrils
        for i in range(3):
            set_pixel(s, 6 + i * 8, 32, light)
            set_pixel(s, 8 + i * 6, 33, c2)
            set_pixel(s, 7 + i * 8, 34, light)

    elif npc_id == "nova":
        # Lunari pilot — tall, flowing hair, jacket
        draw_box(s, 8, 6, 16, 6, skin, True)
        draw_box(s, 6, 0, 20, 8, c2, True)
        draw_box(s, 10, 8, 4, 3, eye_w, True)
        draw_box(s, 18, 8, 4, 3, eye_w, True)
        set_pixel(s, 12, 9, eye_p)
        set_pixel(s, 20, 9, eye_p)
        draw_box(s, 10, 12, 12, 2, skin, True)
        draw_box(s, 4, 14, 24, 14, c1, True)
        draw_box(s, 4, 14, 24, 2, light, True)
        draw_box(s, 16, 14, 8, 6, c2, True)
        draw_box(s, 6, 28, 20, 4, dark, True)
        draw_box(s, 10, 28, 4, 4, dark, True)
        draw_box(s, 18, 28, 4, 4, dark, True)
        draw_box(s, 12, 32, 8, 2, (80, 80, 100), True)

    elif npc_id == "pip":
        # Spriggan helper — small, leafy
        draw_box(s, 8, 2, 16, 8, skin, True)
        set_pixel(s, 12, 0, c2)
        set_pixel(s, 16, 0, c2)
        set_pixel(s, 14, 1, c2)
        draw_box(s, 10, 4, 3, 2, eye_w, True)
        draw_box(s, 18, 4, 3, 2, eye_w, True)
        set_pixel(s, 12, 5, eye_p)
        set_pixel(s, 20, 5, eye_p)
        hline(s, 13, 8, 6, c2)
        draw_box(s, 6, 10, 20, 12, c1, True)
        draw_box(s, 8, 22, 16, 6, dark, True)
        draw_box(s, 10, 22, 4, 4, (80, 120, 80), True)
        draw_box(s, 18, 22, 4, 4, (80, 120, 80), True)
        draw_box(s, 12, 28, 8, 4, dark, True)

    elif npc_id == "luna":
        # Ethereal mystic — flowing robes
        draw_box(s, 8, 2, 16, 8, skin, True)
        draw_box(s, 6, 0, 20, 4, c2, True)
        draw_box(s, 10, 4, 4, 3, eye_w, True)
        draw_box(s, 18, 4, 4, 3, eye_w, True)
        set_pixel(s, 12, 5, eye_p)
        set_pixel(s, 20, 5, eye_p)
        hline(s, 14, 8, 4, (200, 100, 150))
        draw_box(s, 2, 10, 28, 18, c1, True)
        draw_box(s, 4, 10, 24, 2, light, True)
        draw_box(s, 12, 14, 8, 2, light, True)
        draw_box(s, 6, 28, 20, 4, dark, True)
        draw_box(s, 10, 28, 12, 4, c2, True)
        draw_box(s, 6, 32, 20, 2, (100, 80, 120), True)

    elif npc_id == "rex":
        # Terrus farmer — hat, beard, stocky
        draw_box(s, 6, 0, 20, 6, (160, 120, 60), True)
        draw_box(s, 4, 2, 24, 3, (120, 80, 40), True)
        draw_box(s, 8, 6, 16, 8, skin, True)
        draw_box(s, 10, 8, 4, 3, eye_w, True)
        draw_box(s, 18, 8, 4, 3, eye_w, True)
        set_pixel(s, 12, 9, eye_p)
        set_pixel(s, 20, 9, eye_p)
        draw_box(s, 10, 12, 12, 6, c2, True)
        draw_box(s, 4, 14, 24, 16, c1, True)
        draw_box(s, 4, 14, 24, 2, light, True)
        draw_box(s, 16, 14, 8, 4, c2, True)
        draw_box(s, 8, 30, 16, 4, dark, True)
        draw_box(s, 10, 30, 4, 4, (60, 40, 20), True)
        draw_box(s, 18, 30, 4, 4, (60, 40, 20), True)
        draw_box(s, 10, 34, 12, 2, (60, 40, 20), True)

    elif npc_id == "zoop":
        # Fuzzian pet shop — round, fluffy, bowtie
        draw_box(s, 4, 2, 24, 10, light, True)
        draw_box(s, 6, 4, 20, 8, c1, True)
        draw_box(s, 8, 5, 16, 6, c1, True)
        set_pixel(s, 10, 6, eye_w)
        set_pixel(s, 14, 6, eye_w)
        set_pixel(s, 18, 6, eye_w)
        set_pixel(s, 22, 6, eye_w)
        set_pixel(s, 11, 7, eye_p)
        set_pixel(s, 15, 7, eye_p)
        set_pixel(s, 19, 7, eye_p)
        set_pixel(s, 23, 7, eye_p)
        set_pixel(s, 14, 9, (255, 150, 150))
        set_pixel(s, 18, 9, (255, 150, 150))
        # Bowtie
        draw_box(s, 12, 12, 8, 4, c2, True)
        set_pixel(s, 10, 13, c2)
        set_pixel(s, 22, 13, c2)
        # Fluffy body
        draw_box(s, 4, 14, 24, 14, light, True)
        draw_box(s, 6, 16, 20, 10, c1, True)
        for i in range(6):
            px = 4 + i * 4 + (i % 2) * 2
            set_pixel(s, px, 14, (255, 200, 220))
            set_pixel(s, px, 15, (255, 200, 220))
            set_pixel(s, px, 27, (255, 200, 220))
            set_pixel(s, px, 28, (255, 200, 220))
        draw_box(s, 10, 28, 12, 4, dark, True)
        draw_box(s, 12, 32, 8, 2, (80, 80, 100), True)

    else:
        # Fallback — generic alien
        draw_box(s, 6, 24, 8, 8, (60, 60, 80), True)
        draw_box(s, 18, 24, 8, 8, (60, 60, 80), True)
        draw_box(s, 4, 10, 24, 16, color1, True)
        draw_box(s, 4, 22, 24, 3, color2, True)
        draw_box(s, 6, 0, 20, 12, color1, True)
        draw_box(s, 10, 3, 4, 4, WHITE, True)
        draw_box(s, 18, 3, 4, 4, WHITE, True)
        set_pixel(s, 12, 5, BLACK)
        set_pixel(s, 20, 5, BLACK)
        draw_box(s, 13, 8, 6, 2, color2, True)
        set_pixel(s, 8, 0, color2)
        set_pixel(s, 24, 0, color2)
        set_pixel(s, 9, 0, color2)
        set_pixel(s, 23, 0, color2)

    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

SEASONAL_GRASS_SHIFT = {
    "Nebula": (0, 0, 0),
    "Void": (-10, -5, 10),
    "Bloom": (10, 20, 5),
    "Solar": (10, -5, -10),
}

SEASONAL_PATH_SHIFT = {
    "Nebula": (0, 0, 0),
    "Void": (-15, -10, 5),
    "Bloom": (5, 10, 10),
    "Solar": (15, 5, -10),
}

GRASS_PALETTES = [
    [(50, 130, 50), (60, 140, 60), (70, 150, 70)],
    [(40, 120, 60), (50, 130, 70), (65, 145, 80)],
    [(60, 120, 40), (70, 130, 50), (80, 145, 60)],
    [(55, 135, 55), (65, 145, 65), (50, 125, 50)],
]

PATH_PALETTES = [
    [(160, 150, 140), (170, 160, 150), (150, 140, 130)],
    [(150, 145, 135), (165, 155, 145), (145, 135, 125)],
    [(170, 155, 135), (160, 145, 130), (155, 140, 120)],
    [(140, 145, 145), (155, 155, 150), (145, 140, 135)],
]

def _apply_season_shift(r, g, b, season_name, palette="grass"):
    if season_name:
        shift = SEASONAL_GRASS_SHIFT if palette == "grass" else SEASONAL_PATH_SHIFT
        s = shift.get(season_name, (0, 0, 0))
        return (max(0, min(255, r + s[0])), max(0, min(255, g + s[1])), max(0, min(255, b + s[2])))
    return (r, g, b)

def get_tile_surf(tile_type, variant=0, season=None):
    season_str = season or ""
    key = f"tile_{tile_type}_{variant}_{season_str}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    s = make_surface(TILE_SIZE, TILE_SIZE)
    if tile_type == "grass":
        shades = GRASS_PALETTES[variant % len(GRASS_PALETTES)]
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                c = shades[(x + y + variant) % 3]
                c = _apply_season_shift(c[0], c[1], c[2], season, "grass")
                set_pixel(s, x, y, c)
        tuft_count = 4 + variant
        for _ in range(tuft_count):
            sx = (variant * 13 + _ * 7) % TILE_SIZE
            sy = (_ * 9 + variant * 5) % TILE_SIZE
            tc = _apply_season_shift(30, 160 + variant * 10, 30, season, "grass")
            set_pixel(s, sx, sy, tc)
            if sx + 1 < TILE_SIZE:
                tc2 = _apply_season_shift(35, 170 + variant * 8, 35, season, "grass")
                set_pixel(s, sx + 1, sy, tc2)
    elif tile_type == "path":
        shades = PATH_PALETTES[variant % len(PATH_PALETTES)]
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                c = shades[(x + y + variant) % 3]
                c = _apply_season_shift(c[0], c[1], c[2], season, "path")
                if variant > 0 and random.random() < 0.02:
                    c = (c[0] - 20, c[1] - 15, c[2] - 10)
                set_pixel(s, x, y, c)
        if variant % 2 == 0:
            for _ in range(3):
                cx = random.randint(4, 27)
                cy = random.randint(4, 27)
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        px, py = cx + dx, cy + dy
                        if 0 <= px < TILE_SIZE and 0 <= py < TILE_SIZE:
                            set_pixel(s, px, py, (120, 110, 95))
    elif tile_type == "untilled":
        base_shade = (SOIL_BROWN[0] - variant * 5, SOIL_BROWN[1] - variant * 3, SOIL_BROWN[2] + variant * 2)
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                shade = base_shade
                if (x + y + variant) % 4 == 0:
                    shade = (shade[0] - 10, shade[1] - 10, shade[2] - 10)
                if (x + y + variant * 3) % 5 == 0:
                    shade = (shade[0] + 10, shade[1] + 10, shade[2] + 5)
                set_pixel(s, x, y, shade)
        if variant == 0:
            for _ in range(4):
                sx, sy = random.randint(0, TILE_SIZE - 1), random.randint(0, TILE_SIZE - 1)
                set_pixel(s, sx, sy, (90, 140, 60))
    elif tile_type == "tilled":
        base_r, base_g, base_b = DARK_BROWN
        row_offset = variant * 2
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                shade = (base_r + (x + row_offset) % 4 * 5, base_g + (x + row_offset) % 4 * 3, base_b + (y + variant) % 3 * 3)
                set_pixel(s, x, y, shade)
        for row in range(4):
            yy = 4 + row * 7
            furrow_c = (80 - variant * 5, 50 - variant * 3, 20)
            for x in range(TILE_SIZE):
                set_pixel(s, x, yy, furrow_c)
    elif tile_type == "watered":
        water_tint = [(60, 100, 180), (40, 120, 190), (80, 90, 170)]
        wt = water_tint[variant % len(water_tint)]
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                blend = 0.6 + 0.4 * ((x + y + variant) % 4) / 4.0
                r = int(DARK_BROWN[0] * (1 - blend) + wt[0] * blend)
                g = int(DARK_BROWN[1] * (1 - blend) + wt[1] * blend)
                b = int(DARK_BROWN[2] * (1 - blend) + wt[2] * blend)
                set_pixel(s, x, y, (r, g, b))
        for row in range(4):
            yy = 4 + row * 7
            for x in range(TILE_SIZE):
                set_pixel(s, x, yy, (40 + variant * 5, 70 + variant * 5, 130 + variant * 5))
    SPRITE_CACHE[key] = s
    return s

CROP_PIXEL_DATA = {
    "glowroot": {
        "stages": [
            [("box", 13, 26, 6, 4, (40, 180, 40))],
            [("box", 12, 22, 8, 8, (40, 180, 40)), ("box", 13, 20, 6, 3, (60, 220, 60))],
            [("box", 11, 18, 10, 12, (40, 180, 40)), ("box", 13, 28, 6, 2, (100, 255, 100)),
             ("box", 14, 27, 4, 3, (150, 255, 150))],
        ],
    },
    "zargon_fruit": {
        "stages": [
            [("box", 14, 26, 4, 4, (120, 40, 160))],
            [("box", 8, 24, 16, 6, (80, 30, 120)), ("box", 14, 22, 4, 4, (120, 40, 160))],
            [("box", 6, 22, 20, 8, (80, 30, 120)), ("box", 10, 20, 4, 4, (160, 60, 200)),
             ("box", 18, 20, 4, 4, (160, 60, 200))],
            [("box", 8, 20, 16, 10, (60, 20, 100)), ("box", 6, 22, 20, 8, (80, 30, 120)),
             ("box", 10, 18, 4, 6, (180, 80, 220)), ("box", 18, 18, 4, 6, (180, 80, 220)),
             ("box", 12, 16, 8, 4, (200, 100, 240))],
        ],
    },
    "cosmic_wheat": {
        "stages": [
            [("box", 14, 26, 4, 4, (180, 180, 60))],
            [("box", 12, 22, 8, 8, (180, 180, 60)), ("box", 14, 20, 4, 4, (220, 200, 80))],
            [("box", 10, 18, 12, 12, (160, 160, 50)), ("box", 11, 16, 10, 4, (220, 220, 80)),
             ("box", 13, 14, 6, 4, (255, 220, 80)), ("box", 12, 12, 8, 3, (255, 240, 120))],
        ],
    },
    "starlight_melon": {
        "stages": [
            [("box", 14, 26, 4, 4, (60, 160, 200))],
            [("box", 12, 24, 8, 6, (80, 140, 180)), ("box", 14, 22, 4, 4, (60, 180, 220))],
            [("box", 10, 22, 12, 8, (80, 140, 180)), ("box", 8, 24, 4, 4, (60, 200, 100)),
             ("box", 20, 24, 4, 4, (60, 200, 100))],
            [("box", 10, 20, 12, 10, (60, 160, 200)), ("box", 12, 18, 8, 4, (100, 200, 255)),
             ("box", 14, 16, 4, 4, (80, 180, 220))],
            [("box", 8, 18, 16, 12, (60, 140, 200)), ("box", 9, 16, 14, 4, (100, 200, 255)),
             ("box", 12, 14, 8, 4, (130, 220, 255)), ("box", 10, 26, 12, 3, (40, 120, 180)),
             ("pixel", 14, 13, WHITE), ("pixel", 18, 15, WHITE), ("pixel", 10, 17, WHITE)],
        ],
    },
    "nebula_bloom": {
        "stages": [
            [("box", 14, 26, 4, 4, (200, 80, 160))],
            [("box", 14, 22, 4, 8, (40, 180, 40)), ("box", 13, 20, 6, 3, (200, 80, 160))],
            [("box", 14, 20, 4, 10, (40, 180, 40)), ("box", 11, 18, 10, 4, (220, 100, 180))],
            [("box", 14, 18, 4, 12, (40, 180, 40)), ("box", 8, 16, 16, 6, (255, 120, 200)),
             ("box", 10, 15, 12, 3, (255, 160, 220)), ("pixel", 14, 14, (255, 200, 100)),
             ("box", 6, 17, 4, 4, (200, 80, 160)), ("box", 22, 17, 4, 4, (200, 80, 160))],
        ],
    },
    "quasar_berry": {
        "stages": [
            [("box", 14, 26, 4, 4, (200, 60, 40))],
            [("box", 12, 24, 8, 6, (40, 180, 40)), ("box", 13, 22, 6, 4, (60, 200, 60))],
            [("box", 10, 22, 12, 8, (40, 180, 40)), ("box", 11, 20, 10, 4, (60, 200, 60)),
             ("box", 8, 24, 4, 4, (40, 160, 40))],
            [("box", 10, 22, 12, 8, (40, 180, 40)), ("box", 11, 20, 10, 4, (60, 200, 60)),
             ("box", 8, 24, 4, 4, (40, 160, 40)),
             ("box", 12, 20, 3, 3, (255, 80, 50)), ("box", 17, 20, 3, 3, (255, 80, 50)),
             ("box", 14, 22, 4, 3, (255, 60, 40)), ("box", 9, 22, 2, 3, (255, 80, 50)),
             ("box", 21, 22, 2, 3, (255, 80, 50))],
        ],
    },
}

def get_crop_surf(crop_key, stage, total_stages):
    key = f"crop_{crop_key}_{stage}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    s = make_surface(TILE_SIZE, TILE_SIZE)
    if crop_key in CROP_PIXEL_DATA:
        stages = CROP_PIXEL_DATA[crop_key]["stages"]
        idx = min(stage, len(stages) - 1)
        for cmd in stages[idx]:
            if cmd[0] == "box":
                _, x, y, w, h, color = cmd
                draw_box(s, x, y, w, h, color, True)
            elif cmd[0] == "pixel":
                _, x, y, color = cmd
                set_pixel(s, x, y, color)
    else:
        data = CROP_TYPES[crop_key]
        color = data["color"]
        base_y = TILE_SIZE - 4
        draw_box(s, 13, base_y - 4, 6, 6, color, True)
        draw_box(s, 14, base_y - 6, 4, 3, (40, 180, 40), True)
    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

def get_clean_building(building_type):
    key = f"clean_building_{building_type}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    sheet_name = SHEET_BUILDING.get(building_type)
    if sheet_name and os.path.exists(os.path.join("assets", sheet_name)):
        bw, bh = BUILDING_TYPES.get(building_type, {}).get("size", (3, 3))
        w, h = bw * TILE_SIZE, bh * TILE_SIZE
        sheet_surf = load_sprite_sheet(sheet_name)
        base = pygame.Surface((w, h), pygame.SRCALPHA)
        col, row = BUILDING_FRAME_MAP.get("default", (1, 1))
        base.blit(sheet_surf, (0, 0), (col * 96, row * 96, w, h))
        SPRITE_CACHE[key] = base
        return base
    key_96 = f"building_96_{building_type}"
    if key_96 not in SPRITE_CACHE:
        sheet_96_path = os.path.join("assets", f"building_{building_type}_96.png")
        if os.path.exists(sheet_96_path):
            raw = pygame.image.load(sheet_96_path).convert_alpha()
            bw, bh = BUILDING_TYPES.get(building_type, {}).get("size", (3, 3))
            w, h = bw * TILE_SIZE, bh * TILE_SIZE
            SPRITE_CACHE[key_96] = scale_to_fill(raw, w, h)
    if key_96 in SPRITE_CACHE:
        s = SPRITE_CACHE[key_96].copy()
    else:
        s = get_building_surf(building_type)
    SPRITE_CACHE[key] = s
    return s

def get_building_v2(building_type, anim_frame=0):
    t = pygame.time.get_ticks()
    key_96 = f"building_96_{building_type}"
    if key_96 not in SPRITE_CACHE:
        sheet_96_path = os.path.join("assets", f"building_{building_type}_96.png")
        if os.path.exists(sheet_96_path):
            raw = pygame.image.load(sheet_96_path).convert_alpha()
            bw, bh = BUILDING_TYPES.get(building_type, {}).get("size", (3, 3))
            w, h = bw * TILE_SIZE, bh * TILE_SIZE
            SPRITE_CACHE[key_96] = scale_to_fill(raw, w, h)
    if key_96 in SPRITE_CACHE:
        s = SPRITE_CACHE[key_96].copy()
        w, h = s.get_size()
    else:
        sheet_name = SHEET_BUILDING.get(building_type)
        col, row = BUILDING_FRAME_MAP.get("default", (1, 1))
        if sheet_name and os.path.exists(os.path.join("assets", sheet_name)):
            bw, bh = BUILDING_TYPES.get(building_type, {}).get("size", (3, 3))
            w, h = bw * TILE_SIZE, bh * TILE_SIZE
            key = f"building_sheet_{building_type}"
            if key not in SPRITE_CACHE:
                sheet_surf = load_sprite_sheet(sheet_name)
                base = pygame.Surface((w, h), pygame.SRCALPHA)
                base.blit(sheet_surf, (0, 0), (col * 96, row * 96, w, h))
                SPRITE_CACHE[key] = base
            s = SPRITE_CACHE[key].copy()
        else:
            base = get_building_surf(building_type)
            s = base.copy()
            bw, bh = BUILDING_TYPES.get(building_type, {}).get("size", (3, 3))
            w, h = bw * TILE_SIZE, bh * TILE_SIZE

    if building_type == "shop":
        smoke_y = 4 + (t // 200) % 8
        smoke_x = 18 + ((t // 300) % 5 - 2)
        set_pixel(s, smoke_x, smoke_y, (180, 180, 190))
        set_pixel(s, smoke_x + 1, smoke_y - 1, (160, 160, 170))
        for gx in [16, 26, 64, 78]:
            for gy in [36, 44, 52]:
                set_pixel(s, gx, gy, (255, 240, 200))
                set_pixel(s, gx + 1, gy, (255, 240, 180))

    elif building_type == "bar":
        neon = 0.5 + 0.5 * math.sin(t * 0.005)
        nr = int(200 + 55 * neon)
        ng = int(60 + 40 * neon)
        nb = int(100 + 80 * neon)
        for i in range(8):
            nx = 22 + i * 6
            set_pixel(s, nx, 14, (nr, ng, nb))
            set_pixel(s, nx, 15, (nr, ng, nb))
            set_pixel(s, nx, 16, (nr, ng, nb))

    elif building_type == "house":
        glow = 200 + int(40 * math.sin(t * 0.003))
        draw_box(s, 10, 14, 6, 6, (glow, glow, 255), True)
        draw_box(s, w - 16, 14, 6, 6, (glow, glow, 255), True)

    elif building_type == "player_house":
        glow = 200 + int(40 * math.sin(t * 0.003))
        draw_box(s, 8, 16, 6, 6, (glow, glow, 255), True)
        draw_box(s, w - 14, 16, 6, 6, (glow, glow, 255), True)

    elif building_type == "well":
        for wx in range(10, 22, 3):
            for wy in range(14, 20, 3):
                shimmer = int(40 * math.sin(t * 0.004 + wx * 0.5 + wy * 0.7))
                b = 200 + shimmer
                set_pixel(s, wx, wy, (100, b, 255))

    elif building_type == "greenhouse":
        pulse = int(25 * math.sin(t * 0.004))
        for gy in range(3):
            for gx in range(4):
                px = 6 + gx * ((w - 12) // 4)
                py = 6 + gy * ((h - 12) // 3)
                pw = (w - 12) // 4 - 2
                ph = (h - 12) // 3 - 2
                for i in range(2):
                    sx = px + 2 + ((gx * 7 + gy * 11 + i * 17 + t // 200) % max(1, pw - 4))
                    sy = py + 2 + ((gy * 13 + gx * 5 + t // 150) % max(1, ph - 4))
                    g = min(255, 140 + pulse + gy * 20)
                    set_pixel(s, sx, sy, (60, g, 60))

    elif building_type == "shipping_bin":
        if (t // 3000) % 2 == 0:
            hline(s, 2, 0, 28, (100, 80, 50))
            set_pixel(s, 16, 2, (180, 160, 80))
            set_pixel(s, 16, 3, (200, 180, 100))

    elif building_type == "barn":
        angle = t * 0.001
        vx, vy = w // 2, 2
        dx = int(4 * math.cos(angle))
        dy = int(4 * math.sin(angle))
        set_pixel(s, vx + dx, vy + dy, (200, 180, 100))
        set_pixel(s, vx - dx, vy - dy, (200, 180, 100))

    s.set_colorkey(BLACK)
    return s

def get_building_surf(building_type):
    key = f"building_{building_type}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    bw, bh = BUILDING_TYPES.get(building_type, {}).get("size", (3, 3))
    w, h = bw * TILE_SIZE, bh * TILE_SIZE
    s = make_surface(w, h)
    if building_type == "player_house":
        w, h = TILE_SIZE * 3, TILE_SIZE * 3
        s = make_surface(w, h)
        draw_box(s, 0, 0, w, h, (160, 140, 120), True)
        draw_box(s, 4, 4, w - 8, h - 8, (180, 160, 140), True)
        draw_box(s, w // 2 - 8, h - 20, 16, 20, (100, 80, 60), True)
        draw_box(s, 8, 12, w - 16, h + 12, (140, 120, 100), False)
        for yy in range(8, h - 8, 12):
            for xx in range(8, w - 8, 12):
                set_pixel(s, xx, yy, (200, 180, 160))
    elif building_type == "shop":
        w, h = TILE_SIZE * 3, TILE_SIZE * 3
        s = make_surface(w, h)
        draw_box(s, 0, 0, w, h, (100, 60, 140), True)
        draw_box(s, 4, 4, w - 8, h - 8, (130, 90, 170), True)
        draw_box(s, 8, 4, w - 16, 8, (160, 120, 200), True)
        draw_box(s, 12, 12, w - 24, 6, (80, 50, 120), True)
        for i in range(6):
            for j in range(3):
                set_pixel(s, 16 + i * 10, 14 + j * 2, (200, 180, 80))
        draw_box(s, 4, 20, 88, 4, (180, 140, 220), True)
        draw_box(s, 4, 20, 88, 4, (180, 140, 220), True)
        for stripe in range(8):
            ax = 4 + stripe * 11
            draw_box(s, ax, 20, 6, 4, (200, 150, 255) if stripe % 2 == 0 else (255, 200, 255), True)
        draw_box(s, 8, 28, 30, 36, (200, 220, 255), True)
        draw_box(s, 10, 30, 26, 32, (160, 200, 255), True)
        for gx in range(14, 34, 6):
            for gy in range(34, 58, 8):
                set_pixel(s, gx, gy, (100, 200, 100))
                set_pixel(s, gx, gy + 1, (80, 180, 80))
        draw_box(s, 58, 28, 30, 36, (200, 220, 255), True)
        draw_box(s, 60, 30, 26, 32, (160, 200, 255), True)
        for gx in range(64, 84, 6):
            for gy in range(34, 58, 8):
                set_pixel(s, gx, gy, (255, 180, 100))
                set_pixel(s, gx, gy + 1, (220, 150, 80))
        draw_box(s, 40, 30, 16, 36, (80, 50, 100), True)
        draw_box(s, 41, 30, 14, 36, (60, 35, 80), True)
        for knob_y in range(44, 52, 4):
            set_pixel(s, 48, knob_y, (200, 170, 100))
    elif building_type == "bar":
        w, h = TILE_SIZE * 3, TILE_SIZE * 3
        s = make_surface(w, h)
        draw_box(s, 0, 0, w, h, (80, 40, 40), True)
        draw_box(s, 4, 4, w - 8, h - 8, (110, 60, 60), True)
        draw_box(s, 8, 4, w - 16, 8, (150, 80, 80), True)
        draw_box(s, 12, 12, w - 24, 6, (60, 30, 30), True)
        for i in range(8):
            set_pixel(s, 22 + i * 6, 14, (255, 200, 80))
            set_pixel(s, 22 + i * 6, 15, (255, 220, 150))
            set_pixel(s, 22 + i * 6, 16, (255, 200, 80))
        draw_box(s, 4, 20, 88, 2, (60, 30, 30), True)
        draw_box(s, 10, 24, 30, 38, (60, 50, 30), True)
        draw_box(s, 12, 26, 26, 34, (80, 70, 50), True)
        draw_box(s, 14, 38, 22, 2, (120, 100, 60), True)
        for glass_y in range(28, 38, 3):
            set_pixel(s, 18, glass_y, (180, 200, 100))
            set_pixel(s, 30, glass_y, (180, 200, 100))
            set_pixel(s, 24, glass_y + 1, (200, 220, 120))
        draw_box(s, 56, 24, 30, 38, (60, 50, 30), True)
        draw_box(s, 58, 26, 26, 34, (80, 70, 50), True)
        draw_box(s, 60, 38, 22, 2, (120, 100, 60), True)
        for glass_y in range(28, 38, 3):
            set_pixel(s, 64, glass_y, (200, 100, 80))
            set_pixel(s, 76, glass_y, (200, 100, 80))
            set_pixel(s, 70, glass_y + 1, (255, 120, 100))
        draw_box(s, 42, 28, 12, 34, (70, 35, 35), True)
        draw_box(s, 43, 28, 10, 34, (50, 25, 25), True)
        for knob_y in range(40, 50, 4):
            set_pixel(s, 48, knob_y, (180, 150, 80))
        for star_y in range(60, 76, 8):
            mx, my = w // 2, star_y
            set_pixel(s, mx, my, (255, 220, 100))
            set_pixel(s, mx - 2, my, (255, 220, 100))
            set_pixel(s, mx + 2, my, (255, 220, 100))
            set_pixel(s, mx, my - 2, (255, 220, 100))
            set_pixel(s, mx, my + 2, (255, 220, 100))
    elif building_type == "house":
        w, h = TILE_SIZE * 3, TILE_SIZE * 3
        s = make_surface(w, h)
        draw_box(s, 0, 0, w, h, (140, 160, 180), True)
        draw_box(s, 4, 4, w - 8, h - 8, (160, 180, 200), True)
        draw_box(s, w // 2 - 8, h - 20, 16, 20, (100, 120, 140), True)
        draw_box(s, 8, 12, 8, 8, (180, 220, 255), True)
        draw_box(s, w - 16, 12, 8, 8, (180, 220, 255), True)
    elif building_type == "storage_shed":
        draw_box(s, 0, 0, w, h, (90, 70, 45), True)
        draw_box(s, 2, 2, w - 4, h - 4, (110, 85, 55), True)
        draw_box(s, 4, 4, w - 8, h - 8, (130, 100, 65), True)
        for plank_y in range(6, h - 6, 6):
            hline(s, 4, plank_y, w - 8, (100, 75, 45))
        draw_box(s, 0, 0, w, 3, (70, 55, 35), True)
        draw_box(s, 1, 0, w - 2, 2, (85, 65, 40), True)
        draw_box(s, 0, h - 4, w, 4, (70, 55, 35), True)
        dw = w // 3 - 4
        dh = h - 16
        dx1 = 4
        dx2 = dx1 + dw + 4
        for ddx, ddx2 in [(dx1, dx2)]:
            draw_box(s, ddx, 10, dw, dh, (70, 55, 35), True)
            draw_box(s, ddx + 1, 10, dw - 2, dh, (85, 65, 45), True)
            draw_box(s, ddx + 2, 10, dw - 4, dh, (100, 80, 55), True)
        for ddx in [dx1, dx2]:
            set_pixel(s, ddx + dw - 3, 10 + dh // 2, (180, 150, 70))
            set_pixel(s, ddx + dw - 3, 10 + dh // 2 + 1, (200, 170, 90))
        roof_peak = 4
        for dy in range(roof_peak):
            rw = w - (dy * 2)
            rx = dy
            draw_box(s, rx, -roof_peak + dy, rw, 1, (60, 45, 25), True)
            draw_box(s, rx, -roof_peak + dy + 1, rw, 1, (75, 55, 35), True)
    elif building_type == "well":
        color = (60, 100, 180)
        sh = (40, 70, 130)
        hl = (80, 140, 220)
        draw_box(s, 4, 8, 24, 20, sh, True)
        draw_box(s, 5, 9, 22, 18, color, True)
        draw_box(s, 6, 10, 20, 16, hl, True)
        draw_box(s, 10, 11, 12, 14, (50, 90, 170), True)
        draw_box(s, 11, 12, 10, 12, (80, 130, 210), True)
        for wx in range(8, 24, 4):
            for wy in range(13, 22, 4):
                set_pixel(s, wx, wy, (150, 200, 255))
        draw_box(s, 2, 6, 28, 4, (80, 70, 60), True)
        draw_box(s, 3, 6, 26, 3, (100, 85, 70), True)
        draw_box(s, 4, 6, 24, 2, (120, 100, 80), True)
        draw_box(s, 4, 1, 24, 6, sh, True)
        draw_box(s, 5, 1, 22, 5, color, True)
        draw_box(s, 6, 1, 20, 4, hl, True)
        draw_box(s, 14, 2, 4, 4, (50, 90, 170), True)
        for i in range(3):
            set_pixel(s, 12 + i * 4, 0, (150, 140, 120))
    elif building_type == "greenhouse":
        frame_color = (140, 120, 100)
        glass_color = (150, 220, 200)
        glass_hl = (200, 255, 240)
        # base
        draw_box(s, 0, 0, w, h, frame_color, True)
        draw_box(s, 2, 2, w - 4, h - 4, (100, 90, 75), True)
        draw_box(s, 4, 4, w - 8, h - 8, (80, 75, 60), True)
        # glass panels
        for gy in range(3):
            for gx in range(4):
                px = 6 + gx * ((w - 12) // 4)
                py = 6 + gy * ((h - 12) // 3)
                pw = (w - 12) // 4 - 2
                ph = (h - 12) // 3 - 2
                draw_box(s, px, py, pw, ph, glass_color, True)
                draw_box(s, px + 1, py + 1, pw - 2, ph - 2, glass_hl, True)
                # plants inside
                if gy < 2:
                    plant_color = (60 + gx * 20, 140 + gy * 30, 60 + gx * 10)
                    for _ in range(3):
                        sx = px + random.randint(2, pw - 3)
                        sy = py + random.randint(2, ph - 3)
                        set_pixel(s, sx, sy, plant_color)
                        set_pixel(s, sx, sy + 1, (plant_color[0] + 30, plant_color[1] + 20, plant_color[2]))
        # frame lines
        for gy in range(3):
            for gx in range(4):
                px = 6 + gx * ((w - 12) // 4)
                py = 6 + gy * ((h - 12) // 3)
                pw = (w - 12) // 4 - 2
                ph = (h - 12) // 3 - 2
                draw_box(s, px, py, pw, ph, frame_color, False)
    elif building_type == "shipping_bin":
        draw_box(s, 2, 4, 28, 28, (100, 70, 45), True)
        draw_box(s, 3, 5, 26, 26, (120, 85, 55), True)
        draw_box(s, 4, 6, 24, 24, (140, 100, 65), True)
        for plank_y in range(8, 28, 4):
            hline(s, 4, plank_y, 24, (110, 80, 50))
        draw_box(s, 2, 4, 28, 3, (80, 60, 35), True)
        draw_box(s, 3, 4, 26, 2, (100, 80, 50), True)
        draw_box(s, 2, 0, 28, 6, (80, 60, 35), True)
        draw_box(s, 3, 0, 26, 5, (100, 80, 50), True)
        draw_box(s, 4, 0, 24, 4, (120, 100, 65), True)
        set_pixel(s, 16, 2, (180, 160, 80))
        set_pixel(s, 16, 3, (200, 180, 100))
        draw_box(s, 2, 30, 28, 2, (80, 55, 35), True)
        draw_box(s, 3, 30, 26, 1, (100, 70, 45), True)
        draw_box(s, w - 2, 6, 1, 24, (90, 60, 40), True)
        draw_box(s, 1, 6, 1, 24, (90, 60, 40), True)
    elif building_type == "barn":
        draw_box(s, 0, 0, w, h, (110, 75, 45), True)
        draw_box(s, 2, 2, w - 4, h - 4, (130, 90, 55), True)
        draw_box(s, 4, 4, w - 8, h - 8, (150, 110, 70), True)
        for plank_y in range(6, h - 6, 6):
            hline(s, 4, plank_y, w - 8, (120, 85, 50))
        draw_box(s, 0, 0, w, 4, (80, 55, 30), True)
        draw_box(s, 1, 0, w - 2, 3, (100, 70, 40), True)
        draw_box(s, 8, 4, 16, 20, (80, 60, 35), True)
        draw_box(s, 9, 4, 14, 19, (100, 75, 45), True)
        draw_box(s, 10, 4, 12, 18, (120, 90, 55), True)
        dw, dh = w // 4, h // 2 - 8
        for ddx in [4, w - 4 - dw]:
            draw_box(s, ddx, h // 2 - 4, dw, dh, (70, 55, 35), True)
            draw_box(s, ddx + 1, h // 2 - 3, dw - 2, dh - 2, (85, 70, 45), True)
            draw_box(s, ddx + 2, h // 2 - 2, dw - 4, dh - 4, (100, 80, 55), True)
            set_pixel(s, ddx + dw - 3, h // 2 + dh // 2, (180, 150, 70))
        roof_peak = 6
        for dy in range(roof_peak):
            rw = w - (dy * 3)
            rx = dy * 1
            draw_box(s, rx, -roof_peak + dy, rw, 1, (65, 45, 25), True)
            draw_box(s, rx, -roof_peak + dy + 1, rw, 1, (80, 55, 35), True)
        draw_box(s, 0, h - 4, w, 4, (80, 55, 30), True)
        draw_box(s, 1, h - 4, w - 2, 3, (100, 70, 40), True)
    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

def get_prop_surf(prop_type):
    key = f"prop_{prop_type}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    if prop_type == "lamp_post":
        s = make_surface(TILE_SIZE, TILE_SIZE * 2)
        hline(s, 12, 0, 8, (100, 100, 120))
        draw_box(s, 13, 0, 6, 3, (180, 180, 200), True)
        draw_box(s, 14, 3, 4, 20, (80, 80, 100), True)
        draw_box(s, 15, 23, 2, 9, (100, 100, 120), True)
        draw_box(s, 14, 32, 4, 28, (80, 80, 100), True)
        draw_box(s, 15, 60, 2, 4, (100, 100, 120), True)
        s.set_colorkey(BLACK)
        SPRITE_CACHE[key] = s
        return s
    s = make_surface(TILE_SIZE, TILE_SIZE)
    if prop_type == "bench":
        draw_box(s, 2, 14, 28, 4, (100, 80, 55), True)
        draw_box(s, 2, 18, 28, 4, (110, 90, 60), True)
        draw_box(s, 4, 22, 4, 8, (80, 65, 45), True)
        draw_box(s, 24, 22, 4, 8, (80, 65, 45), True)
        draw_box(s, 14, 22, 4, 8, (80, 65, 45), True)
        draw_box(s, 2, 12, 28, 2, (80, 65, 45), True)
    elif prop_type == "fence":
        draw_box(s, 4, 6, 24, 2, (100, 75, 50), True)
        draw_box(s, 4, 14, 24, 2, (100, 75, 50), True)
        draw_box(s, 6, 6, 2, 10, (80, 60, 40), True)
        draw_box(s, 14, 6, 2, 10, (80, 60, 40), True)
        draw_box(s, 22, 6, 2, 10, (80, 60, 40), True)
    elif prop_type == "planter":
        draw_box(s, 2, 18, 28, 14, (100, 75, 50), True)
        draw_box(s, 3, 18, 26, 12, (80, 60, 40), True)
        draw_box(s, 4, 8, 24, 12, (60, 120, 60), True)
        draw_box(s, 6, 6, 20, 4, (80, 160, 80), True)
        for i in range(3):
            set_pixel(s, 10 + i * 6, 10, (200, 100, 200))
            set_pixel(s, 12 + i * 4, 12, (100, 200, 100))
    elif prop_type == "crate":
        draw_box(s, 4, 8, 24, 24, (120, 85, 50), True)
        draw_box(s, 5, 9, 22, 22, (140, 100, 60), True)
        draw_box(s, 6, 10, 20, 20, (160, 115, 70), True)
        draw_box(s, 4, 18, 24, 2, (100, 70, 40), True)
        draw_box(s, 16, 8, 2, 24, (100, 70, 40), True)
    elif prop_type == "signpost":
        draw_box(s, 14, 10, 4, 22, (90, 70, 50), True)
        draw_box(s, 4, 0, 24, 12, (120, 95, 60), True)
        draw_box(s, 5, 1, 22, 10, (100, 80, 50), True)
        draw_box(s, 6, 2, 20, 8, (80, 60, 40), True)
    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

DECORATION_PIXEL_DATA = {
    "flower_pink": [(8, 8, (255, 100, 150)), (9, 8, (255, 120, 170)), (8, 9, (255, 80, 130)),
                    (10, 9, (255, 140, 180)), (9, 10, (200, 60, 100))],
    "flower_yellow": [(8, 8, (255, 220, 50)), (9, 8, (255, 240, 80)), (8, 9, (255, 200, 30)),
                      (10, 9, (255, 255, 100)), (9, 10, (220, 180, 20))],
    "flower_purple": [(8, 8, (180, 80, 255)), (9, 8, (200, 100, 255)), (8, 9, (160, 60, 230)),
                      (10, 9, (220, 140, 255)), (9, 10, (140, 40, 200))],
    "flower_blue": [(8, 8, (80, 140, 255)), (9, 8, (100, 160, 255)), (8, 9, (60, 120, 230)),
                    (10, 9, (140, 200, 255)), (9, 10, (40, 100, 200))],
    "rock_small": [(14, 12, (130, 125, 120)), (15, 12, (140, 135, 130)), (14, 13, (120, 115, 110)),
                   (15, 13, (135, 130, 125))],
    "rock_medium": [(10, 10, (140, 135, 130)), (11, 10, (150, 145, 140)), (12, 10, (145, 140, 135)),
                    (10, 11, (130, 125, 120)), (11, 11, (145, 140, 135)), (12, 11, (140, 135, 130)),
                    (10, 12, (120, 115, 110)), (11, 12, (135, 130, 125)), (12, 12, (130, 125, 120))],
    "rock_large": [(8, 8, (140, 135, 130)), (9, 8, (150, 145, 140)), (10, 8, (155, 150, 145)), (11, 8, (145, 140, 135)),
                   (8, 9, (135, 130, 125)), (9, 9, (150, 145, 140)), (10, 9, (160, 155, 150)), (11, 9, (150, 145, 140)),
                   (8, 10, (130, 125, 120)), (9, 10, (145, 140, 135)), (10, 10, (155, 150, 145)), (11, 10, (145, 140, 135)),
                   (8, 11, (120, 115, 110)), (9, 11, (135, 130, 125)), (10, 11, (140, 135, 130)), (11, 11, (130, 125, 120))],
    "grass_tuft": [(12, 6, (40, 170, 40)), (12, 5, (50, 180, 50)), (13, 7, (45, 175, 45)),
                   (13, 4, (55, 190, 55)), (14, 6, (50, 185, 50)), (15, 5, (60, 200, 60))],
    "mushroom": [(10, 8, (200, 180, 160)), (11, 8, (220, 200, 180)), (10, 9, (180, 160, 140)),
                 (11, 9, (200, 180, 160)),
                 (9, 8, (220, 80, 100)), (10, 7, (240, 100, 120)), (11, 7, (230, 90, 110)), (12, 8, (210, 70, 90))],
    "crystal": [(10, 6, (150, 200, 255)), (11, 5, (180, 220, 255)), (10, 7, (130, 180, 240)),
                (11, 6, (170, 210, 255)), (12, 6, (200, 230, 255)), (10, 8, (110, 160, 230)),
                (11, 7, (160, 200, 250)), (12, 7, (180, 220, 255)), (11, 8, (140, 190, 245))],
}

def get_decoration_surf(deco_type):
    key = f"deco_{deco_type}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    s = make_surface(TILE_SIZE, TILE_SIZE)
    pixels = DECORATION_PIXEL_DATA.get(deco_type, [])
    for x, y, color in pixels:
        set_pixel(s, x, y, color)
    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

def get_interior_surf(interior_type):
    key = f"interior_{interior_type}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    w, h = SCREEN_WIDTH, SCREEN_HEIGHT
    s = make_surface(w, h)
    wall = (40, 35, 55)
    floor = (55, 50, 70)
    dark = (30, 25, 45)

    if interior_type == "kitchen":
        wall = (50, 40, 60)
        floor = (70, 55, 45)
        draw_box(s, 0, 0, w, h, wall, True)
        draw_box(s, 0, 300, w, 240, floor, True)
        hline(s, 0, 300, w, (60, 45, 35))
        # Counter
        draw_box(s, 20, 180, 300, 120, (100, 85, 65), True)
        draw_box(s, 20, 260, 300, 8, (140, 120, 90), True)
        draw_box(s, 20, 180, 300, 10, (120, 100, 80), True)
        # Stove
        draw_box(s, 340, 200, 120, 100, (60, 60, 75), True)
        draw_box(s, 350, 210, 30, 30, (200, 80, 60), True)
        draw_box(s, 390, 210, 30, 30, (200, 80, 60), True)
        draw_box(s, 430, 210, 20, 30, (80, 80, 100), True)
        # Shelves
        for sx in [480, 580, 680]:
            draw_box(s, sx, 100, 60, 180, (80, 65, 55), True)
            draw_box(s, sx, 100, 60, 6, (100, 85, 70), True)
            draw_box(s, sx + 10, 120, 10, 10, (100, 200, 100), True)
            draw_box(s, sx + 30, 140, 10, 15, (200, 100, 200), True)
            draw_box(s, sx + 20, 200, 15, 10, (200, 200, 100), True)
        # Window
        draw_box(s, 200, 40, 160, 100, (100, 140, 200), True)
        draw_box(s, 200, 40, 160, 100, (140, 180, 240), 2)
        hline(s, 200, 90, 160, (140, 180, 240))
        vline(s, 280, 40, 100, (140, 180, 240))

    elif interior_type == "workshop":
        wall = (55, 50, 60)
        floor = (65, 60, 70)
        draw_box(s, 0, 0, w, h, wall, True)
        draw_box(s, 0, 320, w, 220, floor, True)
        hline(s, 0, 320, w, (45, 40, 55))
        # Workbench
        draw_box(s, 30, 200, 400, 120, (120, 100, 75), True)
        draw_box(s, 30, 200, 400, 10, (140, 120, 90), True)
        draw_box(s, 30, 280, 400, 8, (100, 85, 60), True)
        # Tools on wall
        for ti in range(4):
            tx = 80 + ti * 80
            set_pixel(s, tx, 80, (180, 180, 200))
            set_pixel(s, tx, 82, (180, 180, 200))
            hline(s, tx - 3, 85, 6, (100, 80, 60))
        # Anvil
        draw_box(s, 500, 240, 80, 60, (100, 100, 110), True)
        draw_box(s, 510, 230, 60, 20, (80, 80, 95), True)
        draw_box(s, 520, 220, 40, 15, (120, 120, 130), True)
        # Shelf
        draw_box(s, 650, 80, 100, 200, (80, 70, 60), True)
        draw_box(s, 650, 80, 100, 6, (100, 85, 70), True)
        draw_box(s, 650, 140, 100, 6, (100, 85, 70), True)
        draw_box(s, 650, 200, 100, 6, (100, 85, 70), True)

    elif interior_type == "bar_interior":
        wall = (45, 25, 30)
        floor = (70, 55, 40)
        draw_box(s, 0, 0, w, h, wall, True)
        draw_box(s, 0, 320, w, 220, floor, True)
        hline(s, 0, 320, w, (55, 40, 30))
        # Bar counter
        draw_box(s, 0, 180, w, 140, (100, 60, 50), True)
        draw_box(s, 0, 180, w, 14, (130, 80, 65), True)
        draw_box(s, 0, 290, w, 8, (80, 50, 40), True)
        # Shelves with bottles
        for sx in [50, 180, 310, 440, 570, 700]:
            draw_box(s, sx, 100, 80, 80, (70, 50, 45), True)
            draw_box(s, sx, 100, 80, 5, (90, 65, 55), True)
            draw_box(s, sx + 20, 115, 8, 30, (100, 180, 100), True)
            draw_box(s, sx + 50, 120, 8, 25, (200, 100, 100), True)
            draw_box(s, sx + 35, 150, 10, 15, (180, 180, 100), True)
        # Neon sign
        for ni in range(5):
            nx = 200 + ni * 100
            draw_box(s, nx, 30, 80, 30, (100, 30, 50), True)
            draw_box(s, nx + 5, 35, 70, 20, (200, 60, 80), True)
            draw_box(s, nx + 10, 40, 60, 10, (255, 80, 100), True)

    elif interior_type == "barn_interior":
        wall = (50, 40, 25)
        floor = (75, 60, 35)
        draw_box(s, 0, 0, w, h, wall, True)
        draw_box(s, 0, 340, w, 200, floor, True)
        hline(s, 0, 340, w, (55, 45, 30))
        # Hay bales
        for hi in range(3):
            hx = 80 + hi * 120
            draw_box(s, hx, 260, 80, 80, (160, 150, 80), True)
            draw_box(s, hx, 260, 80, 6, (180, 170, 100), True)
        # Animal pens
        for pi in range(2):
            px = 400 + pi * 200
            draw_box(s, px, 280, 140, 60, (60, 50, 35), False)
            draw_box(s, px + 10, 320, 40, 20, (100, 120, 150), True)
            draw_box(s, px + 90, 320, 40, 20, (180, 140, 100), True)
        # Loft
        draw_box(s, 0, 0, w, 60, (70, 55, 35), True)
        draw_box(s, 0, 30, w, 6, (55, 40, 25), True)
        for li in range(8):
            set_pixel(s, 40 + li * 80, 10, (200, 180, 100))
            set_pixel(s, 40 + li * 80, 20, (200, 180, 100))

    elif interior_type == "shop_interior":
        wall = (60, 40, 80)
        floor = (80, 55, 50)
        draw_box(s, 0, 0, w, h, wall, True)
        draw_box(s, 0, 340, w, 300, floor, True)
        hline(s, 0, 340, w, (50, 30, 60))
        # Shelves left
        for sx in [30, 140]:
            draw_box(s, sx, 100, 80, 220, (90, 70, 60), True)
            draw_box(s, sx, 100, 80, 6, (110, 90, 75), True)
            draw_box(s, sx + 15, 120, 10, 10, (100, 200, 100), True)
            draw_box(s, sx + 45, 140, 10, 15, (200, 100, 200), True)
            draw_box(s, sx + 25, 200, 15, 10, (200, 200, 100), True)
            draw_box(s, sx + 55, 230, 10, 10, (100, 100, 200), True)
        # Counter
        draw_box(s, 300, 200, 300, 140, (120, 90, 70), True)
        draw_box(s, 300, 200, 300, 10, (140, 110, 85), True)
        draw_box(s, 300, 320, 300, 8, (100, 75, 55), True)
        # Register
        draw_box(s, 420, 210, 60, 40, (80, 80, 60), True)
        draw_box(s, 435, 220, 10, 10, (100, 255, 100), True)
        draw_box(s, 455, 220, 10, 10, (255, 100, 100), True)
        # Window
        draw_box(s, 680, 80, 180, 120, (120, 160, 220), True)
        draw_box(s, 680, 80, 180, 120, (160, 200, 255), 2)
        vline(s, 770, 80, 120, (160, 200, 255))
        hline(s, 680, 140, 180, (160, 200, 255))
        # Door frame right
        draw_box(s, 880, 160, 60, 180, (80, 60, 50), True)
        draw_box(s, 890, 170, 40, 160, (60, 40, 35), True)

    elif interior_type == "hangar_interior":
        wall = (60, 60, 75)
        floor = (80, 80, 95)
        draw_box(s, 0, 0, w, h, wall, True)
        draw_box(s, 0, 360, w, 180, floor, True)
        hline(s, 0, 360, w, (100, 100, 115))
        # Ship bay
        draw_box(s, 100, 120, 400, 240, (70, 70, 85), True)
        draw_box(s, 90, 110, 420, 260, (90, 90, 105), 2)
        # Ship silhouette placeholder
        draw_box(s, 200, 200, 200, 100, (140, 140, 160), True)
        draw_box(s, 220, 180, 160, 60, (160, 160, 180), True)
        draw_box(s, 260, 160, 80, 40, (180, 180, 200), True)
        # Control panel
        draw_box(s, 600, 280, 200, 80, (50, 50, 65), True)
        draw_box(s, 610, 290, 180, 60, (70, 70, 85), True)
        for ci in range(5):
            cx = 620 + ci * 35
            set_pixel(s, cx, 310, (100, 255, 100))
            set_pixel(s, cx, 320, (255, 100, 100))
            set_pixel(s, cx + 10, 315, (100, 100, 255))
        # Fuel pump
        draw_box(s, 740, 360, 60, 100, (60, 60, 80), True)
        draw_box(s, 750, 370, 40, 80, (80, 80, 100), True)
        # Lights
        for li in range(4):
            lx = 100 + li * 200
            set_pixel(s, lx, 50, (200, 200, 255))
            set_pixel(s, lx + 1, 50, (200, 200, 255))
            set_pixel(s, lx, 51, (200, 200, 255))

    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

def get_animal_surf(animal_type):
    key = f"animal_{animal_type}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    s = make_surface(32, 32)
    if animal_type == "zap_chicken":
        # Body
        draw_box(s, 8, 16, 16, 12, (255, 220, 100), True)
        draw_box(s, 9, 15, 14, 10, (255, 235, 140), True)
        draw_box(s, 10, 14, 12, 8, (255, 245, 180), True)
        # Eyes
        set_pixel(s, 12, 12, (255, 200, 50))
        set_pixel(s, 13, 12, (255, 200, 50))
        set_pixel(s, 19, 12, (255, 200, 50))
        set_pixel(s, 20, 12, (255, 200, 50))
        # Beak
        draw_box(s, 11, 13, 10, 2, (255, 180, 60), True)
        # Tail / wings
        set_pixel(s, 22, 14, (255, 150, 50))
        set_pixel(s, 23, 15, (255, 150, 50))
        # Legs
        for i in range(3):
            set_pixel(s, 5 + i * 2, 18 + i, (255, 220, 100))
            set_pixel(s, 26 - i * 2, 18 + i, (255, 220, 100))
        # Pupils
        set_pixel(s, 14, 14, (80, 60, 40))
        set_pixel(s, 17, 14, (80, 60, 40))
        # Sparkles
        for sp in range(4):
            sx = random.randint(6, 25)
            sy = random.randint(10, 18)
            set_pixel(s, sx, sy, (255, 255, 150))
        # Comb
        draw_box(s, 12, 11, 3, 2, (255, 100, 50), True)
        draw_box(s, 17, 11, 3, 2, (255, 100, 50), True)
        # Enhanced wing sparkle
        draw_box(s, 7, 15, 2, 4, (255, 200, 80), True)
        draw_box(s, 23, 15, 2, 4, (255, 200, 80), True)
    elif animal_type == "moo_droid":
        # Body
        draw_box(s, 6, 14, 20, 14, (100, 200, 255), True)
        draw_box(s, 7, 13, 18, 12, (130, 215, 255), True)
        draw_box(s, 8, 12, 16, 10, (160, 230, 255), True)
        # Belly stripe
        draw_box(s, 6, 16, 20, 3, (80, 180, 230), True)
        # Horns / antenna
        draw_box(s, 10, 10, 4, 4, (80, 180, 255), True)
        draw_box(s, 18, 10, 4, 4, (80, 180, 255), True)
        # Eyes
        set_pixel(s, 12, 12, (60, 60, 80))
        set_pixel(s, 13, 12, (60, 60, 80))
        set_pixel(s, 20, 12, (60, 60, 80))
        set_pixel(s, 21, 12, (60, 60, 80))
        # Nose / tag
        set_pixel(s, 16, 11, (60, 60, 80))
        # Legs
        set_pixel(s, 6, 22, (80, 160, 200))
        set_pixel(s, 7, 23, (80, 160, 200))
        set_pixel(s, 25, 22, (80, 160, 200))
        set_pixel(s, 24, 23, (80, 160, 200))
        for i in range(3):
            set_pixel(s, 10 + i, 26, (150, 200, 230))
            set_pixel(s, 19 + i, 26, (150, 200, 230))
        # Hooves
        set_pixel(s, 9, 27, (60, 60, 60))
        set_pixel(s, 22, 27, (60, 60, 60))
        # Bell / udder
        set_pixel(s, 14, 26, (200, 150, 80))
        set_pixel(s, 15, 26, (200, 150, 80))
        # Panel lights
        set_pixel(s, 12, 18, (100, 255, 100))
        set_pixel(s, 20, 18, (100, 255, 100))
        set_pixel(s, 16, 20, (255, 100, 100))
    elif animal_type == "fluffalo":
        # Fluffy body
        draw_box(s, 4, 10, 24, 18, (255, 180, 255), True)
        draw_box(s, 5, 9, 22, 16, (255, 200, 255), True)
        draw_box(s, 6, 8, 20, 14, (255, 220, 255), True)
        # Fluffy texture
        for fx in range(4, 28, 4):
            for fy in range(8, 24, 3):
                set_pixel(s, fx + random.randint(0, 2), fy, (255, 235, 255))
        # Ears
        draw_box(s, 9, 10, 4, 4, (255, 200, 220), True)
        draw_box(s, 19, 10, 4, 4, (255, 200, 220), True)
        # Eyes
        set_pixel(s, 11, 12, (80, 60, 100))
        set_pixel(s, 12, 12, (80, 60, 100))
        set_pixel(s, 21, 12, (80, 60, 100))
        set_pixel(s, 22, 12, (80, 60, 100))
        # Nose
        set_pixel(s, 16, 9, (180, 120, 180))
        set_pixel(s, 16, 10, (180, 120, 180))
        # Horns
        for i in range(4):
            set_pixel(s, 6 + i, 6, (255, 200, 255))
            set_pixel(s, 22 + i, 6, (255, 200, 255))
        # Legs
        for i in range(3):
            set_pixel(s, 8 + i * 6, 26, (220, 160, 220))
            set_pixel(s, 9 + i * 6, 27, (220, 160, 220))
            set_pixel(s, 10 + i * 6, 28, (220, 160, 220))
        # Tail poof
        draw_box(s, 2, 14, 3, 5, (255, 200, 255), True)
        draw_box(s, 1, 15, 2, 3, (255, 220, 255), True)
        # Sparkle
        set_pixel(s, 14, 6, WHITE)
        set_pixel(s, 18, 7, WHITE)
    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

ICON_PIXEL_DATA = {
    "glowroot": [("box", 4, 7, 8, 8, (100, 220, 100)), ("box", 6, 4, 4, 5, (40, 180, 40)), ("box", 7, 2, 2, 3, (40, 180, 40)), ("box", 8, 12, 2, 2, (150, 255, 150))],
    "zargon_fruit": [("box", 4, 6, 8, 9, (180, 60, 220)), ("box", 5, 5, 6, 3, (100, 40, 140)), ("box", 6, 4, 4, 2, (40, 180, 40))],
    "cosmic_wheat": [("box", 7, 3, 2, 12, (180, 180, 60)), ("box", 5, 2, 6, 4, (255, 220, 80)), ("box", 6, 1, 4, 2, (200, 200, 60)), ("box", 4, 9, 2, 6, (40, 180, 40)), ("box", 10, 10, 2, 5, (40, 180, 40))],
    "starlight_melon": [("box", 3, 6, 10, 9, (80, 180, 255)), ("box", 4, 5, 8, 3, (130, 200, 255)), ("box", 6, 4, 4, 2, (40, 180, 40)), ("pixel", 8, 4, WHITE), ("pixel", 4, 9, WHITE)],
    "nebula_bloom": [("box", 7, 4, 2, 10, (40, 180, 40)), ("box", 3, 2, 10, 6, (255, 100, 200)), ("box", 4, 1, 8, 3, (255, 140, 220)), ("pixel", 7, 3, (255, 200, 100))],
    "quasar_berry": [("box", 4, 8, 8, 6, (40, 180, 40)), ("box", 3, 7, 10, 3, (60, 200, 60)), ("box", 5, 7, 3, 3, (255, 80, 50)), ("box", 9, 7, 3, 3, (255, 80, 50)), ("box", 7, 8, 3, 3, (255, 60, 40))],
    "glowroot_seed": [("box", 3, 5, 10, 8, (200, 180, 100)), ("box", 5, 6, 6, 6, (160, 140, 80)), ("box", 6, 7, 4, 4, (100, 220, 100)), ("box", 7, 3, 2, 3, (40, 180, 40))],
    "zargon_fruit_seed": [("box", 3, 5, 10, 8, (200, 180, 100)), ("box", 5, 6, 6, 6, (160, 140, 80)), ("box", 6, 7, 4, 4, (180, 60, 220)), ("box", 7, 3, 2, 3, (40, 180, 40))],
    "cosmic_wheat_seed": [("box", 3, 5, 10, 8, (200, 180, 100)), ("box", 5, 6, 6, 6, (160, 140, 80)), ("box", 6, 7, 4, 4, (255, 220, 80)), ("box", 7, 3, 2, 3, (40, 180, 40))],
    "starlight_melon_seed": [("box", 3, 5, 10, 8, (200, 180, 100)), ("box", 5, 6, 6, 6, (160, 140, 80)), ("box", 6, 7, 4, 4, (80, 180, 255)), ("box", 7, 3, 2, 3, (40, 180, 40))],
    "nebula_bloom_seed": [("box", 3, 5, 10, 8, (200, 180, 100)), ("box", 5, 6, 6, 6, (160, 140, 80)), ("box", 6, 7, 4, 4, (255, 100, 200)), ("box", 7, 3, 2, 3, (40, 180, 40))],
    "quasar_berry_seed": [("box", 3, 5, 10, 8, (200, 180, 100)), ("box", 5, 6, 6, 6, (160, 140, 80)), ("box", 6, 7, 4, 4, (255, 80, 50)), ("box", 7, 3, 2, 3, (40, 180, 40))],
    "glowroot_salad": [("box", 2, 4, 12, 10, (100, 180, 100)), ("box", 3, 3, 10, 3, (140, 220, 140)), ("box", 4, 2, 8, 2, (60, 200, 60)), ("box", 6, 7, 4, 3, (200, 120, 60))],
    "zargon_jam": [("box", 2, 4, 12, 10, (100, 60, 140)), ("box", 3, 3, 10, 2, (60, 30, 80)), ("box", 4, 2, 8, 2, (40, 20, 60)), ("box", 6, 8, 4, 4, (180, 80, 220))],
    "cosmic_bread": [("box", 2, 6, 12, 8, (200, 170, 100)), ("box", 3, 5, 10, 3, (220, 190, 120)), ("box", 4, 4, 8, 2, (180, 150, 80))],
    "starlight_juice": [("box", 3, 4, 10, 10, (80, 160, 220)), ("box", 4, 3, 8, 2, (60, 120, 180)), ("box", 5, 2, 6, 2, (40, 80, 140)), ("pixel", 8, 6, WHITE)],
    "nebula_tea": [("box", 3, 5, 10, 9, (200, 120, 180)), ("box", 4, 4, 8, 2, (160, 80, 140)), ("box", 5, 3, 6, 2, (220, 140, 200)), ("pixel", 7, 9, (255, 200, 100))],
    "berry_smoothie": [("box", 3, 4, 10, 10, (200, 80, 100)), ("box", 4, 3, 8, 2, (160, 50, 70)), ("box", 5, 2, 6, 2, (220, 100, 120)), ("pixel", 6, 7, (255, 200, 200))],
    "farm_feast": [("box", 2, 6, 12, 8, (200, 160, 80)), ("box", 4, 4, 8, 3, (100, 200, 100)), ("box", 3, 3, 10, 2, (140, 100, 60)), ("box", 6, 9, 4, 2, (255, 80, 50))],
    "galaxy_delight": [("box", 2, 4, 12, 10, (120, 80, 160)), ("box", 3, 3, 10, 2, (80, 40, 120)), ("box", 4, 2, 8, 2, (160, 100, 200)), ("pixel", 5, 7, WHITE), ("pixel", 11, 7, WHITE)],
    "starlight_omelette": [("box", 2, 5, 12, 9, (200, 180, 120)), ("box", 3, 4, 10, 3, (220, 200, 140)), ("box", 5, 3, 6, 2, (255, 220, 160)), ("box", 6, 8, 4, 3, (200, 100, 60))],
    "nebula_milkshake": [("box", 3, 4, 10, 10, (180, 120, 200)), ("box", 4, 3, 8, 2, (140, 80, 160)), ("box", 5, 2, 6, 2, (200, 140, 220)), ("box", 6, 10, 4, 2, (255, 200, 100))],
    "fish_tacos": [("box", 2, 5, 12, 9, (200, 180, 100)), ("box", 4, 4, 8, 3, (100, 200, 200)), ("box", 3, 3, 10, 2, (160, 120, 60)), ("box", 5, 8, 6, 3, (120, 160, 255))],
    "sushi_platter": [("box", 2, 5, 12, 9, (180, 160, 200)), ("box", 3, 4, 10, 3, (140, 120, 160)), ("box", 4, 3, 8, 2, (200, 180, 220)), ("box", 6, 8, 4, 3, (220, 120, 160))],
    "glowroot_chips": [("box", 2, 6, 12, 8, (180, 160, 80)), ("box", 3, 5, 10, 3, (200, 180, 100)), ("box", 4, 4, 8, 2, (160, 140, 60)), ("box", 5, 8, 6, 2, (100, 200, 100))],
    "cosmic_flour": [("box", 2, 4, 12, 10, (200, 200, 180)), ("box", 3, 3, 10, 2, (180, 180, 160)), ("box", 4, 2, 8, 2, (220, 220, 200)), ("pixel", 8, 8, WHITE)],
    "zargon_wine": [("box", 2, 5, 12, 9, (100, 40, 140)), ("box", 3, 4, 10, 2, (60, 20, 100)), ("box", 4, 2, 8, 3, (80, 30, 120)), ("box", 7, 10, 2, 2, (200, 100, 240))],
    "starlight_jam": [("box", 2, 4, 12, 10, (80, 140, 200)), ("box", 3, 3, 10, 2, (50, 100, 160)), ("box", 4, 2, 8, 2, (100, 160, 220)), ("pixel", 6, 8, WHITE)],
    "nebula_perfume": [("box", 3, 4, 10, 10, (140, 80, 180)), ("box", 4, 3, 8, 2, (100, 50, 140)), ("box", 5, 2, 6, 2, (160, 100, 200)), ("box", 6, 9, 4, 3, (255, 200, 100))],
    "cosmic_wine": [("box", 2, 5, 12, 9, (140, 100, 60)), ("box", 3, 4, 10, 2, (100, 60, 40)), ("box", 4, 2, 8, 3, (160, 120, 80)), ("box", 6, 10, 4, 2, (255, 220, 80))],
    "woolen_scarf": [("box", 2, 5, 12, 9, (180, 140, 180)), ("box", 3, 4, 10, 3, (200, 160, 200)), ("box", 4, 3, 8, 2, (160, 120, 160)), ("box", 5, 8, 6, 3, (140, 100, 140))],
    "aged_cheese": [("box", 3, 5, 10, 9, (220, 200, 120)), ("box", 4, 4, 8, 3, (200, 180, 100)), ("box", 5, 3, 6, 2, (240, 220, 140)), ("pixel", 6, 8, (160, 140, 60))],
    "nebula_trout": [("box", 2, 6, 12, 5, (120, 180, 255)), ("box", 3, 5, 10, 2, (80, 140, 220)), ("box", 14, 6, 2, 5, (100, 160, 240)), ("pixel", 4, 7, WHITE)],
    "bloom_bass": [("box", 2, 6, 12, 5, (100, 220, 100)), ("box", 3, 5, 10, 2, (60, 180, 60)), ("box", 14, 6, 2, 5, (80, 200, 80)), ("pixel", 4, 7, WHITE)],
    "solar_salmon": [("box", 2, 6, 12, 5, (255, 180, 80)), ("box", 3, 5, 10, 2, (200, 140, 50)), ("box", 14, 6, 2, 5, (220, 160, 60)), ("pixel", 4, 7, WHITE)],
    "void_catfish": [("box", 2, 6, 12, 5, (80, 60, 120)), ("box", 3, 5, 10, 2, (50, 40, 80)), ("box", 14, 6, 2, 5, (60, 50, 100)), ("pixel", 4, 7, (200, 200, 200))],
    "starlight_sturgeon": [("box", 2, 5, 14, 6, (200, 220, 255)), ("box", 3, 4, 12, 2, (160, 180, 220)), ("box", 16, 5, 2, 6, (180, 200, 240)), ("pixel", 5, 6, (80, 100, 160))],
    "cosmic_koi": [("box", 2, 6, 12, 5, (255, 150, 200)), ("box", 3, 5, 10, 2, (200, 100, 160)), ("box", 14, 6, 2, 5, (220, 120, 180)), ("pixel", 4, 7, WHITE), ("pixel", 8, 7, (255, 200, 100))],
    "hoe": [("box", 7, 2, 2, 12, (160, 140, 100)), ("box", 4, 10, 8, 4, (120, 120, 120))],
    "water": [("box", 6, 2, 4, 12, (100, 150, 200)), ("box", 4, 4, 8, 4, (120, 120, 120))],
    "scythe": [("box", 7, 2, 2, 12, (140, 120, 80)), ("box", 2, 2, 12, 3, (180, 180, 180))],
    "starlight_egg": [("box", 4, 5, 8, 8, (200, 200, 180)), ("box", 5, 4, 6, 3, (220, 220, 200)), ("pixel", 6, 6, (180, 200, 255))],
    "nebula_milk": [("box", 3, 4, 10, 10, (200, 200, 240)), ("box", 4, 3, 8, 2, (180, 180, 220)), ("box", 5, 2, 6, 2, (220, 220, 255))],
    "cosmic_wool": [("box", 3, 4, 10, 10, (255, 200, 255)), ("box", 4, 3, 8, 8, (255, 220, 255)), ("box", 5, 2, 6, 3, (255, 180, 240))],
}

def get_crop_icon(crop_key):
    key = f"icon_{crop_key}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    s = make_surface(16, 16)
    if crop_key in ICON_PIXEL_DATA:
        for cmd in ICON_PIXEL_DATA[crop_key]:
            if cmd[0] == "box":
                _, x, y, w, h, color = cmd
                draw_box(s, x, y, w, h, color, True)
            elif cmd[0] == "pixel":
                _, x, y, color = cmd
                set_pixel(s, x, y, color)
    else:
        color = CROP_TYPES[crop_key]["color"]
        draw_box(s, 4, 8, 8, 8, color, True)
        draw_box(s, 6, 4, 4, 6, (40, 180, 40), True)
        draw_box(s, 7, 2, 2, 3, (40, 180, 40), True)
    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

def get_item_icon(item_name):
    key = f"item_{item_name}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    s = make_surface(16, 16)
    if item_name.lower() in ICON_PIXEL_DATA:
        for cmd in ICON_PIXEL_DATA[item_name.lower()]:
            if cmd[0] == "box":
                _, x, y, w, h, color = cmd
                draw_box(s, x, y, w, h, color, True)
            elif cmd[0] == "pixel":
                _, x, y, color = cmd
                set_pixel(s, x, y, color)
    elif "seed" in item_name.lower() or "seeds" in item_name.lower():
        draw_box(s, 4, 6, 8, 8, (200, 180, 100), True)
        set_pixel(s, 7, 8, (100, 200, 100))
        set_pixel(s, 9, 10, (100, 200, 100))
    else:
        draw_box(s, 2, 2, 12, 12, PURPLE, True)
    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

def get_heart_surf(filled=True):
    key = f"heart_{filled}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    s = make_surface(12, 12)
    if filled:
        c = RED
    else:
        c = (80, 80, 80)
    set_pixel(s, 2, 3, c); set_pixel(s, 3, 2, c)
    set_pixel(s, 4, 2, c); set_pixel(s, 5, 3, c)
    set_pixel(s, 6, 3, c); set_pixel(s, 7, 2, c)
    set_pixel(s, 8, 2, c); set_pixel(s, 9, 3, c)
    for x in range(2, 10):
        set_pixel(s, x, 4, c)
        set_pixel(s, x, 5, c)
    for x in range(3, 9):
        set_pixel(s, x, 6, c)
    for x in range(4, 8):
        set_pixel(s, x, 7, c)
    for x in range(5, 7):
        set_pixel(s, x, 8, c)
    set_pixel(s, 6, 9, c)
    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

def get_star_surf():
    key = "star"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    s = make_surface(4, 4)
    set_pixel(s, 1, 0, WHITE)
    set_pixel(s, 2, 0, WHITE)
    set_pixel(s, 0, 1, WHITE)
    set_pixel(s, 1, 1, YELLOW)
    set_pixel(s, 2, 1, YELLOW)
    set_pixel(s, 3, 1, WHITE)
    set_pixel(s, 1, 2, WHITE)
    set_pixel(s, 2, 2, WHITE)
    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

def get_bot_surf(bot_type):
    key = f"bot_{bot_type}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    sheet_32_path = os.path.join("assets", f"bot_{bot_type}_32.png")
    if os.path.exists(sheet_32_path):
        raw = pygame.image.load(sheet_32_path).convert_alpha()
        s = scale_to_fill(raw, 32, 32)
    else:
        sheet_name = SHEET_BOT.get(bot_type)
        if sheet_name and os.path.exists(os.path.join("assets", sheet_name)):
            s = get_sheet_frame(sheet_name, 2, 0, 32, 32).copy()
        else:
            from src.constants import BOT_TYPES
            c = BOT_TYPES[bot_type]["color"]
            s = make_surface(TILE_SIZE, TILE_SIZE)
            if bot_type == "water_bot":
                draw_box(s, 6, 6, 20, 16, c, True)
                draw_box(s, 7, 4, 18, 4, (c[0]//2, c[1]//2, c[2]//2), True)
                draw_box(s, 12, 4, 8, 3, c, True)
                set_pixel(s, 10, 4, WHITE)
                set_pixel(s, 22, 4, WHITE)
                draw_box(s, 9, 8, 14, 10, (c[0]//2, c[1]//2, c[2]//2), True)
                set_pixel(s, 12, 10, WHITE)
                set_pixel(s, 20, 10, WHITE)
                draw_box(s, 13, 12, 6, 3, (60, 60, 80), True)
                draw_box(s, 11, 20, 4, 4, (60, 60, 80), True)
                draw_box(s, 17, 20, 4, 4, (60, 60, 80), True)
                draw_box(s, 8, 22, 16, 3, (c[0]//2, c[1]//2, c[2]//2), True)
            elif bot_type == "sprout_bot":
                draw_box(s, 4, 8, 24, 14, c, True)
                draw_box(s, 6, 6, 20, 4, (c[0]//2, c[1]//2, c[2]//2), True)
                draw_box(s, 14, 2, 4, 6, (60, 200, 60), True)
                draw_box(s, 13, 1, 6, 2, (80, 220, 80), True)
                set_pixel(s, 12, 6, WHITE)
                set_pixel(s, 20, 6, WHITE)
                draw_box(s, 8, 10, 16, 10, (c[0]//2, c[1]//2, c[2]//2), True)
                set_pixel(s, 12, 12, WHITE)
                set_pixel(s, 20, 12, WHITE)
                draw_box(s, 10, 20, 4, 4, (60, 60, 80), True)
                draw_box(s, 18, 20, 4, 4, (60, 60, 80), True)
                draw_box(s, 8, 22, 16, 3, (c[0]//2, c[1]//2, c[2]//2), True)
            elif bot_type == "harvest_bot":
                draw_box(s, 4, 4, 24, 20, c, True)
                draw_box(s, 6, 6, 20, 16, (c[0]//2, c[1]//2, c[2]//2), True)
                draw_box(s, 8, 8, 16, 12, (c[0]//3, c[1]//3, c[2]//3), True)
                set_pixel(s, 10, 8, WHITE)
                set_pixel(s, 14, 8, WHITE)
                set_pixel(s, 18, 8, WHITE)
                set_pixel(s, 22, 8, WHITE)
                draw_box(s, 10, 12, 12, 4, (c[0]//2, c[1]//2, c[2]//2), True)
                set_pixel(s, 14, 16, (255, 200, 100))
                set_pixel(s, 16, 16, (255, 200, 100))
                set_pixel(s, 18, 16, (255, 200, 100))
                draw_box(s, 8, 22, 4, 4, (60, 60, 80), True)
                draw_box(s, 16, 22, 4, 4, (60, 60, 80), True)
                draw_box(s, 20, 22, 4, 4, (60, 60, 80), True)
            elif bot_type == "mega_water_bot":
                draw_box(s, 4, 4, 24, 20, c, True)
                draw_box(s, 6, 6, 20, 16, (c[0]//2, c[1]//2, c[2]//2), True)
                draw_box(s, 10, 2, 12, 4, c, True)
                set_pixel(s, 10, 2, WHITE)
                set_pixel(s, 22, 2, WHITE)
                draw_box(s, 12, 8, 8, 10, (c[0]//3, c[1]//3, c[2]//3), True)
                set_pixel(s, 10, 12, (100, 200, 255))
                set_pixel(s, 22, 12, (100, 200, 255))
                set_pixel(s, 14, 10, WHITE)
                set_pixel(s, 18, 10, WHITE)
                draw_box(s, 12, 20, 8, 2, (c[0]//2, c[1]//2, c[2]//2), True)
                draw_box(s, 8, 22, 4, 4, (80, 80, 100), True)
                draw_box(s, 14, 22, 4, 4, (80, 80, 100), True)
                draw_box(s, 20, 22, 4, 4, (80, 80, 100), True)
            elif bot_type == "mega_harvest_bot":
                draw_box(s, 2, 4, 28, 20, c, True)
                draw_box(s, 4, 6, 24, 16, (c[0]//2, c[1]//2, c[2]//2), True)
                draw_box(s, 6, 8, 20, 12, (c[0]//3, c[1]//3, c[2]//3), True)
                set_pixel(s, 8, 6, WHITE)
                set_pixel(s, 12, 6, WHITE)
                set_pixel(s, 16, 6, WHITE)
                set_pixel(s, 20, 6, WHITE)
                set_pixel(s, 24, 6, WHITE)
                draw_box(s, 10, 10, 12, 6, (c[0]//2, c[1]//2, c[2]//2), True)
                set_pixel(s, 14, 14, (255, 200, 100))
                set_pixel(s, 18, 14, (255, 200, 100))
                draw_box(s, 6, 22, 4, 4, (80, 80, 100), True)
                draw_box(s, 12, 22, 4, 4, (80, 80, 100), True)
                draw_box(s, 18, 22, 4, 4, (80, 80, 100), True)
                draw_box(s, 24, 22, 4, 4, (80, 80, 100), True)
            else:
                draw_box(s, 6, 4, 20, 18, c, True)
                draw_box(s, 8, 6, 16, 14, (c[0]//2, c[1]//2, c[2]//2), True)
                set_pixel(s, 10, 4, WHITE)
                set_pixel(s, 22, 4, WHITE)
                set_pixel(s, 14, 8, c)
                set_pixel(s, 18, 8, c)
                draw_box(s, 12, 18, 4, 6, (60, 60, 80), True)
                draw_box(s, 18, 18, 4, 6, (60, 60, 80), True)
    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

def get_ship_surf(tier):
    key = f"ship_{tier}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    s = make_surface(TILE_SIZE, TILE_SIZE)
    if tier == 0:
        c = (160, 180, 200)
        draw_box(s, 8, 16, 16, 6, c, True)
        draw_box(s, 10, 12, 12, 6, (c[0]//2, c[1]//2, c[2]//2), True)
        draw_box(s, 12, 8, 8, 6, c, True)
        draw_box(s, 14, 6, 4, 4, (c[0]//2, c[1]//2, c[2]//2), True)
        set_pixel(s, 14, 18, GOLD)
    elif tier == 1:
        c = (200, 180, 120)
        draw_box(s, 6, 14, 20, 8, c, True)
        draw_box(s, 8, 10, 16, 6, (c[0]//2, c[1]//2, c[2]//2), True)
        draw_box(s, 10, 6, 12, 6, c, True)
        draw_box(s, 14, 2, 4, 6, (c[0]//2, c[1]//2, c[2]//2), True)
        draw_box(s, 4, 16, 24, 2, (c[0]//2, c[1]//2, c[2]//2), True)
        set_pixel(s, 12, 16, GOLD)
        set_pixel(s, 20, 16, GOLD)
        set_pixel(s, 14, 18, (255, 100, 100))
    else:
        c = (220, 200, 255)
        draw_box(s, 4, 12, 24, 10, c, True)
        draw_box(s, 6, 8, 20, 6, (c[0]//2, c[1]//2, c[2]//2), True)
        draw_box(s, 8, 4, 16, 6, c, True)
        draw_box(s, 12, 0, 8, 6, (c[0]//2, c[1]//2, c[2]//2), True)
        draw_box(s, 4, 16, 24, 2, (c[0]//2, c[1]//2, c[2]//2), True)
        draw_box(s, 2, 18, 28, 2, (c[0]//3, c[1]//3, c[2]//3), True)
        set_pixel(s, 14, 14, GOLD)
        set_pixel(s, 18, 14, GOLD)
        set_pixel(s, 24, 14, GOLD)
        set_pixel(s, 12, 18, (100, 255, 100))
        set_pixel(s, 20, 18, (100, 255, 100))
    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

def get_fish_surf(fish_id):
    key = f"fish_{fish_id}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    from src.constants import FISH_TYPES
    c = FISH_TYPES[fish_id]["color"]
    dark = (c[0] // 2, c[1] // 2, c[2] // 2)
    s = make_surface(TILE_SIZE, TILE_SIZE)
    if fish_id == "nebula_trout":
        draw_box(s, 8, 12, 14, 8, c, True)
        draw_box(s, 9, 17, 12, 2, dark, True)
        draw_box(s, 22, 11, 6, 10, c, True)
        draw_box(s, 26, 12, 3, 3, c, True)
        draw_box(s, 26, 17, 3, 3, c, True)
        draw_box(s, 11, 9, 8, 3, dark, True)
        set_pixel(s, 10, 14, WHITE)
        set_pixel(s, 11, 14, BLACK)
        for sp in range(3):
            set_pixel(s, 14 + sp * 3, 15, (200, 220, 255))
    elif fish_id == "bloom_bass":
        draw_box(s, 7, 12, 16, 8, c, True)
        draw_box(s, 8, 17, 14, 2, dark, True)
        draw_box(s, 23, 11, 5, 10, c, True)
        draw_box(s, 11, 9, 6, 3, dark, True)
        set_pixel(s, 9, 14, WHITE)
        set_pixel(s, 10, 14, BLACK)
        draw_box(s, 12, 13, 6, 3, (40, 180, 40), True)
    elif fish_id == "solar_salmon":
        draw_box(s, 8, 11, 14, 9, c, True)
        draw_box(s, 9, 17, 12, 2, dark, True)
        draw_box(s, 22, 10, 6, 11, c, True)
        draw_box(s, 26, 11, 3, 4, c, True)
        draw_box(s, 26, 17, 3, 4, c, True)
        draw_box(s, 12, 8, 6, 4, dark, True)
        set_pixel(s, 10, 13, WHITE)
        set_pixel(s, 11, 13, BLACK)
        draw_box(s, 14, 14, 4, 3, (255, 200, 100), True)
    elif fish_id == "void_catfish":
        draw_box(s, 6, 13, 16, 7, c, True)
        draw_box(s, 7, 17, 14, 2, dark, True)
        draw_box(s, 22, 12, 6, 8, c, True)
        draw_box(s, 12, 8, 4, 5, dark, True)
        draw_box(s, 11, 7, 6, 2, (60, 50, 100), True)
        set_pixel(s, 8, 14, (200, 200, 200))
        set_pixel(s, 9, 14, (60, 60, 60))
        draw_box(s, 4, 15, 2, 3, c, True)
    elif fish_id == "starlight_sturgeon":
        draw_box(s, 6, 11, 18, 9, c, True)
        draw_box(s, 7, 17, 16, 2, dark, True)
        draw_box(s, 24, 10, 6, 11, c, True)
        draw_box(s, 28, 11, 3, 4, c, True)
        draw_box(s, 28, 17, 3, 4, c, True)
        draw_box(s, 10, 8, 10, 3, dark, True)
        set_pixel(s, 8, 13, (100, 140, 200))
        set_pixel(s, 9, 13, BLACK)
        for sp in range(4):
            set_pixel(s, 14 + sp * 3, 14, WHITE)
    elif fish_id == "cosmic_koi":
        draw_box(s, 8, 11, 14, 9, c, True)
        draw_box(s, 9, 17, 12, 2, dark, True)
        draw_box(s, 22, 11, 6, 9, c, True)
        draw_box(s, 12, 8, 6, 3, dark, True)
        set_pixel(s, 10, 13, WHITE)
        set_pixel(s, 11, 13, BLACK)
        draw_box(s, 12, 13, 6, 4, (255, 200, 100), True)
        for sp in range(3):
            set_pixel(s, 6 + sp * 2, 12 + sp, (255, 200, 255))
            set_pixel(s, 6 + sp * 2, 16 - sp, (255, 200, 255))
    else:
        draw_box(s, 8, 12, 14, 8, c, True)
        draw_box(s, 9, 17, 12, 2, dark, True)
        draw_box(s, 22, 11, 6, 10, c, True)
        draw_box(s, 12, 9, 6, 3, dark, True)
        set_pixel(s, 10, 14, WHITE)
        set_pixel(s, 11, 14, BLACK)
    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

def get_bobber_surf():
    key = "bobber"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    s = make_surface(12, 12)
    draw_box(s, 3, 0, 6, 6, (220, 60, 60), True)   # red top
    draw_box(s, 3, 6, 6, 5, (240, 240, 240), True)  # white bottom
    hline(s, 3, 5, 6, (120, 30, 30))
    set_pixel(s, 5, 2, WHITE)
    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

def draw_panel(surf, x, y, w, h, border_color, title=None, alpha=180):
    shadow = pygame.Surface((w, h))
    shadow.set_alpha(60)
    shadow.fill((0, 0, 0))
    surf.blit(shadow, (x + 3, y + 3))
    for i in range(h):
        t = i / max(h - 1, 1)
        r = int(15 * (1 - t) + 8 * t)
        g = int(20 * (1 - t) + 10 * t)
        b = int(40 * (1 - t) + 25 * t)
        pygame.draw.line(surf, (r, g, b), (x, y + i), (x + w, y + i))
    pygame.draw.rect(surf, border_color, (x, y, w, h), 2)
    pygame.draw.line(surf, (r + 30, g + 30, b + 30), (x + 2, y + 2), (x + w - 3, y + 2))
    if title:
        from src.ui.context import draw_text
        draw_text(surf, title, x + w // 2, y + 4, border_color, font_small, center=True)
        pygame.draw.line(surf, border_color, (x + 10, y + 20), (x + w - 10, y + 20))
