#!/usr/bin/env python3
"""Probe L3: what controls grid.cdpcbbnfdp on L3?

Walks through the cached L3 solution action-by-action, logging offset,
piece positions, blocks after EACH action. Identifies which actions cause
scroll.

Also tries alternative starts: push-before-click, jump-different-piece,
etc., to find a scroll path that brings col 12 pieces into viewport.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

from arc_agi import Arcade
from arcengine import GameAction

ACTION_MAP = {0: GameAction.RESET, 1: GameAction.ACTION1, 2: GameAction.ACTION2,
              3: GameAction.ACTION3, 4: GameAction.ACTION4, 5: GameAction.ACTION5,
              6: GameAction.ACTION6, 7: GameAction.ACTION7}

def snapshot(eq):
    grid = eq.hncnfaqaddg
    pieces = [(p.grid_x, p.grid_y) for p in grid.ndtvadsrqf("fozwvlovdui")]
    blocks = [(b.grid_x, b.grid_y) for b in grid.whdmasyorl("hupkpseyuim2")]
    return {
        'offset': grid.cdpcbbnfdp,
        'pieces_count': len(pieces),
        'pieces': sorted(pieces),
        'blocks': sorted(blocks),
        'level': eq.whtqurkphir,
        'steps': eq.asqvqzpfdi,
        'won': eq.iajuzrgttrv,
    }

def reach_L3(env):
    sol_path = os.path.join(os.path.dirname(__file__), '..', '..',
                            'knowledge', 'visual-memory', 'lf52', 'solutions.json')
    with open(sol_path) as f:
        solutions = json.load(f)
    for level_idx in [0, 1]:
        for step in solutions[level_idx]:
            a = ACTION_MAP[step['action']]
            env.step(a, data=step.get('data'))
    return solutions

def main():
    arcade = Arcade()
    env = arcade.make('lf52-271a04aa')
    obs = env.reset()
    game = env._game

    solutions = reach_L3(env)
    eq = game.ikhhdzfmarl
    print(f"L3 start: {snapshot(eq)}")
    print(f"L3 solution length: {len(solutions[2])}")

    # Step through L3 cached solution; log offset after EACH action
    prev_off = eq.hncnfaqaddg.cdpcbbnfdp
    for i, step in enumerate(solutions[2]):
        a = ACTION_MAP[step['action']]
        data = step.get('data')
        x = data.get('x') if data else None
        y = data.get('y') if data else None
        oob = (x is not None and (x<0 or x>63 or y<0 or y>63))
        fd = env.step(a, data=data)
        eq = game.ikhhdzfmarl
        snap = snapshot(eq)
        off = snap['offset']
        marker = ""
        if off != prev_off:
            marker = f" <-- OFFSET CHANGED from {prev_off}"
        oob_m = " [OOB]" if oob else ""
        print(f"  step {i}: action={step['action']} data={data}{oob_m}  offset={off} pieces={snap['pieces_count']}{marker}")
        prev_off = off
        if fd.levels_completed > 2:
            print(f"  L3 SOLVED at step {i}")
            break

if __name__ == "__main__":
    main()
