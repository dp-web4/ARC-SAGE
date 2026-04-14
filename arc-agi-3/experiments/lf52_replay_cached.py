#!/usr/bin/env python3
"""Replay cached solutions.json end-to-end (L1..LN), validating that each
level completes and no click is OOB. Uses the reordered L3 if provided.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

from arc_agi import Arcade
from arcengine import GameAction

ACTION_MAP = {0: GameAction.RESET, 1: GameAction.ACTION1, 2: GameAction.ACTION2,
              3: GameAction.ACTION3, 4: GameAction.ACTION4, 5: GameAction.ACTION5,
              6: GameAction.ACTION6, 7: GameAction.ACTION7}


def make_reordered_l3(orig):
    """Build 0-OOB version of L3 cached solution."""
    phase_a = orig[4:16]     # left-side + piece-on-block + 3 scrolls
    phase_b = [
        {'action': 6, 'data': {'x': 56, 'y': 20}},  # click piece (12,2) at off=(-19,5)
        {'action': 6, 'data': {'x': 44, 'y': 20}},  # LEFT-2 arrow
        {'action': 6, 'data': {'x': 56, 'y': 32}},  # click piece (12,4)
        {'action': 6, 'data': {'x': 44, 'y': 32}},  # LEFT-2 arrow
    ]
    phase_c = orig[16:]
    return phase_a + phase_b + phase_c


def main():
    sol_path = os.path.join(os.path.dirname(__file__), '..', '..',
                            'knowledge', 'visual-memory', 'lf52', 'solutions.json')
    with open(sol_path) as f:
        sols = json.load(f)

    # Reorder L3 in-memory for this replay test (DO NOT write back)
    sols[2] = make_reordered_l3(sols[2])

    arcade = Arcade()
    env = arcade.make('lf52-271a04aa')
    obs = env.reset()
    game = env._game

    print(f"Replaying {len(sols)} level solutions")

    total_oob = 0
    total_steps = 0
    levels_completed = 0
    for level_idx, steps in enumerate(sols):
        print(f"\n--- L{level_idx+1}: {len(steps)} steps ---")
        level_oob = 0
        for step in steps:
            a = ACTION_MAP[step['action']]
            data = step.get('data')
            x = data.get('x') if data else None
            y = data.get('y') if data else None
            oob = (x is not None and (x<0 or x>63 or y<0 or y>63))
            if oob:
                level_oob += 1
                print(f"  OOB click at {data}")
            fd = env.step(a, data=data)
            total_steps += 1
            if fd.levels_completed > level_idx:
                levels_completed = fd.levels_completed
                print(f"  L{level_idx+1} solved -> levels_completed={fd.levels_completed}")
                break
        total_oob += level_oob
        if fd.levels_completed <= level_idx:
            print(f"  FAILED to solve L{level_idx+1}")
            break

    print(f"\n=== SUMMARY ===")
    print(f"  levels_completed: {levels_completed}")
    print(f"  total_steps: {total_steps}")
    print(f"  total_oob: {total_oob}")
    print(f"  final state: {fd.state.name}")


if __name__ == "__main__":
    main()
