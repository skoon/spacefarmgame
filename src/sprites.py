import pygame
from src.constants import *

SPRITE_CACHE = {}

def make_surface(w, h, color=None):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    if color:
        s.fill(color)
    return s

def set_pixel(surf, x, y, color):
    if 0 <= x < surf.get_width() and 0 <= y < surf.get_height():
        surf.set_at((x, y), color)

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
    s = make_surface(TILE_SIZE, TILE_SIZE * 2)
    # Simple alien body
    draw_box(s, 6, 24, 8, 8, (60, 60, 80), True)
    draw_box(s, 18, 24, 8, 8, (60, 60, 80), True)
    draw_box(s, 4, 10, 24, 16, color1, True)
    draw_box(s, 4, 22, 24, 3, color2, True)
    # Head
    draw_box(s, 6, 0, 20, 12, color1, True)
    # Eyes
    draw_box(s, 10, 3, 4, 4, WHITE, True)
    draw_box(s, 18, 3, 4, 4, WHITE, True)
    set_pixel(s, 12, 5, BLACK)
    set_pixel(s, 20, 5, BLACK)
    # Mouth
    draw_box(s, 13, 8, 6, 2, color2, True)
    # Antennae
    set_pixel(s, 8, 0, color2)
    set_pixel(s, 24, 0, color2)
    set_pixel(s, 9, 0, color2)
    set_pixel(s, 23, 0, color2)
    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

def get_tile_surf(tile_type, variant=0):
    key = f"tile_{tile_type}_{variant}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    s = make_surface(TILE_SIZE, TILE_SIZE)
    if tile_type == "grass":
        shades = [(50, 130, 50), (60, 140, 60), (70, 150, 70)]
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                c = shades[(x + y + variant) % 3]
                set_pixel(s, x, y, c)
        for _ in range(6):
            sx, sy = (variant * 7 + _ * 5) % TILE_SIZE, (_ * 11 + variant * 3) % TILE_SIZE
            set_pixel(s, sx, sy, (40, 180, 40))
    elif tile_type == "path":
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                c = (160 + (x + y) % 3 * 10, 150 + (x + y) % 3 * 10, 140 + (x + y) % 3 * 10)
                set_pixel(s, x, y, c)
    elif tile_type == "untilled":
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                shade = SOIL_BROWN
                if (x + y) % 4 == 0:
                    shade = (shade[0] - 10, shade[1] - 10, shade[2] - 10)
                if (x + y) % 5 == 0:
                    shade = (shade[0] + 10, shade[1] + 10, shade[2] + 5)
                set_pixel(s, x, y, shade)
    elif tile_type == "tilled":
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                shade = (DARK_BROWN[0] + (x % 4) * 5, DARK_BROWN[1] + (x % 4) * 3, DARK_BROWN[2] + (y % 3) * 3)
                set_pixel(s, x, y, shade)
        for row in range(4):
            yy = 4 + row * 7
            for x in range(TILE_SIZE):
                set_pixel(s, x, yy, (80, 50, 20))
    elif tile_type == "watered":
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                blend = 0.7 + 0.3 * ((x + y) % 4) / 4.0
                r = int(DARK_BROWN[0] * (1 - blend) + WATER_BLUE[0] * blend)
                g = int(DARK_BROWN[1] * (1 - blend) + WATER_BLUE[1] * blend)
                b = int(DARK_BROWN[2] * (1 - blend) + WATER_BLUE[2] * blend)
                set_pixel(s, x, y, (r, g, b))
        for row in range(4):
            yy = 4 + row * 7
            for x in range(TILE_SIZE):
                set_pixel(s, x, yy, (50, 80, 140))
    SPRITE_CACHE[key] = s
    return s

def get_crop_surf(crop_key, stage, total_stages):
    key = f"crop_{crop_key}_{stage}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    data = CROP_TYPES[crop_key]
    color = data["color"]
    s = make_surface(TILE_SIZE, TILE_SIZE)
    progress = stage / max(total_stages - 1, 1)
    center_x, base_y = TILE_SIZE // 2, TILE_SIZE - 4
    if stage == 0:
        draw_box(s, center_x - 1, base_y - 2, 3, 3, (40, 180, 40), True)
    elif stage == 1:
        h = int(6 + progress * 10)
        for i in range(3):
            ox = center_x - 3 + i * 3
            draw_box(s, ox, base_y - h, 2, h, (50 + i * 20, 150 + int(progress * 50), 50), True)
    elif stage == 2 and progress >= 0.5:
        h = 14
        for i in range(3):
            ox = center_x - 4 + i * 4
            draw_box(s, ox, base_y - h, 3, h, color, True)
        draw_box(s, center_x - 3, base_y - h - 2, 6, 3, color, True)
    elif stage >= total_stages - 1 or progress >= 0.8:
        h = 16
        for i in range(3):
            ox = center_x - 4 + i * 4
            draw_box(s, ox, base_y - h, 3, h, (40, 180, 40), True)
        draw_box(s, center_x - 5, base_y - h - 4, 10, 6, color, True)
        set_pixel(s, center_x, base_y - h - 5, YELLOW)
        set_pixel(s, center_x - 3, base_y - h - 3, YELLOW)
        set_pixel(s, center_x + 3, base_y - h - 3, YELLOW)
        set_pixel(s, center_x - 1, base_y - h - 1, YELLOW)
    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

def get_building_surf(building_type):
    key = f"building_{building_type}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    w, h = TILE_SIZE * 3, TILE_SIZE * 3
    s = make_surface(w, h)
    if building_type == "player_house":
        draw_box(s, 0, 0, w, h, (160, 140, 120), True)
        draw_box(s, 4, 4, w - 8, h - 8, (180, 160, 140), True)
        draw_box(s, w // 2 - 8, h - 20, 16, 20, (100, 80, 60), True)
        draw_box(s, 8, 12, w - 16, h + 12, (140, 120, 100), False)
        for yy in range(8, h - 8, 12):
            for xx in range(8, w - 8, 12):
                set_pixel(s, xx, yy, (200, 180, 160))
    elif building_type == "shop":
        draw_box(s, 0, 0, w, h, (120, 80, 160), True)
        draw_box(s, 4, 4, w - 8, h - 8, (140, 100, 180), True)
        draw_box(s, w // 2 - 12, h - 20, 24, 20, (80, 50, 100), True)
        draw_box(s, 8, 8, w - 16, 16, (200, 180, 255), True)
    elif building_type == "bar":
        draw_box(s, 0, 0, w, h, (100, 60, 60), True)
        draw_box(s, 4, 4, w - 8, h - 8, (130, 80, 80), True)
        draw_box(s, w // 2 - 8, h - 20, 16, 20, (70, 40, 40), True)
        set_pixel(s, w // 2, 4, YELLOW)
        set_pixel(s, w // 2 - 4, 6, YELLOW)
        set_pixel(s, w // 2 + 4, 6, YELLOW)
        set_pixel(s, w // 2, 8, YELLOW)
    elif building_type == "house":
        draw_box(s, 0, 0, w, h, (140, 160, 180), True)
        draw_box(s, 4, 4, w - 8, h - 8, (160, 180, 200), True)
        draw_box(s, w // 2 - 8, h - 20, 16, 20, (100, 120, 140), True)
        draw_box(s, 8, 12, 8, 8, (180, 220, 255), True)
        draw_box(s, w - 16, 12, 8, 8, (180, 220, 255), True)
    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

def get_crop_icon(crop_key):
    key = f"icon_{crop_key}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    s = make_surface(16, 16)
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
    if "seed" in item_name.lower() or "seeds" in item_name.lower():
        draw_box(s, 4, 6, 8, 8, (200, 180, 100), True)
        set_pixel(s, 7, 8, (100, 200, 100))
        set_pixel(s, 9, 10, (100, 200, 100))
    elif "hoe" in item_name.lower():
        draw_box(s, 7, 2, 2, 12, (160, 140, 100), True)
        draw_box(s, 4, 10, 8, 4, (120, 120, 120), True)
    elif "water" in item_name.lower():
        draw_box(s, 6, 2, 4, 12, (100, 150, 200), True)
        draw_box(s, 4, 4, 8, 4, (120, 120, 120), True)
    elif "scythe" in item_name.lower():
        draw_box(s, 7, 2, 2, 12, (140, 120, 80), True)
        draw_box(s, 2, 2, 12, 3, (180, 180, 180), True)
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
    from src.constants import BOT_TYPES
    c = BOT_TYPES[bot_type]["color"]
    s = make_surface(TILE_SIZE, TILE_SIZE)
    draw_box(s, 6, 4, 20, 18, c, True)
    draw_box(s, 8, 6, 16, 14, (c[0]//2, c[1]//2, c[2]//2), True)
    set_pixel(s, 10, 4, WHITE)
    set_pixel(s, 22, 4, WHITE)
    set_pixel(s, 14, 8, c)
    set_pixel(s, 18, 8, c)
    draw_box(s, 10, 16, 12, 3, (c[0]//2, c[1]//2, c[2]//2), True)
    draw_box(s, 11, 18, 4, 6, (60, 60, 80), True)
    draw_box(s, 17, 18, 4, 6, (60, 60, 80), True)
    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s

def get_ship_surf(tier):
    key = f"ship_{tier}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    colors = [(160, 180, 200), (200, 180, 120), (220, 200, 255)]
    c = colors[min(tier, len(colors) - 1)]
    s = make_surface(TILE_SIZE, TILE_SIZE)
    draw_box(s, 4, 12, 24, 8, c, True)
    draw_box(s, 8, 8, 16, 6, (c[0]//2, c[1]//2, c[2]//2), True)
    draw_box(s, 10, 4, 12, 6, c, True)
    draw_box(s, 14, 0, 4, 6, (c[0]//2, c[1]//2, c[2]//2), True)
    set_pixel(s, 12, 14, GOLD)
    set_pixel(s, 20, 14, GOLD)
    s.set_colorkey(BLACK)
    SPRITE_CACHE[key] = s
    return s
