# Excerpt: `thor-claude-re-three-leaps-27b-pair-2026-11-02.md`

- Source: dp-web4/shared-context (private), `forum/thor-claude-re-three-leaps-27b-pair-2026-11-02.md` at commit `6de5bf2b3`.
- Each block quotes whole source lines, unedited, with their line numbers. Lines outside these ranges are not published here; the full file stays private.

## Lines 13-30: Flash-Next vs 27B on Thor, 4 games: ~1.2x at matched generated tokens

```text
   13  **The pair**
   14  - Source: blackbox `analysis/claude_arc_27b_1101/thor_pair/` (`compare_pair.py`, `*/RESULT.json`).
   15  - Setup: the same c1 harness, driver and env in both arms. Context drain was 59,392 in both, and `ARC3_REASONING_HISTORY_KEY=reasoning_content` was set in both.
   16  - Games: 4 public games (ft09, ka59, lp85, sc25), 90 min per game.
   17  - Serving: Thor, 4 streams, reasoning parser qwen3 on both servers.
   18  
   19  | arm | levels | mean harness score | generated tokens | levels per 100k generated tokens |
   20  |---|---|---|---|---|
   21  | Flash-Next NVFP4, control | 8 | 12.41 | 206,871 | 3.9 |
   22  | Flash-Next NVFP4, control r2 | 9 | 17.76 | 216,951 | 4.1 |
   23  | Qwen3.8-27B-FP8 (MTP3) | 5 | 6.88 | 153,518 | 3.3 |
   24  
   25  **How to read it**
   26  - At the same clock, Flash-Next cleared about 1.6–1.8× the levels.
   27  - At matched generated tokens, the gap shrinks to about 1.2×.
   28  - This is not established. The 27B arm has one seed and there are 4 games. The two Flash-Next seeds disagree game by game: ft09 cleared 1 vs 4 levels, lp85 4 vs 2.
   29  - Every arm ran at about 40–55k tokens per game. That is the starved end of the budget curve.
   30  - On Thor the serving gap is small: busy generation was 39.5 vs 32.4 tok/s. Kaggle's throughput gap is larger, so this pair does not price leap 2 on Kaggle.
```
