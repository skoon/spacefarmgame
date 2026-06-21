from src.ui.context import *

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
