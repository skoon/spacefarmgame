from src.ui.context import *
from src.ui.hud import *
from src.ui.world_view import *
from src.ui.overlays import *
from src.ui.minigames import *
from src.ui.menus import *
from src.ui.input import handle_events


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

        if game.message_timer > 0:
            game.message_timer -= 1

        render()
        pygame.display.flip()
        clock.tick(FPS)

    game.save_game(game.save_menu_slot)
    pygame.quit()
    sys.exit()
