from src.ui.context import game
from src.ui.loop import main
from src.sprites import load_outside_tileset, load_scifi_creatures

# Bootstrap: load slot 0 if present, otherwise seed a fresh game.
load_outside_tileset()
load_scifi_creatures()
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

if __name__ == "__main__":
    main()
