from src.ui.context import *

def tile_variant(col, row, count=4):
    return (col * 7 + row * 13) % count

DECO_TYPES = ["flower_pink", "flower_yellow", "flower_purple", "flower_blue",
              "rock_small", "rock_medium", "rock_large", "grass_tuft", "mushroom", "crystal"]

SPACEPORT_BG_CACHE = {}

def _build_spaceport_bg(season_name):
    key = f"sp_bg_{season_name}"
    if key in SPACEPORT_BG_CACHE:
        return SPACEPORT_BG_CACHE[key]
    bg = make_surface(SCREEN_WIDTH, SCREEN_HEIGHT)
    # Landing pad (static)
    for dx in range(6):
        for dy in range(4):
            pad_x = (12 + dx) * TILE_SIZE
            pad_y = (16 + dy) * TILE_SIZE
            c = (100 + dx * 10, 100 + dx * 10, 110 + dy * 10)
            s = make_surface(TILE_SIZE, TILE_SIZE, c)
            bg.blit(s, (pad_x, pad_y))
    # Pier planks (static)
    for wy in range(8, 13):
        plank = make_surface(TILE_SIZE, TILE_SIZE, (110, 80, 50))
        bg.blit(plank, (24 * TILE_SIZE, wy * TILE_SIZE))
    # Paths (static)
    for px in range(8, 22):
        bg.blit(get_tile_surf("path", tile_variant(px, 12, 4), season_name), (px * TILE_SIZE, 12 * TILE_SIZE))
    for py in range(8, 13):
        bg.blit(get_tile_surf("path", tile_variant(8, py, 4), season_name), (8 * TILE_SIZE, py * TILE_SIZE))
        bg.blit(get_tile_surf("path", tile_variant(21, py, 4), season_name), (21 * TILE_SIZE, py * TILE_SIZE))
    # Static text labels (cached in dict)
    if "texts" not in SPACEPORT_BG_CACHE:
        SPACEPORT_BG_CACHE["texts"] = {}
    tc = SPACEPORT_BG_CACHE["texts"]
    text_defs = [
        ("lpad", "★ LANDING PAD ★", 15 * TILE_SIZE, 17 * TILE_SIZE, CYAN),
        ("pier", "FISHING PIER", 27 * TILE_SIZE, 7 * TILE_SIZE + 8, CYAN),
        ("shop", "GENERAL STORE", 11 * TILE_SIZE, 2 * TILE_SIZE - 18, GOLD),
        ("bar", "COSMIC COMET", 18 * TILE_SIZE, 2 * TILE_SIZE - 18, PINK),
        ("quest", "QUESTS", 6 * TILE_SIZE + TILE_SIZE // 2, 10 * TILE_SIZE - 8, GOLD),
        ("obs", "OBSERVATORY", 3 * TILE_SIZE + TILE_SIZE // 2, 3 * TILE_SIZE - 8, CYAN),
        ("exit", "→ FARM", 28 * TILE_SIZE + TILE_SIZE // 2, 19 * TILE_SIZE + TILE_SIZE // 2 - 8, CYAN),
    ]
    for tid, txt, tx, ty, tcol in text_defs:
        if tid not in tc:
            tc[tid] = font_small.render(txt, True, tcol)
        bg.blit(tc[tid], (tx - tc[tid].get_width() // 2, ty - tc[tid].get_height() // 2))
    # House name labels (static)
    house_labels = ["Nova's Home", "Pip's Home", "Luna's Home", "Rex's Home"]
    house_positions = [(5, 14), (9, 14), (19, 14), (25, 14)]
    for i, (hx, hy) in enumerate(house_positions):
        hid = f"house_{i}"
        if hid not in tc:
            tc[hid] = font_small.render(house_labels[i], True, WHITE)
        lbl = tc[hid]
        bg.blit(lbl, ((hx + 1) * TILE_SIZE - lbl.get_width() // 2, (hy - 1) * TILE_SIZE - lbl.get_height() // 2))
    # Shop sign background (static)
    sign_y = 2 * TILE_SIZE - 28
    sign_cx = 11 * TILE_SIZE
    draw_box(bg, sign_cx - 60, sign_y, 120, 20, (60, 40, 80), True)
    draw_box(bg, sign_cx - 2, sign_y + 20, 4, 8, (80, 60, 100), True)
    sign_cx = 18 * TILE_SIZE
    draw_box(bg, sign_cx - 60, sign_y, 120, 20, (50, 20, 20), True)
    draw_box(bg, sign_cx - 2, sign_y + 20, 4, 8, (70, 30, 30), True)
    SPACEPORT_BG_CACHE[key] = bg
    return bg

def maybe_draw_deco(col, row, draw_x, draw_y, chance=0.12):
    h = (col * 17 + row * 31) % 100
    if h < chance * 100:
        idx = (col * 11 + row * 7) % len(DECO_TYPES)
        screen.blit(get_decoration_surf(DECO_TYPES[idx]), (draw_x, draw_y))

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

    # Parallax background layer — distant mountain silhouettes
    mount_color = blend_colors((30, 25, 50), sky_color, 0.3)
    peaks = [(0, SCREEN_HEIGHT), (0, 80), (60, 60), (120, 90), (180, 40), (240, 70),
             (300, 50), (360, 85), (420, 35), (480, 65), (540, 45), (600, 75),
             (660, 55), (720, 80), (780, 40), (840, 70), (900, 60), (960, 80),
             (960, SCREEN_HEIGHT)]
    pygame.draw.polygon(screen, mount_color, peaks)
    # Second parallax layer — closer hills
    hill_color = blend_colors((40, 35, 60), sky_color, 0.2)
    hills = [(0, SCREEN_HEIGHT), (0, 120), (80, 100), (160, 130), (240, 95), (320, 115),
             (400, 105), (480, 120), (560, 100), (640, 110), (720, 95), (800, 125),
             (880, 105), (960, 115), (960, SCREEN_HEIGHT)]
    pygame.draw.polygon(screen, hill_color, hills)

    ground_y = 3 * TILE_SIZE
    off_x = game.farm_off_x
    off_y = game.farm_off_y
    f_cols = game.farm_cols
    f_rows = game.farm_rows
    anim = game.anim_frame
    for row in range(ground_y // TILE_SIZE, FARM_TILES_Y):
        for col in range(FARM_TILES_X):
            draw_x = col * TILE_SIZE
            draw_y = row * TILE_SIZE
            if off_y <= row < off_y + f_rows and off_x <= col < off_x + f_cols:
                tile = game.tiles[row - off_y][col - off_x]
                if tile.soil_state == "watered":
                    screen.blit(get_tile_surf("watered", tile_variant(col, row, 3), season_name), (draw_x, draw_y))
                    # Animated water shimmer
                    shimmer = make_surface(TILE_SIZE, TILE_SIZE)
                    shimmer.set_alpha(20 + anim * 10)
                    shimmer.fill((80, 160, 255))
                    screen.blit(shimmer, (draw_x, draw_y))
                elif tile.soil_state == "tilled":
                    screen.blit(get_tile_surf("tilled", tile_variant(col, row, 3), season_name), (draw_x, draw_y))
                else:
                    screen.blit(get_tile_surf("untilled", tile_variant(col, row, 3), season_name), (draw_x, draw_y))
                if tile.crop:
                    data = CROP_TYPES.get(tile.crop_type)
                    if data:
                        stages = data["growth_stages"]
                        cs = get_crop_surf(tile.crop_type, tile.crop_stage, stages)
                        # Slight crop rustle animation
                        rustle_y = 1 if anim == 0 else 0
                        screen.blit(cs, (draw_x, draw_y + rustle_y))
                        if tile.watered:
                            wd = make_surface(TILE_SIZE, TILE_SIZE)
                            wd.set_alpha(100)
                            for _ in range(3):
                                wx, wy = random.randint(0, TILE_SIZE - 1), random.randint(0, TILE_SIZE - 1)
                                set_pixel(wd, wx, wy, (150, 200, 255))
                            screen.blit(wd, (draw_x, draw_y))
            elif row == off_y and (col < off_x or col >= off_x + f_cols):
                screen.blit(get_tile_surf("grass", tile_variant(col, row, 4), season_name), (draw_x, draw_y))
                maybe_draw_deco(col, row, draw_x, draw_y)
            elif row >= off_y + f_rows:
                screen.blit(get_tile_surf("grass", tile_variant(col, row, 4), season_name), (draw_x, draw_y))
                maybe_draw_deco(col, row, draw_x, draw_y)
            elif row < off_y:
                screen.blit(get_tile_surf("grass", tile_variant(col, row, 4), season_name), (draw_x, draw_y))
                maybe_draw_deco(col, row, draw_x, draw_y)

    # Fireflies at night
    if game.time_slot >= 4:
        t = pygame.time.get_ticks()
        for i in range(8):
            fx = (int(t * 0.015 + i * 97) % (FARM_TILES_X * TILE_SIZE))
            fy = (int(t * 0.012 + i * 113) % (FARM_TILES_Y * TILE_SIZE))
            glow = int(160 + 95 * math.sin(t * 0.004 + i * 2.1))
            pygame.draw.circle(screen, (glow, glow, 100), (fx, fy), 2)
            if glow > 200:
                pygame.draw.circle(screen, (255, 255, 180), (fx, fy), 1)

    screen.blit(get_prop_surf("lamp_post"), (6 * TILE_SIZE, 2 * TILE_SIZE))
    player_house = get_building_v2("player_house", game.anim_frame)
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
        screen.blit(get_tile_surf("path", tile_variant(path_exit_x, path_exit_y, 4), season_name), (ex, ey))
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
        bs = get_building_v2(b["type"], game.anim_frame)
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
    player_surf = get_astronaut_animated(game.player.direction, game.anim_state, game.player_anim_frame)
    screen.blit(player_surf, (game.player.x, game.player.y))

    # Tree decorations (seasonal colors)
    tree_leaf_palettes = {
        "Nebula": [(50, 160, 60), (40, 140, 50), (70, 190, 80), (90, 210, 90)],
        "Void": [(80, 60, 140), (70, 50, 120), (90, 70, 150), (60, 40, 110)],
        "Bloom": [(80, 200, 80), (100, 220, 100), (60, 180, 60), (120, 240, 120)],
        "Solar": [(180, 160, 40), (200, 140, 30), (160, 180, 50), (220, 120, 20)],
    }
    tree_outline_palettes = {
        "Nebula": (30, 100, 40),
        "Void": (50, 35, 90),
        "Bloom": (40, 130, 40),
        "Solar": (100, 90, 20),
    }
    leaf_palette = tree_leaf_palettes.get(season_name, tree_leaf_palettes["Nebula"])
    outline_color = tree_outline_palettes.get(season_name, tree_outline_palettes["Nebula"])
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
                    leaf_color = leaf_palette[random.randint(0, 3)]
                    set_pixel(t_surf, px, py, leaf_color)
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

    # Parallax background — distant city/infrastructure silhouettes
    mount_color = blend_colors((25, 20, 45), sky_color, 0.3)
    peaks = [(0, SCREEN_HEIGHT), (0, 90), (80, 70), (160, 100), (240, 60), (320, 85),
             (400, 55), (480, 75), (560, 45), (640, 80), (720, 50), (800, 70),
             (880, 65), (960, 85), (960, SCREEN_HEIGHT)]
    pygame.draw.polygon(screen, mount_color, peaks)
    hill_color = blend_colors((35, 30, 55), sky_color, 0.2)
    hills = [(0, SCREEN_HEIGHT), (0, 110), (100, 95), (200, 120), (300, 90), (400, 105),
             (500, 85), (600, 100), (700, 80), (800, 110), (900, 95), (960, 105),
             (960, SCREEN_HEIGHT)]
    pygame.draw.polygon(screen, hill_color, hills)

    for row in range(SPACEPORT_TILES_Y):
        for col in range(SPACEPORT_TILES_X):
            draw_x = col * TILE_SIZE
            draw_y = row * TILE_SIZE
            screen.blit(get_tile_surf("grass", tile_variant(col, row, 4), season_name), (draw_x, draw_y))
            maybe_draw_deco(col, row, draw_x, draw_y, 0.08)

    # Cached static background (landing pad, pier planks, paths, text labels, sign bases)
    screen.blit(_build_spaceport_bg(season_name), (0, 0))

    # Fishing pier animated water
    t = pygame.time.get_ticks()
    if "pier_surf" not in SPACEPORT_BG_CACHE:
        SPACEPORT_BG_CACHE["pier_surf"] = pygame.Surface((5 * TILE_SIZE, 5 * TILE_SIZE))
    pier_surf = SPACEPORT_BG_CACHE["pier_surf"]
    for wx in range(5):
        for wy in range(5):
            shade = 90 + ((wx + wy) % 2) * 20 + int(10 * math.sin(t / 400.0 + wx + 25 + wy + 8))
            c = (20, 70, max(60, min(150, shade + 40)))
            pier_surf.fill(c, (wx * TILE_SIZE, wy * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    screen.blit(pier_surf, (25 * TILE_SIZE, 8 * TILE_SIZE))

    # Decorative props (drawn behind buildings)
    screen.blit(get_prop_surf("lamp_post"), (8 * TILE_SIZE, 1 * TILE_SIZE))
    screen.blit(get_prop_surf("lamp_post"), (21 * TILE_SIZE, 1 * TILE_SIZE))
    screen.blit(get_prop_surf("bench"), (12 * TILE_SIZE, 1 * TILE_SIZE))
    screen.blit(get_prop_surf("bench"), (18 * TILE_SIZE, 1 * TILE_SIZE))
    screen.blit(get_prop_surf("planter"), (6 * TILE_SIZE, 6 * TILE_SIZE))
    screen.blit(get_prop_surf("planter"), (23 * TILE_SIZE, 6 * TILE_SIZE))
    screen.blit(get_prop_surf("crate"), (4 * TILE_SIZE, 5 * TILE_SIZE))
    screen.blit(get_prop_surf("crate"), (25 * TILE_SIZE, 15 * TILE_SIZE))
    screen.blit(get_prop_surf("signpost"), (14 * TILE_SIZE, 12 * TILE_SIZE))

    # Buildings (clean cached base + per-frame effect overlays)
    t = pygame.time.get_ticks()
    # Shop
    shop_key = "building_clean_shop"
    if shop_key not in SPACEPORT_BG_CACHE:
        SPACEPORT_BG_CACHE[shop_key] = get_clean_building("shop")
    screen.blit(SPACEPORT_BG_CACHE[shop_key], (8 * TILE_SIZE, 2 * TILE_SIZE))
    # Shop effects: smoke + window glow (on a temp overlay instead of screen.set_at)
    shop_overlay_key = "shop_effects_overlay"
    if shop_overlay_key not in SPACEPORT_BG_CACHE:
        SPACEPORT_BG_CACHE[shop_overlay_key] = pygame.Surface((96, 96), pygame.SRCALPHA)
    shop_o = SPACEPORT_BG_CACHE[shop_overlay_key]
    shop_o.fill((0, 0, 0, 0))
    smoke_y = 4 + (t // 200) % 8
    smoke_x = 26 + ((t // 300) % 5 - 2)
    shop_o.set_at((smoke_x, smoke_y), (180, 180, 190))
    shop_o.set_at((smoke_x + 1, smoke_y - 1), (160, 160, 170))
    for gx in [16, 26, 64, 78]:
        for gy in [36, 44, 52]:
            shop_o.set_at((gx, gy), (255, 240, 200))
            shop_o.set_at((gx + 1, gy), (255, 240, 180))
    screen.blit(shop_o, (8 * TILE_SIZE, 2 * TILE_SIZE))
    # Shop sign neon border
    sign_y = 2 * TILE_SIZE - 28
    sign_cx = 11 * TILE_SIZE
    neon_glow = 0.5 + 0.5 * math.sin(t * 0.003)
    border_bright = (int(140 + 60 * neon_glow), int(100 + 80 * neon_glow), int(180 + 40 * neon_glow))
    pygame.draw.rect(screen, border_bright, (sign_cx - 60, sign_y, 120, 20), 3)

    # Bar
    bar_key = "building_clean_bar"
    if bar_key not in SPACEPORT_BG_CACHE:
        SPACEPORT_BG_CACHE[bar_key] = get_clean_building("bar")
    screen.blit(SPACEPORT_BG_CACHE[bar_key], (15 * TILE_SIZE, 2 * TILE_SIZE))
    # Bar effects: neon strip (on temp overlay)
    bar_o_key = "bar_effects_overlay"
    if bar_o_key not in SPACEPORT_BG_CACHE:
        SPACEPORT_BG_CACHE[bar_o_key] = pygame.Surface((96, 96), pygame.SRCALPHA)
    bar_o = SPACEPORT_BG_CACHE[bar_o_key]
    bar_o.fill((0, 0, 0, 0))
    nr = int(200 + 55 * (0.5 + 0.5 * math.sin(t * 0.005)))
    ng = int(60 + 40 * (0.5 + 0.5 * math.sin(t * 0.005)))
    nb = int(100 + 80 * (0.5 + 0.5 * math.sin(t * 0.005)))
    for i in range(8):
        nx = 22 + i * 6
        for ny in range(14, 17):
            bar_o.set_at((nx, ny), (nr, ng, nb))
    screen.blit(bar_o, (15 * TILE_SIZE, 2 * TILE_SIZE))
    # Bar sign neon border
    sign_cx = 18 * TILE_SIZE
    bar_border = (int(180 + 60 * neon_glow), int(80 + 40 * neon_glow), int(120 + 80 * neon_glow))
    pygame.draw.rect(screen, bar_border, (sign_cx - 60, sign_y, 120, 20), 2)

    # Houses
    house_key = "building_clean_house"
    if house_key not in SPACEPORT_BG_CACHE:
        SPACEPORT_BG_CACHE[house_key] = get_clean_building("house")
    house_positions = [(5, 14), (9, 14), (19, 14), (25, 14)]
    for i, (hx, hy) in enumerate(house_positions):
        screen.blit(SPACEPORT_BG_CACHE[house_key], (hx * TILE_SIZE, hy * TILE_SIZE))
        # House effects: window glow
        glow = 200 + int(40 * math.sin(t * 0.003))
        win_color = (glow, glow, 255)
        pygame.draw.rect(screen, win_color, (hx * TILE_SIZE + 10, hy * TILE_SIZE + 14, 6, 6))
        pygame.draw.rect(screen, win_color, (hx * TILE_SIZE + 80, hy * TILE_SIZE + 14, 6, 6))
        # Door (cached)
        door_key = f"door_{i}"
        if door_key not in SPACEPORT_BG_CACHE:
            door_surf = make_surface(8, 12)
            draw_box(door_surf, 0, 0, 8, 12, (100, 80, 60), True)
            draw_box(door_surf, 2, 0, 4, 12, (80, 60, 40), True)
            SPACEPORT_BG_CACHE[door_key] = door_surf
        door_x = (hx + 1) * TILE_SIZE - 4
        door_y = (hy + 2) * TILE_SIZE - 8
        screen.blit(SPACEPORT_BG_CACHE[door_key], (door_x, door_y))

    # Quest board signpost (tile 6, 10)
    qb_x, qb_y = 6 * TILE_SIZE, 10 * TILE_SIZE
    pygame.draw.rect(screen, (70, 50, 30), (qb_x - 6, qb_y - 20, TILE_SIZE + 12, 24))
    pygame.draw.rect(screen, (160, 120, 70), (qb_x - 6, qb_y - 20, TILE_SIZE + 12, 24), 2)
    draw_text(screen, "QUESTS", qb_x + TILE_SIZE // 2, qb_y - 8, GOLD, font_small, center=True)
    pygame.draw.rect(screen, (90, 70, 50), (qb_x + TILE_SIZE // 2 - 2, qb_y + 4, 4, 12))

    # Spaceport Observatory (tile 3, 3) — flavor unlocks at Legend rank
    ob_unlocked = game.get_rank() >= 5
    ob_cx = 3 * TILE_SIZE + TILE_SIZE // 2
    ob_cy = 3 * TILE_SIZE + TILE_SIZE // 2
    dome_c = (120, 160, 220) if ob_unlocked else (70, 70, 90)
    pygame.draw.rect(screen, (60, 60, 80), (3 * TILE_SIZE, 3 * TILE_SIZE + TILE_SIZE // 2, TILE_SIZE, TILE_SIZE // 2))
    pygame.draw.circle(screen, dome_c, (ob_cx, ob_cy), 15)
    draw_text(screen, "OBSERVATORY" if ob_unlocked else "Observatory (locked)",
              ob_cx, 3 * TILE_SIZE - 8, CYAN if ob_unlocked else GRAY, font_small, center=True)

    # Traveling Merchant Cosmo (tile 5, 8) when visiting
    if game.merchant_present:
        cx, cy = 5 * TILE_SIZE, 8 * TILE_SIZE
        cosmo = get_npc_v2("cosmo", (200, 160, 80), (120, 80, 40))
        screen.blit(cosmo, (cx, cy - TILE_SIZE))
        draw_text(screen, "Cosmo (Merchant)", cx + TILE_SIZE // 2, cy - TILE_SIZE - 8, GOLD, font_small, center=True)

    # NPC location markers (visible from afar)
    for npc in game.npcs:
        mx = npc.tile_x * TILE_SIZE + int(npc.pixel_offset_x) + TILE_SIZE // 2
        my = npc.tile_y * TILE_SIZE + int(npc.pixel_offset_y)
        pygame.draw.circle(screen, npc.color, (mx, my), 5)
        pygame.draw.circle(screen, WHITE, (mx, my), 5, 1)

    # NPC Sprites with nameplates + heart level
    for npc in game.npcs:
        ns = get_npc_v2(npc.id, npc.color, npc.color2)
        nx = npc.tile_x * TILE_SIZE + int(npc.pixel_offset_x)
        ny = npc.tile_y * TILE_SIZE + int(npc.pixel_offset_y) - TILE_SIZE
        screen.blit(ns, (nx, ny))
        # Nameplate background (cached per NPC)
        npc_key = f"nameplate_{npc.id}"
        if npc_key not in SPACEPORT_BG_CACHE:
            name_w = len(npc.name) * 8 + 8
            name_bg = pygame.Surface((name_w, 14))
            name_bg.set_alpha(160)
            name_bg.fill((10, 10, 30))
            SPACEPORT_BG_CACHE[npc_key] = (name_bg, name_w, font_small.render(npc.name, True, npc.color))
        nb, nw, name_surf = SPACEPORT_BG_CACHE[npc_key]
        screen.blit(nb, (nx + TILE_SIZE // 2 - nw // 2, ny - 8))
        screen.blit(name_surf, (nx + TILE_SIZE // 2 - name_surf.get_width() // 2, ny - 8))
        # Heart level indicator
        if npc.heart_level > 0:
            h_color = PINK if npc.heart_level >= 7 else RED if npc.heart_level >= 4 else (200, 100, 100)
            heart_str = "♥" * min(npc.heart_level, 5) + ("+" if npc.heart_level > 5 else "")
            draw_text(screen, heart_str, nx + TILE_SIZE // 2, ny + TILE_SIZE - 4, h_color, font_tiny, center=True)

    # Floating space dust particles
    t = pygame.time.get_ticks()
    for i in range(12):
        dx = (int(t * 0.02 + i * 137) % (SPACEPORT_TILES_X * TILE_SIZE))
        dy = (int(t * 0.01 + i * 89) % (SPACEPORT_TILES_Y * TILE_SIZE))
        brightness = 128 + int(64 * math.sin(t * 0.003 + i))
        screen.set_at((dx, dy), (brightness, brightness, brightness + 40))

    # Alien decorations (cached)
    for ax, ay in [(3, 10), (10, 16), (23, 3), (28, 16), (2, 18)]:
        if ax < SPACEPORT_TILES_X and ay < SPACEPORT_TILES_Y:
            deco_key = f"alien_deco_{ax}_{ay}"
            if deco_key not in SPACEPORT_BG_CACHE:
                deco = make_surface(TILE_SIZE, TILE_SIZE)
                for _ in range(8):
                    dx, dy = random.randint(0, TILE_SIZE - 1), random.randint(0, TILE_SIZE - 1)
                    set_pixel(deco, dx, dy, (180, 100, 255))
                SPACEPORT_BG_CACHE[deco_key] = deco
            screen.blit(SPACEPORT_BG_CACHE[deco_key], (ax * TILE_SIZE, ay * TILE_SIZE))

    # Exit sign
    ex, ey = 28 * TILE_SIZE, 19 * TILE_SIZE
    screen.blit(get_tile_surf("path", tile_variant(28, 19, 4), season_name), (ex, ey))
    draw_text(screen, "-> FARM", ex + TILE_SIZE // 2, ey + TILE_SIZE // 2 - 8, CYAN, font_small, center=True)

    # Facing tile highlight
    ftx, fty = game.player.get_facing_tile()
    if 0 <= ftx < SPACEPORT_TILES_X and 0 <= fty < SPACEPORT_TILES_Y:
        hl = pygame.Surface((TILE_SIZE, TILE_SIZE))
        hl.set_alpha(50)
        hl.fill((255, 255, 255))
        screen.blit(hl, (ftx * TILE_SIZE, fty * TILE_SIZE))

    # Player
    player_surf = get_astronaut_animated(game.player.direction, game.anim_state, game.player_anim_frame)
    screen.blit(player_surf, (game.player.x, game.player.y))
