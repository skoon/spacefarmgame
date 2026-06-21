from src.ui.context import *

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
        # Animals near barns
        if b["type"] == "barn":
            for i, a in enumerate(game.animals):
                ax = b["tile_x"] * TILE_SIZE + 4 + (i % 2) * 16
                ay = b["tile_y"] * TILE_SIZE + bh * TILE_SIZE - 12 + (i // 2) * 12
                bob = int(math.sin(pygame.time.get_ticks() * 0.003 + i) * 2)
                asurf = get_animal_surf(a["type"])
                screen.blit(asurf, (ax, ay + bob))

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
        ftx, fty = game.player.get_facing_tile()
        px, py = ftx, fty
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

    # Fishing pier (east edge, tiles 25-29 x 10-14)
    t = pygame.time.get_ticks()
    for wx in range(25, 30):
        for wy in range(10, 15):
            shade = 90 + ((wx + wy) % 2) * 20 + int(10 * math.sin(t / 400.0 + wx + wy))
            water = make_surface(TILE_SIZE, TILE_SIZE, (20, 70, max(60, min(150, shade + 40))))
            screen.blit(water, (wx * TILE_SIZE, wy * TILE_SIZE))
    for wy in range(10, 15):  # wooden pier planks at the approach column
        plank = make_surface(TILE_SIZE, TILE_SIZE, (110, 80, 50))
        screen.blit(plank, (24 * TILE_SIZE, wy * TILE_SIZE))
    draw_text(screen, "FISHING PIER", 27 * TILE_SIZE, 9 * TILE_SIZE + 8, CYAN, font_small, center=True)

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
