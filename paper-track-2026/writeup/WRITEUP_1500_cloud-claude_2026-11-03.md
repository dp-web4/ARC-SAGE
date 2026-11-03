<!-- DRAFT for the paper lane (thor-claude / kimi / codex red-team). Not submitted. Submission is dp's.
     Body (Abstract..Conclusion) target ≤1,500 words. Numbers are from DRAFT_v1 (thor/qwen-substrate), the
     ship run log, thor-claude's 11-01 Thor pair, and dp's final score (11-03). Every interpretive claim is labelled.
     REV 2 (11-03, cloud-claude): applies codex red-team findings 1-7 (forum codex-arc-writeup-redteam-first-findings-2026-11-03)
     and thor-claude's postmortem input; licence footer per NOTEBOOK_LICENCE_RECOMMENDATION.md. Not a sign-off: codex's
     all-claims audit continues. -->

# Where the fluid step fails: a local agent on ARC-AGI-3, and what the harness changed

*Subtitle: Harness failure modes, a goal-failure taxonomy, and an attribution of a 300× score change*

## Abstract

The ARC Prize asks for an AI capable of fluid intelligence. We report a small case study of a competition-legal local agent on ARC-AGI-3. In a quote-level read of the **seven highest-burn game-levels** (a selected sample, coded by our team), six were failures to **pose the right goal for a novel world**, one was a failure to move from exploring to verifying, and none was bounded by exploration. That is a hypothesis about the system's dominant failure, stated with the selection behind it; that the model held the relevant priors is likewise an assumption.

**Results:**
- Our own harness of hand-built "organs" around a 26B model: 0.08–0.20.
- A Duck-lineage harness (the model writes Python against the live game) on Qwen3.8 models: 1.17, then 2.18, then 24.82; with our additions, a best public 31.82.
- Our final score was **26.04**: one run of four stacked changes. We did not isolate a reliable effect of our additions, in either direction.

**Contributions:** three measured harness failure modes, each with a fix and a gauge showing the fix fired; the goal taxonomy; registered interventions that did not lift (answers as text, fine-tuning on our own play, optional verification tools); and an attribution of the score jumps that separates what was isolated from what was not.

## 1. Introduction

ARC-AGI-3 games caricature physical and social worlds: dials, gravity, undo, agency transfer. Our working hypothesis: the priors needed to read them cannot be learned from one episode's pixels; they must already be in the model and be activated by context.

We spent seven months building cognition *around* a model. The score history shows which harness choices mattered. Two findings concern the experimenter, not the agent.

## 2. Prior work

- **Agent-written solvers.** In April 2026 a frontier model writing its own Python solvers reached 94.85% on the public set, using the obfuscated engine source (disclosed; the community leaderboard declined it). REPL agents predate this (Arcgentica).
- **The competition box.** Tufa's Duck and dfranzen's Milestone-2 notebook brought the paradigm to local models; Franzen's notebook is our scored base.

## 3. Approach and attribution

n=1 per scored row.

| Step | Score | What changed | What isolated part of it |
|---|---|---|---|
| Our organism harness (DiffusionGemma-26B) | 0.08–0.20 | — | — |
| → Duck on Qwen3.8-27B | 1.17 | The model decides every action in its own code over verbatim history, instead of choosing from a harness-built goal menu. The model and serving also changed. | Swapping only the model inside our harness: 1.46 vs 0.86 on the one outcome-matched game, through a non-production serving path. Not a population bound |
| → same, 3× throughput | 2.18 | Context/concurrency and MTP decoding: 108 → 330 tok/s | Throughput only; the UNDO patch rode along |
| → Flash-Next copy | 24.82 | Model, quantization, engine, 128k context, scheduler, harness patch | Harness patch ported to the 27B: no lift. Flash-Next at 32k: 5.6 locally vs 16–38 at 128k. At matched generated tokens, Flash-Next ≈ 1.2× the 27B (Thor, 4 games) |

**Never isolated:** a minimal driver on our original model; Flash-Next vs 27B at matched tokens on Kaggle; SGLang vs vLLM. We therefore do not assign causal shares.

**What the record does support:**
- Our decision path between model and game was ~27k lines; the Duck's is ~4.5k.
- On three named v68 games, executors in our harness chose 49–109 actions without a model decision.
- On a local public-game proxy our harness led (14.5 vs the Duck's 4.92). Scored on hidden games, the order reversed (0.08 vs 1.17). Our interpretation, not an ablation: the proxy rewarded seen-game behaviour.

## 4. Measured failure modes (competition-legal stack)

1. **The agent loses its own situation.** At a 32k window, mid-turn trimming evicted the turn's opener. The model concluded "a previous agent already acted", and 19–37% of wall-clock went to turns that never acted. The fix is a turn anchor; its gauge shows 0 firings at 128k.
2. **Harness facts read as world facts.** A bare clock line seeded real-time-mechanics theories in a turn-based world (9 → 37 reasoning lines) until the line stated its origin.
3. **Instruments failed toward our hypotheses:** absence read as a negative; a process checker that matched itself; a fix credited while firing zero times; and a model comparison run through a non-production serving path (354 s per call), read as "model capability is not the blocker". That model family later ran over 30× faster on the competition stack.

## 5. Results

**What was registered before reading** (scored rows are single draws; per-run SD ≈ 3.9, so a two-draw gap has SD ≈ 5.5):

| Intervention | Outcome |
|---|---|
| Text-only goal audit | 24.89, one draw: inconclusive |
| Franzen-verify (`replay_check` + `expect=` verification) | 19.22, one draw |
| Offline goal-gate pilot (separate experiment, not scored) | a goal-referenced `plan_check` was promised 11 times and called 0 times in 160 armed turns. Registration needed ≥20 calls, so: **inert, not measured** (uptake, not efficacy) |
| Fine-tuning on our own winning play | 16.06. Held-out likelihood improved, but leave-families-out play fell from 57 to 34 levels |
| Forced world-model turn | 18.14 |
| Lower reasoning effort | 9.62 |
| Thinking off on routine turns | 11.48 |

**What helped or held, locally:**
- **Time converts depth:** doubling the per-game clock converted 13 of 18 pre-classed clock-starved stalls.
- **Estimated score tracks reasoning tokens per game:** 100k → 27.7, 300k → 56.6. Retrospective: each game's clears in **one** 10-hour local trace truncated at token thresholds, under our scorecard assumptions. Not controlled runs; not causal.
- **Priors activate on fresh layouts:** on generated variant levels, two "universal walls" fell (su15: 20/24 runs cross).

**Goal taxonomy** (n = 7, the highest-burn game-levels, selected by burn; categories and adjudication are our team's coding):
- 6 GOAL failures: the run never acts on a correct win condition;
- 1 explore→verify TRANSITION failure;
- 0 exploration-bound failures.

In this sample, contradiction latency, not error rate, separated failing from clearing runs: the disconfirming evidence was on the board or in the run's own output. Clearing runs verified against a goal-state surrogate; failing runs verified predictions.

**Final.** 26.04: one run of four stacked changes over a base that scored 29.69 alone. Hundreds of unchanged public resubmissions of the copied notebook scored 25.77, SD 3.93 per run: the spread of single draws, not a treatment-effect interval. So 26.04 shows neither that our additions did nothing nor that they hurt. Our best, 31.82, is an unreplicated maximum of ~20 runs. One paired 30-minute local draw pointed lower; against 14 arms' spread it is within draw noise (0.7 SD).

## 6. Theory (interpretation, with falsifiable predictions)

We read the goal taxonomy through one frame: **a goal is a question with a success predicate, and relevance is defined by the open question**. Evidence off the open question goes unseen: on this reading, that is the contradiction latency we measured.

On this reading, the operational core of the fluid step here is question formation under novelty ("what does winning mean here?", "what is this a caricature of?"). This interprets a small case study; it does not claim perception is solved (our measurements show it is not).

**Harness consequence (our hypothesis).** A harness can make the fluid step affordable and cheap to check, and it can suppress it. We have not seen one supply it, though these experiments cannot rule that out:
- **Affordable:** compute, verbatim context, allocation across games.
- **Cheap to check:** goal predicates evaluable from the model's side, signals labelled with their origin.
- **Suppresses it:** our harness handed the model a vocabulary of goals; in an organism-era sample, 149 of 204 of its own goal proposals could not be bound to it. A measured binding failure; whether those goals were correct was not measured.

**Predictions (untested here):**
- Making goal hypotheses first-class objects with cheap predicate checks should cut contradiction latency.
- Answers injected that the agent has not asked for should not lift scored play. We isolated no lift at any entry point we registered; a paired, powered run where unrequested hints raise hidden-set depth would falsify this.

## 7. Conclusion

The largest score jumps coincided with giving a capable model room: authority to act in code, compute, and context. Models and serving changed at the same steps; we assign no causal shares. We did not isolate a reliable effect of our own later additions. We offer the anatomy of where this agent lost, the failure modes with their gauges, and a warning: **the experimenter's instruments fail in the direction of the experimenter's hypothesis.** Check them against the shipped substrate and an unseen-task proxy first.

*Code: the scored notebook behind the selected submission. Our additions are CC-BY-4.0; third-party components are named with their licences. Full paper: PDF link.*
