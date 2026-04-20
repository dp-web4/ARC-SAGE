#!/usr/bin/env python3
"""
Execute the legitimate blue-on-cart reframe path through the real engine,
INCLUDING the actual N jump via click+arrow (ACTION6 with coord data).

Path: 8xUP + 4xLEFT, then click N@(4,0), click DOWN arrow to jump to (4,2).
This verifies the reframe's achievable endpoint: N moves but doesn't reduce.
"""
import os, sys, json
sys.setrecursionlimit(50000)
os.chdir('/mnt/c/exe/projects/ai-agents/SAGE')
os.environ['OPERATION_MODE'] = 'offline'
sys.path.insert(0, '.')
sys.path.insert(0, '/mnt/c/exe/projects/ai-agents/ARC-SAGE/arc-agi-3/experiments')
sys.stdout.reconfigure(line_buffering=True)

import numpy as np
from PIL import Image
from arc_agi import Arcade
from arcengine import GameAction
from lf52_solve_final import extract_state, PALETTE

OUT_DIR = '/mnt/c/exe/projects/ai-agents/ARC-SAGE/knowledge/visual-memory/lf52/run_L10_legitimate'


def save_frame(frame_data, path, scale=12):
    try:
        frame = np.array(frame_data[0])
        h, w = frame.shape
        img = Image.new('RGB', (w * scale, h * scale))
        pix = img.load()
        for y in range(h):
            for x in range(w):
                c = PALETTE.get(int(frame[y, x]), (0, 0, 0))
                for dy in range(scale):
                    for dx in range(scale):
                        pix[x * scale + dx, y * scale + dy] = c
        img.save(path)
        return True
    except Exception as e:
        print(f"  err: {e}")
        return False


def summarize(game):
    eq = game.ikhhdzfmarl
    st = extract_state(eq)
    by_type = {'N': [], 'R': [], 'B': []}
    for (x, y), name in st['pieces'].items():
        key = 'N' if name == 'fozwvlovdui' else ('R' if name == 'fozwvlovdui_red' else 'B')
        by_type[key].append([x, y])
    for k in by_type: by_type[k].sort()
    return {
        'level': int(st['level']),
        'blocks': sorted([list(p) for p in st['pushable']]),
        'pieces': by_type,
        'offset': list(st['offset']),
    }


arc = Arcade(operation_mode='offline')
env = arc.make('lf52-271a04aa')
env.reset()
game = env._game
game.set_level(9)

print("L10 initial state:")
init = summarize(game)
print(f"  blocks={init['blocks']}")
print(f"  pieces={init['pieces']}")
print(f"  grid offset (cdpcbbnfdp) = {init['offset']}")

offset_x, offset_y = init['offset']

# ---------------------------------------------------------------------------
# Phase 1 & 2: 8xUP + 4xLEFT
# ---------------------------------------------------------------------------
print("\nPhase 1: 8x UP")
for _ in range(8):
    env.step(GameAction.ACTION1)

print("Phase 2: 4x LEFT (stop after 4, not 5, to leave blue@(4,1))")
for _ in range(4):
    env.step(GameAction.ACTION3)

mid_state = summarize(game)
print(f"  blocks={mid_state['blocks']}")
print(f"  pieces.N={mid_state['pieces']['N']}")
print(f"  pieces.B (partial)={mid_state['pieces']['B']}")

save_frame(env._game.ikhhdzfmarl.xfyfphklhzp[np.newaxis, :, :],
           os.path.join(OUT_DIR, 'step_012_blue_at_4_1.png'), scale=12)

# ---------------------------------------------------------------------------
# Inspect engine-level jump execution mechanics
# Look at _get_valid_clickable_actions to understand the click protocol
# ---------------------------------------------------------------------------
print("\n=== Click/jump API exploration ===")
valid_clicks = game._get_valid_clickable_actions()
print(f"  valid clickable actions returns: {type(valid_clicks).__name__}, len={len(valid_clicks) if hasattr(valid_clicks, '__len__') else 'n/a'}")
if hasattr(valid_clicks, '__iter__'):
    for i, c in enumerate(list(valid_clicks)[:10]):
        print(f"    [{i}] {c}")

# Check available_actions in FrameDataRaw
fd = env.step(GameAction.ACTION7)  # possibly a no-op
print(f"\n  env.step(ACTION7) action_input={fd.action_input}")
print(f"  available_actions={fd.available_actions}")

# Try ACTION6 with click at N@(4,0) — pixel coords are x=(4+offset_x)*cs, y=(0+offset_y)*cs
# Engine cell size may be 3 or 2. Let's probe by looking at frame size.
frame_arr = np.array(fd.frame[0])
print(f"  Frame shape: {frame_arr.shape}")
# Frame is 64x64. Grid is ~9x14 at offset (5,3). So cell size ~= (64 - 5) / 9 ≈ 6. Let's confirm.
# Actually engine often has cs=6, offset=(5,3). Let's just try.

# The replay step ACTION5 / ACTION6 in engine is click — check which takes coords
# L1 solutions had x=19, y=20. If offset=(5,3), cs=6: that's cell (2.33, 2.83). Makes no sense — so maybe cs=3 + offset=(5,3) for pixel->grid: (19-5)/3=4.67, (20-3)/3=5.67.
# Better: observe env's coordinates in existing L1 solution:
print("\nCheck existing L1 solution for click coordinate convention:")
import json
with open('/mnt/c/exe/projects/ai-agents/ARC-SAGE/knowledge/visual-memory/lf52/run_L7L10_solution/run.json') as f:
    sol = json.load(f)
for step in sol['steps'][:4]:
    print(f"  {step}")

# The L1 solution uses "CLICK" with x, y in pixel space. That translates to ACTION6 most likely.
# Try ACTION6 with data={'x': X, 'y': Y} where X,Y are pixel coords for N@(4,0).
