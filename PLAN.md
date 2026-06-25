# Space Farm Galaxy — Milestone Plan

## Overview

**All 20 milestones are now implemented.** The game's mechanics are complete, and the visual polish phase delivers cohesive 16-bit pixel art across every sprite, NPC, building, item icon, and environment tile.

---

## Milestone 1 — Spaceship Hangar & Planet Exploration ✓

**Goal:** Player can build a spaceship, fly to procedurally generated planets, find rare seeds/resources, and return.

### Data Structures

**`src/constants.py`:**
- `SHIP_TIERS`: 3 tiers — Scout Pod (0g, 50 fuel, 4 cargo), Hauler MK2 (2000g, 120 fuel, 10 cargo), Star Cruiser (8000g, 300 fuel, 20 cargo)
- `PLANETS`: 4 destinations — Xylos Prime (15 fuel), Magma-7 (25), Aquaris (10), Verdantia (20). Each has a `color`, `desc`, and `finds` list of seed items.
- `PLANET_EXCLUSIVE_SEEDS`: rare seeds per planet (e.g. Starlight Melon Seeds on Xylos Prime)

**`src/game/exploration.py`** — new fields on `GameState`:
```python
self.ship_tier = 0
self.fuel = 50
self.ship_cargo = {}
self.hangar_active = False
self.current_planet = None
self.planet_turns_left = 0
self.planet_explore_active = False
self.planet_log = []
```

### Key binds

| Key | Action |
|-----|--------|
| `H` (spaceport) | Open hangar |
| `1-4` (hangar) | Launch to planet |
| `U` (hangar) | Upgrade ship |
| `R` (hangar) | Refuel (up to 50 units, 1g each) |
| `SPACE` (planet) | Scan for resources |
| `E` (planet) | Return to spaceport |

---

## Milestone 2 — Automated Farm Bots ✓

**Goal:** Player can buy bots that autonomously water/harvest crops.

### Key binds

| Key | Action |
|-----|--------|
| `B` (spaceport) | Open bot workshop |
| `1-3` (workshop) | Buy bot |
| `E` (farm, placement) | Place bot |
| `E` (farm, on inactive bot) | Reactivate bot |
| `ESC` (any) | Cancel placement |

---

## Milestone 3 — NPC Schedules & Gift-Giving ✓

**Goal:** NPCs walk the spaceport on daily schedules, accept gifts, and have special heart events.

### Key binds

| Key | Action |
|-----|--------|
| `G` | Toggle gift mode |
| `E` near NPC | Give selected gift or talk |

---

## Milestone 4 — Cosmic Weather & Seasons ✓

**Goal:** Dynamic weather effects and seasonal cycles that affect crop growth.

### Weather transitions

```python
def update_weather(self):
    self.weather_timer -= 1
    if self.weather_timer <= 0:
        weights = SEASONAL_MODIFIERS[SEASONS[self.season_index]]["weather_weights"]
        self.current_weather = random.choices(WEATHER_EVENTS, weights=weights)[0]
        self.weather_timer = random.randint(WEATHER_DURATION["min"], WEATHER_DURATION["max"])
```

### Season transitions

```python
def update_season(self):
    self.day_in_season += 1
    if self.day_in_season >= SEASON_DAY_LENGTH:
        self.day_in_season = 0
        self.season_index = (self.season_index + 1) % len(SEASONS)
        self.set_message(f"Welcome to {SEASONS[self.season_index]} Season!")
```

---

## Milestone 5 — Spaceport Festivals ✓

**Goal:** Seasonal festivals with mini-games, unique rewards, and relationship boosts.

### Mini-games: Crop Tasting, Alien Flower Show, Starlight Dance

---

## Milestone 6 — Save / Load Screen with Three Slots ✓

**Goal:** Player can manage multiple save files through a dedicated UI overlay.

### Key Binds

| Key | Action |
|-----|--------|
| `S` (anywhere) | Open save/load screen |
| `1/2/3` (save menu) | Save to slot |
| `L + 1/2/3` (save menu) | Load from slot |
| `ESC` (save menu) | Close save menu |

---

## Milestone 7 — Cooking & Recipes ✓

**Goal:** Player can cook harvested crops into dishes for energy restoration and profit.

### Key binds

| Key | Action |
|-----|--------|
| `C` (farm) | Open kitchen / cooking menu |
| `1-8` (kitchen) | Cook recipe |
| `Z/X/C/V/B/N/M/P` (shop) | Sell dish |

---

## Milestone 8 — UI Polish ✓

**Goal:** Quality-of-life visual improvements. Facing tile highlight, Shift quantity modifier, crop info HUD, NPC location markers.

---

## Milestone 9 — Skill Progression ✓

**Goal:** Player gains XP in 4 skills (Farming, Exploration, Cooking, Social). Leveling unlocks perks.

### Key binds

| Key | Action |
|-----|--------|
| `K` | Toggle skills overlay |

---

## Milestone 10 — Farm Expansion & Buildings ✓

**Goal:** Player can expand the tillable farm area and construct permanent buildings (storage shed, well, greenhouse, shipping bin).

### Key binds

| Key | Action |
|-----|--------|
| `V` (spaceport) | Open building shop |
| `E` on signpost | Open expansion menu |

---

## Milestone 11 — Animal Husbandry ✓

**Goal:** Player can buy, feed, and care for alien animals (Zap-Chicken, Moo-Droid, Fluffalo) that produce valuable goods.

### Key binds

| Key | Action |
|-----|--------|
| `E` near barn | Open barn overlay |

---

## Milestone 12 — Artisan Crafting & Processing ✓

**Goal:** Player can process crops and animal products into high-value artisan goods via a processing queue.

### Key binds

| Key | Action |
|-----|--------|
| `C` (farm, cycle) | Toggle cook/craft |

---

## Milestone 13 — Fishing ✓

**Goal:** Player can fish at the spaceport pier for unique fish, with a timing-based mini-game and collection log.

### Key binds

| Key | Action |
|-----|--------|
| `E` near pier | Start fishing |
| `SPACE` (fishing) | Cast / Hook / Reel |

---

## Milestone 14 — Town Reputation & Daily Quests ✓

**Goal:** Player earns reputation by completing daily quests and contributing to the spaceport, unlocking rank-based perks.

### Key binds

| Key | Action |
|-----|--------|
| `E` on quest board | Open quests |
| `E` on merchant | Open merchant shop |
| `1/2/3` (quests) | Accept quest |
| `1/2/3` (merchant) | Buy item |

---

## Milestone 15 — Graphics Overhaul ✓

**Goal:** Replace the programmer-art aesthetic with a cohesive 16-bit look: custom space-themed font, redrawn 32×32 sprites, UI panel styling, and visual polish across all screens.

### Completed changes

| Change | Details |
|--------|---------|
| **Font Replacement** | Space Mono TTF bundled in `assets/fonts/`, loaded with graceful `SysFont` fallback |
| **Screen Shake & Flash** | `screen_shake`/`screen_flash` fields on `GameState`, `shake_screen()`/`flash_screen()` helpers, render loop integration |
| **Particle Enhancement** | 4 particle types (sparkle/star, leaf/ellipse, smoke/rising, confetti/rect), per-type gravity/shape rendering |
| **UI Panel Styling** | `draw_panel()` helper with gradient background, drop shadow, title bar, border |
| **Palette System** | Central `PALETTE` dict with 10 color families (3 tones each), `blit_sprite()` pixel data array renderer |
| **Redrawn Player** | `get_astronaut_v2()` with pixel data arrays for all 4 directions, used by farm + spaceport views |
| **NPC Nameplates** | Transparent background, NPC-color name, heart level indicator (♥ symbols) |
| **Animated Water** | Shimmer overlay on watered soil tiles, synchronized to `anim_frame` |
| **Crop Rustle** | 2-frame y-offset oscillation on crop sprites |
| **Neon Signs** | Pulsing glow on building signs using `math.sin` oscillation |
| **Space Dust** | Floating brightness-oscillating particles on spaceport background |
| **Overlay Fade Transitions** | `draw_overlay_backdrop()` with smooth alpha ramp, used by 6+ overlays |

### Key files changed

| File | Changes |
|------|---------|
| `src/ui/context.py` | TTF font loading, `draw_overlay_backdrop()`, `font_bold` |
| `src/game/state.py` | `screen_shake`, `screen_flash`, `overlay_alpha`, `anim_frame`/`anim_timer` |
| `src/game/world_sim.py` | `shake_screen()`, `flash_screen()`, particle type support |
| `src/sprites.py` | `PALETTE`, `blit_sprite()`, `get_astronaut_v2()`, `draw_panel()` |
| `src/ui/loop.py` | Screen shake/flash in render loop, overlay alpha + animation tick |
| `src/ui/hud.py` | Particle type rendering (star, ellipse, rect shapes) |
| `src/ui/world_view.py` | v2 astronaut sprite, NPC nameplates, neon signs, space dust, animated water/crops |
| `src/ui/overlays.py` | `draw_overlay_backdrop()` refactored to context.py |
| `src/ui/menus.py` | Uses `draw_overlay_backdrop()` for save/skills menus |
| `assets/fonts/` | New directory with `SpaceMono-Regular.ttf`, `SpaceMono-Bold.ttf`, `SpaceMono-Italic.ttf` |

---

## Milestone 16 — Player Sprite Animation System ⏳

**Goal:** Replace the single-frame static astronaut with full walk-cycle animation, idle breathing, and tool-use poses.

### Changes

| Change | Details |
|--------|---------|
| **Walk Cycle** | 4 frames per direction (down/up/left/right) — 16 pixel-data arrays total. Frame 0 neutral, frame 1 left-leg-forward + 1px body drop, frame 2 neutral, frame 3 right-leg-forward + 1px body drop. |
| **Idle Animation** | 2-frame subtle breathing bob. Helmet rises/falls 1px every 12 ticks. Visor shine blinks. |
| **Tool Poses** | Static alternate frames for each tool (hoe, water, scythe). Arm extends forward, tool drawn in hand. |
| **Animation Timing** | Walk advances frame every 6 ticks (10 FPS). Idle advances every 12 ticks (5 FPS). Tool pose uses current frame 0 for movement pause. |
| **Sprite Cache** | Keyed by `(direction, state, frame)`. Warm on screen transition. |

### Key files changed

| File | Changes |
|------|---------|
| `src/sprites.py` | Add `PLAYER_WALK_FRAMES`, `PLAYER_IDLE_FRAMES`, `PLAYER_TOOL_FRAMES` nested dicts. Refactor `get_astronaut_v2()` → `get_astronaut_animated(direction, state, frame)` |
| `src/ui/world_view.py` | Pass `game.anim_state`, `game.anim_frame` to player draw calls |
| `src/game/state.py` | Add `anim_state` field (`"idle"`, `"walk"`, `"tool"`), tool-use timer |
| `src/game/entities.py` | Compute `anim_state` from `dx/dy` movement deltas |

### Edge cases

- Pixel arrays are 12×11 → rendered at 32×32 via `set_at`. Adjacent frames must not visibly "jump". Walk cycle must not clip into tile grid or overlap soil tiles.
- Tool pose must read correctly for each direction (watering can held right, hoe overhead, scythe diagonal).

---

## Milestone 17 — NPC Character Art Overhaul ✓

**Goal:** 7 unique NPC pixel-art sprites replacing colored-rectangle bodies, with walk cycles and dialogue portraits.

### NPC Sprite Designs

| NPC | Species | Silhouette | Colors | Special |
|-----|---------|------------|--------|---------|
| **Zara** | Zenorian | Bipedal, shopkeeper apron, antennae | Orange/brown, gold trim | Antennae glow, apron pocket |
| **Blip** | Floatan | Floating jellyfish bell, trailing tendrils | Cyan/blue | Bobs up/down continuously, tendrils wave |
| **Nova** | Lunari | Tall, flowing hair, pilot jacket | Purple/pink | Hair moves in breeze, jacket stars |
| **Pip** | Spriggan | Small, leafy, energetic pose | Green/yellow | Leaf antennae, sprout-like head tuft |
| **Luna** | Ethereal | Floating robes, star patterns, wide eyes | Pink/purple | Translucent robe edges, glimmer particles |
| **Rex** | Terrus | Stocky, suspenders, wide-brim hat | Brown/tan | Beard, hat brim shadow, sturdy boots |
| **Zoop** | Fuzzian | Round, fluffy, pet-shop bowtie | Pink/white | Fur texture via alternating pixel rows |

### Data structure

```python
NPC_PIXEL_DATA = {
    "zara": {
        "front": [...rows...],
        "back":  [...rows...],
        "left":  [...rows...],
        "right": [...rows...],
        "palette_map": {...},
    },
    ...
}
```

### Changes

| Change | Details |
|--------|---------|
| **Pixel-Art Sprites** | 32×64 per NPC, 4 directions, 2 walk frames each. Defined as pixel-data arrays + palette maps. |
| **Walk Animation** | Leg/body bob synced to `anim_frame`. Floatans (Blip, Luna) use vertical sine-bob instead of walk frames. |
| **Dialogue Portraits** | 32×32 face close-ups shown in dialogue overlay. Eye-blink animation every 120 ticks. |
| **Sprite Cache** | Keyed by `(npc_id, direction, frame)`. Pre-warmed on game start. |

### Key files changed

| File | Changes |
|------|---------|
| `src/sprites.py` | Add `NPC_PIXEL_DATA` dict. Add `get_npc_v2(npc_id, direction, frame)`. Keep `get_npc_surf()` as fallback for un-migrated NPCs. |
| `src/ui/world_view.py` | Switch NPC draw from `get_npc_surf()` → `get_npc_v2()`. Pass `anim_frame` for walk/bob. |
| `src/ui/overlays.py` | Display dialogue portrait in speech box. |
| `src/constants.py` | Simplify NPC color fields (become palette hints, not primary rendering data). |

### Edge cases

- NPCs must be visually distinct at 32×64 — each silhouette recognizable within 1 second.
- 2-frame walk cycles (shuffle bob) must look natural.
- Floating NPCs (Blip, Luna) need sine-wave vertical offset instead of walk frames — distinct animation path only for `is_floating` NPCs.

---

## Milestone 18 — Building & Facility Art Pass ✓

**Goal:** Enhance all buildings with consistent 16-bit styling, animated elements, and interior backdrop art for overlays.

### Building Enhancements

| Building | Current | Enhanced |
|----------|---------|----------|
| **Shop** | Purple with awning, display windows | Add chimney smoke particle, animated awning stripes, window glow at night |
| **Bar** | Dark red with sign | Neon tube animation along roofline, door opening animation |
| **Houses** | Blue-gray boxes | Window light toggle, door frames, roof shingle pattern, mailbox |
| **Storage Shed** | Brown plank boxes | Roof tile pattern, door handle animation, side window |
| **Well** | Stone ring with roof | Water surface reflection, rope/ladder detail |
| **Greenhouse** | Glass panels + frame | Internal plant growth visible through glass, window reflection |
| **Shipping Bin** | Wooden crate | Hinged lid animation, "full" indicator when contents > 0 |
| **Barn** | Large brown with roof | Hayloft window, door split-rail detail, weather vane |

### Decorative Props

| Prop | Size | Placement |
|------|------|-----------|
| **Lamp Post** | 1×2 tiles | Spaceport paths, farm path entrance |
| **Bench** | 2×1 tiles | Near shop, bar, landing pad |
| **Fence** | 1×1 tile (segmented) | Farm boundary, along paths |
| **Planter** | 1×1 tile | Outside buildings, landing pad |
| **Crate** | 1×1 tile | Near shop/shipping bin |
| **Signpost** | 1×1 tile | Directional signs |

### Interior Backgrounds

| Interior | Used By | Resolution |
|----------|---------|------------|
| Kitchen | Cooking overlay (`C` on farm) | Full screen backdrop |
| Workshop | Crafting overlay | Full screen backdrop |
| Bar Interior | Bar menu (`E` at bar) | Full screen backdrop |
| Barn Interior | Barn overlay (`E` at barn) | Full screen backdrop |
| Hangar Interior | Hangar menu (`H` at spaceport) | Full screen backdrop |

### Key files changed

| File | Changes |
|------|---------|
| `src/sprites.py` | Add `get_building_v2(building_type, anim_frame)` with animated elements. Add `get_prop_surf(prop_type)`. Add `get_interior_surf(interior_type)`. |
| `src/ui/world_view.py` | Draw props on farm and spaceport. Pass `anim_frame` for animated building elements. |
| `src/ui/overlays.py` | Draw interior backgrounds behind overlay panels. |
| `src/constants.py` | Add `PROP_TYPES` dict, `INTERIOR_TYPES` dict. |

---

## Milestone 19 — Item, Crop & Icon System ⏳

**Goal:** Distinct 16×16 pixel-art icons for every item, reworked crop sprites with per-crop pixel data, and proper animal/bot/ship sprites.

### Icon Categories

| Category | Count | Current | New |
|----------|-------|---------|-----|
| Crops | 6 | Colored box + stem | Unique fruit/vegetable shape per crop, 16×16 |
| Seeds | 6 | Same as crop icon | Seed packet with crop color |
| Cooked Dishes | 8 | Purple box (fallback) | Per-dish icon (salad bowl, bread loaf, juice glass) |
| Artisan Goods | 8 | Purple box (fallback) | Per-good icon (wine bottle, cheese wedge, scarf) |
| Fish | 6 | Colored fish shape (32×32) | Redesigned 16×16 fish with species detail |
| Tools | 3 | Colored rectangles | Proper silhouettes (hoe, watering can, scythe) |
| Bots | 5 | Colored rectangles (32×32) | Redesigned bodies with wheels/appendages |
| Ship Tiers | 3 | Stacked rectangles (32×32) | Distinct ship silhouettes per tier |
| Animals | 3 | Colored shapes (32×32) | Enhanced pixel art per species |

### Crop Growth Sprite Redesign (32×32)

| Crop | Stage 0–1 | Stage 2–3 | Stage 4–5 |
|------|-----------|-----------|-----------|
| Glowroot | Small green sprout | Leafy green top | Glowing bulb visible at base |
| Zargon Fruit | Purple sprout | Vines spreading | Large purple fruit hanging |
| Cosmic Wheat | Golden sprout | Stalks growing | Full golden stalks swaying |
| Starlight Melon | Blue-green sprout | Vines with flowers | Large blue melon, star sparkles |
| Nebula Bloom | Pink sprout | Bud forming | Open flower with 5 petals |
| Quasar Berry | Red sprout | Bush growing | Bush with red berries |

### Key files changed

| File | Changes |
|------|---------|
| `src/sprites.py` | Add `CROP_PIXEL_DATA` per crop per stage. Add `ICON_PIXEL_DATA` for all items. Refactor `get_crop_icon()`, `get_item_icon()`, `get_crop_surf()`. Add per-type pixel data for `get_animal_surf()`, `get_bot_surf()`, `get_ship_surf()`. |
| `src/ui/overlays.py` | Updated icon references in shop, inventory, cooking, crafting. |

---

## Milestone 20 — Environment Tileset & Background Art ⏳

**Goal:** Varied tiles, seasonal ground cover, animated water, weather VFX, parallax backgrounds, and screen transition effects.

### Tile Variety System

| Tile Type | Variants | Selection |
|-----------|----------|-----------|
| Grass | 4 per season | Hash-based on (col, row, season) |
| Path | 4 variants | Hash-based on (col, row) |
| Soil (untilled) | 3 variants | Random per tile on creation |
| Soil (tilled) | 3 variants | Random per tile on tilling |
| Soil (watered) | 3 variants + shimmer | Based on base tilled variant |

### Decorative Ground Objects

- **Grass:** flowers (4 colors), rocks (3 sizes), tall grass tufts, small mushrooms, crystals
- **Path:** cobblestone detail, cracks, moss patches
- **Farm:** weed tufts, fireflies at night (brightness-pulsing dots)

### Seasonal Tile Overrides

| Season | Grass Tint | Tree Appearance | Decorations |
|--------|-----------|-----------------|-------------|
| Nebula | Purple-tinted | Purple foliage | Glowing crystals, star flowers |
| Void | Gray-brown | Bare branches | Dead grass tufts, dark mushrooms |
| Bloom | Bright green | Full bloom, pink/white blossoms | Flower patches everywhere |
| Solar | Golden | Yellow-orange leaves | Sunflowers, warm golden tones |

### Enhanced Background Layers

| Layer | Spaceport | Farm | Planet Exploration |
|-------|-----------|------|--------------------|
| Layer 0 (sky) | Time-of-day gradient | Same sky gradient | Planet color gradient |
| Layer 1 (far) | Mountain silhouettes / nebula | Mountain silhouettes | Star field |
| Layer 2 (mid) | City skyline | Tree line | Space station silhouette |
| Layer 3 (near) | Spaceport buildings | Farm buildings + trees | Ground terrain detail |

### Weather VFX

| Weather | Effect | Implementation |
|---------|--------|----------------|
| Alien Rain | Blue streaks falling at angle | `weather_particles` with `velocity_x`, `velocity_y` |
| Meteor Shower | Bright streaks across sky, occasional fireball | Fast-moving horizontal particles with trail |
| Solar Flare | Warm screen tint + rising heat haze | Full-screen overlay + vertically rising particles |
| Void Fog | Horizontal gray wisps | Low-opacity wide ellipses drifting sideways |
| Clear | No particles | — |

### Screen Transition Effect

- 0.5s wipe when moving between farm ↔ spaceport
- Black overlay fades in at 8 alpha/tick, camera resets, black overlay fades out
- New GameState fields: `transition_active`, `transition_progress`, `transition_from`, `transition_to`

### Key files changed

| File | Changes |
|------|---------|
| `src/sprites.py` | Add `get_tile_v2(tile_type, variant, season)`, `get_decoration_surf(deco_type)` |
| `src/ui/world_view.py` | Multiple tile variants, decor drawing, seasonal selection, parallax background layers |
| `src/ui/loop.py` | Weather VFX rendering, transition effect |
| `src/game/state.py` | Add `transition_active`, `transition_progress`, `transition_map_from/to` |
| `src/game/world_sim.py` | Weather particle spawning per effect type |

---

## Dependency Graph

```
M1 (Spaceship) ✓
  └─► M2 (Farm Bots) ✓
M3 (NPC Schedules) ✓
  └─► M4 (Weather & Seasons) ✓
  └─► M5 (Festivals) ✓
M6 (Save Slots) ✓
M7 (Cooking) ✓
M8 (UI Polish) ✓
M9 (Skills) ✓
M10 (Farm Expansion) ✓
M11 (Animals) ✓
M12 (Artisan Crafting) ✓
M13 (Fishing) ✓
M14 (Town Reputation) ✓
M15 (Graphics Overhaul) ✓
  └─► M16 (Player Animation) ⏳
  └─► M17 (NPC Art) ⏳
  └─► M18 (Building Art) ⏳
  └─► M19 (Icons & Items) ⏳
  └─► M20 (Environment Art) ⏳
```

**All 20 milestones — 15 complete, 5 in planning (M16–M20).**

---

## Save Format

Save files use `savegame_{0,1,2}.json` (3-slot system). Backward compatibility via `data.get("key", default)`.

### Save keys by milestone

| Milestone | New Keys |
|-----------|----------|
| M1 | `ship_tier`, `fuel`, `cargo` |
| M2 | `bots` (list of dicts) |
| M3 | None (NPC hearts/talked already saved) |
| M4 | `season_index`, `day_in_season`, `current_weather`, `weather_timer`, tile `crop_timer` (float) |
| M5 | None (ephemeral event state) |
| M6 | Slot-based save files, `save_menu_slot` |
| M7 | None (inventory-based) |
| M8 | None |
| M9 | `skills` dict |
| M10 | `farm_expansion_tier`, `farm_cols/rows/off_x/off_y`, `buildings`, `shipping_bin_contents` |
| M11 | `animals`, `barn_capacity` |
| M12 | `processing_queue` |
| M13 | `fish_collection`, `fish_caught_total` |
| M14 | `reputation`, `active_quests`, `completed_quests`, `merchant_present/items/last_visit` |
| M15 | None (visual only, no persist needed) |
| M16 | None (visual only, animation state ephemeral) |
| M17 | None (visual only, sprites cached at runtime) |
| M18 | None (visual only, props placed at init) |
| M19 | None (visual only, icon data in sprite cache) |
| M20 | None (visual only, tile variants determinate from position + season) |

---

## Summary of Key Binds

| Key | Action |
|-----|--------|
| `H` (spaceport) | Open hangar |
| `B` (spaceport) | Open bot shop |
| `V` (spaceport) | Open building shop |
| `C` (farm) | Open kitchen / toggle cook-craft |
| `K` | Toggle skills overlay |
| `G` | Toggle gift mode |
| `S` | Open save/load screen |
| `I` | Open inventory |
| `M` | Toggle map |
| `?` | Show help |
| `E` | Interact / talk / gift / confirm |
| `SPACE` | Tool action / planet scan / fish |
| `1-9` | Various select/slot actions |
| `Shift+key` | Bulk action (×10) |
| `L + 1/2/3` | Load save slot |
| `Arrow keys` | Movement / dance mini-game |
| `ESC` | Back / cancel / close overlay |
