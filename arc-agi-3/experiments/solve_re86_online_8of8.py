#!/usr/bin/env python3
"""Play re86 to 8/8 in NORMAL mode (online) by stitching two existing traces.

The current compete trace (run_20260415_021034, 425 actions) reaches L7 cleanly
online.  The older OFFLINE trace (run_20260412_092533, 606 actions) was built
for a different engine version and fails at L3 online -- but its L8 slice (190
actions) still works against the current L8 engine.

This script:
  1. Replays the 425-action L1-L7 trace verbatim.
  2. Appends the 190-action L8 slice extracted from the old trace.
  3. Saves a unified run.json (+ per-step PNG frames) into
     knowledge/visual-memory/re86/run_online_8of8/.

Discovery: the L8 mechanism analysis from CBP fleet learning
(re86_learning.jsonl) describes exactly the route the old trace executes --
dy-chain to 22x4 via wall (34,55), cross UP at gap col 44-49, paint c6 and c11
at safe corridor (y=15), dx-chain to 4x22 at wall (58,1), cross DOWN through
gap, reshape at wall (34,55) to targets.  The old trace IS this route.
"""
import os
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

try:
    from dotenv import load_dotenv
    load_dotenv('/mnt/c/exe/projects/ai-agents/.env')
except ImportError:
    pass

import numpy as np
from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

VM = Path('/mnt/c/exe/projects/ai-agents/ARC-SAGE/knowledge/visual-memory/re86')
OUT = VM / 'run_online_8of8'
OUT.mkdir(parents=True, exist_ok=True)

# Action mapping
ACTION_MAP = {
    'UP':     GameAction.ACTION1,
    'DOWN':   GameAction.ACTION2,
    'LEFT':   GameAction.ACTION3,
    'RIGHT':  GameAction.ACTION4,
    'SEL':    GameAction.ACTION5,
    'SELECT': GameAction.ACTION5,
}

# Action int values (used in run.json ACTION_MAP-compatible style)
A_INT = {'UP': 1, 'DOWN': 2, 'LEFT': 3, 'RIGHT': 4, 'SEL': 5, 'SELECT': 5}


def load_actions(run_json_path, max_level=None):
    d = json.load(open(run_json_path))
    out = []
    for s in d.get('steps', []):
        if max_level is not None and s.get('level', 0) > max_level:
            break
        out.append((s.get('action', ''), s.get('level', 0)))
    return out


def load_l8_slice(run_json_path):
    """Return (action, level) pairs where level == 7 (L8 0-indexed)."""
    d = json.load(open(run_json_path))
    return [(s['action'], s['level']) for s in d['steps']
            if s.get('level') == 7]


def grid_from_env(env):
    try:
        g = env._game
        return np.asarray(g.get_pixels(0, 0, 64, 64), dtype=np.int8)
    except Exception:
        return None


def main():
    # Load the two traces
    t17 = VM / 'run_20260415_021034' / 'run.json'
    t_old = VM / 'run_20260412_092533' / 'run.json'

    l1_7 = load_actions(t17)  # 425 actions, L0-L6 levels (which is L1-L7)
    l8 = load_l8_slice(t_old)  # 190 actions, L8
    combined = l1_7 + l8

    print(f"Loaded: L1-L7 {len(l1_7)} actions, L8 {len(l8)} actions, "
          f"total {len(combined)}")

    # Online in NORMAL mode
    arc = Arcade(operation_mode=OperationMode.NORMAL)
    env = arc.make('re86-8af5384d')
    fd = env.reset()

    # Render each step into run_online_8of8/ with PNG and track metadata
    from arc_session_writer import render_grid

    t0 = time.time()
    run_meta = {
        "game_id": "re86-8af5384d",
        "player": "re86-stitched-online-8of8",
        "started": time.strftime("%Y%m%d_%H%M%S"),
        "win_levels": 8,
        "baseline": 1071,
        "steps": [],
    }

    total = 0
    prev_level = 0
    for action_str, src_level in combined:
        ga = ACTION_MAP.get(action_str)
        if ga is None:
            print(f"  ! unknown action {action_str} at step {total+1}")
            break
        fd = env.step(ga)
        total += 1
        cur_level = fd.levels_completed if fd else prev_level
        # PNG frame
        grid = grid_from_env(env)
        if grid is not None:
            png_name = f"step_{total:04d}_L{prev_level}_{action_str}.png"
            png_path = OUT / png_name
            try:
                render_grid(grid).save(str(png_path))
            except Exception as e:
                png_name = None
        else:
            png_name = None

        step_meta = {
            "step": total,
            "level": prev_level,
            "action": action_str,
        }
        if png_name:
            step_meta["png"] = png_name
        if cur_level > prev_level:
            step_meta["level_up"] = True
            step_meta["new_level"] = cur_level
        run_meta["steps"].append(step_meta)

        if total % 50 == 0:
            print(f"  step {total}: state={fd.state.name} "
                  f"L={cur_level}/8")

        if fd.state != GameState.NOT_FINISHED:
            print(f"  >> TERMINATED at step {total}: {fd.state.name} "
                  f"L={cur_level}/8")
            break
        prev_level = cur_level

    elapsed = time.time() - t0
    result_state = fd.state.name if fd else "UNKNOWN"
    final_levels = fd.levels_completed if fd else 0

    run_meta["finished"] = time.strftime("%Y%m%d_%H%M%S")
    run_meta["result"] = result_state
    run_meta["levels_completed"] = final_levels
    run_meta["total_steps"] = total
    run_meta["elapsed_sec"] = round(elapsed, 2)

    meta_path = OUT / 'run.json'
    with open(meta_path, 'w') as f:
        json.dump(run_meta, f, indent=2)

    print(f"\n=== FINAL ===")
    print(f"State: {result_state}")
    print(f"Levels: {final_levels}/8")
    print(f"Actions: {total}")
    print(f"Time: {elapsed:.1f}s")
    print(f"Trace: {meta_path}")


if __name__ == '__main__':
    main()
