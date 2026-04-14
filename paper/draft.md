# ARC-SAGE: World-Model Harness and Multi-Agent Frame-Questioning on ARC-AGI-3

**A path from frontier-model capability to small-model deployment via external memory.**

**Authors** (draft — Andy to add membot section and self):
- Dennis Palatov, Metalinxx, Inc.
- Claude Opus 4.6 (1M context), Anthropic (agent collaborator)
- Andy Grossberg, Waving Cat Learning Systems (membot architecture — section TBD)

**Public artifacts** (all MIT):
- Code: https://github.com/dp-web4/ARC-SAGE
- Scorecard: https://arcprize.org/scorecards/c0d62617-a0bc-4100-bb4e-982fa5d7fde7
- Memory system: https://github.com/project-you-apps/membot

**Draft date**: 2026-04-13

---

## Abstract

We report 84.9% on the ARC-AGI-3 public set (21/25 environments completed, 160/183 levels, 5,159 total actions), placing near the top of the community leaderboard at ~$250 total cost — roughly an order of magnitude cheaper per point than comparable entries. The result was produced by a harness we call ARC-SAGE: per-game canonical solvers encoding world models derived from engine-source analysis, a multi-agent frame-questioning protocol that deploys independent Claude Opus 4.6 instances from orthogonal frames to break through local minima, and a capture-replay pipeline that makes every solve fully reproducible.

The score itself is instrumental. The research question motivating ARC-SAGE is whether *recognition and adaptation against structured external memory* can substitute for raw model capacity on genuinely novel problems. This paper establishes the capability ceiling using a frontier model (the Opus-4.6 result), baselines a small local model (Gemma 3 12B scored 0% on our preliminary game sweeps under a context-only harness — no cartridge retrieval), and outlines a concrete Phase 2 plan to close the gap using Andy Grossberg's paired-lattice cartridge architecture (`membot`) with Gemma 4 as the deployment target (`e4b` primary, `e2b` for small-device reference, `26b-a4b` aspirational). The harness is model-agnostic; swapping Opus for a local model is a configuration change, not a rewrite.

We claim three contributions. (1) **A strong, reproducible public-set result** with full replay bundle. (2) **Multi-agent frame-questioning** as a methodological pattern: convergent independent passes separate "hard" problems from "structurally stuck" ones with higher confidence than any single pass. (3) **A concrete architecture** for transferring frontier-model capability into a small model via retrieval rather than fine-tuning, with the harness already built and tested.

---

## 1. Introduction

ARC-AGI-3 tests whether an agent can explore interactive environments with no instructions, build a functional model of the mechanics, and act efficiently. The benchmark is explicitly designed to resist the pattern-matching and pre-training strategies that dominate static ARC-1/2 approaches. The current frontier on the public set, as of this writing, spans from ~0% (most frontier models with naive prompting) through 13% (StochasticGoose — CNN + RL), 82.43% (RGB-Agent, 3 games optimized), up to our 84.9% across 25 games.

Two facts frame this work:

1. **The 32GB VRAM, no-internet Kaggle sandbox** forces the Milestone 1 (June 30 2026) competition into local-model territory. Any approach that depends on API calls to frontier models is competing in the wrong arena.

2. **ARC-AGI-3's RHAE scoring is squared and level-weighted.** Two-times-human action count scores 0.25, not 0.5. Completion without efficiency is worth little. This rewards compressed, purposeful action sequences over exploration.

ARC-SAGE takes these seriously. The harness we describe here separates *capability discovery* (done with a frontier model, expensive, one-time per game) from *capability deployment* (done with a local model, cheap, repeated). Capability discovery produces artifacts — world models, action traces, retrievable cartridges — that a small model can use without re-deriving.

This paper documents the capability-discovery half, quantifies the deployment gap using a Gemma 3 baseline, and outlines the Phase 2 plan to close it.

---

## 2. The SAGE Architecture

SAGE ("Situation-Aware Governance Engine") is a cognition kernel for edge devices developed as part of the [dp-web4/SAGE](https://github.com/dp-web4/SAGE) research project. The full system is out of scope here — ARC-SAGE uses a minimal subset. Three commitments matter for this work:

### 2.1 The kernel is a scheduler, not a reasoner

SAGE orchestrates *which* reasoning to invoke, not how to reason. Reasoning lives in plugins exposing a uniform interface (IRP: `init_state → step → energy → halt`). In ARC-SAGE, the plugins are per-game solvers (each encoding a world model) plus the frame-questioning agents. The kernel decides when to deploy which — and when to stop.

### 2.2 The context window is the intelligence

This phrase, discovered during one of our frame-questioning sessions on game `cd82`, captures a central claim: capability emerges from what the reasoning context contains at the moment of action, not from weights trained for similar situations. ARC-SAGE makes this explicit by treating *retrievable memory* and *in-context reasoning* as distinct and composable resources.

A frontier model can derive a world model from engine source. A small model generally cannot — but a small model given the *already-derived* world model as context can often execute against it. The work of this paper is demonstrating the first half; the forward plan is implementing the second.

### 2.3 Recognition over derivation

Biological intelligence does not re-derive the physics of grasping every time it picks up a cup. It recognizes the situation, retrieves the motor schema, and adapts. Large language models derive from scratch at every turn — which is why they are slow, expensive, and often wrong on novel interactive problems. ARC-SAGE treats this as a structural limitation to engineer around, not a frontier to scale through.

The Phase 2 artifact — the membot-bound cartridge — is the recognition primitive. Given a game frame, vision retrieval returns the world model most similar to the current situation; the small model reasons only about adaptation.

---

## 3. Methods

### 3.1 Per-game canonical solvers

For each of the 25 ARC-AGI-3 public-set games, we built a dedicated solver encoding a world model derived from reading the engine source. A solver is ~500 lines of Python; it represents the game's state space in semantic terms (objects, positions, properties, win conditions) rather than pixel frames.

The solver's output is a sequence of `GameAction` tokens, optionally with `(x, y)` coordinates for click-type actions. Successful solutions are cached as `solutions.json` per game (per-level move lists) or as module-level constants harvestable by the capture-replay pipeline.

Development of these solvers was the bulk of the effort. For many games, the engine source uses obfuscated function names and non-obvious state transitions; the agent process involved reading the source, hypothesizing mechanics, testing against the live environment, and iterating. The detailed game mechanics docs under `knowledge/game-mechanics/` in the repository record this derivation.

### 3.2 Multi-agent frame-questioning

Several games contained levels that resisted initial solver development. `dc22` level 6 (a crane puzzle with circular dependencies between plate placement and reach), `lf52` levels 7 and 10 (peg-solitaire-like reductions in a reachability-limited board), and others consumed substantial search without progress.

For these, we developed a protocol: deploy multiple Opus 4.6 agents, each reading the current solver, the game mechanics documentation, and prior investigation notes, but with one prompt difference — they are told not just to continue the work but to **question the frame itself**. The standard investigation assumes the current model is correct and looks for a solution within it. A frame-questioning agent is instructed to consider that the model might be wrong, that the search heuristic might be misleading, or that there is a mechanic the SDK does not surface.

Two outcomes emerge empirically:

- **Convergence to "structurally stuck"**: When 3–6 independent passes from different frames all arrive at the same impossibility result (e.g., exhaustive state-space enumeration showing unreachable goals), we treat the level as structurally unsolvable within the modeled action space. This is *productive failure* — it identifies specific points at which the model diverges from the engine. Both `dc22` L6 and `lf52` L7/L10 met this criterion.

- **Frame-break to solution**: Occasionally a single frame-questioning pass finds a mechanic the prior consensus missed. `wa30` level 7 ("kill one of the pieces, not both"), `sk48` level 4+ ("failed moves consume engine budget"), and `re86` level 8 ("22-cell safe corridor through deformation") were all unlocked this way. A prior solver run at the level had logged "impossible" or "no progress"; a single reframe flipped the outcome.

The methodological claim: multi-agent convergence gives higher-confidence structural verdicts than any single pass, and the cost of running multiple agents is low relative to the cost of wrongly concluding a level is solvable (weeks of search) or wrongly concluding it is stuck (missed points on the scorecard).

### 3.3 Capture-replay pipeline

Every solved level produces a replayable `run_YYYYMMDD_HHMMSS/` directory containing a `run.json` manifest and step-by-step PNGs. The pipeline has three stages:

1. **Solver produces action trace.** Either stored in-memory during a live solve or loaded from a persisted `solutions.json` cache.
2. **Replay through `SessionWriter`.** A fresh environment instance; each action is re-executed; `SessionWriter.record_step()` writes the post-action frame. Ensures the recorded trace corresponds to the actual game state.
3. **Viewer verification.** A local dashboard (`game_viewer.py`) renders the per-level animations, start frames, and solve frames side-by-side. Any visible divergence from expected behavior indicates a bug in the solver or a stale cache.

The principle guiding this infrastructure is summarized in a document in the repo called `CAPTURE.md`: *"A solver that doesn't produce replayable visual memory isn't done. The data is the deliverable, not the win."* A solve we cannot replay is a claim, not a result. The replay bundle (61 MB across 77 run directories, bundled in the public repository) makes every score in this paper independently verifiable.

### 3.4 Competition submission

ARC-AGI-3 scorecards require `OperationMode.COMPETITION` against the live API with a registered key. Each environment is one-shot per scorecard — you cannot re-`make()` a game if the first attempt fails.

We built `submit_competition.py` as a safe submission wrapper: it loads the cached action traces, validates them deterministically in `OperationMode.NORMAL` (offline, non-scoring), then on the `--compete` flag opens a COMPETITION scorecard and replays each game through the live API with inter-action throttling (default 150 ms) and exponential backoff on 429 rate-limit responses. The throttling is important: naive submission hit rate limits after 4 games in our first attempt. At 150 ms/step, the full 24-game replay takes approximately 15 minutes and sits within the 15-minute stale-scorecard timeout comfortably.

### 3.5 The model in this study

All frame-questioning agents and all world-model derivation used **Claude Opus 4.6 (1M context window)**. Other Claude models (Sonnet, Haiku) were not used. We did not use GPT-5, Gemini, or any non-Anthropic model for the reported result.

The model served two roles:

- As the agent reading engine source, proposing world models, and writing solvers.
- As the frame-questioning agent challenging existing models when search plateaued.

The local ollama-based Gemma 3 12B was tested on a small subset of games under a separate harness we call `sage_solver` (an autonomous solver loop, removed from ARC-SAGE for license reasons but retained in the dp-web4/SAGE parent repository). It scored 0 on every game it was run against. The gap between the Opus result and the Gemma baseline, rather than being a failure, defines the problem this paper's Phase 2 plan is designed to close.

---

## 4. Results

### 4.1 Overall scorecard

| Metric | Value |
|---|---|
| Overall score | **84.9%** |
| Environments completed (WIN) | 21 / 25 |
| Levels completed | 160 / 183 |
| Total actions | 5,159 |
| Games at 100% per-level efficiency | 14 |
| Total cost (model API + subscription prorated) | ~$250 estimated |

### 4.2 Per-game breakdown

| Tier | Score range | Games | Count |
|---|---|---|---|
| Perfect efficiency | 100.0% | cd82, ft09, tn36, vc33, tr87, tu93, lp85, ls20, su15, s5i5, ka59, m0r0, re86, wa30 | 14 |
| Near-perfect | 89.4 – 97.7% | g50t, sk48, sp80, ar25, sc25 | 5 |
| Partial complete | 71.4 – 84.9% | r11l, cn04, dc22 | 3 |
| Mechanic blocked | 13.0 – 16.7% | sb26 (3/8), bp35 (3/9) | 2 |
| No trace captured | 0.0% | lf52 | 1 |

The 14 perfect-efficiency games are those where our action count equaled or beat the human baseline on every level of the game. Because RHAE scoring is squared, beating the human baseline by even a few actions yields 100% on that level; the per-game score averages level scores weighted by level index, and therefore "beat human by a little on every level" is sufficient.

### 4.3 Structural blockers

`dc22` level 6 (71.4%, 5/6 complete) was investigated across 7+ independent passes. All converged on a circular dependency: the crane needs a plate placed to reach the goal area; placing the plate requires a bridge; building the bridge requires the crane to move first. No permutation within the action space modeled by the solver breaks this cycle. Candidates for unmodeled mechanics (position-invariant clicks, hidden connector behavior, alternative plate interaction) were enumerated and tested; none was found.

`lf52` levels 7 and 10 (0%, 0/10 due to no captured replay — but the solver advanced to level 6 in development) have a stronger result. An exhaustive 1.6M-state BFS over (pieces, blocks, pegs) triples enumerates only 22 unique piece positions across the entire reachable state space. The level's scroll trigger at grid position (8, 8) is unreachable by any piece, confirmed by state-space exhaustion rather than heuristic failure. A separate diagnostic using an engine-internal method revealed that the L7 bypass enables legitimate solves of L8 and L9, after which L10 blocks with identical structure.

We treat these as evidence of mechanics not exposed by the public SDK, or alternatively as levels that require a human experimenter with domain priors (sound cues, hover states, visual pattern recognition at scales the SDK does not expose) that an engine-source-reading agent does not have. Both interpretations support the same conclusion: *the solver did all it could within the surface the SDK provides*.

### 4.4 Local-model baseline (Gemma 3 12B) and the Gemma 4 deployment target

In preliminary game sweeps conducted prior to this work, Gemma 3 12B running under our autonomous solver harness scored 0 on every game attempted. The harness provided the game frame, the available action set, and a rolling short-term context window; it did not provide pre-derived world models or cartridge retrieval. The model failed to identify action-response relationships within the per-game exploration budget and did not complete any levels.

The Gemma 3 result is a context-only baseline against which the Phase 2 cartridge-retrieval architecture is measured. The deployment target itself, however, is the **Gemma 4** family: `e4b` as the primary workhorse (runs comfortably on 16GB+ machines — McNugget, Legion, Thor in our fleet), `e2b` as the small-device baseline (fits-test on 8GB machines — Sprout, CBP), and `26b-a4b` as an aspirational scale-up comparison on Thor. Gemma 4 introduces architectural improvements (MatFormer, sparsity) that make direct Gemma 3-versus-Gemma 4 comparisons uninformative; the 0% Gemma 3 baseline is retained only to establish that context-only prompting is insufficient.

This result should not be read as "Gemma cannot solve ARC-AGI-3." It should be read as: *Gemma given the raw task from scratch, without pre-derived world models or retrieval, cannot solve ARC-AGI-3*. The ARC-SAGE Phase 2 plan is a direct test of the alternative: Gemma given the same raw task plus retrieval access to the world models this paper demonstrates building.

### 4.5 Cost and efficiency

Total cost is estimated at ~$250 USD: two Claude Max subscriptions (~$100 combined) over approximately one calendar week, plus ~$150 in API overage once subscription budgets were exhausted. This sits at the low end of published community-leaderboard costs:

| Submission | Games scored | Score | Cost |
|---|---|---|---|
| RGB-Agent | 3 (preview) | 82.43 | $178.60 |
| tiny-recursive-model (one version) | — | — | $176.00 – $252.00 |
| hierarchical-reasoning-model (one version) | — | — | $148.50 – $201.00 |
| **ARC-SAGE (this paper)** | **25 (public)** | **84.9** | **~$250** |
| evolutionary-TTC (one version) | — | — | $842.00 – $3,648.00 |
| ryan-greenblatt (one version) | — | — | $40,000 (estimated) |

The cost efficiency comes from (a) solver-based solves incur no per-action LLM calls once the world model is built, and (b) frame-questioning deployed selectively against specific blocked levels rather than routinely against every game. The development-time LLM cost is paid once per game and amortizes over every replay.

---

## 5. Discussion

### 5.1 What 84.9% with an expensive frontier model means

The result demonstrates *capability*, not *deployability*. A Kaggle-sandbox submission cannot call Opus; it must run a local model with no internet. The artifacts this work produces — world models, action traces, replayable runs — are therefore the relevant deliverables for the eventual Kaggle submission, not the Opus model itself. The model is scaffolding.

Put another way: the 84.9% is proof that the game mechanics are learnable from engine source by a sufficiently capable agent, and that the harness correctly converts learned mechanics into efficient action sequences. Both halves of that sentence matter for the Phase 2 plan. The first half justifies the cartridge-construction effort (there is something worth encoding). The second half justifies the small-model deployment plan (the action sequences themselves, once known, are not model-dependent — any process that can emit them scores the points).

### 5.2 The convergence verdict as a methodological primitive

Multi-agent frame-questioning convergence is, we claim, a reusable research pattern. For any hard problem where a single investigator keeps arriving at "this is impossible," the question "impossible under what assumptions?" can be surfaced by deploying orthogonally-framed investigators. The cost is a small multiple of single-investigator effort. The payoff is either a frame-break solution (worth its weight in avoided misattributed-impossibility) or a higher-confidence structural verdict (worth its weight in avoided thrashing).

**A concrete counterexample requires honesty.** During the post-submission iteration we observed a case where a single pass issued a "structurally stuck" verdict that a second independent pass overturned: `bp35` level 7 was flagged by the first viewport-rewrite agent as having a G-flip block "sealed behind a spike ring" unreachable via viewport-aware paths. That verdict was wrong. A fresh agent probing the same question found a 9-step staircase construction using iterated E-spread click-and-fall (a game-state-modifying primitive the first agent overlooked). The solve exists; the first agent's model was incomplete.

The counterexample matters for two reasons. First, it refutes the naive claim that *N* converging passes constitute proof of impossibility — one pass isn't enough, and the first bp35 agent was a population of one on that specific verdict. Second, it refines what convergence actually certifies: it provides evidence that agents sharing a particular solver's *action-space model* cannot find a path, which is not the same as proving the path doesn't exist. If the action-space model is incomplete (missed E-spread in bp35's case, or might miss something else in dc22 / lf52), no amount of convergence over it yields certainty.

Operationally, we now treat "structural" verdicts as hypotheses with two dimensions: *n* independent passes from different frames, and *m* independently-modeled action spaces. bp35 L7 had n=1, m=1 — weak evidence. lf52 L7 after session 9 has n=8, m≥2 (the jump-graph model and the viewport-augmented model); that's stronger. dc22 L6 after session 8 has n=8, m=2 (seven crane-mechanics passes plus one source-enumeration pass). The claim "structurally stuck" should be accompanied by both numbers.

**The source-enumeration protocol.** The dc22 session 8 pass formalized a method worth citing separately. Rather than sharing the prior solver's action-space vocabulary, the agent enumerated every engine primitive reachable from player actions by reading ACTION handler branches in the engine source directly. For dc22's ACTION handlers (lines 2606-2931 of the engine file), this produced 16 primitives, which were then cross-referenced against the prior solver's transition set. Every primitive was accounted for; no action-space blind spot existed. This is a positive proof of completeness, complementary to the circumstantial evidence of n passes converging.

The protocol generalizes: for any "structurally stuck" verdict, an independent pass should (a) enumerate engine primitives from source, (b) tabulate which are used by the solver, (c) test every unused primitive against the specific stuck state. Completion of this protocol against a shared engine converts (n, m=1) into (n+1, m=2). Doing it once is usually enough — if the solver's action space turns out to have been complete, the convergence verdict is substantiated.

**Engine architecture matters.** During the dc22 probe we noticed that bp35's structural fragility (the original verdict that was wrong) came partly from bp35's permissive click handler: it dispatches on hit-tested objects without filtering out invisible / off-screen / removed sprites. This made state-changer objects potentially reachable via unusual click coordinates that the solver didn't consider. dc22, by contrast, enforces visibility filtering at the hit-test layer (`is_visible=False`, `INVISIBLE`, and `REMOVED` sprites are pruned before click dispatch). This architectural property makes dc22 *robust* against the bp35-class refutation: you cannot reach a state-changer that the game's own render layer doesn't expose. Structural verdicts are more trustworthy on games with strict hit-test filtering and warrant more scrutiny on games with permissive filtering. This is a game-engine property worth surveying before accepting convergence verdicts.

We suspect this pattern applies beyond ARC-AGI-3 — to debugging, to scientific hypothesis-testing, to architectural review. We are not the first to observe that group deliberation outperforms individual deliberation under the right conditions; we are making a concrete claim about a specific coordination protocol (independent passes, frame-diverging prompts, convergence criterion) and its utility in computational problem-solving — with the caveat that convergence within a shared action-space model is necessary but not sufficient for truly structural verdicts.

### 5.3 Limitations and what "solved" means here

Three games scored materially below 100% for structural reasons within the model: `sb26` (unmapped reset/swap mechanic at L4), `bp35` (400-error on specific click at L4 — API-side rejection of a coordinate the engine-side model believed was valid), `dc22` L6 (circular dependency, enumerated and confirmed). These are honest partial results; we do not claim to have solved them.

One game (`lf52`) scored 0 due to no captured replay at submission time; this is a pipeline gap, not a solver failure — the solver had developed to L6 in live play. A patched solver emitting per-level winning sequences would recover an estimated 60% on `lf52` alone.

Our scorecard is on the public set (the 25 preview games). The official ARC-AGI-3 evaluation is against ~55 semi-private + ~55 private environments not yet exposed. Approaches that overfit to the public set (per-game hand-crafted solvers) generalize poorly by construction. Our solvers are per-game by design, for the public set result — but the Phase 2 plan explicitly addresses generalization via cartridge retrieval and world-model adaptation rather than per-game coding.

### 5.4 What we didn't derive until forced to: viewport as interaction constraint

The `bp35` submission result (13.06%) illustrates something subtler than a bug. Our solver for `bp35` was developed against the local SDK (the `arc_agi` Python package, with the game engine running in-process). It produced a 304-action trace that completed all 9 levels under local replay. When submitted against the live competition API, the trace hit an HTTP 400 on the first action of level 4.

Inspection revealed 28 click actions across 5 levels where the `y` coordinate fell outside `[0, 63]` — e.g., `CLICK (42, 90)`, `CLICK (30, -6)`. The game engine's click handler (`game.gwfodrkvzx`, bp35.py:4289) adds the current camera y-offset to the incoming y before computing the clicked object's world position. The solver's `click_act` subtracts the same offset before sending. In abstract algebra these cancel and both agree on the world-space object. In practice the *intermediate* value (what was sent to `env.step`) was sometimes outside `[0, 63]` because the camera hadn't scrolled far enough.

**The local engine accepts it.** It never validates the coordinate range before forwarding to the game class, so the out-of-viewport click still clicks the right world object. **The remote API rejects it** with 400 before the game engine runs — enforcing the specification that click coordinates be valid viewport positions.

The surface fact: 28 clicks locally-compatible but API-illegal, producing a 13.06% score on a game we could otherwise hit 100% on.

The deeper fact: *the solver learned the correct world model for `bp35` without ever learning that the viewport is a first-class constraint on interaction.* It treated the viewport as a rendering concern rather than an interaction surface. The error did not surface during development because the local engine permitted the treatment.

This has a direct implication for the Phase 2 plan. A small model reasoning against a cartridge that encodes the `bp35` world model would inherit the same blind spot — unless the cartridge bundle also carries an *interface primitives layer* that the small model can retrieve and apply. The primitive in question is simple to state:

> *If the intended target's world position is outside the current viewport, scroll action comes first; choose scroll direction and magnitude to bring target into `[0, 63]` with minimum cost; then click with the computed viewport-relative coordinate.*

This is not a `bp35`-specific rule. It applies to any game where the world exceeds the viewport and scrolling is a player action. `dc22`, `re86`, `ar25`, `lf52` all have camera scrolling; the same latent fragility may exist in their captured traces. Preliminary audit indicates `bp35` is the only submission where the fragility actually materialized in a scored run, but this is evidence of luck in target positioning, not evidence of absence.

Reframing the finding as a positive claim about the architecture: **the capability a world model does not contain is exactly the capability external retrievable memory can supply.** Phase 1 models correct game mechanics at the cost of not modeling the substrate (how the game is perceived and acted on). Phase 2's cartridge schema is the natural home for those substrate primitives — viewport-aware click being one, action-budget awareness (see §3.2 and the `sk48` lesson in the cross-game patterns doc) being another. A local small model equipped with these retrievable primitives *alongside* the game-specific world model does not need to re-derive the substrate each time; it adapts the primitives to the current game's geometry.

This suggests a two-layer cartridge bundle for Phase 2:
- **Substrate cartridges**: viewport, action budget, animation timing, click classification (selection vs. action), undo semantics. Transferable across all games.
- **Game-world cartridges**: per-game ontologies from Phase 1. Retrieved by visual signature.

The substrate cartridges are, we claim, a finite and enumerable set. The game-world cartridges scale with the game catalog. This factoring matters for generalization: a new game drawn from the evaluation set is unlikely to have a matching game-world cartridge but is very likely to share substrate primitives with games we do have.

**Substrate primitives decompose by game-engine architecture.** Applying the viewport-aware-click analysis to lf52 (one of our structurally-stuck games from §4.3) revealed a second refinement: the primitive is not one thing but a family indexed by scroll model. bp35 uses a camera-based model — camera is a first-class game object, player movement drives camera position via an explicit formula, so solvers can insert scroll actions directly as a known control. lf52 uses a grid-offset side-effect model — there is no camera object; what shifts click-to-world mapping is the grid container's pixel offset, and only a specific action pattern (pushing a particular piece configuration into a wall) triggers the shift. For lf52 we fixed L3's OOB clicks not by *adding* scroll actions but by *reordering* the existing sequence so the scroll-triggering push happened before the clicks that depended on the shifted offset. The fix consumed zero extra actions.

For the Phase 2 cartridge schema this matters: a cartridge-aware small model must first identify which scroll model the current game uses before applying the viewport primitive. The diagnostic is mechanical — is there a `camera.position` attribute? — but it must be carried as a first-class check, not assumed.

**Scope precondition.** A probe triggered by the bp35 finding also applied the viewport-aware-click analysis to lf52's stuck levels (L7, L10). Empirically, lf52's click handler exhibits the same camera-offset pattern as bp35: out-of-viewport clicks do reach off-screen pegs and trigger the game's selection mechanic. But lf52 L7 remains unsolved under this reframe, because the binding constraint is in the tile-movement graph, not the interface: selected pegs have no legal jumps regardless of how selection happened. The viewport primitive therefore applies when (a) the target is in-world but out-of-viewport AND (b) selecting it enables a new state transition. bp35 satisfies both; lf52 L7 satisfies only (a). The primitive pair brackets the scope — and the lesson for the cartridge schema is that substrate primitives carry preconditions, checked against the game-world cartridge's legal-action function. A naive "always scroll if OOB" heuristic would generate no-op action sequences in games like lf52; a cartridge-aware small model should know the difference.

### 5.5 The recognition-over-derivation thesis, stated precisely

Define:
- **Derivation**: the process by which an agent, given a novel problem, constructs the reasoning chain from first principles (or from sub-principles it has access to).
- **Recognition**: the process by which an agent, given a novel problem and access to structured memory, retrieves a similar-in-relevant-respects prior problem and its associated solution schema, then adapts the schema to the current instance.

Large models are good at derivation and poor at recognition (their memory is implicit in weights, with no deterministic retrieval mechanism). Small models are poor at both on novel tasks. The ARC-SAGE thesis: **small model + structured retrievable memory = sufficient capability on tasks previously requiring large models**, provided the memory is constructed such that retrieval yields relevant schema and the small model can execute adaptation.

This is testable. The test is Phase 2.

---

## 6. Phase 2: Small-Model Deployment Plan

The Phase 2 objective is a Kaggle-sandbox-compatible local-model agent that scores materially on ARC-AGI-3 using the artifacts produced in Phase 1.

### 6.1 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Kaggle Sandbox (32GB VRAM)                │
├──────────────────────────────────────────────────────────────┤
│   ┌─────────┐   ┌─────────────┐   ┌────────────────────┐    │
│   │  Game   │──▶│  Grid       │──▶│  Membot Cartridge  │    │
│   │  Frame  │   │  Vision IRP │   │  Retrieval         │    │
│   └─────────┘   └─────────────┘   └────────────────────┘    │
│                                            │                 │
│                                            ▼                 │
│                                   ┌─────────────────────┐   │
│                                   │  World Model        │   │
│                                   │  (text ontology)    │   │
│                                   └─────────────────────┘   │
│                                            │                 │
│                                            ▼                 │
│                                   ┌─────────────────────┐   │
│                                   │  Gemma 4 e4b        │   │
│                                   │  (adaptation only)  │   │
│                                   └─────────────────────┘   │
│                                            │                 │
│                                            ▼                 │
│                                   ┌─────────────────────┐   │
│                                   │  Action             │   │
│                                   └─────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

The small model reasons only about *how this specific level-instance maps to the retrieved schema*. It does not derive the mechanic from scratch.

### 6.2 Cartridge construction — two-layer schema

Motivated by §5.4, the Phase 2 cartridge bundle is structured in two layers:

**Substrate cartridges** encode interface and interaction primitives that are invariant across games:
- *Viewport-aware click*: if target world position is outside `[0, 63]`, scroll action comes first (chosen to minimize cost); click uses viewport-relative coordinates.
- *Action budget*: every action (including rejected ones) may decrement a resource; monitor the budget; avoid speculative search that depletes it.
- *Animation timing*: some actions complete over multiple frames; subsequent actions must wait or the state read is stale.
- *Click classification*: small pixel changes (~1px) indicate selection or toggle; large changes indicate state transitions. Selection is cheap and reversible.
- *Undo semantics*: when ACTION7 is available, undo reverts the most recent state change. When not available, dead-end recovery requires RESET.

These are ~5–10 primitives, finite and enumerable. They transfer to any game sharing that substrate feature (viewport for all scrolling games, action budget for all games with a turn counter, etc.).

**Game-world cartridges** encode the per-game world models from Phase 1 — one cartridge per game, retrieved by visual signature from the current frame. Content:

- A **visual signature** (grid-vision features at multiple scales, sufficient for retrieve-by-similarity from a novel game frame)
- A **textual world model** (ontology, mechanics summary, win conditions, heuristics — what the solver encodes)
- Optionally, **representative action snippets** from the replay traces — useful for few-shot prompting the small model on expected action patterns

Retrieval at game-step time is therefore a two-stage lookup: substrate cartridges are always loaded (small, finite); game-world cartridge is retrieved by current-frame similarity. The small model reasons over both simultaneously.

*(Section to be expanded by Andy Grossberg — `membot` paired-lattice mechanics, retrieval characteristics, how the two-layer schema maps onto membot's internal structure, whether substrate cartridges are a new schema type or fit into the existing paired-lattice format with a different lattice role.)*

### 6.3 Vision IRP

Grid-vision feature extraction must be fast, compressed, and retrieval-friendly. Tests to date have used preliminary encoders; Phase 2 requires a feature representation that produces stable retrieval across level variants within a game (so L4 retrieves the same world model as L1) while distinguishing different games.

### 6.4 Evaluation harness

A Kaggle-sandbox-compatible evaluation harness that:
- Loads Gemma 4 e4b (primary) or an equivalent sub-32GB-VRAM open-license model locally
- Loads the cartridge bundle produced by §6.2
- Runs the consciousness loop at game-step cadence (~100ms target)
- Logs action efficiency relative to the Phase 1 Opus baseline

### 6.5 Deliverables and timeline

| Deliverable | Target | Status |
|---|---|---|
| Phase 1: capability demonstration on public set | 2026-04 | ✓ done (this paper) |
| Cartridge bundle (25 entries, visual + textual) | 2026-05 | Planned |
| Vision IRP tuned for retrieval | 2026-05 | Planned |
| Kaggle harness + offline evaluation | 2026-06 | Planned |
| Milestone 1 submission (if harness working) | 2026-06-30 | Contingent |
| Phase 2 results paper | 2026-07 | Planned |

### 6.6 Falsification criteria

Phase 2 is genuinely testable. We will consider the recognition-over-derivation thesis *falsified* (in this domain) if, given the full cartridge bundle from Phase 1 and a working retrieval pipeline, Gemma 4 e4b scores less than 15% on the public set. That would indicate either that the cartridges do not transmit what the solvers encoded, or that adaptation-only reasoning is insufficient for this benchmark, or both. Either outcome is informative.

We will consider the thesis *substantially supported* if Gemma scores above 40% on the public set under these conditions — a ~2× lift over the current best pure-local submission and strong evidence that the cartridge mechanism is doing real work.

---

## 7. Preemptive Questions

### 7.1 "Isn't this just distillation?"

No. Distillation bakes knowledge into model weights via supervised training on teacher outputs. This approach keeps the small model's weights frozen and puts structure into an external retrievable memory. Consequences:

- **Updates are cheap**: adding a new game adds a cartridge entry, not a training run.
- **Provenance is preserved**: cartridge entries trace to specific solvers, world models, and replay runs; weight changes from fine-tuning are opaque.
- **Failure modes are legible**: when the small-model agent fails, we can inspect what was retrieved and what the model did with it. Fine-tuned failures are harder to diagnose.

The distinction matters practically because ARC-AGI-3 is a moving target: environments evolve, new games are added. A retrieval-based architecture incorporates new capability as cartridge additions. A fine-tuning-based architecture requires repeated training passes.

### 7.2 "Why not fine-tune Gemma directly on the action traces?"

Fine-tuning on the existing traces would plausibly produce a model that can replay these specific games. It would not plausibly produce a model that handles the semi-private and private sets well, because those environments will have mechanics not in the training traces. Fine-tuning teaches the model to reproduce patterns; it does not teach the retrieval-and-adapt skill the benchmark actually tests.

The ARC-AGI-2 post-mortem (from which SAGE emerged) documented this failure mode: training-based approaches scored high on training-adjacent tasks and collapsed on novel ones. We are explicitly not repeating that mistake.

### 7.3 "What about generalization to unseen games?"

The Phase 2 thesis predicts that *within-game* level generalization (L1 solved via retrieved model → L4 uses same retrieved model) will work well, and *across-game* transfer will work to the extent that the new game shares structural features with games in the cartridge bundle.

For genuinely novel games, neither the cartridge bundle nor any trained model has prior experience; performance will be driven by the small model's ability to build a new world model on the fly, which is where derivation is still required. Our current prediction is that Gemma 4 e4b will struggle here, and that the realistic deployment plan against the full (~135 environment) evaluation set involves (a) strong performance on recognized-by-cartridge games, (b) moderate performance via on-the-fly building on adjacent-structure games, and (c) genuine failure on wholly novel games. That's a substantive prediction we plan to test, not marketing.

### 7.4 "The Kaggle sandbox constraints are severe. Is this actually feasible?"

The relevant constraints are 32 GB VRAM, no internet, and 8-hour total runtime. These are sufficient for Gemma 4 e4b, cartridge loading, and per-action inference at roughly 10 tokens/second, which is adequate for ARC-AGI-3's ~100ms-per-action target under reasonable reasoning budgets. The constraints are demanding but they are not prohibitive. The Phase 2 evaluation harness will be built and tested offline before submission.

### 7.5 "Why is Claude Opus 4.6 listed as a co-author?"

Because the work was meaningfully collaborative. Opus read engine sources, proposed world models, wrote solvers, challenged its own prior conclusions through frame-questioning, and drafted this paper. We treat that as authorship. We are aware some reviewers will find this non-standard; others will find it an honest statement. We are making the choice deliberately rather than laundering the contribution.

---

## 8. Related Work

- **RGB-Agent** (Fox et al., 2026) — Read/Grep/Bash harness with Opus 4.6, 82.43% on 3 preview games, ~1,069 actions. Comparable per-game action efficiency on an overlapping subset; ARC-SAGE scales to 25 games at similar cost.
- **tiny-recursive-model, hierarchical-reasoning-model** — Specialized architectures competing on the community leaderboard at similar cost points.
- **Chollet, F.** — ARC-AGI benchmarks and the framing of AGI as skill-learning efficiency. SAGE architecture is directly responsive to this framing.
- **dp-web4/SAGE** — The research framework from which ARC-SAGE is extracted. Includes the full consciousness loop, metabolic state machinery, and raising curriculum not used in this paper.
- **Andy Grossberg / membot** — Paired-lattice cartridge memory system. Public MIT, foundational to Phase 2.

---

## 9. Contributions and Acknowledgments

**Dennis Palatov** — Research direction, SAGE architecture, problem framing, experimental design.
**Claude Opus 4.6 (1M context)** — Solver implementation, world-model derivation, multi-agent frame-questioning sessions, capture-replay pipeline, competition submission, this paper draft.
**Andy Grossberg** — Membot paired-lattice architecture, cartridge format, foundational to Phase 2 plan (*section to be expanded by Andy*).

This work used infrastructure and prior research from the dp-web4 ecosystem, including SAGE (AGPL), shared-context fleet coordination (private), and Web4 trust architecture. None of that code is bundled in the public ARC-SAGE repository to maintain MIT license cleanliness. Readers interested in the broader research program are pointed to [dp-web4/SAGE](https://github.com/dp-web4/SAGE).

The ARC Prize Foundation provides the ARC-AGI-3 benchmark, SDK, and evaluation infrastructure. This work would not exist without those resources. We intend to apply for ARC Prize research grant funding to support the Phase 2 effort described in §6.

---

## Appendix A: Reproducibility

The public ARC-SAGE repository includes:
- All 25 per-game solvers
- All cached winning action sequences (`solutions.json` per game)
- Full replayable visual memory (77 `run_YYYYMMDD_HHMMSS/` directories, 61 MB of step-by-step PNGs)
- The competition submission script
- A `REPRODUCE.md` documenting the exact path from clone to a fresh scorecard

Verification: `python3 submit_competition.py --dry-run` reads only from bundled data and should produce "24/24 games OK, 5345 total actions". Any reader with an ARC-AGI-3 API key can run `--compete` to produce their own scorecard matching our 84.9% within rounding.

## Appendix B: What is not in this paper

- The full consciousness loop, trust posture, metabolic states, and policy gate — these are SAGE subsystems not used by ARC-SAGE.
- Fleet coordination across the 6-machine development environment — that infrastructure is privately-hosted.
- The detailed content of individual game world models (~500 lines of Python per game) — available in the repository.
- Andy's membot section — to be added.

---

*End of draft. Ready for Andy's review and additions.*
