# Space Farm Galaxy — Milestone Plan

## Overview

Six major features, ordered by dependency. Each milestone builds on the prior.
Estimated effort: **Low** (< 50 LoC changed), **Medium** (50–200), **High** (200–500).

---

## Milestone 1 — Spaceship Hangar & Planet Exploration

**Goal:** Player can build a spaceship, fly to procedurally generated planets, find rare seeds/resources, and return.

### Data Structures (implemented)

**`src/constants.py`:**
- `SHIP_TIERS`: 3 tiers — Scout Pod (0g, 50 fuel, 4 cargo), Hauler MK2 (2000g, 120 fuel, 10 cargo), Star Cruiser (8000g, 300 fuel, 20 cargo)
- `PLANETS`: 4 destinations — Xylos Prime (15 fuel), Magma-7 (25), Aquaris (10), Verdantia (20). Each has a `color`, `desc`, and `finds` list of seed items.
- `PLANET_EXCLUSIVE_SEEDS`: rare seeds per planet (e.g. Starlight Melon Seeds on Xylos Prime)

**`src/game.py`** — new fields on `GameState`:
```python
self.ship_tier = 0
self.fuel = 50                     # starts full on Scout Pod
self.ship_cargo = {}               # {item_name: count} — current expedition loot
self.hangar_active = False
self.current_planet = None         # index into PLANETS while exploring
self.planet_turns_left = 0
self.planet_explore_active = False
self.planet_log = []               # recent scan messages
```

### Gameplay flow

1. **Spaceport** → press `H` → Hangar overlay
2. **Hangar** shows: ship name, fuel gauge, cargo slots, upgrade/refuel buttons, planet list
3. Press `1-4` to launch to a planet (costs fuel)
4. **Planet screen**: biome-colored gradient background with ground, stars, planet name
5. Press `SPACE` to scan: 35% find seed, 15% find fuel, 15% find gold, 35% nothing
6. If cargo is full, finds are blocked — must return to unload
7. Press `E` to return early; auto-returns after 5-8 turns
8. Cargo merges into player inventory on return

### Key binds

| Key | Action |
|-----|--------|
| `H` (spaceport) | Open hangar |
| `1-4` (hangar) | Launch to planet |
| `U` (hangar) | Upgrade ship |
| `R` (hangar) | Refuel (up to 50 units, 1g each) |
| `SPACE` (planet) | Scan for resources |
| `E` (planet) | Return to spaceport |

### Files changed

| File | Change |
|------|--------|
| `src/constants.py` | Added `SHIP_TIERS`, `PLANETS`, `PLANET_EXCLUSIVE_SEEDS` |
| `src/game.py` | Added ship fields, `upgrade_ship()`, `refuel_ship()`, `launch_to_planet()`, `scan_planet()`, `return_from_planet()`, save/load |
| `main.py` | Added `draw_hangar()`, `draw_planet_explore()`, key handling |
| `src/sprites.py` | Added `get_ship_surf(tier)` |

---

## Milestone 2 — Automated Farm Bots

**Goal:** Player can buy bots that autonomously water/harvest crops, freeing the player for exploration.

### Data Structures (implemented)

**`src/constants.py`:**
```python
BOT_TYPES = {
    "water_bot":   {"name": "Water-Bot",   "action": "water",   "range": 2, "cost": 300,  "upkeep": 2,  "color": (80,180,255)},
    "sprout_bot":  {"name": "Sprout-Bot",  "action": "water",   "range": 3, "cost": 500,  "upkeep": 5,  "color": (100,200,255)},
    "harvest_bot": {"name": "Harvest-Bot", "action": "harvest", "range": 2, "cost": 1200, "upkeep": 10, "color": (255,200,100)},
}
```

**`src/game.py`** — new `FarmBot` class:
```python
class FarmBot:
    def __init__(self, bot_type, array_x, array_y):
        self.bot_type = bot_type
        self.array_x = array_x        # 0..13 (tile array coords)
        self.array_y = array_y        # 0..9
        self.active = True
```

### Gameplay flow

1. **Spaceport** → press `B` → Bot Workshop overlay shows 3 bots with stats
2. Press `1-3` to buy → gold deducted, enters placement mode
3. **Farm** → green ghost highlights current tillable tile
4. Press `E` to place bot on that tile
5. Each day (`advance_day`): `run_bots()` deducts upkeep, waters/harvests in diamond range
6. If gold < total upkeep: bots are deactivated (shown dimmed with "(off)" label)
7. Press `E` on a deactivated bot to pay back-upkeep and reactivate it

### Key binds

| Key | Action |
|-----|--------|
| `B` (spaceport) | Open bot workshop |
| `1-3` (workshop) | Buy bot |
| `E` (farm, placement) | Place bot |
| `E` (farm, on inactive bot) | Reactivate bot |
| `ESC` (any) | Cancel placement |

### Bot behavior

- **Water-Bot** (range 2): waters tilled soil within 2-tile diamond
- **Sprout-Bot** (range 3): waters tilled soil within 3-tile diamond
- **Harvest-Bot** (range 2): harvests mature crops, adds to inventory + gold

### Bug fix (added post-launch)

- Inactive bots were invisible → now rendered dimmed with gray overlay + "(off)" label
- Reactivation via E key on bot tile pays one day's upkeep

---

## Milestone 3 — NPC Schedules & Gift-Giving

**Goal:** NPCs walk the spaceport on daily schedules, accept gifts, and have special heart events.

### Schedule System

**`src/constants.py`** — add schedule data to `NPC_DEFS`:
```python
{
    # ...existing fields...
    "schedule": [
        {"time": 0, "tile": (10, 10)},   # Dawn: at shop counter
        {"time": 2, "tile": (10, 12)},   # Midday: outside shop
        {"time": 4, "tile": (3, 5)},     # Evening: stargazing
    ],
}
```

**`src/game.py`** — NPC changes:
```python
# New NPC fields
self.schedule = defn.get("schedule", [])
self.home_tile = (self.tile_x, self.tile_y)  # original spawn tile
self.moving = False
self.move_target = None
self.move_progress = 0.0

# New methods
def get_current_tile(self, time_slot):
    """Interpolate schedule to return current tile based on time_slot."""
    # If no schedule entries for this time, return home tile
    # Otherwise find the two nearest schedule entries and lerp

def update_movement(self):
    """Animate sprite between tiles (smooth pixel movement)."""
```

**`src/game.py`** — `GameState.update_npc_positions(time_slot)`:
- Called once per time slot advance
- Sets each NPC's `move_target` to their schedule-based tile
- NPCs smoothly walk to target over ~60 frames via `update_movement()`

### Gift-Giving System

**`src/game.py`** — new method:
```python
def give_gift(self, npc, item_key):
    """Give an item to an NPC. Check likes/loves for heart bonus."""
    if not self.player.has_item(item_key):
        return False
    self.player.remove_item(item_key, 1)
    if item_key in npc.loves:
        gain = 2
    elif item_key in npc.likes:
        gain = 1
    else:
        gain = 0
    npc.heart_level = min(10, npc.heart_level + gain)
    return gain
```

### Heart Events

**`src/game.py`** — new dict + trigger:
```python
HEART_EVENTS = {
    "nova": {
        4: "Nova shows you her old star charts...",
        7: "Nova cooks you dinner under the stars.",
        10: "Nova confesses her feelings.",
    },
    # ... per NPC
}
```

Triggered in `start_dialogue()` when heart_level crosses a threshold.

### Interaction update

**`main.py`** — when pressing E near an NPC:
1. If player has an item selected (press `G` to enter gift mode), give gift
2. Otherwise, start dialogue as before

### Key binds

| Key | Action |
|-----|--------|
| `G` | Toggle gift mode (highlights inventory item to give) |
| `E` near NPC | Give selected gift or talk |

### Files to change

| File | Change | Effort |
|------|--------|--------|
| `src/constants.py` | Add schedule + heart event data to `NPC_DEFS` | Medium |
| `src/game.py` | `NPC.schedule`, `get_current_tile()`, `update_movement()`, `give_gift()`, `HEART_EVENTS` dict | High |
| `src/game.py` | `GameState.update_npc_positions()`, heart event trigger in `start_dialogue()` | Medium |
| `main.py` | `draw_npc_movement()` in spaceport render, gift mode UI overlay, `G` key | Medium |
| `main.py` | Save/load: persist NPC `heart_level` + `talked_today` (already saved) | None |

### Movement detail

NPC movement is purely visual — collision rects still exist at NPC positions. When an NPC moves, their collision rect follows. The player cannot walk through them at any time.

NPCs walk at **2px/frame** (~3.7 tiles/sec diagonal) via `NPC.update_movement()`, called from the main render loop.

`update_schedule()` sets `move_target` instead of teleporting; `update_movement()` interpolates `pixel_offset_x/y` as floats each frame until the target is reached, then snaps `tile_x/y`.

---



## Milestone 4 — Cosmic Weather & Seasons

**Goal:** Dynamic weather effects and seasonal cycles that affect crop growth.

### New Data Structures

**`src/constants.py`** — add:
```python
SEASONS = ["Nebula", "Void", "Bloom", "Solar"]
SEASON_DAY_LENGTH = 14  # days per season (7 seasons per in-game year, 4 seasons)

WEATHER_EVENTS = [
    {"name": "Clear",       "crop_bonus": 0,   "energy_cost": 0,  "color": None},
    {"name": "Meteor Shower","crop_bonus": 0.5,"energy_cost": 0,  "color": (255,200,100)},
    {"name": "Solar Flare", "crop_bonus": 0.25,"energy_cost": 15,"color": (255,100,50)},
    {"name": "Alien Rain",  "crop_bonus": 0,   "energy_cost": 0,  "color": (100,150,255)},
    {"name": "Void Fog",    "crop_bonus": -0.5,"energy_cost": 5,  "color": (80,60,100)},
]

SEASONAL_MODIFIERS = {
    "Nebula": {"weather_weights": [30, 20, 10, 30, 10], "growth_mod": 1.5,  "sky_tint": (200,180,255)},
    "Void":   {"weather_weights": [20, 10, 5,  20, 45], "growth_mod": 0.5,  "sky_tint": (60,60,80)},
    "Bloom":  {"weather_weights": [40, 15, 25, 15, 5],  "growth_mod": 1.25, "sky_tint": (180,255,200)},
    "Solar":  {"weather_weights": [25, 10, 45, 10, 10], "growth_mod": 1.0,  "sky_tint": (255,230,150)},
}

WEATHER_DURATION = {"min": 2, "max": 4}  # days per weather event
```

### Changes to game systems

**`src/game.py`** — new fields on `GameState`:
```python
self.season_index = 0      # 0-3, increments every SEASON_DAY_LENGTH days
self.day_in_season = 0     # resets when season changes
self.current_weather = WEATHER_EVENTS[0]
self.weather_timer = 0     # days remaining for current weather
```

**Tile growth modifier** — in `Tile.grow()`:
```python
if self.crop and self.watered:
    mod = SEASONAL_MODIFIERS[SEASONS[game.season_index]]["growth_mod"]
    weather_mod = game.current_weather["crop_bonus"]
    self.crop_timer += mod + weather_mod  # can be fractional
```

Now `crop_timer` must be a `float`. This is a **breaking change** to the save format — existing saves with `crop_timer` as int will need conversion on load.

### Visual changes

**`main.py`** — sky rendering:
```python
# In draw_farm() and draw_spaceport():
season = SEASONS[game.season_index]
sky = time_colors[game.time_slot]
tint = SEASONAL_MODIFIERS[season]["sky_tint"]
blended = blend(sky, tint, 0.3)  # tint the sky

# Weather particles:
if game.current_weather["name"] == "Alien Rain":
    # draw falling blue drops
elif game.current_weather["name"] == "Meteor Shower":
    # occasional falling yellow streaks
```

**`main.py`** — HUD addition:
```python
draw_text(screen, f"{SEASONS[game.season_index]} Season", 750, 26, ...)
draw_text(screen, f"Weather: {game.current_weather['name']}", 750, 42, ...)
```

### Files to change

| File | Change | Effort |
|------|--------|--------|
| `src/constants.py` | `SEASONS`, `WEATHER_EVENTS`, `SEASONAL_MODIFIERS`, `WEATHER_DURATION` | Low |
| `src/game.py` | New season/weather fields, `update_weather()`, `update_season()` called from `advance_day()`, tile growth modifier, `crop_timer` → float | High |
| `main.py` | Sky tint blending, weather particle rendering, HUD season/weather display | Medium |
| `main.py` | Save/load: persist season/weather fields | Low |

### Weather transitions

```python
def update_weather(self):
    self.weather_timer -= 1
    if self.weather_timer <= 0:
        weights = SEASONAL_MODIFIERS[SEASONS[self.season_index]]["weather_weights"]
        self.current_weather = random.choices(WEATHER_EVENTS, weights=weights)[0]
        self.weather_timer = random.randint(WEATHER_DURATION["min"], WEATHER_DURATION["max"])
```

Called at the top of `advance_day()`.

### Season transitions

```python
def update_season(self):
    self.day_in_season += 1
    if self.day_in_season >= SEASON_DAY_LENGTH:
        self.day_in_season = 0
        self.season_index = (self.season_index + 1) % len(SEASONS)
        self.set_message(f"Welcome to {SEASONS[self.season_index]} Season!")
```

Called from `advance_day()` after `update_weather()`.

---

## Milestone 5 — Spaceport Festivals

**Goal:** Seasonal festivals with mini-games, unique rewards, and relationship boosts.

### Festival Schedule

**`src/constants.py`** — add:
```python
FESTIVALS = {
    "nebula": {
        "name": "Harvest Moon Feast",
        "season": "Nebula",
        "day": 7,                   # day 7 of Nebula season
        "type": "crop_tasting",     # mini-game type
        "reward_item": "Nebula Seeds",
        "reward_gold": 500,
    },
    "bloom": {
        "name": "Alien Flower Show",
        "season": "Bloom",
        "day": 7,
        "type": "flower_arrange",
        "reward_item": "Starlight Melon Seeds",
        "reward_gold": 300,
    },
    "solar": {
        "name": "Starlight Dance",
        "season": "Solar",
        "day": 10,
        "type": "rhythm",
        "reward_item": "Quasar Berry Seeds",
        "reward_gold": 200,
    },
}
```

**`src/game.py`** — new field:
```python
self.festival_today = None    # FESTIVALS key or None
self.festival_active = False  # player entered festival zone
```

### Festival trigger

In `advance_day()`, after season update:
```python
for key, fest in FESTIVALS.items():
    if fest["season"] == SEASONS[self.season_index] and fest["day"] == self.day_in_season:
        self.festival_today = key
        self.set_message(f"Today: {fest['name']}! Visit the Space Port!")
        break
else:
    self.festival_today = None
```

When player is on the spaceport during a festival day and walks near the landing pad (tile 12-17, 16-19), `game.interact()` triggers the festival.

### Mini-game: Crop Tasting

**`main.py`** — new draw function + key handling:
- 3 NPC judges appear on screen with thought bubbles
- Player is given 3 crops they've harvested
- Choose which crop to submit (1/2/3 keys)
- Score based on crop sell price + random factor
- Win → reward_item + reward_gold + all nearby NPCs +1 heart

### Mini-game: Alien Flower Show

- Grid of tiles, some have flowers
- Player has 30 seconds to arrange flowers in a pattern
- Click to swap adjacent tiles
- Matching the target pattern → win

### Mini-game: Starlight Dance (Rhythm)

- Arrow keys appear on screen in sequence
- Player must press matching keys in time
- 10 rounds, score based on accuracy
- Win → reward

### Files to change

| File | Change | Effort |
|------|--------|--------|
| `src/constants.py` | `FESTIVALS` dict | Low |
| `src/game.py` | Festival fields, `start_festival()`, `end_festival()`, `get_festival_score()` | Medium |
| `main.py` | `draw_festival_notice()` on HUD, festival mini-game screens: `draw_crop_tasting()`, `draw_flower_arrange()`, `draw_starlight_dance()` | High |
| `main.py` | Movement input capture for rhythm game, E to submit, festival interaction in `interact()` | Medium |
| `main.py` | Save/load: `festival_today` (ephemeral, no save needed) | None |

### Mini-game architecture

Each mini-game is a self-contained loop within `handle_events()`:

```python
# Pseudocode for Crop Tasting
if game.festival_active and festival_type == "crop_tasting":
    if event.type == KEYDOWN and event.key in [K_1, K_2, K_3]:
        submitted_crop = available_crops[event.key - K_1]
        score = CROP_TYPES[submitted_crop]["sell_price"] * random.uniform(0.8, 1.2)
        if score >= threshold:
            grant_reward()
        game.festival_active = False
        continue  # absorb input during festival
```

Festival screens use the same overlay pattern as shop/inventory:
- Semi-transparent backdrop
- Centered panel with instructions and choices
- ESC to leave early (no reward)

---

---

## Milestone 6 — Save / Load Screen with Three Slots

**Goal:** Player can manage multiple save files through a dedicated UI overlay.

### Data Structures

**`src/constants.py`** — add:
```python
SAVE_SLOT_COUNT = 3
```

**`src/game.py`** — new fields on `GameState`:
```python
self.save_menu_active = False
self.save_menu_slot = 0       # currently selected slot index (0-2)
```

### Slot System

- Save files: `savegame_0.json`, `savegame_1.json`, `savegame_2.json`
- `save_game(slot)` writes to `savegame_{slot}.json`
- `load_game(slot)` reads from `savegame_{slot}.json`
- `get_slot_info(slot)` statically reads preview data (day, gold, season) without loading full game state
- `save_menu_slot` is persisted as the "active" slot; auto-loaded on startup and saved on quit

### Save/Load Screen

**`main.py`** — new function `draw_save_menu()`:
- Dark overlay with centered panel
- 3 slot cards, each showing: slot number, Day, Season, Gold (or "Empty")
- Current slot highlighted with gold border
- Press **1/2/3** to save to that slot
- Press **L + 1/2/3** (hold L, tap digit) to load from that slot
- Press **ESC** to close

### Key Binds

| Key | Action |
|-----|--------|
| `S` (anywhere) | Open save/load screen |
| `1/2/3` (save menu) | Save to slot |
| `L + 1/2/3` (save menu) | Load from slot |
| `ESC` (save menu) | Close save menu |

### Files changed

| File | Change | Effort |
|------|--------|--------|
| `src/constants.py` | `SAVE_SLOT_COUNT` constant | Low |
| `src/game.py` | `save_menu_active`, `save_menu_slot` fields; `save_game(slot)`, `load_game(slot)`, `get_slot_info()` | Medium |
| `main.py` | `draw_save_menu()`, S key redirect, save menu event handling, quit uses `save_menu_slot` | High |

### Migration

`savegame.json` is replaced by `savegame_0.json`. On first launch with M6, the player will see "Empty" for all three slots (no migration from old single-slot save).

## Dependency Graph

```
Milestone 1 (Spaceship)
  └─► Milestone 2 (Farm Bots) — requires ship cargo for bot parts
  │
Milestone 3 (NPC Schedules)
  └─► Milestone 4 (Weather & Seasons) — requires day tracking
  │
Milestone 5 (Festivals) — requires NPC Schedules + Seasons
  │
Milestone 6 (Save Slots) — requires existing save/load infrastructure
```

Milestones 1-3 and 5-6 are largely independent of each other aside from dependency arrows above.

## Save Format

Each milestone adds new keys to `savegame.json`. Backward compatibility: `data.get("key", default)` for all new fields ensures old saves load without error.

### New save keys by milestone

| Milestone | New Keys |
|-----------|----------|
| M1 | `ship_tier`, `fuel`, `cargo` |
| M2 | `bots` (list of dicts) |
| M3 | None (NPC hearts/talked already saved) |
| M4 | `season_index`, `day_in_season`, `current_weather`, `weather_timer`, tile `crop_timer` changes to float |
| M5 | None (ephemeral event state) |
| M6 | Slot-based save files (`savegame_{0,1,2}.json`), `save_menu_slot` |

### Migration path

For Milestone 4, existing saves have integer `crop_timer`. Load code should handle:
```python
self.crop_timer = float(td["timer"])  # float conversion handles int → float seamlessly
```
This is a non-breaking change since JSON doesn't distinguish int/float when loaded.

---

## Summary of New Files

| File | Purpose |
|------|---------|
| `assets/fonts/space-mono.ttf` | Custom pixel font for all in-game text (M15) |

---

## Milestone 7 — Cooking & Recipes

**Goal:** Player can cook harvested crops into dishes for energy restoration and profit.

### Data Structures

**`src/constants.py`** — add `RECIPES` dict:
```python
RECIPES = {
    "glowroot_salad": {
        "name": "Glowroot Salad",
        "ingredients": {"glowroot": 2},
        "energy": 50,
        "sell_price": 80,
        "desc": "A crunchy, glowing salad",
    },
    # ... 8 recipes total combining different crops
}
```

**`src/game.py`** — new field:
```python
self.cooking_active = False
```

### Gameplay flow

1. **Farm** → press `C` → Kitchen overlay shows available recipes (those with all ingredients)
2. Each recipe shows: name, ingredients, energy restore, sell price
3. Press number key to cook → ingredients consumed, dish added to inventory, energy restored
4. **Shop** → dishes appear in a "Dishes" sell section below crops using `Z/X/C/V/B/N/M/P` keys
5. Dishes sell for more than the sum of their ingredients, creating a profit incentive

### Key binds

| Key | Action |
|-----|--------|
| `C` (farm) | Open kitchen / cooking menu |
| `1-8` (kitchen) | Cook recipe |
| `Z/X/C/V/B/N/M/P` (shop) | Sell dish |

### Files changed

| File | Change | Effort |
|------|--------|--------|
| `src/constants.py` | `RECIPES` dict with 8 recipes | Low |
| `src/game.py` | `cooking_active` field, `cook_recipe()`, `sell_dish()` methods | Medium |
| `main.py` | `draw_cooking()` UI, C key handler, cooking events, dish sell in shop | Medium |

---

## Milestone 8 — UI Polish

**Goal:** Quality-of-life visual improvements to make the game feel more polished and informative.

### Improvements

#### 1. Facing Tile Highlight
A subtle white highlight (50% alpha) appears on the tile the player is facing. This shows exactly which tile will be affected by a tool or interaction.

- Added to both **farm** and **spaceport** views
- Uses `Player.get_facing_tile()` to determine position
- Drawn right before the player sprite so it appears under the player's feet

#### 2. Quantity Modifier (Shift)
Hold **Shift** while pressing a buy/sell/cook key to perform the action 10× at once.

- **Shop (buy seeds):** `Shift + 1-6` buys 10×
- **Shop (sell crops):** `Shift + Q-Y` sells 10×  
- **Shop (sell dishes):** `Shift + Z-P` sells 10×
- **Bar:** `Shift + 1-4` buys 10× (capped by gold)
- **Kitchen:** `Shift + 1-8` cooks 10× (checks ingredient quantity)

Backend: `buy_item()`, `sell_item()`, `sell_dish()`, `buy_bar_item()`, `cook_recipe()` all accept a `count` parameter.

#### 3. Crop Info HUD
When on the farm and near a crop, a centered info line appears at the bottom of the screen showing:
- Crop name
- Growth stage (e.g. "Stage 2/4")
- Growth percentage
- Water status (watered / needs water)

Shown only when no overlays (shop, inventory, etc.) are open.

#### 4. NPC Location Markers
Colored dots drawn on the ground at each NPC's tile position on the spaceport:
- Filled circle matching the NPC's `color`
- White outline for visibility
- Updates with NPC movement (respects `pixel_offset_x/y`)

Makes NPCs easy to spot from across the map.

### Files Changed

| File | Change | Effort |
|------|--------|--------|
| `src/game.py` | `buy_item()`, `sell_item()`, `sell_dish()`, `buy_bar_item()`, `cook_recipe()` added `count` param | Medium |
| `main.py` | Facing tile highlight in `draw_farm()` + `draw_spaceport()`, crop info in `draw_hud()`, NPC markers in `draw_spaceport()`, Shift quantity in shop/bar/cooking events | Medium |

---

## Milestone 9 — Skill Progression

**Goal:** Player gains XP in 4 skills (Farming, Exploration, Cooking, Social) by performing actions. Leveling unlocks perks that improve gameplay.

### Data Structures

**`src/constants.py`** — `SKILLS` list (4 skills with name, color, desc) and `SKILL_PERKS` dict (perk name + description at levels 5, 10, 15, 20 for each skill).

### XP Sources

| Skill | Action | XP |
|-------|--------|----|
| Farming | Till soil / water | 2 |
| Farming | Plant seed | 3 |
| Farming | Harvest crop | 5 |
| Exploration | Launch to planet | 2 |
| Exploration | Scan planet | 3 |
| Exploration | Return from planet | 5 |
| Cooking | Cook a dish | 3 per dish |
| Social | Talk to NPC (first daily) | 1 |
| Social | Give a gift | 3 |
| Social | Get married | 20 |

### Perks

| Skill | Lv | Perk | Effect |
|-------|----|------|--------|
| Farming | 5 | Green Thumb | Crops grow 25% faster |
| Farming | 10 | Master Farmer | 20% chance of double harvest |
| Exploration | 5 | Fuel Saver | Planet travel costs 20% less fuel |
| Exploration | 10 | Scout | +1 cargo slot during expeditions |
| Exploration | 20 | Star Navigator | +2 planet turns per expedition |
| Cooking | 5 | Home Cook | Dishes give +25% energy |
| Cooking | 10 | Master Chef | Dishes sell for 25% more |
| Social | 5 | Friendly | +1 extra heart per gift |

### UI

Press **K** to open a skills overlay showing:
- Each skill: name, level, XP bar with current/total XP
- Checkmark badges for unlocked perks (★Lv5, ★Lv10, etc.)

### Files Changed

| File | Change | Effort |
|------|--------|--------|
| `src/constants.py` | `SKILLS` array, `SKILL_PERKS` dict | Low |
| `src/game.py` | `skills` / `skills_active` fields, `add_skill_xp()`, `get_skill_level()`, XP gain calls in 10 methods, perk effects in 7 methods, save/load | High |
| `main.py` | `draw_skills()` UI, K key handler, movement blocker | Medium |

## Summary of Key Binds

| Key | M1 | M2 | M3 | M4 | M5 | M6 | M7 | M9 |
|-----|----|----|----|----|----|----|----|----|
| `H` | Open hangar | — | — | — | — | — | — | — |
| `B` | — | Open bot shop | — | — | — | — | — | — |
| `G` | — | — | Toggle gift mode | — | — | — | — | — |
| `C` | — | — | — | — | — | — | Open kitchen | — |
| `K` | — | — | — | — | — | — | — | Toggle skills |
| `ENTER` | Launch/land | — | — | — | Submit festival | — | — | — |
| `1/2/3` | — | — | — | — | Choose crop in tasting | Save to slot | Cook recipe | — |
| `S` | — | — | — | — | — | Open save/load screen | — | — |
| `L + 1/2/3` | — | — | — | — | — | Load from slot | — | — |
| Arrow keys | — | — | — | — | Dance mini-game | — | — | — |

Existing keys (`M`, `I`, `SPACE`, `E`, `?`) remain unchanged.

---

## Milestone 10 — Farm Expansion & Buildings

**Goal:** Player can expand the tillable farm area and construct permanent buildings that provide utility (storage, auto-water, greenhouse, shipping).

### Land Expansion

The initial 10×14 tillable grid is too small for late-game. A signpost at the farm's southeast edge opens an expansion menu.

**Data — `src/constants.py`:**
```python
FARM_EXPANSIONS = [
    {"tier": 0, "cost": 0,     "cols": 14, "rows": 10, "off_x": 2, "off_y": 5},
    {"tier": 1, "cost": 1000,  "cols": 16, "rows": 12, "off_x": 1, "off_y": 4},
    {"tier": 2, "cost": 3000,  "cols": 18, "rows": 14, "off_x": 1, "off_y": 3},
    {"tier": 3, "cost": 6000,  "cols": 20, "rows": 16, "off_x": 0, "off_y": 2},
    {"tier": 4, "cost": 10000, "cols": 22, "rows": 18, "off_x": 0, "off_y": 1},
    {"tier": 5, "cost": 15000, "cols": 24, "rows": 20, "off_x": 0, "off_y": 0},
]
```

### Buildings

**Data — `src/constants.py`:**
```python
BUILDING_TYPES = {
    "storage_shed": {
        "name": "Storage Shed",
        "cost": 2000,
        "size": (3, 2),
        "desc": "+24 extra inventory slots",
        "color": (120, 80, 40),
    },
    "well": {
        "name": "Well",
        "cost": 1500,
        "size": (1, 1),
        "desc": "Auto-waters 4 adjacent tiles each day",
        "color": (60, 100, 180),
    },
    "greenhouse": {
        "name": "Greenhouse",
        "cost": 5000,
        "size": (4, 3),
        "desc": "Crops inside ignore season/weather penalties",
        "color": (150, 220, 150),
    },
    "shipping_bin": {
        "name": "Shipping Bin",
        "cost": 500,
        "size": (1, 1),
        "desc": "Drop items to sell overnight",
        "color": (180, 100, 60),
    },
}
```

### New GameState Fields

```python
self.farm_expansion_tier = 0
self.farm_cols = 14
self.farm_rows = 10
self.farm_off_x = 2
self.farm_off_y = 5
self.buildings = []                    # [{type, tile_x, tile_y}]
self.build_mode = None                 # building type string when placing
self.shipping_bin_contents = {}        # {item_name: count}
self.expand_menu_active = False
```

### New Methods

**`buy_expansion()`** — pay gold, increment tier, expand tiles array:
```python
def buy_expansion(self):
    next_tier = FARM_EXPANSIONS[self.farm_expansion_tier + 1]
    if self.player.gold < next_tier["cost"]:
        self.set_message(f"Need {next_tier['cost']}g to expand!")
        return
    self.player.gold -= next_tier["cost"]
    self.farm_expansion_tier += 1
    tier = FARM_EXPANSIONS[self.farm_expansion_tier]
    self.farm_cols = tier["cols"]
    self.farm_rows = tier["rows"]
    self.farm_off_x = tier["off_x"]
    self.farm_off_y = tier["off_y"]
    # Expand tiles array with new Tile objects for new cells
    old_rows, old_cols = len(self.tiles), len(self.tiles[0])
    for r in range(self.farm_rows):
        if r < old_rows:
            for c in range(old_cols, self.farm_cols):
                self.tiles[r].append(Tile(c, r))
        else:
            self.tiles.append([Tile(c, r) for c in range(self.farm_cols)])
    self.set_message(f"Farm expanded! ({self.farm_cols}x{self.farm_rows})")
```

**`buy_building(building_id)`** — pay cost, enter placement mode:
```python
def buy_building(self, building_id):
    bt = BUILDING_TYPES[building_id]
    if self.player.gold < bt["cost"]:
        self.set_message(f"Need {bt['cost']}g to build {bt['name']}!")
        return
    self.player.gold -= bt["cost"]
    self.build_mode = building_id
    self.set_message(f"Placed {bt['name']}! (Building system TBD)")
```

**`process_shipping_bin()`** — called in `advance_day()`:
- All items in `shipping_bin_contents` are sold at their base sell price
- Gold is added, bin is cleared, message shows total earned

**`apply_buildings()`** — called in `advance_day()`:
- Each **Well** auto-waters the 4 adjacent tiles (up/down/left/right) before growth
- **Greenhouse** tiles use growth_mod = 1.0 regardless of season/weather (checked in grow())

### Changes to Existing Systems

| System | Change |
|--------|--------|
| `main.py` `draw_farm()` | Use `game.farm_rows/cols/off_x/off_y` instead of `TILLABLE_ROWS/COLS` + `FARM_TILES_OFFSET_X/Y` |
| `main.py` `draw_farm()` | Render building sprites on the farm |
| `main.py` | New `draw_expand_menu()` panel with tier info/cost |
| `main.py` | Building place ghost (green outline on valid tiles) |
| `main.py` | Shipping bin interaction: pressing E on bin opens transfer UI |
| `main.py` | Building shop at spaceport (new panel or added to existing shop) |
| `main.py` `draw_hud()` | Show expanded inventory capacity if shed is built |
| `main.py` | Key: `V` to open building shop at spaceport; E on signpost to expand |
| `src/game.py` `get_tile_at()` | Use runtime `farm_off_x/y` instead of `FARM_TILES_OFFSET` |
| `src/game.py` `place_bot()` | Use runtime `farm_cols/rows` instead of `TILLABLE_COLS/ROWS` |
| `src/game.py` `run_bots()` | Use runtime dimensions |
| `src/sprites.py` | `get_building_surf(building_id)` — pixel-art for 4 buildings |
| Save/load | Persist `farm_expansion_tier`, `farm_cols/rows/off_x/off_y`, `buildings`, `shipping_bin_contents` |
| Save/load | Load expanded tiles (existing loop handles variable size via `data["tiles"]` length) |

### Effect on Crop Growth (Greenhouse)

When a tile is inside the greenhouse footprint, `grow()` ignores season and weather modifiers:
```python
def grow(self, growth_rate=1.0, in_greenhouse=False):
    if self.crop and self.watered:
        if not in_greenhouse:
            self.crop_timer += growth_rate  # applies season/weather mods
        else:
            self.crop_timer += 1.0  # neutral growth
```

### Files Changed

| File | Change | Effort |
|------|--------|--------|
| `src/constants.py` | `FARM_EXPANSIONS`, `BUILDING_TYPES` | Low |
| `src/game.py` | Dynamic farm dimensions, `buy_expansion()`, `buy_building()`, `process_shipping_bin()`, `apply_buildings()`, building placement methods | High |
| `main.py` | Runtime dimensions in all render/event code, building sprites, expand menu UI, building shop UI, shipping bin UI | High |
| `src/sprites.py` | `get_building_surf()` for 4 building types | Low |

---

## Milestone 11 — Animal Husbandry

**Goal:** Player can buy, feed, and care for alien animals that produce valuable goods (eggs, milk, wool).

### New NPC — Zoop at the Spaceport

A new pet-shop NPC stands near the bot workshop. Interact with Zoop to open the Exotic Pet Shop overlay.

### Animal Types

**Data — `src/constants.py`:**
```python
ANIMAL_TYPES = {
    "zap_chicken": {
        "name": "Zap-Chicken",
        "cost": 500,
        "produce": "Starlight Egg",
        "produce_interval": 2,
        "feed": {"glowroot": 1},
        "sell_price": 300,
        "color": (255, 220, 100),
        "desc": "A tiny electric chicken from Nebula.",
    },
    "moo_droid": {
        "name": "Moo-Droid",
        "cost": 1200,
        "produce": "Nebula Milk",
        "produce_interval": 3,
        "feed": {"cosmic_wheat": 2},
        "sell_price": 600,
        "color": (100, 200, 255),
        "desc": "A robotic bovine from the outer rings.",
    },
    "fluffalo": {
        "name": "Fluffalo",
        "cost": 2500,
        "produce": "Cosmic Wool",
        "produce_interval": 4,
        "feed": {"zargon_fruit": 1, "nebula_bloom": 1},
        "sell_price": 1200,
        "color": (255, 180, 255),
        "desc": "A giant fluffy creature from Bloom.",
    },
}
```

**Animal Products** — new items that exist in the player's inventory:

| Product | Sell Price | Used In |
|---------|-----------|---------|
| Starlight Egg | 75g | Cooking (new recipes), gifts |
| Nebula Milk | 100g | Cooking, gifts |
| Cosmic Wool | 200g | Crafting (M12), gifts |

### New Recipes (bonus for M11)

Add to existing `RECIPES` in constants:
```python
"starlight_omelette": {
    "name": "Starlight Omelette",
    "ingredients": {"starlight_melon": 1, "starlight_egg": 2},
    "energy": 120,
    "sell_price": 250,
    "desc": "A fluffy, glowing omelette",
},
"nebula_milkshake": {
    "name": "Nebula Milkshake",
    "ingredients": {"nebula_bloom": 1, "nebula_milk": 1},
    "energy": 140,
    "sell_price": 300,
    "desc": "A creamy, cosmic milkshake",
},
```

### New GameState Fields

```python
self.animals = []               # [{type, days_since_produce, fed_today}]
self.barn_capacity = 4          # upgraded via M10 building system
self.pet_shop_active = False
```

### New Methods

**`buy_animal(animal_id)`** — called from pet shop:
```python
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
```

**`feed_animals()`** — called in `advance_day()`:
- For each animal, check if player has the required feed item
- If yes, consume from inventory, set `fed_today = True`
- If no, set_message warns about unfed animals

**`produce_animals()`** — called in `advance_day()` after feeding:
- For fed animals, increment `days_since_produce`
- If `days_since_produce >= produce_interval`, add product to inventory, reset counter
- Unfed animals do not produce (counter does not increment)

**`get_animal_product_price(product_name)`** — lookup sell price for product.

### UI

- **Pet Shop overlay** — separate panel at spaceport, shows 3 animals with cost, product, feed requirements
- **Barn overlay** — accessed by pressing E on the barn building on the farm (M10)
  - List of animals with name, days until next produce, fed status
  - Shows products produced today
  - "Sell Animal" option with gold return (half cost)
- **HUD addition** — small animal icon + produce-ready indicator near energy/gold display when near barn

### Animal Rendering

- Animals rendered as small sprites near the barn building
- `get_animal_surf(type)` in sprites.py — 32×32 pixel art for each species
- Bouncy idle animation (simple 2-frame y-offset oscillation)

### Files Changed

| File | Change | Effort |
|------|--------|--------|
| `src/constants.py` | `ANIMAL_TYPES`, `RECIPES` additions (2 animal-based recipes) | Low |
| `src/game.py` | `animals` field, `buy_animal()`, `feed_animals()`, `produce_animals()`, pet shop integration in `interact()`, day advance integration | Medium |
| `main.py` | `draw_pet_shop()`, `draw_barn_overlay()`, animal render on farm, pet shop key handling | Medium |
| `src/sprites.py` | `get_animal_surf()` for 3 animal types, product item icons | Low |

---

## Milestone 12 — Artisan Crafting & Processing

**Goal:** Player can process crops and animal products into high-value artisan goods using processing machines on the farm.

### Overview

Unlike cooking (which restores energy), artisan crafting is purely profit-oriented. Some recipes are instant, others take multiple days to process (fermenting, aging).

### Artisan Recipes

**Data — `src/constants.py`:**
```python
ARTISAN_RECIPES = {
    "glowroot_chips": {
        "name": "Glowroot Chips",
        "ingredients": {"glowroot": 2},
        "sell_price": 100,
        "processing_days": 0,
        "desc": "Crunchy, savory chips",
    },
    "cosmic_flour": {
        "name": "Cosmic Flour",
        "ingredients": {"cosmic_wheat": 2},
        "sell_price": 150,
        "processing_days": 0,
        "desc": "Fine, sparkling flour",
    },
    "zargon_wine": {
        "name": "Zargon Wine",
        "ingredients": {"zargon_fruit": 3},
        "sell_price": 400,
        "processing_days": 3,
        "desc": "Aged purple wine",
    },
    "starlight_jam": {
        "name": "Starlight Jam",
        "ingredients": {"starlight_melon": 2},
        "sell_price": 350,
        "processing_days": 2,
        "desc": "Sweet jam that glows",
    },
    "nebula_perfume": {
        "name": "Nebula Perfume",
        "ingredients": {"nebula_bloom": 3},
        "sell_price": 600,
        "processing_days": 2,
        "desc": "Exquisite cosmic perfume",
    },
    "cosmic_wine": {
        "name": "Cosmic Wine",
        "ingredients": {"cosmic_wheat": 3, "zargon_fruit": 1},
        "sell_price": 500,
        "processing_days": 4,
        "desc": "Wine aged among the stars",
    },
    "woolen_scarf": {
        "name": "Woolen Scarf",
        "ingredients": {"cosmic_wool": 2},
        "sell_price": 500,
        "processing_days": 0,
        "desc": "A warm scarf from cosmic wool",
    },
    "aged_cheese": {
        "name": "Aged Nebula Cheese",
        "ingredients": {"nebula_milk": 3},
        "sell_price": 450,
        "processing_days": 3,
        "desc": "Sharp cheese aged in nebula dust",
    },
}
```

### Processing Queue

Rather than placing physical machines on the farm grid, use an abstract **Processing Queue** (like a crafting queue) accessible from the farmhouse or a workshop building.

### New GameState Fields

```python
self.crafting_active = False
self.processing_queue = []  # [{recipe_key, days_remaining, count}]
```

### New Methods

**`start_crafting(recipe_key, count=1)`** — called from crafting UI:
```python
def start_crafting(self, recipe_key, count=1):
    recipe = ARTISAN_RECIPES[recipe_key]
    for ing, need in recipe["ingredients"].items():
        if self.player.inventory.get(ing, 0) < need * count:
            self.set_message("Missing ingredients!")
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
```

**`process_crafting()`** — called in `advance_day()`:
- Decrement `days_remaining` for each item in the queue
- When an item reaches 0, add the finished good to inventory
- Set a summary message: "X items finished processing!"

**`collect_processed_goods()`** — called when player opens crafting UI:
- Check queue for completed items, move them to inventory if any were missed

### UI — Crafting Workshop Overlay

Accessible from the farmhouse (press `C` cycles between cooking and crafting, or use a new key like `V`).

- **Tabbed interface** or separate button: "Cook" / "Craft"
- **Craft tab** shows all artisan recipes with:
  - Recipe name, description, ingredients needed/available
  - Sell price and processing time (highlight "instant" vs "X days")
  - Number key to craft 1, Shift+key to craft 10
- **Processing Queue** section at the bottom:
  - Shows items in progress: name, days remaining, count
  - Auto-collects completed items on open

### Profit Margin Comparison

Display a "profit analysis" line per recipe showing:
- Input value (sum of ingredient sell prices)
- Output value (artisan sell price)
- Profit margin

This helps the player decide what to craft.

### Skill Perk Integration

Farming Lv15 perk "Soil Whisperer" could be adjusted, or a new Exploration perk could reduce processing time by 1 day (min 1).

### Files Changed

| File | Change | Effort |
|------|--------|--------|
| `src/constants.py` | `ARTISAN_RECIPES` dict | Low |
| `src/game.py` | `crafting_active`, `processing_queue`, `start_crafting()`, `process_crafting()`, `collect_processed_goods()`, integrate into `advance_day()` | Medium |
| `main.py` | Crafting tab in kitchen UI or separate `draw_crafting()` overlay, processing queue display, key handling (`V` for workshop or `C`-cycle) | Medium |

---

## Milestone 13 — Fishing

**Goal:** Player can fish at the spaceport pier for unique fish, with a timing-based mini-game and collection log.

### Fishing Location

A new spot on the spaceport map: the **Fishing Pier** at the east edge (tiles 25-29, 10-14). Press `E` at the pier to enter fishing mode.

### Fish Types

**Data — `src/constants.py`:**
```python
FISH_TYPES = {
    "nebula_trout": {
        "name": "Nebula Trout",
        "difficulty": 1,
        "sell_price": 50,
        "seasons": ["Nebula", "Void", "Bloom", "Solar"],  # any
        "weather": [],
        "time_slots": [],
        "color": (120, 180, 255),
    },
    "bloom_bass": {
        "name": "Bloom Bass",
        "difficulty": 1,
        "sell_price": 60,
        "seasons": ["Bloom"],
        "weather": [],
        "time_slots": [0, 1, 2, 3],
        "color": (100, 220, 100),
    },
    "solar_salmon": {
        "name": "Solar Salmon",
        "difficulty": 2,
        "sell_price": 120,
        "seasons": ["Solar"],
        "weather": [],
        "time_slots": [4, 5, 6],
        "color": (255, 180, 80),
    },
    "void_catfish": {
        "name": "Void Catfish",
        "difficulty": 2,
        "sell_price": 100,
        "seasons": ["Void"],
        "weather": ["Void Fog"],
        "time_slots": [6, 7],
        "color": (80, 60, 120),
    },
    "starlight_sturgeon": {
        "name": "Starlight Sturgeon",
        "difficulty": 3,
        "sell_price": 250,
        "seasons": ["Nebula", "Bloom", "Solar"],
        "weather": [],
        "time_slots": [6, 7, 0, 1],
        "color": (200, 220, 255),
    },
    "cosmic_koi": {
        "name": "Cosmic Koi",
        "difficulty": 4,
        "sell_price": 500,
        "seasons": ["Nebula"],
        "weather": ["Meteor Shower"],
        "time_slots": [2, 3],
        "color": (255, 150, 200),
    },
}
```

**Conditions for catching each fish:**
- Season, weather, and time slot must match the fish's requirements
- Empty arrays = no restriction
- If multiple fish match, pick randomly weighted by difficulty (harder = rarer)

### Fishing Mini-Game

A simple timing-based sequence:

1. **Cast** — Press `SPACE` while facing water → line casts, bobber appears
2. **Wait** — Bobber floats. After 1-3 random seconds, bobber shakes (visual + sound cue)
3. **Hook** — Press `SPACE` when bobber shakes → fish hooked!
   - Miss the window (0.5s) → fish escapes, try again
4. **Reel** — A vertical progress bar appears. Press `SPACE` repeatedly to fill it.
   - Each press adds progress. Progress drains continuously at rate = `difficulty * 0.3` / frame
   - If bar fills → caught! If bar empties → fish escapes
5. **Result** — Show fish sprite, name, size flavor text ("A tiny Nebula Trout!"), add to inventory

### Fish Collection

Track which fish the player has caught. Display as a log with empty/ filled silhouettes.

```python
self.fish_collection = {}  # {fish_id: True/False}
self.fish_caught_total = 0
```

Collection log accessible from the skills screen (new tab) or from a sign at the pier.

### New GameState Fields

```python
self.fishing_active = False
self.fishing_state = "idle"         # "casting", "waiting", "hooked", "reeling", "caught"
self.fishing_timer = 0              # countdown frames for bite
self.fishing_bite_window = 0        # frames remaining to press SPACE after bite
self.fishing_progress = 0.0         # 0-1 reel progress
self.fishing_current_fish = None    # fish_id currently hooked, or None
self.fishing_caught_fish = None     # fish just caught for display
```

### New Methods

```python
def start_fishing(self)              # enter fishing mode, set state to "casting"
def cast_line(self)                  # set state to "waiting", random timer
def hook_fish(self)                  # determine which fish, enter "reeling"
def reel_press(self)                 # SPACE during reeling → add progress
def update_fishing(self)             # called each frame, ticks timers, drains progress
def catch_fish(self)                 # add to inventory, collection, show result
def escape_fish(self)                # reset, show "It got away!"
```

**`update_fishing()`** is called from the render loop (not `advance_day`) — it works in real-time, not turn-based.

### Fishing Display (overlay)

- Dark water background with gentle wave animation
- Bobber sprite at center (bobs up/down slowly)
- When waiting: wavy line "~" particles for atmosphere
- When hooked: splash particles, progress bar on right side
- When caught: fish sprite + name + size text, press SPACE to dismiss
- ESC to exit fishing mode early

### New Recipes (bonus for M13)

Add to `RECIPES`:
```python
"fish_tacos": {
    "name": "Galaxy Fish Tacos",
    "ingredients": {"nebula_trout": 1, "cosmic_wheat": 1},
    "energy": 100,
    "sell_price": 150,
    "desc": "Tacos with a cosmic twist",
},
"sushi_platter": {
    "name": "Nebula Sushi Platter",
    "ingredients": {"solar_salmon": 1, "nebula_bloom": 1},
    "energy": 160,
    "sell_price": 300,
    "desc": "Raw fish on seasoned cosmic rice",
},
```

### Skill Synergy

- Exploration skill grants fishing bonuses:
  - Lv5: Fish bite 20% faster (less waiting)
  - Lv10: Reel progress drains 20% slower
  - Lv15: Rare fish are 2x more likely
  - Lv20: Fish sell for 50% more

### Files Changed

| File | Change | Effort |
|------|--------|--------|
| `src/constants.py` | `FISH_TYPES`, new recipes | Low |
| `src/game.py` | Fishing state fields, `start_fishing()`, `cast_line()`, `hook_fish()`, `reel_press()`, `update_fishing()`, `catch_fish()`, `escape_fish()`, fish collection | High |
| `main.py` | `draw_fishing()` overlay, fishing mini-game rendering, pier interaction, fishing event handling (SPACE during game), ESC to exit | High |
| `src/sprites.py` | `get_fish_surf(fish_id)`, `get_bobber_surf()` | Low |
| `src/game.py` | Exploration skill perk integration (faster bite, slower drain, rare bonus, sell bonus) | Low |

---

## Milestone 14 — Town Reputation & Daily Quests

**Goal:** Player earns reputation by completing daily quests and contributing to the spaceport, unlocking rank-based perks.

### Town Ranks

**Data — `src/constants.py`:**
```python
TOWN_RANKS = [
    {"level": 0, "name": "Visitor",    "rep_needed": 0,    "perk": "No perks"},
    {"level": 1, "name": "Resident",   "rep_needed": 50,   "perk": "10% discount at Zara's shop"},
    {"level": 2, "name": "Citizen",    "rep_needed": 150,  "perk": "Traveling Merchant visits"},
    {"level": 3, "name": "Benefactor", "rep_needed": 300,  "perk": "Upgraded bots available"},
    {"level": 4, "name": "Hero",       "rep_needed": 500,  "perk": "Festival rewards doubled"},
    {"level": 5, "name": "Legend",     "rep_needed": 1000, "perk": "Unlock Spaceport Observatory"},
]
```

### Reputation Sources

| Action | Rep Gained | Notes |
|--------|-----------|-------|
| Complete a quest | 15-30 (depends on difficulty) | Primary source |
| Give a gift to NPC | 2 per heart gained | Ties to M3 |
| Win a festival | 25 | Ties to M5 |
| Sell items at shop | 1 per 100g earned | Small passive gain |

### Daily Quests

**Quest generation** — called in `advance_day()`:
- Generate 3 quests from the pool of quest types
- Each quest has a deadline (same day, complete before sleeping)

**Quest types:**

```python
QUEST_TEMPLATES = [
    {
        "id": "deliver",
        "name": "Delivery",
        "desc": "Bring {count}x {item} to {npc}",
        "min_count": 1, "max_count": 5,
        "reward_gold": (50, 200),
        "reward_rep": 15,
    },
    {
        "id": "harvest",
        "name": "Harvest",
        "desc": "Harvest {count} mature {crop} crops",
        "min_count": 5, "max_count": 20,
        "reward_gold": (100, 500),
        "reward_rep": 20,
    },
    {
        "id": "fish",
        "name": "Fishing",
        "desc": "Catch {count} fish at the pier",
        "min_count": 1, "max_count": 5,
        "reward_gold": (80, 300),
        "reward_rep": 25,
    },
    {
        "id": "cook",
        "name": "Cooking",
        "desc": "Cook {count}x {dish}",
        "min_count": 1, "max_count": 5,
        "reward_gold": (100, 400),
        "reward_rep": 20,
    },
]
```

**Quest tracking:**
- Active quests stored in `active_quests` list with `{template_id, params, progress, completed}`
- Progress is checked at relevant actions:
  - Delivery: pressing E on target NPC while quest is active checks inventory and completes
  - Harvest: increment on successful harvest, check at threshold
  - Fish: increment on successful catch
  - Cook: increment on successful cook

### Traveling Merchant

When the player reaches Rank 2 ("Citizen"), a traveling merchant named "Cosmo" visits the spaceport every 7 days.

- Cosmo appears on the spaceport map (tile 5, 8) on visit days
- His inventory is randomly generated from rare items:
  - Rare seeds not normally available
  - Unique furniture/decorations
  - Artifact items that sell for high prices
  - Fishing bait (increases rare fish chance for the day)

```python
def generate_merchant_items(self):
    pool = [
        {"name": "Ancient Seed", "price": 2000, "desc": "Grows into something unknown..."},
        {"name": "Nebula Crystal", "price": 500, "desc": "A pretty decorative crystal"},
        {"name": "Lucky Charm", "price": 1000, "desc": "+1 luck for the day"},
        {"name": "Golden Bait", "price": 300, "desc": "Rare fish love this"},
        {"name": "Cosmic Coffee Machine", "price": 5000, "desc": "Free coffee daily!"},
    ]
    self.merchant_items = random.sample(pool, 3)
```

### New GameState Fields

```python
self.reputation = 0
self.active_quests = []             # [{template_id, params, progress, completed, reward_gold, reward_rep}]
self.completed_quests = 0
self.quest_board_active = False
self.merchant_visit_day = -1        # next day Cosmo visits (set in advance_day based on rank)
self.merchant_active = False
self.merchant_items = []            # [{name, price, desc}]
```

### New Methods

```python
def add_reputation(self, amount)                         # add rep, check rank unlock
def get_rank(self)                                       # return current rank level
def get_rank_perks(self)                                 # list of unlocked perks
def generate_daily_quests(self)                          # called in advance_day()
def accept_quest(self, index)                            # add to active quests
def check_quest_progress(self, quest_type, params)       # update quest progress
def complete_quest(self, index)                          # grant rewards, remove quest
def update_merchant(self)                                # called in advance_day()
def generate_merchant_items(self)                        # random merchant inventory
```

### Rank Perk Implementation

| Rank | Perk | Implementation |
|------|------|---------------|
| 1 | 10% shop discount | In `buy_item()`, multiply cost by 0.9 when rank >= 1 |
| 2 | Traveling Merchant | `update_merchant()` sets `merchant_active = True` every 7 days |
| 3 | Upgraded bots | Add 2 new bot types to `BOT_TYPES` with higher range/efficiency (loaded on rank up) |
| 4 | Double festival rewards | In `end_festival()`, multiply gold reward by 2 |
| 5 | Spaceport Observatory | Add new area tile on spaceport map with special interactions |

### UI Changes

- **Quest Board** — new overlay at spaceport (signpost near Zara's shop)
  - Shows 3 daily quests with description, reward gold, rep
  - Highlighted quest shows more detail
  - `1/2/3` to accept, ESC to close
  - Completed quests show "✓" — press key to claim reward

- **HUD — Quest Tracker** — shown when away from quest board:
  - Small section on the right side showing active quest(s) with progress bar
  - Example: "Harvest 5/20 Cosmic Wheat ████░░░░░"

- **Town Rank Display** — shown in HUD or in a new "Town" tab:
  - Current rank name and progress to next rank
  - List of unlocked perks

- **Traveling Merchant** — when Cosmo is present:
  - Special NPC sprite on spaceport
  - E to interact → merchant shop overlay (same panel style as Zara's shop)
  - Shows 3 items with price and description
  - Number keys to buy, ESC to exit

### Files Changed

| File | Change | Effort |
|------|--------|--------|
| `src/constants.py` | `TOWN_RANKS`, `QUEST_TEMPLATES` | Low |
| `src/game.py` | Reputation/quest fields, `add_reputation()`, `get_rank()`, `generate_daily_quests()`, `accept_quest()`, `check_quest_progress()`, `complete_quest()`, merchant system, `advance_day()` integration | High |
| `main.py` | `draw_quest_board()`, `draw_merchant_shop()`, quest tracker HUD, rank display, key handling for quests/merchant, E interaction on quest board + merchant NPC | High |

---

## Dependency Graph (updated)

```
Milestone 1  (Spaceship)
Milestone 2  (Farm Bots)
  │
Milestone 3  (NPC Schedules & Gifts)
  │
Milestone 4  (Weather & Seasons)
  │
Milestone 5  (Festivals)
  │
Milestone 6  (Save Slots)
  │
Milestone 7  (Cooking)
  │
Milestone 8  (UI Polish)
  │
Milestone 9  (Skills)
  │
Milestone 10 (Farm Expansion) — requires dynamic tile dimensions
  │
Milestone 11 (Animals) — requires M10 barn placement or farm space
  │
Milestone 12 (Artisan Crafting) — uses M10 crops + M11 animal products
  │
Milestone 13 (Fishing) — standalone, adds fish recipes to M7
  │
Milestone 14 (Town Reputation) — ties into M3 gifts, M5 festivals, M13 fishing
  │
Milestone 15 (Graphics Overhaul) — touches every visual function, no code deps
```

Milestones 10, 11, and 12 form a **economic progression chain**: expand farm → raise animals → process goods. Milestones 13 and 14 are largely independent. Milestone 15 touches nearly every visual file and is best done last to avoid merge conflicts, but has zero code dependency on M10-M14.

---

## Milestone 15 — Graphics Overhaul: Fonts, Sprites & Polish

**Goal:** Replace the programmer-art aesthetic with a cohesive 16-bit look: a custom space-themed font, redrawn 32×32 sprites with more detail, UI panel styling, and visual polish across all screens.

### Font Replacement

**Current:** `pygame.font.SysFont("monospace", 14/18/24)` — system monospace, no character.

**Target:** Load a custom pixel font `.ttf` bundled with the game.

**Font choice — "Space Mono" or similar free pixel font:**
- **Space Mono** (Google Fonts, OFL license) — a fixed-width sci-fi font with round glyphs
- Fallback: **Perfect DOS VGA 437** — classic 8×16 pixel font, great for retro games
- Bundle the `.ttf` file as `assets/fonts/space-mono.ttf` (or similar)

**Implementation:**
```python
# In main.py, replace SysFont with loaded TTF:
FONT_PATH = os.path.join(os.path.dirname(__file__), "assets", "fonts", "space-mono.ttf")
font_small = pygame.font.Font(FONT_PATH, 14)
font_med = pygame.font.Font(FONT_PATH, 18)
font_large = pygame.font.Font(FONT_PATH, 24)
```

If the font file is missing, fall back gracefully to `pygame.font.SysFont("monospace", size)`.

**Font sizing considerations:**
- A pixel font at 14px may render differently than monospace — test and adjust sizes
- Some glyphs (arrows, special chars) may be missing — test the `?`, `♥`, `→` characters used in the game
- If `♥` is missing, use a text replacement like `<3` or draw a small heart surface

### Sprite Overhaul — 16-Bit Detail Upgrade

**Current sprites (in `src/sprites.py`):**
- Mostly simple `draw_box()` calls and `set_pixel()` for pixel art
- 32×32 tiles with basic shapes and flat colors
- Functions: `get_tile_surf()`, `get_crop_icon()`, `get_crop_surf()`, `get_bot_surf()`, `get_ship_surf()`, `get_astronaut_surf()`, `get_npc_surf()`, `get_building_surf()`, `get_item_icon()`, `get_heart_surf()`

**Target:** Redraw each sprite with:
- Shading / highlights (at least 3 tones per color instead of 1-2)
- Anti-aliased edges (via careful pixel placement, not AA filter)
- Small detail accents (buttons, visor reflections, panel lines)
- Consistent 16-bit palette (see palette section below)

**Sprite priority list (high → low):**

| Priority | Sprite | Current | Target |
|----------|--------|---------|--------|
| P0 | Player (astronaut) | 4-direction colored box with visor | Full helmet, suit details, boots, 3-frame idle bob |
| P0 | Tiles (soil, water, grass) | Flat colored rectangles | Textured soil, rippled water, grass with tiny flowers |
| P1 | Crops (6 types, 3-5 stages) | Simple colored boxes with dots | Recognizable plant shapes: roots, vines, fruits, leaves |
| P1 | NPCs | Colored humanoid boxes | Distinct outfits, hair, accessories per NPC |
| P2 | Bots | Rectangular boxes with lights | Panel lines, antenna, glowing indicator light |
| P2 | Buildings | Simple colored rectangles | Roof overhangs, windows, doors, shadows |
| P3 | Ship (3 tiers) | Basic geometric shapes | Wing details, cockpit, engine glow |
| P3 | UI icons / items | Tiny colored squares | Recognizable item shapes (seed bag, crop icon) |
| P3 | Heart / Festival / Misc | Simple shapes | Animated hearts, festival banners |

**Sprite architecture upgrade:**
- Most sprites are generated via `make_surface()` + `draw_box()` / `set_pixel()`
- For 16-bit quality, consider **pre-drawing sprites as pixel data arrays** rather than calling many individual `set_pixel()` calls
- New helper: `blit_sprite(surface, pixels_2d, x, y, palette)` where `pixels_2d` is a 2D array of palette indices
- This makes sprites easier to author and edit

**Example pixel data approach:**
```python
# Instead of 20 set_pixel calls, use a 2D array:
PLAYER_SPRITE = [
    "  WWWW  ",
    " WBBBBW ",
    "WBBBBBBW",
    "WBYBBYBW",
    "WBBBBBBW",
    " WBBBBW ",
    "  RRWW  ",
    " RR  RR ",
]
# Where W=white, B=blue, Y=yellow, R=red mapped through a palette dict
# In practice, use int indices into a palette list for compactness
```

**Palette system:**
```python
# Central palette for consistent colors across sprites
PALETTE = {
    "skin": [(255, 200, 170), (235, 180, 150), (200, 150, 120)],
    "suit_white": [(240, 242, 245), (210, 215, 220), (180, 185, 190)],
    "visor_blue": [(80, 200, 255), (50, 160, 220), (20, 100, 180)],
    "metal_gray": [(200, 200, 200), (160, 160, 160), (120, 120, 120)],
    # ... per crop, per bot, per NPC
}
```

### UI Panel Styling

**Current panels** (shop, inventory, save, etc.):
- Dark blue rectangles (`(10, 10, 30)`) with thin colored borders
- Flat, utilitarian look

**Target panel style:**
- 9-slice bordered panels with a subtle gradient (top edge lighter, bottom darker)
- Rounded corner effect (via corner pixel patterns)
- Title bar with accent color and subtle underline
- Button-style list items with hover/select highlight (currently implemented with colored rects)
- Drop shadow behind panels (semi-transparent black rect offset by 2-3px)

**New helper in sprites.py:**
```python
def draw_panel(surface, x, y, w, h, border_color, title=None):
    """Draw a styled 16-bit panel with 9-slice border and optional title bar."""
    # 1. Drop shadow
    shadow = pygame.Surface((w, h))
    shadow.set_alpha(60)
    shadow.fill((0, 0, 0))
    surface.blit(shadow, (x + 3, y + 3))
    # 2. Background gradient (top to bottom)
    for i in range(h):
        t = i / h
        r = lerp(15, 8, t)
        g = lerp(20, 10, t)
        b = lerp(40, 25, t)
        pygame.draw.line(surface, (r, g, b), (x, y + i), (x + w, y + i))
    # 3. Border
    pygame.draw.rect(surface, border_color, (x, y, w, h), 2)
    # 4. Inner highlight (top edge lighter)
    pygame.draw.line(surface, (r+30, g+30, b+30), (x+2, y+2), (x+w-3, y+2))
```

### Screen-Level Polish

| Screen | Polish |
|--------|--------|
| **Farm** | Grass texture variation (2-3 grass tile variants), animated water on watered tiles, subtle parallax for background stars, crop leaves rustle (2-frame animation) |
| **Spaceport** | Animated neon signs on buildings, floating particles (space dust), NPC nameplates with heart level |
| **Planet Explore** | Animated background (slow color shift), ground with per-planet texture, blinking stars |
| **Festivals** | Confetti particles, banner decorations on screen edges, spotlight effect on judges |
| **Overlay transitions** | Fade-in (alpha ramp from 0→180 over 10 frames) when opening shops/menus |

### Screen Shake & Juice

Add subtle screen effects to make actions feel impactful:
- **Hoe/Water/Scythe:** 2px vertical shake on use
- **Harvest:** 4px shake + 5 sparkle particles
- **Festival win:** Screen flash white (100ms) + 20 confetti particles
- **Ship launch:** 6px shake, screen flash, fade to black

```python
# In GameState:
self.screen_shake = 0          # frames remaining
self.screen_shake_intensity = 0
self.screen_flash = 0          # frames remaining
self.screen_flash_color = (255, 255, 255)

# In main.py render loop:
if game.screen_shake > 0:
    offset_x = random.randint(-game.screen_shake_intensity, game.screen_shake_intensity)
    offset_y = random.randint(-game.screen_shake_intensity, game.screen_shake_intensity)
    screen.blit(offscreen_buffer, (offset_x, offset_y))  # render to buffer first
    game.screen_shake -= 1
if game.screen_flash > 0:
    flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    flash.set_alpha(100)
    flash.fill(game.screen_flash_color)
    screen.blit(flash, (0, 0))
    game.screen_flash -= 1
```

### Particle System Enhancement

**Current:** `self.particles` is a list of dicts with `x, y, color, life, max_life, size, vx, vy`. Drawn as simple colored squares.

**Upgrade:**
- Particle **types**: sparkle (star shape), leaf (small oval), smoke (fading circle), confetti (colored rectangle)
- Particle **gravity**: some particles fall (gravity = 0.1 px/frame²)
- Particle **fade**: alpha interpolation from 255 → 0 over lifetime
- Particle **size variation**: random initial size 1-4px
- Particle **color cycling**: for festival confetti, cycle through rainbow colors

```python
# New particle types:
PARTICLE_TYPES = {
    "sparkle": {"shape": "star",  "gravity": 0,   "fade": True,  "size_range": (1, 3)},
    "leaf":    {"shape": "oval",  "gravity": 0.2, "fade": True,  "size_range": (2, 4)},
    "smoke":   {"shape": "circle","gravity": -0.05,"fade": True, "size_range": (3, 6)},
    "confetti":{"shape": "rect",  "gravity": 0.1, "fade": False, "size_range": (2, 4)},
}
```

### Files Changed

| File | Change | Effort |
|------|--------|--------|
| `assets/fonts/space-mono.ttf` | Bundle the font file (git LFS or raw URL) | Low |
| `main.py` | Replace `SysFont` with `Font` from TTF, update all `draw_text()` calls, add screen shake/flash, fade transitions, particle upgrade | Medium |
| `src/sprites.py` | Complete sprite overhaul: pixel data arrays for player, NPCs, crops, tiles, bots, buildings, ship, icons. Add `draw_panel()`, palette system. | High |
| `src/game.py` | Add `screen_shake`, `screen_flash`, `screen_flash_color` fields, particle type support | Medium |
| `src/constants.py` | No changes needed (colors defined in sprites) | None |

### Dependency Note

M15 touches almost every visual function in the codebase. It is recommended to implement **after M10-M14** to avoid merge conflicts with new features that also add sprites/UI. However, it has **no code dependency** on M10-M14 — it can be started at any time.

---

## Summary of Key Binds (M10-M15)

| Key | M10 | M11 | M12 | M13 | M14 |
|-----|-----|-----|-----|-----|-----|
| `V` (spaceport) | Open building shop | — | — | — | — |
| `E` on signpost | Open expansion menu | — | — | — | — |
| `E` near barn | — | Open barn overlay | — | — | — |
| `E` near pier | — | — | — | Start fishing | — |
| `E` on quest board | — | — | — | — | Open quests |
| `E` on merchant | — | — | — | — | Open merchant shop |
| `C` (farm, cycle) | — | — | Toggle cook/craft | — | — |
| `SPACE` (fishing) | — | — | — | Cast / Hook / Reel | — |
| `1/2/3` (quests) | — | — | — | — | Accept quest |
| `1/2/3` (merchant) | — | — | — | — | Buy item |

---

## Summary of New Files

| File | Purpose |
|------|---------|
| `assets/fonts/space-mono.ttf` | Custom pixel font for all in-game text (M15) |
