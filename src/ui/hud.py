from src.ui.context import *

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

    draw_text(screen, f"Rank: {game.get_rank_name()}  ({game.reputation} rep)", 10, 96, (200, 170, 255), font_small)
    tracked = [q for q in game.active_quests if q["accepted"] and not q["claimed"]]
    qy = 112
    for q in tracked[:4]:
        mark = "DONE" if q["completed"] else f"{q['progress']}/{q['count']}"
        col = GOLD if q["completed"] else WHITE
        draw_text(screen, f"• {q['desc']} [{mark}]", 10, qy, col, font_small)
        qy += 16

    if game.player.current_map == "farm" and not any([game.dialogue_active, game.shop_active, game.bot_shop_active, game.hangar_active, game.inventory_active, game.seed_select_active, game.sleep_prompt, game.bar_active, game.festival_active, game.save_menu_active, game.cooking_active, game.crafting_active, game.expand_menu_active, game.building_shop_active, game.subscreen == "shipping_bin", game.build_mode is not None, game.pet_shop_active, game.barn_overlay_active]):
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

def draw_weather_particles():
    for p in game.weather_particles:
        alpha = int(255 * p["life"] / max(p["max_life"], 1))
        size = p["size"]
        s = pygame.Surface((size, size))
        s.set_alpha(alpha)
        c = p["color"]
        s.fill(c)
        screen.blit(s, (int(p["x"]), int(p["y"])))
