"""Deep probe: does eq.win() call actually complete the level?
And where do (14,1) and (22,3) blocks end up after many UP pushes?
"""
import os
os.chdir("/mnt/c/exe/projects/ai-agents/SAGE")
os.environ['OPERATION_MODE'] = 'offline'
import arc_agi
from arcengine import GameAction


def get_state(eq):
    grid = eq.hncnfaqaddg
    pieces = {}
    blocks = set()
    walkable = set()
    walls = set()
    pegs = set()
    for y in range(30):
        for x in range(30):
            objs = grid.ijpoqzvnjt(x, y)
            names = [o.name for o in objs]
            for n in names:
                if n == 'fozwvlovdui':
                    pieces[(x, y)] = 'N'
                elif n == 'fozwvlovdui_red':
                    pieces[(x, y)] = 'R'
                elif n == 'fozwvlovdui_blue':
                    pieces[(x, y)] = 'B'
                if 'hupkpseyuim2' in n:
                    blocks.add((x, y))
                if n == 'hupkpseyuim':
                    walkable.add((x, y))
                if 'kraubslpehi' in n:
                    walls.add((x, y))
                if n == 'dgxfozncuiz':
                    pegs.add((x, y))
    return dict(pieces=pieces, blocks=blocks, walkable=walkable, walls=walls, pegs=pegs,
                won=eq.iajuzrgttrv, lost=eq.evxflhofing, level=eq.whtqurkphir)


def fresh_L7(arcade):
    env = arcade.make('lf52-271a04aa')
    env.reset()
    g = env._game
    g.set_level(6)
    return env, g


def main():
    arcade = arc_agi.Arcade(operation_mode='offline')

    # === Test 1: eq.win() effect on full level advancement ===
    print("=== Test 1: eq.win() followed by multiple steps ===")
    env, g = fresh_L7(arcade)
    eq = g.ikhhdzfmarl
    print(f"  pre: level={eq.whtqurkphir} won={eq.iajuzrgttrv} completed?")
    eq.win()
    print(f"  post-win(): won={eq.iajuzrgttrv}")
    # Take several steps to drain animation
    for i in range(5):
        fd = env.step(GameAction.ACTION1)
        print(f"  step {i}: state={fd.state.name} levels_completed={fd.levels_completed} current_level={g.ikhhdzfmarl.whtqurkphir}")

    # === Test 2: col 22 block behavior under many UPs ===
    print(f"\n=== Test 2: col 22 under many UP pushes ===")
    env2, g2 = fresh_L7(arcade)
    for i in range(8):
        env2.step(GameAction.ACTION1)
        s = get_state(g2.ikhhdzfmarl)
        col22 = sorted([p for p in s['blocks'] if p[0] == 22])
        print(f"  UP×{i+1}: col22 blocks={col22}")

    # === Test 3: multi-direction to explore block reachability on col 22 ===
    print(f"\n=== Test 3: can block at (22,4) reach col 21 somehow? ===")
    # (22,4) is adjacent to (21,4). Does (21,4) have wall variant?
    env3, g3 = fresh_L7(arcade)
    s3 = get_state(g3.ikhhdzfmarl)
    # Check what's at (21,4), (21,5), (21,6)
    for pos in [(20,4),(21,4),(21,5),(21,6),(22,4),(22,5),(22,6),(22,7)]:
        objs = g3.ikhhdzfmarl.hncnfaqaddg.ijpoqzvnjt(*pos)
        names = [o.name for o in objs]
        print(f"  {pos}: {names}")

    # === Test 4: left-N can actually reach which cells? ===
    # Prior claim: cols 0-6. Let me quickly verify (21,6) is reachable for left-N
    # after some specific pushes.
    # Actually check: left-N is at (0,1). The grid has walkable (22,5) and (22,6).
    # Are there any walkable cells between (6,x) and (22,y)? Look at walkable.
    print(f"\n=== Test 4: walkable-cell connectivity ===")
    walkable = s3['walkable']
    # Group by row
    by_row = {}
    for (x, y) in sorted(walkable):
        by_row.setdefault(y, []).append(x)
    for y in sorted(by_row):
        print(f"  row {y}: cols {by_row[y]}")
    # Key question: can a piece walk from left half to right half?
    # Piece movement is only via jumps, so it's jump-graph reachability.
    # But what about through block-riding? Blocks move through walls.

    # === Test 5: block moving through walls — can a piece RIDE a block into a
    # new walkable cell? ===
    # Piece on walkable cell (0,1). Block at (5,5). Push LLUULLL moves block to (0,3).
    # Piece must be ON the block to ride. What if a piece is on a cell that
    # becomes a block cell after push? Check: pieces at (0,1), block ends at (0,3)
    # — not same cell. But if left-N JUMPS to (0,3) then pushes, does it ride?
    print(f"\n=== Test 5: piece riding on a block via push ===")
    env5, g5 = fresh_L7(arcade)
    # Execute push sequence to position block at (0,3)
    seq = [GameAction.ACTION3, GameAction.ACTION3, GameAction.ACTION1, GameAction.ACTION1,
           GameAction.ACTION3, GameAction.ACTION3, GameAction.ACTION3]
    for a in seq:
        env5.step(a)
    s5a = get_state(g5.ikhhdzfmarl)
    print(f"  after pushes: pieces={s5a['pieces']} blocks_col_0={sorted([p for p in s5a['blocks'] if p[0]==0])}")
    # Now do the jump — click N@(0,1) and down arrow
    off = g5.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp
    px_n = 0*6 + off[0] + 3
    py_n = 1*6 + off[1] + 3
    # Click N
    env5.step(GameAction.ACTION6, data={'x': px_n, 'y': py_n})
    # Click down arrow (arrow is ~2 cells below piece)
    env5.step(GameAction.ACTION6, data={'x': px_n, 'y': py_n + 12})
    s5b = get_state(g5.ikhhdzfmarl)
    print(f"  after jump: pieces={s5b['pieces']}")
    # Now N is at (0,3) ON the block. Push UP — does N ride?
    env5.step(GameAction.ACTION1)
    s5c = get_state(g5.ikhhdzfmarl)
    print(f"  after push UP: pieces={s5c['pieces']} blocks_col_0={sorted([p for p in s5c['blocks'] if p[0]==0])}")

    # === Test 6: piece-rides-block toward right half of board ===
    # If N rides block through walls, and blocks can travel far, N could
    # potentially reach right-N's neighborhood.
    # But blocks are constrained to wall-channel paths. Need to map block
    # reachability with wall channels.


if __name__ == '__main__':
    main()
