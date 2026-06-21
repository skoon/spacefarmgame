import pygame
import json
import os
import random
import math
from src.constants import *
from src.sprites import *


class EconomyMixin:
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
                return
            artisan = next((r for r in ARTISAN_RECIPES.values() if r["name"] == dish_name), None)
            if artisan:
                price = artisan["sell_price"] * count
                self.player.remove_item(dish_name, count)
                self.player.gold += price
                self.set_message(f"Sold {count}x {dish_name} for {price}g!")
        else:
            self.set_message("You don't have any to sell!")

    def sell_fish(self, fish_id, count=1):
        if self.player.has_item(fish_id, count):
            price = FISH_TYPES[fish_id]["sell_price"] * count
            if self.get_skill_level("exploration") >= 20:   # Lv20: +50% sell
                price = int(price * 1.5)
            self.player.remove_item(fish_id, count)
            self.player.gold += price
            self.set_message(f"Sold {count}x {FISH_TYPES[fish_id]['name']} for {price}g!")
        else:
            self.set_message("You don't have any to sell!")
