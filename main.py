import pygame
import sys
import random
from src.constants import *
from src.sprites import *
from src.game import *

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Farm Galaxy")
clock = pygame.time.Clock()
font_small = pygame.font.SysFont("monospace", 14)
font_med = pygame.font.SysFont("monospace", 18)
font_large = pygame.font.SysFont("monospace", 24)

game = GameState()
if game.load_game():
    pass
else:
    game.player.add_item("Glowroot Seeds", 8)
    game.player.add_item("Berry Seeds", 5)
    game.player.add_item("Cosmic Wheat Seeds", 5)
    game.player.add_item("Zargon Seeds", 3)
    game.player.add_item("Nebula Seeds", 2)
    game.player.gold = 500
    game.set_message("Welcome to Space Farm Galaxy! Press WASD to move, E to interact, Space to use tools.")

def draw_text(surf, text, x, y, color=WHITE, font=font_small, center=False):
    img = font.render(text, True, color)
    if center:
        x -= img.get_width() // 2
        y -= img.get_height() // 2
    surf.blit(img, (x, y))

def draw_toolbar():
    bar_y = SCREEN_HEIGHT - 36
    pygame.draw.rect(screen, (0, 0, 0, 180), (0, bar_y, SCREEN_WIDTH, 36))
    pygame.draw.rect(screen, (60, 60, 80), (0, bar_y, SCREEN_WIDTH, 36), 1)
    tools = ["Hoe", "Water", "Scythe"]
    for i, t in enumerate(tools):
        x = 10 + i * 110
        color = GOLD if i == game.player.selected_tool else WHITE
        bg = (40, 40, 60) if i == game.player.selected_tool else (20, 20, 40)
        pygame.draw.rect(screen, bg, (x, bar_y + 4, 100, 28))
        pygame.draw.rect(screen, (80, 80, 100), (x, bar_y + 4, 100, 28), 1)
        icon = get_item_icon(t)
        screen.blit(icon, (x + 4, bar_y + 10))
        draw_text(screen, f"{i+1}: {t}", x + 24, bar_y + 12, color)

def draw_hud():
    pygame.draw.rect(screen, (0, 0, 0, 160), (0, 0, SCREEN_WIDTH, 28))
    day_str = f"Day {game.day} - {TIME_NAMES[game.time_slot]}"
    draw_text(screen, day_str, 10, 6, WHITE, font_small)
    draw_text(screen, f"Gold: {game.player.gold}g", 200, 6, GOLD, font_small)
    energy_pct = game.player.energy / max(game.player.max_energy, 1)
    ecolor = ENERGY_GREEN if energy_pct > 0.3 else (255, 200, 0) if energy_pct > 0.1 else RED
    pygame.draw.rect(screen, (40, 40, 40), (370, 8, 104, 12))
    pygame.draw.rect(screen, ecolor, (372, 10, int(100 * energy_pct), 8))
    draw_text(screen, f"Energy: {game.player.energy}", 480, 6, ecolor, font_small)
    tool_names = ["Hoe", "Water", "Scythe"]
    draw_text(screen, f"Tool: {tool_names[game.player.selected_tool]}", 650, 6, WHITE, font_small)
    draw_text(screen, f"Map: {game.player.current_map.upper()}", 800, 6, CYAN, font_small)
    if game.gift_mode:
        draw_text(screen, "GIFT MODE", 750, 24, PINK, font_small)

def draw_message():
    if game.message_timer > 0:
        alpha = min(255, game.message_timer * 4)
        color = (255, 255, 200)
        lines = game.message.split("\n")
        total_h = len(lines) * 20 + 10
        bg = pygame.Surface((SCREEN_WIDTH, total_h))
        bg.set_alpha(min(180, alpha))
        bg.fill((0, 0, 30))
        screen.blit(bg, (0, SCREEN_HEIGHT // 2 - total_h // 2))
        for i, line in enumerate(lines):
            draw_text(screen, line, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - total_h // 2 + 10 + i * 20, color, font_med, center=True)
        game.message_timer -= 1

def draw_dialogue():
    if not game.dialogue_active:
        return
    npc = game.dialogue_npc
    if not npc:
        return
    box_h = 120
    box_y = SCREEN_HEIGHT - box_h - 10
    bg = pygame.Surface((SCREEN_WIDTH - 40, box_h))
    bg.fill((10, 10, 30))
    bg.set_alpha(230)
    screen.blit(bg, (20, box_y))
    pygame.draw.rect(screen, (80, 80, 120), (20, box_y, SCREEN_WIDTH - 40, box_h), 2)
    heart_surf = get_heart_surf(True)
    for h in range(npc.heart_level):
        screen.blit(heart_surf, (30 + h * 14, box_y + 8))
    draw_text(screen, f"{npc.name} the {npc.species}", 30, box_y + 24, WHITE, font_med)
    draw_text(screen, f'"{npc.bio}"', 30, box_y + 44, LIGHT_GRAY, font_small)
    if game.dialogue_index < len(game.dialogue_lines):
        line = game.dialogue_lines[game.dialogue_index]
        draw_text(screen, line, 30, box_y + 66, (220, 220, 255), font_small)
    draw_text(screen, "Press E to continue", SCREEN_WIDTH // 2, box_y + box_h - 24, LIGHT_GRAY, font_small, center=True)

    if npc.romanceable:
        if game.married_to == npc.id:
            draw_text(screen, "♥ Married ♥", SCREEN_WIDTH - 160, box_y + 8, PINK, font_small)
        else:
            draw_text(screen, f"Hearts: {npc.heart_level}/10", SCREEN_WIDTH - 160, box_y + 8, RED, font_small)

def draw_shop():
    if not game.shop_active:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    panel_w, panel_h = 700, 450
    px, py = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
    pygame.draw.rect(screen, (20, 10, 40), (px, py, panel_w, panel_h))
    pygame.draw.rect(screen, (100, 80, 150), (px, py, panel_w, panel_h), 3)
    draw_text(screen, "Zara's General Store", px + panel_w // 2, py + 20, GOLD, font_large, center=True)
    draw_text(screen, f"Your Gold: {game.player.gold}g", px + panel_w // 2, py + 48, GOLD, font_med, center=True)

    col_w = panel_w // 2
    draw_text(screen, "-- Buy Seeds --", px + col_w // 2, py + 75, CYAN, font_med, center=True)
    draw_text(screen, "-- Sell Crops --", px + col_w + col_w // 2, py + 75, ORANGE, font_med, center=True)

    for i, crop_key in enumerate(CROP_ORDER):
        data = CROP_TYPES[crop_key]
        yy = py + 100 + i * 28
        # Buy column
        icon = get_crop_icon(crop_key)
        screen.blit(icon, (px + 20, yy + 2))
        draw_text(screen, f"{data['seed_name']} - {data['seed_price']}g", px + 40, yy + 4, WHITE, font_small)
        draw_text(screen, f"[{i+1}]", px + col_w - 40, yy + 4, GOLD, font_small)

        # Sell column
        sell_price = data["sell_price"]
        count = game.player.inventory.get(crop_key, 0)
        sell_keys = ["Q", "W", "E", "R", "T", "Y"]
        screen.blit(icon, (px + col_w + 20, yy + 2))
        draw_text(screen, f"{data['name']} x{count} - {sell_price}g", px + col_w + 40, yy + 4, WHITE, font_small)
        draw_text(screen, f"[{sell_keys[i]}]", px + panel_w - 50, yy + 4, ORANGE, font_small)

    draw_text(screen, "ESC: Exit Shop", px + panel_w // 2, py + panel_h - 30, LIGHT_GRAY, font_med, center=True)

def draw_bot_shop():
    if not game.bot_shop_active:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    panel_w, panel_h = 550, 330
    px, py = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
    pygame.draw.rect(screen, (20, 20, 40), (px, py, panel_w, panel_h))
    pygame.draw.rect(screen, (80, 120, 180), (px, py, panel_w, panel_h), 3)
    draw_text(screen, "Bot Workshop", px + panel_w // 2, py + 15, CYAN, font_large, center=True)
    draw_text(screen, f"Gold: {game.player.gold}g", px + panel_w // 2, py + 42, GOLD, font_med, center=True)
    bot_keys = list(BOT_TYPES.keys())
    for i, bk in enumerate(bot_keys):
        bt = BOT_TYPES[bk]
        yy = py + 75 + i * 70
        pygame.draw.rect(screen, (30, 30, 50), (px + 20, yy, panel_w - 40, 60))
        icon = get_bot_surf(bk)
        screen.blit(icon, (px + 30, yy + 4))
        draw_text(screen, bt["name"], px + 70, yy + 6, WHITE, font_med)
        draw_text(screen, f"Range: {bt['range']} tiles | Upkeep: {bt['upkeep']}g/day", px + 70, yy + 28, LIGHT_GRAY, font_small)
        draw_text(screen, f"[{i+1}] {bt['cost']}g", px + panel_w - 80, yy + 14, GOLD, font_med)
    draw_text(screen, "1-3: Buy | ESC: Exit", px + panel_w // 2, py + panel_h - 25, LIGHT_GRAY, font_small, center=True)

def draw_hangar():
    if not game.hangar_active:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    panel_w, panel_h = 650, 480
    px, py = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
    pygame.draw.rect(screen, (10, 10, 40), (px, py, panel_w, panel_h))
    pygame.draw.rect(screen, (60, 120, 200), (px, py, panel_w, panel_h), 3)
    draw_text(screen, "Spaceship Hangar", px + panel_w // 2, py + 15, CYAN, font_large, center=True)
    tier = SHIP_TIERS[game.ship_tier]
    draw_text(screen, f"Ship: {tier['name']}", px + 20, py + 45, WHITE, font_med)
    draw_text(screen, f"Fuel: {game.fuel}/{tier['fuel_capacity']}", px + 20, py + 70, GOLD, font_small)
    draw_text(screen, f"Cargo: {sum(game.ship_cargo.values())}/{tier['cargo_capacity']} slots", px + 20, py + 90, LIGHT_GRAY, font_small)
    if game.ship_tier + 1 < len(SHIP_TIERS):
        next_tier = SHIP_TIERS[game.ship_tier + 1]
        draw_text(screen, f"[U] Upgrade to {next_tier['name']} ({next_tier['cost']}g)", px + 20, py + 115, GOLD, font_small)
    else:
        draw_text(screen, "MAX LEVEL", px + 20, py + 115, PINK, font_small)
    draw_text(screen, f"[R] Refuel (1g per unit, max 50)", px + 20, py + 135, GOLD, font_small)
    draw_text(screen, "--- Destinations ---", px + panel_w // 2, py + 165, CYAN, font_med, center=True)
    for i, planet in enumerate(PLANETS):
        yy = py + 190 + i * 45
        has_fuel = game.fuel >= planet["fuel_cost"]
        color = GREEN if has_fuel else RED
        pygame.draw.rect(screen, (20, 20, 50), (px + 20, yy, panel_w - 40, 38))
        draw_text(screen, f"[{i+1}] {planet['name']}", px + 35, yy + 4, color, font_med)
        draw_text(screen, planet["desc"], px + 35, yy + 22, LIGHT_GRAY, font_small)
        draw_text(screen, f"{planet['fuel_cost']} fuel", px + panel_w - 80, yy + 8, color, font_small)
    draw_text(screen, "ESC: Close", px + panel_w // 2, py + panel_h - 22, LIGHT_GRAY, font_small, center=True)

def draw_planet_explore():
    if not game.planet_explore_active or game.current_planet is None:
        return
    planet = PLANETS[game.current_planet]
    c = planet["color"]
    for y in range(SCREEN_HEIGHT):
        strip = (c[0] * (SCREEN_HEIGHT - y) // SCREEN_HEIGHT,
                 c[1] * (SCREEN_HEIGHT - y) // SCREEN_HEIGHT,
                 c[2] * (SCREEN_HEIGHT - y) // SCREEN_HEIGHT)
        pygame.draw.line(screen, strip, (0, y), (SCREEN_WIDTH, y))
    for _ in range(80):
        sx = random.randint(0, SCREEN_WIDTH)
        sy = random.randint(0, SCREEN_HEIGHT)
        screen.set_at((sx, sy), (255, 255, 255, random.randint(50, 200)))
    ground_y = SCREEN_HEIGHT - 100
    pygame.draw.rect(screen, (c[0] // 2, c[1] // 2, c[2] // 2), (0, ground_y, SCREEN_WIDTH, 100))
    for _ in range(20):
        gx = random.randint(0, SCREEN_WIDTH)
        h = random.randint(10, 40)
        gc = (c[0] // 3, c[1] // 3, c[2] // 3)
        pygame.draw.rect(screen, gc, (gx, ground_y - h, 4, h))
    overlay = pygame.Surface((SCREEN_WIDTH, 140))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    draw_text(screen, f"Exploring: {planet['name']}", SCREEN_WIDTH // 2, 10, WHITE, font_large, center=True)
    draw_text(screen, planet["desc"], SCREEN_WIDTH // 2, 36, LIGHT_GRAY, font_med, center=True)
    tier = SHIP_TIERS[game.ship_tier]
    draw_text(screen, f"Turns left: {game.planet_turns_left}  |  Cargo: {sum(game.ship_cargo.values())}/{tier['cargo_capacity']}", SCREEN_WIDTH // 2, 62, GOLD, font_small, center=True)
    draw_text(screen, "[SPACE] Scan  |  [E] Return to ship", SCREEN_WIDTH // 2, 84, WHITE, font_med, center=True)
    log_y = 110
    for msg in game.planet_log[-4:]:
        draw_text(screen, msg, SCREEN_WIDTH // 2, log_y, CYAN, font_small, center=True)
        log_y += 18

def draw_inventory():
    if not game.inventory_active:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    panel_w, panel_h = 500, 400
    px, py = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
    pygame.draw.rect(screen, (10, 20, 30), (px, py, panel_w, panel_h))
    pygame.draw.rect(screen, (80, 100, 140), (px, py, panel_w, panel_h), 3)
    draw_text(screen, "Inventory", px + panel_w // 2, py + 15, WHITE, font_large, center=True)
    y = py + 50
    for item, count in sorted(game.player.inventory.items()):
        draw_text(screen, f"{item}: x{count}", px + 30, y, WHITE, font_small)
        icon = get_item_icon(item)
        screen.blit(icon, (px + 10, y))
        y += 24
    if y == py + 50:
        draw_text(screen, "Empty inventory", px + panel_w // 2, py + 100, LIGHT_GRAY, font_med, center=True)
    draw_text(screen, "Press I to close", px + panel_w // 2, py + panel_h - 30, LIGHT_GRAY, font_small, center=True)

def draw_seed_select():
    if not game.seed_select_active:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    panel_w, panel_h = 400, 300
    px, py = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
    pygame.draw.rect(screen, (10, 20, 30), (px, py, panel_w, panel_h))
    pygame.draw.rect(screen, (60, 140, 60), (px, py, panel_w, panel_h), 3)
    draw_text(screen, "Select Seeds to Plant", px + panel_w // 2, py + 15, WHITE, font_large, center=True)
    idx = 0
    for crop_key in CROP_ORDER:
        seed_name = CROP_TYPES[crop_key]["seed_name"]
        if seed_name in game.player.inventory:
            yy = py + 55 + idx * 35
            hilight = (40, 80, 40) if idx == game.selected_seed_index else (20, 30, 40)
            pygame.draw.rect(screen, hilight, (px + 20, yy - 2, panel_w - 40, 30))
            icon = get_crop_icon(crop_key)
            screen.blit(icon, (px + 30, yy + 2))
            count = game.player.inventory[seed_name]
            draw_text(screen, f"{CROP_TYPES[crop_key]['name']} x{count}", px + 55, yy + 6, WHITE, font_small)
            draw_text(screen, f"({CROP_TYPES[crop_key]['desc']})", px + 55, yy + 18, LIGHT_GRAY, font_small, center=True)
            idx += 1
    draw_text(screen, "E: Select | Q: Cancel", px + panel_w // 2, py + panel_h - 25, LIGHT_GRAY, font_small, center=True)

def draw_relationship_bar():
    if game.player.current_map != "spaceport":
        return
    nearby = []
    px, py = game.player.x // TILE_SIZE, game.player.y // TILE_SIZE
    for npc in game.npcs:
        dx = abs(px - npc.tile_x)
        dy = abs(py - npc.tile_y)
        if dx <= 3 and dy <= 3:
            nearby.append(npc)
    if not nearby:
        return
    y = 32
    for npc in nearby:
        name = npc.name
        if game.married_to == npc.id:
            name += " ♥"
        draw_text(screen, name, 10, y, WHITE, font_small)
        heart_filled = get_heart_surf(True)
        heart_empty = get_heart_surf(False)
        for h in range(10):
            hx = 120 + h * 12
            if h < npc.heart_level:
                screen.blit(heart_filled, (hx, y))
            else:
                screen.blit(heart_empty, (hx, y))
        y += 14

def draw_particles():
    for p in game.particles:
        alpha = int(255 * p["life"] / max(p["max_life"], 1))
        size = p["size"]
        s = pygame.Surface((size, size))
        s.set_alpha(alpha)
        c = p["color"]
        s.fill(c)
        screen.blit(s, (int(p["x"]), int(p["y"])))

def draw_farm():
    bg = (20, 15, 40)
    screen.fill(bg)

    time_colors = [(80, 120, 200), (120, 160, 230), (160, 200, 255), (180, 160, 120),
                   (220, 140, 80), (200, 100, 60), (60, 40, 80), (15, 10, 40)]
    sky_color = time_colors[min(game.time_slot, len(time_colors) - 1)]
    screen.fill(sky_color)

    if game.time_slot >= 4:
        for sx, sy in game.stars:
            screen.set_at((sx, sy), WHITE)

    ground_y = 3 * TILE_SIZE
    for row in range(ground_y // TILE_SIZE, FARM_TILES_Y):
        for col in range(FARM_TILES_X):
            draw_x = col * TILE_SIZE
            draw_y = row * TILE_SIZE
            if 5 <= row < 5 + TILLABLE_ROWS and 2 <= col < 2 + TILLABLE_COLS:
                tile = game.tiles[row - 5][col - 2]
                if tile.soil_state == "watered":
                    screen.blit(get_tile_surf("watered"), (draw_x, draw_y))
                elif tile.soil_state == "tilled":
                    screen.blit(get_tile_surf("tilled"), (draw_x, draw_y))
                else:
                    screen.blit(get_tile_surf("untilled"), (draw_x, draw_y))
                if tile.crop:
                    data = CROP_TYPES.get(tile.crop_type)
                    if data:
                        stages = data["growth_stages"]
                        cs = get_crop_surf(tile.crop_type, tile.crop_stage, stages)
                        screen.blit(cs, (draw_x, draw_y))
                        if tile.watered:
                            wd = make_surface(TILE_SIZE, TILE_SIZE)
                            for _ in range(3):
                                wx, wy = random.randint(0, TILE_SIZE - 1), random.randint(0, TILE_SIZE - 1)
                                set_pixel(wd, wx, wy, (150, 200, 255, 100))
                            screen.blit(wd, (draw_x, draw_y))
            elif row == 5 and (col < 2 or col >= 2 + TILLABLE_COLS):
                screen.blit(get_tile_surf("grass"), (draw_x, draw_y))
            elif row >= 5 + TILLABLE_ROWS:
                screen.blit(get_tile_surf("grass"), (draw_x, draw_y))
            elif row < 5:
                screen.blit(get_tile_surf("grass"), (draw_x, draw_y))

    player_house = get_building_surf("player_house")
    screen.blit(player_house, (7 * TILE_SIZE, 0))

    draw_text(screen, "Your Farm", 7 * TILE_SIZE + TILE_SIZE, -2, WHITE, font_small)

    path_exit_tx, path_exit_ty = 2 + TILLABLE_COLS + 1, 5 + TILLABLE_ROWS + 1
    ex, ey = (2 + TILLABLE_COLS + 1) * TILE_SIZE, (5 + TILLABLE_ROWS + 1) * TILE_SIZE
    screen.blit(get_tile_surf("path"), (ex, ey))
    draw_text(screen, "SPACE PORT ->", ex + TILE_SIZE // 2, ey + TILE_SIZE // 2 - 8, CYAN, font_small, center=True)

    # Farm bots
    for bot in game.bots:
        bx = (bot.array_x + FARM_TILES_OFFSET_X) * TILE_SIZE
        by = (bot.array_y + FARM_TILES_OFFSET_Y) * TILE_SIZE
        bot_surf = get_bot_surf(bot.bot_type)
        if not bot.active:
            dim = pygame.Surface((TILE_SIZE, TILE_SIZE))
            dim.set_alpha(140)
            dim.fill((60, 60, 60))
            bot_surf = bot_surf.copy()
            bot_surf.blit(dim, (0, 0))
        screen.blit(bot_surf, (bx, by))
        label_color = LIGHT_GRAY if not bot.active else WHITE
        label = BOT_TYPES[bot.bot_type]["name"]
        if not bot.active:
            label += " (off)"
        draw_text(screen, label, bx + TILE_SIZE // 2, by - 8, label_color, font_small, center=True)

    # Placement ghost
    if game.placement_mode and game.player.current_map == "farm":
        px = game.player.x // TILE_SIZE
        py = game.player.y // TILE_SIZE
        ax = px - FARM_TILES_OFFSET_X
        ay = py - FARM_TILES_OFFSET_Y
        if 0 <= ax < TILLABLE_COLS and 0 <= ay < TILLABLE_ROWS:
            ghost = pygame.Surface((TILE_SIZE, TILE_SIZE))
            ghost.set_alpha(100)
            ghost.fill((0, 255, 0))
            screen.blit(ghost, (px * TILE_SIZE, py * TILE_SIZE))

    # Draw player
    player_surf = get_astronaut_surf(game.player.direction)
    screen.blit(player_surf, (game.player.x, game.player.y))

    # Tree decorations
    tree_positions = [(1, 4), (1, 7), (1, 10), (0, 15),
                      (2 + TILLABLE_COLS + 2, 3), (2 + TILLABLE_COLS + 2, 8)]
    for tx, ty in tree_positions:
        if tx < FARM_TILES_X and ty < FARM_TILES_Y:
            t_surf = make_surface(TILE_SIZE, TILE_SIZE * 2)
            draw_box(t_surf, 11, 20, 4, 12, (90, 60, 30), True)
            draw_box(t_surf, 12, 18, 2, 4, (90, 60, 30), True)
            for r in range(2, 9):
                for c in range(0, 12):
                    px = c * 3 + random.randint(0, 2)
                    py = r * 3 + random.randint(0, 2)
                    shade = random.randint(0, 3)
                    if shade == 0:
                        leaf_color = (50, 160, 60)
                    elif shade == 1:
                        leaf_color = (40, 140, 50)
                    elif shade == 2:
                        leaf_color = (70, 190, 80)
                    else:
                        leaf_color = (90, 210, 90)
                    set_pixel(t_surf, px, py, leaf_color)
            outline_color = (30, 100, 40)
            for r in range(2, 9):
                set_pixel(t_surf, 0, r * 3, outline_color)
                set_pixel(t_surf, 33, r * 3, outline_color)
            for c in range(0, 12):
                set_pixel(t_surf, c * 3, 6, outline_color)
                set_pixel(t_surf, c * 3, 24, outline_color)
            screen.blit(t_surf, (tx * TILE_SIZE, ty * TILE_SIZE - TILE_SIZE))

def draw_spaceport():
    time_colors = [(80, 120, 200), (120, 160, 230), (160, 200, 255), (180, 160, 120),
                   (220, 140, 80), (200, 100, 60), (60, 40, 80), (15, 10, 40)]
    sky_color = time_colors[min(game.time_slot, len(time_colors) - 1)]
    screen.fill(sky_color)

    if game.time_slot >= 4:
        for sx, sy in game.stars:
            screen.set_at((sx, sy), WHITE)

    for row in range(SPACEPORT_TILES_Y):
        for col in range(SPACEPORT_TILES_X):
            draw_x = col * TILE_SIZE
            draw_y = row * TILE_SIZE
            screen.blit(get_tile_surf("grass"), (draw_x, draw_y))

    # Landing pad
    for dx in range(6):
        for dy in range(4):
            pad_x = (12 + dx) * TILE_SIZE
            pad_y = (16 + dy) * TILE_SIZE
            c = (100 + dx * 10, 100 + dx * 10, 110 + dy * 10)
            s = make_surface(TILE_SIZE, TILE_SIZE, c)
            screen.blit(s, (pad_x, pad_y))
    draw_text(screen, "★ LANDING PAD ★", 15 * TILE_SIZE, 17 * TILE_SIZE, CYAN, font_small, center=True)

    # Paths
    for px in range(8, 22):
        screen.blit(get_tile_surf("path"), (px * TILE_SIZE, 12 * TILE_SIZE))
    for py in range(8, 13):
        screen.blit(get_tile_surf("path"), (8 * TILE_SIZE, py * TILE_SIZE))
        screen.blit(get_tile_surf("path"), (21 * TILE_SIZE, py * TILE_SIZE))

    # Buildings
    shop_b = get_building_surf("shop")
    screen.blit(shop_b, (8 * TILE_SIZE, 2 * TILE_SIZE))
    draw_text(screen, "General Store", 11 * TILE_SIZE, 1 * TILE_SIZE, GOLD, font_small, center=True)

    bar_b = get_building_surf("bar")
    screen.blit(bar_b, (15 * TILE_SIZE, 2 * TILE_SIZE))
    draw_text(screen, "Cosmic Comet Bar", 18 * TILE_SIZE, 1 * TILE_SIZE, PINK, font_small, center=True)

    house_positions = [(5, 14), (12, 14), (19, 14), (25, 14)]
    house_labels = ["Nova's Home", "Pip's Home", "Luna's Home", "Rex's Home"]
    for i, (hx, hy) in enumerate(house_positions):
        hb = get_building_surf("house")
        screen.blit(hb, (hx * TILE_SIZE, hy * TILE_SIZE))
        draw_text(screen, house_labels[i], (hx + 1) * TILE_SIZE, (hy - 1) * TILE_SIZE, WHITE, font_small, center=True)
        # Door
        door_x = (hx + 1) * TILE_SIZE - 4
        door_y = (hy + 2) * TILE_SIZE - 8
        door_surf = make_surface(8, 12)
        draw_box(door_surf, 0, 0, 8, 12, (100, 80, 60), True)
        draw_box(door_surf, 2, 0, 4, 12, (80, 60, 40), True)
        screen.blit(door_surf, (door_x, door_y))

    # NPC Sprites
    for npc in game.npcs:
        ns = get_npc_surf(npc.id, npc.color, npc.color2)
        nx = npc.tile_x * TILE_SIZE
        ny = npc.tile_y * TILE_SIZE - TILE_SIZE
        screen.blit(ns, (nx, ny))
        draw_text(screen, npc.name, nx + TILE_SIZE // 2, ny - 8, WHITE, font_small, center=True)

    # Alien decorations
    for ax, ay in [(3, 10), (10, 16), (23, 3), (28, 8), (2, 18)]:
        if ax < SPACEPORT_TILES_X and ay < SPACEPORT_TILES_Y:
            deco = make_surface(TILE_SIZE, TILE_SIZE)
            for _ in range(8):
                dx, dy = random.randint(0, TILE_SIZE - 1), random.randint(0, TILE_SIZE - 1)
                set_pixel(deco, dx, dy, (180, 100, 255))
            screen.blit(deco, (ax * TILE_SIZE, ay * TILE_SIZE))

    # Exit sign
    ex, ey = 28 * TILE_SIZE, 19 * TILE_SIZE
    screen.blit(get_tile_surf("path"), (ex, ey))
    draw_text(screen, "-> FARM", ex + TILE_SIZE // 2, ey + TILE_SIZE // 2 - 8, CYAN, font_small, center=True)

    # Player
    player_surf = get_astronaut_surf(game.player.direction)
    screen.blit(player_surf, (game.player.x, game.player.y))

def draw_help():
    if not game.help_active:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    lines = [
        "=== HELP ===",
        "",
        "WASD / Arrows    Move",
        "SPACE            Use selected tool / Scan planet",
        "E                Interact / Place bot / Return from planet",
        "1-3              Select tool (Hoe/Water/Scythe)",
        "4                Plant seeds",
        "H (spaceport)    Spaceship hangar",
        "B (spaceport)    Bot workshop",
        "G (spaceport)    Gift mode (E to give to NPC)",
        "U / R (hangar)   Upgrade ship / Refuel",
        "I                Toggle inventory",
        "M                Toggle map (farm/spaceport)",
        "S                Save game",
        "?                Toggle this help",
        "ESC              Quit game",
    ]
    y_start = SCREEN_HEIGHT // 2 - len(lines) * 12
    for i, line in enumerate(lines):
        color = GOLD if i == 0 else WHITE
        draw_text(screen, line, SCREEN_WIDTH // 2, y_start + i * 22, color, font_med, center=True)

def draw_sleep_prompt():
    if not game.sleep_prompt:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    draw_text(screen, "Go to sleep for the night?", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30, WHITE, font_large, center=True)
    draw_text(screen, "Press Y to sleep | N to stay up", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10, LIGHT_GRAY, font_med, center=True)

def show_title_card():
    screen.fill((10, 5, 30))
    draw_text(screen, "SPACE FARM GALAXY", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60, CYAN, font_large, center=True)
    draw_text(screen, "Grow alien crops. Explore the stars.", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20, WHITE, font_med, center=True)
    draw_text(screen, "Find love among the cosmos.", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10, PINK, font_med, center=True)
    draw_text(screen, "Press ENTER to start", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60, GOLD, font_med, center=True)
    draw_text(screen, "Controls: WASD=Move E=Interact Space=UseTool 1-3=Tools", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100, LIGHT_GRAY, font_small, center=True)
    draw_text(screen, "M=Map I=Inventory Q=Back B=Sleep at house", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120, LIGHT_GRAY, font_small, center=True)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.running = False
            return
        if event.type == pygame.KEYDOWN:
            if event.unicode == '?':
                game.help_active = not game.help_active
                continue
            if game.seed_select_active:
                available = [c for c in CROP_ORDER if CROP_TYPES[c]["seed_name"] in game.player.inventory]
                if event.key == pygame.K_q:
                    game.seed_select_active = False
                elif event.key == pygame.K_e and available:
                    if game.selected_seed_index < len(available):
                        game.plant_seed(available[game.selected_seed_index])
                    game.seed_select_active = False
                elif event.key == pygame.K_UP:
                    game.selected_seed_index = max(0, game.selected_seed_index - 1)
                elif event.key == pygame.K_DOWN:
                    max_i = len(available) - 1
                    game.selected_seed_index = min(max_i, game.selected_seed_index + 1)
                continue

            if game.shop_active:
                if event.key == pygame.K_ESCAPE:
                    game.shop_active = False
                    game.subscreen = None
                sell_keys = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r, pygame.K_t, pygame.K_y]
                for i, crop_key in enumerate(CROP_ORDER):
                    if event.key == getattr(pygame, f"K_{i+1}"):
                        game.buy_item(crop_key)
                    if i < len(sell_keys) and event.key == sell_keys[i]:
                        game.sell_item(crop_key)
                continue

            if game.bot_shop_active:
                if event.key == pygame.K_ESCAPE:
                    game.bot_shop_active = False
                bot_keys = list(BOT_TYPES.keys())
                for i, bk in enumerate(bot_keys):
                    if event.key == getattr(pygame, f"K_{i+1}"):
                        game.buy_bot(bk)
                continue

            if game.hangar_active:
                if event.key == pygame.K_ESCAPE:
                    game.hangar_active = False
                elif event.key == pygame.K_u:
                    game.upgrade_ship()
                elif event.key == pygame.K_r:
                    game.refuel_ship()
                for i in range(len(PLANETS)):
                    if event.key == getattr(pygame, f"K_{i+1}"):
                        game.launch_to_planet(i)
                continue

            if game.planet_explore_active:
                if event.key == pygame.K_SPACE:
                    game.scan_planet()
                elif event.key == pygame.K_e:
                    game.return_from_planet()
                continue

            if game.inventory_active:
                if event.key == pygame.K_i:
                    game.inventory_active = False
                continue

            if game.dialogue_active:
                if event.key == pygame.K_e:
                    if game.dialogue_npc and game.married_to is None:
                        last_line = game.dialogue_lines[-1] if game.dialogue_lines else ""
                        if "Propose?" in last_line:
                            if game.dialogue_index >= len(game.dialogue_lines) - 1:
                                game.propose_marriage(game.dialogue_npc.id)
                            else:
                                game.advance_dialogue()
                        else:
                            game.advance_dialogue()
                    else:
                        game.advance_dialogue()
                continue

            if game.sleep_prompt:
                if event.key == pygame.K_y:
                    game.advance_day()
                    game.sleep_prompt = False
                    game.player.x = game.player.farm_x
                    game.player.y = game.player.farm_y
                    game.player.current_map = "farm"
                    game.set_message("Good morning! A new day on the farm!")
                elif event.key == pygame.K_n:
                    game.sleep_prompt = False
                continue

            if game.placement_mode:
                if event.key == pygame.K_ESCAPE:
                    game.placement_mode = None
                    game.set_message("Bot placement cancelled.")
                    continue
                elif event.key == pygame.K_e:
                    game.place_bot()
                    continue

            if event.key == pygame.K_ESCAPE:
                game.running = False
            elif event.key == pygame.K_e:
                game.interact()
            elif event.key == pygame.K_SPACE:
                if game.player.selected_tool <= 2:
                    if game.player.energy > 0:
                        game.use_tool()
                    else:
                        game.set_message("Too exhausted! Sleep to recover energy.")
            elif event.key == pygame.K_4:
                game.select_seed_to_plant()
            elif event.key == pygame.K_1:
                game.player.selected_tool = 0
            elif event.key == pygame.K_2:
                game.player.selected_tool = 1
            elif event.key == pygame.K_3:
                game.player.selected_tool = 2
            elif event.key == pygame.K_i:
                game.inventory_active = not game.inventory_active
            elif event.key == pygame.K_m:
                if game.player.current_map == "farm":
                    game.player.current_map = "spaceport"
                    game.player.x = game.player.sp_x
                    game.player.y = game.player.sp_y
                    game.set_message("Arrived at the Space Port!")
                else:
                    game.player.current_map = "farm"
                    game.player.x = game.player.farm_x
                    game.player.y = game.player.farm_y
                    game.set_message("Back on the farm!")
            elif event.key == pygame.K_g:
                if game.player.current_map == "spaceport":
                    game.gift_mode = not game.gift_mode
                    if game.gift_mode:
                        game.set_message("Gift mode on! Walk near an NPC and press E to give an item.")
                    else:
                        game.set_message("Gift mode off.")
            elif event.key == pygame.K_h:
                if game.player.current_map == "spaceport":
                    game.hangar_active = True
            elif event.key == pygame.K_b:
                if game.player.current_map == "spaceport":
                    game.bot_shop_active = True
                elif game.player.current_map == "farm":
                    px = game.player.x // TILE_SIZE
                    py = game.player.y // TILE_SIZE
                    if 7 <= px <= 10 and 0 <= py <= 3:
                        game.sleep_prompt = True
            elif event.key == pygame.K_s:
                game.save_game()

    keys = pygame.key.get_pressed()
    if not game.dialogue_active and not game.shop_active and not game.bot_shop_active and not game.hangar_active and not game.planet_explore_active and not game.seed_select_active and not game.inventory_active and not game.sleep_prompt:
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
            game.player.direction = "up"
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1
            game.player.direction = "down"
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
            game.player.direction = "left"
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1
            game.player.direction = "right"

        if dx or dy:
            speed = game.player.speed
            margin = 4
            tile_size = TILE_SIZE
            player_rect = pygame.Rect(game.player.x, game.player.y, tile_size - 2, tile_size - 2)

            new_x = game.player.x + dx * speed
            new_y = game.player.y + dy * speed

            if game.player.current_map == "farm":
                new_x = max(margin, min(new_x, FARM_TILES_X * tile_size - tile_size - margin))
                new_y = max(margin, min(new_y, FARM_TILES_Y * tile_size - tile_size - margin))
            else:
                new_x = max(margin, min(new_x, SPACEPORT_TILES_X * tile_size - tile_size - margin))
                new_y = max(margin, min(new_y, SPACEPORT_TILES_Y * tile_size - tile_size - margin))

            solid_rects = game.get_solid_rects()
            test_rect = pygame.Rect(new_x, game.player.y, tile_size - 2, tile_size - 2)
            if test_rect.collidelist(solid_rects) == -1:
                game.player.x = new_x
            test_rect = pygame.Rect(game.player.x, new_y, tile_size - 2, tile_size - 2)
            if test_rect.collidelist(solid_rects) == -1:
                game.player.y = new_y

            if game.player.current_map == "farm":
                game.player.farm_x = game.player.x
                game.player.farm_y = game.player.y
                px_t = game.player.x // TILE_SIZE
                py_t = game.player.y // TILE_SIZE
                if py_t >= 5 + TILLABLE_ROWS + 1 and px_t >= 2 + TILLABLE_COLS:
                    game.player.current_map = "spaceport"
                    game.player.x = 2 * TILE_SIZE
                    game.player.y = 16 * TILE_SIZE
                    game.player.sp_x = game.player.x
                    game.player.sp_y = game.player.y
                    game.set_message("Welcome to the Space Port!")
            else:
                game.player.sp_x = game.player.x
                game.player.sp_y = game.player.y
                px_t = game.player.x // TILE_SIZE
                py_t = game.player.y // TILE_SIZE
                if px_t >= 28 and py_t >= 18:
                    game.player.current_map = "farm"
                    game.player.x = (2 + TILLABLE_COLS + 1) * TILE_SIZE
                    game.player.y = (5 + TILLABLE_ROWS) * TILE_SIZE
                    game.player.farm_x = game.player.x
                    game.player.farm_y = game.player.y
                    game.set_message("Back on the farm!")

def render():
    if game.player.current_map == "farm":
        draw_farm()
    else:
        draw_spaceport()

    draw_hud()
    draw_toolbar()
    draw_relationship_bar()
    draw_message()
    draw_particles()

    if game.dialogue_active:
        draw_dialogue()
    if game.shop_active:
        draw_shop()
    if game.hangar_active:
        draw_hangar()
    if game.bot_shop_active:
        draw_bot_shop()
    if game.planet_explore_active:
        draw_planet_explore()
    if game.inventory_active:
        draw_inventory()
    if game.seed_select_active:
        draw_seed_select()
    if game.sleep_prompt:
        draw_sleep_prompt()
    if game.help_active:
        draw_help()

def main():
    show_title_card()
    game.set_message("Welcome to Space Farm Galaxy! Press G at the port to give gifts to NPCs!")

    while game.running:
        handle_events()
        game.update_particles()

        if game.message_timer > 0:
            game.message_timer -= 1

        render()
        pygame.display.flip()
        clock.tick(FPS)

    game.save_game()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
