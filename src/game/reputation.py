import pygame
import json
import os
import random
import math
from src.constants import *
from src.sprites import *


class ReputationMixin:
    """Town reputation, daily quests, and the traveling merchant (Milestone 14).

    Reputation rises from quests, gifts, festival wins, and sales. Crossing a
    TOWN_RANKS threshold unlocks a rank perk. Daily quests are generated each
    morning onto the quest board; the player accepts up to three and claims the
    reward once the goal is met. The merchant (Cosmo) visits every
    MERCHANT_INTERVAL days once the town reaches rank 2.
    """

    # --- Reputation & ranks ---

    def get_rank(self):
        rank = 0
        for r in TOWN_RANKS:
            if self.reputation >= r["rep_needed"]:
                rank = r["level"]
        return rank

    def get_rank_name(self):
        return TOWN_RANKS[self.get_rank()]["name"]

    def get_rank_perks(self):
        rank = self.get_rank()
        return [r["perk"] for r in TOWN_RANKS if 0 < r["level"] <= rank]

    def add_reputation(self, amount):
        if amount <= 0:
            return
        old = self.get_rank()
        self.reputation += amount
        new = self.get_rank()
        if new > old:
            r = TOWN_RANKS[new]
            self.set_message(f"★ Town Rank Up! You are now {r['name']}: {r['perk']}")

    # --- Daily quests ---

    def generate_daily_quests(self):
        self.active_quests = []
        templates = random.sample(QUEST_TEMPLATES, min(3, len(QUEST_TEMPLATES)))
        for tmpl in templates:
            q = self._build_quest(tmpl)
            if q:
                self.active_quests.append(q)

    def _build_quest(self, tmpl):
        tid = tmpl["id"]
        count = random.randint(tmpl["min_count"], tmpl["max_count"])
        q = {
            "template_id": tid,
            "name": tmpl["name"],
            "count": count,
            "progress": 0,
            "accepted": False,
            "completed": False,
            "claimed": False,
            "reward_gold": random.randint(*tmpl["gold"]),
            "reward_rep": tmpl["rep"],
            "item": None,
            "npc_id": None,
            "npc_name": None,
            "desc": "",
        }
        if tid == "harvest":
            crop = random.choice(CROP_ORDER)
            q["item"] = crop
            q["desc"] = f"Harvest {count}x {CROP_TYPES[crop]['name']}"
        elif tid == "fish":
            q["desc"] = f"Catch {count} fish at the pier"
        elif tid == "cook":
            rk = random.choice(list(RECIPES.keys()))
            q["item"] = RECIPES[rk]["name"]
            q["desc"] = f"Cook {count}x {RECIPES[rk]['name']}"
        elif tid == "deliver":
            candidates = [n for n in self.npcs if n.id != "zoop"]
            if not candidates:
                return None
            npc = random.choice(candidates)
            crop = random.choice(CROP_ORDER)
            q["item"] = crop
            q["npc_id"] = npc.id
            q["npc_name"] = npc.name
            q["desc"] = f"Bring {count}x {CROP_TYPES[crop]['name']} to {npc.name}"
        return q

    def accept_quest(self, i):
        if not (0 <= i < len(self.active_quests)):
            return
        q = self.active_quests[i]
        if q["claimed"]:
            return
        if q["completed"]:
            self.claim_quest(i)
        elif not q["accepted"]:
            q["accepted"] = True
            self.set_message(f"Accepted quest: {q['desc']}")
        else:
            self.set_message("Already working on that one!")

    def claim_quest(self, i):
        if not (0 <= i < len(self.active_quests)):
            return
        q = self.active_quests[i]
        if not q["completed"] or q["claimed"]:
            return
        q["claimed"] = True
        self.player.gold += q["reward_gold"]
        self.completed_quests += 1
        self.add_reputation(q["reward_rep"])
        self.set_message(f"Quest complete! +{q['reward_gold']}g, +{q['reward_rep']} rep")

    def check_quest_progress(self, action, item=None, amount=1):
        """Advance accepted, in-progress quests matching this action/item."""
        for q in self.active_quests:
            if q["template_id"] != action or not q["accepted"] or q["completed"]:
                continue
            if q["item"] is not None and item is not None and q["item"] != item:
                continue
            q["progress"] = min(q["count"], q["progress"] + amount)
            if q["progress"] >= q["count"]:
                q["completed"] = True
                self.set_message(f"Quest ready to claim at the board: {q['desc']}")

    def try_complete_delivery(self, npc):
        """Hand in a delivery quest when pressing E on the target NPC.

        Returns True if a delivery was completed (so the caller skips dialogue).
        """
        for i, q in enumerate(self.active_quests):
            if (q["template_id"] == "deliver" and q["accepted"] and not q["completed"]
                    and q["npc_id"] == npc.id and self.player.has_item(q["item"], q["count"])):
                self.player.remove_item(q["item"], q["count"])
                q["completed"] = True
                self.claim_quest(i)
                return True
        return False

    # --- Rank-3 perk: upgraded bots gated by town rank in the shop ---

    def shop_bot_keys(self):
        rank = self.get_rank()
        return [k for k, v in BOT_TYPES.items() if v.get("rank_req", 0) <= rank]

    # --- Rank-5 perk: Spaceport Observatory ---

    def visit_observatory(self):
        if self.get_rank() >= 5:
            self.player.energy = min(self.player.max_energy, self.player.energy + 5)
            self.set_message("Observatory: you gaze at distant galaxies and feel inspired. +5 energy.")
        else:
            need = TOWN_RANKS[5]["rep_needed"]
            self.set_message(f"The Observatory is locked. Reach Legend rank ({need} rep) to enter.")

    # --- Traveling Merchant (Cosmo) ---

    def update_merchant(self):
        """Called each morning from advance_day()."""
        if self.get_rank() >= 2 and self.day % MERCHANT_INTERVAL == 0:
            self.merchant_present = True
            self.merchant_last_visit = self.day
            self.generate_merchant_items()
            self.set_message("A Traveling Merchant has arrived at the Space Port!")
        else:
            self.merchant_present = False
            self.merchant_shop_active = False

    def generate_merchant_items(self):
        self.merchant_items = random.sample(MERCHANT_POOL, min(3, len(MERCHANT_POOL)))

    def buy_merchant_item(self, idx):
        if not (0 <= idx < len(self.merchant_items)):
            return
        item = self.merchant_items[idx]
        if self.player.gold >= item["price"]:
            self.player.gold -= item["price"]
            self.player.add_item(item["name"], 1)
            self.set_message(f"Bought {item['name']} for {item['price']}g!")
        else:
            self.set_message(f"Not enough gold! Need {item['price']}g.")
