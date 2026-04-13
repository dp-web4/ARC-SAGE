# ARC-AGI-3 Game Solutions Reference

*Fleet-maintained. Updated as games are solved.*

## Solved Games (23/25)

---

### sb26 — Pick-and-Place / Structural Matching
**Solved by:** CBP + dp | **Levels:** 8/8 | **Baseline:** 153 | **Actions:** click + move

**Objects:** Colored tiles, connectors, borders, containers, structural groups
**Goal:** Place tiles into matching positions. Later levels: match structural relationships, not just colors.
**Interaction:** Click to pick up a tile, click destination to place. Arrow keys to navigate cursor.
**Key mechanic:** Connectors between tiles indicate parent-child hierarchy. Border colors match slot assignments. Structure determines validity, not just position.
**Winning strategy:**
- L1-5: Identify tile → find matching slot → pick and place
- L6+: Paradigm shift — pick-and-place becomes swap mechanic. Detect rule changes between levels.
- Cross-level: Each level uses ALL previous patterns. Carry rules forward.

**Discovery tips:** Click each object type once. Movement reveals cursor. Connectors are semantic cues — same border color = "goes here."

---

### vc33 — Wall-Swap Puzzle with Dual Buttons
**Solved by:** CBP + dp | **Levels:** 7/7 | **Baseline:** 307 | **Result:** 167 actions (184% efficiency) | **Actions:** click only

**Objects:** Brown buttons (instant), blue buttons (animated), wall segments, goal objects, target positions
**Goal:** Move goal objects to target positions by manipulating wall segments.
**Interaction:** Click brown buttons to move walls. Blue buttons activate after wall rearrangement — trigger free animated transitions.
**Key mechanic:** Brown buttons come in PAIRS (forward/reverse). One depletes → click the other to "refill." Blue buttons start inactive, turn olive when clickable.
**Winning strategy:**
- Map ALL buttons first (click each once, observe)
- Brown buttons: find pairs, use alternating clicks
- Blue buttons: rearrange walls until blue turns olive, then click for free animation
- Win condition is STRUCTURAL alignment, not just position — objects must be in correct relative arrangement

**Discovery tips:** Two button types look different. Test each. Brown = immediate. Blue = delayed/animated. Blue activation depends on brown clicks.

---

### cd82 — Cursor Stamp / Canvas Painting
**Solved by:** Nomad + dp | **Levels:** 6/6 | **Baseline:** 136 | **Actions:** click + move

**Objects:** Big cursor (orbiting stamp), small cursor (overlay stamp), canvas, palette (target), color indicators
**Goal:** Paint the canvas to match the target palette using cursor stamps.
**Interaction:** Arrow keys orbit the big cursor around the canvas (8 clock positions). SELECT stamps. Click color indicators to change fill color.
**Key mechanic:**
- Cardinal positions (12/3/6/9) → half-fill stamps
- Diagonal positions (1:30/4:30/7:30/10:30) → triangle-fill stamps
- Small cursor creates small rectangular overlays
- Stamps OVERWRITE — later stamps cover earlier ones
**Winning strategy:**
- Reverse-engineer from target: what shapes compose the final image?
- Determine layering order (paint back-to-front)
- Position cursor, select correct color, stamp
- Action cost: verify cursor position, color, target BEFORE stamping (stamping is consequential)

**Discovery tips:** Move cursor with arrows — watch it orbit. SELECT to stamp. Color indicators change the stamp color. Palette at top-left IS the target.

---

### lp85 — Ring Rotation Puzzle
**Solved by:** McNugget + dp | **Levels:** 8/8 | **Baseline:** 422 | **Actions:** click only

**Objects:** Colored tiles arranged in rings, cyan buttons (rotate left), teal buttons (rotate right), maroon goal markers, check markers
**Goal:** Rotate rings to place goal markers at target positions.
**Interaction:** Click cyan button → ring rotates left. Click teal button → ring rotates right.
**Key mechanic:**
- Tiles form closed loops (rings) that rotate when buttons are clicked
- Rings INTERSECT — tiles at intersection points can transfer between rings
- Commutator technique: rotate ring A, rotate ring B, undo A, undo B → moves tiles independently
- Later levels use BUTTON GROUPS — one click rotates multiple rings simultaneously
**Winning strategy:**
- Identify ring structure (which tiles form which ring)
- Find intersections (shared positions between rings)
- Compute rotation counts: (goal_slot - current_slot) mod ring_size
- For multiple goals on same ring: use commutators through intersections
- BFS over goal positions finds optimal sequences (state space is small)

**Discovery tips:** Click each button once — watch which tiles move in a cycle. Tiles that move together = one ring. Positions that respond to TWO different buttons = intersection.

---

### ft09 — Color Constraint Puzzle
**Solved by:** McNugget + dp | **Levels:** 6/6 | **Baseline:** 163 | **Actions:** click only

**Objects:** Colored tiles in grids, small indicator dots (constraint encoders), color palette (2-3 colors per level)
**Goal:** Set each tile to the correct color to satisfy all constraint indicators.
**Interaction:** Click a tile → cycles its color through the palette (brown→cyan→brown, or 3-color cycle).
**Key mechanic:**
- Small multi-colored dots in grid cells ARE INSTRUCTIONS
- Dot center pixel = the "reference color"
- Surrounding pixels: BLACK = neighbor must be this color, NON-BLACK = neighbor must NOT be this color
- Each click affects only the clicked tile (center-only pattern for all levels)
- L5-6: Special tiles (NTi) affect multiple neighbors when clicked — pattern encoded in magenta pixels
**Winning strategy:**
- Decode each indicator dot: center = target color, black surroundings = must match, colored surroundings = must not match
- Compile constraints for all tiles
- Click every tile that's the wrong color
- For multi-effect tiles (L5-6): solve as system of linear equations mod palette size

**Discovery tips:** Look for small multi-colored patterns INSIDE grid cells. These are NOT decoration — they encode constraints on neighboring tiles. Black pixels = "yes this color." Non-black = "not this color."

---

### sp80 — Gravity Pipes: Water Routing Puzzle
**Solved by:** Claude + dp | **Levels:** 6/6 | **Baseline:** 472 | **Actions:** move + select + click

**Objects:** Pipe segments (grey horizontal/vertical bars, movable), L-shaped deflectors (white), drip sources (yellow markers), water drops (pink), receptacles (cyan cups with opening), danger zones (green bars)
**Goal:** Position pipe segments to channel falling water from drip sources into all receptacles without hitting danger zones.
**Interaction:** CLICK selects a pipe (turns maroon). Arrows reposition it. SELECT (ACTION5) triggers the pour — water simulation runs automatically.
**Key mechanic:**
- Water falls from drip sources downward
- Straight pipes SPLIT water perpendicular to flow direction (water runs along pipe surface, falling off both ends)
- A pipe at grid position (px, py) with width w creates exit streams at x=(px-1) and x=(px+w)
- Receptacles need water entering through the cup OPENING (center top pixel, where pixel=-1). Water must approach from directly above the opening, with both perpendicular neighbors being receptacle cells → FILL
- Hitting receptacle edge (not opening) → splash to perpendicular positions, does NOT fill
- L-pipes deflect water 90° (later levels)
- Danger zones span the bottom — any water reaching them = fail
- Max 4 pours per level. Failed pour resets all receptacles.
- Display may be ROTATED (0/90/180/270°). Rotation affects both controls and visuals.
- A 5w pipe at x=4 exits at x=3 and x=9 — **both are cup centers** in many layouts. This is the key safe configuration.
**Winning strategy:**
- L1 (rot=0): Move the single pipe RIGHT 3 under the drip source. Pour.
- L2 (rot=180): Move pipe1 to (4,3), move pipe2 to (4,11). Pour. Route source through one pipe to fill left+middle cups, second pipe catches the rest.
- L3 (rot=180): 4-pipe solution: p2→LEFT 1, p1→LEFT 5, p0→RIGHT 10 UP 5, p3→LEFT 1 UP 1. Pour.
- L4 (rot=0, 20x20): Move the 7w pipe+drip (adbrqflmwi) to (10,10) — its drip fills cup3 at x=13, pipe exits fill cups 1+2. Move 5w pipe to (4,5) for cup0. Move other pipes to safe positions.
- L5 (rot=180, 20x20): p0→(-1,5), p1(L-pipe)→(6,7), p2→(2,3), p3→(4,10). L-pipe deflects water rightward to fill side receptacle.
- L6 (rot=0, 20x20): p0→(10,8), p1(L-pipe)→(14,10), p2(L-pipe)→(12,9), p3(pipe+drip)→(11,6). Both L-pipes and movable drip source used.
- **ALL 6 LEVELS SOLVED.**

**Critical discoveries:**
- Pipes can extend beyond grid boundary → movement blocked silently (4w pipe max x = gw-4).
- The `adbrqflmwi` pipe IS movable despite lacking `sys_click` tag — the game checks `ksmzdcblcz` tag for click targets, not `sys_click`. Its drip source moves with it!
- A 7w pipe at x=10 exits at x=9 (cup2) AND x=17 (cup1) — two cups from one pipe. With drip at x=13 (cup3), it fills THREE cups.

**Discovery tips:** On level start, the closest pipe is auto-selected (maroon). Just move it with arrows. SELECT to pour. Watch where water goes — exit streams tell you where to route.

### tr87 — Grid Navigation / Tree Translation
**Solved by:** CBP + dp | **Levels:** 6/6 | **Baseline:** 317 | **Result:** 137 actions (231% efficiency) | **Actions:** move only

**Objects:** Player avatar, trees (obstacles that translate), goal markers, grid cells
**Goal:** Navigate player to goal position while trees shift positions each turn.
**Key mechanic:** Trees translate in predictable patterns each move. Player must time movement to avoid collisions while reaching the goal.
**Winning strategy:** Track tree translation patterns, plan path that threads through shifting obstacles.

---

### sc25 — Maze Wizard / Spell Casting
**Solved by:** CBP + dp | **Levels:** 6/6 | **Baseline:** 216 | **Result:** 171 actions | **Actions:** move + click

**Objects:** Player wizard, maze walls, fireballs, scale tiles, spell indicators, exit portals
**Goal:** Navigate maze, cast spells to overcome obstacles, reach exit.
**Key mechanic:** Multiple spell types (fireball, scale, etc.) activated by clicking. Spells interact with environment — fireballs destroy walls, scale tiles resize passages. Later levels require multi-spell combos.
**Winning strategy:** Map maze, identify required spell sequence, execute spell combos in correct order.

---

### tn36 — Waypoint / Portal Timing
**Solved by:** CBP | **Levels:** 7/7 | **Baseline:** 250 | **Result:** 119 actions | **Actions:** click only

**Objects:** Checkerboard grid, game pieces, arrow indicators, waypoints (checkered squares), portals
**Goal:** Move pieces to target positions via waypoint docking and portal timing.
**Key mechanic:** Checkered squares are waypoints — pieces dock there. Arrow indicators show movement direction. Binary encoding determines piece movement patterns. Portal timing required for later levels.
**Winning strategy:** Identify waypoint positions, decode arrow indicators as movement instructions, time portal transitions.

---

### tu93 — Entity Navigation with Bouncers
**Solved by:** CBP + dp | **Levels:** 9/9 | **Baseline:** 378 | **Result:** 189 actions | **Actions:** move only

**Objects:** Player entity, bouncers (oscillating obstacles), walls, goal positions, pathways
**Goal:** Navigate entity through maze-like levels with bouncer obstacles to reach goal.
**Key mechanic:** Bouncers oscillate on fixed patterns blocking pathways. Player must time movement to pass through gaps. Later levels introduce entity+bouncer timing puzzles and perceptual approaches (watching bounce patterns before moving).
**Winning strategy:**
- L1-L5: Map bouncer patterns, find timing windows, navigate directly
- L6+: Perceptual approach — observe full oscillation cycle before committing to path
- L8-L9: Complex multi-bouncer timing with "goose chase" routing through loops

---

### ls20 — Movement Puzzle
**Solved by:** Sprout | **Levels:** 7/7 | **Baseline:** 546 | **Result:** 309 actions (43% improvement) | **Actions:** move only

**Objects:** Player, obstacles, goal positions, grid environment
**Goal:** Navigate through all 7 levels with movement-only controls.
**Winning strategy:** Documented in fleet learning — sprout solved all levels autonomously.

---

## In Progress (6 — one per machine)

### su15 — Suika Merge: Vacuum Fruits, Dodge Enemies
**Claimed by:** CBP | **Levels:** 6/9 solved | **Baseline:** 566 | **Actions:** click + undo

**Objects:** Fruits (various sizes), enemies, vacuum effect, merge zones
**Goal:** Click to vacuum nearby fruits together. Matching sizes merge into larger fruit. Dodge enemies. Clear all fruits.
**Interaction:** Click position triggers radial vacuum pulling fruits/enemies toward click point. UNDO reverts state.
**Key mechanic:** 2048-style merge with spatial physics. Enemies chase player clicks. Later levels require simultaneous goal delivery and enemy displacement strategies.
**Current state:** L1-L6 solved. L7 stuck — enemy reach exceeds merge time window.

---

### s5i5 — Slider-Card Rotation / Path Routing
**Claimed by:** McNugget | **Levels:** 6/8 solved | **Baseline:** 608 | **Actions:** click only

**Objects:** Colored bars (growable/shrinkable), patterned cards (two-way sliders), obstacles (walls), red cross markers (targets)
**Goal:** Grow colored bars along a path around obstacles to reach the red cross target.
**Interaction:** Click LEFT half of card → shrink. Click RIGHT half → grow. Vertical cards: TOP shrinks, BOTTOM grows.
**Key mechanic:** Bars grow in ONE direction per card. L5+ introduces rotation mechanics and blue rotation requiring green-free rows. Retract-before-reroute pattern for dependency chains.
**Current state:** L1-L6 solved. L7 route verified but GAME_OVER on first attempt — needs debugging.

---

### r11l — Pick-and-Place Creature Assembly
**Claimed by:** Nomad | **Levels:** 5/6 solved | **Baseline:** 167 | **Actions:** click only

**Objects:** Colored balls/limbs, compass targets, obstacles, creature assembly points
**Goal:** Click to pick up pieces, click destination to place. Assemble creatures at target locations.
**Key mechanic:** Each action triggers multi-frame animation (piece slides to click point). Ball CAN jump obstacles — only landing position matters. L5 introduces pickup-and-deliver mechanic.
**Current state:** L1-L5 solved. L6 mechanics unknown.

---

### cn04 — Jigsaw Connector: Sprite Alignment
**Claimed by:** Thor | **Levels:** 1/5 solved | **Baseline:** 779 | **Actions:** move + select + click

**Objects:** Sprites with connectors, alignment targets, rotation indicators
**Goal:** Click to select sprites, arrows to move, rotate to align connectors.
**Key mechanic:** Spatial puzzle about fitting connectors together. Select/deselect with click, move with arrows, rotate 90° CW.
**Current state:** L1 solved. Just started after completing sp80.

---

### g50t — Clone Replay / Maze Navigation
**Claimed by:** Sprout | **Levels:** 0/7 | **Baseline:** 575 | **Actions:** move + select

**Objects:** Player, clones, maze walls, replay triggers
**Goal:** Navigate maze. ACTION5 triggers clone replay — previous moves replayed by clones.
**Key mechanic:** Multi-phase puzzle where player's recorded path is replayed by clones to solve cooperative objectives. Movement step size = 6 pixels.
**Current state:** Claimed, exploring mechanics.

---

### bp35 — Gravity Platformer / Gem Collection
**Claimed by:** Legion | **Levels:** 0/9 | **Baseline:** 637 | **Actions:** left/right + click + undo

**Objects:** Player, gems, tiles (o=floor, x=wall), moving platforms, gravity
**Goal:** Side-scrolling platformer. Move left/right, gravity handles vertical. Collect gems.
**Key mechanic:** Moving platforms shift every other move — scanning/undoing corrupts state. Every click must be deliberate. BFS solver broken due to grid coordinate parsing issues. Needs visual/human-guided approach.
**Current state:** Claimed, mechanics mapped, coordinate mapping unsolved.

---

## Fleet Status Summary (updated 2026-04-12)

**16/25 games solved (64%). 6 in progress. 3 unclaimed.**

---

### re86 — Shape-Matching / Paint Zone Puzzle
**Solved by:** CBP | **Levels:** 8/8 | **Baseline:** 1071 | **Result:** 606 actions (1.8x efficiency) | **Actions:** move only

**Objects:** Hollow rectangles (deformable), crosses (border-shiftable), paint zones, walls, targets
**Goal:** Recolor pieces via paint zones, reshape via wall collision, position to match target pixel positions.
**Key mechanics:**
- **Paint zone spreading**: Zone touch triggers flood-fill animation → ENTIRE piece becomes zone color. Zone iteration order determines which zone wins when multiple overlap.
- **Wall deformation** (nogegkgqgd tag): dx collision = width-3/height+3. dy = inverse. Min dimension 6 checked before deform (so 7→4 possible).
- **Border-shifting**: Non-deformable crosses shift arm col/row ±3 on wall collision, enabling target coverage impossible with default arms.
- **L8 barrier**: 9 paint zones at rows 28-32 form impassable repaint wall. Solution: deform to 22x4 (4 rows tall) to fit in safe corridor between blocking zones, then deform to 4x22 (4 cols wide) to fit through barrier gap at cols 44-49.
**Discovery tips:** Pieces don't collide with each other. Color 4 = wildcard in win check. Zone iteration order is critical — first matching zone wins.

---

### m0r0 — Move+Click Puzzle
**Solved by:** Sprout | **Levels:** 6/6 | **Baseline:** 970 | **Result:** 181 actions (5.4x efficiency) | **Actions:** move + click

---

### wa30 — Sokoban with AI Movers (helpers + saboteurs)
**Solved by:** CBP | **Levels:** 9/9 | **Baseline:** 1564 | **Result:** 637 actions (2.5x efficiency) | **Actions:** move only

**Objects:** Puzzle pieces, goal slots, BLUE AI movers (helpers → correct slots), WHITE AI movers (saboteurs → wrong slots)
**Goal:** Deliver all pieces to correct slots; win when all in slots AND unlinked.
**Key mechanics:**
- **AI behavior is deterministic BFS**: one BFS step per player action, fully simulatable given state
- **Blue pickup is geometric** (manhattan-4), NOT reachability — pieces on blocked wall cells are grabbable by blues on any non-blocked neighbor
- **Whites are parasitic carriers**: they force-detach pieces from blues AND player mid-delivery if within manhattan-4. They DO re-grab from correct slots (undo progress) but NOT from wrong slots
- **Blues auto-rescue wrong-slotted pieces** (line 1157) — they don't exclude wrong-slot pieces from pickup, which makes wa30 winnable at all
- **ACTION5 + adjacent-to-carrying-white**: destroys white, drops piece at current cell
- **Whites can self-stall** when their BFS is blocked by their own deliveries (L6 exploit)
- **Wall handoff**: carried pieces pass through blocked positions but carriers cannot — direction faced at pickup determines carry offset

**Winning strategy per level**:
- L0: Pure BFS (no AI)
- L1: Engine greedy with one blue helper
- L2: Hand-coded wall handoff sequence
- L3: Trapped-player box — handoff feasibility table + blue cluster assignment + manhattan geometric pickup
- L4, L5: Engine greedy after L3 unblocked
- L6: Let white self-stall, destroy-white-to-drop, ferry pieces manually (saboteur exploit)
- L7: "Lower-white-first" opening book — BFS-to-adjacent kills lower white (~18 moves), 20-move cap on upper-chase, let smart_action finish. Key insight: don't try to kill both whites, commit to the winnable sub-goal and trust the system
- L8: Biased random search (seed=21, 5-30% random deviation from smart_action) found 67-move win; trapped white (60,56) in wall maze effectively dead on spawn

**Discovery tips:** Deterministic engine means found solutions can be baked as fixed action strings. `env.reset()` after a LOSE can leave stale state — use fresh `Arcade()` per search attempt. When greedy caps below target, try biased random from the greedy policy — sometimes the ceiling is local, not global.

---

| Category | Games |
|----------|-------|
| **Solved (23)** | sb26 8/8, vc33 7/7, cd82 6/6, lp85 8/8, ft09 6/6, sp80 6/6, tr87 6/6, sc25 6/6, tn36 7/7, tu93 9/9, ls20 7/7, s5i5 8/8, su15 9/9, cn04 5/5, ar25 8/8, bp35 9/9, re86 8/8, m0r0 6/6, r11l 6/6, g50t 7/7, ka59 7/7, wa30 9/9, sk48 8/8 |
| **Partial (2)** | dc22 5/6 (L6 new mechanics), lf52 6/10 (L7 research boundary) |

### Algorithmic Solver Results (2026-04-08 batch run)

| Result | Games |
|--------|-------|
| **WON** | ft09 6/6 (75 actions) |
| **Partial (1+ levels)** | r11l 1/6, s5i5 1/8, ls20 1/7, cn04 1/5, m0r0 2/6, re86 1/8 |
| **0 levels** | lp85, tn36, cd82, sb26, vc33, tu93, sc25, tr87, sk48, su15, wa30, ar25, dc22, g50t, lf52, sp80 |
| **Timeout** | bp35, ka59 |

**Gap analysis:** Most solver failures are output format/coordinate mapping issues, not wrong mechanics understanding. The solvers compute correct solutions internally but the translation to live API actions needs debugging per game.

Full results tracked in `SOLUTIONS_DB.json`.

---

## Universal Principles (from 11 solves)

### 1. Discovery Before Solving
First 5-10 actions should EXPLORE: click each object type once, move in each direction once. Map what's possible before planning.

### 2. Action Tiers
| Tier | Example | Recovery | Strategy |
|------|---------|----------|----------|
| Observation | Look at screen | Free | Maximize |
| Reversible | Click that toggles | 1 click | Explore freely |
| Consequential | Stamp that overwrites | 5+ clicks | Verify first |

### 3. Available Actions = Game Type
- `[6]` click-only → puzzle (toggle, rotate, constraint)
- `[1,2,3,4]` move-only → navigation (maze, sokoban)
- `[1,2,3,4,6]` move+click → cursor + interaction
- `[5]` SELECT present → confirmation/placement mechanic
- `[7]` UNDO present → use it when stuck

### 4. Zoom Out Before Zooming In
Pixels → Objects → Groups → Constraints → Mechanics. Solve at the highest abstraction level. Small multi-colored patterns ARE instructions. Same-colored objects in regular spacing = structural group.

### 5. Carry Patterns Across Levels
Rules evolve but build on prior levels. The first hypothesis for a new level = the rule that worked on the previous level. Test it before exploring alternatives.

### 6. Never Restart
Undo mistakes with reverse actions (LEFT click, opposite button). Restarting compounds cost across all previously-solved levels.

---

## All 25 Games — Toolset & Classification

L1 screenshots in `game-screenshots/`. Toolset determines game type before you see a single pixel.

| Game | Actions | Type | Levels | Baseline | Status | Machine |
|------|---------|------|--------|----------|--------|---------|
| cd82 | UP/DOWN/LEFT/RIGHT, SELECT, CLICK | cursor+stamp | 6 | 136 | **SOLVED** | — |
| sb26 | SELECT, CLICK, UNDO | pick+place | 8 | 153 | **SOLVED** | — |
| ft09 | CLICK | click puzzle | 6 | 163 | **SOLVED** | — |
| r11l | CLICK | click puzzle | 6 | 167 | 5/6 | Nomad |
| sc25 | UP/DOWN/LEFT/RIGHT, CLICK | move+click | 6 | 216 | **SOLVED** | — |
| tn36 | CLICK | click puzzle | 7 | 250 | **SOLVED** | — |
| vc33 | CLICK | click puzzle | 7 | 307 | **SOLVED** | — |
| tr87 | UP/DOWN/LEFT/RIGHT | move only | 6 | 317 | **SOLVED** | — |
| tu93 | UP/DOWN/LEFT/RIGHT | move only | 9 | 378 | **SOLVED** | — |
| lp85 | CLICK | click puzzle | 8 | 422 | **SOLVED** | — |
| sp80 | UP/DOWN/LEFT/RIGHT, SELECT, CLICK | full set | 6 | 472 | **SOLVED** | — |
| ls20 | UP/DOWN/LEFT/RIGHT | move only | 7 | 546 | **SOLVED** | — |
| su15 | CLICK, UNDO | click+undo | 9 | 566 | 6/9 | CBP |
| g50t | UP/DOWN/LEFT/RIGHT, SELECT | move+select | 7 | 575 | 0/7 | Sprout |
| ar25 | UP/DOWN/LEFT/RIGHT, SELECT, CLICK, UNDO | full set | 8 | 577 | **SOLVED** | — |
| s5i5 | CLICK | click puzzle | 8 | 608 | 6/8 | McNugget |
| bp35 | LEFT/RIGHT, CLICK, UNDO | partial move | 9 | 637 | 0/9 | Legion |
| sk48 | UP/DOWN/LEFT/RIGHT, CLICK, UNDO | move+click+undo | 8 | 696 | unclaimed | — |
| cn04 | UP/DOWN/LEFT/RIGHT, SELECT, CLICK | move+select+click | 5 | 779 | 1/5 | Thor |
| ka59 | UP/DOWN/LEFT/RIGHT, CLICK | move+click | 7 | 826 | unclaimed | — |
| m0r0 | UP/DOWN/LEFT/RIGHT, SELECT, CLICK | move+select+click | 6 | 970 | unclaimed | — |
| re86 | UP/DOWN/LEFT/RIGHT, SELECT | move+select | 8 | 1071 | unclaimed | — |
| dc22 | UP/DOWN/LEFT/RIGHT, CLICK | move+click | 6 | 1192 | unclaimed | — |
| lf52 | UP/DOWN/LEFT/RIGHT, CLICK, UNDO | move+click+undo | 10 | 1211 | unclaimed | — |
| wa30 | UP/DOWN/LEFT/RIGHT, SELECT | move+select | 9 | 1564 | unclaimed | — |
