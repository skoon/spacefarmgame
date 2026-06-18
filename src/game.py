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
            self.base_tile_x, self.base_tile_y = 13, 17
            self.screen = "spaceport"
        elif self.location == "house3":
            self.base_tile_x, self.base_tile_y = 20, 17
            self.screen = "spaceport"
        elif self.location == "house4":
            self.base_tile_x, self.base_tile_y = 26, 17
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

class GameState:
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
        self.skills = {"farming": 0, "exploration": 0, "cooking": 0, "social": 0}
        self.skills_active = False

    def add_particles(self, x, y, color, count=8):
        for _ in range(count):
            self.particles.append({
                "x": x, "y": y,
                "vx": random.uniform(-2, 2),
                "vy": random.uniform(-3, -1),
                "life": random.randint(15, 30),
                "max_life": 30,
                "color": color,
                "size": random.randint(2, 4),
            })

    def update_particles(self):
        for p in self.particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.1
            p["life"] -= 1
            if p["life"] <= 0:
                self.particles.remove(p)

    def update_weather_particles(self):
        weather = self.current_weather["name"]
        if weather == "Alien Rain":
            if random.random() < 0.3:
                self.weather_particles.append({
                    "x": random.randint(0, SCREEN_WIDTH),
                    "y": -10,
                    "vx": random.uniform(-0.5, 0.5),
                    "vy": random.uniform(4, 7),
                    "life": random.randint(30, 60),
                    "max_life": 60,
                    "color": (100, 150, 255),
                    "size": random.randint(1, 3),
                })
        elif weather == "Meteor Shower":
            if random.random() < 0.05:
                start_x = random.randint(0, SCREEN_WIDTH)
                self.weather_particles.append({
                    "x": start_x,
                    "y": -20,
                    "vx": random.uniform(2, 4),
                    "vy": random.uniform(3, 6),
                    "life": random.randint(20, 40),
                    "max_life": 40,
                    "color": (255, 220, 100),
                    "size": random.randint(2, 4),
                })
        elif weather == "Void Fog":
            if random.random() < 0.15:
                self.weather_particles.append({
                    "x": random.randint(0, SCREEN_WIDTH),
                    "y": random.randint(0, SCREEN_HEIGHT // 2),
                    "vx": random.uniform(0.3, 1.0),
                    "vy": random.uniform(-0.2, 0.2),
                    "life": random.randint(60, 120),
                    "max_life": 120,
                    "color": (80, 60, 100),
                    "size": random.randint(8, 20),
                })
        for p in self.weather_particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            if p["life"] <= 0 or p["y"] > SCREEN_HEIGHT + 20:
                self.weather_particles.remove(p)

    def set_message(self, msg):
        self.message = msg
        self.message_timer = 120

    def add_skill_xp(self, skill, amount):
        old_level = self.get_skill_level(skill)
        self.skills[skill] = self.skills.get(skill, 0) + amount
        new_level = self.get_skill_level(skill)
        if new_level > old_level and new_level in SKILL_PERKS.get(skill, {}):
            perk = SKILL_PERKS[skill][new_level]
            self.set_message(f"★ {perk['name']} unlocked! {perk['desc']}")

    def get_skill_level(self, skill):
        xp = self.skills.get(skill, 0)
        level = 0
        cum = 0
        while True:
            needed = (level + 1) * 10
            if cum + needed > xp:
                break
            cum += needed
            level += 1
        return min(level, 20)

    def get_skill_xp_for_next(self, skill):
        level = self.get_skill_level(skill)
        return (level + 1) * 10

    def get_skill_progress(self, skill):
        level = self.get_skill_level(skill)
        xp = self.skills.get(skill, 0)
        total = 0
        for i in range(level):
            total += (i + 1) * 10
        return xp - total

    def get_skill_xp_needed(self, skill):
        level = self.get_skill_level(skill)
        return (level + 1) * 10

    def update_weather(self):
        self.weather_timer -= 1
        if self.weather_timer <= 0:
            weights = SEASONAL_MODIFIERS[SEASONS[self.season_index]]["weather_weights"]
            self.current_weather = random.choices(WEATHER_EVENTS, weights=weights)[0]
            self.weather_timer = random.randint(WEATHER_DURATION["min"], WEATHER_DURATION["max"])
        self.weather_particles = []

    def update_season(self):
        self.day_in_season += 1
        if self.day_in_season >= SEASON_DAY_LENGTH:
            self.day_in_season = 0
            self.season_index = (self.season_index + 1) % len(SEASONS)
            self.set_message(f"Welcome to {SEASONS[self.season_index]} Season!")

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
        self.run_bots()
        for npc in self.npcs:
            npc.talked_today = False
        season_name = SEASONS[self.season_index]
        mod = SEASONAL_MODIFIERS[season_name]["growth_mod"]
        weather_mod = self.current_weather["crop_bonus"]
        growth_rate = mod + weather_mod
        if self.get_skill_level("farming") >= 5:
            growth_rate *= 1.25
        for row in self.tiles:
            for tile in row:
                tile.grow(growth_rate)
                tile.watered = False
                if tile.soil_state == "watered":
                    tile.soil_state = "tilled"
        self.set_message(f"Day {self.day} - {TIME_NAMES[0]} ({SEASONS[self.season_index]}, {self.current_weather['name']})")

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
            "npc_hearts": {n.id: n.heart_level for n in self.npcs},
            "married_to": self.married_to,
            "bots": [{"type": b.bot_type, "x": b.array_x, "y": b.array_y, "active": b.active}
                     for b in self.bots],
            "ship_tier": self.ship_tier,
            "fuel": self.fuel,
            "season_index": self.season_index,
            "day_in_season": self.day_in_season,
            "weather_timer": self.weather_timer,
            "current_weather_idx": WEATHER_EVENTS.index(self.current_weather) if self.current_weather in WEATHER_EVENTS else 0,
            "skills": self.skills,
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
        idx = 0
        for r in range(TILLABLE_ROWS):
            for c in range(TILLABLE_COLS):
                td = data["tiles"][idx]
                self.tiles[r][c].soil_state = td["soil"]
                self.tiles[r][c].crop_type = td.get("crop")
                self.tiles[r][c].crop = td.get("crop")
                self.tiles[r][c].crop_stage = td["stage"]
                self.tiles[r][c].crop_timer = td["timer"]
                self.tiles[r][c].watered = td["watered"]
                self.tiles[r][c].crop_regrows = td.get("regrows", False)
                idx += 1
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
        return True

    def reactivate_bot(self, bot):
        cost = BOT_TYPES[bot.bot_type]["upkeep"]
        if self.player.gold >= cost:
            self.player.gold -= cost
            bot.active = True
            self.set_message(f"{BOT_TYPES[bot.bot_type]['name']} reactivated! ({cost}g)")
        else:
            self.set_message(f"Need {cost}g to reactivate {BOT_TYPES[bot.bot_type]['name']}.")

    def give_gift(self, npc):
        if not self.gift_mode:
            return False
        available = [item for item in self.player.inventory if item not in [CROP_TYPES[c]["seed_name"] for c in CROP_ORDER]]
        if not available:
            self.set_message("You don't have anything to give.")
            self.gift_mode = False
            return True
        item = available[0]
        if not self.player.has_item(item):
            self.set_message(f"You don't have {item}.")
            return True
        self.player.remove_item(item, 1)
        response = npc.get_gift_response(item)
        if item in npc.loves:
            gain = 2
        elif item in npc.likes:
            gain = 1
        else:
            gain = 0
        if self.get_skill_level("social") >= 5:
            gain += 1
        if gain > 0:
            old = npc.heart_level
            npc.heart_level = min(10, npc.heart_level + gain)
            self.dialogue_lines = [f"{npc.name}: {response}", f"♥ +{gain} hearts! ({npc.heart_level}/10)"]
        else:
            self.dialogue_lines = [f"{npc.name}: {response}"]
        self.dialogue_active = True
        self.dialogue_npc = npc
        self.dialogue_index = 0
        self.gift_mode = False
        self.add_skill_xp("social", 3)
        return True

    def get_tile_at(self, tx, ty):
        if self.player.current_map == "farm":
            tx -= FARM_TILES_OFFSET_X
            ty -= FARM_TILES_OFFSET_Y
        if 0 <= ty < TILLABLE_ROWS and 0 <= tx < TILLABLE_COLS:
            return self.tiles[ty][tx]
        return None

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

    def upgrade_ship(self):
        tier = SHIP_TIERS[self.ship_tier + 1] if self.ship_tier + 1 < len(SHIP_TIERS) else None
        if tier is None:
            self.set_message("Your ship is already maxed out!")
            return
        if self.player.gold >= tier["cost"]:
            self.player.gold -= tier["cost"]
            self.ship_tier += 1
            self.fuel = min(self.fuel, SHIP_TIERS[self.ship_tier]["fuel_capacity"])
            self.set_message(f"Upgraded to {tier['name']}!")
        else:
            self.set_message(f"Need {tier['cost']}g to upgrade. ({tier['name']})")

    def refuel_ship(self):
        tier = SHIP_TIERS[self.ship_tier]
        max_fuel = tier["fuel_capacity"]
        if self.fuel >= max_fuel:
            self.set_message("Fuel tank is full!")
            return
        max_refuel = min(50, max_fuel - self.fuel)
        cost = max_refuel
        if self.player.gold >= cost:
            self.player.gold -= cost
            self.fuel += max_refuel
            self.set_message(f"Refueled +{max_refuel} fuel for {cost}g.")
        else:
            can_afford = self.player.gold
            if can_afford > 0:
                self.fuel += can_afford
                self.player.gold = 0
                self.set_message(f"Refueled +{can_afford} fuel.")
            else:
                self.set_message("Not enough gold to refuel!")

    def launch_to_planet(self, planet_idx):
        planet = PLANETS[planet_idx]
        fuel_cost = planet["fuel_cost"]
        if self.get_skill_level("exploration") >= 5:
            fuel_cost = max(1, int(fuel_cost * 0.8))
        if self.fuel < fuel_cost:
            self.set_message(f"Need {fuel_cost} fuel to reach {planet['name']}!")
            return
        self.fuel -= fuel_cost
        self.current_planet = planet_idx
        turns = random.randint(5, 8)
        if self.get_skill_level("exploration") >= 20:
            turns += 2
        self.planet_turns_left = turns
        self.planet_explore_active = True
        self.hangar_active = False
        self.ship_cargo = {}
        self.planet_log = []
        self.set_message(f"Landed on {planet['name']}! Scan (SPACE) or Return (E).")
        self.add_skill_xp("exploration", 2)

    def scan_planet(self):
        if not self.planet_explore_active or self.current_planet is None:
            return
        self.planet_turns_left -= 1
        planet = PLANETS[self.current_planet]
        tier = SHIP_TIERS[self.ship_tier]
        cargo_cap = tier["cargo_capacity"]
        if self.get_skill_level("exploration") >= 10:
            cargo_cap += 1
        cargo_total = sum(self.ship_cargo.values())
        roll = random.random()
        if roll < 0.35:
            if cargo_total < cargo_cap:
                finds = planet["finds"]
                exclusive = PLANET_EXCLUSIVE_SEEDS.get(planet["name"], [])
                all_finds = finds + exclusive
                found = random.choice(all_finds)
                self.ship_cargo[found] = self.ship_cargo.get(found, 0) + 1
                self.planet_log.append(f"Found {found}!")
            else:
                self.planet_log.append("Cargo full! Return to unload.")
        elif roll < 0.50:
            fuel_find = random.randint(3, 8)
            self.fuel += fuel_find
            self.planet_log.append(f"Found {fuel_find} fuel!")
        elif roll < 0.65:
            gold_find = random.randint(10, 30)
            self.player.gold += gold_find
            self.planet_log.append(f"Found {gold_find}g!")
        else:
            self.planet_log.append("Nothing interesting here.")
        self.add_skill_xp("exploration", 3)
        if self.planet_turns_left <= 0:
            self.return_from_planet()

    def return_from_planet(self):
        if self.current_planet is None:
            return
        planet = PLANETS[self.current_planet]
        for item, count in self.ship_cargo.items():
            self.player.add_item(item, count)
        total = sum(self.ship_cargo.values())
        self.ship_cargo = {}
        self.current_planet = None
        self.planet_explore_active = False
        self.set_message(f"Returned from {planet['name']}! Collected {total} items.")
        self.add_skill_xp("exploration", 5)

    def interact(self):
        if self.dialogue_active:
            return
        px = self.player.x // TILE_SIZE
        py = self.player.y // TILE_SIZE

        if self.player.current_map == "farm":
            for bot in self.bots:
                wx = bot.array_x + FARM_TILES_OFFSET_X
                wy = bot.array_y + FARM_TILES_OFFSET_Y
                if abs(px - wx) <= 0 and abs(py - wy) <= 0:
                    if not bot.active:
                        self.reactivate_bot(bot)
                        return
            if abs(px - 8) <= 1 and abs(py - 2) <= 1:
                self.sleep_prompt = True
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
                    self.start_dialogue(npc)
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
            for npc in self.npcs:
                if npc.location in ["house1", "house2", "house3", "house4"]:
                    hx, hy = npc.base_tile_x, npc.base_tile_y
                    if abs(px - hx) <= 2 and abs(py - hy) <= 2:
                        if self.gift_mode:
                            if self.give_gift(npc):
                                return
                        self.start_dialogue(npc)
                        return

    def start_dialogue(self, npc):
        if npc.talked_today:
            lines = [f"{npc.name}: {npc.get_dialogue()}"]
        else:
            npc.talked_today = True
            old_level = npc.heart_level
            npc.heart_level = min(10, npc.heart_level + 1)

            lines = [f"{npc.name}: {npc.get_dialogue()}"]
            if npc.heart_level > old_level:
                lines.append(f"♥ Relationship with {npc.name} grew! ({npc.heart_level}/10)")
            self.add_skill_xp("social", 1)

            if npc.romanceable and npc.heart_level >= 10 and self.married_to is None:
                lines.append(f"★ {npc.name} looks at you with love in their eyes...")
                lines.append("Propose? (Y/N)")

        self.dialogue_active = True
        self.dialogue_npc = npc
        self.dialogue_lines = lines
        self.dialogue_index = 0

    def advance_dialogue(self):
        if not self.dialogue_active:
            return
        self.dialogue_index += 1
        if self.dialogue_index >= len(self.dialogue_lines):
            self.dialogue_active = False
            self.dialogue_npc = None

    def start_shop(self):
        self.shop_active = True
        self.subscreen = "shop"

    def start_bar(self):
        self.bar_active = True
        self.subscreen = "bar"

    def buy_bar_item(self, idx, count=1):
        if 0 <= idx < len(BAR_ITEMS):
            item = BAR_ITEMS[idx]
            total = item["price"] * count
            if self.player.gold >= total:
                self.player.gold -= total
                self.player.energy = min(self.player.max_energy, self.player.energy + item["energy"] * count)
                self.set_message(f"Bought {count}x {item['name']}! +{item['energy'] * count} energy.")
                self.bar_active = False
                self.subscreen = None
            else:
                self.set_message(f"Not enough gold! Need {total}g.")

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

    def buy_item(self, crop_key, count=1):
        data = CROP_TYPES[crop_key]
        cost = data["seed_price"] * count
        if self.player.gold >= cost:
            self.player.gold -= cost
            seed_name = data["seed_name"]
            self.player.add_item(seed_name, count)
            self.set_message(f"Bought {count}x {seed_name} for {cost}g!")
        else:
            self.set_message("Not enough gold!")

    def sell_item(self, crop_key, count=1):
        if self.player.has_item(crop_key, count):
            price = CROP_TYPES[crop_key]["sell_price"] * count
            self.player.remove_item(crop_key, count)
            self.player.gold += price
            self.set_message(f"Sold {count}x {CROP_TYPES[crop_key]['name']} for {price}g!")
        else:
            self.set_message("You don't have any to sell!")

    def sell_dish(self, dish_name, count=1):
        if self.player.has_item(dish_name, count):
            recipe = next((r for r in RECIPES.values() if r["name"] == dish_name), None)
            if recipe:
                price = recipe["sell_price"] * count
                if self.get_skill_level("cooking") >= 10:
                    price = int(price * 1.25)
                self.player.remove_item(dish_name, count)
                self.player.gold += price
                self.set_message(f"Sold {count}x {dish_name} for {price}g!")
        else:
            self.set_message("You don't have any to sell!")

    def cook_recipe(self, recipe_key, count=1):
        recipe = RECIPES.get(recipe_key)
        if not recipe:
            return
        for ing, need in recipe["ingredients"].items():
            if self.player.inventory.get(ing, 0) < need * count:
                self.set_message(f"Missing ingredients for {count}x {recipe['name']}!")
                return
        for ing, need in recipe["ingredients"].items():
            self.player.remove_item(ing, need * count)
        dish_name = recipe["name"]
        self.player.add_item(dish_name, count)
        energy_gain = recipe["energy"] * count
        if self.get_skill_level("cooking") >= 5:
            energy_gain = int(energy_gain * 1.25)
        self.player.energy = min(self.player.max_energy, self.player.energy + energy_gain)
        self.cooking_active = False
        self.set_message(f"Cooked {count}x {dish_name}! +{energy_gain} energy!")
        self.add_skill_xp("cooking", 3 * count)

    def get_solid_rects(self):
        rects = []
        ts = TILE_SIZE
        if self.player.current_map == "farm":
            rects.append(pygame.Rect(7 * ts, 0, 3 * ts, 3 * ts))
            tree_positions = [(1, 4), (1, 7), (1, 10), (0, 15),
                              (2 + TILLABLE_COLS + 2, 3), (2 + TILLABLE_COLS + 2, 8)]
            for tx, ty in tree_positions:
                if tx < FARM_TILES_X and ty < FARM_TILES_Y:
                    rects.append(pygame.Rect(tx * ts, ty * ts, ts, ts))
        else:
            rects.append(pygame.Rect(8 * ts, 2 * ts, 3 * ts, 3 * ts))
            rects.append(pygame.Rect(15 * ts, 2 * ts, 3 * ts, 3 * ts))
            for hx, hy in [(5, 14), (12, 14), (19, 14), (25, 14)]:
                rects.append(pygame.Rect(hx * ts, hy * ts, 3 * ts, 3 * ts))
            for npc in self.npcs:
                rects.append(pygame.Rect(npc.tile_x * ts + 3 + int(npc.pixel_offset_x), npc.tile_y * ts - 13 + int(npc.pixel_offset_y), 26, 26))
        return rects

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
        ax = px - FARM_TILES_OFFSET_X
        ay = py - FARM_TILES_OFFSET_Y
        if 0 <= ax < TILLABLE_COLS and 0 <= ay < TILLABLE_ROWS:
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
        total_upkeep = sum(BOT_TYPES[b.bot_type]["upkeep"] for b in self.bots if b.active)
        if self.player.gold < total_upkeep:
            for b in self.bots:
                b.active = False
            self.set_message("Not enough gold for bot upkeep! Bots deactivated.")
            return
        self.player.gold -= total_upkeep
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
                    if 0 <= ay < TILLABLE_ROWS and 0 <= ax < TILLABLE_COLS:
                        tile = self.tiles[ay][ax]
                        if bt["action"] == "water" and tile.soil_state == "tilled" and not tile.watered:
                            tile.water()
                        elif bt["action"] == "harvest" and tile.is_mature():
                            value, crop_type = tile.harvest()
                            if crop_type:
                                count = random.randint(1, 3)
                                self.player.add_item(crop_type, count)
                                self.player.gold += value

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

    def get_npc_by_id(self, nid):
        for n in self.npcs:
            if n.id == nid:
                return n
        return None

    def propose_marriage(self, npc_id):
        if self.married_to:
            self.set_message("You're already married!")
            return
        npc = self.get_npc_by_id(npc_id)
        if npc and npc.romanceable and npc.heart_level >= 10:
            self.married_to = npc_id
            self.set_message(f"♥ You married {npc.name}! Congratulations! ♥")
            self.dialogue_active = False
            self.dialogue_npc = None
            self.add_particles(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, PINK, 40)
            self.add_particles(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, GOLD, 30)
            self.add_skill_xp("social", 20)

    def start_festival(self):
        if not self.festival_today:
            return
        fest = FESTIVALS[self.festival_today]
        self.festival_active = True
        self.festival_type = fest["type"]
        self.festival_data = {"round": 0, "score": 0, "won": False, "over": False}
        if self.festival_type == "crop_tasting":
            available = [c for c in CROP_ORDER if c in self.player.inventory]
            if len(available) < 1:
                self.set_message("You need at least one crop to enter!")
                self.festival_active = False
                self.festival_type = None
                return
            random.shuffle(available)
            self.festival_data["crops"] = available[:min(3, len(available))]
            self.festival_data["threshold"] = max(CROP_TYPES[c]["sell_price"] for c in available) * 0.5
        elif self.festival_type == "flower_arrange":
            colors = [(255, 80, 80), (80, 200, 80), (80, 120, 255), (255, 200, 80)]
            self.festival_data["grid"] = [[random.choice(colors) for _ in range(4)] for _ in range(4)]
            self.festival_data["target"] = [[random.choice(colors) for _ in range(4)] for _ in range(4)]
            self.festival_data["timer"] = 600
            self.festival_data["cursor"] = [0, 0]
        elif self.festival_type == "rhythm":
            arrows = ["UP", "DOWN", "LEFT", "RIGHT"]
            self.festival_data["sequence"] = [random.choice(arrows) for _ in range(10)]
            self.festival_data["index"] = 0
            self.festival_data["misses"] = 0
            self.festival_data["cooldown"] = 0

    def end_festival(self, won=False):
        fest = FESTIVALS[self.festival_today] if self.festival_today else None
        if won and fest:
            self.player.add_item(fest["reward_item"])
            self.player.gold += fest["reward_gold"]
            for npc in self.npcs:
                npc.heart_level = min(10, npc.heart_level + 1)
            self.set_message(f"You won the {fest['name']}! +{fest['reward_gold']}g, {fest['reward_item']}, +1♥ all NPCs!")
            self.add_particles(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, GOLD, 30)
            self.add_particles(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, PINK, 30)
        elif fest:
            self.set_message(f"You didn't win the {fest['name']}. Better luck next time!")
        self.festival_active = False
        self.festival_type = None
        self.festival_data = {}
