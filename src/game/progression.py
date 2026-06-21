import pygame
import json
import os
import random
import math
from src.constants import *
from src.sprites import *


class ProgressionMixin:
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
