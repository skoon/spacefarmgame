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

```python
# In update_movement():
if self.move_target:
    target_px = self.move_target[0] * TILE_SIZE
    target_py = self.move_target[1] * TILE_SIZE
    dx = target_px - self.tile_x * TILE_SIZE
    dy = target_py - self.tile_y * TILE_SIZE
    speed = 1  # pixel per frame
    if abs(dx) <= speed and abs(dy) <= speed:
        self.tile_x, self.tile_y = self.move_target
        self.move_target = None
    else:
        # move toward target
        pass  # update pixel offsets for smooth animation
```

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
| (no new files) | All changes are in existing files |

## Summary of Key Binds

| Key | M1 | M2 | M3 | M4 | M5 | M6 |
|-----|----|----|----|----|----|----|
| `H` | Open hangar | — | — | — | — | — |
| `B` | — | Open bot shop | — | — | — | — |
| `G` | — | — | Toggle gift mode | — | — | — |
| `ENTER` | Launch/land | — | — | — | Submit festival | — |
| `1/2/3` | — | — | — | — | Choose crop in tasting | Save to slot |
| `S` | — | — | — | — | — | Open save/load screen |
| `L + 1/2/3` | — | — | — | — | — | Load from slot |
| Arrow keys | — | — | — | — | Dance mini-game | — |

Existing keys (`M`, `I`, `SPACE`, `E`, `?`) remain unchanged.
