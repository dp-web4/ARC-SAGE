#!/usr/bin/env python3
"""
lf52 L10 Full Legitimate Execution — blue-on-cart reframe with actual clicks.

Pixel conversion (confirmed): pixel_x = gx*6 + 5, pixel_y = gy*6 + 3

Sequence:
  1. 8x UP (ACTION1)
  2. 4x LEFT (ACTION3) — leaves blue@(4,1), block@(4,1)
  3. CLICK N@(4,0) at pixel (29, 3) — selects piece, shows arrows
  4. CLICK DOWN arrow at (4,2)'s pixel area — attempts jump
     - Arrow appears at position N + 2*dir, i.e. (4,2) pixel = (29, 15)
  5. Log resulting state

If no win: continue exploring post-jump possibilities.
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
os.makedirs(OUT_DIR, exist_ok=True)

CS = 6
OFF_X, OFF_Y = 5, 3


def grid_to_pixel(gx, gy):
    """Convert grid cell (gx, gy) to pixel (px, py) for ACTION6 click — center of cell."""
    return (gx * CS + OFF_X + CS // 2, gy * CS + OFF_Y + CS // 2)


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
    except Exception as e:
        print(f"  [save err] {e}")


def summarize(game):
    eq = game.ikhhdzfmarl
    st = extract_state(eq)
    by_type = {'N': [], 'R': [], 'B': []}
    for (x, y), name in st['pieces'].items():
        key = 'N' if name == 'fozwvlovdui' else ('R' if name == 'fozwvlovdui_red' else 'B')
        by_type[key].append([x, y])
    for k in by_type: by_type[k].sort()
    sel = eq.wpwvsglgmb.qoifrofmiu
    return {
        'level': int(st['level']),
        'blocks': sorted([list(p) for p in st['pushable']]),
        'pieces': by_type,
        'selected': getattr(sel, 'chahdtpdoz', None) if sel else None,
    }


class Tracer:
    def __init__(self, env, game, out_dir):
        self.env = env
        self.game = game
        self.out_dir = out_dir
        self.trace = []
        self.step_idx = 0

    def step(self, action, data=None, note=''):
        self.step_idx += 1
        pre = summarize(self.game)
        kw = {'data': data} if data is not None else {}
        fd = self.env.step(action, **kw)
        post = summarize(self.game)
        changed = pre != post
        entry = {
            'step': self.step_idx,
            'action': action.name if hasattr(action, 'name') else str(action),
            'data': data,
            'note': note,
            'pre_selected': pre.get('selected'),
            'post_selected': post.get('selected'),
            'pre_N': pre['pieces']['N'],
            'post_N': post['pieces']['N'],
            'pre_B_count': len(pre['pieces']['B']),
            'post_B_count': len(post['pieces']['B']),
            'pre_blocks': pre['blocks'],
            'post_blocks': post['blocks'],
            'changed': changed,
            'game_state': str(fd.state),
            'level': int(fd.levels_completed),
        }
        if changed:
            save_frame(fd.frame, os.path.join(self.out_dir, f'fullexec_{self.step_idx:03d}.png'))
            entry['frame'] = f'fullexec_{self.step_idx:03d}.png'
        marker = '*' if changed else ' '
        print(f"  [{self.step_idx:3d}] {marker} {entry['action']:<9s} {note:<40s} "
              f"sel={post.get('selected')} N={post['pieces']['N']} state={entry['game_state']}")
        self.trace.append(entry)
        return fd, changed

    def save(self, meta):
        out = {**meta, 'total_steps': self.step_idx, 'trace': self.trace,
               'final': summarize(self.game)}
        with open(os.path.join(self.out_dir, 'run.json'), 'w') as f:
            json.dump(out, f, indent=2, default=str)


print("=" * 76)
print("lf52 L10 Full Legitimate Execution")
print("=" * 76)

arc = Arcade(operation_mode='offline')
env = arc.make('lf52-271a04aa')
env.reset()
game = env._game
game.set_level(9)

init = summarize(game)
print(f"L10 initial: N={init['pieces']['N']} blocks={init['blocks'][:3]}...")
# save initial frame via a no-op ACTION7
fd = env.step(GameAction.ACTION7)
save_frame(fd.frame, os.path.join(OUT_DIR, 'fullexec_000_initial.png'))

tracer = Tracer(env, game, OUT_DIR)

# -----------------------------------------------------------------------
# Phase 1: 8x UP
# -----------------------------------------------------------------------
print("\n[Phase 1] 8x UP")
for i in range(8):
    tracer.step(GameAction.ACTION1, note=f'UP {i+1}/8')

# -----------------------------------------------------------------------
# Phase 2: 4x LEFT (stop early to leave blue@(4,1))
# -----------------------------------------------------------------------
print("\n[Phase 2] 4x LEFT — stops with blue@(4,1), block@(4,1)")
for i in range(4):
    tracer.step(GameAction.ACTION3, note=f'LEFT {i+1}/4')

mid = summarize(game)
print(f"\nAfter phase 2:")
print(f"  blocks: {mid['blocks']}")
print(f"  blue positions: {mid['pieces']['B']}")
print(f"  N positions: {mid['pieces']['N']}")
assert [4, 1] in mid['pieces']['B'], "blue not at (4,1)!"
assert [4, 1] in mid['blocks'], "block not at (4,1)!"

# -----------------------------------------------------------------------
# Phase 3: Click N@(4,0) to select, then click DOWN arrow to jump
# -----------------------------------------------------------------------
print("\n[Phase 3] Click N@(4,0) to select piece (showing arrows)")
px, py = grid_to_pixel(4, 0)  # (29, 3)
print(f"  N@(4,0) pixel = ({px}, {py})")
tracer.step(GameAction.ACTION6, data={'x': px, 'y': py},
            note=f'CLICK N@(4,0) pixel ({px},{py}) — select')

after_sel = summarize(game)
print(f"  After click: selected = {after_sel['selected']}")

# Arrows are displayed at 2*dir from piece. DOWN arrow for N@(4,0) is at (4,2).
# But arrow offsets use (dx*2*6, dy*2*6) — 12 world units in the direction.
# Arrow is a separate sprite. Let's just click at grid cell (4, 2) pixel.
print("\n[Phase 3b] Click DOWN arrow for jump to (4,2)")
px2, py2 = grid_to_pixel(4, 2)  # (29, 15)
print(f"  (4,2) pixel = ({px2}, {py2})")
tracer.step(GameAction.ACTION6, data={'x': px2, 'y': py2},
            note=f'CLICK DOWN arrow pixel ({px2},{py2}) — attempt jump')

after_jump = summarize(game)
print(f"\nAfter jump attempt:")
print(f"  N positions: {after_jump['pieces']['N']}")
print(f"  B positions: {after_jump['pieces']['B']}")
print(f"  blocks: {after_jump['blocks']}")

# -----------------------------------------------------------------------
# Phase 4: If N moved to (4,2), explore continuing
# -----------------------------------------------------------------------
n_positions = [tuple(p) for p in after_jump['pieces']['N']]
if (4, 2) in n_positions:
    print("\n[Phase 4] N moved to (4,2). Explore continuations.")

    # Now what? N@(4,2) is on a wall. Can it jump further?
    # Check neighborhood
    eq = game.ikhhdzfmarl
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        mid = (4 + dx, 2 + dy)
        dst = (4 + 2*dx, 2 + 2*dy)
        mid_objs = eq.hncnfaqaddg.ijpoqzvnjt(*mid)
        dst_objs = eq.hncnfaqaddg.ijpoqzvnjt(*dst)
        print(f"  N@(4,2) dir=({dx:+d},{dy:+d}) mid={mid}:{[o.name for o in mid_objs]} dst={dst}:{[o.name for o in dst_objs]}")

    # Try more pushes to see if we can open a path for N@(4,2) toward N@(6,9)
    # The other N is at (6,9) — very far away. We need them to meet.
    # N@(4,2) jump DOWN over (4,3)?
    print("\n  Try DOWN push to shift blocks under N")
    tracer.step(GameAction.ACTION2, note='DOWN push post-jump')
    # Try to jump N@(4,2) further
    # Re-click and try
    print("\n  Click N (should now be at new position)")
    n_post = summarize(game)['pieces']['N']
    for npos in n_post:
        nx, ny = npos
        npx, npy = grid_to_pixel(nx, ny)
        print(f"    N@({nx},{ny}) pixel=({npx},{npy})")
        tracer.step(GameAction.ACTION6, data={'x': npx, 'y': npy},
                    note=f'click N@({nx},{ny})')
        # Try each direction
        for dx, dy, dname in [(0,1,'DOWN'), (0,-1,'UP'), (1,0,'RIGHT'), (-1,0,'LEFT')]:
            tx, ty = nx + 2*dx, ny + 2*dy
            tpx, tpy = grid_to_pixel(tx, ty)
            fd, changed = tracer.step(GameAction.ACTION6, data={'x': tpx, 'y': tpy},
                                       note=f'try jump {dname} to ({tx},{ty})')
            if changed:
                # A jump worked — check N positions
                post = summarize(game)
                new_n = post['pieces']['N']
                if new_n != n_post:
                    print(f"    *** Jump succeeded: N moved from {n_post} to {new_n}")
                    if len(new_n) < len(n_post):
                        print(f"    *** WIN: N count reduced!")
                        break
                    n_post = new_n
                # Re-select
                npx, npy = grid_to_pixel(new_n[0][0], new_n[0][1]) if new_n else (nx, ny)
                tracer.step(GameAction.ACTION6, data={'x': npx, 'y': npy},
                           note=f'reselect N')

else:
    print(f"\n[Phase 4] Jump didn't execute or N didn't move to (4,2).")
    print(f"  Current N positions: {n_positions}")

# -----------------------------------------------------------------------
# Save full trace
# -----------------------------------------------------------------------
meta = {
    'game': 'lf52-271a04aa',
    'level': 'L10',
    'method': 'game.set_level(9) — individual-level capture',
    'purpose': 'legitimate blue-on-cart reframe with click-based N jump',
    'pixel_conversion': 'px = gx*6+5, py = gy*6+3',
    'rules': ['no eq.win() bypass', 'only env.step()', 'full trace logged'],
    'initial': init,
}
tracer.save(meta)

final = summarize(game)
print(f"\n" + "=" * 76)
print("FINAL STATE:")
print(f"  N positions: {final['pieces']['N']}")
print(f"  B count: {len(final['pieces']['B'])}")
print(f"  blocks: {final['blocks']}")
print(f"  selected: {final['selected']}")
print(f"  game level: {final['level']}")
print(f"\nTotal actions: {tracer.step_idx}")
