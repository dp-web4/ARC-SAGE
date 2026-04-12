# Replay Queue — Data Gaps in Early Solves

*Updated: 2026-04-12*

Some early game solves predate the visual memory / SessionWriter infrastructure. These games are "solved" in the coordination sense but lack the training data corpus needed for Gemma 4. They need to be replayed for data capture once priority work settles.

## Priority Order

### HIGH — Missing Visual Memory Entirely

These games have mechanics docs and coordination entries but **zero visual frames captured**. They need full replay for training data.

| Game | Levels | Solved Date | Solved By | Why It's a Gap |
|------|--------|-------------|-----------|----------------|
| sb26 | 8/8 | 2026-04-07 | CBP | Earliest solve, pre-infrastructure |
| vc33 | 7/7 | 2026-04-09 | CBP | Pre-SessionWriter |
| lp85 | 8/8 | 2026-04-07 | McNugget | Pre-SessionWriter |
| tn36 | 7/7 | 2026-04-09 | CBP | Pre-SessionWriter |
| g50t | 7/7 | 2026-04-11 | Sprout | Recent but no visuals captured |

### MEDIUM — Sparse Visual Memory

| Game | Levels | Visual Files | Status |
|------|--------|--------------|--------|
| bp35 | 9/9 | 13 | <2 frames per level, likely only start/end of a few levels. Also missing solutions JSON. |

### MEDIUM — Missing Solutions JSON (But Visuals Exist)

These have visual memory but no `{game}_solutions.json` file in SAGE/experiments. The solutions JSON isn't strictly required for training (the visual frames + action log are), but it's part of the expected artifact set.

| Game | Visuals | Notes |
|------|---------|-------|
| sp80 | 792 | Heavy visual capture, needs solutions JSON summary |
| su15 | 452 | Good visual capture, missing summary |
| ar25 | 1568 | Extensive visual capture, missing summary |

### COMPLETE — No Replay Needed

Games with full data corpus already captured:

| Game | Visual Files |
|------|--------------|
| cd82 | 44 |
| ft09 | 81 |
| tr87 | 144 |
| sc25 | 199 |
| s5i5 | 275 |
| ls20 | 345 |
| cn04 | 920 |
| tu93 | 4226 |

## Replay Protocol

When replaying a game for data capture:

1. **Verify SessionWriter is running** — visual memory capture must be enabled before starting
2. **Don't just re-run the solver** — the goal is frames, not solve speed. If the solver executes in 5 seconds, increase dwell time or run interactively to give the frame capture time to land
3. **Capture per-level state**: start frame, major action frames, final frame
4. **Record action sequences** — the `(frame_N, action, frame_N+1)` triples are the core training signal
5. **Update fleet learning JSONL** with replay entry (mark as replay-for-data, not original solve)
6. **Commit each level's replay immediately** — don't batch

## Solutions JSON Generation

For games missing solutions JSON (sp80, su15, ar25, bp35):
- Generate retrospectively from visual memory + coordination data
- Must describe verified runs, not BFS predictions
- Include per-level action counts, strategies, and key mechanics
- Reference visual memory directories

## Estimated Effort

- 5 games need full replay (sb26, vc33, lp85, tn36, g50t) — roughly the smallest / most algorithmic games, so replay is cheap
- 1 game needs partial replay (bp35) — visual gaps to fill
- 3 games need solutions JSON backfill from existing data (sp80, su15, ar25) — documentation work, no replay needed

Total: ~6 replay sessions + 3 documentation passes. Should fit in one full day across the fleet once current in-progress games (r11l, sk48, wa30, ka59, re86, m0r0, dc22, lf52) settle.

## When to Do This

- Not now — current priority is finishing live game-solving for the remaining 8 games
- After hardbound rollout completes, so replay commits carry per-machine attribution
- Before any model training begins — this is a prerequisite for usable training data

## Blocker

None. Replays can happen any time after current game-solving queue clears. Consider this a quality-completion phase, not an interruption of forward progress.
