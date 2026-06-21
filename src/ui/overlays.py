from src.ui.context import *

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

    artisan_y = dish_y + 20 + di * 22 + 10
    draw_text(screen, "-- Artisan Goods --", px + col_w + col_w // 2, artisan_y, GOLD, font_med, center=True)
    artisan_keys = ["F", "G", "H", "J", "K", "L", "U", "O"]
    ai = 0
    for rk, recipe in ARTISAN_RECIPES.items():
        name = recipe["name"]
        count = game.player.inventory.get(name, 0)
        if count <= 0:
            continue
        yy = artisan_y + 20 + ai * 22
        draw_text(screen, f"{name} x{count} - {recipe['sell_price']}g", px + col_w + 40, yy, WHITE, font_small)
        if ai < len(artisan_keys):
            draw_text(screen, f"[{artisan_keys[ai]}]", px + panel_w - 50, yy, ORANGE, font_small)
        ai += 1

    fish_y = artisan_y + 20 + ai * 22 + 10
    draw_text(screen, "-- Fish --", px + col_w + col_w // 2, fish_y, CYAN, font_med, center=True)
    fish_keys = ["7", "8", "9", "0", "A", "I"]
    fi = 0
    for fid in FISH_ORDER:
        count = game.player.inventory.get(fid, 0)
        if count <= 0:
            continue
        yy = fish_y + 20 + fi * 22
        f = FISH_TYPES[fid]
        draw_text(screen, f"{f['name']} x{count} - {f['sell_price']}g", px + col_w + 40, yy, WHITE, font_small)
        if fi < len(fish_keys):
            draw_text(screen, f"[{fish_keys[fi]}]", px + panel_w - 50, yy, ORANGE, font_small)
        fi += 1

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

def draw_crafting():
    if not game.crafting_active:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    panel_w, panel_h = 600, 500
    px, py = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
    pygame.draw.rect(screen, (30, 20, 30), (px, py, panel_w, panel_h))
    pygame.draw.rect(screen, (200, 160, 80), (px, py, panel_w, panel_h), 3)
    draw_text(screen, "~ Artisan Workshop ~", px + panel_w // 2, py + 15, GOLD, font_large, center=True)

    recipe_keys = list(ARTISAN_RECIPES.keys())
    for i, rk in enumerate(recipe_keys):
        recipe = ARTISAN_RECIPES[rk]
        can_craft = all(game.player.inventory.get(ing, 0) >= need for ing, need in recipe["ingredients"].items())
        yy = py + 55 + i * 42
        row_color = (45, 35, 25) if can_craft else (30, 28, 28)
        pygame.draw.rect(screen, row_color, (px + 15, yy, panel_w - 30, 38))
        pygame.draw.rect(screen, (90, 70, 40), (px + 15, yy, panel_w - 30, 38), 1)
        name_color = WHITE if can_craft else LIGHT_GRAY
        draw_text(screen, recipe["name"], px + 30, yy + 3, name_color, font_med)
        ings = ", ".join(f"{game.player.inventory.get(k, 0)}/{v} {k}" for k, v in recipe["ingredients"].items())
        draw_text(screen, ings, px + 30, yy + 21, LIGHT_GRAY, font_small)
        # Profit analysis: output price vs. sum of ingredient base sell prices
        in_val = 0
        for ing, need in recipe["ingredients"].items():
            in_val += _ingredient_value(ing) * need
        profit = recipe["sell_price"] - in_val
        time_txt = "Instant" if recipe["processing_days"] == 0 else f"{recipe['processing_days']}d"
        draw_text(screen, f"{recipe['sell_price']}g ({time_txt})  +{profit}g", px + 320, yy + 3, GOLD, font_small)
        draw_text(screen, f"profit", px + 320, yy + 21, (120, 200, 120) if profit >= 0 else ORANGE, font_small)
        if can_craft:
            draw_text(screen, f"[{i+1}]", px + panel_w - 50, yy + 10, GOLD, font_med)

    # Processing queue
    qy = py + 55 + len(recipe_keys) * 42 + 10
    draw_text(screen, "-- Processing Queue --", px + panel_w // 2, qy, CYAN, font_med, center=True)
    if not game.processing_queue:
        draw_text(screen, "(empty)", px + panel_w // 2, qy + 22, LIGHT_GRAY, font_small, center=True)
    else:
        for j, entry in enumerate(game.processing_queue):
            recipe = ARTISAN_RECIPES.get(entry["recipe_key"], {})
            label = f"{entry['count']}x {recipe.get('name', '?')} - {entry['days_remaining']}d left"
            draw_text(screen, label, px + panel_w // 2, qy + 22 + j * 18, WHITE, font_small, center=True)

    draw_text(screen, "1-8: Craft (Shift=10)  |  ESC: Exit", px + panel_w // 2, py + panel_h - 25, LIGHT_GRAY, font_small, center=True)

def _ingredient_value(item_key):
    """Base sell value of a crafting ingredient (crop, dish, or animal product)."""
    if item_key in CROP_TYPES:
        return CROP_TYPES[item_key]["sell_price"]
    recipe = next((r for r in RECIPES.values() if r["name"] == item_key), None)
    if recipe:
        return recipe["sell_price"]
    return ANIMAL_PRODUCTS.get(item_key, 0)

def draw_sleep_prompt():
    if not game.sleep_prompt:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    draw_text(screen, "Go to sleep for the night?", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30, WHITE, font_large, center=True)
    draw_text(screen, "Press Y to sleep | N to stay up", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10, LIGHT_GRAY, font_med, center=True)

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
        draw_text(screen, bt["name"], px + 70, yy + 6, WHITE if can_afford else GRAY, font_small)
        draw_text(screen, bt["desc"], px + 70, yy + 28, LIGHT_GRAY, font_small)
        draw_text(screen, f"[{i+1}] {bt['cost']}g", px + panel_w - 80, yy + 14, GOLD if can_afford else RED, font_small)
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

def draw_pet_shop():
    if not game.pet_shop_active:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    panel_w, panel_h = 550, 420
    px, py = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
    pygame.draw.rect(screen, (30, 20, 40), (px, py, panel_w, panel_h))
    pygame.draw.rect(screen, (200, 100, 180), (px, py, panel_w, panel_h), 3)
    draw_text(screen, "~ Exotic Pet Shop ~", px + panel_w // 2, py + 15, PINK, font_large, center=True)
    draw_text(screen, f"Gold: {game.player.gold}g  |  Barn: {len(game.animals)}/{game.barn_capacity}", px + panel_w // 2, py + 42, GOLD, font_med, center=True)
    ak = list(ANIMAL_TYPES.keys())
    for i, aid in enumerate(ak):
        at = ANIMAL_TYPES[aid]
        yy = py + 75 + i * 100
        can_afford = game.player.gold >= at["cost"]
        can_house = len(game.animals) < game.barn_capacity
        can_buy = can_afford and can_house
        bg = (40, 30, 50) if can_buy else (30, 20, 30)
        pygame.draw.rect(screen, bg, (px + 20, yy, panel_w - 40, 88))
        pygame.draw.rect(screen, (120, 80, 120), (px + 20, yy, panel_w - 40, 88), 1)
        asurf = get_animal_surf(aid)
        screen.blit(asurf, (px + 28, yy + 6))
        draw_text(screen, at["name"], px + 70, yy + 6, WHITE if can_buy else GRAY, font_med)
        draw_text(screen, at["desc"], px + 70, yy + 26, LIGHT_GRAY, font_small)
        feed_str = ", ".join(f"{v}x {k}" for k, v in at["feed"].items())
        draw_text(screen, f"Feed: {feed_str} | Produces: {at['produce']} every {at['produce_interval']} days", px + 70, yy + 44, CYAN, font_small)
        draw_text(screen, f"[{i+1}] {at['cost']}g  |  Sell: {at['sell_price']}g", px + panel_w - 120, yy + 62, GOLD if can_afford else RED, font_med)
        if not can_house:
            draw_text(screen, "BARN FULL", px + panel_w - 120, yy + 62, RED, font_small)
    draw_text(screen, "1-3: Buy Animal  |  ESC: Exit", px + panel_w // 2, py + panel_h - 25, LIGHT_GRAY, font_small, center=True)

def draw_barn_overlay():
    if not game.barn_overlay_active:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 20))
    screen.blit(overlay, (0, 0))
    panel_w, panel_h = 500, 400
    px, py = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
    pygame.draw.rect(screen, (20, 30, 20), (px, py, panel_w, panel_h))
    pygame.draw.rect(screen, (140, 80, 40), (px, py, panel_w, panel_h), 3)
    draw_text(screen, "~ Barn ~", px + panel_w // 2, py + 15, GOLD, font_large, center=True)
    draw_text(screen, f"Animals: {len(game.animals)}/{game.barn_capacity}", px + panel_w // 2, py + 42, WHITE, font_med, center=True)
    if not game.animals:
        draw_text(screen, "No animals yet. Visit Zoop at the Space Port!", px + panel_w // 2, py + 120, LIGHT_GRAY, font_med, center=True)
    else:
        for i, a in enumerate(game.animals):
            at = ANIMAL_TYPES[a["type"]]
            yy = py + 75 + i * 55
            bar_h = min(i, 5) * 55
            if bar_h + 75 + 55 > panel_h - 30:
                break
            pygame.draw.rect(screen, (30, 40, 30), (px + 20, yy, panel_w - 40, 48))
            pygame.draw.rect(screen, (80, 100, 60), (px + 20, yy, panel_w - 40, 48), 1)
            asurf = get_animal_surf(a["type"])
            screen.blit(asurf, (px + 28, yy + 4))
            status = "Fed" if a["fed_today"] else "Hungry"
            days_left = at["produce_interval"] - a["days_since_produce"]
            prod_status = f"Next produce in {days_left}d" if days_left > 0 else "Ready!"
            draw_text(screen, f"{at['name']}  |  {status}  |  {prod_status}", px + 70, yy + 8, WHITE, font_small)
            feed_str = ", ".join(f"{v}x {k}" for k, v in at["feed"].items())
            draw_text(screen, f"Feed: {feed_str}", px + 70, yy + 28, LIGHT_GRAY, font_small)
    draw_text(screen, "ESC: Close", px + panel_w // 2, py + panel_h - 22, LIGHT_GRAY, font_small, center=True)

def draw_fishing():
    if not game.fishing_active:
        return
    # Animated water background
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill((10, 30, 60))
    screen.blit(overlay, (0, 0))
    t = pygame.time.get_ticks()
    for wy in range(80, SCREEN_HEIGHT, 24):
        shade = 40 + (wy // 24 % 2) * 15
        pygame.draw.rect(screen, (10, shade, shade + 40), (0, wy, SCREEN_WIDTH, 12))
    for i in range(0, SCREEN_WIDTH, 40):
        wx = i + int(8 * math.sin((t / 400.0) + i))
        draw_text(screen, "~", wx, 120 + int(10 * math.sin(t / 300.0 + i)), (60, 120, 160), font_small)

    draw_text(screen, "~ Fishing Pier ~", SCREEN_WIDTH // 2, 30, CYAN, font_large, center=True)
    state = game.fishing_state
    cx = SCREEN_WIDTH // 2

    if state in ("casting", "waiting", "hooked"):
        bob = get_bobber_surf()
        bob_y = 240 + int(6 * math.sin(t / 250.0))
        if state == "hooked":
            bob_y += random.randint(-4, 4)  # shake
        screen.blit(bob, (cx - 6, bob_y))

    if state == "casting":
        draw_text(screen, "Press SPACE to cast your line", cx, 380, WHITE, font_med, center=True)
    elif state == "waiting":
        draw_text(screen, "Waiting for a bite...", cx, 380, LIGHT_GRAY, font_med, center=True)
    elif state == "hooked":
        draw_text(screen, "A BITE!  Press SPACE!", cx, 380, YELLOW, font_large, center=True)
    elif state == "reeling":
        draw_text(screen, "Tap SPACE to reel it in!", cx, 110, YELLOW, font_med, center=True)
        # vertical progress bar on the right
        bar_x, bar_y, bar_w, bar_h = SCREEN_WIDTH - 90, 150, 40, 320
        pygame.draw.rect(screen, (30, 30, 50), (bar_x, bar_y, bar_w, bar_h))
        fill_h = int(bar_h * max(0.0, min(1.0, game.fishing_progress)))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y + bar_h - fill_h, bar_w, fill_h))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 2)
        # struggling fish silhouette
        if game.fishing_current_fish:
            fs = get_fish_surf(game.fishing_current_fish)
            fy = 250 + int(30 * math.sin(t / 120.0))
            screen.blit(pygame.transform.scale(fs, (64, 64)), (cx - 32, fy))
    elif state == "caught":
        fid = game.fishing_caught_fish
        if fid:
            f = FISH_TYPES[fid]
            fs = get_fish_surf(fid)
            screen.blit(pygame.transform.scale(fs, (96, 96)), (cx - 48, 200))
            draw_text(screen, f["name"], cx, 320, f["color"], font_large, center=True)
            draw_text(screen, game.message, cx, 356, WHITE, font_med, center=True)
        draw_text(screen, "Press SPACE to continue", cx, 400, GOLD, font_med, center=True)

    # Collection panel (bottom strip)
    panel_y = SCREEN_HEIGHT - 80
    pygame.draw.rect(screen, (8, 16, 32), (0, panel_y, SCREEN_WIDTH, 80))
    pygame.draw.rect(screen, (60, 100, 140), (0, panel_y, SCREEN_WIDTH, 80), 2)
    caught_n = sum(1 for v in game.fish_collection.values() if v)
    draw_text(screen, f"Collection: {caught_n}/{len(FISH_TYPES)}  (total caught: {game.fish_caught_total})",
              12, panel_y + 6, LIGHT_GRAY, font_small)
    for i, fid in enumerate(FISH_ORDER):
        slot_x = 16 + i * 64
        have = game.fish_collection.get(fid, False)
        fs = get_fish_surf(fid)
        if have:
            screen.blit(fs, (slot_x, panel_y + 30))
        else:
            sil = fs.copy()
            sil.fill((40, 40, 50), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(sil, (slot_x, panel_y + 30))

    draw_text(screen, "ESC: Leave the pier", SCREEN_WIDTH - 12, panel_y + 6, LIGHT_GRAY, font_small)
