# cd82 COMPLETE — 6/6 Levels, 127 Steps (Baseline 136)

*2026-04-07, Nomad + dp interactive session*

## Game Summary

cd82 is a circular stamp painting puzzle. Paint the canvas to match a target pattern using two stamp tools (big cursor = full-width, small cursor = small overlay) that orbit around the canvas on a circle.

**Result**: 6/6 levels, 127 steps, beating human baseline of 136.

## Level Solutions

### L1 (5 steps, baseline 41)
Target: white bottom half. Canvas starts white-top, black-bottom.
- Navigate white cursor to 6 o'clock: RIGHT, DOWN, DOWN, LEFT
- SELECT

### L2 (10 steps with recovery, baseline 8)
Target: white top, black bottom, olive diagonal bottom-right.
- SELECT white from 12 (white top half — already partially there)
- Click olive, navigate to 4:30: RIGHT, DOWN, DOWN
- SELECT olive (bottom-right diagonal)
- Black already in place

### L3 (~35 steps with recovery, baseline 30)
Target: cyan bottom, teal right, white upper-left diagonal, olive small top.
- Click cyan, navigate to 6, SELECT (bottom half)
- Click teal, navigate to 3, SELECT (right half, overwrites cyan lower-right)
- Click white (col 29!), navigate to 10:30, SELECT (upper-left diagonal)
- Click olive, navigate to 12, CLICK small cursor (small rectangle top)

### L4 (~30 steps with recovery, baseline 21)
Target: brown left, white right, olive upper-right (partially obscured), maroon middle-left small.
- Click brown, navigate to 9, SELECT (left half)
- Click olive, navigate to 10:30, SELECT (upper-left diagonal — visible only in upper-right after brown covers left)
- Click white, navigate to 3, SELECT (right half — carves olive, leaves it in upper-right only)
- Click maroon, navigate to 9, CLICK small cursor (middle-left)

**Optimal order discovered**: brown 9 → olive 10:30 → white 3 → maroon small 9.
Earlier stamps get carved by later ones. Olive BEFORE white, not after.

### L5 (~23 steps, baseline 19)
Target: teal upper-left, brown thin strip, olive lower-right, cyan small top.
- Click brown, navigate to 1:30, SELECT (upper-right diagonal)
- Click teal, navigate to 7:30, SELECT (lower-left diagonal, carves brown)
- Click olive, navigate to 4:30, SELECT (lower-right diagonal, carves both)
- Click cyan, navigate to 12, CLICK small cursor (top)
- Black was already the starting canvas color — no stamp needed

### L6 (~27 steps, baseline 17)
Target: teal right, cyan upper-left, black lower-left, maroon small left, white small top.
- Click teal, navigate to 3, SELECT (right half rectangle)
- Click cyan, navigate to 10:30, SELECT (upper-left diagonal)
- Black already in place (starting canvas)
- Click maroon, navigate to 9, CLICK small cursor (left)
- Click white, navigate to 12, CLICK small cursor (top)

## Meta-Learning: Shape Decomposition

### The Key Skill: Reverse-Engineering from Target

1. **Remove small stamps mentally** — replace them with the color they overlay (always the background/big-stamp color). This reveals the big-stamp-only image.

2. **Identify each big stamp's shape** — rectangles (from cardinal positions) or triangles (from 45° positions). Look at EDGES:
   - Straight vertical/horizontal edges = boundary between two rectangle stamps
   - Diagonal edges = boundary created by a diagonal stamp

3. **Determine which stamp is on top** — the color that's FULLY visible (no other color covers it) was stamped LAST. Work backwards.

4. **Check what's already there** — canvas starts white-top, black-bottom. If the target has black in the lower area, you might not need to stamp it at all.

### Partially Obscured Shapes

**The visible shape ≠ the stamp shape.** Every big stamp is a full-width half or full-width diagonal. The visible shape is what remains after later stamps cover parts of it.

To identify the correct stamp position for a partially obscured color:
- Find its DIAGONAL edge → that tells you the stamp angle (which 45° position)
- Find which SIDE of the diagonal the color is on → that tells you 10:30 vs 4:30 or 1:30 vs 7:30
- The STRAIGHT edges are created by other stamps (rectangles from cardinal positions) covering the diagonal

### Stamp Ordering Rules

1. **Background/largest area first** — it gets carved by everything else
2. **Diagonals in the middle** — they create the angular boundaries
3. **Rectangles that carve diagonals** — they create the straight boundaries
4. **Small cursor stamps LAST** — they sit on top of everything
5. **Don't stamp what's already correct** — check canvas starting state

### Confidence-Based Execution

- **Highest confidence stamps first** — if you're sure about teal from 3, do it first
- **Lowest consequence first** — background stamps are cheapest to redo
- **Verify before every consequential action** — look at the image, confirm position
- **Low-cost recovery** — small stamps are easily re-applied, big stamps cost more to fix

## Action Cost Lessons from This Game

| Mistake | Cost | Prevention |
|---------|------|------------|
| Olive from 1:30 instead of 10:30 (L4) | ~10 recovery steps | Analyze diagonal edge direction, not visible shape |
| White indicator at wrong column | ~5 wasted steps | Find actual pixel data, don't assume column spacing |
| Stamping before reaching target position | ~5 recovery steps | Always verify position visually before SELECT |
| Restarting to L1 unnecessarily | ~11 steps lost | Never reset — recover from current state |
| Stamping olive from 3 (small cursor, L4) | ~3 recovery steps | Small cursor from cardinal = small rectangle, wrong tool for diagonal area |
