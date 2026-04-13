# Iteration 2 Findings — Raising the Scorecard Above 90%

**Date**: 2026-04-13
**Baseline**: scorecard `c0d62617`, 84.9% overall
**Target**: >90% realistically, 95% aspirational

## Executive Summary

Today's investigation produced three concrete mechanical findings, two asynchronous agent efforts in progress, and a clearer understanding of why some games won't move without substantial solver work.

## Mechanical Findings

### 1. bp35 viewport-aware rewrite (partial)

**Prior state**: 13.06% — API 400 on first OOB click of scorecard L4.
**Work done**: rewrote `click_act` in `bp35_solve.py` to capture OOB clicks for diagnosis; rewrote L3 and L4 sequences to use "walk-trigger-fall-then-click-in-viewport" pattern; camera mechanics documented in-source.
**Current state**: 4 of 28 OOB clicks eliminated (L3, L4 clean). L5=1, L7=7, L8=16 remain.
**Commits**: `50e3493`, `dc96ea4` (solver + fresh run.json).
**Remaining**: agent in progress on L7/L8; L5 has structural limitation documented.

### 2. cn04 L6 — version drift, not solver work

**Finding**: Local `environment_files/cn04/65d47d14/cn04.py` defines 5 levels; `metadata.json` baseline_actions has 6 entries; live server scorecard reports `level_count: 6`. The SDK `fd.win_levels` reads from local source (5), so our solver thinks the game ends at L5. Live server expects us to play L6.

**Scope of drift**: cn04 is the only game with this mismatch. Audit confirmed all other 24 games have baseline_actions count matching `Level(...)` declarations in source.

**Implication**: cn04 L6 cannot be solved from cached data. Would require either (a) ARC-AGI-3 SDK to sync the updated cn04.py source, or (b) developing the L6 solver live against ONLINE mode. Not low-hanging fruit.

**Cost of leaving it**: 28.57% on cn04 (currently scoring 71.43% at 5/6 levels because L6=0). Can't be fixed without live play.

### 3. Efficiency trims on near-100% games are game-logic-deep

Scanned sub-100% levels across r11l, ar25, sp80, sc25, sk48, g50t for mechanical trim opportunities (duplicate consecutive actions, wasted round-trips). Consecutive-duplicate counts were high (>100) for most games but **duplicates are not waste** in ARC-AGI-3 — directional actions move one cell per press, so 10 consecutive RIGHTs means moving 10 cells right. Legitimate.

Examined sp80 L3 (27/17, 39.6% score) directly. Its sequence includes a round-trip: 5 RIGHTs followed much later by 10 LEFTs. Could look like waste, but the click between them depended on the character being at the intermediate position. The 10 LEFTs weren't undoing the 5 RIGHTs; they continued past the start to reach a different click position. Game-logic constraints, not mechanical inefficiency.

**Implication**: per-level trimming requires per-game understanding of the world model to find a genuinely shorter solution path. Not achievable in a one-week iteration without investing solver-development hours per game.

**Where trims are viable**: g50t L6 (49/48, cut 1) and L7 (69/67, cut 2). Small gains. Pushes g50t from 97.71% to 100% (~0.1pp on overall scorecard). Worth doing if we're already in the code.

## In-Progress Agent Work

### 4. bp35 L7/L8 OOB cleanup

Background agent continuing the viewport-aware rewrite on the remaining 23 OOB clicks in L7 (7) and L8 (16). Task: apply the same walk-trigger-fall pattern used on L3/L4 to interleave movement into the pre-click setup phases that currently batch OOB clicks. Expected outcome: bp35 recovers to ~70-95% on scorecard if the rewrite is clean, depending on action-count efficiency.

### 5. lf52 viewport-reframe probe

Background agent investigating whether the viewport insight from bp35 applies to lf52 L7/L10 (previously declared structurally unsolvable by 7 convergent frame-questioning passes). Specific question: does lf52's ACTION6 click handler add camera offset to incoming y (the bp35 pattern), making previously-unreachable world positions clickable via OOB viewport coords?

Predicted outcome: unlikely to unlock lf52 because lf52's constraint is in the tile-jump graph (which ACTION1-4 produce), not in click-based interaction. But worth one convergent-pass probe for the paper either way.

## Scorecard Forecast

| Scenario | Score | Notes |
|---|---|---|
| Current baseline | 84.9% | `c0d62617` |
| + bp35 full rewrite (all 28 OOB → 0) | ~88-90% | if agent completes L7/L8 |
| + g50t L6/L7 trim | ~88-90% | ~0.1pp gain |
| + lf52 partial (if viewport unlocks) | ~90-92% | speculative |
| + cn04 L6 (requires live dev) | ~86% (recover 28% on cn04) | not this iteration |
| + r11l/ar25/sp80 solver trims | ~91-94% | hours per game |
| + sb26 L4+ mechanic decode | ~88-92% | uncertain, frame-questioning agent needed |
| **Realistic 1-week iteration** | **~91-93%** | bp35 fix + 1-2 small trims |
| **Aspirational with deep work** | **95%+** | solver rewrites on 3+ games |

## Meta-Lesson for the Paper

The iteration today strengthens the paper's §5.4 claim: **world models do not automatically contain interface primitives**. bp35's failure was diagnostic of exactly the gap the Phase 2 cartridge architecture is designed to fill. The cn04 version drift is a separate lesson — reproducibility depends on the environment source matching the evaluation server, which isn't always guaranteed. For Phase 2, the cartridge retrieval system should probably include version tracking for world models, not just retrieval by visual similarity.

## Files Touched This Session

- `arc-agi-3/experiments/bp35_solve.py` (partial rewrite)
- `knowledge/visual-memory/bp35/run_20260413_104041/` (fresh run)
- `paper/draft.md` (§5.4 new subsection)
- `paper/phase2-substrate-cartridges.md` (new file)
- `knowledge/cross-game-patterns.md` (Viewport ≠ World section)
- `knowledge/iteration-2-findings.md` (this file)
- `environment_files/cn04/` (re-downloaded, still 5 levels; drift confirmed)
