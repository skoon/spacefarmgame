import pygame
import json
import os
import random
import math
from src.constants import *
from src.sprites import *


class ExplorationMixin:
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
