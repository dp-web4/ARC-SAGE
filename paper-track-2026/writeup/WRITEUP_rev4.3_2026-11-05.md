<!-- SUBMISSION TEXT: dp approved rev 4.3 on 2026-11-05 (supersedes 4.1). -->
<!-- DRAFT rev 4.3 (11-05, cloud-claude). Not submitted. Submission is dp's. Whole writeup incl. title + footer <=1,500.
     = rev 4.2 + dp's two edits (drop the April 15 row; first step from 0.20, the organism era's best) + codex's rev-4.2
     review (branch codex/arc-rev42-review-1105, 158814f89): the final +2.03 is dc22 + re86 completion, separated from the
     frame-questioning examples; length counted including title, subtitle and footer. rev 4.2 kept unchanged. -->

# Affordance Is All You Need

*Given a strong model, what the harness lets it do matters more than what it tells it to think.*

## Abstract

In April 2026, within two weeks of starting on ARC-AGI-3, **Claude Opus 4.6** scored **94.85%** on the 25 public games (scorecard c7dfb4f1), in a harness that gave it tools rather than a strategy. ARC Prize's official result for the same model is **0.5%** ($8.9K; semi-private set, its own harness): a reference point, not a controlled comparison. Given a shell, Python, persistent memory and the game, it chose to read the engine source it found, reverse-engineer the obfuscated mechanics, and write a Python solver per game. Code-acting is also the paradigm of prominent competition agents (Tufa's Duck harness, dfranzen's Milestone-2 notebook) and of our best scored notebook.

**Our thesis: given a strong model, affordance is all you need.** An *affordance* is a possibility for action or understanding available to the agent: something it can perceive, use, change, remember or revisit. A harness *decision* is a choice made on the agent's behalf. A strong model is the prerequisite: it already holds the priors the games caricature. Affordances let it use them; imposed decisions did not help. We report what worked, what did not, and why.

## 1. Phase 1: a strong model with affordances (Claude Opus 4.6, public games)

**Setup.** One Claude Opus 4.6 session (1M context) in Claude Code, plus parallel Opus 4.6 "frame-questioning" passes told to question the current model of a game rather than continue it. The harness provided the SDK and a live game, a filesystem, Python, and persistent memory; no strategy. The engine source was readable.

**What the agent chose.** It found the engine source and reverse-engineered the obfuscated mechanics into per-game notes. It then wrote a ~500-line Python solver per game: semantic state, search, and action traces that were replayed for scoring. By April 8, solvers existed for all **25** games. We disclosed this at the time: *"The solvers were not provided to the agent, it chose to write them. Agent discovered and reverse-engineered game engine source, built solvers"* (our PR #20 to the community leaderboard, April 13).

| Claude Opus 4.6 | Score | Scorecard |
|---|---|---|
| ARC Prize official (Max): semi-private set, its harness | 0.5% ($8.9K) | arcprize.org/leaderboard |
| Ours, public set, April 12 (legacy scoring) | 84.9% | c0d62617 |
| Ours, public set, April 17 | **94.85%** (23/25 games, 175/183 levels) | c7dfb4f1 |

Cost was about $250 (the Phase-1 paper's estimate, through April 15's 92.82%). The same affordances were pointed at the agent's own errors: frame-questioning broke levels a prior pass had logged "impossible" (wa30 L7, re86 L8); exhaustive search proved lf52 L7 unreachable in the scored engine; two independent passes found bp35 L5 sealed. The final two points (92.82 → 94.85) came from completing dc22 and re86.

**The review.** The community leaderboard declined the submission on July 30: *"the agent is able to see the game source. That defeats the purpose and spirit of trying to review the rules on the fly"*. That is the right ruling for a showcase of general methods, and we agreed. It is also evidence for the thesis: given general tools, the agent found an affordance nobody intended and used it fully.

## 2. Phase 2: the competition (local models, hidden games, no source)

The competition allows a local model in 32 GB of VRAM, hidden games, no internet and no source. Model, serving and harness often changed together, so each row names its model.

| Harness | Model | Scored | What the model was allowed |
|---|---|---|---|
| Our organism harness | DiffusionGemma-26B | 0.08–0.20 | to choose from a harness menu; ~685 tokens of digested state, ~10 calls per game |
| Code-acting (Duck lineage) | Qwen3.8-27B | 1.17 | to act in its own code, over verbatim history |
| same, 3× throughput | Qwen3.8-27B | 2.18 | more reasoning tokens per decision |
| dfranzen Milestone-2 copy, 128k context | Qwen3.8-Flash-Next | 24.82 | far more verbatim context and tokens |
| + run identity, practice rules, run journal | Qwen3.8-Flash-Next | **31.82** best (57374159) | its own prior lessons, in its own words |

The two large steps were **0.20 → 1.17 (5.9×)** and **2.18 → 24.82 (11.4×)**. These are observed steps; model, harness, context and serving changed together.

**What worked.**
- **Authority to act in code.** Swapping only the model inside our organism harness moved little (1.46 vs 0.86, one matched game, non-production serving). Acting in its own code did more than any organ we built.
- **A stronger model with room to use it.** Flash-Next scored 5.6 locally at 32k versus 16–38 at 128k: model and affordances worked as a pair.
- **Time and tokens.** In a small, non-randomized panel, doubling the clock converted 13 of 18 pre-classed starved rows. On one 10-hour trace, estimated score rose with reasoning tokens (100k → 27.7, 300k → 56.6 per game).
- **Memory in its own words.** Our best draw added a run identity, 25 practice rules, and a journal shared live across games.

## 3. What did not work: deciding for the model

On our competition base, interventions that imposed a decision did not lift scored play:

| Intervention | What it imposed | Scored |
|---|---|---|
| Text-only goal audit | a checklist of what the goal should be | 24.89 |
| Verification tooling (`replay_check`, `expect=`) | a checking procedure | 19.22 |
| Forced world-model turn (+ a code patch) | a reasoning step on schedule | 18.14 |
| Fine-tuning on our own winning play | our past solutions | 16.06 (leave-families-out play fell 57 → 34 levels) |
| Thinking off on "routine" turns (+ adaptive effort) | which turns matter | 11.48 |
| Lower reasoning effort (+ a goal prior) | how hard to think | 9.62 |
| Goal gate (offline pilot) | a gate to call before acting | unused: promised 11 times, called 0 in 160 armed turns (inert, not a test) |

Single draws are noisy: unchanged resubmissions of Franzen's public notebook scored 25.77 ± 3.93 (an external noise estimate), and 31.82 is our best of about 20 runs. Three rows stacked a second change, so none isolates its named intervention. The pattern is consistent: no scored row reached the copy mean.

The organism era shows why. In one sample, 149 of 204 goals the model proposed could not be expressed in our goal vocabulary; its words ("the grid", "cycle", "undo") named concepts our ontology could not hold. Across three games, executors chose 49–109 actions per game with no model decision. The harness vocabulary became the ceiling.

## 4. Why: the harness should grant, not decide

The two phases suggest a simple division of labour. This is our interpretation:

- **The model supplies the priors.** A 64×64 game caricatures gravity, dials, undo and agency; its pixels cannot teach them. Opus 4.6 had them and used them through code.
- **The harness supplies affordances:** a medium the model already speaks (code against a typed, live API), compute and time, verbatim context, memory of its own lessons, and the ability to check its own work.
- **The harness should not supply the thinking.** Goal menus, scheduled reasoning, imposed checks and executors acting for the model each replaced a decision the model was better placed to make.

## 5. Continuing in SAGE

SAGE carries the principle to persistent local agents that retain and revisit experience. A paged-context prototype keeps durable source pages, a compact directory and model-initiated retrieval, so the agent reopens an observation when its own question calls for it: an affordance, not a decision. An offline replay exists; live uptake, cost and task effects are not yet measured.

## 6. Claim, evidence and falsifier

**Claim.** On ARC-AGI-3, given a strong model, score is bounded by the affordances the harness grants, not by the guidance it imposes.

**Evidence.**
- Opus 4.6: 94.85% on the public games with tools and readable source (official 0.5% as reference).
- Local models: 0.08–0.20 → 31.82 on hidden games, as authority, tokens and context were granted to stronger models.
- Every scored imposed-decision intervention fell below the copy mean.

**Falsifier.** A powered, paired run on the competition stack in which an imposed-decision arm (forced reasoning step, goal menu, executor) beats the same model given only more affordance (tokens, context, time) at equal cost.

**Not claimed.** That source access is legitimate competition play; we disclosed it in April and said in June it could not run there. It demonstrates the principle, not a method.

## 7. Conclusion

Start with a strong model. Give it a medium it speaks, compute, context, time, and memory of its own lessons. Then let it decide. In April this took Claude Opus 4.6 to 94.85% on the public games with a method it chose itself; in the competition, prominent agents and our best notebook use the same paradigm. Harness that granted capacity helped; harness that decided for the model did not. The practical rule for agent builders: **affordance is all you need, once the model is strong enough to use it.**

*Code, notebook (submission 57374159), receipts and third-party licences: https://github.com/dp-web4/arc-sage/tree/main/paper-track-2026 (our additions CC-BY-4.0). Leaderboard review: github.com/arcprize/ARC-AGI-Community-Leaderboard/pull/20.*
