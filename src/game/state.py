import pygame
import json
import os
import random
import math
from src.constants import *
from src.sprites import *
from src.game.entities import Tile, Player, NPC, FarmBot
from src.game.farming import FarmingMixin
from src.game.exploration import ExplorationMixin
from src.game.buildings import BuildingsMixin
from src.game.animals import AnimalsMixin
from src.game.kitchen import KitchenMixin
from src.game.economy import EconomyMixin
from src.game.social import SocialMixin
from src.game.world_sim import WorldSimMixin
from src.game.progression import ProgressionMixin
from src.game.fishing import FishingMixin
from src.game.reputation import ReputationMixin


class GameState(FarmingMixin, ExplorationMixin, BuildingsMixin, AnimalsMixin, KitchenMixin, EconomyMixin, SocialMixin, WorldSimMixin, ProgressionMixin, FishingMixin, ReputationMixin):
    def __init__(self):
        self.player = Player()
        self.day = 1
        self.time_slot = 0
        self.time_progress = 0.0
        self.tiles = [[Tile(c, r) for c in range(TILLABLE_COLS)] for r in range(TILLABLE_ROWS)]
        self.npcs = [NPC(d) for d in NPC_DEFS]
        self.screen = "farm"
        self.subscreen = None
        self.message = ""
        self.message_timer = 0
        self.dialogue_active = False
        self.dialogue_npc = None
        self.dialogue_lines = []
        self.dialogue_index = 0
        self.shop_active = False
        self.inventory_active = False
        self.seed_select_active = False
        self.selected_seed_index = 0
        self.running = True
        self.camera_x = 0
        self.camera_y = 0
        self.advance_day_pending = False
        self.sleep_prompt = False
        self.stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT // 2)) for _ in range(60)]
        self.active_interact_npc = None
        self.romanceable_npcs = [n for n in self.npcs if n.romanceable]
        self.married_to = None
        self.particles = []
        self.help_active = False
        self.bot_shop_active = False
        self.placement_mode = None
        self.bots = []
        self.upkeep_failed = False
        self.gift_mode = False
        self.bar_active = False
        self.ship_tier = 0
        self.fuel = SHIP_TIERS[0]["fuel_capacity"]
        self.ship_cargo = {}
        self.hangar_active = False
        self.current_planet = None
        self.planet_turns_left = 0
        self.planet_explore_active = False
        self.planet_log = []
        self.season_index = 0
        self.day_in_season = 0
        self.current_weather = WEATHER_EVENTS[0]
        self.weather_timer = random.randint(WEATHER_DURATION["min"], WEATHER_DURATION["max"])
        self.weather_particles = []
        self.festival_today = None
        self.festival_active = False
        self.festival_type = None
        self.festival_data = {}
        self.save_menu_active = False
        self.save_menu_slot = 0
        self.cooking_active = False
        self.crafting_active = False
        self.processing_queue = []  # [{recipe_key, days_remaining, count}]
        self.skills = {"farming": 0, "exploration": 0, "cooking": 0, "social": 0}
        self.skills_active = False

        # Farm Expansion & Buildings
        self.farm_expansion_tier = 0
        self.farm_cols = FARM_EXPANSIONS[0]["cols"]
        self.farm_rows = FARM_EXPANSIONS[0]["rows"]
        self.farm_off_x = FARM_EXPANSIONS[0]["off_x"]
        self.farm_off_y = FARM_EXPANSIONS[0]["off_y"]
        self.buildings = []
        self.build_mode = None
        self.shipping_bin_contents = {}
        self.expand_menu_active = False
        self.building_shop_active = False
        # Animal Husbandry
        self.animals = []
        self.barn_capacity = 4
        self.pet_shop_active = False
        self.barn_overlay_active = False
        # Fishing
        self.fishing_active = False
        self.fishing_state = "idle"
        self.fishing_timer = 0
        self.fishing_bite_window = 0
        self.fishing_progress = 0.0
        self.fishing_current_fish = None
        self.fishing_caught_fish = None
        self.fish_collection = {}
        self.fish_caught_total = 0
        # Town Reputation & Daily Quests
        self.reputation = 0
        self.active_quests = []
        self.completed_quests = 0
        self.quest_board_active = False
        self.merchant_present = False
        self.merchant_shop_active = False
        self.merchant_items = []
        self.merchant_last_visit = -1

    def set_message(self, msg):
        self.message = msg
        self.message_timer = 120

    def advance_time(self, amount=0.25):
        self.time_progress += amount
        while self.time_progress >= 1.0:
            self.time_progress -= 1.0
            self.time_slot += 1
            for npc in self.npcs:
                npc.update_schedule(self.time_slot)
            if self.time_slot >= len(TIME_NAMES):
                self.advance_day()

    def advance_day(self):
        self.day += 1
        self.time_slot = 0
        self.time_progress = 0.0
        self.player.energy = self.player.max_energy
        self.update_weather()
        self.update_season()
        season_name = SEASONS[self.season_index]
        self.festival_today = None
        for key, fest in FESTIVALS.items():
            if fest["season"] == season_name and fest["day"] == self.day_in_season:
                self.festival_today = key
                self.set_message(f"Today: {fest['name']}! Visit the Space Port!")
                break
        for npc in self.npcs:
            npc.talked_today = False
        season_name = SEASONS[self.season_index]
        mod = SEASONAL_MODIFIERS[season_name]["growth_mod"]
        weather_mod = self.current_weather["crop_bonus"]
        growth_rate = mod + weather_mod
        if self.get_skill_level("farming") >= 5:
            growth_rate *= 1.25
        # Check which map tiles are inside a greenhouse
        greenhouse_tiles = set()
        for b in self.buildings:
            if b["type"] == "greenhouse":
                g_tx = b["tile_x"]
                g_ty = b["tile_y"]
                for dy in range(3):
                    for dx in range(4):
                        greenhouse_tiles.add((g_tx + dx, g_ty + dy))
        for row in self.tiles:
            for tile in row:
                map_tx = tile.x + self.farm_off_x
                map_ty = tile.y + self.farm_off_y
                in_greenhouse = (map_tx, map_ty) in greenhouse_tiles
                if in_greenhouse:
                    tile.grow(1.0)
                else:
                    tile.grow(growth_rate)
                tile.watered = False
                if tile.soil_state == "watered":
                    tile.soil_state = "tilled"
        self.feed_animals()
        self.produce_animals()
        self.process_crafting()
        self.set_message(f"Day {self.day} - {TIME_NAMES[0]} ({SEASONS[self.season_index]}, {self.current_weather['name']})")
        self.process_shipping_bin()
        self.apply_buildings()
        self.run_bots()
        self.generate_daily_quests()
        self.update_merchant()

    def save_game(self, slot=0):
        data = {
            "day": self.day,
            "time_slot": self.time_slot,
            "time_progress": self.time_progress,
            "gold": self.player.gold,
            "energy": self.player.energy,
            "inventory": self.player.inventory,
            "seed_inventory": self.player.seed_inventory,
            "tiles": [
                {"soil": t.soil_state, "crop": t.crop_type, "stage": t.crop_stage,
                 "timer": t.crop_timer, "watered": t.watered, "regrows": t.crop_regrows}
                for row in self.tiles for t in row
            ],
            "farm_rows": self.farm_rows,
            "farm_cols": self.farm_cols,
            "farm_off_x": self.farm_off_x,
            "farm_off_y": self.farm_off_y,
            "farm_expansion_tier": self.farm_expansion_tier,
            "buildings": self.buildings,
            "shipping_bin_contents": self.shipping_bin_contents,
            "npc_hearts": {n.id: n.heart_level for n in self.npcs},
            "married_to": self.married_to,
            "bots": [{"type": b.bot_type, "x": b.array_x, "y": b.array_y, "active": b.active}
                     for b in self.bots],
            "animals": self.animals,
            "barn_capacity": self.barn_capacity,
            "ship_tier": self.ship_tier,
            "fuel": self.fuel,
            "season_index": self.season_index,
            "day_in_season": self.day_in_season,
            "weather_timer": self.weather_timer,
            "current_weather_idx": WEATHER_EVENTS.index(self.current_weather) if self.current_weather in WEATHER_EVENTS else 0,
            "skills": self.skills,
            "processing_queue": self.processing_queue,
            "fish_collection": self.fish_collection,
            "fish_caught_total": self.fish_caught_total,
            "reputation": self.reputation,
            "completed_quests": self.completed_quests,
            "active_quests": self.active_quests,
            "merchant_present": self.merchant_present,
            "merchant_items": self.merchant_items,
            "merchant_last_visit": self.merchant_last_visit,
        }
        path = f"savegame_{slot}.json"
        with open(path, "w") as f:
            json.dump(data, f)
        self.set_message(f"Game saved to Slot {slot + 1}!")

    def load_game(self, slot=0):
        path = f"savegame_{slot}.json"
        if not os.path.exists(path):
            return False
        with open(path, "r") as f:
            data = json.load(f)
        self.day = data["day"]
        self.time_slot = data["time_slot"]
        self.time_progress = data.get("time_progress", 0.0)
        self.player.gold = data["gold"]
        self.player.energy = data["energy"]
        self.player.inventory = data["inventory"]
        self.player.seed_inventory = data.get("seed_inventory", {})
        self.farm_expansion_tier = data.get("farm_expansion_tier", 0)
        self.farm_cols = data.get("farm_cols", FARM_EXPANSIONS[0]["cols"])
        self.farm_rows = data.get("farm_rows", FARM_EXPANSIONS[0]["rows"])
        self.farm_off_x = data.get("farm_off_x", FARM_EXPANSIONS[0]["off_x"])
        self.farm_off_y = data.get("farm_off_y", FARM_EXPANSIONS[0]["off_y"])
        self.tiles = []
        idx = 0
        for r in range(self.farm_rows):
            row = []
            for c in range(self.farm_cols):
                tile = Tile(c, r)
                if idx < len(data["tiles"]):
                    td = data["tiles"][idx]
                    tile.soil_state = td["soil"]
                    tile.crop_type = td.get("crop")
                    tile.crop = td.get("crop")
                    tile.crop_stage = td["stage"]
                    tile.crop_timer = td["timer"]
                    tile.watered = td["watered"]
                    tile.crop_regrows = td.get("regrows", False)
                row.append(tile)
                idx += 1
            self.tiles.append(row)
        self.buildings = data.get("buildings", [])
        self.shipping_bin_contents = data.get("shipping_bin_contents", {})
        self.animals = data.get("animals", [])
        self.barn_capacity = data.get("barn_capacity", 4)
        if "npc_hearts" in data:
            for nid, h in data["npc_hearts"].items():
                for npc in self.npcs:
                    if npc.id == nid:
                        npc.heart_level = h
        self.married_to = data.get("married_to")
        self.bots = []
        for bd in data.get("bots", []):
            bot = FarmBot(bd["type"], bd["x"], bd["y"])
            bot.active = bd.get("active", True)
            self.bots.append(bot)
        self.ship_tier = data.get("ship_tier", 0)
        self.fuel = data.get("fuel", SHIP_TIERS[self.ship_tier]["fuel_capacity"])
        self.season_index = data.get("season_index", 0)
        self.day_in_season = data.get("day_in_season", 0)
        self.weather_timer = data.get("weather_timer", random.randint(WEATHER_DURATION["min"], WEATHER_DURATION["max"]))
        weather_idx = data.get("current_weather_idx", 0)
        self.current_weather = WEATHER_EVENTS[weather_idx] if 0 <= weather_idx < len(WEATHER_EVENTS) else WEATHER_EVENTS[0]
        self.skills = data.get("skills", {"farming": 0, "exploration": 0, "cooking": 0, "social": 0})
        self.processing_queue = data.get("processing_queue", [])
        self.fish_collection = data.get("fish_collection", {})
        self.fish_caught_total = data.get("fish_caught_total", 0)
        self.reputation = data.get("reputation", 0)
        self.completed_quests = data.get("completed_quests", 0)
        self.active_quests = data.get("active_quests", [])
        self.merchant_present = data.get("merchant_present", False)
        self.merchant_items = data.get("merchant_items", [])
        self.merchant_last_visit = data.get("merchant_last_visit", -1)
        return True

    def get_tile_at(self, tx, ty):
        if self.player.current_map == "farm":
            tx -= self.farm_off_x
            ty -= self.farm_off_y
        if 0 <= ty < self.farm_rows and 0 <= tx < self.farm_cols:
            return self.tiles[ty][tx]
        return None

    def interact(self):
        if self.dialogue_active:
            return
        px = self.player.x // TILE_SIZE
        py = self.player.y // TILE_SIZE

        if self.player.current_map == "farm":
            for bot in self.bots:
                wx = bot.array_x + self.farm_off_x
                wy = bot.array_y + self.farm_off_y
                if abs(px - wx) <= 0 and abs(py - wy) <= 0:
                    if not bot.active:
                        self.reactivate_bot(bot)
                        return
            if abs(px - 8) <= 1 and abs(py - 2) <= 1:
                self.sleep_prompt = True
                return
            # Building interaction (check facing tile)
            ftx, fty = self.player.get_facing_tile()
            for b in self.buildings:
                bt = BUILDING_TYPES[b["type"]]
                bw, bh = bt["size"]
                if b["tile_x"] <= ftx < b["tile_x"] + bw and b["tile_y"] <= fty < b["tile_y"] + bh:
                    if b["type"] == "shipping_bin":
                        self.open_shipping_bin()
                        return
                    elif b["type"] == "storage_shed":
                        self.set_message("Storage Shed: extra inventory space!")
                        return
                    elif b["type"] == "greenhouse":
                        self.set_message("Greenhouse: crops here ignore season penalties!")
                        return
                    elif b["type"] == "barn":
                        self.barn_overlay_active = True
                        return
            # Signpost at southeast edge of tillable area
            sign_x = self.farm_off_x + self.farm_cols
            sign_y = self.farm_off_y + self.farm_rows
            if abs(px - sign_x) <= 1 and abs(py - sign_y) <= 1:
                self.expand_menu_active = True
                return
            return

        if self.player.current_map == "spaceport":
            for npc in self.npcs:
                dx = abs(px - npc.tile_x)
                dy = abs(py - npc.tile_y)
                if dx <= 1 and dy <= 1:
                    if self.gift_mode:
                        if self.give_gift(npc):
                            return
                    if npc.id == "zoop":
                        self.pet_shop_active = True
                        return
                    if self.try_complete_delivery(npc):
                        return
                    self.start_dialogue(npc)
                    return
            if self.get_rank() >= 5 and abs(px - 3) <= 1 and abs(py - 3) <= 1:
                self.visit_observatory()
                return
            if abs(px - 6) <= 1 and abs(py - 10) <= 1:
                self.quest_board_active = True
                return
            if self.merchant_present and abs(px - 5) <= 1 and abs(py - 8) <= 1:
                self.merchant_shop_active = True
                return
            if 8 <= px <= 12 and 4 <= py <= 8:
                self.start_shop()
                return
            if 13 <= px <= 17 and 4 <= py <= 8:
                if self.gift_mode:
                    for npc in self.npcs:
                        if npc.id == "blip":
                            if self.give_gift(npc):
                                return
                self.start_bar()
                return
            if self.festival_today and 12 <= px <= 17 and 16 <= py <= 19:
                self.start_festival()
                return
            if 25 <= px <= 29 and 8 <= py <= 12:
                self.start_fishing()
                return
            for npc in self.npcs:
                if npc.location in ["house1", "house2", "house3", "house4"]:
                    hx, hy = npc.base_tile_x, npc.base_tile_y
                    if abs(px - hx) <= 2 and abs(py - hy) <= 2:
                        if self.gift_mode:
                            if self.give_gift(npc):
                                return
                        if self.try_complete_delivery(npc):
                            return
                        self.start_dialogue(npc)
                        return

    def get_solid_rects(self):
        rects = []
        ts = TILE_SIZE
        if self.player.current_map == "farm":
            rects.append(pygame.Rect(7 * ts, 0, 3 * ts, 3 * ts))
            tree_positions = [(1, 4), (1, 7), (1, 10), (0, 15),
                              (self.farm_off_x + self.farm_cols + 2, 3),
                              (self.farm_off_x + self.farm_cols + 2, 8)]
            for tx, ty in tree_positions:
                if tx < FARM_TILES_X and ty < FARM_TILES_Y:
                    rects.append(pygame.Rect(tx * ts, ty * ts, ts, ts))
            # Building solids
            for b in self.buildings:
                bt = BUILDING_TYPES[b["type"]]
                bw, bh = bt["size"]
                rects.append(pygame.Rect(b["tile_x"] * ts, b["tile_y"] * ts, bw * ts, bh * ts))
        else:
            rects.append(pygame.Rect(8 * ts, 2 * ts, 3 * ts, 3 * ts))
            rects.append(pygame.Rect(15 * ts, 2 * ts, 3 * ts, 3 * ts))
            for hx, hy in [(5, 14), (9, 14), (19, 14), (25, 14)]:
                rects.append(pygame.Rect(hx * ts, hy * ts, 3 * ts, 3 * ts))
            for npc in self.npcs:
                rects.append(pygame.Rect(npc.tile_x * ts + 3 + int(npc.pixel_offset_x), npc.tile_y * ts - 13 + int(npc.pixel_offset_y), 26, 26))
        return rects

    @staticmethod
    def get_slot_info(slot):
        path = f"savegame_{slot}.json"
        if not os.path.exists(path):
            return None
        with open(path, "r") as f:
            data = json.load(f)
        return {
            "day": data.get("day", 1),
            "gold": data.get("gold", 0),
            "season": SEASONS[data.get("season_index", 0)] if data.get("season_index", 0) < len(SEASONS) else "?",
            "day_in_season": data.get("day_in_season", 0),
        }
