# Excerpt: `DECISIONS.md`

- Source: dp-web4/dev-SAGE (private), `kaggle/harness/ship/DECISIONS.md` at commit `162d86cd1`.
- Each block quotes whole source lines, unedited, with their line numbers. Lines outside these ranges are not published here; the full file stays private.

## Lines 706-710: executors chose 49-109 actions per game (ka59, cd82, wa30) with no model decision; v68 proxy 12.3 -> 14.5 = scaffold

```text
  706  
  707  ## 2026-10-03 ~04:45 UTC: v67 and v68 VIOLATE the 09-24 rule "the scaffold works at cognition's pleasure" (thor-claude, caught by dp)
  708  - **What happened:** the agency, copy, carry and demonstration organs are EXECUTORS (`SAGE_*_EXEC=1`, default ON
  709    since c22e947b). In the v68 arms they chose 49–109 actions per game in ka59, cd82 and wa30 with no model decision.
  710  - **So the 12.3 → 14.5 proxy gain is the SCAFFOLD playing, not the model.** It must not be read as cognition.
```

## Lines 749-753: Duck on Qwen3.8-27B, Thor token-parity dojo: mean 4.92

```text
  749  ## 2026-10-03 23:20 UTC: the duck on Qwen3.8-27B, measured on Thor (thor-claude)
  750  - **45-min baseline:** mean 0.70; 3 levels.
  751  - **Token-parity dojo (5 h per game, turn budget off):** mean **4.92**; **13 levels across 9 of 14 games**.
  752    - ft09 4 levels (47.6), su15 L0 and bp35 L0 (never cleared by the scaffold), cd82 ×2, lp85, r11l, sb26, tu93.
  753    - Every action was chosen by the model (the 09-24 rule holds by construction).
```

## Lines 864-872: throughput: job wall clock 108.25 (v8) -> 263.55 (fast) -> 329.84 (fast-MTP) tok/s

```text
  864  - **23:05 UTC — denominators (thor-codex caught it).** My tok/s figures above are vLLM's sampled "generation
  865    throughput" mean while requests ran. The harness's own job-wall-clock rate (summary.txt `generated tokens/sec`):
  866    | arm | vLLM sample mean | job wall clock | x v8 (job) |
  867    |---|---|---|---|
  868    | v8 (65k, 14 conc, 490 min/game) | ~120 | 108.25 | 1.0 |
  869    | fast (32k, 20 conc) | 287.6 | 263.55 | 2.4 |
  870    | fast-MTP | 414.8 | 329.84 | 3.0 |
  871    | Franzen-MTP v2 | 447.4 | 268.84 | 2.5 |
  872    "About 3x the reasoning per scored game" is INFERRED (rate x per-game time), not measured on the scored set. The
```

## Lines 873-875: turn anchor: 37% (Franzen-MTP) and 19% (fast-MTP) of wall-clock lost to final turns that never acted

```text
  873    Franzen gap between the two meters (447 vs 269) is unexplained; under investigation (ARM_READING_1004.md).
  874  - **23:55 UTC — 10-08 target: the turn anchor.** ARM_READING_1004.md (transcripts, measured): Franzen lost 37% of
  875    wall-clock (fast-MTP 19%) to final turns that never acted; the mid-turn trim popped the turn's opener (current
```

## Lines 890-897: harness ported to the 27B: Franzen-MTP 5 levels / 1.24 vs fast-MTP 8 / 1.86 (30-min smoke)

```text
  890    Anchor smoke (kernel arc-agi-3-duck-qwen38-anchor v1, duck 267b7b1): gate `14 none`; per arm (n=1, 14 games x 30 min):
  891    | gauge | Franzen-MTP | anchor | fast-MTP |
  892    |---|---|---|---|
  893    | turn opener lost | (34 bare nudges) | 0 (41 compactions fired) | (8 bare nudges) |
  894    | finish_reason length | 27 | 3 | 9 |
  895    | games with "previous agent acted" confusion | 6 | 0 | 0 |
  896    | levels / mean score | 5 / 1.24 | 8 / 2.39 | 8 / 1.86 |
  897    | tok/s job wall clock | 268.8 | 327.6 | 329.8 |
```

## Lines 920-925: 10-05: copy of Franzen M2; "the model and serving stack were the missing piece"

```text
  920    levels; otherwise decide then. Seat: thor-claude
  921  - **19:30 UTC 10-05 — THE BIG LEVER: copy Franzen's public M2 notebook (27.9 on the private set, 24x our 1.17).**
  922    dfranzen/arc-agi-3-milestone-2-solution v3 = the Duck harness + his patch + **Qwen3.8-Flash-Next W4A16 (Intel
  923    AutoRound) + an MTP drafter, on SGLang ("pennyroyal" wheelhouse)**, a 136k context, 10 concurrent requests, all
  924    games admitted with priority scheduling. Every input is public (2 datasets, 2 models). Codex had ported his harness
  925    mechanisms onto OUR model and server; the model and serving stack were the missing piece.
```

## Lines 982-987: copy band: hundreds of unchanged public resubmissions, mean 25.77, SD 3.93; anchor fired 0 times

```text
  982    gate otherwise. Next smokes: set ARC3_MAX_ACTIVE_STREAMS >= games in the NON-submission branch so arms are measured
  983    without the admission cliff. Seat: thor-claude
  984  - **05:00 UTC 10-06 — RETRACTION of the 04:10 attribution.** In the anchor arm, `turn_anchor_compaction` fired **0**
  985    times (21 transcripts), `turn_anchor_lost` 0, finish_reason length 2. The patch applied but never acted, so the two
  986    arms were behaviourally identical and **40 vs 28 levels is run-to-run noise**. The M2 study (blackbox/runs/
  987    M2_STACK_STUDY_1006.md): hundreds of unchanged public resubmissions of Franzen's notebook scored mean 25.77, SD 3.93.
```
