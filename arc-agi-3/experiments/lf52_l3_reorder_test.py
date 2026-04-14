#!/usr/bin/env python3
"""Test L3 re-ordering: execute steps 4-15 of cached L3 first (these do
left-side jumps + land a piece on block then scroll via RIGHT x3), then execute
the right-side jumps (old steps 0-3) at shifted coords.

If this WORKS we know re-ordering produces valid L3 solve with 0 OOB clicks.
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


def run_step(env, game, step, label):
    a = ACTION_MAP[step['action']]
    data = step.get('data')
    fd = env.step(a, data=data)
    eq = game.ikhhdzfmarl
    snap = snapshot(eq)
    x = data.get('x') if data else None
    y = data.get('y') if data else None
    oob = (x is not None and (x<0 or x>63 or y<0 or y>63))
    oob_m = " [OOB]" if oob else ""
    print(f"  {label}: action={step['action']} data={data}{oob_m} off={snap['offset']} pcs={snap['pieces_count']}")
    return fd, snap


def main():
    arcade = Arcade()
    env = arcade.make('lf52-271a04aa')
    obs = env.reset()
    game = env._game

    solutions = reach_L3(env)
    eq = game.ikhhdzfmarl
    print(f"L3 start: {snapshot(eq)}")

    L3 = solutions[2]

    # Execute steps 4-15 first (left-side jumps + piece-on-block + scroll)
    print("\n=== Phase 1: left-side jumps + piece-on-block + scroll ===")
    for i in range(4, 16):
        fd, snap = run_step(env, game, L3[i], f"step {i}")

    eq = game.ikhhdzfmarl
    off = eq.hncnfaqaddg.cdpcbbnfdp
    print(f"\nAfter phase 1: offset={off}")

    # Now execute the previously-OOB steps 0-3, but rewritten for current offset.
    # Steps 0-3 were: click (12,2), arrow LEFT, click (12,4), arrow LEFT
    # Pieces (12,2) and (12,4) should still be there (phase 1 didn't touch them).
    print(f"\n=== Phase 2: execute ex-OOB steps with shifted coords ===")
    # Click piece (12,2)
    x = 12 * 6 + off[0] + 3
    y = 2 * 6 + off[1] + 3
    fd, snap = run_step(env, game, {'action': 6, 'data': {'x': x, 'y': y}}, "ex-step0")
    # Arrow LEFT -> land (10,2)
    x = 12 * 6 + off[0] + (-1) * 12 + 3
    y = 2 * 6 + off[1] + 3
    fd, snap = run_step(env, game, {'action': 6, 'data': {'x': x, 'y': y}}, "ex-step1")
    # Click piece (12, 4)
    x = 12 * 6 + off[0] + 3
    y = 4 * 6 + off[1] + 3
    fd, snap = run_step(env, game, {'action': 6, 'data': {'x': x, 'y': y}}, "ex-step2")
    # Arrow LEFT
    x = 12 * 6 + off[0] + (-1) * 12 + 3
    y = 4 * 6 + off[1] + 3
    fd, snap = run_step(env, game, {'action': 6, 'data': {'x': x, 'y': y}}, "ex-step3")

    # Now continue cached solution from step 16 onwards (the remaining steps)
    print(f"\n=== Phase 3: continue with cached steps 16+ ===")
    # Offset should match what cached sol expects at step 16: (-19, 5)
    # Current offset should be same
    eq = game.ikhhdzfmarl
    print(f"Current offset: {eq.hncnfaqaddg.cdpcbbnfdp}")
    for i in range(16, len(L3)):
        fd, snap = run_step(env, game, L3[i], f"step {i}")
        if fd.levels_completed > 2:
            print(f"\nL3 SOLVED! Pieces: {snap['pieces_count']}, levels_completed={fd.levels_completed}")
            return
    print(f"\nFinal state: {snapshot(game.ikhhdzfmarl)}")
    print(f"fd.state: {fd.state.name}, levels_completed: {fd.levels_completed}")


if __name__ == "__main__":
    main()
