#!/usr/bin/env python3
"""Test L3 patch: push RIGHT 3x to scroll, then execute rest of cached L3 solution
WITH updated coords based on new offset.

The cached L3 solution was built for offset=(5,5). If we scroll to (-19,5) first,
world clicks need to shift too. Click formula: new_x = old_x - 24, new_y = old_y.
Old OOB clicks become in-bounds: (80,20)->(56,20), (68,20)->(44,20), etc.

But if we scroll after first few jumps — as the cached solution does — the
cached solution's LATER x-coords may need re-shifting. Simpler: prepend 3 RIGHT
pushes, then shift ALL remaining solution clicks by -24 in x.

Then at step 33, the cached solution does LEFT (unscroll back to (-11,5)) — but
we pre-scrolled so we're already at (-19,5), and subsequent LEFTs in the cached
sol will return us to (-19 + 8*count)...

Actually — simpler: DON'T prepend. Use the existing LEFTs/RIGHTs in the cached
sol BUT reorder so scroll happens BEFORE the OOB clicks. The cached solution
already has pushes later that scroll; we just move them earlier.

Actually even simpler test first: start L3, do 3 RIGHTs, check blocks/pieces,
then try the first OOB click with re-mapped x.
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

    # Push RIGHT 3 times
    for i in range(3):
        env.step(GameAction.ACTION4)
        eq = game.ikhhdzfmarl
        print(f"After RIGHT #{i+1}: {snapshot(eq)}")

    # Now offset should be (-19, 5). Click piece at (12, 2) via shifted coord.
    # new_x = 12*6 + (-19) + 3 = 56. new_y = 2*6 + 5 + 3 = 20
    off = eq.hncnfaqaddg.cdpcbbnfdp
    print(f"\nCurrent offset: {off}")
    # piece at (12, 2)?  check
    pieces = snapshot(eq)['pieces']
    print(f"Pieces now: {pieces}")
    # Click piece (12,2)
    x = 12 * 6 + off[0] + 3
    y = 2 * 6 + off[1] + 3
    print(f"\nClick piece (12,2) at world ({x},{y})")
    fd = env.step(GameAction.ACTION6, data={'x': x, 'y': y})
    eq = game.ikhhdzfmarl
    print(f"After click: {snapshot(eq)}")

    # Now click arrow (LEFT-2) — land at (10, 2)
    # arrow at (12*6 + off[0] + half_dx*12 + 3, 2*6 + off[1] + 3)
    # half_dx = (10-12)//2 = -1
    ax = 12 * 6 + off[0] + (-1) * 12 + 3
    ay = 2 * 6 + off[1] + 3
    print(f"\nClick LEFT arrow at ({ax},{ay})")
    fd = env.step(GameAction.ACTION6, data={'x': ax, 'y': ay})
    eq = game.ikhhdzfmarl
    print(f"After arrow: {snapshot(eq)}")

    # Now replay remainder of cached L3 solution — but first 4 clicks were the OOB ones
    # We just executed 2 of them (the (12,2)->LEFT sequence). The other 2 are (12,4)->LEFT.
    # Do those similarly.
    x = 12 * 6 + off[0] + 3
    y = 4 * 6 + off[1] + 3
    print(f"\nClick piece (12,4) at world ({x},{y})")
    fd = env.step(GameAction.ACTION6, data={'x': x, 'y': y})
    print(f"After click: {snapshot(game.ikhhdzfmarl)}")
    ax = 12 * 6 + off[0] + (-1) * 12 + 3
    ay = 4 * 6 + off[1] + 3
    print(f"\nClick LEFT arrow at ({ax},{ay})")
    fd = env.step(GameAction.ACTION6, data={'x': ax, 'y': ay})
    eq = game.ikhhdzfmarl
    print(f"After arrow: {snapshot(eq)}")

    # Now replay cached L3 solution from step 4 onwards, but SHIFT x-coords by the current offset
    # diff from (5,5). We're at (-19,5) so diff = (-24, 0). Each click needs x -= 24.
    # But: further RIGHT/LEFT in the cached sol will again change offset — so we need
    # to TRACK offset as we go and adjust each click accordingly.
    # The cached sol clicks were computed against offset at the time they were emitted.
    # Actually — simpler: the cached sol later does RIGHT, RIGHT, RIGHT (steps 13-15)
    # to get to offset (-19,5). We already scrolled there. So skip those. The cached
    # sol also does LEFT, LEFT, LEFT (steps 33, 36, 37) to return to (5,5) — those
    # would return to the initial offset which we BYPASSED. So we'd need to NOT do
    # those LEFTs either.
    #
    # Too complex — try something simpler: run the full cached sol from step 4 unchanged.
    # Offset is (-19,5) now; but cached sol step 4 click (14,14) was computed for
    # offset (5,5). At that time piece was at grid (1,1), world (1*6+5+3, 1*6+5+3) = (14,14).
    # Now offset is (-19,5); piece at (1,1) would be world (1*6-19+3, 1*6+5+3) = (-10,14) OOB!
    # So the cached sol's later clicks are ALSO miscalibrated for our new offset.
    #
    # Correct approach: re-resolve each cached click from its INTENDED (sx,sy) using
    # current offset. But the cached solution doesn't tell us (sx,sy) — only pixel x,y.
    # We can back-infer: at cached time, sx = (x - off_at_time - 3) // 6. If we know
    # when each scroll happened in the cached sol, we can reconstruct.
    #
    # Easier alternative: re-run solver with viewport-aware patched execute_actions.

    print("\n--- Current state: we executed 4 click-pairs from shifted coords. ---")
    print(f"--- If we made legitimate jumps, pieces count should be 10 now. ---")
    print(f"--- Actual: {snapshot(eq)['pieces_count']} pieces.  Good? ---")


if __name__ == "__main__":
    main()
