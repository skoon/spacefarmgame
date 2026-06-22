import pygame
import json
import os
import random
import math
from src.constants import *
from src.sprites import *


class KitchenMixin:
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
        self.check_quest_progress("cook", dish_name, count)

    def start_crafting(self, recipe_key, count=1):
        recipe = ARTISAN_RECIPES.get(recipe_key)
        if not recipe:
            return
        for ing, need in recipe["ingredients"].items():
            if self.player.inventory.get(ing, 0) < need * count:
                self.set_message(f"Missing ingredients for {count}x {recipe['name']}!")
                return
        for ing, need in recipe["ingredients"].items():
            self.player.remove_item(ing, need * count)
        if recipe["processing_days"] == 0:
            self.player.add_item(recipe["name"], count)
            self.set_message(f"Crafted {count}x {recipe['name']}!")
            self.add_skill_xp("farming", 2)
        else:
            self.processing_queue.append({
                "recipe_key": recipe_key,
                "days_remaining": recipe["processing_days"],
                "count": count,
            })
            self.set_message(f"{recipe['name']} started! Ready in {recipe['processing_days']} days.")

    def process_crafting(self):
        finished = 0
        for entry in self.processing_queue[:]:
            entry["days_remaining"] -= 1
            if entry["days_remaining"] <= 0:
                recipe = ARTISAN_RECIPES.get(entry["recipe_key"])
                if recipe:
                    self.player.add_item(recipe["name"], entry["count"])
                    finished += entry["count"]
                self.processing_queue.remove(entry)
        if finished > 0:
            self.set_message(f"{finished} artisan good(s) finished processing!")
