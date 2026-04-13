# Capture Convention

**A solver that doesn't produce replayable visual memory isn't done.**

The data is the deliverable, not the win. A solve we can't replay is a parlor
trick — proof the engine can be beaten, but no transferable record of how.
The whole approach (Phase 2 Gemma integration, membot cartridge binding, the
"world model per game" thesis) depends on being able to replay any game at any
time, frame by frame.

## What "replayable" means

Every solved level produces a directory:
```
knowledge/visual-memory/{game}/run_{YYYYMMDD_HHMMSS}/
  run.json              # manifest: game_id, player, win_levels, steps array
  step_0001_L0_{ACTION}.png
  step_0002_L0_{ACTION}.png
  ...
  step_NNNN_L{lv}_{ACTION}.png
```

Where each step PNG shows the frame AFTER that action executed. The run.json
step array lets the viewer reconstruct the full play trajectory.

## How to capture

Use `SessionWriter` from `arc_session_writer.py`. The cleanest pattern is
shown in `capture_visuals.py` with its `ClickCollector`:

1. Run the solver with `env.step` monkey-patched to collect (action, data)
   tuples into a list.
2. After the solver completes, construct a fresh Arcade environment and
   replay the collected tuples through `env.step`, passing each to
   `sw.record_step(action, grid, ...)`.

This two-phase approach works with any solver because it doesn't require
the solver itself to know about capture — the wrapper handles it.

```python
from capture_visuals import ClickCollector, replay_with_capture

# Phase 1: Run solver, collect actions
env = arcade.make(game_id)
fd = env.reset()
collector = ClickCollector(env)
collector.patch()
run_solver(env, fd)
collector.unpatch()

# Phase 2: Replay with capture
replay_with_capture(game_id, collector.captures, label="my-solver")
```

## What NOT to do

### Don't save single snapshots per level
The `L0_start.png` / `L0_solved.png` flat layout is **not replayable**. Two
frames per level can't reconstruct the action sequence between them. These
also suffer from the post-transition bug (solved frame shows next level's
start). Acceptable only for interactive debugging, never as the deliverable.

### Don't skip capture for "partial" solves
Levels you didn't solve are just as informative as levels you did. Capture
everything the agent actually played — including failed attempts, stuck
states, exec_fail scenarios. These are the world-model learning signal.

### Don't roll your own frame-to-PNG
`SessionWriter.record_step` handles the palette, scaling, naming, and run.json
update. Using `PIL.Image.fromarray` in a solver means you're reimplementing
what already exists and will probably get the format subtly wrong.

## Verification

After your solver runs, the viewer at `http://localhost:8765/game/{game}/run_{timestamp}`
should show:
- Per-level start and solved frames (with -2 pre-transition logic)
- GIF animations where multi-frame actions produced intermediate states
- Correct level count matching game_coordination.json
- run.json fields: `result: WIN`, `levels_completed == win_levels`, `total_steps`

If the viewer's browse page shows your game with only `level-snapshots` (flat
layout) rather than a timestamped `run_` entry, capture is broken.

## Retroactive regeneration

Solvers written before this convention may not capture. `regen_flat_visuals.py`
has the infrastructure to replay them via the same ClickCollector pattern,
producing proper run directories. Run it for any game whose visual memory
shows as "level-snapshots" in the browse view.

## Convention summary

- Every solver → proper run_ directory with step-by-step frames
- No flat layouts in new work
- Use SessionWriter via ClickCollector pattern, don't reinvent
- Failed attempts count: capture everything actually played
- Verify via viewer before declaring done
