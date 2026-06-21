import pygame
import json
import os
import random
import math
from src.constants import *
from src.sprites import *
from src.game.entities import FarmBot


class FarmingMixin:
    def reactivate_bot(self, bot):
        cost = BOT_TYPES[bot.bot_type]["upkeep"]
        if self.player.gold >= cost:
            self.player.gold -= cost
            bot.active = True
            self.set_message(f"{BOT_TYPES[bot.bot_type]['name']} reactivated! ({cost}g)")
        else:
            self.set_message(f"Need {cost}g to reactivate {BOT_TYPES[bot.bot_type]['name']}.")

    def use_tool(self):
        tx, ty = self.player.get_facing_tile()
        tile = self.get_tile_at(tx, ty)
        if tile is None:
            self.set_message("Can't reach that tile.")
            return

        tool = self.player.tools[self.player.selected_tool]

        if tool == "hoe":
            if tile.till():
                self.player.energy -= 3
                if self.player.energy >= 0:
                    self.add_particles(tx * TILE_SIZE + TILE_SIZE // 2,
                                       ty * TILE_SIZE + TILE_SIZE // 2,
                                       SOIL_BROWN)
                    self.set_message("Tilled the soil.")
                    self.add_skill_xp("farming", 2)
                    self.advance_time()
                else:
                    self.player.energy += 3
                    self.set_message("Too tired!")
            else:
                self.set_message("Soil is already tilled.")
        elif tool == "watering_can":
            if tile.water():
                self.player.energy -= 2
                if self.player.energy >= 0:
                    self.add_particles(tx * TILE_SIZE + TILE_SIZE // 2,
                                       ty * TILE_SIZE + TILE_SIZE // 2,
                                       WATER_BLUE, 12)
                    self.set_message("Watered the soil.")
                    self.add_skill_xp("farming", 2)
                    self.advance_time()
                else:
                    self.player.energy += 2
                    self.set_message("Too tired!")
            else:
                self.set_message("Soil doesn't need watering.")
        elif tool == "scythe":
            if tile.is_mature():
                value, crop_type = tile.harvest()
                if crop_type:
                    count = random.randint(1, 3)
                    if self.get_skill_level("farming") >= 10 and random.random() < 0.2:
                        count *= 2
                    self.player.add_item(crop_type, count)
                    self.player.gold += value
                    self.player.energy -= 2
                    self.add_particles(tx * TILE_SIZE + TILE_SIZE // 2,
                                       ty * TILE_SIZE + TILE_SIZE // 2,
                                       CROP_TYPES[crop_type]["color"], 15)
                    self.set_message(f"Harvested {count}x {CROP_TYPES[crop_type]['name']}! (+{value}g)")
                    self.add_skill_xp("farming", 5)
                    self.advance_time()
            else:
                self.set_message("Nothing to harvest here.")

    def plant_seed(self, crop_key):
        tx, ty = self.player.get_facing_tile()
        tile = self.get_tile_at(tx, ty)
        if tile is None:
            self.set_message("Can't reach that tile.")
            return
        seed_name = CROP_TYPES[crop_key]["seed_name"]
        if self.player.has_item(seed_name):
            if tile.plant(crop_key):
                self.player.remove_item(seed_name)
                self.player.energy -= 2
                self.add_particles(tx * TILE_SIZE + TILE_SIZE // 2,
                                   ty * TILE_SIZE + TILE_SIZE // 2,
                                   (100, 200, 100), 8)
                self.set_message(f"Planted {CROP_TYPES[crop_key]['name']}!")
                self.add_skill_xp("farming", 3)
                self.advance_time()
            else:
                self.set_message("Can't plant here. Need watered soil.")
        else:
            self.set_message(f"You don't have {seed_name}!")

    def select_seed_to_plant(self):
        available = []
        for crop_key in CROP_ORDER:
            seed_name = CROP_TYPES[crop_key]["seed_name"]
            if seed_name in self.player.inventory:
                available.append(crop_key)
        if not available:
            self.set_message("You don't have any seeds!")
            return
        self.seed_select_active = True
        self.selected_seed_index = 0

    def buy_bot(self, bot_type):
        bt = BOT_TYPES[bot_type]
        if self.player.gold >= bt["cost"]:
            self.player.gold -= bt["cost"]
            self.placement_mode = bot_type
            self.bot_shop_active = False
            self.set_message(f"Bought {bt['name']}! Go to the farm and press E to place it.")
        else:
            self.set_message(f"Not enough gold! Need {bt['cost']}g.")

    def place_bot(self):
        if self.placement_mode is None:
            return
        px = self.player.x // TILE_SIZE
        py = self.player.y // TILE_SIZE
        ax = px - self.farm_off_x
        ay = py - self.farm_off_y
        if 0 <= ax < self.farm_cols and 0 <= ay < self.farm_rows:
            for bot in self.bots:
                if bot.array_x == ax and bot.array_y == ay:
                    self.set_message("A bot is already there!")
                    return
            bot_type = self.placement_mode
            self.bots.append(FarmBot(bot_type, ax, ay))
            self.placement_mode = None
            self.set_message(f"{BOT_TYPES[bot_type]['name']} placed!")
        else:
            self.set_message("Can't place a bot there.")

    def run_bots(self):
        watered = 0
        harvested = 0
        harvest_names = []
        for bot in self.bots:
            if not bot.active:
                continue
            bt = BOT_TYPES[bot.bot_type]
            for dy in range(-bt["range"], bt["range"] + 1):
                for dx in range(-bt["range"], bt["range"] + 1):
                    if abs(dx) + abs(dy) > bt["range"]:
                        continue
                    ax = bot.array_x + dx
                    ay = bot.array_y + dy
                    if 0 <= ay < self.farm_rows and 0 <= ax < self.farm_cols:
                        tile = self.tiles[ay][ax]
                        if bt["action"] == "water" and tile.soil_state == "tilled" and not tile.watered:
                            tile.water()
                            watered += 1
                        elif bt["action"] == "harvest" and tile.is_mature():
                            value, crop_type = tile.harvest()
                            if crop_type:
                                count = random.randint(1, 3)
                                self.player.add_item(crop_type, count)
                                self.player.gold += value
                                harvested += count
                                name = CROP_TYPES[crop_type]["name"]
                                if name not in harvest_names:
                                    harvest_names.append(name)

        total_upkeep = sum(BOT_TYPES[b.bot_type]["upkeep"] for b in self.bots if b.active)
        if total_upkeep > 0 and self.player.gold < total_upkeep:
            for b in self.bots:
                b.active = False
            self.upkeep_failed = True
        elif total_upkeep > 0:
            self.player.gold -= total_upkeep
            self.upkeep_failed = False

        if self.upkeep_failed:
            self.set_message("Not enough gold for bot upkeep! Bots deactivated.")
        elif harvested > 0:
            items = ", ".join(harvest_names)
            self.set_message(f"Bots harvested {harvested}x {items}!")
        elif watered > 0:
            self.set_message(f"Bots watered {watered} tile(s).")
