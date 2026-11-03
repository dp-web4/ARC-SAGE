# Excerpt: `SUBSTRATE_AB_diffusiongemma_vs_qwen38_2026-09-19.md`

- Source: dp-web4/dev-SAGE (private), `kaggle/harness/results/SUBSTRATE_AB_diffusiongemma_vs_qwen38_2026-09-19.md` at commit `162d86cd1`.
- Each block quotes whole source lines, unedited, with their line numbers. Lines outside these ranges are not published here; the full file stays private.

## Lines 14-30: model-only swap inside our harness, same 4 games; 354 s per ask

```text
   14  ## 1. The headline
   15  
   16  **Same outcome. One third of the decisions. Zero deaths. 5.7x the cost per decision.**
   17  
   18  `ab_substrate.py` verdict: *"CLEAN A/B: one variable moved (the substrate), decision paths identical,
   19  both saw."* Same commit, same 4 games, same 9000 s wall, both bf16, both vision-enabled.
   20  
   21  | | DiffusionGemma | Qwen3.8-27B |
   22  |---|---|---|
   23  | levels cleared | **2** | **2** |
   24  | tu93 — actions to clear 2 levels | 95 | **73** |
   25  | tu93 — asks spent | 32 | **10** |
   26  | deaths (all games) | 2 | **0** |
   27  | asks in the wall | 86 | 24 |
   28  | s/ask | 62 | 354 |
   29  | wall actually used | 5371 s (ran out of GAMES) | 8484 s (ran out of TIME) |
   30  
```

## Lines 117-120: 354 s/ask buys ~90 asks across 110 private games

```text
  117    close to a finding at n=1. Everything else is a place to look. Two runs are two samples."*
  118  * Whether Qwen's action efficiency survives more turns — it never got enough to wander.
  119  * Whether Qwen is affordable. At 354 s/ask a 9-hour scored run buys it ~90 asks across 110 private games.
  120    **It cannot finish the set.** If the decision is "which substrate for the scored lane", this run argues
```

## Lines 156-169: correction: env score 1.46 vs 0.86 on the one outcome-matched game (tu93)

```text
  156  ## CORRECTION, same day: "levels 2 = 2" was not a tie
  157  
  158  Scored through the competition's own formula (`ladder.py`, read out of `arc_agi.scorecard`), tu93:
  159  
  160  | | levels | actions | vs human | per-level points | env score |
  161  |---|---|---|---|---|---|
  162  | DiffusionGemma | 2 | 95 | 2.7x | [16.0, 11.3] | **0.86** |
  163  | Qwen3.8-27B | 2 | 73 | 2.1x | [27.1, 19.2] | **1.46** |
  164  
  165  Per level: `min(((baseline/actions)**2)*100, 115)`, weighted by `level_index+1`. **Efficiency enters
  166  SQUARED**, so Qwen's 73 actions against Gemma's 95 on the identical clear is worth **1.7x**, not a tie.
  167  
  168  I reported a tie because I read the levels column. The score exists to measure mastery and mastery includes
  169  economy; the levels column cannot see it. This does not change the affordability conclusion — at 354 s/ask
```
