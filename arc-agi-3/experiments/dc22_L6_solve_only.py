#!/usr/bin/env python3
"""Run just solve_macro on L6 with verbose output."""
import os, sys, json
os.chdir("/mnt/c/exe/projects/ai-agents/SAGE")
os.environ['OPERATION_MODE'] = 'offline'
sys.path.insert(0, ".")
sys.stdout.reconfigure(line_buffering=True)

from arc_agi import Arcade
from arcengine import GameAction, InteractionMode
sys.path.insert(0, "arc-agi-3/experiments")
from dc22_solve_final import solve_macro

VIS = "/mnt/c/exe/projects/ai-agents/shared-context/arc-agi-3/visual-memory/dc22"

def main():
    arcade = Arcade(operation_mode='offline')
    env = arcade.make('dc22-4c9bff3e')
    env.reset()
    with open(f"{VIS}/solutions.json") as f:
        raw = json.load(f)
    am = {1: GameAction.ACTION1, 2: GameAction.ACTION2, 3: GameAction.ACTION3, 4: GameAction.ACTION4, 6: GameAction.ACTION6}
    for lvl_idx in range(5):
        for m in raw[lvl_idx]:
            env.step(am[m['action']], data=m.get('data', {}))
    # Now we're at start of L6
    sol = solve_macro(env, 5, timeout=600, max_click_depth=15)
    if sol:
        print(f"SOLVED! {len(sol)} moves")
        # Encode
        enc = []
        for m in sol:
            if isinstance(m, tuple):
                enc.append({'action': m[0].value, 'data': m[1]})
            else:
                enc.append({'action': m.value})
        with open(f"{VIS}/L6_solution_candidate.json", 'w') as f:
            json.dump(enc, f, indent=2)
        print("Saved to L6_solution_candidate.json")
    else:
        print("FAILED")

if __name__ == "__main__":
    main()
