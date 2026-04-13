# dc22 L5 — SOLVED (2026-04-12)

## Status
L1-L5 cached and verified. 108-move solution in solutions.json.

## Solution Key Insights (corrections to prior analysis)

**b and d clicks are NOT strict mutexes.** Both sprites involved in each cycle
become INTANGIBLE (walkable) after the click — BUT the cycled variants have
different pixel patterns. wbze-efzv1 and vucz_1 use checkerboard `[-2,15,...]`
patterns that happen to be unwalkable at even coordinates (player always lands
on even coords due to 2-pixel steps). So effectively:

- Click b once: (26,34) opens, but (10,38) becomes checkerboard (unwalkable at even x).
- Click b TWICE: both back to initial, i.e. (26,34) blocks, (10,38) walkable.
- Click d once (requires zbhi(10,18) walked first): p-2 opens (26..29,46..53), but vucz becomes checkerboard.
- Click d TWICE: vucz back to walkable, p blocks again.

The trick is to click b/d in between walking phases so the player traverses
regions that need DIFFERENT toggle states — **traverse half the path, toggle,
traverse the other half**.

## The Winning Plan (108 moves)

1. Click b (jpug-jbyz): opens wbze1 at (26,34). Player can now walk from (32,34)
   to kbqq(26,30). Note: breaks (10,38) temporarily.
2. Walk to kbqq(26,30).
3. Crane sequence: u\u00d73 r\u00d73 (to 3,3), grab (at 3,3), l\u00d73 d\u00d73 r\u00d73
   (to 3,0) \u2014 U-shape navigation; x=0 column for vertical motion only. Object now
   at (20, 22..33), bridge spans (22..25, 22..33) connecting kbqq(26,30)\u2194bridge\u2194kbqq(26,20).
4. Walk onto bridge, up to kbqq(26,20) (via (25,22..23)\u2194(26,22..23)).
5. Crane moves to (3,3): l\u00d73 u\u00d73 r\u00d73. Object now at (20, 10..21), bridge
   spans (22..25, 10..21) connecting kbqq(26,20)\u2194bridge\u2194kbqq(22,6).
6. Walk to itki1 (24,6) via kbqq(22,6).
7. Click c (jpug-bjuk): teleport from itki1(24,6) to itki2(10,34).
8. Crane to (0,0): l\u00d73 d\u00d73. Object at (8, 22..33), bridge covers (10..13, 22..33).
   Now x=10..13 column kbqq(10,18)\u2194bridge\u2194kbqq(10,34) connected.
9. **Click b again**: restores wbze2 at (10,38) to walkable state. Player now
   has continuous walk from (10,18) to (10,45) (kbqq + wbze2 + kbqq + bridge).
10. Walk to zbhi(10,18): activates jpug-adnw (d-click becomes usable).
11. Click d: opens p-2 at (26..29, 46..53) as walkable. vucz becomes
    checkerboard (unwalkable).
12. Click e \u00d74 (vckz-jpug): cycles vckz through 8 variants to vckz-5 (fully
    solid at (14..29, 44..45)).
13. Click f \u00d74 (sprite-6): cycles qgdz-1 to qgdz-5 (solid at (22..27, 54..55)).
14. Walk: (10,18) \u2192 column down to (13,45) \u2192 (14,45) vckz-5 \u2192 (26..29, 45)
    \u2192 p-2 (26..29, 46..53) \u2192 (26..27, 54..55) qgdz-5.
15. **Click d again**: p goes back to blocking, vucz back to walkable. Player
    on qgdz-5 at (26, 54) unaffected.
16. Walk left along qgdz-5 (22..27, 54..55), up to (22..23, 52..53) vucz_2,
    left through vucz_2 to (14..15, 50..53), left via (13, 50..53) kbqq to
    (10, 50) = goal.

## Verified Mechanics

- **Crane U-shape (non-hhxv mode)**: x\u2208{0..3} y\u2208{0,3} OR x=0 y\u2208{0..3}.
  10 positions forming a U. Vertical motion only at x=0.
- **Grab requires anchor alignment**: bhbhmgxpud() checks crane anchor \u2261
  object center. For L5 setup, grab only succeeds at logical (3,3).
- **Click cycles find existing pre-cloned variants** (from oavrxgtjnl) at the
  same position. Tags inherited from source sprite, so the cycled clone's
  gigzqgcfncq tag is preserved, making it INTANGIBLE rather than TANGIBLE.
  THIS is why the previous analysis was wrong about "mutex" \u2014 both end up
  INTANGIBLE. The walkability difference comes from pixel patterns.
- **Support (uxwpppoljm)** checks only top-left player pixel at (x,y). Player
  x,y always even (2-pixel step motion). Checkerboard pattern with -2 at
  (even,even) is therefore not walkable.
- **Collision (collides_with)**: skipped entirely when sprite.is_collidable
  returns False, which it does for INTANGIBLE sprites. So player can move
  through INTANGIBLE sprites freely, independent of pixels.

## Solver Extensions That Helped

- `dc22_L5_solve.py`: handcrafted execution. Bypasses BFS. Direct replay works
  because all state transitions are deterministic.
- Previous macro BFS (`solve_macro`) could NOT find this in 20 minutes / 30k
  nodes / depth 20 because:
  - Walk-to-stable only walks to kbqq cells, never bridge cells. Bridge
    (the crane object) is tagged bynyvtuepbt-object, not kbqq. Player can
    stand on it via floodfill but macro won't PARK there.
  - Even if it did, the dedup by board_key means many equivalent states
    collapse, but the REQUIRED sequence (16+ clicks + walks + more clicks +
    walks + more clicks + walks) exceeds depth budget.
  - The "b-click twice" insight is non-obvious and BFS has no reason to
    prefer it.

## L6 Status (Handoff Notes for Next Session)

Same script runs on L6 via cached L5 replay (see dc22_L6_probe.py for init state).

**L6 state**:
- Player at (28,52), goal bqxa-ppew at (46,6).
- Steps budget: 1024.
- Crane: **hhxvnxhz-1** (hhxv mode, `uzungcfexgf=True`) at (22,30). Free x/y motion.
  - hhxv-dmxj1 already placed at (0,24) 20x20 — massive pre-placed bridge.
- Initial reach: 18 cells (18..29, 48..53) via itki + kbqq-1 pads.
- **4 Pressure plates** at (32..37, 56..61), tagged a/b/e/h:
  - sprite_81 (e) (32,58); sprite_81-1 (b) (34,56); sprite_81-2 (a) (36,58); sprite_81-4 (h) (34,60)
- **4 crane-direction buttons**: nxhz-ghqmfnmmgrz-1 (a/right), nxhz-zmjbupyjfyb-1 (b/down),
  nxhz-vbdduyutyiw-1 (e/left), nxhz-vbdduyutyiw-2 (h/up-alias-jffakyxiury).
  All **INVISIBLE initially**. Activated only while player stands on matching-letter plate.
  See `mbszrqqnqm()` at line 2313: sets visible+INTANGIBLE if plate overlapped.
- Other clicks:
  - jpug-bjuk (c): itki color cycle. itki variants: itkiupry, itkibgeg, itkizfrq, itkijbyz.
  - nxhz-bynyvtuepbt-1 (g): grab — activated by zbhi-jpug-bgeg-1 at (34,48).
  - gkrr-jpug (d): ? (activated by zbhi-jpug-adnw-1 at (6,18))
  - sprite-6 (f): qgdz cycle.
- Multiple itkis with tag 'c': itkizfrq2(4,4), itkiupry1(18,48), itkiupry2(32,52), itkijbyz2(34,58).
- itkiupry1 has tag 'd' (itki-color-cycle candidate).

**Likely solution structure** (requires verification):
1. Teleport via c-click while on itkiupry1 (reach) to itkiupry2 at (32,52).
2. Walk to kbqq-1(32,48) covering (32..37, 48..53), then down to (32..37, 54..61)?
   Note: qgdz at y=54..61 but shapes are mutex (need f-cycle to extend).
3. Get onto pressure plates by walking to (34, 56..60) area.
4. While on plate, click matching crane-direction button to move the hhxv crane
   towards kbqq(32..49, 4..11) top-right cluster.
5. Grab hhxv bridge via g-click (need zbhi-jpug-bgeg at (34,48) triggered first).
6. Place hhxv segments to bridge from mid-bottom area to top-right goal area.
7. Walk to goal (46,6) which is jpug-tagged (clicking it may be a step too? or just walk-into).

**What the existing solver lacks for L6**:
- `solve_macro` has no walk-to-pressure-plate transition. It walks only to kbqq,
  zbhi, itki+teleport. Plate-gated clicks will always be no-ops in BFS as written.
- Needs: "walk to plate P, click each visible crane button, then walk off plate"
  as a single macro transition.
- Also needs hhxv grab/place mechanics support (the existing crane transitions
  in solve_macro assume U-shape crane, but L6 uses free-motion hhxv crane).

**Recommended next-session approach**:
1. Add walk-to-plate transition to solve_macro.
2. Study hhxv crane action handlers (lines 2812-2870) — the grab logic for
   hhxv attaches by finding hhxv near crane anchor via `fnonlfqqca()`.
3. Handcraft an L6 solve plan similar to dc22_L5_solve.py once the mechanics
   are verified on a smaller test.
4. Given L6 is the final level, alternative: brute-force teleport + pressure
   plate BFS with much deeper search (if L1-L5 cached, only L6 is searched).

---
# ORIGINAL FINDINGS (superseded but preserved for history)



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
