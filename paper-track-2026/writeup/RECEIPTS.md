# Receipts: public paths for every number in the writeup

This file maps claims in `WRITEUP_rev4.3_2026-11-05.md` (rows written for rev 4.1 still apply unless amended below) to public evidence where available, and identifies claims whose underlying records are private. A published excerpt is the team's report, not an independent verification of its underlying run data. The writeup is copied verbatim, so the qualifications here are not all stated in the text.

- **Built from:** cloud-claude's private receipts (`WRITEUP_1500_RECEIPTS_2026-11-03.md`, dp-web4/dev-SAGE at `162d86cd1`).
- **What changed:** that file cites private repositories. Here each citation points to one of these public files:
  - `cover/scored.json`: our 120 Kaggle submissions with their public scores;
  - `evidence/excerpts/`: the cited source lines, quoted verbatim with line numbers;
  - `analysis/`: the three-leaps analysis.
- **Rewritten by** thor-claude, 2026-11-03.

**Labels:**
- **public**: the number can be read directly in the cited file.
- **excerpt**: the cited lines are quoted here, but the full source file is private.
- **evidence private**: the underlying data (transcripts, run directories) is not published. The claim rests on our own report of it.

Paths are relative to `paper-track-2026/`.

## Current draft: Phase 1, score steps, and SAGE

| Draft claim | Evidence and limitations |
|---|---|
| Phase 1 public 94.85%, 23/25 games, 175/183 levels | [`../README.md`](../../README.md) and its [scorecard](https://arcprize.org/scorecards/c7dfb4f1-8642-4c9e-ab4d-152f5f8e33b4). The run used game engine source and replayed agent-generated action traces. |
| Phase 1 84.9% legacy and 92.82%; approximate $250 | [`../paper/ARC-SAGE-AGI-84-9.md`](../../paper/ARC-SAGE-AGI-84-9.md), header and abstract; $250 is the estimate in the April 15 report, not a verified final total through the later 94.85% scorecard. |
| Official Opus 4.6 0.5%, $8.9K | [ARC Prize leaderboard](https://arcprize.org/leaderboard). This is a semi-private evaluation, different from the Phase-1 public set and conditions. |
| 25/25 solvers by April 8 | The Phase-1 repository contains solvers; the April 8 chronology is a team report based on a private shared-context Git record. **Underlying chronology private.** |
| Frame-questioning wa30 L7 and re86 L8 | `../paper/ARC-SAGE-AGI-84-9.md` §3.2 records the team's account; the contemporaneous underlying records are private. |
| lf52 L7 exhaustive search and bp35 L5 geometry | Team reports in the private Phase-1 day-17 record; **underlying search logs and geometry argument private**. No independent verification is claimed here. |
| Disclosure and leaderboard review | [Community leaderboard PR #20](https://github.com/arcprize/ARC-AGI-Community-Leaderboard/pull/20). The PR is a first-hand account of source discovery and solver writing, not an independent recreation of the process. |
| 0.12 → 1.17 and 2.18 → 24.82; intermediate 1.17 → 2.18 | `cover/scored.json` refs 56105013, 56836531, 56864492, 56894159, respectively. Ratios: 9.75×, 11.39× and 1.86×. The JSON is our copied score history. Different model, harness, context and serving changes prevent a single-factor attribution. |
| Rev 4.3: final 92.82 → 94.85 (+2.03) | Team report in the private Phase-1 day-17 record: completion of dc22 (71.4 → 100) and re86 (77.8 → 100; L1–L7 new plus an earlier L8 trace). **Underlying record private.** The wa30 L7 / re86 L8 frame-questioning examples are separate (Phase-1 paper §3.2). |
| Rev 4.3: steps 0.20 → 1.17 (5.9×) and 2.18 → 24.82 (11.4×) | `cover/scored.json`: 0.20 = ref 54948614 (v53, the organism era's best); 1.17 = 56836531; 2.18 = 56864492; 24.82 = 56894159. Observed steps; model, harness, context and serving changed together. |
| Rev 4.3: ≈$250 | Phase-1 paper estimate through the April 15 92.82% result; the April 15 table row was dropped in rev 4.3. |
| Selected 31.82 | `cover/scored.json` ref 57374159 and `evidence/excerpts/COMPETITION_RUN_LOG.md` line 51. One unreplicated selected result. |
| Copy mean 25.77 and SD 3.93 | `evidence/excerpts/DECISIONS.md` lines 984–987 describes unchanged public resubmissions of Franzen's notebook, not a measured distribution for our identity-modified notebook. Underlying study **private**. |
| Timing panel: 13 of 18 | `evidence/excerpts/DRAFT_v1.md` lines 276–282 describes 13 converted pre-classed STARVED rows in a small panel; the panel was not randomized per level. |

**Interpretation limits.** The official Opus score and Phase-1 score use different evaluation sets and conditions, and the latter replayed traces; their contrast does not isolate the effect of tools. The $250 estimate comes from the April 15 Phase-1 report; a total through the April 17 94.85% scorecard has not been independently reconciled. The copy mean and SD are from Franzen's public notebook, not a measured distribution of our identity-modified notebook. Three intervention scores contain stacked changes (note A below), so the named change's effect is not isolated. The goal gate was unused and therefore inert, not a test demonstrating that goal checking failed. These qualifications narrow causal readings of the paper's comparisons.

The tables below retain the prior draft's evidence index; rows that are not in the current draft are historical context rather than current claims. They include the scored intervention and small-panel receipts used by this draft.

## Scored numbers (Kaggle public field, 0-100+ scale, one draw on the hidden set per row)

| Writeup claim | Public file | Label |
|---|---|---|
| Our harness 0.08–0.20 | `cover/scored.json`: ref 54948614 (v53, 0.20); ref 56809141 (v68, 0.08) | public examples, not a full minimum-to-maximum range: ref 56655811 (v60) scored 0.07, and other runs scored 0.00 |
| Duck on Qwen3.8-27B 1.17 | `cover/scored.json` ref 56836531 | public |
| 3× throughput 2.18 | `cover/scored.json` ref 56864492 | public |
| Flash-Next copy 24.82 | `cover/scored.json` ref 56894159 | public |
| Best 31.82 (selected submission 57374159) | `cover/scored.json` ref 57374159; `evidence/excerpts/COMPETITION_RUN_LOG.md` line 51 | public |
| Final 26.04 (one run, four stacked changes) | `cover/scored.json` ref 57911309; `evidence/excerpts/COMPETITION_RUN_LOG.md` line 23 | public. The private-set score is `?` until Kaggle publishes it |
| Base alone 29.69 | `cover/scored.json` ref 57747094 | public |
| Text-only goal audit 24.89 | `cover/scored.json` ref 56979852; run log line 61 | public |
| Franzen-verify 19.22 | `cover/scored.json` ref 57026619; run log line 60 | public |
| Fine-tuning 16.06 | `cover/scored.json` ref 57088784; run log line 58 | public |
| Forced world-model turn 18.14 | `cover/scored.json` ref 57819070; run log line 26 | public, with a caveat (see note A) |
| Lower reasoning effort 9.62 | `cover/scored.json` ref 57668634; run log line 41 | public, with a caveat (see note A) |
| Thinking off on routine turns 11.48 | `cover/scored.json` ref 57784941; run log line 27 | public, with a caveat (see note A) |

**Note A (thor-claude, found while tracing these receipts).** The run-log rows quoted in the excerpt describe these three runs as stacked changes:
- **18.14:** the forced world-model turn plus a combined code patch.
- **9.62:** GOALPRIOR v1 plus low reasoning effort.
- **11.48:** thinking off plus adaptive effort v3.

The writeup's table names only the first change of each. The scores are as stated; their attribution to one change is not isolated. This was reported to the writeup's editor and was not changed here, because the writeup is a verbatim copy.

## Spread and attribution

| Writeup claim | Public file | Label |
|---|---|---|
| Copy band 25.77, SD 3.93 per run (hundreds of unchanged public resubmissions) | `evidence/excerpts/DECISIONS.md` lines 984-987 | excerpt. The underlying M2 stack study is **evidence private** |
| 31.82 is an unreplicated maximum of ~20 runs; two-draw SD ≈ 5.5 | `evidence/excerpts/COMPETITION_RUN_LOG.md` line 23 | excerpt |
| Paired Thor draw within draw noise (0.7 SD) | `evidence/excerpts/FORUM_thor-claude-research-loop-final-pair-in-its-field-2026-11-03.md` | excerpt. The per-arm run data is **evidence private** |
| Model-only swap in our harness: 1.46 vs 0.86 on the one outcome-matched game | `evidence/excerpts/SUBSTRATE_AB_2026-09-19.md` lines 156-169 | excerpt |
| 108 → 330 tok/s | `evidence/excerpts/DECISIONS.md` lines 864-872 | excerpt |
| Harness patch ported to the 27B: no lift (5 / 1.24 vs 8 / 1.86, 30-min smoke) | `evidence/excerpts/DECISIONS.md` lines 890-897 and 920-925 | excerpt |
| Flash-Next at 32k 5.6 locally vs 16–38 at 128k | `evidence/excerpts/FORUM_thor-claude-reply-arc-reviews-2026-11-01.md` | excerpt (local bench) |
| ≈1.2× at matched generated tokens (Thor, 4 games) | `evidence/excerpts/FORUM_thor-claude-re-three-leaps-27b-pair-2026-11-02.md` | excerpt. The `RESULT.json` files are **evidence private** |
| Decision path ~27k lines (ours) vs ~4.5k (Duck) | `analysis/ARC_HARNESS_AB_THREE_LEAPS_2026-11-02.md` §2 | our count. The Duck tree is public (Tufalabs/duck-harness@7652836); our v68 tree is **evidence private** |
| Executors chose 49–109 actions per game with no model decision (ka59, cd82, wa30) | `evidence/excerpts/DECISIONS.md` lines 706-710 | excerpt |
| Proxy 14.5 vs 4.92; scored 0.08 vs 1.17 | `evidence/excerpts/DECISIONS.md` lines 706-710 and 749-753; `cover/scored.json` | excerpt + public |

## Failure modes, interventions, taxonomy

| Writeup claim | Public file | Label |
|---|---|---|
| 19–37% of wall-clock to turns that never acted | `evidence/excerpts/DECISIONS.md` lines 873-875 | excerpt. Transcripts are **evidence private** |
| Turn-anchor gauge: 0 firings at 128k | `evidence/excerpts/DECISIONS.md` lines 984-986 | excerpt |
| Clock line: 9 → 37 real-time-mechanics reasoning lines | `evidence/excerpts/DRAFT_v1.md` lines 162-168 | excerpt (n=1). Transcripts are **evidence private** |
| Instrument failures: "absence read as a negative" and "a process checker that matched itself" | — | **evidence private**: internal method notes, not excerpted |
| Instrument failure: a fix credited while firing 0 times | `evidence/excerpts/DECISIONS.md` lines 984-987 | excerpt |
| Instrument failure: non-production serving path, 354 s per call, read as "model capability is not the blocker" | `evidence/excerpts/SUBSTRATE_AB_2026-09-19.md` lines 14-30 and 117-120; `evidence/excerpts/THE_HARNESS_IS_THE_BLOCKER_2026-09-19.md` | excerpt |
| "over 30× faster on the competition stack" | `analysis/ARC_HARNESS_AB_THREE_LEAPS_2026-11-02.md` §4 item 1 | inference in our analysis, not a measured ratio |
| Offline goal-gate pilot: `plan_check` intended 11×, called 0× in 160 armed turns; <20 calls = inert, not measured | `evidence/excerpts/DRAFT_v1.md` lines 340-348; run log line 60 | excerpt. The census is **evidence private** |
| Fine-tuning: held-out likelihood improved, leave-families-out play 57 → 34 levels | `evidence/excerpts/DRAFT_v1.md` lines 372-388 | excerpt. The P1-T verdict files are **evidence private** |
| Doubling the clock converted 13 of 18 pre-classed stalls | `evidence/excerpts/DRAFT_v1.md` lines 276-282 | excerpt |
| Estimated score by reasoning tokens: 100k → 27.7, 300k → 56.6 (one 10-h local trace, truncated) | `evidence/excerpts/FORUM_thor-claude-budget-axis-is-tokens-fp4-starvation-2026-10-29.md` | excerpt. The trace and `tokcurve.py` are **evidence private** |
| su15: 20/24 variant runs cross | `evidence/excerpts/DRAFT_v1.md` lines 258-264 | excerpt |
| Taxonomy 6 GOAL / 1 TRANSITION / 0 exploration-bound, n=7 | `evidence/excerpts/DRAFT_v1.md` lines 565-572 | excerpt. The quote-level reads are **evidence private** |
| 149 of 204 goal proposals could not be bound | `evidence/excerpts/PRIORS_BEFORE_OUTSIDE_ZAP_2026-09-06.md` | excerpt. The private receipt cited a different private file. This excerpt is the original measurement note |

## Context claims

| Writeup claim | Public file | Label |
|---|---|---|
| April 2026: agent-written solvers 94.85% on the public set, using engine source | top-level `README.md` of this repository (public scorecard link) | public |
| Franzen's Milestone-2 notebook is our scored base; Duck lineage | `notebook/arc-agi-3-lean-capnudge-dprime-identity.ipynb` cell 0; `notebook/THIRD_PARTY_NOTICES.md` | public |
| Arcgentica predates agent-written solvers | — | external, not receipted here |
| Licence footer (our additions CC-BY-4.0) | `evidence/rules/rules.md` §1.6, §2.5; `evidence/NOTEBOOK_LICENCE_RECOMMENDATION.md` | public. The wording is pending dp's review (see `README.md`) |

**Interpretive claims** (§6 theory, both predictions) are labelled as interpretation in the writeup and carry no receipt.
