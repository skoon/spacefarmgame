from src.ui.context import *
from src.ui.hud import *
from src.ui.world_view import *
from src.ui.overlays import *
from src.ui.minigames import *
from src.ui.menus import *
from src.ui.input import handle_events


def render():
    shake_off_x = 0
    shake_off_y = 0
    if game.screen_shake > 0:
        shake_off_x = random.randint(-game.screen_shake_intensity, game.screen_shake_intensity)
        shake_off_y = random.randint(-game.screen_shake_intensity, game.screen_shake_intensity)
        game.screen_shake -= 1

    if shake_off_x != 0 or shake_off_y != 0:
        offscreen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        offscreen.blit(screen, (0, 0))
        screen.fill(BLACK)
        screen.blit(offscreen, (shake_off_x, shake_off_y))

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

    if game.screen_flash > 0:
        flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        flash.set_alpha(80)
        flash.fill(game.screen_flash_color)
        screen.blit(flash, (0, 0))
        game.screen_flash -= 1

    if game.current_weather["name"] == "Void Fog":
        fog = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fog.set_alpha(60)
        fog.fill((60, 40, 80))
        screen.blit(fog, (0, 0))

    if game.transition_active:
        p = game.transition_progress
        if p < 0.5:
            wipe_w = int(SCREEN_WIDTH * (p * 2))
        else:
            wipe_w = int(SCREEN_WIDTH * ((1.0 - p) * 2))
        wipe = pygame.Surface((wipe_w, SCREEN_HEIGHT))
        wipe.fill((5, 5, 20))
        screen.blit(wipe, (0, 0))

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
    if game.crafting_active:
        draw_crafting()
    if game.expand_menu_active:
        draw_expand_menu()
    if game.building_shop_active:
        draw_building_shop()
    if game.subscreen == "shipping_bin":
        draw_shipping_bin()
    if game.pet_shop_active:
        draw_pet_shop()
    if game.barn_overlay_active:
        draw_barn_overlay()
    if game.fishing_active:
        draw_fishing()
    if game.quest_board_active:
        draw_quest_board()
    if game.merchant_shop_active:
        draw_merchant_shop()
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
        game.update_fishing()

        if game.overlay_alpha < game.overlay_target_alpha:
            game.overlay_alpha = min(game.overlay_alpha + 15, game.overlay_target_alpha)
        elif game.overlay_alpha > game.overlay_target_alpha:
            game.overlay_alpha = max(game.overlay_alpha - 15, game.overlay_target_alpha)

        game.update_transition()

        game.anim_timer += 1
        if game.anim_timer >= 8:
            game.anim_timer = 0
            game.anim_frame = (game.anim_frame + 1) % 2

        if game.tool_use_timer > 0:
            game.tool_use_timer -= 1
            if game.tool_use_timer == 0:
                game.anim_state = "idle"

        game.player_anim_timer += 1
        if game.anim_state == "walk":
            threshold = 6
        elif game.anim_state == "idle":
            threshold = 12
        else:
            threshold = 999
        if game.player_anim_timer >= threshold:
            game.player_anim_timer = 0
            if game.anim_state == "walk":
                game.player_anim_frame = (game.player_anim_frame + 1) % 4
            elif game.anim_state == "idle":
                game.player_anim_frame = (game.player_anim_frame + 1) % 2

        if game.message_timer > 0:
            game.message_timer -= 1

        render()
        pygame.display.flip()
        clock.tick(FPS)

    game.save_game(game.save_menu_slot)
    pygame.quit()
    sys.exit()
