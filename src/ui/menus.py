from src.ui.context import *

def draw_help():
    if not game.help_active:
        return
    draw_overlay_backdrop()
    panel_w, panel_h = 720, 440
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
            ("V", "Artisan Workshop (farm)"),
            ("C", "Kitchen (farm)"),
            ("E near bar", "Bar menu"),
            ("E on Zoop", "Pet Shop (spaceport)"),
            ("E on Barn", "Barn overlay (farm)"),
            ("G", "Gift mode (spaceport)"),
            ("U / R", "Upgrade / Refuel (hangar)"),
            ("E on signpost", "Expand farm"),
        ]),
    ]

    col_l = px + 20
    col_r = px + 380
    key_w = 110
    lh = 15

    def draw_section(col_x, sections, y_start):
        y = y_start
        for sname, items in sections:
            draw_text(screen, f"-- {sname} --", col_x, y, CYAN, font_tiny)
            y += 16
            for key, desc in items:
                draw_text(screen, key, col_x + 10, y, GOLD, font_tiny)
                draw_text(screen, desc, col_x + 10 + key_w, y, WHITE, font_tiny)
                y += lh
            y += 4
        return y

    sy = py + 44
    left_end = draw_section(col_l, left_sections, sy)
    right_end = draw_section(col_r, right_sections, sy)

    tips_y = max(left_end, right_end) + 10
    draw_text(screen, "-- TIPS --", col_l, tips_y, CYAN, font_tiny)
    draw_text(screen, "E near landing pad: Enter festival  |  Ctrl+Q: Quit", col_l + 10, tips_y + 16, LIGHT_GRAY, font_tiny)
    draw_text(screen, "Weather & seasons affect crop growth  |  Nebula > Bloom > Solar > Void", col_l + 10, tips_y + 30, LIGHT_GRAY, font_tiny)

def draw_save_menu():
    if not game.save_menu_active:
        return
    draw_overlay_backdrop()
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
    draw_text(screen, "↑↓: Select  |  ENTER: Save  |  L+1-3: Load  |  ESC: Close", px + panel_w // 2, py + panel_h - 25, LIGHT_GRAY, font_small, center=True)

def draw_skills():
    if not game.skills_active:
        return
    draw_overlay_backdrop()
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
