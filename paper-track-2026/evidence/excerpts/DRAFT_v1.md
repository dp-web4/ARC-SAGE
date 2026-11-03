# Excerpt: `DRAFT_v1.md`

- Source: dp-web4/dev-SAGE (private), `paper/arc3-paper-track-2026/DRAFT_v1.md` at commit `ca448ede9`.
- Each block quotes whole source lines, unedited, with their line numbers. Lines outside these ranges are not published here; the full file stays private.

## Lines 162-168: clock line: 9 -> 37 real-time-mechanics reasoning lines

```text
  162  **(b) The agent mistakes harness facts for world facts.** The harness knew the per-game wall-clock budget and never
  163  said it; in one game the model found a correct 8-move plan after time had expired. Adding a bare line, *"Game clock:
  164  12.4 min elapsed, 17.2 min remaining"*, made the model hypothesise that in-game timer bars run in real time.
  165  - Reasoning lines proposing real-time mechanics: 9 → 37. "Running out of time" ruminations: 0 → 18. Levels: 8 → 4
  166    (n=1; that arm also halved the tool-output cap).
  167  - ARC-AGI-3 games are turn-based, and the model holds that prior, but a context-free number activated the wrong one.
  168  - Fix: **every fact the harness states carries its origin and the prior that bounds it**: *"Harness clock (your
```

## Lines 258-264: variant levels: su15 wall falls in 20/24 package-runs

```text
  258  | block 2 base | 5/6 | 2/2 |
  259  | block 2 level memory | 6/6 | 1/2 |
  260  
  261  The parents stay walled: su15 never passed its wall in 6 earlier runs; tn36 cleared it once in 7. On fresh layouts
  262  **su15's wall falls in 20/24 package-runs**, tn36's in 6/8 (n = 2 packages, small). So neither is a universal wall
  263  for this model.
  264  
```

## Lines 276-282: time 2x: 13/18 pre-classed STARVED rows converted

```text
  276  
  277  **Time (measured, one block; pre-registered by kimi, 2026-10-09 18:55 UTC).** Before the run, each depth-stall row
  278  in the paired pilot was classed STARVED (the clock ran out while progress continued), MIXED or WALL, using a classifier
  279  frozen at commit 878dcaa5. We then gave the five depth games (m0r0, ls20, ka59, g50t, bp35) a 2x per-game cap
  280  (5,803 s vs 2,902 s) and changed nothing else (`pilot_time2x`, base arm).
  281  - **Primary endpoint: 13/18 STARVED rows converted**, against a pre-set bar of ≥4. m0r0 finished 6/6 levels (never
  282    finished in 6 earlier trajectories), ls20 converted all 6 rows, g50t both.
```

## Lines 340-348: goal-gate pilot: plan_check intent 11 turns, 0 calls, 160 armed turns; <20 calls = not measured

```text
  340    were used only when the post-arm stall was long (block 1: stalls of 13–102 actions), and ignored when arming landed
  341    late on a level about to clear (blocks 2–3: 0/7 and 0/8 armed levels touched a tool).
  342  - **Goal-gate pilot** (two blocks): 46 / 44 levels vs base 45 / 45 / 45. The tool was armed on 18–20 levels, and
  343    **`plan_check` was called 0 times.** Pre-registered reading: fewer than 20 calls = NOT MEASURED (the instrument was
  344    unused). kimi's census of armed levels (`blackbox/runs/GOALGATE_ARMED_CENSUS_1010.md`; 19 armed levels, 160 post-arming
  345    turns) shows what happened instead. The model mentions `plan_check` in 20 turns and states an intent to use it in 11
  346    (*"Let me use the harness's plan_check first to validate"*), then acts directly. It reads the docs (9 times) and uses
  347    the one tool with no setup cost, `expect=` (13 turns). The two tools that require it to write a simulator are never
  348    called. The stated reasons are a simple plan, the cost of writing `sim_fn`, not knowing the goal, and budget pressure.
```

## Lines 372-388: fine-tuning: 16.06 scored; P1-T leave-families-out 34 vs 57 levels, NLL improves

```text
  372    A zero-LoRA merge served correctly. MTP acceptance 2.75 → 2.60; logprob parity top-1 0.945 against a 0.95 bar.
  373  - **P1** (launched 2026-10-10 19:28 UTC): 689 records / 4.8M tokens, r16, full backward. **Text-only**: images are
  374    placeholders in training, a declared deviation from our multimodal rule (the vision path is unchanged at serving).
  375    Under dp's 10-10 directive there is no family holdout, so the scored slot was the read: the TUNED arm
  376    (LEAN + P1 LoRA) scored **16.06** public (submission 57088784, 2026-10-12) against LEAN's 25.23 (57055743, 10-11) —
  377    beyond the band. A serving confound (drafter acceptance) was checked and refuted as the cause
  378    (`blackbox/runs/POSTTRAIN_P1_READ_1009.md`).
  379  - **P1-T (measured; pre-registered 10-13, verdict 10-17).** P1's scored loss conflated two causes: cloning
  380    exploratory play, or the LoRA degrading reasoning. P1-T separated "does the recipe transfer" from the slot noise
  381    with a leave-families-out measurement (`runs/POSTTRAIN_APPROACH.md`, P1-T section; verdict
  382    `runs/p1t_runs/20261017T021532Z/read/P1T_VERDICT.md`; independently reproduced by two readers). A fresh adapter
  383    tuned on all 25 public families was played against the base on 5 held-out-at-measurement families (OOF) and 5
  384    in-family controls, 15 game-passes each. The pre-registered promotion rule required OOF levels ≥ base AND improved
  385    OOF NLL. **Verdict: NO_SCORED_ARM.** OOF levels tuned 34 vs base 57 (−1.53 per game-pass against a pre-computed
  386    MDD of 1.02); control 31 vs 42 — the tuned player is worse in 9 of 10 families, *including the families it was
  387    trained on*, and spends 129.7 actions per OOF level against the base's 56.6. Yet token NLL on our own trajectories
  388    improves under the adapter on every set (−0.17 OOF, −0.19 in-family), and the serving gate passed.
```

## Lines 565-572: goal taxonomy: 6 GOAL / 1 TRANSITION / 0 exploration-bound of 7 highest-burn game-levels

```text
  565  **A measured taxonomy of goal failure** (kimi-code; `blackbox/runs/KILLER_PRIORS_1008.md`, proposed as
  566  `TAXONOMY_KIMI.md`). We read every failed attempt on the seven highest-burn game-levels at quote level and contrasted
  567  each with clearing runs of the same level where those exist. For each attempt we recorded the believed goal, the prior
  568  it assumed, the prior the level needed, and how long the contradicting evidence went unnoticed. **Six of seven failures
  569  are GOAL-class** (the run never acts on a correct win condition), **one is TRANSITION** (sb26: the switch from
  570  exploring to verifying), **none is exploration-bound.** The GOAL failures fall into four subclasses, in increasing severity:
  571  1. **Unposed target** (cd82, tn36): the run never asks what end state wins. The budget dies on modelling the mechanism.
  572     One cd82 run debugged a pixel-exact simulator to `pred 53 act 55 match False` four times while one stamp from the
```
