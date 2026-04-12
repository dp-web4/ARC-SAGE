# bp35 Progress — Legion

## Key Discoveries

1. **Gravity is UPWARD** (vivnprldht=True, dy=-1). Player falls toward the top of the screen.
2. **Row numbers increase downward in grid, but upward on screen.** Row 28 (gem) is near the top of the screen.
3. **Green blocks are breakable 'x' tiles.** Light blue tiles are solid 'o' (not breakable).
4. **Moving platforms shift every other move** — this changes which tiles are clickable. The game state is move-count-dependent.
5. **Breakable tiles from starting camera:** Only at y=6 (x=12,18,24) — 3 tiles
6. **After RIGHT x4 + LEFT x2:** Additional tiles at (24,12) and (24,18) become breakable
7. **After first float up:** More tiles visible at y=15 (x=15,21,27) and y=21 (x=15,21,27) and y=33 (x=33)
8. **After second float:** More tiles at y=13 (x=27,30)
9. **Player keeps overshooting the gem** — floats all the way up into moving platforms and dies
10. **The gem at grid (3,28) needs to be reached at col 3** — player must be at the right column when floating

## Grid Map (Level 1)
```
Row  0-4:  wwwwwwwwwww  (moving platforms — DEADLY when touching)
Row  5:    mmmmmmmmmmm  (moving platform — shifts every 2 moves)
Rows 6-11: oo·······oo  (air in middle, solid walls on sides)
Row 12:    oo n     oo  (PLAYER at col 3)
Row 13:    ooooooo·ooo  (ceiling — player walks on this with gravity up)
Rows 14-15:oo·······oo  (air)
Row 16:    oooooxxxxoo  (breakable at cols 5-8)
Row 17:    ooooo····oo  
Rows 18-19:ooxxx····oo  (breakable at cols 2-4)
Row 20:    ooxxxoooooo  (breakable at cols 2-4)
Rows 21-22:oo·······oo  (air)
Row 23:    oo··xxx··oo  (breakable at cols 4-6)
Rows 24-25:oo·······oo  (air)
Row 26:    oooooxxxooo  (breakable at cols 5-7)
Row 27:    oo·······oo  (air)
Row 28:    oo +     oo  (GEM at col 3!)
Row 29+:   ooooooooooo  (solid ground)
```

## What Works
- Breaking tiles by clicking what you SEE (green blocks)
- Floating up by walking off platform edges
- Multi-stage ascent: break, float, break more, float higher

## What Doesn't Work
- Computing grid-to-screen coordinates (camera offset changes)
- Scanning with undo (corrupts game state via moving platforms)
- Uncontrolled floating (overshoots gem, hits moving platforms)

## Next Steps
- Need to control float distance — break only enough tiles to float to gem level, not past
- The gem is at col 3. Player needs to be AT col 3 when they float through row 28
- Moving platforms at rows 0-5 are deadly — must not float all the way up
- Consider: break tiles below gem (row 26 cols 5-7) and approach from the side at row 28

## Update: BFS Solver is BROKEN

The BFS solver's grid parsing produces WRONG tile coordinates. All 5 BFS target
tiles (4,12), (4,15), (5,19), (5,9), (4,16) are NOT breakable 'x' tiles — they're
spaces or 'o' tiles. The BFS solution is invalid.

The actual 'x' tiles are at:
- Row 16: cols 5-8
- Rows 18-20: cols 2-4
- Row 23: cols 4-6
- Row 26: cols 5-7

Gravity is DOWNWARD. The gem at row 28 is BELOW the player at row 12.
Player needs to navigate DOWN through these breakable tile layers.
Each layer has 'x' tiles in different columns — need to clear a zigzag path.

Need to solve by vision, not BFS.

## Update 2: Key Mechanic Understanding

**The player walks on 'o' tiles (light blue). These CANNOT be broken.**
**Only 'x' tiles (green blocks) can be broken by clicking.**

The puzzle: break 'x' tiles in the green block areas to create gaps, then
navigate the player (who walks on 'o' tiles) to positions where the 'o'
platform ends and the player falls through a gap created by broken 'x' tiles.

The player NEVER stands on 'x' tiles directly (they're in separate areas).
The 'x' tiles form walls/barriers that block the player's fall path. Breaking
them opens fall routes through the level.

This means: click green blocks that are IN the player's vertical fall path
(below the edge they'll walk off), not green blocks at the player's walking level.

The game is a connected-path puzzle, not a "break the floor" puzzle.

**BFS solver is broken** — its grid coordinate parsing is wrong. All solutions
must be done visually.

**Moving platforms shift every other move** — this means scan+undo corrupts
game state. NO SCANNING. Every click must be deliberate based on what you SEE.

## L1 SOLVED! L2 Path Planned

### L1 Solution (reproducible):
RIGHT x4, CLICK(46,33), LEFT x2, CLICK(27,30), CLICK(21,30), CLICK(15,30),
CLICK(27,36), CLICK(21,36), CLICK(15,36), LEFT x3, RIGHT x5, CLICK(36,30), LEFT x5

### L2 Path Plan (col 5 is the golden column):
1. Break (5,13) and (5,14) → fall to (5,15) pillar
2. Walk RIGHT to col 6 → fall through 15-20 to (6,21) breakable
3. Walk LEFT to (5,21) → fall through 22-24 to (5,25) breakable
4. Break (5,25) and (5,26) → fall to (5,29) solid
5. Walk LEFT to (3,29) breakable → break → fall to (3,32) breakable
6. Walk RIGHT to (5,32) → break (5,33) → land (5,34)
7. Fall from (5,35-36) through to (5,40) breakable
8. Break (5,40) → fall to (5,42) = GEM!

Key: col 5 avoids all spikes except row 31 (but solid at 29 stops you).
Switch to col 3 for rows 29-32 (safe corridor), then back to col 5.

## L2: STUCK

### What We Know
- L2 grid has 103 rows, gem at (5, 42)
- Two rows of breakable `x` tiles at rows 13-14 (cols 2-8) form a wall
- Green blocks visible on screen ARE the x tiles, but NOT clickable from starting position
- Moving platforms at rows 0-5 kill on contact and shift every other move
- Undo triggers moving platform shifts which often kill the player
- The ONLY clickable tiles found were below the player at y=34 on the RIGHT side
- Breaking those led to a dead end with no further breakable tiles
- Col 5 is the safe path through the level (avoids all spikes)

### What We Don't Know
- WHY the x tiles at rows 13-14 aren't clickable from the starting position
- The exact click coordinate system (scene graph transform, not simple formula)
- Whether L2 requires a different approach entirely (maybe moving platforms create gaps?)

### Key Blocker
The click coordinate mapping for this game's custom scene graph engine is unsolved.
Every formula attempted fails. The game uses nested coordinate transforms that
don't match the simple `row * 6 - camera_offset` model.

### Recommendation
Try autonomous solver with vision (gemma4:e4b) — let the model see the screen
and reason about what to click, rather than computing coordinates.
Or study the source code's coordinate transform chain more carefully.

## BREAKTHROUGH: Pixel Detection Solves Coordinate Problem

The click coordinates were wrong because I was estimating player position
visually from the 256x256 displayed image. Using numpy pixel detection:
- Find yellow pixels → player position in 64px game space
- Find green pixels → breakable block centers

This gives EXACT screen coordinates. All green blocks became clickable
once I used the right coordinates.

### L2 Key Finding
- Player at screen (22, 18), NOT (22, 33) as I was guessing
- Green wall at screen y=27-33, NOT y=16-22
- All 14 green blocks at y=27 and y=33 are breakable
- But breaking ALL of them creates uncontrolled falls into spikes
- Must break ONLY tiles on the safe path (col 5 → col 3 → col 5)

### Technique for ALL future levels:
1. Use pixel color detection to find player + block positions
2. Map to grid coordinates via the known grid layout
3. Break ONLY tiles on the planned safe path
4. Navigate one fall at a time

## L2 Safe Path Analysis (COMPLETE)

Spike locations and safe corridors fully mapped:
- Rows 15-17: Spikes cols 2-4 → use cols 5-8 (pillar at col 5)
- Rows 22-24: Spikes cols 6-8 → use cols 2-5
- Row 28: Spike col 8 → use cols 2-7
- Row 31: CRITICAL → ONLY col 3 is safe (all others spiked)
- Rows 36-37: Spikes cols 2-4 → use cols 5-8
- Rows 41-42: Spikes cols 6-8 → use cols 2-5 (gem at col 5)

Zigzag path: col 5 down through wall → col 5-8 (avoid left spikes) →
col 2-5 (avoid right spikes) → col 3 ONLY (row 31 bottleneck) →
col 5-8 (avoid left spikes) → col 2-5 to gem

### Pixel Detection Technique (WORKING)
- Yellow pixels (R>200,G>200,B<80) → player position
- Green pixels (R<80,G>150,B<80) → breakable block centers
- Pink pixels (R>180,G<100,B>100) → gem
- Divide by 4 (256→64 scale) for game coordinates
- Click at block center coordinates → WORKS

### L1 Solution (stable, reproducible):
RIGHT x4, CLICK(46,33), LEFT x2, CLICK(27,30), CLICK(21,30), CLICK(15,30),
CLICK(27,36), CLICK(21,36), CLICK(15,36), LEFT x3, RIGHT x5, CLICK(36,30), LEFT x5
