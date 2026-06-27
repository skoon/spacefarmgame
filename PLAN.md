# Space Farm Galaxy — Expanded Milestone Plan (Milestones 21–30)

Acting as a senior game developer, this plan outlines the next 10 Milestones to fix existing engine bugs, polish the visual systems (scaling and animations), improve game architecture, and add key immersive features. 

---

## Milestone 21 — Correct Tiling Engine Coordinates & Original Asset Restoration
**Goal:** Fix the coordinate mappings in `src/sprites.py` so the original unmodified `outside.png` tileset displays correctly, and restore the original `outside.png` file to standardise graphics.

### Technical Changes
- **`src/sprites.py` (`OUTSIDE_TILE_MAP`)**:
  - Update coordinate lists to point to actual coordinates from the unmodified standard `outside.png` (matching `tools/tile_grid_viewer.html` specs):
    ```python
    OUTSIDE_TILE_MAP = {
        "grass": [(2, 0), (2, 1), (0, 2), (1, 2)],
        "path": [(9, 0), (10, 0), (9, 1), (10, 1)],
        "untilled": [(3, 2), (4, 2), (5, 3)],
        "tilled": [(3, 3), (4, 3), (1, 3)],
        "watered": [(4, 3), (5, 3), (3, 2)],
    }
    ```
- **Assets Restoration**:
  - Overwrite `assets/outside.png` with the unmodified version located at `tools/outside.png~`.
  - Delete any manual hack tiles inside `assets/outside.png`.

---

## Milestone 22 — Autotiler & Terrain Transition System
**Goal:** Implement clean transitions and borders (edges/corners) between different tile types (e.g., grass-to-path, grass-to-soil) instead of abrupt box transitions.

### Technical Changes
- **`src/sprites.py` / `src/game/farming.py`**:
  - Write an autotiling bitmask evaluator (standard 8-bit or 4-bit neighbor checking).
  - Define sprite mappings for edge borders, outer corners, and inner corners of paths, soil, and tilled land.
  - Modify `get_tile_surf` to check adjacent cell types using the current map state and render the correct blended transition tile.

---

## Milestone 23 — Maintain Aspect Ratio in Sprite Scaling
**Goal:** Fix the squashing and stretching of building, animal, and entity sprites by replacing aspect-ratio-ignoring scaling.

### Technical Changes
- **`src/sprites.py` (`scale_to_fill`)**:
  - Refactor or replace `scale_to_fill` with a method that preserves the original aspect ratio (aspect fit or integer pixel scaling).
  - Calculate target scale factor based on minimum scale delta: `scale = min(target_w / original_w, target_h / original_h)`.
  - Create a target surface padded with transparent pixels and center the aspect-correct scaled sprite onto it.

---

## Milestone 24 — NPC Caching, Sheet Loading & Walk Animations
**Goal:** Enable direction-based sprites and walking animations for NPCs. Fix cache collisions and bypass static layout overrides.

### Technical Changes
- **`src/sprites.py` (`get_npc_v2`)**:
  - Update cache key to include direction and frame variables: `key = f"npcv2_{npc_id}_{direction}_{frame}"`.
  - Remove or bypass the `assets/npc_{npc_id}_32.png` static file branch which forces a single static 32x32 image to scale to 32x64. This forces the system to load `assets/npc_{npc_id}_256.png` sprite sheets containing direction/walk animations.
- **`src/ui/world_view.py` (`draw_spaceport`)**:
  - Update `ns = get_npc_v2(npc.id, npc.color, npc.color2)` to pass the NPC's actual facing direction and current animation frame: `get_npc_v2(npc.id, npc.color, npc.color2, npc.direction, game.anim_frame)`.

---

## Milestone 25 — Player Sprite Walk Cycle & Tool Animation Restoration
**Goal:** Ensure the player astronaut displays correct pixel-art walk animations instead of falling back to a static procedural box outline.

### Technical Changes
- **`src/sprites.py` (`get_astronaut_animated`)**:
  - Refactor the code to call the pixel-data-driven compiler `_build_astro_surf(direction, state, frame)` (which processes the detailed `_ASTRO_BASE` arrays).
  - Remove the fallback call to `get_astronaut_surf(direction)`, which procedurally draws a single frame using blocks of white color.

---

## Milestone 26 — Dialogue Portraits Rendering in Speech Box
**Goal:** Display dialogue portraits in the speech overlay box when talking to NPCs.

### Technical Changes
- **`src/ui/overlays.py` (`draw_dialogue`)**:
  - Modify `draw_dialogue` layout to accommodate a dedicated portrait box (e.g., 64x64 or 96x96 window) on the left side of the text area.
  - Blit the corresponding face profile/dialogue frame from the NPC's assets.
  - Implement a basic blink animation timer using the globally ticking `anim_frame` value.

---

## Milestone 27 — NPC Pathfinding & Collision Grid
**Goal:** Prevent NPCs from walking through walls, buildings, and water, forcing them to walk on valid paths.

### Technical Changes
- **`src/game/entities.py` / `src/game/social.py`**:
  - Implement a grid-based collision map for the Spaceport layout identifying solid block coordinates (buildings, fences, map borders).
  - Implement A* (A-Star) pathfinding or simple collision-avoidance logic for NPCs when calculating random daily movement targets.
  - Adjust NPC update steps to verify collisions before advancing coordinates.

---

## Milestone 28 — Sound Effects & Music Manager
**Goal:** Introduce audio feedback for player actions (tools usage, menus) and atmospheric background music.

### Technical Changes
- **Sound Manager (`src/ui/context.py` / `src/audio.py`)**:
  - Initialize the `pygame.mixer` subsystem.
  - Create a music and sound effects manager that loads assets and supports basic functions (play, stop, fade, volume control).
- **Integration**:
  - Play tool sound effects (hoe, water, scythe) in `src/game/farming.py`.
  - Loop background music themes depending on the active screen: `farm`, `spaceport`, and `planet_explore`.

---

## Milestone 29 — Command Pattern Input Refactoring
**Goal:** Clean up the highly nested conditional keyboard events structure in `src/ui/input.py` and replace it with an action-command dispatcher.

### Technical Changes
- **`src/ui/input.py`**:
  - Create a mappings configuration binding keyboard constants to abstract actions (e.g., `ACTION_MOVE_UP`, `ACTION_USE_TOOL`, `ACTION_TOGGLE_INVENTORY`).
  - Implement sub-context dispatchers (e.g., `FarmInputContext`, `HangarInputContext`) to avoid global state collisions.

---

## Milestone 30 — Save File Metadata & Auto-Backup System
**Goal:** Display detailed metadata in the save slot screen (current season, gold, playtime, date) and implement a backup save system to protect against file corruption.

### Technical Changes
- **`src/game/state.py` (`save_game` / `load_game`)**:
  - Add save metadata (save time, gold count, season name, farm expansion tier) to the top-level of the JSON files.
- **`src/ui/menus.py`**:
  - Redesign the 3-slot save screen cards to dynamically parse and show metadata instead of blank text placeholders.
- **Corruption Prevention**:
  - Write temporary backup files (`savegame_{slot}.json.tmp`) first, verify write integrity, then swap filenames atomically.
