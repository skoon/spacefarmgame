# Space Farm Galaxy — Milestone Plan

## Overview

Five major features, ordered by dependency. Each milestone builds on the prior.
Estimated effort: **Low** (< 50 LoC changed), **Medium** (50–200), **High** (200–500).

---

## Milestone 1 — Spaceship Hangar & Planet Exploration

**Goal:** Player can build a spaceship, fly to procedurally generated planets, find rare seeds/resources, and return.

### New Data Structures

**`src/constants.py`** — add:
```python
SHIP_TIERS = [
    {"name": "Scout Pod",  "fuel_capacity": 50, "cargo_slots": 4,  "cost": 0},
    {"name": "Hauler MK2", "fuel_capacity": 120,"cargo_slots": 10, "cost": 2000},
    {"name": "Star Cruiser","fuel_capacity": 300,"cargo_slots": 20, "cost": 8000},
]

PLANET_TEMPLATES = [
    {"name": "Xylos Prime", "biome": "crystal", "hazard": 0.1, "crop_bonus": "cosmic_wheat", "color": (180,100,255)},
    {"name": "Magma-7",     "biome": "volcanic","hazard": 0.3, "crop_bonus": "zargon_fruit", "color": (255,80,80)},
    {"name": "Aquaris",     "biome": "ocean",   "hazard": 0.0, "crop_bonus": "glowroot",     "color": (60,150,255)},
    {"name": "Verdantia",   "biome": "jungle",  "hazard": 0.2, "crop_bonus": "nebula_bloom", "color": (80,220,100)},
]

PLANET_EXCLUSIVE_SEEDS = {
    "Xylos Prime": ["Starlight Melon Seeds"],    # 30% chance to find
    "Magma-7":     ["Quasar Berry Seeds"],
}
```

**`src/game.py`** — new fields on `GameState`:
```python
self.ship_tier = 0            # index into SHIP_TIERS
self.fuel = 0                 # current fuel
self.fuel_max = 0             # from SHIP_TIERS[s].fuel_capacity
self.cargo = []               # list of dicts {item, count}
self.cargo_max = 0            # from SHIP_TIERS[s].cargo_slots
self.current_planet = None    # str or None (flying or landed)
self.planet_seeds = {}        # {crop_key: count} collected on current planet
self.player.current_map = "farm" | "spaceport" | "planet_<name>"
```

### Files to change

| File | Change | Effort |
|------|--------|--------|
| `src/constants.py` | Add `SHIP_TIERS`, `PLANET_TEMPLATES`, `PLANET_EXCLUSIVE_SEEDS` | Low |
| `src/game.py` | Add ship fields + methods: `build_ship()`, `launch_sequence()`, `generate_planet()`, `collect_resource()`, `return_to_port()` | High |
| `main.py` | Add `draw_planet_screen()` with biome-colored terrain, `draw_hangar_ui()` for ship management | Medium |
| `main.py` | Key binds: `H` for hangar, `ENTER` to launch/land | Low |
| `main.py` | Save/load: persist ship fields + cargo in `save_game()`/`load_game()` | Low |
| `src/sprites.py` | `get_planet_bg(biome)`, `get_ship_surf(tier)` | Medium |

### Key mechanics

- **Fuel** consumed per expedition (`fuel -= random.randint(5, 15)`). Refuel at spaceport shop (1g per unit).
- **Planet exploration** = 5–8 turns on planet screen. Each turn you pick a direction card; may find seeds, fuel pods, or trigger a hazard event (costs energy).
- **Cargo** slots limit how much you bring back. Excess items are lost on return.
- **Save compatibility**: existing saves start with 0 fuel and ship_tier=0 — no new-game penalty.

### Ship upgrade flow

1. Player saves gold, goes to spaceport, presses `H`
2. Hangar UI shows current ship + upgrade cost
3. Pay gold → ship_tier++ → fuel_max and cargo_max increase
4. New sprite rendered for higher tier

---

## Milestone 2 — Automated Farm Bots

**Goal:** Player can buy or craft bots that autonomously water/harvest crops, freeing the player for exploration.

### New Data Structures

**`src/constants.py`** — add:
```python
BOT_TYPES = {
    "sprout_bot": {
        "name": "Sprout-Bot",
        "action": "water",
        "range": 3,            # tiles radius from bot position
        "cost": 500,
        "upkeep": 5,           # gold per day
        "color": (100, 200, 255),
    },
    "harvest_bot": {
        "name": "Harvest-Bot",
        "action": "harvest",
        "range": 2,
        "cost": 1200,
        "upkeep": 10,
        "color": (255, 200, 100),
    },
}
```

**`src/game.py`** — new class:
```python
class FarmBot:
    def __init__(self, bot_type, farm_tile_x, farm_tile_y):
        self.bot_type = bot_type          # "sprout_bot" | "harvest_bot"
        self.tile_x = farm_tile_x         # 0..13 (tile array coords)
        self.tile_y = farm_tile_y
        self.active = True
```

New fields on `GameState`:
```python
self.bots = []                # list[FarmBot]
self.total_upkeep = 0         # sum of bot upkeep costs
```

### Files to change

| File | Change | Effort |
|------|--------|--------|
| `src/constants.py` | Add `BOT_TYPES` dict | Low |
| `src/game.py` | Add `FarmBot` class, `buy_bot()`, `remove_bot()`, `run_bots()` called in `advance_day()`, deduct upkeep from gold | Medium |
| `main.py` | Add `draw_bot_shop()` in spaceport (or as shop tab), `draw_bots_on_farm()` in `draw_farm()`, bot placement cursor | Medium |
| `main.py` | Key: `B` opens bot shop (rebind farm sleep to `F`?), `CLICK` to place | Low |
| `src/sprites.py` | `get_bot_surf(bot_type)` — small floating robot sprite | Low |
| `main.py` | Save/load: persist `bots` list | Low |

### Bot behavior (`run_bots()`)

Called at end of `advance_day()`, before tile growth:
- **Sprout-Bot**: For each tile within `range` that is `soil_state == "tilled"` and `watered == False`, call `tile.water()`. Max 1 action per day per bot.
- **Harvest-Bot**: For each mature tile within `range`, collect harvest directly (gold + item to player inventory).
- If `player.gold < total_upkeep` on day advance, deactivate all bots and show "Bots ran out of power!"

### Placement flow

1. Buy bot from spaceport shop → enters placement mode
2. Farm map shows a ghost cursor
3. Press E on a tillable tile → bot placed there
4. Bot rendered as small floating sprite above tile

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

## Dependency Graph

```
Milestone 1 (Spaceship)
  └─► Milestone 2 (Farm Bots) — requires ship cargo for bot parts
  │
Milestone 3 (NPC Schedules)
  └─► Milestone 4 (Weather & Seasons) — requires day tracking
  │
Milestone 5 (Festivals) — requires NPC Schedules + Seasons
```

All milestones can be built in parallel after Milestone 1 and 3 are complete, since they touch largely independent systems.

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

| Key | M1 | M2 | M3 | M4 | M5 |
|-----|----|----|----|----|----|
| `H` | Open hangar | — | — | — | — |
| `B` | — | Open bot shop | — | — | — |
| `G` | — | — | Toggle gift mode | — | — |
| `ENTER` | Launch/land | — | — | — | Submit festival |
| `1/2/3` | — | — | — | — | Choose crop in tasting |
| Arrow keys | — | — | — | — | Dance mini-game |

Existing keys (`M`, `I`, `S`, `SPACE`, `E`, `?`) remain unchanged.
