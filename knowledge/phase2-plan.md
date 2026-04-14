# Phase 2 Plan — Deployment Engineering

*Dated 2026-04-13. Pivoting from game-engineering to deployment-engineering.*

## The shift

Iter-1 produced 25 per-game world models and 173/183 level-wins via Opus-4.6 solver development. Iter-2 added viewport-aware fixes, convergence-framework refinements, and a 90.53% reserve scorecard. Both phases were *game engineering* — cracking specific games' world models and interface quirks.

Phase 2 is *deployment engineering* — making a small local model use what we cracked, under Kaggle constraints (32GB VRAM, no internet, 8-hour budget).

The system-level unknowns that matter now are different from the ones that mattered in Phases 1-2. Prioritized below.

## Model plan

**Competition target**: Gemma 4 family (not Gemma 3). Gemma 3 experiments, if any, are for completeness only — it is not a deployment candidate.

| Variant | Target machines | Role |
|---|---|---|
| `gemma4:e4b` | McNugget (M4, 16GB unified), Legion (RTX 4090 24GB), Thor (AGX Thor 128GB) | Workhorse + gladiator candidate. Primary deployment target. |
| `gemma4:e2b` | CBP (RTX 2060S 8GB), Sprout (Orin Nano 8GB) | Fits-test on small machines. Probably won't fit, worth trying. If it fits, becomes the lowest-end baseline. |
| `gemma4:26b-a4b` | Thor only | Aspirational scale-up comparison. Unlikely in Kaggle without a quant not yet available. Use to characterize "with more compute, how much better?" |

**Later / if needed**: expert evictions (same technique tried on qwen3.5-30b previously) could shrink `26b-a4b` to fit Kaggle. Not the immediate focus.

**Fleet delegation**: tests that require compute beyond local capacity get dispatched to the machine with headroom. Gemma evaluation sweeps naturally fan out to Legion / Thor / McNugget; CBP and Sprout run lighter probes.

## Tier 1 — directly unblocks Phase 2 deployment

Do these first. Results shape every downstream design choice.

### 1.1 Gemma 4 failure-mode taxonomy

Instrument the autonomous solver harness with per-stage logging:
- Perception stage: does the model parse the 64x64 grid correctly?
- Reasoning stage: given correct perception, does it plan coherent action sequences?
- Context management: does it retain observations across 10+ actions?
- Action emission: does it produce well-formed output the harness can execute?

Run matrix against the simplest game in our catalog (`cd82`, 73-action solve, 6 levels):
- No context (baseline): Gemma gets frame + action set only
- With textual world model (cartridge simulation): Gemma gets ontology, mechanics, heuristics
- With action-trace demonstrations: Gemma gets 3-5 example action sequences from our capture

Each condition × each Gemma variant (e4b primary; e2b if fits; 26b-a4b on Thor for reference) → ~3-6 combinations. Each takes ~10-30 min of model time.

**Deliverable**: concrete failure-mode classification. "Gemma fails at X when given Y" for each X ∈ {perception, reasoning, context, action} and Y ∈ {no-context, cartridge, demos}. This shapes what cartridges must carry.

**Budget**: 1 day distributed across fleet machines.

### 1.2 Visual-signature retrieval fidelity

Build vision-feature encoding (grid-vision IRP or equivalent) for 5 diverse games: `cd82` (click-only), `r11l` (multi-entity), `tu93` (move-only), `sk48` (move+click), `lp85` (click-only).

Generate feature vectors for:
- Start frame of each level of each game (5 games × ~6 levels = ~30 frames)
- Hold out 1 level per game, retrieve against the rest

Measure: does the held-out frame retrieve the correct game's cartridge? What's the margin vs. nearest-neighbor alternative?

**Deliverable**: confusion matrix + quantitative retrieval quality measure. Gate check on the Phase 2 architecture — if retrieval is unreliable, the whole cartridge mechanism fails.

**Budget**: 1 day on one machine.

### 1.3 End-to-end pipeclean on ONE game

Build a full cartridge for `cd82` (world model text + visual signatures + example action traces). Assemble the full Phase 2 inference loop: frame → retrieval → cartridge-load → Gemma 4 e4b inference → action.

Run end-to-end on `cd82` L1-L6 (full game). Measure:
- Does Gemma 4 solve the game end-to-end with the cartridge?
- Action efficiency vs. the 73-action Opus baseline
- Which cartridge fields actually get used (vs. dead content)

**Deliverable**: either a working end-to-end Phase 2 solve on one game OR a concrete diagnosis of what blocks it. If it works, scale to 25 games. If it doesn't, iterate on cartridge shape before scaling.

**This is the single most important experiment.** Converts theory to working/failing artifact.

**Budget**: 2-3 days. Best machine for inference + iteration speed.

## Tier 2 — competition path (after Tier 1 artifacts exist)

### 2.1 Substrate cartridge implementation

Code the 7 substrate primitive cartridges enumerated in `paper/phase2-substrate-cartridges.md`:
- Viewport-aware click (with scroll-model dispatch: camera-based vs grid-offset side-effect)
- Action budget
- Animation timing
- Click classification by pixel delta
- Undo semantics
- Structural vs. positional win
- Directional ambiguity

Test composition: can Gemma 4 reason jointly over a substrate cartridge and a game-world cartridge without confusion?

**Budget**: 3-5 days.

### 2.2 Kaggle sandbox simulation

Offline-test the full stack under 32GB VRAM + no-internet constraints. Find memory pressure points, inference latency, 8-hour time budget reality.

**Budget**: 2 days.

### 2.3 Private-set generalization probe

Run the Phase 2 harness against semi-private environments (if accessible). THE competition-critical question: does recognition+adaptation via cartridges generalize beyond the 25 public games?

**Budget**: 1-2 days once harness is stable.

## Tier 3 — research depth (parallel to above, lower priority)

### 3.1 Multi-agent convergence across models

Re-run the convergence protocol using non-Opus agents (Sonnet, GPT-5, Gemini) on `dc22 L6` or `lf52 L7`. Tests the hypothesis in `knowledge/system-level-unknowns.md` §3 that convergence verdicts carry Opus training blind-spots.

### 3.2 Human solve attempt on stuck levels

Hand `dc22 L6` or `lf52 L7` to a human (or Nova, or a non-Opus AI) and see if they solve. Any refutation teaches us about convergence limits.

### 3.3 Gemma 3 baseline completeness (optional)

For paper completeness only, since Gemma 3 isn't a deployment target. Run 1.1 methodology against Gemma 3 12B alongside Gemma 4 e4b. Not a priority.

### 3.4 Expert-eviction on 26b-a4b

If `26b-a4b` makes a materially different showing on Tier 1.1, and we later want it in Kaggle, revisit the expert-eviction technique tried on `qwen3.5-30b`. Not focus now.

### 3.5 Action-efficiency theoretical minimums

Academic question: for our 100%-scored games, what's the true shortest solve? Interesting for paper framing, not score-relevant.

## Fleet machine assignments (initial)

| Machine | VRAM / unified | Gemma fit | Role for Tier 1-2 |
|---|---|---|---|
| Thor | 128GB unified | e4b, e2b, 26b-a4b | Gladiator (run 26b-a4b as scale reference); also e4b production |
| Legion | 24GB VRAM | e4b | Primary Tier 1.1 / 1.3 inference workhorse |
| McNugget | 16GB unified (M4) | e4b (borderline) | Secondary e4b inference; game-mechanics tooling |
| Nomad | 8GB VRAM | e4b (tight) or e2b | Field test; oversight-pool work |
| Sprout | 8GB unified | e2b attempt | Fits-test the low-end; if e2b fits, continues as edge reference |
| CBP | 8GB VRAM (this machine) | e2b attempt | Fits-test + Phase 2 infrastructure dev |

Cross-machine sync: each machine writes to its own slot in `knowledge/fleet-learning/<machine>/phase2/` to avoid conflicts.

## Sequencing this week

Day 1-2: Tier 1.1 (Gemma failure-mode taxonomy) — fan out across Legion, McNugget, Thor.
Day 2-3: Tier 1.2 (retrieval fidelity) — one machine (probably Legion).
Day 3-5: Tier 1.3 (end-to-end pipeclean on cd82) — primary machine, whichever shows best single-session efficiency from Tier 1.1.

Tier 2 starts after Tier 1 closes.

## Falsification triggers for Phase 2 as a thesis

From `paper/draft.md` §6.6: Phase 2 is *falsified* if Gemma 4 e4b with full cartridge bundle scores <15% on the public set. *Substantially supported* at >40%. Run the falsification test as soon as Tier 1.3 is working, don't wait for the full cartridge bundle — a partial bundle scoring 30%+ is already strong signal.

## What gets documented, where

- This file (`knowledge/phase2-plan.md`) — the plan itself, updated as we learn
- `paper/draft.md` §4.4 and §6 — update model references from Gemma 3 to Gemma 4 family
- `paper/phase2-substrate-cartridges.md` — update model mentions similarly
- `knowledge/system-level-unknowns.md` — cross-reference to this plan; update Tier 1 items with Gemma 4 specifics
- Per-machine Phase 2 progress logs in `knowledge/fleet-learning/<machine>/phase2/` (created as each machine starts contributing)
