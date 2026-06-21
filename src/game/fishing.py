import pygame
import json
import os
import random
import math
from src.constants import *
from src.sprites import *


class FishingMixin:
    """Real-time fishing mini-game played at the spaceport pier.

    State machine (self.fishing_state):
        casting  -> SPACE casts the line          -> waiting
        waiting  -> timer ticks down to a bite    -> hooked
        hooked   -> SPACE within bite window      -> reeling   (else escape)
        reeling  -> SPACE fills bar vs. drain     -> caught    (else escape)
        caught   -> SPACE dismisses               -> casting

    update_fishing() is driven from the render loop (real time), not advance_day.
    """

    def start_fishing(self):
        self.fishing_active = True
        self.fishing_state = "casting"
        self.fishing_timer = 0
        self.fishing_bite_window = 0
        self.fishing_progress = 0.0
        self.fishing_current_fish = None
        self.fishing_caught_fish = None
        self.set_message("Cast your line! (SPACE to cast, ESC to leave)")

    def exit_fishing(self):
        self.fishing_active = False
        self.fishing_state = "idle"
        self.fishing_current_fish = None
        self.fishing_caught_fish = None

    def _eligible_fish(self):
        season = SEASONS[self.season_index]
        weather = self.current_weather["name"]
        ts = self.time_slot
        out = []
        for fid, f in FISH_TYPES.items():
            if f["seasons"] and season not in f["seasons"]:
                continue
            if f["weather"] and weather not in f["weather"]:
                continue
            if f["time_slots"] and ts not in f["time_slots"]:
                continue
            out.append(fid)
        return out

    def cast_line(self):
        self.fishing_state = "waiting"
        self.fishing_timer = random.randint(60, 180)  # 1-3s at 60 FPS
        if self.get_skill_level("exploration") >= 5:    # Lv5: bite 20% faster
            self.fishing_timer = int(self.fishing_timer * 0.8)
        self.set_message("Waiting for a bite...")

    def hook_fish(self):
        eligible = self._eligible_fish()
        if not eligible:
            self.escape_fish("Nothing's biting right now.")
            return
        rare_boost = self.get_skill_level("exploration") >= 15  # Lv15: rarer 2x
        weights = []
        for fid in eligible:
            d = FISH_TYPES[fid]["difficulty"]
            w = 1.0 / d  # harder fish are rarer
            if rare_boost and d >= 3:
                w *= 2.0
            weights.append(w)
        self.fishing_current_fish = random.choices(eligible, weights=weights)[0]
        self.fishing_state = "reeling"
        self.fishing_progress = 0.3  # small head start
        self.set_message("Reel it in! Tap SPACE!")

    def reel_press(self):
        if self.fishing_state != "reeling":
            return
        self.fishing_progress = min(1.0, self.fishing_progress + 0.12)
        if self.fishing_progress >= 1.0:
            self.catch_fish()

    def update_fishing(self):
        if not self.fishing_active:
            return
        if self.fishing_state == "waiting":
            self.fishing_timer -= 1
            if self.fishing_timer <= 0:
                self.fishing_state = "hooked"
                self.fishing_bite_window = 30  # 0.5s to react
                self.set_message("A bite! Press SPACE!")
        elif self.fishing_state == "hooked":
            self.fishing_bite_window -= 1
            if self.fishing_bite_window <= 0:
                self.escape_fish("It got away! Too slow.")
        elif self.fishing_state == "reeling":
            d = FISH_TYPES[self.fishing_current_fish]["difficulty"]
            drain = d * 0.003
            if self.get_skill_level("exploration") >= 10:   # Lv10: 20% slower
                drain *= 0.8
            self.fishing_progress -= drain
            if self.fishing_progress <= 0.0:
                self.escape_fish("It got away! The line went slack.")

    def catch_fish(self):
        fid = self.fishing_current_fish
        f = FISH_TYPES[fid]
        self.player.add_item(fid, 1)
        first = not self.fish_collection.get(fid, False)
        self.fish_collection[fid] = True
        self.fish_caught_total += 1
        self.fishing_caught_fish = fid
        self.fishing_state = "caught"
        self.add_skill_xp("exploration", 3)
        size = random.choice(["tiny", "small", "average", "large", "huge"])
        extra = "  (NEW!)" if first else ""
        self.set_message(f"Caught a {size} {f['name']}!{extra}")

    def escape_fish(self, msg="It got away!"):
        self.fishing_state = "casting"
        self.fishing_current_fish = None
        self.fishing_progress = 0.0
        self.fishing_timer = 0
        self.fishing_bite_window = 0
        self.set_message(msg)
