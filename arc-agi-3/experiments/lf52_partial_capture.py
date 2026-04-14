#!/usr/bin/env python3
"""Capture lf52 L1-L6 as replayable visual memory.

Prior frame-questioning concluded L7 is structurally unsolvable in the pinned
engine version (8 convergent passes). This script emits a run_ directory with
SessionWriter + updates the all-solutions cache in solutions.json.

Runs in one of two modes:
  - If knowledge/visual-memory/lf52/solutions.json exists, REPLAYS it directly
    (fast, deterministic, preserves any 0-OOB reorders applied to the cache).
  - Otherwise, runs the full solver (slow, fresh) and writes the cache.

The replay-first mode was added 2026-04-13 when L3 was re-ordered to eliminate
4 OOB clicks — the reorder relies on a piece-on-block push scrolling the
camera offset from (5,5) to (-19,5), turning previously-OOB col-12 clicks
into in-bounds (56,y) / (44,y) clicks. See game-mechanics/lf52.md "Session 9".

Usage: python3 lf52_partial_capture.py
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(__file__))

from arc_agi import Arcade
from arcengine import GameAction

MAX_LEVEL = 6  # L1-L6 only; L7 is structurally stuck in this engine version

VM = os.path.join(os.path.dirname(__file__), '..', '..',
                  'knowledge', 'visual-memory', 'lf52')
SOL_PATH = os.path.join(VM, 'solutions.json')

ACTION_MAP = {0: GameAction.RESET, 1: GameAction.ACTION1, 2: GameAction.ACTION2,
              3: GameAction.ACTION3, 4: GameAction.ACTION4, 5: GameAction.ACTION5,
              6: GameAction.ACTION6, 7: GameAction.ACTION7}


def run_from_cache(env, game, solutions):
    """Replay solutions.json end-to-end, yielding (action, data, fd) tuples."""
    trace = []
    for level_idx, steps in enumerate(solutions[:MAX_LEVEL]):
        print(f"\n=== L{level_idx+1}: replaying {len(steps)} cached steps ===")
        for step in steps:
            a = ACTION_MAP[step['action']]
            data = step.get('data')
            fd = env.step(a, data=data)
            trace.append((a, data, fd))
            if fd.levels_completed > level_idx:
                print(f"  L{level_idx+1} solved -> levels_completed={fd.levels_completed}")
                break
            if fd.state.name in ('WIN', 'GAME_OVER'):
                return trace, fd
        if fd.levels_completed <= level_idx:
            print(f"  FAILED at L{level_idx+1}; state={fd.state.name}")
            return trace, fd
    return trace, fd


def run_from_solver(env, game):
    """Solve fresh, returning (trace, fd)."""
    import lf52_solve_final as L
    trace = []
    _orig_step = env.step
    def traced_step(action, data=None, **kw):
        fd = _orig_step(action, data=data, **kw)
        trace.append((action, data, fd))
        return fd
    env.step = traced_step

    for level in range(MAX_LEVEL):
        print(f"\n=== Level {level+1} ===")
        fd = L.solve_level(env, game, level)
        if fd is None or fd.levels_completed <= level:
            print(f"Stuck at L{level+1}; stopping.")
            break
        if fd.state.name == 'WIN':
            print(f"Full game WIN (unexpected — all levels solved?)")
            break
    return trace, fd


def main():
    arcade = Arcade()
    env = arcade.make('lf52-271a04aa')
    obs = env.reset()
    game = env._game

    use_cache = os.path.exists(SOL_PATH)
    if use_cache:
        with open(SOL_PATH) as f:
            cached = json.load(f)
        print(f"LF52 partial capture — REPLAY mode from {SOL_PATH} "
              f"({len(cached)} levels cached)")
        trace, fd = run_from_cache(env, game, cached)
    else:
        print(f"LF52 partial capture — SOLVE mode (no cache at {SOL_PATH})")
        trace, fd = run_from_solver(env, game)

    print(f"\nCaptured {len(trace)} env.step calls")

    # Replay through SessionWriter to produce a proper run directory
    from arc_session_writer import SessionWriter
    from arc_perception import get_all_frames

    arc2 = Arcade()
    env2 = arc2.make('lf52-271a04aa')
    fd2 = env2.reset()
    sw = SessionWriter(
        game_id='lf52-271a04aa',
        win_levels=fd2.win_levels,
        available_actions=[a.value if hasattr(a, 'value') else int(a)
                           for a in (fd2.available_actions or [])],
        player='lf52-partial-capture',
    )

    # Build a solutions.json for future regens (only if not already cached)
    all_solutions = []
    current_level_actions = []
    current_level = 0

    for action, data, _ in trace:
        fd2 = env2.step(action, data=data)
        if fd2 is None:
            break
        a_val = action.value if hasattr(action, 'value') else int(action)
        entry = {'action': a_val}
        if data:
            entry['data'] = data
        current_level_actions.append(entry)
        if fd2.levels_completed > current_level:
            all_solutions.append(current_level_actions)
            current_level_actions = []
            current_level = fd2.levels_completed
        all_frames = get_all_frames(fd2)
        grid = all_frames[-1]
        x = data.get('x') if data else None
        y = data.get('y') if data else None
        sw.record_step(
            a_val, grid,
            all_frames=all_frames if len(all_frames) > 1 else None,
            levels_completed=fd2.levels_completed,
            x=x, y=y,
            state=fd2.state.name if hasattr(fd2.state, 'name') else str(fd2.state),
        )
        if fd2.state.name in ('WIN', 'GAME_OVER'):
            break

    sw.record_game_end(fd2.state.name if fd2 else 'NOT_FINISHED',
                       fd2.levels_completed if fd2 else current_level)

    # Only write a fresh solutions.json if we solved (not replayed) — replay
    # should preserve the cached file (which may have hand-tuned reorders).
    if not use_cache:
        os.makedirs(VM, exist_ok=True)
        with open(SOL_PATH, 'w') as f:
            json.dump(all_solutions, f, indent=2)
        print(f"Solutions cached: {len(all_solutions)} levels at {SOL_PATH}")
    else:
        print(f"Solutions cache preserved at {SOL_PATH}")

    print(f"\nRun dir: {sw.run_dir}")
    print(f"Final state: {fd2.state.name}  levels: {fd2.levels_completed}/{fd2.win_levels}")


if __name__ == "__main__":
    main()
