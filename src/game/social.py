import pygame
import json
import os
import random
import math
from src.constants import *
from src.sprites import *


class SocialMixin:
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
        if gain > 0:
            self.add_reputation(2 * gain)
        return True

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
