import pygame
import json
import os
import random
import math
from src.constants import *
from src.sprites import *


class AnimalsMixin:
    def buy_animal(self, animal_id):
        if len(self.animals) >= self.barn_capacity:
            self.set_message("Your barn is full! Expand it first.")
            return
        at = ANIMAL_TYPES[animal_id]
        if self.player.gold < at["cost"]:
            self.set_message(f"Need {at['cost']}g!")
            return
        self.player.gold -= at["cost"]
        self.animals.append({"type": animal_id, "days_since_produce": 0, "fed_today": False})
        self.set_message(f"Bought {at['name']}!")

    def feed_animals(self):
        for a in self.animals:
            at = ANIMAL_TYPES[a["type"]]
            a["fed_today"] = False
            can_feed = True
            for feed_item, need in at["feed"].items():
                if not self.player.has_item(feed_item, need):
                    can_feed = False
                    break
            if can_feed:
                for feed_item, need in at["feed"].items():
                    self.player.remove_item(feed_item, need)
                a["fed_today"] = True

    def produce_animals(self):
        for a in self.animals:
            if a["fed_today"]:
                a["days_since_produce"] += 1
                at = ANIMAL_TYPES[a["type"]]
                if a["days_since_produce"] >= at["produce_interval"]:
                    product = at["produce"]
                    self.player.add_item(product)
                    a["days_since_produce"] = 0
