# cd82 Mechanics — World Model

*2026-04-07, Nomad + dp interactive session*

## Game Elements

- **Big cursor**: Red-bordered rectangle, orbits canvas on a circle (8 positions like a clock)
- **Small cursor**: Smaller red element, separate from big cursor
- **Canvas**: Central area to be painted to match target
- **Palette** (top-left): Shows the TARGET pattern — this IS what the canvas should look like
- **Indicators** (top-right): Clickable color swatches. Click to change big cursor's fill color
- **Step counter** (bottom bar): Decrements with each action

## Cursor Mechanics

**Big cursor**: Fills full-width diagonal or half when SELECT is pressed. Creates large shapes.
**Small cursor**: Fills small portion. Creates small rectangles/overlays.

**Movement**: Arrow keys rotate the big cursor around the canvas circle.
- The circle has ~8 positions: 12, 1:30, 3, 4:30, 6, 7:30, 9, 10:30
- Which key continues rotation depends on current position:
  - At 12: RIGHT goes to 1:30, LEFT goes to 10:30
  - At 1:30: DOWN goes to 3, UP goes to 12
  - At 3: DOWN goes to 4:30, UP goes to 1:30
  - At 4:30: LEFT goes to 6, etc.
- Cardinal positions (12, 3, 6, 9) → stamp creates HALF fills (top/right/bottom/left)
- Diagonal positions (1:30, 4:30, 7:30, 10:30) → stamp creates TRIANGLE fills

## Action Cost Model

| Action | Canvas Change | Recovery Cost | Pre-check Required |
|--------|-------------|---------------|-------------------|
| Move (arrows) | None | 0 (just pick another direction) | No |
| Click indicator | Changes cursor color only | 0 | No |
| SELECT (stamp) | **Overwrites canvas** | Multiple steps to repaint | **YES — verify position first** |

**Key principle**: Moves are cheap, stamps are expensive. ALWAYS verify cursor position before stamping.

## Planning Methodology

1. **Analyze target**: Look at palette, identify each color's shape, size, position
2. **Identify starting state**: Canvas starts white-top/black-bottom each level
3. **Determine stamp sequence**: Background first, overlays last. Later stamps overwrite earlier ones.
4. **Determine cursor type**: Big cursor for large fills, small cursor for precise overlays
5. **For each stamp**:
   a. Select the right color (click indicator) — LOW COST
   b. Batch move to intended position — LOW COST
   c. **VERIFY position matches intent** — ZERO COST (just look)
   d. Only then SELECT — HIGH COST

## Stamp Sequence Design

**Rule**: Each stamp should only ADD correct pixels, never damage previously correct ones.

**Order principle**: 
- Large background areas first
- Smaller overlay areas last
- If two colors overlap, the one that should be VISIBLE goes last

**Efficiency**: Check what's already correct. Canvas starts with white top + black bottom. If target has white on top, don't repaint it. Only stamp what's DIFFERENT.

## Recovery

If a stamp goes wrong:
- Recovery = re-stamp the damaged area with correct color
- Cost = indicator click + moves + another stamp
- Minimum recovery cost: ~3-5 steps per wrong stamp
- Prevention (verify before stamp) costs 0 steps

## Meta-Learning

This is reverse-engineering: visualize the final output, mentally decompose it into available operations, verify each step internally before committing. 

The same principle applies to any consequential action:
- Low-cost actions (exploration, movement, color selection): batch freely
- High-cost actions (stamping, committing, deploying): verify context first
- Zero-cost actions (planning, visualization, checking): do as much as possible

"Think before you paint. Verify before you commit. Recover costs more than prevention."
