"""Keyboard/event input handling, split out of the main loop.

`handle_keydown` dispatches a KEYDOWN event: first the global help toggle,
then the active modal overlay's handler (each consumes the event), then the
non-modal global key handler. `handle_movement` processes held movement keys.
"""
from src.ui.context import *


# --- Modal overlay handlers (each fully consumes the KEYDOWN event) ---

def handle_festival_keydown(event):
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
            return
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


def handle_seed_select_keydown(event):
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


def handle_shop_keydown(event):
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
    artisan_keys = [pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_u, pygame.K_o]
    ai = 0
    for rk, recipe in ARTISAN_RECIPES.items():
        if game.player.inventory.get(recipe["name"], 0) <= 0:
            continue
        if ai < len(artisan_keys) and event.key == artisan_keys[ai]:
            game.sell_dish(recipe["name"], qty)
        ai += 1
    fish_keys = [pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0, pygame.K_a, pygame.K_i]
    fi = 0
    for fid in FISH_ORDER:
        if game.player.inventory.get(fid, 0) <= 0:
            continue
        if fi < len(fish_keys) and event.key == fish_keys[fi]:
            game.sell_fish(fid, qty)
        fi += 1


def handle_bar_keydown(event):
    if event.key == pygame.K_ESCAPE:
        game.bar_active = False
        game.subscreen = None
    qty = 10 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
    for i in range(len(BAR_ITEMS)):
        if event.key == getattr(pygame, f"K_{i+1}"):
            game.buy_bar_item(i, qty)


def handle_bot_shop_keydown(event):
    if event.key == pygame.K_ESCAPE:
        game.bot_shop_active = False
    bot_keys = list(BOT_TYPES.keys())
    for i, bk in enumerate(bot_keys):
        if event.key == getattr(pygame, f"K_{i+1}"):
            game.buy_bot(bk)


def handle_hangar_keydown(event):
    if event.key == pygame.K_ESCAPE:
        game.hangar_active = False
    elif event.key == pygame.K_u:
        game.upgrade_ship()
    elif event.key == pygame.K_r:
        game.refuel_ship()
    for i in range(len(PLANETS)):
        if event.key == getattr(pygame, f"K_{i+1}"):
            game.launch_to_planet(i)


def handle_planet_keydown(event):
    if event.key == pygame.K_SPACE:
        game.scan_planet()
    elif event.key == pygame.K_e:
        game.return_from_planet()


def handle_inventory_keydown(event):
    if event.key == pygame.K_i:
        game.inventory_active = False


def handle_dialogue_keydown(event):
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


def handle_sleep_keydown(event):
    if event.key == pygame.K_y:
        game.advance_day()
        game.sleep_prompt = False
        game.player.x = game.player.farm_x
        game.player.y = game.player.farm_y
        game.player.current_map = "farm"
        game.set_message("Good morning! A new day on the farm!")
    elif event.key == pygame.K_n:
        game.sleep_prompt = False


def handle_save_menu_keydown(event):
    if event.key == pygame.K_ESCAPE:
        game.save_menu_active = False
    elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
        slot = event.key - pygame.K_1
        game.save_game(slot)
        game.save_menu_slot = slot
        game.save_menu_active = False
    elif event.key == pygame.K_RETURN:
        game.save_game(game.save_menu_slot)
        game.save_menu_active = False
    elif event.key == pygame.K_UP:
        game.save_menu_slot = max(0, game.save_menu_slot - 1)
    elif event.key == pygame.K_DOWN:
        game.save_menu_slot = min(SAVE_SLOT_COUNT - 1, game.save_menu_slot + 1)
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


def handle_cooking_keydown(event):
    if event.key == pygame.K_ESCAPE:
        game.cooking_active = False
    else:
        qty = 10 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
        available = [rk for rk in RECIPES if all(game.player.inventory.get(ing, 0) >= need * qty for ing, need in RECIPES[rk]["ingredients"].items())]
        for i in range(len(available)):
            if event.key == getattr(pygame, f"K_{i+1}"):
                game.cook_recipe(available[i], qty)
                game.cooking_active = False


def handle_crafting_keydown(event):
    if event.key == pygame.K_ESCAPE:
        game.crafting_active = False
    else:
        qty = 10 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
        recipe_keys = list(ARTISAN_RECIPES.keys())
        for i, rk in enumerate(recipe_keys):
            if event.key == getattr(pygame, f"K_{i+1}", None):
                game.start_crafting(rk, qty)


def handle_expand_keydown(event):
    if event.key == pygame.K_ESCAPE:
        game.expand_menu_active = False
    elif event.key == pygame.K_e:
        game.buy_expansion()
        game.expand_menu_active = False


def handle_building_shop_keydown(event):
    if event.key == pygame.K_ESCAPE:
        game.building_shop_active = False
    else:
        bk = list(BUILDING_TYPES.keys())
        for i, btype in enumerate(bk):
            if event.key == getattr(pygame, f"K_{i+1}"):
                game.buy_building(btype)


def handle_pet_shop_keydown(event):
    if event.key == pygame.K_ESCAPE:
        game.pet_shop_active = False
    else:
        ak = list(ANIMAL_TYPES.keys())
        for i, aid in enumerate(ak):
            if event.key == getattr(pygame, f"K_{i+1}"):
                game.buy_animal(aid)


def handle_barn_keydown(event):
    if event.key == pygame.K_ESCAPE:
        game.barn_overlay_active = False


def handle_fishing_keydown(event):
    if event.key == pygame.K_ESCAPE:
        game.exit_fishing()
        return
    if event.key == pygame.K_SPACE:
        st = game.fishing_state
        if st == "casting":
            game.cast_line()
        elif st == "hooked":
            game.hook_fish()
        elif st == "reeling":
            game.reel_press()
        elif st == "caught":
            game.fishing_caught_fish = None
            game.fishing_state = "casting"
            game.set_message("Cast again (SPACE) or leave (ESC).")


def handle_shipping_bin_keydown(event):
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


# --- Fall-through placement handlers: consume only ESC / E, else let the
#     event reach the global handler (so the player can still move the ghost). ---

def handle_placement_keydown(event):
    """Return True if the event was consumed."""
    if event.key == pygame.K_ESCAPE:
        game.placement_mode = None
        game.set_message("Bot placement cancelled.")
        return True
    elif event.key == pygame.K_e:
        game.place_bot()
        return True
    return False


def handle_build_keydown(event):
    """Return True if the event was consumed."""
    if event.key == pygame.K_ESCAPE:
        game.build_mode = None
        game.set_message("Building placement cancelled.")
        return True
    elif event.key == pygame.K_e:
        game.place_building()
        return True
    return False


# Active-flag -> handler, in original priority order. Each consumes the event.
def _modal_handlers():
    return [
        (game.festival_active, handle_festival_keydown),
        (game.seed_select_active, handle_seed_select_keydown),
        (game.shop_active, handle_shop_keydown),
        (game.bar_active, handle_bar_keydown),
        (game.bot_shop_active, handle_bot_shop_keydown),
        (game.hangar_active, handle_hangar_keydown),
        (game.planet_explore_active, handle_planet_keydown),
        (game.inventory_active, handle_inventory_keydown),
        (game.dialogue_active, handle_dialogue_keydown),
        (game.sleep_prompt, handle_sleep_keydown),
    ]


def _modal_handlers_late():
    return [
        (game.save_menu_active, handle_save_menu_keydown),
        (game.cooking_active, handle_cooking_keydown),
        (game.crafting_active, handle_crafting_keydown),
        (game.expand_menu_active, handle_expand_keydown),
        (game.building_shop_active, handle_building_shop_keydown),
        (game.pet_shop_active, handle_pet_shop_keydown),
        (game.barn_overlay_active, handle_barn_keydown),
        (game.fishing_active, handle_fishing_keydown),
        (game.subscreen == "shipping_bin", handle_shipping_bin_keydown),
    ]


def handle_keydown(event):
    if event.unicode == '?':
        game.help_active = not game.help_active
        return
    for active, handler in _modal_handlers():
        if active:
            handler(event)
            return
    # Placement/build only consume ESC and E; other keys fall through to global.
    if game.placement_mode and handle_placement_keydown(event):
        return
    if game.build_mode and handle_build_keydown(event):
        return
    for active, handler in _modal_handlers_late():
        if active:
            handler(event)
            return
    handle_global_keydown(event)


def handle_global_keydown(event):
    if event.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
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
        elif game.player.current_map == "farm":
            game.crafting_active = True
    elif event.key == pygame.K_s:
        if not game.save_menu_active:
            game.save_menu_active = True


def _movement_blocked():
    return (game.dialogue_active or game.shop_active or game.bot_shop_active or game.hangar_active
            or game.planet_explore_active or game.seed_select_active or game.inventory_active
            or game.sleep_prompt or game.bar_active or game.festival_active or game.save_menu_active
            or game.skills_active or game.cooking_active or game.crafting_active or game.expand_menu_active
            or game.building_shop_active or game.subscreen == "shipping_bin" or game.pet_shop_active
            or game.barn_overlay_active or game.fishing_active)


def handle_movement():
    keys = pygame.key.get_pressed()
    if _movement_blocked():
        return
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


def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.running = False
            return
        if event.type == pygame.KEYDOWN:
            handle_keydown(event)
    handle_movement()
