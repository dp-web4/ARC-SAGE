# DC22 L6 Findings (2026-04-12)

## Status: UNSOLVED — analysis inconclusive

dc22 remains at 5/6. Macro solver exhausts at 624 board-configuration states without finding goal. Problem is not "solver needs more power" — problem is that **within my understanding of the L6 mechanics, the goal is not reachable from the initial state at all**. Either my model is wrong in a subtle way, or L6 requires a transition that no current probe is exposing.

## Level layout

- **Player** starts at (28, 52) in a narrow horizontal corridor y=48..52 x=18..28 (18 reachable cells).
- **Goal** (bqxa-ppew) at (46, 6), inside a walkable "top-right" island y=4..10 x=32..48 with a small gap at x=40 that only opens at y=6 and y=10 (the wall has -1 pixels in a narrow band).
- **Step budget**: 1024 (generous).
- **Crane** (hhxvnxhz-1) at (22, 30), uzungcfexgf=True → "free-motion" mode (bounded by `bg` path tiles in region x=8..31 y=8..36).
- **hhxv-dmxj1** at (0, 24), a 20x20 wbze sprite with a horizontal beam (c=0) or vertical beam (c=1) pattern. Its tag `c` means clicking jpug-bjuk cycles its variant.
- **4 pressure plates** (sprite_81*) arranged in a cross at (32,58), (34,56), (36,58), (34,60) — all inside a 3x3 "plate cross island" supported by kbqq-efzv-1 at (32,56), entirely disconnected from the player's corridor.
- **4 direction buttons** (nxhz-*-1) in a cross at (45,35), (49,31), (49,39), (53,35), all with `visible=False, collidable=False` → start as REMOVED. Turned INTANGIBLE only when player stands on the matching pressure plate (via `mbszrqqnqm`).
- **Grab button** (nxhz-bynyvtuepbt-1) at (47,17), tagged `jpug+g+bynyvtuepbt`, starts REMOVED.
- **Color-cycle button** (gkrr-jpug) at (49,46), tagged `jpug+d+itki-color-jpug`, starts REMOVED.
- **Two zbhi trigger tiles**: zbhi-jpug-adnw-1 at (6,18) letter d (resurrects gkrr-jpug), zbhi-jpug-bgeg-1 at (34,48) letter g (resurrects grab button).
- **Two always-visible jpug click targets**: `jpug-bjuk` (c) at (45,23) and `sprite-6` (f) at (53,5).

## Mechanics summary

### Click handlers
- **Click jpug-bjuk (letter c)** when player is on itkiupry1 or itkiupry2 → player teleports to the matching other-variant pair (the pair is: itkiupry1@(18,48) ↔ itkiupry2@(32,52)) — this IS how player enters the plate-top island. Then cycles all c-tagged wbze variants (swaps hhxv-dmxj1↔dmxj2, itkiupry1↔2, itkijbyz1↔2, itkizfrq1↔2). Period: 2.
- **Click sprite-6 (letter f)** cycles qgdz-efzv-1/2/3/4/5/6 variants (a staircase at x=6..21 y=54..58). Period: 6. Does not affect the plate-cross region at all (qgdz is at x=6..21 only).
- Direction buttons and grab button all have no effect because they are invisible/REMOVED unless specifically resurrected (by stepping on a matching zbhi tile — unreachable from start).

### Teleport chain
The only way to leave the starting corridor is the c-click teleport on itkiupry1@(18,48) ↔ itkiupry2@(32,52). This oscillates between those two 9/18-cell islands.

### Pressure plate gating
Direction buttons (a/b/e/h) remain INVISIBLE whenever player is not standing on the matching plate. Clicks on their coordinates are no-ops. Crane can only be moved via clicks on visible direction buttons. So crane cannot be moved until player reaches a plate.

### Plate reachability (the crux)
Plate cross (y=56..60 x=32..36) is disconnected from plate-top (y=48..52 x=32..36) by a 2-pixel vertical gap at y=54..55 (between kbqq-efzv-1 at (32,48) y=48..53 and kbqq-efzv-1 at (32,56) y=56..61). Nothing in L6 fills this gap under any c/f cycle state. I verified with a full board walkability scan across all 12 (c,f) combos (see dc22_L6_probe11.py, probe19.py).

### Goal reachability
Goal island (y=4..10 x=32..48) is disconnected from everything else under all verified board states. The only sprite large enough to bridge it is hhxv-dmxj (20x20), which is fixed at (0,24) and can only be moved by the crane — which requires plate access — which requires the gap bridge — which requires hhxv-dmxj to move. Circular dependency.

## What I verified

- Clicking ANY grid cell (x,y in 0..63) from initial state produces only 1 unique state change class (probe20.py). Clicking c (jpug-bjuk) or f (sprite-6) is the only effective click; both leave player fixed at (28,52) with reach=18.
- c-teleport: walking to (18,48) and clicking c teleports player to (32,52), reach=9 cells in plate-top island. Subsequent c-clicks oscillate back to (18,48).
- From (32,52), walking to (34,48) (zbhi-g) activates grab button (nxhz-bynyvtuepbt-1 → INTANGIBLE). But clicking grab button is a no-op because `fnonlfqqca()` requires the crane anchor (26,34) to match an hhxv sprite center — hhxv-dmxj1 center is (10,34). Mismatch, no grab.
- Full solve_macro BFS explores 624 board configurations and fails. All 8 jpug click targets are tried in every state, including invisible direction buttons (whose clicks silently fail). All walkable zbhi and itki cells are tried as macro destinations.

## Evidence that L6 is structurally stuck (not just a solver weakness)

The solve_macro's state space is genuinely exhausted — the queue drains naturally, not by timeout, and the set of 624 visited boards covers all accessible (player_pos, sprite_state) tuples under the transitions {click any jpug target, walk to zbhi, walk to itki + click jpug for letter}. Goal cell (46,6) is never in any reach-computation's output across all 624 states.

## Hypotheses I could not rule out

1. **Hidden mechanic in the click handler**: I walked through engine lines 2705-2931 multiple times. The only actions a click can produce are: teleport (itki at player pos), variant cycle (wbze tagged), color cycle (gkrr-jpug via fnhzudfjhd), crane move (direction buttons, plate-gated), crane grab (bynyvtuepbt handler, fnonlfqqca), and jpug zbhi-resurrect (via zbhi step handler at 2917, not click handler). None of these produce a reach expansion that gets player to a plate.
2. **Off-by-one in player support**: I checked with `uxwpppoljm` directly for every (x,y) in the gap region and confirmed no support at y=54 between x=28..38.
3. **Side effect in walking over an itki that I missed**: the move handler at 2913 only fires on zbhi tiles, not itki. Walking onto an itki does nothing except check for zbhi overlap. Confirmed by reading the `bwxffbswqz` call at line 2913 which explicitly filters `"zbhi"`.
4. **A subtler crane grab condition**: `fnonlfqqca` iterates `kelxnkuznz` which returns wbze sprites with `qmxenejanqe[base] == 2` AND name starting with "hhxv". Only hhxv-dmxj matches. And its center is (10,34), never at crane anchor (26,34) without moving something. Unless I run `xcrifaqaiy` (save checkpoint) which doesn't move anything — that's just a state snapshot for undo.
5. **The wall could be walk-through somewhere I missed**: qeqe-bg-1 has a pixel gap at rows 4..11 cols 0..9 → abs y=4..11 x=40..49. This IS the pass-through near the goal. But it's unreachable from player without getting y=4..11 walkable somewhere between x=14..32 first, and nothing does that.

## What the previous agent's handoff said

> L6 needs handcrafted plan like L5 with new macro transitions. Plain A* gets stuck at best_h=46.

The "best_h=46" ≈ matches reaching (32,52) where manhattan to (46,6) is 14+46=60. Or (34,48) where it's 12+42=54. Or maybe they reached some better state I haven't. The best_h number suggests the solver got to **somewhere closer than initial** but could not connect to goal.

## What should be tried next

1. **Re-verify with a completely different solver**: a truly brute-force BFS that doesn't prune by board_key at all (or uses a stricter key including ALL sprites) to check if the pruning is dropping a state.
2. **Re-read `fnonlfqqca` and the crane grab condition again with a debugger**: maybe the wbze selection I'm seeing differs from what the engine sees at runtime.
3. **Check if there's a level 6 entry-time mutation beyond line 2025-2030**. I only found one (`itki-color-cycle` tag added to itkiupry1@18,48). There might be more that I missed in a helper.
4. **Visual inspection**: reopen L6_start.png side-by-side with the support map and see if there's something visually obvious I'm dismissing textually.
5. **Look at the dc22 SOURCE for L6 FIRST, not by symbolic analysis**: dump the on_set_level hook at runtime, trace what runs, see if something non-obvious executes during init.

## Artifacts

- `arc-agi-3/experiments/dc22_L6_probe.py` through `dc22_L6_probe21.py` — 22 probes documenting the analysis
- `arc-agi-3/experiments/dc22_L6_solve.py` — solve_macro runner for L6 only
- `shared-context/arc-agi-3/visual-memory/dc22/L6_start.png` — initial frame
- `shared-context/arc-agi-3/visual-memory/dc22/L6_after_teleport.png` — after first c-teleport
- `shared-context/arc-agi-3/visual-memory/dc22/L6_after_grab.png` — after attempting grab

## Productive failure

This investigation rules out: the naive click-combinations hypothesis, the "click at invisible button coord" hypothesis, the "grab without crane move" hypothesis, the "color cycle unlocks everything" hypothesis. It narrows the search: whatever L6's solution is, it either uses a mechanic that isn't the standard click/walk action space, OR there's a specific sequence of existing actions that produces a reach expansion I haven't observed in 624 macro states.

Given the time spent, the honest path forward is: (a) leave dc22 at 5/6 and move on, OR (b) have a fresh agent approach L6 with zero context from this session to see if a different mental model finds something I missed.

---

## Second agent pass (2026-04-12, fresh frame-questioning session)

**Confirmed previous findings and added one refinement.**

### What was re-verified
- Cycling c-click swaps `hhxv-dmxj1 ↔ hhxv-dmxj2` (horizontal ↔ vertical beam), swaps itkiupry1↔2, itkijbyz1↔2, itkizfrq1↔2. Engine creates ghost REMOVED variants at init (line 2080-2109) which explains how cycling reinstantiates the cycled sprite at the same position. Clicking c from corridor (not on itki) cycles variants without teleporting.
- `ozbgzuaoya` (click hit-test) filters INVISIBLE + not-is-visible + REMOVED. So invisible jpug buttons (direction buttons, gkrr-jpug, grab button) are unreachable via clicks until resurrected by a zbhi step-trigger.
- zbhi-jpug-adnw-1 at (6,18) is the only thing that can resurrect gkrr-jpug (d-gate). (6,18) is unreachable from all known board states.
- `fnonlfqqca` requires exact crane-anchor-center = hhxv-center match. Anchor is (26,34) initially, hhxv-dmxj1 center is (10,34). Crane cannot move without plate → no match ever reached.
- `fnhzudfjhd` (color cycle via itki-color-jpug) only fires when you CLICK a jpug with `itki-color-jpug` tag. Only gkrr-jpug has that tag — and it starts REMOVED.
- bqxa-ppew at (46,6) has `jpug` tag but no single-letter tag, so clicking it is a harmless no-op (costs 1 step).
- All 6 f-click phases produce valid board states. Macro solver's 624-state exhaustion is reproducible.

### Refinement the previous pass didn't document
**4-5 consecutive f-clicks expand player reach from 18 → 29-30 cells**, opening a staircase region at y=54..58, x=6..20. Previous findings said qgdz "doesn't affect plate-cross region" — true, and the staircase is structurally disconnected from both the plate-cross (y=56..60 x=32..36) and the plate-top (y=48..52 x=32..36). The expanded reach at y=58 maxes out around x=14; the plate cross starts at x=32. The 14→32 gap contains only yellow wall (wbze, tangible) under all f-cycle states.

### Macro solver incompleteness noted but not exploited
`solve_macro`'s "stable walk" transition (line 491-505) filters to `name.startswith('kbqq')` for support sprites. After f-cycle, the new walkable cells are qgdz-supported, not kbqq-supported — so the solver never positions the player on those cells as a distinct branching state. This is a real gap but doesn't matter for correctness: clicks that only toggle variants (no teleport, no zbhi step-handler) are player-position-independent, and the only position-dependent mechanic (teleport via c-click on itki) is already covered by transition C.

### Final framing
The deadlock is structural: crane needs plate, plate needs crane, no third mechanic breaks it. The f-click reach expansion is a distractor — the extra cells are all disconnected from the plate region and from any resurrection trigger.

**dc22 at 5/6 stands.** Two independent agent passes, starting from different frames, converged on the same conclusion with no refutation of the structural-stuck hypothesis. This matches the lf52 L7 pattern: multi-agent frame-questioning converges when the puzzle is genuinely unreachable within the modeled mechanic set.

Consistent with the fleet-wide insight that "verifying the work inside the frame scales linearly with agent count; only questioning the frame closes investigations." Both frame-questions (crane mobility, reach expansion) closed with no new mechanism found. Further agent passes are unlikely to yield progress without engine-source modifications or a human-played reference trajectory.

### Artifacts from this pass
- `arc-agi-3/experiments/dc22_L6_frame.py` — enumerates all sys_click/jpug sprites and their states
- `arc-agi-3/experiments/dc22_L6_trace.py` — traces c-click state diff (proves cycling swaps variants including hhxv-dmxj orientation)
- `arc-agi-3/experiments/dc22_L6_walkmap.py` — full 64x64 walkability scan; shows all disconnected regions
- `arc-agi-3/experiments/dc22_L6_explore.py` — walks each bottom-staircase cell to confirm no hidden mechanic
- `arc-agi-3/experiments/dc22_L6_solve_only.py` — re-ran solve_macro to confirm 624-state exhaustion is reproducible
