# Receipts: public paths for every number in the writeup

This file traces each number in `WRITEUP_1500_cloud-claude_2026-11-03.md` to a file in this repository.

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

## Scored numbers (Kaggle public field, 0-100+ scale, one draw on the hidden set per row)

| Writeup claim | Public file | Label |
|---|---|---|
| Our harness 0.08–0.20 | `cover/scored.json`: ref 54948614 (v53, 0.20); ref 56809141 (v68, 0.08) | public |
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
