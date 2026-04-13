#!/usr/bin/env python3
"""Regenerate replayable visual memory for every solved ARC-AGI-3 game.

Strategy: run each game's solver via importlib, but patch `Arcade.make`
globally BEFORE the solver runs. Every env the solver creates is pre-wrapped
to record (action, data) tuples on every env.step call. After the solver
completes, we have the full action trace. Then we construct a fresh env and
replay the trace through SessionWriter for proper step-by-step capture.

This works for any solver that:
  1. Calls `Arcade().make(game_id)` to get an env
  2. Calls `env.step(action, data=...)` to play actions
  3. Runs to completion (no interactive input)

It does NOT care about:
  - Solver structure (main() vs top-level code)
  - Caching strategies (KNOWN dicts, solutions.json, etc.)
  - Search algorithms (BFS, A*, beam, etc.)

Usage:
  python3 regen_all_visuals.py              # all solved games
  python3 regen_all_visuals.py wa30 ka59    # specific games
  python3 regen_all_visuals.py --list       # show what would run
"""

import sys
import os
import importlib
import importlib.util
import json
import shutil
from pathlib import Path
from io import StringIO

sys.path.insert(0, os.path.dirname(__file__))

from arc_agi import Arcade
from arcengine import GameAction
from arc_perception import get_all_frames
from arc_session_writer import SessionWriter

VM = Path("/mnt/c/exe/projects/ai-agents/shared-context/arc-agi-3/visual-memory")
COORD = Path("/mnt/c/exe/projects/ai-agents/shared-context/arc-agi-3/game_coordination.json")
EXPERIMENTS = Path(os.path.dirname(__file__))


def load_solutions_json(game):
    """If visual-memory/{game}/solutions.json exists in the per-level move
    format (list of lists of {action, data} dicts), convert to a replay trace.
    Returns list of (GameAction, data_dict_or_None, None) tuples or None."""
    p = VM / game / "solutions.json"
    if not p.exists():
        return None
    try:
        raw = json.load(open(p))
    except Exception:
        return None
    if not isinstance(raw, list) or not raw or not isinstance(raw[0], list):
        return None
    act_map = {1: GameAction.ACTION1, 2: GameAction.ACTION2,
               3: GameAction.ACTION3, 4: GameAction.ACTION4,
               5: GameAction.ACTION5, 6: GameAction.ACTION6}
    flat = []
    for lvl in raw:
        for m in lvl:
            if not isinstance(m, dict) or 'action' not in m:
                return None
            a = act_map.get(m['action'])
            if a is None:
                return None
            flat.append((a, m.get('data'), None))
    return flat if flat else None


# ────────────────────────────────────────────────────────────
# Game ↔ solver registry
# ────────────────────────────────────────────────────────────

# Each entry: (game_id, solver_script, label).
# Solver script must be in experiments/. Game must be in coordination as solved.
REGISTRY = [
    ('ar25-e3c63847',   None,                    'ar25-replay'),
    ('bp35-0a0ad940',   'bp35_solve.py',         'bp35-solver'),
    ('cd82-fb555c5d',   'cd82_solve.py',         'cd82-solver'),
    ('cn04-e5f82f82',   None,                    'cn04-replay'),
    ('ft09-0d8bbf25',   None,                    'ft09-replay'),
    ('g50t-5849a774',   'g50t_solve_final.py',   'g50t-solver'),
    ('ka59-9f096b4a',   'ka59_solve_final.py',   'ka59-solver'),
    ('lp85-305b61c3',   'lp85_solve.py',         'lp85-solver'),
    ('ls20-9f9cdcdf',   None,                    'ls20-replay'),
    ('m0r0-dadda488',   'm0r0_solve.py',         'm0r0-solver'),
    ('r11l-aa269680',   'r11l_solve.py',         'r11l-solver'),
    ('re86-4e57566e',   None,                    're86-replay'),
    ('s5i5-a48e4b1d',   's5i5_solve.py',         's5i5-solver'),
    ('sb26-7fbdac44',   'sb26_solve.py',         'sb26-solver'),
    ('sc25-f9b21a2f',   None,                    'sc25-replay'),
    ('sk48-41055498',   'sk48_solve_final.py',   'sk48-solver'),
    ('sp80-b62ff70e',   None,                    'sp80-replay'),
    ('su15-cb2e3f1a',   None,                    'su15-replay'),
    ('tn36-ab4f63cc',   'tn36_solve.py',         'tn36-solver'),
    ('tr87-cd924810',   None,                    'tr87-replay'),
    ('tu93-2b534c15',   None,                    'tu93-replay'),
    ('vc33-9851e02b',   'vc33_solve.py',         'vc33-solver'),
    ('wa30-ee6fef47',   'wa30_solve_final.py',   'wa30-solver'),
    # partial games
    ('dc22-4c9bff3e',   'dc22_solve_final.py',   'dc22-partial'),
    ('lf52-271a04aa',   'lf52_solve_final.py',   'lf52-partial'),
]


# ────────────────────────────────────────────────────────────
# Tracing Arcade wrapper
# ────────────────────────────────────────────────────────────

class TracingEnv:
    """Wraps an env. Forwards all attribute access, records env.step calls."""
    def __init__(self, env):
        self._env = env
        self._trace = []
        self._initial_fd = None

    def reset(self):
        fd = self._env.reset()
        self._initial_fd = fd
        return fd

    def step(self, action, data=None):
        fd = self._env.step(action, data=data)
        self._trace.append((action, data, fd))
        return fd

    def __getattr__(self, name):
        # forward unknown attrs to inner env
        return getattr(self._env, name)


class TracingArcade:
    """Returns TracingEnv instances. Forwards init args to Arcade."""
    def __init__(self, *args, **kwargs):
        self._arcade = Arcade(*args, **kwargs)
        self.last_env = None

    def make(self, game_id, **kwargs):
        env = self._arcade.make(game_id, **kwargs)
        tenv = TracingEnv(env)
        self.last_env = tenv
        return tenv


# ────────────────────────────────────────────────────────────
# Replay with SessionWriter
# ────────────────────────────────────────────────────────────

CLICK = 6

def replay_trace(game_id, trace, label="replay"):
    """Given a trace of (action, data, _) tuples, replay through a fresh env
    and capture via SessionWriter."""
    arcade = Arcade()
    env = arcade.make(game_id)
    fd = env.reset()

    sw = SessionWriter(
        game_id,
        win_levels=fd.win_levels,
        available_actions=[
            a.value if hasattr(a, 'value') else int(a)
            for a in (fd.available_actions or [])
        ],
        player=label,
    )

    for action, data, _ in trace:
        fd = env.step(action, data=data)
        all_frames = get_all_frames(fd)
        grid = all_frames[-1]
        a_val = action.value if hasattr(action, 'value') else int(action)
        x = data.get('x') if data else None
        y = data.get('y') if data else None
        sw.record_step(
            a_val, grid,
            all_frames=all_frames if len(all_frames) > 1 else None,
            levels_completed=fd.levels_completed,
            x=x, y=y,
            state=fd.state.name if hasattr(fd.state, 'name') else str(fd.state),
        )
        if fd.state.name in ("GAME_OVER", "WON"):
            break

    sw.record_game_end(fd.state.name, fd.levels_completed)

    run_dir = Path(sw.run_dir)
    n_png = len(list(run_dir.glob("*.png")))
    n_gif = len(list(run_dir.glob("*.gif")))
    print(f"  {fd.levels_completed}/{fd.win_levels}L, {sw.step} steps, "
          f"{n_png} PNGs, {n_gif} GIFs, state={fd.state.name}")
    print(f"  → {run_dir}")
    return fd.levels_completed >= fd.win_levels


# ────────────────────────────────────────────────────────────
# Run a solver with Arcade monkey-patched
# ────────────────────────────────────────────────────────────

def run_solver_with_trace(solver_script, game_id):
    """Execute solver_script with Arcade replaced by TracingArcade.
    Returns the trace of (action, data, fd) tuples."""
    import arc_agi
    import sys as _sys

    solver_path = EXPERIMENTS / solver_script
    if not solver_path.exists():
        raise FileNotFoundError(f"Solver not found: {solver_path}")

    # Save originals
    orig_arcade = arc_agi.Arcade
    orig_argv = _sys.argv[:]
    traces = []  # list of traces from any envs the solver creates

    class RecordingArcade(TracingArcade):
        def make(self, gid, **kw):
            tenv = super().make(gid, **kw)
            traces.append(tenv)
            return tenv

    # Patch
    arc_agi.Arcade = RecordingArcade
    _sys.argv = [str(solver_path)]  # some solvers check argv
    # Don't redirect stdout — some solvers call sys.stdout.reconfigure()
    # which StringIO doesn't support. Just let their output through; we
    # prefix lines in post-processing if needed.

    solver_ns = {}
    try:
        # Execute solver source as __main__ so its `if __name__ == '__main__'`
        # blocks actually run. importlib with exec_module renames, so use exec.
        with open(solver_path) as f:
            src = f.read()
        ns = {
            '__name__': '__main__',
            '__file__': str(solver_path),
            '__builtins__': __builtins__,
        }
        code = compile(src, str(solver_path), 'exec')
        try:
            exec(code, ns)
        except SystemExit:
            pass  # some solvers sys.exit on completion
        solver_ns.update(ns)
    finally:
        arc_agi.Arcade = orig_arcade
        _sys.argv = orig_argv

    # Prefer solver-exported canonical sequences over raw traces.
    # Common variable names where solvers store per-level winning sequences:
    for var in ('all_solutions', 'per_level_solutions', 'canonical_solutions',
                'winning_sequences', 'KNOWN_SOLUTIONS'):
        if var in solver_ns and isinstance(solver_ns[var], (list, dict)):
            # For dict keyed by level: sort by level, flatten
            data = solver_ns[var]
            if isinstance(data, dict):
                data = [data[k] for k in sorted(data.keys())]
            # data is now list of per-level sequences (each a string or list)
            # Build a synthetic trace: (action, data_dict, None) per step
            flat = []
            from arcengine import GameAction as _GA
            CHAR_TO_GA = {
                'U': _GA.ACTION1, 'D': _GA.ACTION2,
                'L': _GA.ACTION3, 'R': _GA.ACTION4,
                '5': _GA.ACTION5, 'S': _GA.ACTION5,
            }
            for level_seq in data:
                if not level_seq:
                    continue
                if isinstance(level_seq, str):
                    for ch in level_seq:
                        if ch in CHAR_TO_GA:
                            flat.append((CHAR_TO_GA[ch], None, None))
                elif isinstance(level_seq, list):
                    for item in level_seq:
                        if isinstance(item, _GA):
                            flat.append((item, None, None))
                        elif isinstance(item, int):
                            flat.append((_GA(item), None, None))
                        elif isinstance(item, (tuple, list)) and len(item) >= 1:
                            a = item[0]
                            if isinstance(a, int): a = _GA(a)
                            d = None
                            if len(item) >= 3:
                                d = {'x': item[1], 'y': item[2]}
                            elif len(item) == 2 and isinstance(item[1], dict):
                                d = item[1]
                            flat.append((a, d, None))
            if flat:
                return flat

    # Fallback: use raw trace (includes exploration, unreliable for replay)
    best_trace = None
    best_completed = -1
    for tenv in traces:
        if tenv._trace:
            last_fd = tenv._trace[-1][2]
            if last_fd.levels_completed > best_completed:
                best_completed = last_fd.levels_completed
                best_trace = tenv._trace
    return best_trace


# ────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    list_only = '--list' in args
    args = [a for a in args if not a.startswith('--')]

    if not args:
        targets = REGISTRY
    else:
        targets = [r for r in REGISTRY if any(a in r[0] for a in args)]

    print(f"{'='*60}")
    print(f"Regenerating visual memory ({len(targets)} games)")
    print(f"{'='*60}")

    results = []
    for game_id, solver, label in targets:
        game = game_id.split('-')[0]
        print(f"\n[{game}] ({game_id})")

        # Fast path: if visual-memory/{game}/solutions.json is the per-level
        # move format, replay from it directly — no solver run needed.
        cached = load_solutions_json(game)
        if cached:
            print(f"  Found cached solutions.json with {len(cached)} actions")
            if list_only:
                print(f"  WOULD REPLAY: solutions.json → {label}")
                results.append((game, 'list', f'cache:{len(cached)}'))
                continue
            try:
                success = replay_trace(game_id, cached, label=label + '-cache')
                results.append((game, 'ok' if success else 'partial',
                                f'cache:{len(cached)} actions'))
                continue
            except Exception as e:
                import traceback
                print(f"  ERROR replaying cache: {e}")
                traceback.print_exc()
                # fall through to solver path

        if solver is None:
            print(f"  SKIP: no solver script registered (replay-from-sequence needed)")
            results.append((game, 'skip', 'no solver'))
            continue
        if list_only:
            print(f"  WOULD RUN: {solver} → {label}")
            results.append((game, 'list', solver))
            continue

        try:
            trace = run_solver_with_trace(solver, game_id)
            if not trace:
                print(f"  FAIL: solver produced no trace")
                results.append((game, 'fail', 'empty trace'))
                continue
            print(f"  Captured {len(trace)} actions")
            success = replay_trace(game_id, trace, label=label)
            results.append((game, 'ok' if success else 'partial', f'{len(trace)} actions'))
        except Exception as e:
            import traceback
            print(f"  ERROR: {e}")
            traceback.print_exc()
            results.append((game, 'error', str(e)[:80]))

    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    for game, status, detail in results:
        mark = {'ok': '✓', 'partial': '~', 'skip': '-', 'fail': '✗', 'error': '!', 'list': '·'}.get(status, '?')
        print(f"  {mark} {game:6s}  {status:8s}  {detail}")


if __name__ == '__main__':
    main()
