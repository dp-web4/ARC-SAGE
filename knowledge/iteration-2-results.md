# Iteration 2 Results — 84.9% → ~89.2% Projected

**Date**: 2026-04-13
**Baseline**: scorecard `c0d62617`, 84.9%
**Projected after iteration 2**: ~89.2% (computed from local dry-run replays + RHAE-squared scoring + per-game baselines)
**Delta**: +4.3pp

## What Changed

### sb26: 16.67% → ~100% (+3.3pp scorecard)
**Largest single win.** A frame-questioning agent decoded the L4+ paradigm shift the prior solver had misidentified. Old solver assumed 1:1 palette-to-slot mapping and tried 120 permutations for "7 targets in 5 slots". Actual mechanic: the game uses a stack-based evaluator — when it hits a portal, it pushes a sub-frame onto the evaluation stack; portal-reachable frames contribute their own slots to the overall sequence. The "5 slots" was wrong; sub-frames provide more.

The fix simulates the engine's evaluator in Python and DFS-searches palette assignments. At each empty slot the required color is fixed (current target in the sequence), so branching is narrow: place a regular token of that color, or place a portal whose sub-frame walk produces the required suffix.

Result: 8/8 levels in 124 actions (baseline 153). Every level scores 100% under RHAE-squared.

Also revealed: the `sb26_solutions.json` claim of "L6+ SWAP mechanic paradigm shift" was a misread — the interaction model is uniform across all 8 levels, just the structural pattern (single hierarchy vs. multi-group, etc.) varies. The portal-routing evaluator handles them all.

### bp35: 13.06% → ~32.7% (+0.8pp scorecard)
A second agent continued the viewport-aware rewrite started earlier today. L7 went from 155 to 35 actions (78% reduction). L8 went from 422 to 87 actions (79% reduction). Total trace: 321 actions across 9/9 local levels, down from 304 with 28 OOB to 321 with only 2 OOB.

The 2 remaining OOB clicks are at L5 and L7, both documented as **structurally** OOB — the relevant G-blocks are sealed behind spike barriers with no viewport-reachable alternative path. Live submission will:
- L1-L4: clean, 4 levels at 100%
- L5: 6 actions before 400 → 0% on L5 (incomplete)
- L6-L9: 0%

Notable methodological move: on L8, the agent discovered that 6 of the original 11 gravity-flip G-blocks sit at x=0 on the left wall — never on the player's path. These are functionally interchangeable with the y=1 G-blocks the original solver used (each G-click flips gravity AND removes the block). Substituting cleared most OOB issues by routing through in-viewport blocks.

### lf52: 0% → ~5.5% (+0.2pp scorecard)
Captured a 6/10 partial trace (L1-L6, 317 actions all under per-level baselines). However, the lf52 solver also generates OOB clicks — 4 of them in L3 — so live submission will 400 there. Effective score: only L1-L2 register on the live scorecard.

The full lf52 fix (viewport-aware click reasoning matching what bp35's agent did) is a future iteration.

### Other findings (no scorecard impact)
- **cn04 L6**: client-server version drift confirmed. Local `environment_files/cn04/65d47d14/cn04.py` defines 5 levels, server expects 6, only cn04 has this drift. Cannot be fixed without re-developing L6 against ONLINE mode.
- **lf52 L7/L10**: 8th convergent frame-questioning pass (this one with the viewport reframe) confirmed structurally unsolvable. The viewport primitive applies to lf52 (off-viewport clicks reach off-screen pegs) but doesn't unlock L7 because the binding constraint is the tile-jump movement graph, not interface access. This refines the substrate primitive's scope: it requires both (a) target out-of-viewport AND (b) selecting it enables a state transition.

## What Was Documented

Three places now carry the "world model ≠ interface model" insight, with the lf52 refinement:

1. `knowledge/cross-game-patterns.md` — "Viewport ≠ World" pattern with diagnostic method, scope refinement
2. `paper/draft.md` §5.4 — "What we didn't derive until forced to" subsection, two-layer cartridge schema
3. `paper/phase2-substrate-cartridges.md` — standalone Phase 2 design note with 7 substrate primitive candidates, scope brackets, falsification criteria
4. `knowledge/game-mechanics/lf52.md` — session 8 notes appended
5. `knowledge/game-mechanics/bp35.md` — viewport-constraint section + structural-OOB notes

## What Remains for Iteration 3

Tier 1 (highest ROI):
- **lf52 viewport-aware solver patch** — same pattern bp35 got. Recovers L3-L6 instead of stopping at L2. Estimated +1.3pp scorecard.
- **bp35 L5 / L7 deeper investigation** — agent flagged structural; another frame-questioning pass might find alternate paths. Estimated +1-2pp if either unlocks.

Tier 2 (per-game solver work):
- **cn04 L6 live development** — requires playing live to access L6, building a solver against the new mechanic. ~+1.5pp.
- **r11l L4 trim** (44/20 → 22) — solver heuristic improvement. ~+1.6pp.
- **ar25 L2/L5 trim** — solver work. ~+1pp.
- **sp80 L3 trim** — solver work. ~+0.5pp.

Tier 3 (long shot):
- **dc22 L6** — multi-pass convergence on structurally stuck. Very low probability of unlock.
- **lf52 L7/L10** — 8 convergent passes; same.

If we hit Tier 1 + 2 in iteration 3: ~93%.

## Submission Decision

Three options for the user:
- **Submit now** at projected 89.2%. Safe, reliable, beats prior baseline by 4.3pp.
- **Wait one more iteration** to fix lf52 viewport (estimated 1-2 days), submit at ~91%.
- **Wait longer** for tier 2 work to land, submit at ~93%.

The 89.2% submission is one-shot — once posted, it overwrites our public scorecard. Subsequent submissions are not "appended"; each is a fresh scorecard. Multiple submissions to the leaderboard yaml are supported (RGB-Agent listed 3) so we can show progress over iterations.

## Files Touched This Session

- `arc-agi-3/experiments/bp35_solve.py` (L7/L8 viewport rewrite by agent)
- `arc-agi-3/experiments/sb26_solve.py` (full rewrite to evaluator-simulation DFS by agent)
- `arc-agi-3/experiments/lf52_partial_capture.py` (new — captures L1-L6 + solutions.json)
- `arc-agi-3/experiments/arc_session_writer.py` (repo-relative VM path)
- `arc-agi-3/experiments/submit_competition.py` + `regen_all_visuals.py` (already done previously)
- `knowledge/visual-memory/{bp35, sb26, lf52}/run_*` (fresh runs)
- `knowledge/visual-memory/lf52/solutions.json` (new cache)
- `knowledge/cross-game-patterns.md` (Viewport ≠ World section + scope refinement)
- `knowledge/game-mechanics/{bp35, lf52, sb26}.md` (per-game updates by agents)
- `knowledge/iteration-2-findings.md` (mid-session snapshot)
- `knowledge/iteration-2-results.md` (this file)
- `paper/draft.md` (§5.4 added with scope refinement)
- `paper/phase2-substrate-cartridges.md` (new design note)

## Commits

```
b7f0168 sb26: solve all 8 levels via evaluator-simulation DFS (124 actions)
da2db6e bp35: viewport-aware L7/L8 rewrites — 22 OOB clicks fixed
c9c9715 lf52: partial capture L1-L6 (0% → projected 38% on lf52)
4038230 paper+docs: refine viewport primitive scope from lf52 session 8
5111fbf iter2: findings doc + cn04 re-download (version drift confirmed)
85f29f6 lf52: session 8 — viewport reframe (bp35 pattern) doesn't help L7
ecaf349 paper+docs: viewport-as-interaction-constraint, two-layer cartridge schema
50e3493 bp35: viewport-aware click_act + L3/L4 rewrites (4 OOB clicks fixed)
```
