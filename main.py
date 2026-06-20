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
if game.load_game(0):
    game.save_menu_slot = 0
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
    season_name = SEASONS[game.season_index]
    draw_text(screen, f"{season_name} Season", 750, 26, SEASONAL_MODIFIERS[season_name]["sky_tint"], font_small)
    w_name = game.current_weather["name"]
    w_color = game.current_weather["color"] if game.current_weather["color"] else WHITE
    draw_text(screen, f"Weather: {w_name}", 750, 42, w_color, font_small)
    if game.festival_today and not game.festival_active:
        fest = FESTIVALS[game.festival_today]
        draw_text(screen, f"★ {fest['name']} Today! Visit the Landing Pad! ★", SCREEN_WIDTH // 2, 60, GOLD, font_small, center=True)
    if game.gift_mode:
        draw_text(screen, "GIFT MODE", 750, 60, PINK, font_small)

    shed_count = sum(1 for b in game.buildings if b["type"] == "storage_shed")
    if shed_count > 0:
        draw_text(screen, f"Storage Shed (+{shed_count * 24} slots)", 10, 80, CYAN, font_small)

    if game.player.current_map == "farm" and not any([game.dialogue_active, game.shop_active, game.bot_shop_active, game.hangar_active, game.inventory_active, game.seed_select_active, game.sleep_prompt, game.bar_active, game.festival_active, game.save_menu_active, game.cooking_active, game.expand_menu_active, game.building_shop_active, game.subscreen == "shipping_bin", game.build_mode is not None]):
        ftx, fty = game.player.get_facing_tile()
        tile = game.get_tile_at(ftx, fty)
        if tile and tile.crop:
            data = CROP_TYPES.get(tile.crop_type)
            if data:
                stages = data["growth_stages"]
                pct = int(tile.crop_timer / max(tile.crop_growth_time, 1) * 100)
                stage_str = f"Stage {tile.crop_stage + 1}/{stages}"
                water_str = " 💧" if tile.watered else " 💦 needs water"
                info = f"{data['name']} — {stage_str} ({pct}%){water_str}"
                draw_text(screen, info, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 48, WHITE, font_small, center=True)

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
    draw_text(screen, "-- Sell --", px + col_w + col_w // 2, py + 75, ORANGE, font_med, center=True)

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

    dish_y = py + 100 + len(CROP_ORDER) * 28 + 10
    draw_text(screen, "-- Dishes --", px + col_w + col_w // 2, dish_y, PINK, font_med, center=True)
    dish_keys = ["Z", "X", "C", "V", "B", "N", "M", "P"]
    di = 0
    for rk, recipe in RECIPES.items():
        name = recipe["name"]
        count = game.player.inventory.get(name, 0)
        if count <= 0:
            continue
        yy = dish_y + 20 + di * 22
        draw_text(screen, f"{name} x{count} - {recipe['sell_price']}g", px + col_w + 40, yy, WHITE, font_small)
        if di < len(dish_keys):
            draw_text(screen, f"[{dish_keys[di]}]", px + panel_w - 50, yy, ORANGE, font_small)
        di += 1

    draw_text(screen, "ESC: Exit Shop", px + panel_w // 2, py + panel_h - 30, LIGHT_GRAY, font_med, center=True)

def draw_bar():
    if not game.bar_active:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    panel_w, panel_h = 500, 350
    px, py = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
    pygame.draw.rect(screen, (30, 10, 40), (px, py, panel_w, panel_h))
    pygame.draw.rect(screen, (180, 80, 180), (px, py, panel_w, panel_h), 3)
    draw_text(screen, "~ Cosmic Comet Bar ~", px + panel_w // 2, py + 15, PINK, font_large, center=True)
    draw_text(screen, f"Gold: {game.player.gold}g  |  Energy: {game.player.energy}/{game.player.max_energy}", px + panel_w // 2, py + 42, GOLD, font_med, center=True)
    for i, item in enumerate(BAR_ITEMS):
        yy = py + 80 + i * 55
        pygame.draw.rect(screen, (40, 20, 50), (px + 20, yy, panel_w - 40, 45))
        pygame.draw.rect(screen, (100, 60, 120), (px + 20, yy, panel_w - 40, 45), 1)
        draw_text(screen, item["name"], px + 40, yy + 6, WHITE, font_med)
        draw_text(screen, f"+{item['energy']} Energy", px + 40, yy + 28, ENERGY_GREEN, font_small)
        draw_text(screen, f"{item['price']}g", px + panel_w - 80, yy + 10, GOLD, font_med)
        draw_text(screen, f"[{i+1}]", px + panel_w - 120, yy + 10, GOLD, font_small)
    draw_text(screen, "1-4: Buy | ESC: Exit", px + panel_w // 2, py + panel_h - 25, LIGHT_GRAY, font_small, center=True)

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
    overlay.set_alpha(180)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    panel_w, panel_h = 440, 420
    px, py = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
    pygame.draw.rect(screen, (10, 20, 30), (px, py, panel_w, panel_h))
    pygame.draw.rect(screen, (60, 140, 60), (px, py, panel_w, panel_h), 3)
    draw_text(screen, "Select Seeds to Plant", px + panel_w // 2, py + 14, WHITE, font_large, center=True)
    draw_text(screen, f"Gold: {game.player.gold}g  |  Energy: {game.player.energy}/{game.player.max_energy}",
              px + panel_w // 2, py + 36, GOLD, font_small, center=True)

    idx = 0
    entry_h = 48
    for crop_key in CROP_ORDER:
        data = CROP_TYPES[crop_key]
        seed_name = data["seed_name"]
        if seed_name in game.player.inventory:
            yy = py + 56 + idx * entry_h
            selected = idx == game.selected_seed_index
            bg = (40, 80, 40) if selected else (18, 26, 36)
            border = (80, 200, 80) if selected else (40, 50, 60)
            pygame.draw.rect(screen, bg, (px + 20, yy, panel_w - 40, entry_h - 4))
            pygame.draw.rect(screen, border, (px + 20, yy, panel_w - 40, entry_h - 4), 1)

            icon = get_crop_icon(crop_key)
            screen.blit(icon, (px + 28, yy + 6))

            count = game.player.inventory[seed_name]
            draw_text(screen, f"{data['name']}  x{count}", px + 56, yy + 4, WHITE, font_small)
            draw_text(screen, data['desc'], px + 56, yy + 18, LIGHT_GRAY, font_small)

            growth = f"{data['growth_time']} days"
            if data.get("regrows"):
                growth += " (regrows)"
            sell_str = f"Sell: {data['sell_price']}g"
            growth_str = f"Growth: {growth}"
            draw_text(screen, f"{growth_str}  |  {sell_str}", px + 56, yy + 32, CYAN, font_small)

            idx += 1

    if idx == 0:
        draw_text(screen, "No seeds in inventory!", px + panel_w // 2, py + panel_h // 2, LIGHT_GRAY, font_med, center=True)
    else:
        draw_text(screen, "Arrow keys: Navigate  |  E: Plant  |  Q: Cancel",
                  px + panel_w // 2, py + panel_h - 22, LIGHT_GRAY, font_small, center=True)

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

def draw_crop_tasting():
    if not game.festival_active or game.festival_type != "crop_tasting":
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    panel_w, panel_h = 500, 350
    px, py = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
    pygame.draw.rect(screen, (40, 20, 10), (px, py, panel_w, panel_h))
    pygame.draw.rect(screen, (200, 150, 80), (px, py, panel_w, panel_h), 3)
    draw_text(screen, "★ Harvest Moon Feast ★", px + panel_w // 2, py + 15, GOLD, font_large, center=True)
    draw_text(screen, "Choose your best crop for the judges!", px + panel_w // 2, py + 45, WHITE, font_med, center=True)
    if "result" in game.festival_data:
        result = game.festival_data["result"]
        draw_text(screen, result, px + panel_w // 2, py + 120, GOLD if "won" in result.lower() else WHITE, font_large, center=True)
        draw_text(screen, "Press E to continue", px + panel_w // 2, py + panel_h - 30, LIGHT_GRAY, font_small, center=True)
        return
    crops = game.festival_data.get("crops", [])
    for i, crop_key in enumerate(crops):
        data = CROP_TYPES[crop_key]
        yy = py + 90 + i * 70
        pygame.draw.rect(screen, (60, 40, 20), (px + 30, yy, panel_w - 60, 55))
        pygame.draw.rect(screen, (120, 80, 40), (px + 30, yy, panel_w - 60, 55), 1)
        icon = get_crop_icon(crop_key)
        screen.blit(icon, (px + 45, yy + 8))
        draw_text(screen, data["name"], px + 75, yy + 8, WHITE, font_med)
        draw_text(screen, f"Sell price: {data['sell_price']}g", px + 75, yy + 30, LIGHT_GRAY, font_small)
        draw_text(screen, f"[{i+1}]", px + panel_w - 70, yy + 14, GOLD, font_med)
    draw_text(screen, "1-3: Select crop | ESC: Leave", px + panel_w // 2, py + panel_h - 25, LIGHT_GRAY, font_small, center=True)

def draw_flower_arrange():
    if not game.festival_active or game.festival_type != "flower_arrange":
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    panel_w, panel_h = 600, 450
    px, py = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
    pygame.draw.rect(screen, (20, 30, 20), (px, py, panel_w, panel_h))
    pygame.draw.rect(screen, (80, 180, 80), (px, py, panel_w, panel_h), 3)
    draw_text(screen, "★ Alien Flower Show ★", px + panel_w // 2, py + 12, GOLD, font_large, center=True)
    timer = game.festival_data.get("timer", 0) // 10
    draw_text(screen, f"Time: {timer}s", px + panel_w - 80, py + 16, RED if timer < 10 else WHITE, font_med)
    draw_text(screen, "Match the target pattern!", px + panel_w // 2, py + 38, WHITE, font_small, center=True)
    grid = game.festival_data.get("grid", [])
    target = game.festival_data.get("target", [])
    cursor = game.festival_data.get("cursor", [0, 0])
    cell_size = 40
    gap = 4
    start_x = px + 40
    start_y = py + 70
    for r in range(4):
        for c in range(4):
            cx = start_x + c * (cell_size + gap)
            cy = start_y + r * (cell_size + gap)
            if r < len(grid) and c < len(grid[r]):
                s = make_surface(cell_size, cell_size, grid[r][c])
                screen.blit(s, (cx, cy))
            draw_box(screen, cx, cy, cell_size, cell_size, (255, 255, 255), False)
            if cursor[0] == r and cursor[1] == c:
                draw_box(screen, cx - 1, cy - 1, cell_size + 2, cell_size + 2, GOLD, 2)
    target_x = px + 340
    target_y = py + 70
    draw_text(screen, "Target:", target_x, target_y - 16, CYAN, font_small)
    for r in range(4):
        for c in range(4):
            cx = target_x + c * (cell_size + gap)
            cy = target_y + r * (cell_size + gap)
            if r < len(target) and c < len(target[r]):
                s = make_surface(cell_size, cell_size, target[r][c])
                screen.blit(s, (cx, cy))
            draw_box(screen, cx, cy, cell_size, cell_size, (255, 255, 255), False)
    draw_text(screen, "Arrows: Move  SPACE: Swap  ENTER: Submit", px + panel_w // 2, py + panel_h - 25, LIGHT_GRAY, font_small, center=True)

def draw_rhythm():
    if not game.festival_active or game.festival_type != "rhythm":
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    panel_w, panel_h = 500, 350
    px, py = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
    pygame.draw.rect(screen, (20, 10, 40), (px, py, panel_w, panel_h))
    pygame.draw.rect(screen, (180, 100, 200), (px, py, panel_w, panel_h), 3)
    draw_text(screen, "★ Starlight Dance ★", px + panel_w // 2, py + 15, PINK, font_large, center=True)
    seq = game.festival_data.get("sequence", [])
    idx = game.festival_data.get("index", 0)
    misses = game.festival_data.get("misses", 0)
    total = len(seq)
    score = total - misses
    draw_text(screen, f"Step {min(idx+1, total)}/{total}  |  Score: {score}/{total}", px + panel_w // 2, py + 42, WHITE, font_med, center=True)
    arrow_names = {"UP": "↑", "DOWN": "↓", "LEFT": "←", "RIGHT": "→"}
    if "result" in game.festival_data:
        draw_text(screen, game.festival_data["result"], px + panel_w // 2, py + 120, GOLD, font_large, center=True)
        draw_text(screen, "Press E to continue", px + panel_w // 2, py + panel_h - 30, LIGHT_GRAY, font_small, center=True)
        return
    arrow_y = py + 100
    next_arrow = seq[idx] if idx < total else "?"
    draw_text(screen, "Press the arrow key:", px + panel_w // 2, arrow_y, WHITE, font_med, center=True)
    draw_text(screen, arrow_names.get(next_arrow, "?"), px + panel_w // 2, arrow_y + 40, GOLD, font_large, center=True)
    draw_text(screen, "Then SPACE to confirm", px + panel_w // 2, arrow_y + 80, LIGHT_GRAY, font_small, center=True)

def draw_festival():
    if not game.festival_active:
        return
    if game.festival_type == "crop_tasting":
        draw_crop_tasting()
    elif game.festival_type == "flower_arrange":
        draw_flower_arrange()
    elif game.festival_type == "rhythm":
        draw_rhythm()

def blend_colors(c1, c2, alpha):
    return (
        int(c1[0] * (1 - alpha) + c2[0] * alpha),
        int(c1[1] * (1 - alpha) + c2[1] * alpha),
        int(c1[2] * (1 - alpha) + c2[2] * alpha),
    )

def draw_weather_particles():
    for p in game.weather_particles:
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
    season_name = SEASONS[game.season_index]
    tint = SEASONAL_MODIFIERS[season_name]["sky_tint"]
    sky_color = blend_colors(sky_color, tint, 0.25)
    w_name = game.current_weather["name"]
    if w_name == "Void Fog":
        sky_color = blend_colors(sky_color, (60, 40, 80), 0.4)
    elif w_name == "Solar Flare":
        sky_color = blend_colors(sky_color, (255, 200, 100), 0.15)
    screen.fill(sky_color)

    if game.time_slot >= 4:
        for sx, sy in game.stars:
            screen.set_at((sx, sy), WHITE)

    ground_y = 3 * TILE_SIZE
    off_x = game.farm_off_x
    off_y = game.farm_off_y
    f_cols = game.farm_cols
    f_rows = game.farm_rows
    for row in range(ground_y // TILE_SIZE, FARM_TILES_Y):
        for col in range(FARM_TILES_X):
            draw_x = col * TILE_SIZE
            draw_y = row * TILE_SIZE
            if off_y <= row < off_y + f_rows and off_x <= col < off_x + f_cols:
                tile = game.tiles[row - off_y][col - off_x]
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
            elif row == off_y and (col < off_x or col >= off_x + f_cols):
                screen.blit(get_tile_surf("grass"), (draw_x, draw_y))
            elif row >= off_y + f_rows:
                screen.blit(get_tile_surf("grass"), (draw_x, draw_y))
            elif row < off_y:
                screen.blit(get_tile_surf("grass"), (draw_x, draw_y))

    player_house = get_building_surf("player_house")
    screen.blit(player_house, (7 * TILE_SIZE, 0))

    draw_text(screen, "Your Farm", 7 * TILE_SIZE + TILE_SIZE, -2, WHITE, font_small)

    # Signpost at southeast edge
    sign_x = (off_x + f_cols) * TILE_SIZE
    sign_y = (off_y + f_rows) * TILE_SIZE
    sign_post = make_surface(TILE_SIZE, TILE_SIZE)
    draw_box(sign_post, 14, 0, 4, 32, (90, 70, 50), True)
    draw_box(sign_post, 15, 0, 2, 32, (110, 85, 65), True)
    draw_box(sign_post, 4, 0, 24, 10, (70, 55, 40), True)
    draw_box(sign_post, 5, 0, 22, 8, (90, 70, 50), True)
    draw_box(sign_post, 6, 1, 20, 6, (110, 85, 65), True)
    draw_text(sign_post, "EXPAND", 16, 3, GOLD, font_small, center=True)
    screen.blit(sign_post, (sign_x, sign_y))

    # Path exit
    path_exit_x = off_x + f_cols + 1
    path_exit_y = off_y + f_rows + 1
    if path_exit_x < FARM_TILES_X and path_exit_y < FARM_TILES_Y:
        ex, ey = path_exit_x * TILE_SIZE, path_exit_y * TILE_SIZE
        screen.blit(get_tile_surf("path"), (ex, ey))
        draw_text(screen, "SPACE PORT ->", ex + TILE_SIZE // 2, ey + TILE_SIZE // 2 - 8, CYAN, font_small, center=True)

    # Farm bots
    for bot in game.bots:
        bx = (bot.array_x + off_x) * TILE_SIZE
        by = (bot.array_y + off_y) * TILE_SIZE
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

    # Buildings on farm
    for b in game.buildings:
        bt = BUILDING_TYPES[b["type"]]
        bs = get_building_surf(b["type"])
        bw, bh = bt["size"]
        screen.blit(bs, (b["tile_x"] * TILE_SIZE, b["tile_y"] * TILE_SIZE))
        draw_text(screen, bt["name"], b["tile_x"] * TILE_SIZE + bw * TILE_SIZE // 2,
                  b["tile_y"] * TILE_SIZE - 8, WHITE, font_small, center=True)

    # Facing tile highlight
    ftx, fty = game.player.get_facing_tile()
    if 0 <= ftx < FARM_TILES_X and 0 <= fty < FARM_TILES_Y:
        hl = pygame.Surface((TILE_SIZE, TILE_SIZE))
        hl.set_alpha(50)
        hl.fill((255, 255, 255))
        screen.blit(hl, (ftx * TILE_SIZE, fty * TILE_SIZE))

    # Placement ghost (bots)
    if game.placement_mode and game.player.current_map == "farm":
        px = game.player.x // TILE_SIZE
        py = game.player.y // TILE_SIZE
        ax = px - off_x
        ay = py - off_y
        if 0 <= ax < f_cols and 0 <= ay < f_rows:
            ghost = pygame.Surface((TILE_SIZE, TILE_SIZE))
            ghost.set_alpha(100)
            ghost.fill((0, 255, 0))
            screen.blit(ghost, (px * TILE_SIZE, py * TILE_SIZE))

    # Placement ghost (buildings)
    if game.build_mode and game.player.current_map == "farm":
        px = game.player.x // TILE_SIZE
        py = game.player.y // TILE_SIZE
        bt = BUILDING_TYPES[game.build_mode]
        bw, bh = bt["size"]
        ghost = pygame.Surface((bw * TILE_SIZE, bh * TILE_SIZE))
        ghost.set_alpha(80)
        can_place = True
        for b in game.buildings:
            obw, obh = BUILDING_TYPES[b["type"]]["size"]
            if px < b["tile_x"] + obw and px + bw > b["tile_x"] and py < b["tile_y"] + obh and py + bh > b["tile_y"]:
                can_place = False
                break
        if off_x <= px < off_x + f_cols and off_y <= py < off_y + f_rows and can_place:
            ghost.fill((0, 255, 0))
        else:
            ghost.fill((255, 0, 0))
        screen.blit(ghost, (px * TILE_SIZE, py * TILE_SIZE))

    # Draw player
    player_surf = get_astronaut_surf(game.player.direction)
    screen.blit(player_surf, (game.player.x, game.player.y))

    # Tree decorations
    tree_positions = [(1, 4), (1, 7), (1, 10), (0, 15),
                      (off_x + f_cols + 2, 3), (off_x + f_cols + 2, 8)]
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
    season_name = SEASONS[game.season_index]
    tint = SEASONAL_MODIFIERS[season_name]["sky_tint"]
    sky_color = blend_colors(sky_color, tint, 0.25)
    w_name = game.current_weather["name"]
    if w_name == "Void Fog":
        sky_color = blend_colors(sky_color, (60, 40, 80), 0.4)
    elif w_name == "Solar Flare":
        sky_color = blend_colors(sky_color, (255, 200, 100), 0.15)
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
    sign_y = 2 * TILE_SIZE - 28
    sign_cx = 11 * TILE_SIZE
    draw_box(screen, sign_cx - 60, sign_y, 120, 20, (60, 40, 80), True)
    draw_box(screen, sign_cx - 2, sign_y + 20, 4, 8, (80, 60, 100), True)
    draw_box(screen, sign_cx + 16, sign_y + 20, 4, 8, (80, 60, 100), True)
    draw_box(screen, sign_cx - 60, sign_y, 120, 20, (140, 100, 180), 3)
    draw_text(screen, "GENERAL STORE", sign_cx, sign_y + 10, GOLD, font_small, center=True)

    bar_b = get_building_surf("bar")
    screen.blit(bar_b, (15 * TILE_SIZE, 2 * TILE_SIZE))
    sign_cx = 18 * TILE_SIZE
    draw_box(screen, sign_cx - 60, sign_y, 120, 20, (50, 20, 20), True)
    draw_box(screen, sign_cx - 2, sign_y + 20, 4, 8, (70, 30, 30), True)
    draw_box(screen, sign_cx + 16, sign_y + 20, 4, 8, (70, 30, 30), True)
    draw_box(screen, sign_cx - 60, sign_y, 120, 20, (180, 80, 120), 2)
    draw_text(screen, "COSMIC COMET", sign_cx, sign_y + 10, PINK, font_small, center=True)

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

    # NPC location markers (visible from afar)
    for npc in game.npcs:
        mx = npc.tile_x * TILE_SIZE + int(npc.pixel_offset_x) + TILE_SIZE // 2
        my = npc.tile_y * TILE_SIZE + int(npc.pixel_offset_y)
        pygame.draw.circle(screen, npc.color, (mx, my), 5)
        pygame.draw.circle(screen, WHITE, (mx, my), 5, 1)

    # NPC Sprites
    for npc in game.npcs:
        ns = get_npc_surf(npc.id, npc.color, npc.color2)
        nx = npc.tile_x * TILE_SIZE + int(npc.pixel_offset_x)
        ny = npc.tile_y * TILE_SIZE + int(npc.pixel_offset_y) - TILE_SIZE
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

    # Facing tile highlight
    ftx, fty = game.player.get_facing_tile()
    if 0 <= ftx < SPACEPORT_TILES_X and 0 <= fty < SPACEPORT_TILES_Y:
        hl = pygame.Surface((TILE_SIZE, TILE_SIZE))
        hl.set_alpha(50)
        hl.fill((255, 255, 255))
        screen.blit(hl, (ftx * TILE_SIZE, fty * TILE_SIZE))

    # Player
    player_surf = get_astronaut_surf(game.player.direction)
    screen.blit(player_surf, (game.player.x, game.player.y))

def draw_help():
    if not game.help_active:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    panel_w, panel_h = 640, 370
    px, py = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
    pygame.draw.rect(screen, (10, 10, 30), (px, py, panel_w, panel_h))
    pygame.draw.rect(screen, (80, 100, 160), (px, py, panel_w, panel_h), 3)
    draw_text(screen, "HELP", px + panel_w // 2, py + 14, GOLD, font_large, center=True)

    left_sections = [
        ("MOVEMENT", [("WASD / Arrows", "Move")]),
        ("ACTIONS", [
            ("SPACE", "Use tool / Scan planet"),
            ("E", "Interact / Place bot / Return"),
        ]),
        ("TOOLS", [
            ("1", "Hoe"),
            ("2", "Watering Can"),
            ("3", "Scythe"),
            ("4", "Plant Seeds"),
        ]),
    ]
    right_sections = [
        ("MENUS", [
            ("I", "Inventory"),
            ("K", "Skills & Progress"),
            ("M", "Map"),
            ("S", "Save Game"),
            ("?", "Toggle Help"),
        ]),
        ("LOCATIONS", [
            ("H", "Hangar (spaceport)"),
            ("B", "Bot Workshop (spaceport)"),
            ("V", "Building Shop (spaceport)"),
            ("C", "Kitchen (farm)"),
            ("E near bar", "Bar menu"),
            ("G", "Gift mode (spaceport)"),
            ("U / R", "Upgrade / Refuel (hangar)"),
            ("E on signpost", "Expand farm"),
        ]),
    ]

    col_l = px + 20
    col_r = px + 335
    key_w = 120
    lh = 16

    def draw_section(col_x, sections, y_start):
        y = y_start
        for sname, items in sections:
            draw_text(screen, f"-- {sname} --", col_x, y, CYAN, font_small)
            y += 17
            for key, desc in items:
                draw_text(screen, key, col_x + 10, y, GOLD, font_small)
                draw_text(screen, desc, col_x + 10 + key_w, y, WHITE, font_small)
                y += lh
            y += 3
        return y

    sy = py + 40
    draw_section(col_l, left_sections, sy)
    draw_section(col_r, right_sections, sy)

    tips_y = py + 265
    draw_text(screen, "-- TIPS --", col_l, tips_y, CYAN, font_small)
    draw_text(screen, "E near landing pad: Enter festival  |  ESC: Quit", col_l + 10, tips_y + 18, LIGHT_GRAY, font_small)
    draw_text(screen, "Weather & seasons affect crop growth  |  Nebula > Bloom > Solar > Void", col_l + 10, tips_y + 34, LIGHT_GRAY, font_small)

def draw_save_menu():
    if not game.save_menu_active:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    panel_w, panel_h = 550, 380
    px, py = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
    pygame.draw.rect(screen, (10, 10, 30), (px, py, panel_w, panel_h))
    pygame.draw.rect(screen, (80, 100, 160), (px, py, panel_w, panel_h), 3)
    draw_text(screen, "SAVE / LOAD", px + panel_w // 2, py + 15, CYAN, font_large, center=True)
    for i in range(SAVE_SLOT_COUNT):
        yy = py + 55 + i * 90
        info = GameState.get_slot_info(i)
        is_current = (i == game.save_menu_slot)
        bg_color = (40, 40, 70) if is_current else (20, 20, 45)
        border_color = GOLD if is_current else (60, 60, 100)
        pygame.draw.rect(screen, bg_color, (px + 25, yy, panel_w - 50, 78))
        pygame.draw.rect(screen, border_color, (px + 25, yy, panel_w - 50, 78), 2)
        slot_label = f"Slot {i + 1}"
        if is_current:
            slot_label += "  < current"
        slot_color = GOLD if is_current else WHITE
        draw_text(screen, slot_label, px + 40, yy + 8, slot_color, font_med)
        if info:
            draw_text(screen, f"Day {info['day']}  |  {info['season']} (Day {info['day_in_season'] + 1}/{SEASON_DAY_LENGTH})", px + 40, yy + 32, LIGHT_GRAY, font_small)
            draw_text(screen, f"Gold: {info['gold']}g", px + 40, yy + 50, GOLD, font_small)
        else:
            draw_text(screen, "Empty", px + 40, yy + 36, GRAY, font_small)
        draw_text(screen, f"[{i + 1}]", px + panel_w - 60, yy + 24, GOLD, font_med)
    draw_text(screen, "1-3: Save to slot  |  L + 1-3: Load from slot  |  ESC: Close", px + panel_w // 2, py + panel_h - 25, LIGHT_GRAY, font_small, center=True)

def draw_skills():
    if not game.skills_active:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    panel_w, panel_h = 420, 340
    px, py = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
    pygame.draw.rect(screen, (10, 20, 30), (px, py, panel_w, panel_h))
    pygame.draw.rect(screen, (100, 140, 200), (px, py, panel_w, panel_h), 3)
    draw_text(screen, "Skills & Progression", px + panel_w // 2, py + 15, WHITE, font_large, center=True)
    for i, sk in enumerate(SKILLS):
        skid = sk["id"]
        level = game.get_skill_level(skid)
        xp = game.skills.get(skid, 0)
        xp_progress = game.get_skill_progress(skid)
        xp_needed = game.get_skill_xp_needed(skid)
        yy = py + 50 + i * 65
        pygame.draw.rect(screen, (20, 30, 45), (px + 20, yy, panel_w - 40, 55))
        pygame.draw.rect(screen, (60, 80, 120), (px + 20, yy, panel_w - 40, 55), 1)
        draw_text(screen, f"{sk['name']}  Lv.{level}", px + 35, yy + 4, sk["color"], font_med)
        draw_text(screen, sk["desc"], px + 35, yy + 24, LIGHT_GRAY, font_small)
        # XP bar
        bar_x, bar_y = px + panel_w - 120, yy + 8
        bar_w, bar_h = 90, 12
        pygame.draw.rect(screen, (30, 30, 40), (bar_x, bar_y, bar_w, bar_h))
        if xp_needed > 0:
            fill = int(bar_w * xp_progress / max(xp_needed, 1))
            pygame.draw.rect(screen, sk["color"], (bar_x, bar_y, fill, bar_h))
        draw_text(screen, f"{xp} XP", bar_x + bar_w // 2, bar_y - 2, WHITE, font_small, center=True)
        # Perk checkmarks
        perk_line = []
        for plv in [5, 10, 15, 20]:
            if plv <= level:
                perk_line.append(f"★Lv{plv}")
        if perk_line:
            draw_text(screen, " ".join(perk_line), px + 35, yy + 40, GOLD, font_small)
    draw_text(screen, "Press K to close", px + panel_w // 2, py + panel_h - 22, LIGHT_GRAY, font_small, center=True)

def draw_cooking():
    if not game.cooking_active:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    panel_w, panel_h = 550, 440
    px, py = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
    pygame.draw.rect(screen, (20, 30, 20), (px, py, panel_w, panel_h))
    pygame.draw.rect(screen, (80, 180, 80), (px, py, panel_w, panel_h), 3)
    draw_text(screen, "~ Kitchen ~", px + panel_w // 2, py + 15, ENERGY_GREEN, font_large, center=True)
    draw_text(screen, f"Energy: {game.player.energy}/{game.player.max_energy}", px + panel_w // 2, py + 42, GOLD, font_med, center=True)
    recipe_keys = list(RECIPES.keys())
    idx = 0
    for i, rk in enumerate(recipe_keys):
        recipe = RECIPES[rk]
        can_cook = all(game.player.inventory.get(ing, 0) >= need for ing, need in recipe["ingredients"].items())
        yy = py + 75 + idx * 70
        if not can_cook:
            continue
        pygame.draw.rect(screen, (30, 50, 30), (px + 20, yy, panel_w - 40, 60))
        pygame.draw.rect(screen, (60, 120, 60), (px + 20, yy, panel_w - 40, 60), 1)
        draw_text(screen, recipe["name"], px + 40, yy + 6, WHITE, font_med)
        ings = ", ".join(f"{v}x {k}" for k, v in recipe["ingredients"].items())
        draw_text(screen, ings, px + 40, yy + 26, LIGHT_GRAY, font_small)
        draw_text(screen, f"+{recipe['energy']}E  Sell: {recipe['sell_price']}g", px + 40, yy + 44, GOLD, font_small)
        draw_text(screen, f"[{idx+1}]", px + panel_w - 60, yy + 12, GOLD, font_med)
        idx += 1
    if idx == 0:
        draw_text(screen, "No recipes available — harvest some crops first!", px + panel_w // 2, py + 150, LIGHT_GRAY, font_med, center=True)
    draw_text(screen, "1-8: Cook  |  ESC: Exit", px + panel_w // 2, py + panel_h - 25, LIGHT_GRAY, font_small, center=True)

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
            if game.festival_active:
                if game.festival_type == "crop_tasting":
                    if "result" in game.festival_data:
                        if event.key == pygame.K_e:
                            game.end_festival(game.festival_data.get("won", False))
                    else:
                        for i in range(3):
                            if event.key == getattr(pygame, f"K_{i+1}"):
                                crops = game.festival_data.get("crops", [])
                                if i < len(crops):
                                    chosen = crops[i]
                                    price = CROP_TYPES[chosen]["sell_price"]
                                    score = price * random.uniform(0.8, 1.2)
                                    threshold = game.festival_data.get("threshold", 50)
                                    won = score >= threshold
                                    game.festival_data["won"] = won
                                    game.festival_data["result"] = f"Score: {score:.0f}! You won!" if won else f"Score: {score:.0f}. Not enough for the judges."
                                    game.festival_data["over"] = True
                                    game.player.remove_item(chosen, 1)
                elif game.festival_type == "flower_arrange":
                    if event.key == pygame.K_ESCAPE:
                        game.end_festival(False)
                    elif event.key == pygame.K_UP:
                        game.festival_data["cursor"][0] = max(0, game.festival_data["cursor"][0] - 1)
                    elif event.key == pygame.K_DOWN:
                        game.festival_data["cursor"][0] = min(3, game.festival_data["cursor"][0] + 1)
                    elif event.key == pygame.K_LEFT:
                        game.festival_data["cursor"][1] = max(0, game.festival_data["cursor"][1] - 1)
                    elif event.key == pygame.K_RIGHT:
                        game.festival_data["cursor"][1] = min(3, game.festival_data["cursor"][1] + 1)
                    elif event.key == pygame.K_SPACE:
                        r, c = game.festival_data["cursor"]
                        grid = game.festival_data["grid"]
                        if event.key == pygame.K_SPACE:
                            dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                            for dr, dc in dirs:
                                nr, nc = r + dr, c + dc
                                if 0 <= nr < 4 and 0 <= nc < 4:
                                    grid[r][c], grid[nr][nc] = grid[nr][nc], grid[r][c]
                                    break
                    elif event.key == pygame.K_RETURN:
                        if game.festival_data.get("grid") == game.festival_data.get("target"):
                            game.festival_data["won"] = True
                            game.festival_data["over"] = True
                            game.festival_data["result"] = "Perfect arrangement! You won!"
                        else:
                            game.set_message("Not quite right. Keep trying!")
                elif game.festival_type == "rhythm":
                    if "result" in game.festival_data:
                        if event.key == pygame.K_e:
                            game.end_festival(game.festival_data.get("won", False))
                        continue
                    key_map = {
                        pygame.K_UP: "UP", pygame.K_DOWN: "DOWN",
                        pygame.K_LEFT: "LEFT", pygame.K_RIGHT: "RIGHT",
                    }
                    if game.festival_data.get("cooldown", 0) > 0:
                        game.festival_data["cooldown"] -= 1
                    if event.key in key_map and game.festival_data.get("cooldown", 0) == 0:
                        pressed = key_map[event.key]
                        idx = game.festival_data.get("index", 0)
                        seq = game.festival_data.get("sequence", [])
                        if idx < len(seq) and pressed == seq[idx]:
                            game.festival_data["index"] = idx + 1
                            game.festival_data["cooldown"] = 15
                            if idx + 1 >= len(seq):
                                misses = game.festival_data.get("misses", 0)
                                score = len(seq) - misses
                                won = score >= 7
                                game.festival_data["won"] = won
                                game.festival_data["result"] = f"Perfect dance! You won!" if won else f"Scored {score}/10. Not quite enough."
                                game.festival_data["over"] = True
                        elif pressed != "UP" and pressed != "DOWN" and pressed != "LEFT" and pressed != "RIGHT":
                            pass
                        else:
                            game.festival_data["misses"] = game.festival_data.get("misses", 0) + 1
                            game.festival_data["index"] += 1
                            game.festival_data["cooldown"] = 15
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
                qty = 10 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
                sell_keys = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r, pygame.K_t, pygame.K_y]
                for i, crop_key in enumerate(CROP_ORDER):
                    if event.key == getattr(pygame, f"K_{i+1}"):
                        game.buy_item(crop_key, qty)
                    if i < len(sell_keys) and event.key == sell_keys[i]:
                        game.sell_item(crop_key, qty)
                dish_keys = [pygame.K_z, pygame.K_x, pygame.K_c, pygame.K_v, pygame.K_b, pygame.K_n, pygame.K_m, pygame.K_p]
                di = 0
                for rk, recipe in RECIPES.items():
                    if game.player.inventory.get(recipe["name"], 0) <= 0:
                        continue
                    if di < len(dish_keys) and event.key == dish_keys[di]:
                        game.sell_dish(recipe["name"], qty)
                    di += 1
                continue

            if game.bar_active:
                if event.key == pygame.K_ESCAPE:
                    game.bar_active = False
                    game.subscreen = None
                qty = 10 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
                for i in range(len(BAR_ITEMS)):
                    if event.key == getattr(pygame, f"K_{i+1}"):
                        game.buy_bar_item(i, qty)
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

            if game.build_mode:
                if event.key == pygame.K_ESCAPE:
                    game.build_mode = None
                    game.set_message("Building placement cancelled.")
                    continue
                elif event.key == pygame.K_e:
                    game.place_building()
                    continue

            if game.save_menu_active:
                if event.key == pygame.K_ESCAPE:
                    game.save_menu_active = False
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    slot = event.key - pygame.K_1
                    game.save_game(slot)
                    game.save_menu_slot = slot
                    game.save_menu_active = False
                elif event.key == pygame.K_l:
                    keys = pygame.key.get_pressed()
                    load_slot = None
                    if keys[pygame.K_1]: load_slot = 0
                    elif keys[pygame.K_2]: load_slot = 1
                    elif keys[pygame.K_3]: load_slot = 2
                    if load_slot is not None and game.load_game(load_slot):
                        game.save_menu_slot = load_slot
                        game.set_message(f"Loaded Slot {load_slot + 1}!")
                        game.save_menu_active = False
                continue

            if game.cooking_active:
                if event.key == pygame.K_ESCAPE:
                    game.cooking_active = False
                else:
                    qty = 10 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
                    available = [rk for rk in RECIPES if all(game.player.inventory.get(ing, 0) >= need * qty for ing, need in RECIPES[rk]["ingredients"].items())]
                    for i in range(len(available)):
                        if event.key == getattr(pygame, f"K_{i+1}"):
                            game.cook_recipe(available[i], qty)
                            game.cooking_active = False
                continue

            if game.expand_menu_active:
                if event.key == pygame.K_ESCAPE:
                    game.expand_menu_active = False
                elif event.key == pygame.K_e:
                    game.buy_expansion()
                    game.expand_menu_active = False
                continue

            if game.building_shop_active:
                if event.key == pygame.K_ESCAPE:
                    game.building_shop_active = False
                else:
                    bk = list(BUILDING_TYPES.keys())
                    for i, btype in enumerate(bk):
                        if event.key == getattr(pygame, f"K_{i+1}"):
                            game.buy_building(btype)
                continue

            if game.subscreen == "shipping_bin":
                if event.key == pygame.K_ESCAPE:
                    game.subscreen = None
                else:
                    for i, crop_key in enumerate(CROP_ORDER):
                        if event.key == getattr(pygame, f"K_{i+1}"):
                            count = game.player.inventory.get(crop_key, 0)
                            if count > 0:
                                qty = 1
                                game.player.remove_item(crop_key, qty)
                                game.shipping_bin_contents[crop_key] = game.shipping_bin_contents.get(crop_key, 0) + qty
                                data = CROP_TYPES[crop_key]
                                game.set_message(f"Added {data['name']} to shipping bin!")
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
            elif event.key == pygame.K_c:
                if game.player.current_map == "farm":
                    game.cooking_active = True
            elif event.key == pygame.K_k:
                game.skills_active = not game.skills_active
            elif event.key == pygame.K_b:
                if game.player.current_map == "spaceport":
                    game.bot_shop_active = True
                elif game.player.current_map == "farm":
                    px = game.player.x // TILE_SIZE
                    py = game.player.y // TILE_SIZE
                    if 7 <= px <= 10 and 0 <= py <= 3:
                        game.sleep_prompt = True
            elif event.key == pygame.K_v:
                if game.player.current_map == "spaceport":
                    game.building_shop_active = True
            elif event.key == pygame.K_s:
                if not game.save_menu_active:
                    game.save_menu_active = True

    keys = pygame.key.get_pressed()
    if not game.dialogue_active and not game.shop_active and not game.bot_shop_active and not game.hangar_active and not game.planet_explore_active and not game.seed_select_active and not game.inventory_active and not game.sleep_prompt and not game.bar_active and not game.festival_active and not game.save_menu_active and not game.skills_active and not game.expand_menu_active and not game.building_shop_active and not game.subscreen == "shipping_bin":
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
                off_x = game.farm_off_x
                off_y = game.farm_off_y
                if py_t >= off_y + game.farm_rows + 1 and px_t >= off_x + game.farm_cols:
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
                    game.player.x = (game.farm_off_x + game.farm_cols + 1) * TILE_SIZE
                    game.player.y = (game.farm_off_y + game.farm_rows) * TILE_SIZE
                    game.player.farm_x = game.player.x
                    game.player.farm_y = game.player.y
                    game.set_message("Back on the farm!")

def draw_expand_menu():
    if not game.expand_menu_active:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    panel_w, panel_h = 500, 320
    px, py = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
    pygame.draw.rect(screen, (20, 15, 30), (px, py, panel_w, panel_h))
    pygame.draw.rect(screen, (120, 100, 80), (px, py, panel_w, panel_h), 3)
    draw_text(screen, "~ Farm Expansion ~", px + panel_w // 2, py + 15, GOLD, font_large, center=True)
    cur = game.farm_expansion_tier
    draw_text(screen, f"Current Size: {game.farm_cols}x{game.farm_rows}", px + panel_w // 2, py + 45, WHITE, font_med, center=True)
    if cur + 1 < len(FARM_EXPANSIONS):
        nxt = FARM_EXPANSIONS[cur + 1]
        can_afford = game.player.gold >= nxt["cost"]
        color = GREEN if can_afford else RED
        draw_text(screen, f"Next: {nxt['cols']}x{nxt['rows']}  Cost: {nxt['cost']}g", px + panel_w // 2, py + 70, color, font_med, center=True)
        draw_text(screen, f"[E] Expand ({nxt['cost']}g)  |  [ESC] Cancel", px + panel_w // 2, py + panel_h - 25, LIGHT_GRAY, font_small, center=True)
    else:
        draw_text(screen, "★ MAX SIZE ★", px + panel_w // 2, py + 70, PINK, font_med, center=True)
        draw_text(screen, "[ESC] Close", px + panel_w // 2, py + panel_h - 25, LIGHT_GRAY, font_small, center=True)
    for i in range(cur + 1):
        t = FARM_EXPANSIONS[i]
        yy = py + 100 + i * 24
        icon = "★" if i <= cur else "☆"
        draw_text(screen, f"{icon} Tier {i}: {t['cols']}x{t['rows']} ({t['cost']}g)", px + 30, yy, GOLD if i <= cur else GRAY, font_small)

def draw_building_shop():
    if not game.building_shop_active:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    panel_w, panel_h = 550, 420
    px, py = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
    pygame.draw.rect(screen, (20, 20, 30), (px, py, panel_w, panel_h))
    pygame.draw.rect(screen, (80, 120, 80), (px, py, panel_w, panel_h), 3)
    draw_text(screen, "Construction Shop", px + panel_w // 2, py + 15, GOLD, font_large, center=True)
    draw_text(screen, f"Gold: {game.player.gold}g", px + panel_w // 2, py + 42, GOLD, font_med, center=True)
    bk = list(BUILDING_TYPES.keys())
    for i, btype in enumerate(bk):
        bt = BUILDING_TYPES[btype]
        yy = py + 75 + i * 70
        can_afford = game.player.gold >= bt["cost"]
        bg = (40, 40, 50) if can_afford else (30, 20, 20)
        pygame.draw.rect(screen, bg, (px + 20, yy, panel_w - 40, 60))
        pygame.draw.rect(screen, (80, 100, 80), (px + 20, yy, panel_w - 40, 60), 1)
        bsurf = get_building_surf(btype)
        screen.blit(bsurf, (px + 28, yy + 4))
        draw_text(screen, bt["name"], px + 70, yy + 6, WHITE if can_afford else GRAY, font_med)
        draw_text(screen, bt["desc"], px + 70, yy + 28, LIGHT_GRAY, font_small)
        draw_text(screen, f"[{i+1}] {bt['cost']}g", px + panel_w - 80, yy + 14, GOLD if can_afford else RED, font_med)
    draw_text(screen, "1-4: Buy  |  ESC: Exit", px + panel_w // 2, py + panel_h - 25, LIGHT_GRAY, font_small, center=True)

def draw_shipping_bin():
    if game.subscreen != "shipping_bin":
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    panel_w, panel_h = 500, 400
    px, py = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
    pygame.draw.rect(screen, (20, 20, 30), (px, py, panel_w, panel_h))
    pygame.draw.rect(screen, (180, 100, 60), (px, py, panel_w, panel_h), 3)
    draw_text(screen, "Shipping Bin", px + panel_w // 2, py + 15, GOLD, font_large, center=True)
    total_items = sum(game.shipping_bin_contents.values()) if game.shipping_bin_contents else 0
    draw_text(screen, f"Items to sell tonight: {total_items}", px + panel_w // 2, py + 45, WHITE, font_med, center=True)
    y = py + 75
    for item, count in sorted(game.shipping_bin_contents.items()):
        data = CROP_TYPES.get(item)
        if data:
            draw_text(screen, f"{data['name']} x{count}  ({data['sell_price'] * count}g)", px + 40, y, WHITE, font_small)
            y += 22
    if not game.shipping_bin_contents:
        draw_text(screen, "No items yet. Press I to transfer items from inventory.", px + panel_w // 2, py + 120, LIGHT_GRAY, font_small, center=True)
    y = max(y + 20, py + 180)
    draw_text(screen, "Items in inventory: press [1-6] to add to bin", px + panel_w // 2, y, CYAN, font_small, center=True)
    for i, crop_key in enumerate(CROP_ORDER):
        count = game.player.inventory.get(crop_key, 0)
        if count > 0:
            data = CROP_TYPES[crop_key]
            sy = y + 20 + i * 22
            draw_text(screen, f"[{i+1}] {data['name']} x{count} → add {data['sell_price']}g each", px + 40, sy, WHITE, font_small)
    draw_text(screen, "ESC: Close", px + panel_w // 2, py + panel_h - 22, LIGHT_GRAY, font_small, center=True)

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
    draw_weather_particles()

    if game.current_weather["name"] == "Void Fog":
        fog = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fog.set_alpha(60)
        fog.fill((60, 40, 80))
        screen.blit(fog, (0, 0))

    if game.dialogue_active:
        draw_dialogue()
    if game.shop_active:
        draw_shop()
    if game.hangar_active:
        draw_hangar()
    if game.bot_shop_active:
        draw_bot_shop()
    if game.bar_active:
        draw_bar()
    if game.planet_explore_active:
        draw_planet_explore()
    if game.inventory_active:
        draw_inventory()
    if game.seed_select_active:
        draw_seed_select()
    if game.sleep_prompt:
        draw_sleep_prompt()
    if game.save_menu_active:
        draw_save_menu()
    if game.skills_active:
        draw_skills()
    if game.festival_active:
        draw_festival()
    if game.cooking_active:
        draw_cooking()
    if game.expand_menu_active:
        draw_expand_menu()
    if game.building_shop_active:
        draw_building_shop()
    if game.subscreen == "shipping_bin":
        draw_shipping_bin()
    if game.help_active:
        draw_help()

def main():
    show_title_card()
    game.set_message("Welcome to Space Farm Galaxy! Press G at the port to give gifts to NPCs!")

    while game.running:
        handle_events()
        for npc in game.npcs:
            npc.update_movement()
        game.update_particles()
        game.update_weather_particles()

        if game.message_timer > 0:
            game.message_timer -= 1

        render()
        pygame.display.flip()
        clock.tick(FPS)

    game.save_game(game.save_menu_slot)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
