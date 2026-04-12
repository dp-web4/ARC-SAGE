# s5i5 Playbook — Learned from Interactive Play

*2026-04-08/09, Claude Opus 4.6 + dp*

## Game Type
Path-routing puzzle. Grow colored bars to reach target crosses. Walls block paths and must be moved first.

## Core Physics
- **Cards** are two-way sliders: RIGHT half grows/pushes, LEFT half shrinks/retracts
- **Bars** grow in one direction toward their target cross
- **Walls** are rigid structures that must be moved out of the bar's path
- **Yellow coupling (L4+)**: ALL yellow pixels (bar + wall pieces) respond to every click. Corner cards move their specific wall a LOT + nudge all yellow a little. Center card grows the bar a LOT + nudges everything a little.

## Universal Strategy
1. Identify the bar(s) and cross(es)
2. Identify walls blocking the path
3. Move ALL walls BEFORE growing any bars
4. Move walls one at a time, verify after each click
5. Never reset — use LEFT clicks to undo mistakes
6. Think before clicking — thinking is free, moving is expensive

## Epistemic Discipline
- **Don't perseverate**: if something doesn't work, STOP and change approach
- **Track negative feedback**: remember what FAILED, not just what worked
- **Model physics**: cause → effect → sequence. Predict before acting.
- **Visualize solved state**: work BACKWARD from the goal to determine the move sequence

## Card Positions (consistent across levels)
- Cards have RED borders, GREEN dividers at center
- RIGHT half = divider_x + 3, LEFT half = divider_x - 3
- Divider positions: typically x=9, 31, 51 (but VERIFY each level — L4 has 5 cards not 6)
- Top row y≈48, Bottom row y≈57

## Level Solutions

### L1 (13 clicks)
Two bars, two crosses. No walls. Just grow.
- Upper card RIGHT x7: click(46, 20)
- Center card BOTTOM x6: click(24, 44)

### L2 (26 clicks)
Two bars, inverted-U obstacle. Route: right→up→shift→down.
- Card1 RIGHT x8: click(12, 57)
- Card2 RIGHT x8: click(27, 57)
- Card3 RIGHT x4: click(42, 57)
- Card4 RIGHT x6: click(57, 57)

### L3 (46 clicks)
Two bars, two crosses. Two wall structures with colored segments.
Strategy: push each wall down/out of the path, then extend bars.

**Left wall (red+blue+gray):**
- C4R x8: click(15, 57) — blue pushes, unlocks wall
- C1L x6: click(10, 48) — wall shifts down, clears row 27

**Right wall (orange-lg+green+gray):**
- C6R x7: click(53, 57) — push orange-lg up (stops when hits pink)
- C3L x5: click(48, 48) — retract orange-lg horizontally past col 49

**Extend bars:**
- C2R x12: click(34, 48) — cyan to left cross
- C5R x8: click(34, 57) — pink to right cross

### L4 (in progress — fully analyzed, not yet executed)

**Layout:** ONE yellow bar at bottom (r42-43 c30-32), ONE cross at top (r9-11 c30-32), FOUR horizontal yellow wall pieces at different columns, ONE large orange vertical bar.

**5 cards (not 6!):**
- TL (top-left): controls GREEN wall. RIGHT=click(12,48), LEFT=click(7,48)
- TR (top-right): controls BLUE wall. RIGHT=click(57,48), LEFT=click(51,48)
- CTR (center): grows YELLOW BAR. RIGHT=click(34,54), LEFT=click(28,54)
- BL (bottom-left): controls ORANGE wall. RIGHT=click(12,57), LEFT=click(7,57)
- BR (bottom-right): controls RED wall. RIGHT=click(57,57), LEFT=click(51,57)

**Initial wall positions (fresh L4):**
- Green-attached yellow: r15-17, c10-11 (6px)
- Blue-attached yellow: r12-14, c51-52 (6px)
- Orange-attached yellow: r24-26, c19-20 (6px)
- Red-attached yellow: r18-20, c45-46 (6px)
- Bar: r42-43, c30-32 (6px)

**The coupling problem:** CTR-R grows the bar AND expands all wall pieces horizontally. If walls are between bar and cross, CTR-R pushes walls INTO the bar's path. MUST move walls first.

**The stacking problem:** 3 walls go ABOVE the cross (r0-8). They need to be staggered (r0-2, r3-5, r6-8) so they don't collide. Push topmost first to make room.

**The orange exception:** The orange wall goes DOWN (not up) because:
- 4 walls × 3 rows = 12 rows. Only 9 rows available above cross (r0-8). Can't fit all 4.
- Orange is attached to a tall vertical bar below the cross — it can clear downward.
- 3 walls above (9 rows, perfect fit) + 1 wall below = all clear.

**Correct L4 sequence (VERIFIED — 35 clicks, solved at step 120):**
1. Push BLUE wall to r0-2: TR-R x4 (click 57,48)
2. Push GREEN wall to r3-5: TL-R x3 (click 12,48)
3. Push RED wall to r6-8: BR-R x4 (click 57,57)
4. Stagger: TR-R x1 (blue r3→r0) + TL-R x1 (green r6→r3) — now blue r0-2, green r3-5, red r6-8
5. Push ORANGE wall DOWN past r43: BL-L x7 (click 7,57) — orange r24→r45
6. CTR-R x7 (click 34,54) — bar grows from r42 to cross, gap closes progressively
7. Total: 4+3+4+1+1+7+7 = 27 wall moves + 7 bar grows = ~35 clicks for L4

**Staggering is CRITICAL:** Green and red both land at r6-8 initially (same rows, different cols). They won't collide at their own columns, but CTR-R expands ALL yellow horizontally. Must push blue to r0-2 and green to r3-5 BEFORE growing bar, so the three walls are at r0-2, r3-5, r6-8 (no overlap in rows).

**Gap-closing mechanic:** CTR-R doesn't instantly fill the bar. The gap between bar-top and bar-body closes progressively: each CTR-R reduces the gap by ~3 rows. Takes 4-5 CTR-R clicks to close a 12-row gap.

**What failed and why (negative feedback — cost ~300 clicks across attempts):**
- Growing bar (CTR-R) before clearing walls → walls expanded into path, blocked bar
- Pushing walls wrong direction → wasted budget, created collisions
- Batching clicks without checking → wasted 10+ clicks on no-ops
- Merging bar with wall (both yellow at same position) → couldn't separate them
- Using wrong corner card for a wall → no effect
- CTR-L shrinks BOTH bar AND walls → can partially recover but loses progress
- Once walls merge with bar, corner cards can't separate them
- Not staggering walls → green and red at same rows, expand into each other
- Pushing all walls UP without considering that 4×3 > 9 rows available above cross → orange must go DOWN

**Key insights from dp coaching:**
- "Visualize the solved state and reverse-engineer the sequence"
- "3 walls above the cross staggered (r0-2, r3-5, r6-8). Orange goes below. This is determined by physics: 4×3=12 rows won't fit in 9 rows above cross."
- "The orange bar is different — it's vertical, below the cross. It can clear DOWN instead of up."
- "Don't perseverate. Track negative AND positive feedback concurrently."
- "Model the physics. Cause, effect, sequence. You can write code — apply the same discipline."

## Principles Learned (from dp coaching)

1. **Visualize the solved state first** — work backward from the goal
2. **Think before moving** — thinking is free, moving is expensive  
3. **One click at a time** — verify after every move
4. **Walls before bars** — always. No exceptions.
5. **Track what failed** — negative feedback prevents perseveration
6. **Model the physics** — rigid bodies, coupling, cause→effect→sequence
7. **Topmost first** — when stacking, make room from the top down
8. **Objects are coupled** — same-color elements respond to ALL clicks of that color
9. **Each wall needs its own card** — don't assume one card moves everything
10. **Retract to recover** — LEFT clicks undo RIGHT clicks, but prevention > recovery
11. **Never restart levels** — the cost compounds. Fix in place.
12. **Budget awareness** — every wrong click costs 1 step AND recovery overhead
13. **Chain growth order** — grow from ROOT outward. Root moves everything downstream.
14. **Rotation before growth** — orient the bar correctly BEFORE extending it
15. **Each level adds a mechanic** — L1-2=growth, L3=walls, L4=coupling, L5=dependency, L6=rotation+chains
16. **Every chain segment has a task** — don't skip segments. Chain order = route order. If route has 4 turns, each of 4 bars handles one in sequence. Skipping a bar wastes it.
17. **Rotation before growth** — use + controls to point bar in desired direction, THEN use R to grow. L to shrink.
18. **Resource management** — 4 bars = 4 segments. Plan the full route BEFORE growing. Each bar is a scarce resource.

## L5 Analysis (in progress — step 194/608)

**Layout:** 2 crosses, 2 bars. Purple walls are FIXED (no controls). 4 cards.
- Cross A: r36-38, c21-23 (bottom-left)
- Cross B: r24-26, c36-38 (was hidden under cyan initially)
- Cyan bar: r24-26, horizontal. C4R grows RIGHT. Reaches Cross B.
- Green bar: TWO clusters — r18-20 c10-14 (left, near cross A path) and r30-34 c54-56 (right). Reaches Cross A.
- Gray wall: r30-43 c21-23. C1R shifts LEFT, C1L shifts RIGHT. Must be cleared from c22.
- Blue wall: r27-29 c21-55. C1L shrinks LEFT edge. Blocks green growth when overlapping cyan.
- Purple walls: r9-17 and r21-26 at c15-17. FIXED. Gap at r18-20 is the passage.

**Card mapping:**
- C1R (12,56): shifts gray LEFT + grows blue RIGHT
- C1L (6,56): shifts gray RIGHT + SHRINKS blue LEFT edge
- C2R (27,56): shifts green DOWN + grows orange
- C2L (21,56): shifts green UP
- C3R (42,56): grows blue RIGHT + grows green (right cluster LEFT)
- C3L (36,56): does nothing visible
- C4R (57,56): grows CYAN RIGHT (bar only, no coupling!)
- C4L (51,56): shrinks CYAN RIGHT edge

**Critical dependency chain:** Cyan blocks blue → blue blocks green → green can't reach Cross A.
**Fix:** Retract cyan FIRST. Then shrink blue (C1L). Then green can grow through purple gap.

**L5 sequence (planned):**
1. Retract cyan fully (C4L x5)
2. Move gray wall out of c22 (C1R x3)
3. Shrink blue away from c22 (C1L x1)
4. Grow green DOWN to purple gap r18-20 (C2R x2)
5. Grow green RIGHT through gap (C3R — need to verify this works with cyan retracted)
6. Grow green DOWN to cross A at r36 (C2R x several)
7. LAST: Grow cyan RIGHT to Cross B (C4R x5)

**Key failures and lessons:**
- Extended cyan before clearing walls → blocked blue → blocked green → wasted 50+ clicks
- C3L doesn't shrink blue — C1L does (wrong card assumption)
- C3R grows green's RIGHT cluster, may not grow LEFT cluster rightward
- Green has two growth directions: C2R=down, C3R=right (but which cluster?)
- Must retract ALL bars before moving walls

**L5 SOLVED (125 clicks, step 254 total)**

Two crosses, two bars. Green bar reaches Cross A, cyan bar reaches Cross B. Purple walls FIXED with gap at r18-20.

**Dependency chain:** Cyan blocks blue → blue blocks green. Must retract cyan FIRST.

**Correct L5 sequence:**
1. Retract cyan fully (C4L x10) — unblocks blue
2. Move gray wall RIGHT past Cross B (C1L x2)
3. Shrink blue left edge (C1L x1) — unblocks green's rightward growth
4. Grow green RIGHT through purple gap (C3R x3) — green reaches c22
5. RETRACT green from gap (C3L x3) — green back to c10-11, freed from purple trap
6. Grow green DOWN at narrow c10-11 (C2R, alternating with C1L to shrink blue when it blocks)
7. Grow green RIGHT at cross row r36 (C3R x4) — green reaches Cross A
8. Grow cyan RIGHT to Cross B (C4R x5) — LAST step, triggers level-up

**Critical lesson: retract before rerouting.** Green went through the gap and got stuck (too wide to go down past purple below). C3L retracts the rightward extension. Then grow DOWN first (narrow), RIGHT second (at target row). Order of growth directions matters.

**What failed:**
- Growing cyan before clearing walls → blocked entire chain
- Growing green RIGHT through gap before DOWN → stuck, couldn't move down (purple below blocks wide cluster)
- Assumed C3L didn't work (was clicking wrong position or wrong state) → wasted 50+ clicks
- C1L controls blue AND gray (dual function) — needed for both wall clearing
- C3R and C3L both affect green AND blue — coupling requires alternating with C1L

**Card mapping verified:**
- C1R (12,56): gray LEFT + blue grows RIGHT
- C1L (6,56): gray RIGHT + blue SHRINKS left edge
- C2R (27,56): green DOWN + orange grows
- C2L (21,56): green UP
- C3R (42,56): green RIGHT + blue grows
- C3L (36,56): green RETRACTS right + blue shrinks
- C4R (57,56): cyan RIGHT (pure bar, no coupling)
- C4L (51,56): cyan SHRINKS right edge

## L6 — Rotation + Chain Structure (SOLVED, 52 clicks, step 211)

**Layout:** Purple U-maze (r27-41, c3-59) with gap at top-left (c9-17, r27-29). ONE cross at r33-35 c51-53 inside the U. Chain: green(ROOT) → yellow → blue. Green is horizontal bar, yellow small block, blue small block.

**Cards (L6):**
- Blue slider (c8-16): Blue-R (14,57) grow / Blue-L (10,57) shrink
- Yellow slider (c27-35): Yellow-R (33,57) grow / Yellow-L (29,57) shrink
- Green slider (c46-54): Green-R (52,57) grow / Green-L (48,57) shrink
- Blue+ (12,48): rotate blue 90°
- Yellow+ (31,48): rotate yellow 90°
- Green+ (50,48): rotate green 90°

**Growth directions depend on bar orientation AND rotation state.** Each rotation cycles through 4 directions (UP→LEFT→DOWN→RIGHT). R=grow outward from root, L=retract toward root.

**Critical mechanics:**
- Bars start with default orientations. Green is horizontal (grows LEFT/RIGHT). Yellow+blue are vertical initially (grow UP/DOWN).
- After rotating, R/L control growth in the NEW axis direction.
- Rotation cycles: each + click rotates 90°. May need 2 clicks to flip from UP→DOWN.
- **Shrink bars before rotating** — extended bars may collide and revert rotation.
- **Shrink all bars first** to compact the chain before repositioning.

**VERIFIED L6 sequence (52 clicks from fresh):**
1. **Shrink all:** Green-L(48,57) x3, Yellow-L(29,57) x2, Blue-L(10,57) x2 = 7 clicks
2. **Rotate green horizontal:** Green+(50,48) x1 = 1 click
3. **Shift chain LEFT to gap (c9-17):** Green-R(52,57) x7 = 7 clicks
   - Blue head moves from c42→c16 (above the gap)
4. **Rotate yellow to point DOWN:** Yellow+(31,48) x1 (UP→LEFT), Yellow-L(29,57) x3 retract, Yellow+(31,48) x1 (LEFT→DOWN) = 5 clicks
5. **Grow yellow DOWN through gap:** Yellow-R(33,57) x5 = 5 clicks
   - Blue head moves from r18→r33 (cross row, inside U)
6. **Rotate blue + grow RIGHT:** Blue+(12,48) x1, Blue-R(14,57) x3 = 4 clicks
   - Blue+ expands blue into horizontal block, Blue-R extends RIGHT to cross c51-53
   - ★ Level complete on Blue-R #3

Total: 7+1+7+5+5+4 = 29 optimal clicks (actual 52 due to exploration overhead)

**Key failures and lessons (cost ~120 wasted clicks across attempts):**
- Clicking controls without understanding orientation → wrong direction growth
- Yellow-R pushed UP when yellow pointed UP. Needed Yellow+ x2 to flip to DOWN.
- Blue-R grew DOWN when blue pointed DOWN. Needed Blue+ to rotate to RIGHT.
- Not shrinking before rotating → bars too extended, collisions reverted rotations
- Exploring 9 controls with batch clicks instead of single-click observation → wasted budget
- **"Assess, don't bash"** — always check bar orientation BEFORE deciding which control to use
- **Rotation cycling**: UP → LEFT → DOWN → RIGHT. Count clicks to reach desired direction.
- **The + button rotates, it doesn't just toggle.** Each click is 90° in one direction.

## L7 — SOLVED (9 clicks from fresh, 2026-04-11)

**Layout:** Vertical wall c39-41 r0-26, horizontal wall r27-29 with gaps at c6-8 and c30-32. Two crosses: A at (24,15), B at (21,6). Chain: white→gray→maroon→cyan→targetA. Orange→targetB (already at goal).

**Key insight:** Target B already at goal (21,6). Only target A needs to move from (54,15) to (24,15) — LEFT 30. Solution uses rotation to swing the chain like a crane boom, bypassing all barriers.

**VERIFIED 9-CLICK SOLUTION:**
```
CYN-R(32,58), WHT-R(10,51), WHT+(17,51), WHT+(17,51),
MRN-R(32,51), MRN-R(32,51), MRN-R(32,51), MRN-R(32,51),
MRN+(39,51)
```

**Step-by-step trace:**
1. CYN-R — Grow cyan LEFT: target (54,15)→(51,15)
2. WHT-R — Grow white UP: target UP to (51,12)
3. WHT+ — Rotate white: entire chain restructures
4. WHT+ — Rotate white again: chain at new geometry
5. MRN-R — Grow maroon UP: target (45,12)→(45,9)
6. MRN-R — Grow maroon UP: (45,9)→(45,6)
7. MRN-R — Grow maroon UP: (45,6)→(45,3)
8. MRN-R — Grow maroon UP: (45,3)→(45,0) [top of grid]
9. MRN+ — Rotate maroon: swings cyan+target from (45,0) to (24,15) — EXACT goal!

**Win condition met:** target A at (24,15), target B at (21,6). Both match goals.

**Why this works:** Growing maroon to the top of the grid, then MRN+ rotation acts like a pendulum — the sub-chain (maroon+cyan+target) swings 90° around maroon's pivot point. The rotation formula places the target precisely at (24,15). No routing through barriers needed.

**Contrast with failed approaches:**
- Previous attempts tried routing chain DOWN→LEFT→UP through barrier gaps: required 30+ clicks, stalled at barriers
- Direct GRY-L + CYN-R ratchet maxed at x=42 (barrier collision)
- The rotation trick bypasses ALL barriers by swinging OVER them

**Controls (verified from source):**
- WHT slider (2,49): white chain | WHT+ (17,51): rotate white
- MRN slider (24,49): maroon chain | MRN+ (39,51): rotate maroon
- ORG slider (52,49): orange chain (DON'T TOUCH — moves target B)
- GRY slider (2,56): gray chain | GRY+ (17,56): rotate gray
- CYN slider (24,56): cyan chain | AZU+ (60,56): rotate azure (isolated)

**L5 VERIFIED SOLUTION (43 clicks from fresh L5, step 159 total — 2026-04-10):**

Key insight: cyan's right edge LIMITS green's rightward extension through the purple gap. Green extends to match cyan's right edge. Retract cyan PARTIALLY (not fully!) to control how far green extends.

**Dependency chain:** off-white wall blocks green span → must walk wall RIGHT. C1L walks wall through blue. C3R also moves wall right. But need green through purple gap FIRST for C1L to work repeatedly.

**Exact sequence:**
1. C4L(51,56) x2 — partial cyan retract (c22-38 → c22-32). NOT x10!
2. C1L(6,56) x1 — wall right (c30→c33), blue shrinks (c33→c36)
3. C2R(27,56) x3 — green left cluster down to r18-20 (purple gap level)
4. C3R(42,56) x4 — green RIGHT through purple gap to c23
5. C1L(6,56) x6 — walk wall ALL THE WAY right (c33→c36→...→c51). Blue shrinks to 6px. This works because green is through the gap.
6. C3L(36,56) x3 — retract green to narrow (c10-14). Wall stays at c51!
7. C2R(27,56) x6 — green DOWN to r36-38 (cross row). Goes straight through!
8. C3R(42,56) x3 — green RIGHT to c22 at cross row. STOP at 3 (don't overshoot past cross!)
9. C4R(57,56) x2 — cyan grows RIGHT to Cross B (c36-38). Triggers level-up!

Total: 2+1+3+4+6+3+6+3+2 = 30 clicks (optimized from 43 with overshoot correction)

**Critical learnings:**
- Cyan right edge controls green's extension limit through the gap. Partial retract (x2) gives green enough room to reach c23 while keeping cyan useful.
- C1L walks wall through blue ONLY after green extends through the gap (changes game state)
- C3L retracts green but does NOT move the wall backward (unlike C3R which moves wall forward)
- Orange (c9-44) grows with every C2R as side effect — harmless unless it fills the purple gap. Keep C2R count minimal.
- Small fixed purple at c36-38 r36-38 blocks wall from ever passing c36 via C1L alone. But C1L+blue-shrink ratchets wall past it.
- Green can go DOWN from r18 to r36 at narrow width (c10-14) because: purple is only at c15-17 (green at c10-14 avoids it), and the off-white wall is far right (c51).

## L8 — Analysis (NOT SOLVED, 2026-04-11)

**Layout:** Target at (18,3), goal at (18,42). Need DOWN 39. Two wall sprites form barriers. Only S2-R moves target (grows cuykgjlznu DOWN). Same slider also grows dxgsplbcdi (sibling chain in rectangle area).

**Two horizontal blockers:**
1. **vgzxuhvxge** at (9,15,21,3) — blocks at y=15. Cleared by: WHT+x3, S3-R x3, S5-L x6
2. **kuvfhdmqbz** at (9,36,21,3) — blocks at y=36. Needs S4-R x3+ and S1-L x6

**The coupling problem:** S2-R grows BOTH cuyk AND dxgs. After different WHT rotations, dxgs grows in different directions and hits walls:
- WHT+x0: dxgs LEFT → wall at x=39 after 2 clicks
- WHT+x1: dxgs DOWN → safe (best for growth, ~13 S2-R possible)
- WHT+x2: dxgs RIGHT → wall at x=57 after 2 clicks
- WHT+x3: dxgs UP → wall at y=23 after 2 clicks

**The barrier-clearing capacities per WHT rotation:**
- S3-R (vgz clearing): WHT+x3 → 3 clicks. Others → 2 clicks.
- S4-R (kuv clearing): WHT+x2 → 5 clicks. Others → 2 clicks.

**Key constraint:** xipfwfleij (child of kuv, height 15) collides with wall at x=24-26,y=42-44 when moved LEFT to x=24. This limits S1-L to 1-2 effective shrinks unless xip is moved above y=27 (bottom at y=41 avoids wall at y=42).

**Best sequence found (A* solver, 25 clicks → y=36):**
```
S2R, S3R, S5L, W+, W+, W+, S3R, S5L, S5L, S3L, W+, W+,
S2R, S3L, S2R, S5L, S5L, S2R, S2R, S2R, S2R, S2R, S2R, S2R, S2R
```
Clears vgz barrier, reaches y=36, blocked by kuv.

**What's needed for full solve:** A clearing sequence that handles BOTH barriers before growing. The barriers need different WHT rotations (x3 for vgz, x2 for kuv), and transitioning between WHT states causes chain interaction issues. The A* search (30K+ states, depth 25+) could not find the kuv clearing mechanism from the y=36 state.

**Critical finding: kuv needs xip at y≤27 (bottom at y=41 avoids wall at y=42).** This requires S4-R x3 (kuv from y=36 to y=27). S4-R x3 needs: WHT+x2 (5 capacity) or TWO rounds: S4-R x2 at WHT+x3 + S4-R x2 at WHT+x0 (total UP 12, y=36→24).

**Failed approaches (2026-04-11):**
1. Clear both upfront (WHT+x2→kuv, WHT+x3→vgz): WHT transitions between cleared states cause collisions
2. Insert S4-R/S1-L into A* interleaving: disrupts the vgz clearing mechanism
3. Clear upfront + S2R/S2L ratchet: ratchet doesn't work, S2L undoes cuyk progress
4. Sequential clearing: clear vgz at x3, undo S3, cycle to x0 for S4-R, clear kuv → kuv cleared but vgz NOT cleared (S5-L broken by intermediate state changes)

**Best approach for interactive play:**
- Use the A* 25-click sequence to reach y=33
- From y=33: try combinations of S4-R, S1-L, W+, and S2-R to navigate past kuv
- Key: kuv at (9,36,21,3) needs right edge < 18 (width ≤ 8 = need 5+ S1-L effective)
- Each S1-L beyond width 18 causes xipfwfleij collision with wall at x=24-26, y=42-44
- Interactive observation may reveal timing/ordering invisible to automated search

**Budget:** L1-L7 uses ~220 clicks. Remaining ~388 for L8.

**Replay sequence to reach L7:**
L1: C4R(46,20)x7 + C2R(24,44)x6 = 13
L2: C1R(12,57)x8 + C2R(27,57)x8 + C3R(42,57)x4 + C4R(57,57)x6 = 26
L3: C4R(15,57)x8 + C1L(10,48)x6 + C6R(53,57)x7 + C3L(48,48)x5 + C2R(34,48)x12 + C5R(34,57)x8 = 46
L4: TR-R(57,48)x4 + TL-R(12,48)x3 + BR-R(57,57)x4 + TR-R(57,48)x1 + TL-R(12,48)x1 + BL-L(7,57)x7 + CTR-R(34,54)x7 = ~35
L5: ~30 clicks (optimized)
L6: ~29 clicks (optimized)
L7: CYN-R(32,58), WHT-R(10,51), WHT+(17,51)x2, MRN-R(32,51)x4, MRN+(39,51) = 9 clicks

## CRITICAL: step() vs perform_action() (2026-04-11)

**ALL solutions found with `game.step()` are INVALID for the live SDK.**

The SDK calls `game.perform_action()` which runs `step()` in a while loop until `is_action_complete()`. When a collision occurs:
- `step()`: saves rollback state, returns EARLY (before `complete_action()`). Win check runs externally and sees the collision state.
- `perform_action()`: detects action incomplete, calls `step()` again which ROLLS BACK, THEN completes. Win is never visible.

**Every level that reaches the goal WITH collision (target at goal but chain overlaps wall) passes `step()` but fails `perform_action()`.**

**L7 example:** MRN+ rotation lands target at (24,15) ✓ but maroon chain (width 18) overlaps wall at x=39-41 ✗. With `step()`: win=True. With `perform_action()`: rollback, win=False.

**Implication:** Solutions must achieve goal WITHOUT ANY collision in the final state. This is much harder — the A* needs collision-free paths, not just target-at-goal paths.

**A* progress with perform_action:**
- L4: dist=3 (y=12→y=9 blocked by wall coupling). 500K states.
- L6: dist not tested yet.
- L7: dist=6 at 65K states. Different approach from step() solution.
- All L1-L3 solutions work (no collision at goal).

**Solver approach needed:** Use `perform_action()` in A* solver. Solutions will be longer (chains must route AROUND obstacles instead of through them). Need more compute time (hours, not minutes).
