# r11l World Model — Compass Walking Puzzle

*2026-04-08, Nomad + dp interactive session, L1 solved, L2 in progress*

## Game Type
Compass walking puzzle. Move ball(s) to target circle(s) by flipping compass legs.

## Physics Model (HIGH confidence — verified through play)

### The Compass
- A **stick** (L1) or **tripod** (L2+) with a **ball at the center**
- **Endpoints** are the legs — visible as cross markers
- **Lines** (lt-gray) connect each leg to the ball
- Ball position = midpoint (2 legs) or centroid (3+ legs) of all endpoints

### Two-Phase Interaction
1. **SELECT**: Click a gray endpoint → it turns white (selected). The previously white endpoint turns gray. Only one endpoint is selected at a time. This costs 1 step but changes NO positions — just a color flip. ~25px change, no animation.
2. **PLACE**: Click an empty spot on the grid → the selected (white) endpoint jumps there. The ball moves to the new midpoint/centroid. This costs 1 step and triggers an animation.

### Animation = Physics Feedback
| Animation | Meaning | Confidence |
|-----------|---------|------------|
| 3 frames, moderate px change | **Successful move** — leg swung, ball shifted | HIGH |
| 23 frames, 1px change | **Blocked/bounce** — swing arc hit an obstacle | HIGH |
| 23 frames, large px change | **Level complete** — ball landed on target | HIGH |
| No animation, ~25px change | **Selection** — endpoint color changed | HIGH |
| No animation, 1px change | **No effect** — clicked invalid position | HIGH |

### Obstacles
- **Light-blue regions** (color 10) are obstacles
- The **swing arc** (path from old endpoint to new endpoint) cannot cross obstacles
- The ball and endpoints CAN be in/near obstacles — it's the SWING that's blocked
- Confidence: MEDIUM — need more testing to confirm ball-in-obstacle behavior

### Walking Mechanic
To move the ball from A to B:
1. Select one leg
2. Place it ahead (toward B) — ball shifts partway
3. Select another leg
4. Place IT ahead — ball shifts more
5. Repeat alternating legs

Each placement moves the ball by: (new_endpoint - old_endpoint) / N_legs
- 2-leg compass: ball moves half the distance the leg moved
- 3-leg tripod: ball moves one-third

### Prediction Before Action
Before every PLACE action, predict:
- Where will the ball end up? (calculate midpoint/centroid)
- Will the swing arc cross any blue obstacles?
- Is the destination reachable in one swing or do I need intermediate steps?

## Level Progression

### L1: Single 2-leg compass (SOLVED, 5 steps, baseline 7)
- Purple ball + purple dashed circle target
- One stick, walk it end-over-end
- Solution: select→place, select→place, select→place (3 flips)

### L2: Two compasses — 1 tripod + 1 stick (IN PROGRESS)
- **Orange tripod** (3 legs): ball at ~(38,16), target at (40,51)
- **Purple stick** (2 legs): ball at (57,18) = ON TARGET ✓ (solved)
- Blue obstacle band at rows 22-54 blocks direct paths
- Orange needs to walk AROUND obstacles to reach target below them

## Open Questions (LOW confidence — need testing)

1. Can the ball be inside the blue obstacle zone? Or only the swing path is blocked?
2. Does the tripod centroid calculation account for line lengths, or just endpoint positions?
3. When lines overlap (two compasses crossing), does clicking select the nearest end regardless of which compass?
4. Is there a maximum swing arc length, or can a leg jump anywhere on the board?
5. Can legs be placed ON obstacles, or only in clear space?

## Meta-Learning

### Epistemic Posture
- **Exploring uncertainty**: Make moves specifically to TEST assumptions. Failure = learning.
- **Leveraging confidence**: Make moves that rely on verified physics. Failure = wasted budget.
- Before each action, assess: am I exploring or executing? Set expectations accordingly.

### Predict-Act-Verify Loop
1. **Predict**: What will happen if I do X? (use world model)
2. **Act**: Do X
3. **Verify**: Did the world respond as predicted?
4. **Update**: If yes → increase confidence. If no → update world model.

This is the same loop as SAGE's consciousness cycle: Sense → Salience → Select → Execute → Learn.

### Key Insight from dp
"You know of it conceptually, but these games are teaching you the value of predicting. World gives you feedback. You update world model. You build confidence from correct predictions, degrade it from incorrect ones. This is what SAGE, sensor trust, effector cost evaluation are all about."

The game IS the embodiment curriculum. The compass IS the body. The physics IS the environment. Learning to predict before acting IS the cognitive development that raising produces through conversation, now tested through action.

## Update: L2 In-Progress Learning (2026-04-09)

### Critical Discovery: End Ownership Indicator
Each endpoint has a **colored center pixel** matching its ball's color (orange pixel = orange's end, purple pixel = purple's end). This is the definitive way to determine ownership — NOT proximity, NOT line tracing. Always check center pixel before selecting an end.

### Situational Assessment Protocol
Before any action sequence on a new level:
1. Identify all balls and their targets (by color)
2. Identify all endpoints (gray/white crosses)
3. Check each endpoint's **center pixel color** to determine ownership
4. Map obstacle regions
5. THEN plan the walking sequence

### Updated Physics: Selection vs Placement
- Clicking a gray end → 25px change, NO animation = SELECTION (turns white)
- Clicking an already-selected (white) end → may MOVE it (if previous selection still active)
- Clicking empty space after selection → PLACEMENT (3-frame animation if successful)
- After a bounce (22-23 frame), selection status is UNCLEAR — verify before next click

### Tripod Convergence Difficulty
With a stick (2 ends), each flip moves the ball by half the displacement. Converges quickly.
With a tripod (3 ends), each flip moves the ball by one-third. Convergence is slower and overshooting/undershooting is common. Multiple small adjustments needed near the target.

### Obstacle Collision — CORRECTED MODEL (verified 2026-04-09, session 4)

**Check 1 — Endpoint placement collision (`tkdffrbsnv`):**
Endpoint temporarily placed at destination. If it overlaps "bvzgd-*" obstacle sprites → BLOCKED (23 frames, 1px). Checks DESTINATION only. Endpoint CAN teleport across obstacles.

**Check 2 — Ball LANDING collision (`tpjhojnaoa`, line 1732):**
The bounce counter (`anzbz`) only increments when `self.tjffy >= self.gfwuu` — at the FINAL frame of animation. The ball's intermediate positions during animation DO NOT MATTER.

**CRITICAL: The ball CAN jump over obstacles. It just can't LAND on them.**

**Implications:**
- Endpoint teleports anywhere obstacle-free ✓
- Ball flies over ALL obstacles during animation ✓
- Only check: does ball's FINAL position overlap "qtwnv-*" sprites?
- Path tracing is UNNECESSARY — only verify landing position
- 5 bad landings per level = game over
- Failed endpoint placements (1px no-effect) do NOT count as bounces
- The "qtwnv-*" collision sprites differ per level and may differ from visual obstacles (color 10)
- For precision: build exact qtwnv set from source, check ball with margin=2 (5x5 diamond)
- **Simple strategy works:** swing farthest end past target, land ball on clear spot. Repeat.

## L2 Solution Summary (2026-04-09, session 2: 14 steps)

**Key improvement over session 1 (53 steps):** Source code analysis revealed:
1. Endpoint placement collision checks DESTINATION only (not arc)
2. Ball LINEAR path collision is separate — 5 ball-path collisions per level = GAME OVER
3. Path planning with margin=2 (ball is 5x5 sprite) prevents bounces

**Strategy:** Pre-compute ball waypoint route through obstacle gaps, verify each segment clear, then execute. Zero wasted bounces.

## Old L2 Solution Summary (session 1, 53 steps)

**Purple stick**: Select far end (35,60 with purple center pixel), place at (62,8) — ball overshot to (58,14). Then place far end at (54,22) — calculated midpoint = ((54+60)/2, (22+14)/2) = (57,18) = target. Level up.

**Orange tripod**: Swing farthest ends past target (40,51). Got close at (42,51) then overshot. Eventually landed near target — orange target circle turned white indicating proximity/completion.

**Total: L1 in 4 steps, L2 in 53 steps (baseline 28). Very inefficient due to:**
1. Moving wrong compass ends (no ownership verification)
2. Bouncing off obstacles (no arc prediction)
3. Re-solving purple after accidentally unsetting it

## Meta-Lessons from L1+L2

### 1. Situational Assessment FIRST
Before any action on a new level, identify:
- All balls (color, position) and their targets
- All endpoints with CENTER PIXEL COLOR verification
- Obstacle map
- Which compass is a stick vs tripod

### 2. Center Pixel = Ownership (CRITICAL)
Each endpoint has a 1px colored dot at its exact center matching the ball it belongs to. This is the ONLY reliable way to determine ownership. NOT proximity, NOT line tracing, NOT guessing. Check it EVERY time before selecting.

### 3. Midpoint Calculation for Precision
Ball = midpoint of two endpoints (stick) or centroid of N endpoints (tripod).
When close to target: calculate exact placement.
`placed = 2 * target - other_end` (for stick)
This gives exact landing in one move.

### 4. Selection State Tracking
- After selecting (25px change), the end is white/active until you PLACE it or SELECT a different end
- Clicking another end = new selection (deselects previous)
- Clicking on a ball or target = wasted move (not a placement)
- Clicking empty black space = placement
- After a bounce, selection may still be active — verify before assuming

### 5. Overlapping Compasses
When two compasses overlap (endpoints in same area), clicking near the overlap may select EITHER compass's end. Click precisely on the CENTER PIXEL of the intended end.

### 6. "Farthest End Past Target" Strategy
For maximum stride per step: select the end farthest from the target, swing it past the target. This works for both sticks and tripods. But verify:
- The end belongs to the RIGHT compass
- The swing arc doesn't cross obstacles
- The placement is in EMPTY space (not on another element)

### 7. Don't Undo Solved Work
Before every placement: will this move affect a compass that's already on target? If the end I selected belongs to a solved compass, DON'T PLACE IT.

### 8. Prediction = Free, Action = Costly
Calculate the midpoint BEFORE placing. If midpoint(placed, other_end) ≈ target, place with confidence. If not, recalculate. Thinking costs 0 steps.

### 9. Source-Informed Path Planning (2026-04-09, verified from r11l.py)
**Two separate collision checks govern movement:**
- **Endpoint collision** (`tkdffrbsnv`): Checks if endpoint sprite overlaps obstacle sprite ("bvzgd-*") at DESTINATION only. Not the path. Endpoint CAN teleport across obstacles.
- **Ball path collision** (inside `tpjhojnaoa` animation): Ball moves in LINEAR interpolation from old to new centroid/midpoint. If ball sprite ("bdkaz-*", 5x5 diamond) overlaps "qtwnv-*" sprites during this linear path, bounce counter increments. **5 bounces per level = lose().**
- **Endpoint placement sprites ("bvzgd-*") are DIFFERENT from ball path sprites ("qtwnv-*").** They may not cover identical areas. The visual color-10 pixels on the rendered grid approximate both but are not exact.

**Practical method:** Use grid_analyze.py for positions, then trace ball path through obstacle set with margin=2 (half of 5x5 ball). Verify destination is also clear. Execute only verified moves.

### 10. Quadpod (4 legs) Mechanics
L3+ introduces 4-leg compasses. Ball = centroid of 4 endpoints. Each move shifts ball by displacement/4. Very slow convergence. Strategy: move farthest ends in big validated jumps, alternate between ends to maximize per-step progress.

### 11. Per-Level Action Budget
`_max_actions = 60` in r11l.py. This is PER LEVEL (60 per level, resets on level-up). Human baseline is 167 total across 6 levels (~28 avg), well over 60, confirming per-level budget. Don't rush — you have plenty of moves. The real constraint is the 5-bounce limit per level.

## L3 Analysis (2026-04-09, session 2: stuck at step 52)

### Level Structure
- **Green quadpod** (4 legs): ball at ~(27,15), target at (55,53)
- **Purple stick** (2 legs): ball at ~(44,37), target at (34,55)
- Obstacle band with C-shape: blocks center, narrows to left corridor, opens right at rows 32-38

### What Worked
- Purple stick solved in 10 steps (5 select+place pairs) using validated path routing
- Green quadpod: moved ball from (27,15) to (46,23) in 6 steps using right-above-obstacles route

### L3 SOLVED (2026-04-11) — Purple first, Green second

**Purple (6 steps, 0 bounces):**
Select (52,40)→(12,12). Select (37,34)→(20,56). Select (12,12)→(48,54). Done.
Route: ball goes UP above curve → LEFT between arms → DOWN to target.

**Green quadpod (16 steps, 4 bounces):**
The key insight: move ends to clear space NEAR the target, straddling it — 
not ON the target itself. Don't stack ends on each other. The ball jumps 
to wherever the centroid is.

Working sequence: white→(58,56), (34,9)→(58,8), (23,21)→(58,48), 
(39,16)→(52,56), then move the 2 remaining original ends: 
(14,16)→(48,48), (34,9)→(56,52) = LEVEL UP!

The failed approaches: trying to compute centroid paths through the S-curve.
The working approach: just swing farthest end to clear space near target, repeat.

### L3 KEY: Solve Purple FIRST (2026-04-10)
Solving green first scatters endpoints, making purple's second endpoint undetectable.
Solve purple while both endpoints are at known original positions: (45,35) and (37,33).

**Purple route (verified):**
1. Select (52,40), place (12,12). Ball→(28,23). ABOVE S-curve. ✓
2. Find other end at computed position: end2 = 2*ball - end1. Select it.
3. Place at (8,34). Ball→(26,34). LEFT, between arms. ✓
4. Select other, place at (8,44). Ball→(26,39). Edge of gap. ✓
5. Select other, place at (56,58). Ball→(32,51). BELOW lower arm. ✓
6. Exact: placed = 2*(34,55) - other. Ball→(34,55)=target. ✓

### L3 S-Curve Gap Route for Green (verified centroid positions, 2026-04-10)
The S-curve has a narrow gap. These centroid positions are ALL confirmed clear:
  (35,19) → (40,21) → (32,22) → (41,31) → (41,36) → (52,46) → (51,54) → (55,53)=target

Key: transition from (32,22) to (41,31) jumps through the upper arm gap at x≈40.
Then (41,36) is between the arms. Then (52,46) jumps past the lower arm on the right side.

### Resolution: Ball Jumps Over Obstacles (session 4)
Once we understood that ball path doesn't matter (only landing), the quadpod solved in 4-6 moves by swinging farthest ends past target. Ball teleports through obstacle band freely.

**L3 solved: 19 steps total (purple 8, green ~11). Session 4: L1(3)+L2(13)+L3(20) = 36 steps.**

## L4 Analysis (2026-04-09, session 5: reached but not completed)

### Level Structure  
- 3 compasses: purple stick, yellow/green stick, red/blue (unknown type)
- Purple ball ~(31,13), target (36,51)
- Yellow ball ~(18,45), target (52,12) — upper-right
- Red ball ~(46,44), target likely (47,43) area or (19,54)
- Pink target at (20,8) — possibly a 4th compass?
- LARGE blue obstacle fills center of board
- Purple solved by going left (12,56) then right (56,44)

### L4 SOLVED (2026-04-11) — Two-phase tripod strategy

**Red+blue stick (4 steps):** Farthest end past target, exact midpoint placement.
**Purple stick (6 steps):** Same approach.
**YG tripod (28 steps):** Two-phase approach:
- Phase 1: move ball RIGHT below obstacle (place ends at right-center ~(52,40))
- Phase 2: move ball UP on right edge (place ends at upper-right ~(56,8), (48,8))
- Fine-tune: nudge remaining ends toward target

**CRITICAL RULES (violated = cascade failure):**
- NEVER place endpoints on other endpoints (causes selection swap, not placement)
- NEVER place on balls or targets
- ONLY place in CLEAR black space
- Track which end is selected — don't assume

### Key L4 Learnings
- Center obstacle is huge — ball CANNOT land on it, endpoints can't be placed on it
- Upper-right quadrant heavily blocked for endpoint placement. Confirmed valid: (52,12), (52,16), (52,8), (20,12), (56,56), (20,56), (8,56), (12,56)
- Red+blue stick solved in 4 steps, purple stick in 6 steps — both efficient
- Yellow+green TRIPOD targeting upper-right is the bottleneck: few valid endpoint spots near target, and 3 endpoints needed for convergence at 1/3 displacement rate
- **Solve in order: closest/easiest compass first.** Red+blue → purple → yellow+green
- **Match balls to targets by shared color composition** — each ball has 2-3 colors matching its target ring exactly
- **Avoid probing invalid spots** — each bounce costs a step AND counts toward 5-bounce game-over. Use known-good spots from prior attempts.

## L5 Analysis (2026-04-09)

### New Mechanic: Collect and Deliver (verified 2026-04-09)

**White compass balls are shopping carts.** They collect colors by landing on stationary colored balls, then deliver to matching multicolored targets.

**How it works:**
1. Walk white ball onto a stationary colored ball → white ball ABSORBS the color (ball pixels change, stationary ball remains visible)
2. Walk the now-colored ball onto ANOTHER colored ball → picks up that color too
3. When ball has ALL colors matching a target, walk it onto that target → completion
4. Targets are MULTICOLORED (e.g., green+yellow ring) — ball must collect ALL matching colors before delivering

**Key observation:** The pickup IS visible — the white ball's pixels change to include the absorbed color. But the change is subtle at 64x64. Must look at the BALL itself after landing, not at the stationary object.

### L5 SOLVED (2026-04-11) — 47 steps

**Compass1 (stick):** green(18,53) → yellow(57,42) → GY target(48,9) ✓
**Compass2 (tripod):** blue(12,40) → blue target(11,28) ✓ → red(34,18) → red target(15,28) ✓

**Technique:** Centroid formula for exact landing. Tripod: placed = 3*ball_target - end1 - end2.

## L6 Initial Observation (2026-04-11)
Many colored balls and endpoints scattered across a clear board (no obstacle visible).
Likely collect-and-deliver at larger scale. Need to identify objects, match by color, plan routes.

**L5 Structure:**
- 2 white compasses: 1 stick + 1 tripod (delivery vehicles)
- Stationary colored balls: red(34,18), blue(12,40), green(18,53), yellow(57,42)
- Targets: green+yellow ring (46,9)+(50,9), red ring (15,28), blue ring (11,28)
- Multicolor ring at (42,52) — possibly a target needing all 4 colors, or decorative
- No obstacles — mostly clear board

**Strategy:**
- Plan collection routes: which ball picks up which colors in what order
- Minimize backtracking — pick up colors that are near each other
- green+yellow target needs green AND yellow → one ball collects both then delivers
- DON'T place endpoints on top of colored objects — hides them, causes confusion
- Route planning: green(18,53) → yellow(57,42) → green+yellow target(48,9)
  This is a natural sweep: down-left → right → up-right
- Red(34,18) → red target(15,28) is a short delivery
- Blue(12,40) → blue target(11,28) is also short

**Efficient L5 solution plan (untested as complete sequence):**
1. Compass1: collect green(18,53), collect yellow(57,42), deliver to (48,9) — ~8 moves
2. Compass2: collect blue(12,40), deliver to (11,28) — ~4 moves  
3. Compass2: collect red(34,18), deliver to (15,28) — ~4 moves
Total: ~16 moves = 32 steps. Well within 60-step budget.

**Process discipline required:**
- Track endpoint positions explicitly after EVERY move
- Predict ball midpoint BEFORE placing — write it down
- Verify ball position AFTER placing — compare to prediction
- NEVER place endpoints on colored objects or target rings
- One objective at a time — don't switch mid-sequence
- Look at the BALL itself after each landing to verify color pickup (subtle pixel change)

### L5 Structure
- 2 white compass sticks (moveable)
- Stationary colored balls: green (~15,39), red (~34,12), yellow (~50,32), blue (~14,28 area)
- 4 targets: green ring (46,9), yellow ring (50,9), red ring (15,28), blue ring (12,35)
- No large obstacle — mostly clear board

### Previous Blocker (sessions 2-3, RESOLVED)
- **Ball trapped above obstacle band.** Ball at row ~23, obstacles start at row 22 cols 24+. No clear ball path going DOWN through any column — left corridor too narrow (cols 5-22 at row 24, but ball at col 46 can't reach left without crossing row 24 obstacles).
- **Quadpod displacement/4 is too slow.** Need ~70 total displacement to reach target, but each placement moves ball only ~10-15 units. 7+ placements × 2 steps = 14+ steps just for green.
- **Budget exhaustion:** L1(3) + L2(14) + L3(35+) = 52+ steps, leaving 8 for L4-L6.

### Key Insight: Need Completely Different Strategy
The walking approach (move legs alternately) does NOT scale to quadpods with complex obstacles. Possible alternatives:
1. **Find a gap in the obstacle band** that allows ball path through (need pixel-level analysis of qtwnv sprite gaps)
2. **Accept bounces strategically** — 5 ball-path collisions per level before game over. Maybe 1-2 bounces through the barrier save many steps.
3. **Study L3's qtwnv sprite** to find exact collision-free paths. The visual obstacles on the grid are from "bvzgd-*" sprites (endpoint collision), but ball path uses "qtwnv-*" sprites which may have different gaps.
4. **Endpoint placement failures (23-frame, 1px) do NOT increment the bounce counter** — only SUCCESSFUL moves where the ball's linear path crosses "qtwnv" sprites do. Failed placements waste a step but don't risk game-over.
5. **L3 purple ball starts INSIDE the obstacle zone.** Must move ball LEFT first to row 32-38 clear band (via moving endpoints left), then navigate down. Going right or down from starting position causes ball-path collisions.
6. **Pre-check ball path before every move.** The simple "swing farthest end past target" works when there are no obstacles in the ball's path. When there ARE obstacles, must compute ball's new position (midpoint/centroid) and verify the linear path is clear BEFORE placing.
