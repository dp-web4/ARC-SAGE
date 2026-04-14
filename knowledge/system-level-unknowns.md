# System-Level Unknowns

*Parked for after game-level questions are exhausted.*

## 1. Client-server version drift

**Observation**: `cn04-65d47d14` is the only game where local `environment_files/<game>/<version>/cn04.py` disagrees with the live evaluation server. Local says 5 levels; server says 6. The `metadata.json` baseline_actions list was updated to 6 entries at some point without the game source being refreshed.

**Unknowns**:
- What triggered the server-side addition of cn04 L6?
- Is this a pattern (game designers add levels without bumping version suffix) or a one-off?
- How do we detect future drift before it bites a submission?

**Would resolve by**: mirroring scorecard results against local dry-run deltas after each submission. Any game where scorecard `level_count > local win_levels` is drift.

## 2. Full action-budget accounting rules

**Resolved (2026-04-13)**: budget is per-level, resets on level transition, consumed by all actions including failed moves (confirmed visually via the in-game progress bar).

**Still unknown**: does RESET action consume from the per-level budget? Does UNDO refund consumed budget for the last action only, or for several? In competition mode where UNDO isn't available, do we ever need to know?

## 3. Multi-agent convergence reliability

**Updated claim (2026-04-13)**: N-pass convergence over a **shared action-space model** is necessary but not sufficient for "structurally unsolvable" to be true. bp35 L7 was declared structural by one pass; a second pass solved it via a game-state-modifying primitive (E-spread staircase) the first pass had overlooked. The first pass's action-space model was incomplete.

**Revised framing**: structural verdicts carry two dimensions.
- *n* — number of independent frame-questioning passes converging on the same verdict
- *m* — number of distinct action-space models those passes reasoned within

bp35 L7 (before re-investigation): n=1, m=1. Weak evidence → refuted.
bp35 L5 (after re-investigation): n=2, m=2. Moderate evidence.
lf52 L7 (session 9): n=8, m=2 (jump-graph + viewport-augmented). Stronger evidence.
dc22 L6: n=7, m=1 (all passes within crane action-space). Should probe an alternative model.

**Remaining unknowns**:
- Do Opus-4.6-based agents share systematic blind spots that come from training distribution?
- Is the convergence pattern robust to swapping models (Sonnet, Gemini, GPT-5)?
- How do we guarantee a new pass reasons within a *different* action-space model rather than silently sharing the previous one?
- Are there specific action-space primitives (like E-spread) that agents tend to overlook unless explicitly prompted about them?

**Would resolve by**: (a) getting human solves on disputed structurally-stuck levels. If someone solves lf52 L7, our convergence verdict is refuted and we learn something about the blind spot. (b) Systematically swapping the prompting to force each new pass to enumerate and reason within each primitive the game-engine source exposes — not just the ones the prior solver used.

### Partial resolution (2026-04-13, dc22 session 8)

The source-enumeration protocol was formalized and executed against dc22 L6. Agent enumerated all 16 engine primitives from ACTION handler source, cross-referenced against solver transition set, and confirmed no missed primitive exists. Converts (n=7, m=1) to (n=8, m=2) and provides positive proof of action-space completeness.

Also surfaced: **engine architectural properties determine susceptibility to bp35-style refutation**. dc22 filters invisible/removed sprites before click dispatch (hit-test filtering); bp35 does not. Convergence verdicts on hit-test-filtered games are harder to refute than on permissive-hit-test games. This should be an explicit check when assessing a structural claim: does the engine filter click targets at the hit-test layer?

## 4. Gemma failure-mode taxonomy (see `knowledge/phase2-plan.md` Tier 1.1 for current plan)

**Prior observation**: Gemma 3 12B scored 0 on every game attempted under a context-only harness. Unknown which subsystem broke.

**Deployment target is Gemma 4**, not Gemma 3. The Gemma 3 baseline stands as evidence that context-only prompting is insufficient, but per-variant failure-mode taxonomy will be re-run against Gemma 4 (e4b primary, e2b on small machines, 26b-a4b on Thor for scale reference). Do not assume Gemma 3 failures translate directly to Gemma 4.

**Candidates**:
- **Perception**: can't reliably parse 64×64 grids into object descriptions
- **Reasoning**: parses correctly but gets lost in the space of plausible next actions
- **Context management**: loses track of prior observations over multi-action sequences
- **Action emission**: knows the answer but produces malformed output the harness can't parse
- **Domain knowledge**: lacks priors for "this sprite is a wall, that sprite is a player" category judgments

**Would resolve by**: instrumenting the autonomous harness with per-stage logging and running Gemma 4 e4b on one easy game (cd82 — 73-action solve) under three conditions: no-context baseline, cartridge simulation (pre-built world model in context), action-demonstration. Observe at which stage behavior diverges from what the harness expected. Phase 2 cartridge shape depends on the answer. Full protocol in `knowledge/phase2-plan.md` Tier 1.1.

## 5. Visual-signature retrieval fidelity

**Claim** (Phase 2 plan): a game frame can retrieve the correct world-model cartridge from the bundle via visual similarity.

**Unknowns**:
- Do similar-looking games (e.g. r11l and tu93, both with small colorful entities on a blank field) produce confusable signatures?
- Do distinct levels of the same game (e.g. cd82 L1 vs L6, visually different layouts) retrieve the same cartridge?
- What happens when NO cartridge matches closely — does retrieval degrade gracefully or fail?

**Would resolve by**: building a preliminary cartridge bundle from 5 games, running grid-vision retrieval on held-out frames from each, measuring confusion matrix.

## 6. Substrate primitive coverage

**Current list** (7): viewport-aware click, action budget, animation timing, click classification, undo semantics, structural vs positional win, directional type.

**Unknown**: are there more? The bp35 finding was incidental — we stumbled on the viewport primitive via a competition-mode failure, not by deliberate enumeration. There may be 5 more primitives waiting for us to hit their specific failure mode.

**Would resolve by**: running a private-set environment through the Phase 2 harness and cataloging every "our solver does X but real mechanic is Y" gap as a potential new primitive.

## 7. Kaggle sandbox resource budget

**Unknown**: does Gemma 4 e4b (deployment target) + cartridge bundle + game-step inference loop fit in 32GB VRAM alongside game state and perception? Does the full 8-hour time budget cover the public+semi-private+private environments at our target pace? The 26b-a4b variant (Thor-only) is aspirational and needs a quant not yet available for Kaggle.

**Would resolve by**: running a local simulation of the Kaggle sandbox with memory constraints and timing one full evaluation run on the 25 public games.

## 8. Private-set generalization

**Unknown**: our world models don't transfer. The Phase 2 cartridge-retrieval claim is that it will — or that it'll at least let the small model adapt faster than building from scratch. We have no evidence for this yet.

**Would resolve by**: playing the semi-private set (if accessible) with the Phase 2 harness. Compare action efficiency vs human baselines on games our cartridge bundle was NOT trained on.

## 9. Action-efficiency theoretical minimum

**Unknown**: for games where we score 100% (beat human baseline), is there a shorter solution path than ours? The baseline is the 2nd-best human, not a proven lower bound.

**Would resolve by**: exhaustive search over the solver's action space for each "100%" game, finding the true minimum. Interesting for the paper but not score-relevant.

## Priority for after game-level work is done

1. (4) Gemma failure-mode taxonomy — cheap to probe, highest Phase 2 leverage
2. (5) Visual retrieval fidelity — directly tests a Phase 2 design assumption
3. (3) Convergence reliability — epistemic check on our methodology
4. (8) Private-set generalization — the competition-critical unknown, but requires Phase 2 artifacts to exist
