#!/usr/bin/env python3
"""Capture lf52 L1-L6 as replayable visual memory.

Prior frame-questioning concluded L7 is structurally unsolvable in the pinned
engine version (8 convergent passes). This script runs the solver for L1-L6
only, producing a run_ directory with SessionWriter + an all_solutions cache
in solutions.json so future regens don't need to re-solve.

Usage: python3 lf52_partial_capture.py
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(__file__))

from arc_agi import Arcade
from arcengine import GameAction

# Import solver pieces from lf52_solve_final
import lf52_solve_final as L

# Load game, reset
arcade = Arcade()
env = arcade.make('lf52-271a04aa')
obs = env.reset()
game = env._game

MAX_LEVEL = 6  # L1-L6 only; L7 is structurally stuck

print(f"LF52 partial capture — solving L1..L{MAX_LEVEL}")

# Set up tracing: wrap env.step to capture (action, data, fd) tuples
trace = []
_orig_step = env.step
def traced_step(action, data=None, **kw):
    fd = _orig_step(action, data=data, **kw)
    trace.append((action, data, fd))
    return fd
env.step = traced_step

# Solve each level
for level in range(MAX_LEVEL):
    print(f"\n=== Level {level+1} ===")
    fd = L.solve_level(env, game, level)
    if fd is None or fd.levels_completed <= level:
        print(f"Stuck at L{level+1}; stopping.")
        break
    if fd.state.name == 'WIN':
        print(f"Full game WIN (unexpected — all levels solved?)")
        break

print(f"\nCaptured {len(trace)} env.step calls")

# Now replay via SessionWriter to produce a proper run directory
from arc_session_writer import SessionWriter
from arc_perception import get_all_frames

arc2 = Arcade()
env2 = arc2.make('lf52-271a04aa')
fd2 = env2.reset()
sw = SessionWriter(
    game_id='lf52-271a04aa',
    win_levels=fd2.win_levels,
    available_actions=[a.value if hasattr(a,'value') else int(a) for a in (fd2.available_actions or [])],
    player='lf52-partial-capture',
)

# Also build a solutions.json for future regens
all_solutions = []  # per-level list of [{'action': int, 'data': dict}]
current_level_actions = []
current_level = 0

for action, data, trace_fd in trace:
    fd2 = env2.step(action, data=data)
    if fd2 is None:
        break
    a_val = action.value if hasattr(action, 'value') else int(action)
    # Record for solutions.json
    entry = {'action': a_val}
    if data:
        entry['data'] = data
    current_level_actions.append(entry)
    if fd2.levels_completed > current_level:
        all_solutions.append(current_level_actions)
        current_level_actions = []
        current_level = fd2.levels_completed
    # Record to SessionWriter
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

# If there's a partial level at the end (level we're still playing), don't include it
sw.record_game_end(fd2.state.name if fd2 else 'NOT_FINISHED',
                    fd2.levels_completed if fd2 else current_level)

# Write solutions.json
VM = os.path.join(os.path.dirname(__file__), '..', '..', 'knowledge', 'visual-memory', 'lf52')
os.makedirs(VM, exist_ok=True)
with open(os.path.join(VM, 'solutions.json'), 'w') as f:
    json.dump(all_solutions, f, indent=2)

print(f"\nRun dir: {sw.run_dir}")
print(f"Solutions cached: {len(all_solutions)} levels at {VM}/solutions.json")
print(f"Final state: {fd2.state.name}  levels: {fd2.levels_completed}/{fd2.win_levels}")
