"""
lf52 L7 — new probes not covered by sessions 1-6.

Focus: things the convergence notes *didn't* explicitly rule out.
"""
import os
os.chdir("/mnt/c/exe/projects/ai-agents/SAGE")
os.environ['OPERATION_MODE'] = 'offline'
import arc_agi
from arcengine import GameAction


def get_state(eq):
    """Extract piece and block positions."""
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
    env, g = fresh_L7(arcade)
    eq = g.ikhhdzfmarl
    s0 = get_state(eq)
    print(f"=== Pristine L7 ===")
    print(f"  pieces: {s0['pieces']}")
    print(f"  blocks: {sorted(s0['blocks'])}")
    print(f"  pegs: {sorted(s0['pegs'])}")
    print(f"  walkable: {sorted(s0['walkable'])}")

    # --- PROBE 1: push directions on pristine — track EVERYTHING ---
    print(f"\n=== PROBE 1: each push from pristine, track all object movement ===")
    for act_name, act in [("UP", GameAction.ACTION1), ("DOWN", GameAction.ACTION2),
                           ("LEFT", GameAction.ACTION3), ("RIGHT", GameAction.ACTION4)]:
        env2, g2 = fresh_L7(arcade)
        s_before = get_state(g2.ikhhdzfmarl)
        fd = env2.step(act)
        s_after = get_state(g2.ikhhdzfmarl)
        block_diff = sorted(s_after['blocks'] - s_before['blocks'])
        block_gone = sorted(s_before['blocks'] - s_after['blocks'])
        peg_diff = sorted(s_after['pegs'] - s_before['pegs'])
        peg_gone = sorted(s_before['pegs'] - s_after['pegs'])
        piece_diff = {k: v for k, v in s_after['pieces'].items() if s_before['pieces'].get(k) != v}
        piece_gone = {k: v for k, v in s_before['pieces'].items() if s_after['pieces'].get(k) != v}
        print(f"  {act_name}: blocks+={block_diff} -={block_gone}; pegs+={peg_diff} -={peg_gone}; pieces+={piece_diff} -={piece_gone}")
        print(f"    won={s_after['won']} lost={s_after['lost']}")

    # --- PROBE 2: sequential RIGHT pushes — does block at (22,4) move UP? ---
    # Already verified blocks on col 22: (22,4) can only go up to (22,0) but
    # (22,5) has no wall-variant. Let's test whether pushing LEFT from pristine
    # moves (22,4) — it shouldn't (no wall to left to push into).
    print(f"\n=== PROBE 2: Can block at (22,4) ever reach (22,5)? ===")
    env3, g3 = fresh_L7(arcade)
    # Try: UP×N to lift it, DOWN might push it back? Or what if blocks on col 22
    # chain-push?
    for seq_name, seq in [
        ("DOWN", [GameAction.ACTION2]),
        ("UP×6", [GameAction.ACTION1]*6),
        ("UP×3 DOWN", [GameAction.ACTION1]*3 + [GameAction.ACTION2]),
    ]:
        env_x, g_x = fresh_L7(arcade)
        for a in seq:
            env_x.step(a)
        sx = get_state(g_x.ikhhdzfmarl)
        col22 = sorted([p for p in sx['blocks'] if p[0] == 22])
        col22_walk = sorted([p for p in sx['walkable'] if p[0] == 22])
        col22_walls = sorted([p for p in sx['walls'] if p[0] == 22])
        print(f"  {seq_name}: col22 blocks={col22}, walkable={col22_walk}, walls-in-col22={col22_walls}")

    # --- PROBE 3: ACTION6 with various data ---
    print(f"\n=== PROBE 3: ACTION6 with various data (from pristine L7) ===")
    # Try every possible integer action_id, and unusual data shapes
    for data in [
        {'x': 0, 'y': 0}, {'x': 63, 'y': 63}, {'x': 32, 'y': 32},
        {}, {'x': 5, 'y': 5, 'extra': 'foo'},
    ]:
        env_d, g_d = fresh_L7(arcade)
        try:
            fd = env_d.step(GameAction.ACTION6, data=data)
            eqd = g_d.ikhhdzfmarl
            sd = get_state(eqd)
            diff_pieces = (sd['pieces'] != s0['pieces'])
            print(f"  data={data} won={sd['won']} lost={sd['lost']} level={sd['level']} pieces_changed={diff_pieces}")
        except Exception as e:
            print(f"  data={data} ERROR: {type(e).__name__}: {e}")

    # --- PROBE 4: ACTION5 ---
    print(f"\n=== PROBE 4: ACTION5 effects ===")
    env5, g5 = fresh_L7(arcade)
    for _ in range(3):
        env5.step(GameAction.ACTION5)
    s5 = get_state(g5.ikhhdzfmarl)
    print(f"  After 3× ACTION5: pieces={s5['pieces']} won={s5['won']}")

    # --- PROBE 5: call internal eq.win() ---
    print(f"\n=== PROBE 5: Call eq.win() directly ===")
    env_w, g_w = fresh_L7(arcade)
    eq_w = g_w.ikhhdzfmarl
    print(f"  before win(): iajuzrgttrv={eq_w.iajuzrgttrv}")
    try:
        eq_w.win()
        print(f"  after  win(): iajuzrgttrv={eq_w.iajuzrgttrv}")
        # Now try env.step - does it advance?
        fd = env_w.step(GameAction.ACTION1)
        print(f"  after step: state={fd.state.name} levels_completed={fd.levels_completed}")
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")

    # --- PROBE 6: try clicking at scrolled piece location ---
    # Right-N is at grid (22,6). offset is (5,5) initially.
    # cell_size=6, so pixel = (22*6+5+3, 6*6+5+3) = (140, 44) — off-screen (>63)
    # After a RIGHT push, offset might shift? Let's try a full sequence
    # of RIGHT pushes and see.
    print(f"\n=== PROBE 6: does offset change with pushes? ===")
    env6, g6 = fresh_L7(arcade)
    offs = [g6.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp]
    for act_name, act in [("U", GameAction.ACTION1), ("D", GameAction.ACTION2),
                           ("L", GameAction.ACTION3), ("R", GameAction.ACTION4)]*6:
        env6.step(act)
        offs.append((act_name, g6.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp))
    print(f"  offsets: {offs[:10]}")

    # --- PROBE 7: N-over-peg landing on block — unusual landing ---
    # (0,3) after pushes has block AND peg overlap? Check peg+block cells.
    print(f"\n=== PROBE 7: peg-on-block overlap cells ===")
    peg_block = s0['pegs'] & s0['blocks']
    print(f"  initial peg∩block: {sorted(peg_block)}")
    # These are cells where jumper lands on peg+block. Do they allow reducing?

    # --- PROBE 8: block-of-blocks adjacency check ---
    # Are any blocks adjacent? If so, pushing one into the other might cascade.
    print(f"\n=== PROBE 8: block adjacency ===")
    blks = s0['blocks']
    for (x, y) in sorted(blks):
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            if (x+dx, y+dy) in blks:
                print(f"  block ({x},{y}) adjacent to block ({x+dx},{y+dy})")

    # --- PROBE 9: Try ACTION6 click on piece THEN arrow where jump rule *should* fail ---
    # What if jump rule has edge cases we missed? Try clicking right-N then
    # clicking below/above/etc.
    print(f"\n=== PROBE 9: direct click on right-N ===")
    env9, g9 = fresh_L7(arcade)
    # Right-N at (22,6), with current offset (5,5), pixel = (22*6+5+3, 6*6+5+3) = (140, 44)
    eq9 = g9.ikhhdzfmarl
    off = eq9.hncnfaqaddg.cdpcbbnfdp
    # Try clicking — selection object aufxjsaidrw should change
    before_sel = eq9.aufxjsaidrw
    px, py = 22*6 + off[0] + 3, 6*6 + off[1] + 3
    print(f"  offset={off} trying click at pixel=({px},{py})")
    try:
        fd = env9.step(GameAction.ACTION6, data={'x': px, 'y': py})
        after_sel = g9.ikhhdzfmarl.aufxjsaidrw
        print(f"  before_sel={before_sel is None} after_sel={after_sel is not None}")
    except Exception as e:
        print(f"  ERROR: {e}")


if __name__ == '__main__':
    main()
