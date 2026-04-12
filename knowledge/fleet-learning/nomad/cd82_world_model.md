# cd82 World Model — Complete Game Mechanics

*2026-04-07, Nomad + dp interactive session, levels 0-3 solved*

## Game Type
Color painting puzzle. Paint the canvas to match the target pattern using two stamp tools.

## Elements

| Element | Location | Function |
|---------|----------|----------|
| **Target/Palette** | Top-left, yellow-bordered | Shows the EXACT pattern the canvas must match |
| **Indicators** | Top-right, on green bar | Clickable color swatches — click to load color into cursors |
| **Big cursor** | Orbits canvas on a circle | Red-bordered, fills FULL WIDTH of canvas when stamped |
| **Small cursor** | Sits on top of big cursor | Smaller red element, fills SMALL PORTION when stamped |
| **Canvas** | Center | The area to be painted. Starts white-top/black-bottom each level |
| **Step counter** | Bottom bar | Decrements with each action |

## Two Stamp Tools

| Tool | Activation | Scope | Shape |
|------|-----------|-------|-------|
| **Big cursor** | SELECT (action 5) | Full canvas width | Cardinal = half fill, 45° = diagonal triangle |
| **Small cursor** | CLICK on it (action 6 at its position) | Small portion | Small rectangle overlay |

## Big Cursor Positions and Effects

The big cursor orbits the canvas on 8 clock positions:

| Position | How to reach from 12 | Stamp shape |
|----------|----------------------|-------------|
| 12 (top) | start | Top half rectangle |
| 1:30 (upper-right) | RIGHT | Upper-right triangle (diagonal) |
| 3 (right) | RIGHT, DOWN | Right half rectangle |
| 4:30 (lower-right) | RIGHT, DOWN, DOWN | Lower-right triangle (diagonal) |
| 6 (bottom) | RIGHT, DOWN, DOWN, LEFT | Bottom half rectangle |
| 7:30 (lower-left) | continue from 6: LEFT | Lower-left triangle |
| 9 (left) | continue: UP | Left half rectangle |
| 10:30 (upper-left) | continue: UP or from 12: LEFT | Upper-left triangle |

**Movement is context-sensitive**: which arrow key continues rotation depends on current position. At top: LEFT/RIGHT. At sides: UP/DOWN. The cursor always moves along the circle.

## Color Selection

- CLICK an indicator square at the top-right bar to load that color into BOTH cursors
- The cursors adopt the clicked color
- Clicking an indicator does NOT reset the canvas or cursor position
- White indicator position: cols 28-30 (value 15) — the FIRST color square after the gap
- Not all indicators are needed — only the colors in the target pattern

## Planning Methodology

### 1. Analyze the target (ZERO COST)
- The palette image IS the target
- Identify each color's shape, size, and position
- Determine which colors are needed (ignore irrelevant indicators)

### 2. Determine starting delta
- Canvas starts white-top, black-bottom each level
- What's already correct? Don't repaint it.
- What needs to change? Only stamp the delta.

### 3. Decompose target into stamp operations
- Each color region = one stamp from a specific position
- Large fills (half/diagonal) = big cursor (SELECT)
- Small overlays = small cursor (CLICK)
- **Layering order**: stamps overwrite. Paint in order so each stamp only ADDS correct pixels:
  - Background rectangles first (cardinal positions)
  - Diagonal overlays next
  - Small precise overlays LAST

### 4. Execute with pre-action verification
- **Batch moves freely** — low cost, no canvas change
- **VERIFY position before every stamp** — look at the image, confirm cursor is where intended
- **Never batch a stamp with moves** — always check between the last move and the stamp

## Action Cost Model

| Action | Canvas Risk | Recovery Cost | Pre-check? |
|--------|-----------|---------------|------------|
| Arrow keys (move) | None | 0 steps | No |
| CLICK indicator | None (color change only) | 0 steps | No |
| CLICK canvas (small stamp) | **Overwrites small area** | 3-5 steps | **YES** |
| SELECT (big stamp) | **Overwrites large area** | 5-10 steps | **YES** |
| Planning/looking | None | 0 steps | N/A — always free |

## Key Lessons Learned

1. **Think before you paint**: Mental simulation is free. Recovery is expensive.
2. **Verify before high-cost actions**: Check cursor position AND color before stamping.
3. **Trust what you see, not what you computed**: When data contradicts observation, re-examine the data.
4. **Only stamp the delta**: Don't repaint what's already correct.
5. **Order stamps by scope**: Large background fills first, small overlays last. Each stamp should only add correct pixels.
6. **Context-sensitive controls**: The same arrow key does different things at different positions. Verify the result.
7. **Irrelevant options exist**: Not all indicators are needed. Clicking wrong ones wastes steps.
8. **When assumptions fail, recheck**: If something "doesn't exist" but you need it, your search was wrong, not reality.

## Solved Levels

| Level | Steps | Baseline | Strategy |
|-------|-------|----------|----------|
| L1 | 5 | 41 | White from 6 o'clock (canvas starts with black, just add white bottom) |
| L2 | 10 | 8 | White from 12, olive from 4:30 (black already correct) |
| L3 | ~35 | 30 | Cyan from 6 (rectangle), teal from 3 (rectangle), white from 10:30 (diagonal), olive via small cursor CLICK at 12 |

## Level Progression Pattern

- L1: 1 stamp (1 color to add)
- L2: 2 stamps (2 colors: 1 diagonal + 1 existing)
- L3: 4 stamps (3 big + 1 small, 4 colors)
- L4+: Expect more colors, more stamps, more complex layering

## L4 Key Lesson: Partially Obscured Shapes

The olive shape in L4's target appeared as:
```
          O O O O
          O O O .
          O O . .
          O . . .
```

This LOOKS like a triangle with its right angle at upper-right. But it's actually a **full diagonal stamp from 10:30 (upper-left 45°)** that is **partially obscured** by brown (from the left) and white (from the right).

**The visible shape ≠ the stamp shape.** The stamp is always a full-width half or diagonal. The visible shape is what remains AFTER other stamps cover parts of it.

**To identify the correct stamp:**
1. Look at the EDGES of the color region, not its overall shape
2. The diagonal edge orientation tells you the stamp position (which 45° angle)
3. The direction the color fills FROM tells you which side of the diagonal it's on
4. The straight edges (vertical/horizontal) are created by OTHER stamps covering the diagonal

**L4 optimal sequence** (learned through trial):
1. Brown from 9 (left half)
2. Olive from 10:30 (upper-left diagonal — covers both halves in upper area)
3. White from 3 (right half — carves olive, leaving it only in upper-right)
4. Maroon small cursor from 9 (small rectangle middle-left)

**L4 actual sequence** (with recovery):
1. Brown from 9 ✓
2. White from 3 ✓ (did this before olive — wrong order)
3. Olive from 1:30 attempt (wrong — that's upper-RIGHT, olive diagonal is upper-LEFT)
4. Recovery: multiple attempts
5. Olive from 10:30 ✓ (correct)
6. Brown from 9 again (recovery — olive overwrote brown)
7. Maroon small from 9 ✓

**Cost of wrong order**: ~10 extra steps for recovery vs optimal 4-stamp solution.
