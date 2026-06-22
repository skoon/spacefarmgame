import pygame
import json
import os
import random
import math
from src.constants import *
from src.sprites import *

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.soil_state = "untilled"
        self.crop = None
        self.crop_type = None
        self.crop_stage = 0
        self.crop_timer = 0
        self.crop_growth_time = 0
        self.crop_regrows = False
        self.watered = False

    def till(self):
        if self.soil_state == "untilled":
            self.soil_state = "tilled"
            self.watered = False
            return True
        return False

    def water(self):
        if self.soil_state == "tilled" and not self.watered:
            self.watered = True
            self.soil_state = "watered"
            return True
        return False

    def plant(self, crop_key):
        if self.soil_state == "watered" and self.crop is None:
            data = CROP_TYPES[crop_key]
            self.crop_type = crop_key
            self.crop = crop_key
            self.crop_stage = 0
            self.crop_timer = 0
            self.crop_growth_time = data["growth_time"]
            self.crop_regrows = data.get("regrows", False)
            return True
        return False

    def grow(self, growth_rate=1.0):
        if self.crop and self.watered:
            self.crop_timer += growth_rate
            data = CROP_TYPES.get(self.crop_type)
            if data:
                stages = data["growth_stages"]
                progress = self.crop_timer / max(self.crop_growth_time, 1)
                new_stage = min(int(progress * stages), stages - 1)
                if new_stage > self.crop_stage:
                    self.crop_stage = new_stage
                    return True
        return False

    def is_mature(self):
        if self.crop:
            data = CROP_TYPES.get(self.crop_type)
            if data:
                return self.crop_stage >= data["growth_stages"] - 1
        return False

    def harvest(self):
        if self.is_mature():
            crop_type = self.crop_type
            if self.crop_regrows:
                self.crop_stage = max(0, CROP_TYPES[crop_type]["growth_stages"] - 3)
                self.crop_timer = 0
            else:
                self.crop = None
                self.crop_type = None
                self.crop_stage = 0
                self.crop_timer = 0
                self.crop_regrows = False
                self.soil_state = "tilled"
                self.watered = False
            return CROP_TYPES[crop_type]["sell_price"] // 2, crop_type
        return 0, None

class Player:
    def __init__(self):
        self.x = 8 * TILE_SIZE
        self.y = 10 * TILE_SIZE
        self.farm_x = self.x
        self.farm_y = self.y
        self.sp_x = 14 * TILE_SIZE
        self.sp_y = 18 * TILE_SIZE
        self.direction = "down"
        self.speed = 3
        self.energy = 100
        self.max_energy = 100
        self.gold = 200
        self.selected_tool = 0
        self.tools = ["hoe", "watering_can", "scythe"]
        self.inventory = {}
        self.seed_inventory = {}
        self.current_map = "farm"

    def add_item(self, item_name, count=1):
        if item_name in self.inventory:
            self.inventory[item_name] += count
        else:
            self.inventory[item_name] = count

    def remove_item(self, item_name, count=1):
        if item_name in self.inventory and self.inventory[item_name] >= count:
            self.inventory[item_name] -= count
            if self.inventory[item_name] <= 0:
                del self.inventory[item_name]
            return True
        return False

    def has_item(self, item_name, count=1):
        return self.inventory.get(item_name, 0) >= count

    def get_facing_tile(self):
        tx = self.x // TILE_SIZE
        ty = self.y // TILE_SIZE
        if self.direction == "up":
            ty -= 1
        elif self.direction == "down":
            ty += 1
        elif self.direction == "left":
            tx -= 1
        elif self.direction == "right":
            tx += 1
        return tx, ty

class NPC:
    def __init__(self, defn):
        self.id = defn["id"]
        self.name = defn["name"]
        self.color = defn["color"]
        self.color2 = defn["color2"]
        self.species = defn["species"]
        self.location = defn["location"]
        self.romanceable = defn["romanceable"]
        self.bio = defn["bio"]
        self.likes = defn["likes"]
        self.loves = defn["loves"]
        self.dialogues = defn["dialogues"]
        self.heart_level = 0
        self.talked_today = False
        self.dialogue_state = "intro"
        self.schedule = defn.get("schedule", [])
        self.base_tile_x = 10
        self.base_tile_y = 10

        if self.location == "shop":
            self.base_tile_x, self.base_tile_y = 10, 10
            self.screen = "spaceport"
        elif self.location == "bar":
            self.base_tile_x, self.base_tile_y = 16, 10
            self.screen = "spaceport"
        elif self.location == "house1":
            self.base_tile_x, self.base_tile_y = 6, 17
            self.screen = "spaceport"
        elif self.location == "house2":
            self.base_tile_x, self.base_tile_y = 10, 17
            self.screen = "spaceport"
        elif self.location == "house3":
            self.base_tile_x, self.base_tile_y = 20, 17
            self.screen = "spaceport"
        elif self.location == "house4":
            self.base_tile_x, self.base_tile_y = 26, 17
            self.screen = "spaceport"
        elif self.location == "pet_shop":
            self.base_tile_x, self.base_tile_y = 22, 10
            self.screen = "spaceport"
        else:
            self.base_tile_x, self.base_tile_y = 10, 10
            self.screen = "spaceport"

        self.tile_x = self.base_tile_x
        self.tile_y = self.base_tile_y
        self.pixel_offset_x = 0.0
        self.pixel_offset_y = 0.0
        self.move_target = None
        self.last_schedule_time = -1

    def update_schedule(self, time_slot):
        if time_slot == self.last_schedule_time:
            return
        self.last_schedule_time = time_slot
        if not self.schedule:
            return
        best_entry = None
        for entry in self.schedule:
            if entry[0] == time_slot:
                best_entry = entry
                break
            if entry[0] > time_slot:
                if best_entry is None or entry[0] < best_entry[0]:
                    best_entry = entry
        if best_entry is None and self.schedule:
            best_entry = self.schedule[0]
        if best_entry:
            next_x, next_y = best_entry[1], best_entry[2]
            if (next_x, next_y) != (self.tile_x, self.tile_y) and self.move_target is None:
                self.move_target = (next_x, next_y)

    def update_movement(self):
        if self.move_target is None:
            return
        tx, ty = self.move_target
        current_x = self.tile_x * TILE_SIZE + self.pixel_offset_x
        current_y = self.tile_y * TILE_SIZE + self.pixel_offset_y
        target_x = tx * TILE_SIZE
        target_y = ty * TILE_SIZE
        dx = target_x - current_x
        dy = target_y - current_y
        dist = math.hypot(dx, dy)
        speed = 2.0
        if dist <= speed:
            self.tile_x = tx
            self.tile_y = ty
            self.pixel_offset_x = 0.0
            self.pixel_offset_y = 0.0
            self.move_target = None
        else:
            self.pixel_offset_x += (dx / dist) * speed
            self.pixel_offset_y += (dy / dist) * speed

    def get_dialogue(self):
        if self.heart_level >= 4:
            key = "friendly"
        elif self.heart_level >= 1:
            key = "neutral"
        else:
            key = "intro"
        lines = self.dialogues.get(key, self.dialogues["intro"])
        if isinstance(lines, str):
            return lines
        return random.choice(lines)

    def get_gift_response(self, item_key):
        if item_key in self.loves:
            return self.dialogues.get("gift_love", "Wow, I love this!")
        elif item_key in self.likes:
            return self.dialogues.get("gift_like", "Thanks, I like this!")
        return self.dialogues.get("gift_neutral", "Thanks.")

class FarmBot:
    def __init__(self, bot_type, array_x, array_y):
        self.bot_type = bot_type
        self.array_x = array_x
        self.array_y = array_y
        self.active = True

