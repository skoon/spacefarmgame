import pygame
import json
import os
import random
import math
from src.constants import *
from src.sprites import *


class BuildingsMixin:
    def buy_expansion(self):
        next_tier_idx = self.farm_expansion_tier + 1
        if next_tier_idx >= len(FARM_EXPANSIONS):
            self.set_message("Farm is already max size!")
            return
        next_tier = FARM_EXPANSIONS[next_tier_idx]
        if self.player.gold < next_tier["cost"]:
            self.set_message(f"Need {next_tier['cost']}g to expand!")
            return
        self.player.gold -= next_tier["cost"]
        self.farm_expansion_tier = next_tier_idx
        tier = FARM_EXPANSIONS[self.farm_expansion_tier]
        old_rows = len(self.tiles)
        old_cols = len(self.tiles[0]) if old_rows > 0 else 0
        new_rows = tier["rows"]
        new_cols = tier["cols"]
        for r in range(new_rows):
            if r < old_rows:
                for c in range(old_cols, new_cols):
                    self.tiles[r].append(Tile(c, r))
            else:
                self.tiles.append([Tile(c, r) for c in range(new_cols)])
        self.farm_cols = tier["cols"]
        self.farm_rows = tier["rows"]
        self.farm_off_x = tier["off_x"]
        self.farm_off_y = tier["off_y"]
        self.set_message(f"Farm expanded! ({self.farm_cols}x{self.farm_rows})")

    def buy_building(self, building_id):
        bt = BUILDING_TYPES[building_id]
        if self.player.gold < bt["cost"]:
            self.set_message(f"Need {bt['cost']}g to build {bt['name']}!")
            return
        self.player.gold -= bt["cost"]
        self.build_mode = building_id
        self.building_shop_active = False
        self.set_message(f"Placed {bt['name']}! Walk to the farm and press E to place it.")

    def place_building(self):
        if self.build_mode is None:
            return
        px, py = self.player.get_facing_tile()
        bt = BUILDING_TYPES[self.build_mode]
        bw, bh = bt["size"]
        # Check if within tillable area
        if not (self.farm_off_x <= px < self.farm_off_x + self.farm_cols and
                self.farm_off_y <= py < self.farm_off_y + self.farm_rows):
            self.set_message("Can't place here — must be on tillable soil!")
            return
        # Check if area overlaps another building
        for b in self.buildings:
            ox = b["tile_x"]
            oy = b["tile_y"]
            obw, obh = BUILDING_TYPES[b["type"]]["size"]
            if px < ox + obw and px + bw > ox and py < oy + obh and py + bh > oy:
                self.set_message("Can't place here — overlaps another building!")
                return
        self.buildings.append({"type": self.build_mode, "tile_x": px, "tile_y": py})
        self.build_mode = None
        self.set_message(f"{bt['name']} built!")

    def process_shipping_bin(self):
        if not self.shipping_bin_contents:
            return
        total = 0
        for item_name, count in self.shipping_bin_contents.items():
            price = CROP_TYPES[item_name]["sell_price"] * count
            self.player.gold += price
            total += count
        self.shipping_bin_contents = {}
        self.set_message(f"Shipping bin earned {total} item sales!")

    def apply_buildings(self):
        for b in self.buildings:
            if b["type"] == "well":
                cx = b["tile_x"]
                cy = b["tile_y"]
                for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                    ax = cx + dx - self.farm_off_x
                    ay = cy + dy - self.farm_off_y
                    if 0 <= ay < self.farm_rows and 0 <= ax < self.farm_cols:
                        tile = self.tiles[ay][ax]
                        if tile.soil_state == "tilled" and not tile.watered:
                            tile.water()

    def open_shipping_bin(self):
        self.subscreen = "shipping_bin"
        self.set_message("Drop items to sell overnight. Press I to transfer items.")
