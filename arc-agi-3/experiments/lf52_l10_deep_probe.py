#!/usr/bin/env python3
"""
lf52 L10 deep probe — inspect engine's accepted jump paths at critical states.

Goal: find whether ANY legitimate jump path from L10 init state can reduce
the N count by 1. Uses env.step() only; tries the specific sequence that
leaves blue@(4,1) on block adjacent to N@(4,0).
"""
import os, sys, json
sys.setrecursionlimit(50000)
os.chdir('/mnt/c/exe/projects/ai-agents/SAGE')
os.environ['OPERATION_MODE'] = 'offline'
sys.path.insert(0, '.')
sys.path.insert(0, '/mnt/c/exe/projects/ai-agents/ARC-SAGE/arc-agi-3/experiments')
sys.stdout.reconfigure(line_buffering=True)

from arc_agi import Arcade
from arcengine import GameAction
from lf52_solve_final import extract_state

arc = Arcade(operation_mode='offline')
env = arc.make('lf52-271a04aa')
env.reset()
game = env._game
game.set_level(9)

# Execute the "stop at LEFT 4" state that leaves blue@(4,1)
for _ in range(8):
    env.step(GameAction.ACTION1)  # UP
for _ in range(4):
    env.step(GameAction.ACTION3)  # LEFT (only 4!)

eq = game.ikhhdzfmarl
st = extract_state(eq)
print("After 8xUP + 4xLEFT:")
print(f"  blocks: {sorted(st['pushable'])}")
print(f"  pieces: {dict(st['pieces'])}")

# Inspect critical cells for N@(4,0) DOWN jump
print("\nCell inventory for N@(4,0) DOWN jump candidate:")
for pos in [(4, 0), (4, 1), (4, 2), (4, 3)]:
    objs = eq.hncnfaqaddg.ijpoqzvnjt(*pos)
    print(f"  {pos}: {[o.name for o in objs]}")

# ---------------------------------------------------------------------------
# To actually execute a jump in the engine, we need to simulate click events.
# Engine has dghsidbuet (click handler). Check the click API.
# ---------------------------------------------------------------------------
print("\nEngine click API introspection:")
print(f"  game: {[m for m in dir(game) if 'click' in m.lower() or 'select' in m.lower()][:10]}")
print(f"  eq: {[m for m in dir(eq) if 'click' in m.lower() or 'select' in m.lower()][:10]}")

# ACTION6 is typically "click at coords" — test that path
print("\nTry ACTION6 (click) to select N@(4,0). Need pixel coords.")
# Engine scene cs (cell size) and offset
cs = getattr(eq, 'cs', None)
offset = getattr(eq.hncnfaqaddg, 'cdpcbbnfdp', None) if hasattr(eq, 'hncnfaqaddg') else None
print(f"  eq.cs: {cs}")
print(f"  grid.cdpcbbnfdp (offset): {offset}")

# Let's look at the renderer to see the piece pixel coords
print("\nScene graph intro:")
for attr in dir(eq):
    if attr.startswith('_'): continue
    try:
        val = getattr(eq, attr)
        if not callable(val) and not isinstance(val, (int, float, str, bool, type(None), list, dict)):
            print(f"  eq.{attr} = {type(val).__name__}")
    except Exception:
        pass

# Find how actions are exposed — look at the action enum
from arcengine import GameAction
print(f"\nGameAction values: {[a.name for a in GameAction]}")

# Try ACTION5 which is often 'select' via data dict
# L1 solutions used: "action": "CLICK", "x": 19, "y": 20 — so CLICK is one of the actions
# Check env's action_space
print(f"\nenv.action_space: {env.action_space}")
