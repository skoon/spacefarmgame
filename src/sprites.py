import pygame
import random
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

def get_animal_surf(animal_type):
    key = f"animal_{animal_type}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    s = make_surface(32, 32)
    if animal_type == "zap_chicken":
        draw_box(s, 8, 16, 16, 12, (255, 220, 100), True)
        draw_box(s, 9, 15, 14, 10, (255, 235, 140), True)
        draw_box(s, 10, 14, 12, 8, (255, 245, 180), True)
        set_pixel(s, 12, 12, (255, 200, 50))
        set_pixel(s, 13, 12, (255, 200, 50))
        set_pixel(s, 19, 12, (255, 200, 50))
        set_pixel(s, 20, 12, (255, 200, 50))
        draw_box(s, 11, 13, 10, 2, (255, 180, 60), True)
        set_pixel(s, 22, 14, (255, 150, 50))
        set_pixel(s, 23, 15, (255, 150, 50))
        for i in range(3):
            set_pixel(s, 5 + i * 2, 18 + i, (255, 220, 100))
            set_pixel(s, 26 - i * 2, 18 + i, (255, 220, 100))
        set_pixel(s, 14, 14, (80, 60, 40))
        set_pixel(s, 17, 14, (80, 60, 40))
        for sp in range(4):
            sx = random.randint(6, 25)
            sy = random.randint(10, 18)
            set_pixel(s, sx, sy, (255, 255, 150))
    elif animal_type == "moo_droid":
        draw_box(s, 6, 14, 20, 14, (100, 200, 255), True)
        draw_box(s, 7, 13, 18, 12, (130, 215, 255), True)
        draw_box(s, 8, 12, 16, 10, (160, 230, 255), True)
        draw_box(s, 6, 16, 20, 3, (80, 180, 230), True)
        draw_box(s, 10, 10, 4, 4, (80, 180, 255), True)
        draw_box(s, 18, 10, 4, 4, (80, 180, 255), True)
        set_pixel(s, 12, 12, (60, 60, 80))
        set_pixel(s, 13, 12, (60, 60, 80))
        set_pixel(s, 20, 12, (60, 60, 80))
        set_pixel(s, 21, 12, (60, 60, 80))
        set_pixel(s, 16, 11, (60, 60, 80))
        set_pixel(s, 6, 22, (80, 160, 200))
        set_pixel(s, 7, 23, (80, 160, 200))
        set_pixel(s, 25, 22, (80, 160, 200))
        set_pixel(s, 24, 23, (80, 160, 200))
        for i in range(3):
            set_pixel(s, 10 + i, 26, (150, 200, 230))
            set_pixel(s, 19 + i, 26, (150, 200, 230))
        set_pixel(s, 9, 27, (60, 60, 60))
        set_pixel(s, 22, 27, (60, 60, 60))
        set_pixel(s, 14, 26, (200, 150, 80))
        set_pixel(s, 15, 26, (200, 150, 80))
    elif animal_type == "fluffalo":
        draw_box(s, 4, 10, 24, 18, (255, 180, 255), True)
        draw_box(s, 5, 9, 22, 16, (255, 200, 255), True)
        draw_box(s, 6, 8, 20, 14, (255, 220, 255), True)
        for fx in range(5, 27, 4):
            for fy in range(8, 24, 3):
                set_pixel(s, fx + random.randint(0, 2), fy, (255, 235, 255))
        draw_box(s, 9, 10, 4, 4, (255, 200, 220), True)
        draw_box(s, 19, 10, 4, 4, (255, 200, 220), True)
        set_pixel(s, 11, 12, (80, 60, 100))
        set_pixel(s, 12, 12, (80, 60, 100))
        set_pixel(s, 21, 12, (80, 60, 100))
        set_pixel(s, 22, 12, (80, 60, 100))
        set_pixel(s, 16, 9, (180, 120, 180))
        set_pixel(s, 16, 10, (180, 120, 180))
        for i in range(4):
            set_pixel(s, 6 + i, 6, (255, 200, 255))
            set_pixel(s, 22 + i, 6, (255, 200, 255))
        for i in range(3):
            set_pixel(s, 8 + i * 6, 26, (220, 160, 220))
            set_pixel(s, 9 + i * 6, 27, (220, 160, 220))
            set_pixel(s, 10 + i * 6, 28, (220, 160, 220))
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

def get_fish_surf(fish_id):
    key = f"fish_{fish_id}"
    if key in SPRITE_CACHE:
        return SPRITE_CACHE[key]
    from src.constants import FISH_TYPES
    c = FISH_TYPES[fish_id]["color"]
    dark = (c[0] // 2, c[1] // 2, c[2] // 2)
    s = make_surface(TILE_SIZE, TILE_SIZE)
    # body (oval-ish)
    draw_box(s, 8, 12, 14, 8, c, True)
    draw_box(s, 6, 14, 2, 4, c, True)
    draw_box(s, 22, 13, 2, 6, c, True)
    # belly shading
    draw_box(s, 9, 17, 12, 2, dark, True)
    # tail fin
    draw_box(s, 24, 11, 4, 4, c, True)
    draw_box(s, 24, 17, 4, 4, c, True)
    set_pixel(s, 27, 15, dark)
    set_pixel(s, 27, 16, dark)
    # top fin
    draw_box(s, 12, 9, 6, 3, dark, True)
    # eye
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
