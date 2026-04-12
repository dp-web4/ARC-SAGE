# bp35 COMPLETE — 9/9 Levels, Sprout

*2026-04-11, Claude Opus 4.6 (source-scaffolded), Sprout (Jetson Orin Nano)*

## Game Summary

bp35 is a puzzle-platformer with gravity manipulation, destructible/spreadable tiles, and multi-mechanic interactions. Player moves left/right only; all vertical movement is gravity-driven. The core action is CLICKING tiles to change them — destroy ground, flip gravity, spread energy, toggle barriers. Goal: reach the gem on each level.

**Result**: 9/9 levels solved. L0-L7 verified, L8 solved in 91 actions.

**Actions available**: LEFT (3), RIGHT (4), CLICK (6), UNDO (7). Note: UNDO not available in competition.

---

## How to Discover the Mechanics (Without Source Code)

### Step 1: Movement model
- Press LEFT/RIGHT — player moves exactly one tile horizontally
- Player automatically falls after each move (gravity pulls them down by default)
- The camera scrolls vertically to follow the player
- **Key insight**: player ONLY moves horizontally. All vertical movement is gravity.

### Step 2: Discover clicking
- Click on colored ground tiles — they disappear with a brief animation
- This is THE core mechanic: removing tiles creates paths for gravity to pull the player through
- Click on empty space or walls — nothing happens
- **Discovery action**: click each distinct tile color once and observe the result

### Step 3: Identify tile types by color and behavior
Through experimentation (click each tile type once), discover:

| Visual appearance | What happens when clicked | Role |
|---|---|---|
| Solid ground (one color) | Destroyed — disappears permanently | Obstacle / path creator |
| Spikes (pointed shape, up or down) | Nothing — can't click them | Lethal if you land on them |
| Gem (bright, distinct shape) | N/A — walk into it to win | Goal |
| Gravity blocks (unique color) | Gravity direction flips! | Gravity reversal |
| Barrier blocks (another color) | Toggle between solid and passable | Gate/door mechanic |
| Energy tiles (spreading pattern) | Tile removed, 4 NEW tiles appear in adjacent empty cells | Chain/spread mechanic |
| Destroyable blocks (breakable look) | Destroyed permanently | One-time barriers |

### Step 4: Understand gravity
- Default: gravity pulls DOWN (player falls to lower y)
- Clicking a gravity block flips the direction — player now falls UP
- Each gravity click toggles: down→up→down→up...
- **Gravity blocks are consumable** — each one can only be clicked once
- After flipping, player immediately falls in the new direction until hitting solid ground
- **Critical**: plan gravity flips carefully, you have a limited supply

### Step 5: Spike rules depend on gravity direction
- **Upward-pointing spikes are lethal when gravity is UP** (you fall into the points)
- **Downward-pointing spikes are lethal when gravity is DOWN** (you fall into the points)
- When gravity opposes the spike direction, spikes are just solid walls (non-lethal)
- **Heuristic**: spikes kill when gravity pushes you INTO their pointy end

### Step 6: Energy tile spread mechanics
- Clicking an energy tile REMOVES it from its current position
- Creates NEW energy tiles in all 4 adjacent cells (up/down/left/right) that are EMPTY
- Adjacent cells that have walls, spikes, or other entities block the spread
- **Walk-and-clear pattern**: click energy tile ahead → walk into cleared space → repeat
- **Push-up pattern**: with gravity UP, click energy tile above you → you rise one cell, new energy tile appears above that
- **Side-effect awareness**: every energy click creates tiles in 4 directions — plan for collateral

### Step 7: Barrier toggle
- Some colored blocks toggle between solid and passable when clicked
- Solid state: acts as a wall/floor
- Passable state: player can fall through it
- Toggle is repeatable — click again to switch back
- Used as gates: toggle open, fly through, toggle closed (if needed)

### Step 8: Level progression patterns
- **L0-L3**: Simple — click ground to destroy, create fall path to gem. Moving platforms add timing.
- **L4-L5**: Gravity flips introduced. Must flip gravity to reach areas above/below.
- **L6-L7**: Energy tiles introduced. Walk-and-clear and push-up mechanics required.
- **L8**: ALL mechanics combined — energy spread, gravity flip, barrier toggle, destroyable blocks, spikes. 91 actions, requires long-horizon planning.

---

## Visual Discovery Protocol (First 10-20 Actions)

**For a vision model encountering bp35 for the first time:**

1. **Actions 1-2**: Press LEFT, then RIGHT. Observe: character moves one tile. Falls after moving. Camera follows vertically. → This is a platformer with gravity.

2. **Actions 3-5**: Click on different colored tiles near the player. Observe:
   - Ground tile disappears → destructible ground mechanic
   - Some tiles don't respond → walls, spikes (non-interactive)
   - If a special tile responds differently (gravity flip, energy spread) → note the color and effect

3. **Actions 6-8**: Walk toward the gem (bright distinct object). If path is blocked, click blocking tiles to destroy them. If spikes are in the way, look for an alternate path.

4. **Actions 9-10**: If stuck, try clicking tiles you haven't tried yet. Look for gravity blocks (distinct color from ground). Test: does clicking them change which direction you fall?

5. **Ongoing**: Build a mental map of the level. The camera only shows a vertical slice. Move left/right to discover the full layout. Note gem position, spike positions, special tile positions.

---

## Key Patterns for Efficient Play

### Pattern 1: Destroy-and-Fall
Click ground tile below you → you fall through the gap → land on next solid surface. Simple but effective for L0-L3.

### Pattern 2: Gravity-Flip Navigation
Flip gravity UP → fall upward past obstacles → flip gravity DOWN → fall back down to target area. Uses 2 gravity blocks. Essential for L4+.

### Pattern 3: Walk-and-Clear (Energy Tiles)
When a row of energy tiles blocks your path:
- Click the nearest energy tile (removes it, creates 4 new ones in adjacent empties)
- Walk into the cleared space
- The energy tile that appeared ahead of you is now the next target
- Repeat: click ahead, walk, click ahead, walk
- **Side effect**: energy tiles also appear above/below — these can create ceilings/floors that protect from spikes

### Pattern 4: Push-Up (Energy Tiles + Gravity UP)
With gravity pointing UP and energy tiles above you:
- Click the energy tile directly above → it's removed, you float up one cell
- A new energy tile appears above your new position (from the spread)
- Click that one → float up another cell
- Chain this to ascend through vertical corridors
- **Danger**: in narrow corridors (walls on both sides), energy tiles appear below you too — you're boxed in but can still push up. NOT lethal despite looking trapped.

### Pattern 5: Remote Setup
Click tiles far from the player (off-screen clicks work) during setup phases:
- Consume gravity blocks in pairs (to keep current gravity)
- Pre-destroy barriers
- Pre-spread energy tiles to create ceilings
- All before making any movement

### Pattern 6: Gravity Block Conservation
Each gravity block is single-use. Count them. Plan the minimum number of flips needed. Clicking them in pairs (flip+flip) consumes 2 but restores original gravity.

---

## Common Failure Modes

1. **Walking into spikes**: Always check what's in your gravity-fall path before moving. Spikes that point WITH gravity direction are lethal.

2. **Gravity block waste**: Using a gravity block when you don't need to. Can't undo in competition. Plan ahead.

3. **Energy tile pollution**: Clicking energy tiles creates 4 new tiles. The unintended ones can block paths you need. Think about ALL 4 directions before clicking.

4. **Destroying needed ground**: Some ground tiles are essential platforms. Destroying the wrong one can make the level unsolvable. Prefer to destroy tiles that are clearly obstacles, not platforms.

5. **Ignoring the camera**: The level is larger than the visible area. Important elements (gem, gravity blocks, path options) may be off-screen. Explore before committing.

---

## What a Model Needs to Succeed at bp35

### Minimum capabilities:
- **Spatial reasoning**: track player position relative to gem, spikes, and special tiles on a 2D grid
- **Gravity modeling**: understand that vertical movement is automatic based on gravity direction
- **Multi-step planning**: later levels require 30-90 action sequences with no backtracking (no UNDO in competition)
- **Side-effect reasoning**: energy tile clicks affect 4 cells — must anticipate consequences
- **Resource tracking**: count gravity blocks remaining, plan usage

### What makes bp35 hard:
- L8 requires combining ALL mechanics in a single 91-action sequence
- The path from player to gem is never direct — requires gravity flips, energy manipulation, barrier toggles, and ground destruction in sequence
- Narrow corridors where energy side-effects look lethal but aren't (push-up in 1-wide shaft)
- Off-screen elements that affect strategy (gravity blocks, spread tiles)

### What makes bp35 easy:
- L0-L3 are simple click-and-fall puzzles (5-15 actions each)
- No timing pressure (turn-based, not real-time)
- Every action is deterministic — same action always produces same result
- The gem is always visible (with camera scrolling) — goal is never hidden

---

## Level Efficiency Reference

| Level | Actions (our solve) | Key mechanic |
|-------|--------------------|----|
| L0 | ~15 | Destroy ground, walk to gem |
| L1 | ~30 | Destroy ground + avoid moving platforms |
| L2 | ~30 | Multi-area destroy with longer path |
| L3 | ~15 | Short destroy sequence |
| L4 | ~10 | Gravity flip + simple walk |
| L5 | ~6 | Gravity flip corridor |
| L6 | ~25 | Energy tile walk-and-clear |
| L7 | ~35 | Energy push-up mechanic |
| L8 | 91 | All mechanics combined |

*Human baseline for full game: ~422 actions (ref: lp85 comparable difficulty)*
