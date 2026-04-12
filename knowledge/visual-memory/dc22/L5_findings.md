# dc22 L5 — Productive Failure Notes (2026-04-12)

## Status
L1-L4 cached and verified. L5 UNSOLVED after extensive mechanical analysis.

## What works in the solver
- `player_reachable_cells(game)` — pure-position floodfill using direct sprite manipulation. Does NOT call `env.step`, so safe to call many times. Verified correct against real movement.
- Macro BFS over click sequences (`solve_macro` in dc22_solve_final.py). Transitions: pure clicks, walk-to-zbhi, walk-to-itki+click-letter (teleport), walk-to-stable-kbqq (park for crane moves).
- Handcrafted partial L5 execution confirms mechanics: crane move→object bridge→park→crane move→walk-up→itki teleport→zbhi unlock→'d' jpug toggle all execute correctly.

## L5 geometry (after L1-L4 replayed)
- Player starts at (32,34). Goal at (10,50).
- Single bynyvtuepbt-object `sprite-10` (6x12) attached-only to crane. Non-hhxv mode — crane follows U-shape path, 10 positions only, object center lands at {(11,16),(11,20),(11,24),(11,28),(15,16),(15,28),(19,16),(19,28),(23,16),(23,28)}. Object y-range is thus always ∈ {10..21} or {22..33} — NEVER reaches y≥34.
- No hhxv bridge segments. No pressure plates (`vfuxmgtevge` empty).
- itki pair: (24,6) and (10,34), tag 'c'. jpug-bjuk is the 'c' button. Teleport works between them when player stands on an itki and clicks the letter jpug.
- zbhi-jpug-adnw at (10,18) unlocks jpug-adnw (initially REMOVED) when player walks onto it.
- 'e' group (vckz) at (14..29, 44..45): 8 variants with different pixel shapes. vckz-1 is all -2 (phantom — collision blocker but NOT support). vckz-5 (full cycle) is solid 16-wide.
- 'f' group (qgdz) at (14..29, 54..55): 6 variants, each is a 6-wide slab at different x offsets.
- 'b' toggles wbze-efzv1 at (26,34) and wbze-efzv2 at (10,38) between TANGIBLE and INTANGIBLE (both have `gigzqgcfncq` tag → intangible after flip). Extends usable floor.
- **'d' toggle is the critical trade-off**: swaps wbze-efzv_vucz_{1,2} at (14..23, 50..53) AND wbze-efzv-p-{1,2} at (26..29, 46..53).
  - d NOT toggled: vucz_2 is SOLID intangible (floor) at (14..23, 50..53); p-1 is TANGIBLE checkerboard (blocking).
  - d TOGGLED: vucz_1 is CHECKERBOARD intangible at (14..23, 50..53) — **unwalkable** because pixel check at even (x,y) always lands on pattern-0; p-2 is SOLID intangible at (26..29, 46..53).

## The blocker
Goal kbqq(10,50) can only be entered from adjacent cells: (14,50) via vucz_2 (needs d NOT toggled), (12,48) via nothing, (10,48) via nothing, (14,52) via vucz_2, etc.

- With d NOT toggled: vucz_2 solid, so (14,50..53) is reachable IF we can enter that region. But the only entrances to (14..23, 50..53) are from (14,54..55) qgdz OR from (14..23, 48..49) which has no floor ever. And qgdz at y=54..55 has no approach from above either (y=52 is inside vucz, but getting TO y=52 from anywhere requires already being on vucz).
- With d TOGGLED: vucz_1 is unwalkable, p-2 is walkable at (26..29, 46..53) reachable from (26..29, 44..45) vckz-5. But then player is stuck at x=26..29 — no bridge from x=26 to x=14 at y=46..53.

Neither single toggle state connects player-reach area to goal. The 'd' toggle is strictly either/or.

## Hypotheses for unexplored mechanics
1. **Odd-parity player positions**: the itki teleport could put player at an odd coordinate if the other itki sprite is at odd coords. Both are (10,34) and (24,6) — even. Not it.
2. **Shape-aware support check**: I verified `uxwpppoljm` only checks top-left pixel of player at (x,y). This is confirmed in the game source (line 2455-2463). So checkerboard IS unwalkable.
3. **Sprite-10 orientation**: it's 6x12. What if we're supposed to use it as a wider-than-expected bridge at y=22..33 AND the path goes *sideways* rather than down? Already exhausted.
4. **Crane position I missed**: Maybe the crane has more positions I don't know about. The `ogwbggfvor` check limits uzungcfexgf=False to x in {0..3} at y∈{0,3} and y in {0..3} at x=0. That's 10 positions. I enumerated them all.
5. **Multi-object**: Only one `bynyvtuepbt-object`. Confirmed.
6. **Falling into checkpoint**: falling restores the last checkpoint (before last click). Doesn't create new positions.
7. **Step counter shrink mechanic**: L5 has 512 steps budget. Plenty for any reasonable solution.
8. **The 'c' teleport also swaps itki NAMES**: after 'c' toggle, the itki at (10,34) becomes itki1 (was itki2). This could change which jpug-letter-tag triggers teleport next click. But both stay 'c' tagged. Hmm — wait, let me check whether after cycling, the itki tag changes. Actually no — `ulgmrcjxz` uses `dzpheqwbxaj` which is set once. And letter tag is in `tags` list which is copied. tag swap doesn't happen.
9. **wbze itki cycling via itki-color-jpug**: needs the `itki-color-jpug` / `itki-color-cycle` tags, which our L5 itkis don't have.

## Partial solution path (verified up to step 11)
Handcrafted sequence that reaches player at (10,18) after d-toggle with reach=20 (locked to x=10..13 column):
```
# Setup floors
e×4, b×1  (vckz→solid, wbze-efzv2→floor at 10,38)
# Grab object and create bridge to kbqq(26,20)
up×3, right×3, click bynyvtuepbt   (pickup at crane 3,3)
left×3, down×3, right×3             (move to 3,0, obj at 20,22..33)
# Park player on stable kbqq
walk (32,34)→(28,20)
# Move crane up to expose vertical path
left×3, up×3, right×3               (back to 3,3, obj at 20,10..21)
# Climb to itki1
walk (28,20)→(24,6)
# Teleport to (10,34)
click jpug-bjuk (c)
# Bring bridge near x=10 column
left×3, down×3                      (crane to 0,0, obj at 8,22..33)
# Walk to zbhi, triggers jpug-adnw reveal
walk (10,34)→(10,18)
# Toggle 'd'
click jpug-adnw (d)
```
After this: player at (10,18), reach set is just (10..13, 18..37) because the x=10 column is now continuous but (10..13, 42..45) kbqq is disconnected from (10..13, 38..41) wbze? Actually both should be connected via walking. Need to verify — last trace showed 20 cells ending at (12,36), missing (10..13, 42..45) somehow. BUG possibility in the walking state.

## Handoff
Next agent should:
1. Re-run the handcrafted sequence, verify actual reach after d-toggle
2. Check the sprite `merged-sprite` at (38,-2) 2x66 and `qeqe-bg` at (38,0) 32x64 which are TANGIBLE — these might be the "right panel" decoration but could potentially block parts I haven't mapped
3. Consider that maybe I misread mask pixel value `-2` handling — it IS collidable (bwxffbswqz returns it) but NOT supportive (uxwpppoljm filters `<0`). Double-check by having player step onto a -2 position and verify they're treated as supported or not.
4. Carefully look at whether the 'c' teleport also triggers a side-effect that changes *which itki is on floor* — maybe after teleport, the itki2 at (24,6) swaps in, and a different kbqq becomes reachable.

## Artifacts
- Solver: `arc-agi-3/experiments/dc22_solve_final.py` — has the macro BFS with working reachability floodfill
- Cached L1-L4 solutions: `shared-context/arc-agi-3/visual-memory/dc22/solutions.json`
- Visual memory: `L1_solved.png`, ..., `L4_solved.png`, `L5_start.png`
