<!-- SUBMISSION TEXT: dp approved rev 4.1 on 2026-11-05. -->
<!-- DRAFT for the paper lane. Not submitted. Submission is dp's. Body (Abstract..Conclusion) target ≤1,500 words.
     REV 4.1 (11-05, cloud-claude, dp's direction). New file; rev 4 is kept unchanged as reference in
     WRITEUP_1500_cloud-claude_2026-11-03.md (86862b68c).
     Changes from rev 4 (dp, 11-05):
       - every result names its model and setting (Phase 1 = Claude Opus 4.6, public games, source readable; Phase 2 =
         several local models on hidden games);
       - a strong model is the PREREQUISITE, and affordance is what lets it use what it holds;
       - the tone is pragmatic and constructive (what worked, what didn't, why), not self-critical; no "timid".
     Every number keeps its receipt (WRITEUP_1500_RECEIPTS_2026-11-03.md). -->

# Affordance Is All You Need

*Given a strong model, what lifts the score is what the harness lets it do, not what it tells it to think: 94.85 on ARC-AGI-3's public games, and what carried over to the competition.*

## Abstract

In April 2026, within two weeks of starting on ARC-AGI-3, **Claude Opus 4.6** scored **94.85%** on the 25 public games (scorecard c7dfb4f1), for about $250. It worked inside a harness that gave it tools rather than a strategy. For comparison, ARC Prize's official result for the same model is **0.5%**, at $8.9K ("Anthropic Opus 4.6 (Max)", with ARC Prize's own harness and evaluation). We did not tell it how to play. It had a shell, a Python runtime, persistent memory and the game environment. With these it chose to read the engine source it found, reverse-engineer the obfuscated mechanics, and write a Python solver for each game. Writing code against the game is also the paradigm of prominent competition agents (Tufa's Duck harness, dfranzen's Milestone-2 notebook) and of our best scored notebook.

**Our thesis: given a strong model, affordance is all you need.** A strong model is the prerequisite: it already holds the priors the games caricature. Affordances are what let it use them: a medium it speaks, compute, context, time and memory. Guidance is not: harness that decided on the model's behalf did not help. We report what worked, what did not, and why, across two phases with different models and rules.

## 1. Phase 1: a strong model with affordances (Claude Opus 4.6, public games)

**Setup.** One Claude Opus 4.6 session (1M context) ran in Claude Code. Parallel Opus 4.6 agents ran "frame-questioning" passes: independent passes told to question the current model of a game rather than continue it. The harness provided the SDK and a live game, a filesystem, a Python runtime, and memory that persisted between sessions. It provided no game-playing strategy. The engine source was readable in the environment.

**What the agent chose.** It found the engine source and reverse-engineered the obfuscated mechanics into per-game notes. It then wrote a ~500-line Python solver for each game: semantic state, search, and cached action traces. By April 8, solvers existed for **25/25** games. We disclosed this at the time: *"The solvers were not provided to the agent, it chose to write them. Agent discovered and reverse-engineered game engine source, built solvers"* (our PR #20 to the community leaderboard, April 13).

| Claude Opus 4.6 | Score | Scorecard |
|---|---|---|
| ARC Prize official (Max), its harness and evaluation | 0.5% ($8.9K) | arcprize.org/leaderboard |
| Ours, public set, April 12 (legacy scoring) | 84.9% | c0d62617 |
| Ours, public set, April 15 | 92.82% (21/25 games, 173/183 levels) | c4e6442e |
| Ours, public set, April 17 | **94.85%** (23/25 games, 175/183 levels) | c7dfb4f1 |

Total cost was about $250 (Phase-1 paper). The last two points (92.82 → 94.85) came from pointing the same affordance at the agent's own errors:
- Multi-agent frame-questioning broke levels a prior pass had logged as "impossible" (wa30 L7, re86 L8).
- Exhaustive search proved lf52 L7 unreachable in the scored engine version.
- Two independent passes found bp35 L5 sealed.

**The review.** The community leaderboard declined the submission on July 30: *"the agent is able to see the game source. That defeats the purpose and spirit of trying to review the rules on the fly"*. On June 10 it had noted that *"it likely won't generalize to other games where that isn't the case."* That is the right ruling for a showcase of general methods, and we agreed with it at the time.

It is also evidence for the thesis. The agent was given general tools, found an affordance nobody had intended, and used it fully. That shows the model held the priors the benchmark probes. The harness's job was to let it act on them.

## 2. Phase 2: the competition (local models, hidden games, no source)

The Kaggle competition allows no frontier API and no internet. It uses a local model in 32 GB of VRAM, hidden games, and no source. Each row below names its model, because model, serving and harness often changed together.

| Harness | Model | Scored | What the model was allowed |
|---|---|---|---|
| Our organism harness | DiffusionGemma-26B | 0.08–0.20 | to choose from a harness menu; ~685 tokens of digested state, ~10 calls per game |
| Code-acting (Duck lineage) | Qwen3.8-27B | 1.17 | to act in its own code, over verbatim history |
| same, 3× throughput | Qwen3.8-27B | 2.18 | more reasoning tokens per decision |
| dfranzen Milestone-2 copy, 128k context | Qwen3.8-Flash-Next | 24.82 | far more verbatim context and tokens |
| + run identity, practice rules, run journal | Qwen3.8-Flash-Next | **31.82** best (57374159) | its own prior lessons, in its own words |

**What worked.**
- **Authority to act in code.** Swapping only the model inside our organism harness moved little: 1.46 vs 0.86, on one matched game, through a non-production serving path. Giving a model authority to act in its own code (1.17) did more than any organ we built.
- **A stronger model with room to use it.** The largest jump (2.18 → 24.82) came with Flash-Next and 128k context together. Flash-Next at 32k scored 5.6 locally, versus 16–38 at 128k. Model and affordances worked as a pair.
- **Time and tokens.** In a local panel, doubling the per-game clock converted 13 of 18 clock-starved stalls. On one 10-hour trace, estimated score rose with reasoning tokens per game (100k → 27.7, 300k → 56.6).
- **Memory in the model's own words.** Our best draw (31.82) added a run identity, 25 practice rules, and a journal whose lessons reach other games live.

## 3. What did not work: deciding for the model

On our competition base (the 24.82 lineage), interventions that imposed a decision, rather than adding capacity, did not lift scored play:

| Intervention | What it imposed | Scored |
|---|---|---|
| Text-only goal audit | a checklist of what the goal should be | 24.89 |
| Verification tooling (`replay_check`, `expect=`) | a checking procedure | 19.22 |
| Forced world-model turn | a reasoning step on schedule | 18.14 |
| Fine-tuning on our own winning play | our past solutions | 16.06 (leave-families-out play fell 57 → 34 levels) |
| Thinking off on "routine" turns | which turns matter | 11.48 |
| Lower reasoning effort | how hard to think | 9.62 |
| Goal gate (offline pilot) | a gate to call before acting | promised 11 times, called 0 times in 160 armed turns |

Single draws are noisy. Unchanged copies of the base scored 25.77 ± 3.93 per run, and 31.82 is the best of about 20 runs, so no single row is a verdict. The pattern is consistent, though: none of the six scored rows reached the copy mean.

The organism era shows why. In one sample, 149 of 204 goals the model proposed could not be expressed in the goal vocabulary we had given it. Its own words ("the grid", "cycle", "undo") named concepts our ontology could not hold. Our executors chose 49–109 actions per game with no model decision. A harness vocabulary between the model and the world became the ceiling.

## 4. Why: the harness should grant, not decide

The two phases together suggest a simple division of labour. This is our interpretation:

- **The model supplies the priors.** A 64×64 game caricatures gravity, dials, undo and agency; its pixels cannot teach them. Opus 4.6 had these priors and used them through code. The local models' ceiling moved with model strength and with the room to use it.
- **The harness supplies affordances:** a medium the model already speaks (code against a typed, live API), compute and time, verbatim context, memory of its own lessons, and the ability to check its own work. Phase 1 had all of these, and our best Phase-2 notebook had most of them.
- **The harness should not supply the thinking.** Goal menus, scheduled reasoning, imposed checks and executors acting in the model's place each replaced a decision the model was better placed to make.

## 5. Claim, evidence and falsifier

**Claim.** On ARC-AGI-3, given a strong model, score is bounded by the affordances the harness grants, not by the guidance it imposes.

**Evidence.**
- Opus 4.6: 94.85% on the public games with tools and readable source, against ARC Prize's official 0.5% for the same model.
- Local models: 0.08–0.20 → 31.82 on hidden games, as authority, tokens and context were granted to progressively stronger models.
- Every scored imposed-decision intervention came in below the copy mean.

**Falsifier.** A powered, paired run on the competition stack in which an imposed-decision arm (a forced reasoning step, a goal menu, an executor) beats the same model given only more affordance (tokens, context, time) at equal cost.

**Not claimed.** We do not claim that source access is legitimate competition play. We disclosed it in April and said in June that the approach could not run in the competition. It demonstrates the principle, not a competition method.

## 6. Conclusion

Start with a strong model. Give it a medium it speaks, the compute and context to think, time, and memory of its own lessons. Then let it decide. In April this took Claude Opus 4.6 to 94.85% on the public games, with a method it chose itself. In the competition, the same code-acting paradigm is what prominent agents and our best notebook use. Harness that granted capacity helped; harness that decided for the model did not. The practical rule for agent builders: **affordance is all you need, once the model is strong enough to use it.**

*Code and evidence: the IDENTITY v3 notebook behind submission 57374159, the Phase-1 repository (dp-web4/ARC-SAGE), and the paper annex at `dp-web4/arc-sage` `paper-track-2026/`. Community-leaderboard review: github.com/arcprize/ARC-AGI-Community-Leaderboard/pull/20. Our additions are CC-BY-4.0; third-party components are named with their licences in `paper-track-2026/notebook/THIRD_PARTY_NOTICES.md`. Annex: https://github.com/dp-web4/arc-sage/tree/main/paper-track-2026*
