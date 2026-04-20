#!/usr/bin/env python3
"""
lf52 L10 Winning Path — UP×8, RIGHT, LEFT, DOWN, LEFT×3 positions
blue@(4,1) AND block@(4,2), enabling N@(4,0) DOWN jump to (4,2).

Then: check if N can chain further jumps to reduce N count.
This is the FIRST PASS at finding a legitimate reducing jump.
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
from lf52_solve_final import extract_state, PuzzleState, DIRS, DIR_NAMES, DIR_ACTIONS, PALETTE

OUT_DIR = '/mnt/c/exe/projects/ai-agents/ARC-SAGE/knowledge/visual-memory/lf52/run_L10_legitimate'
CS = 6
OFF_X, OFF_Y = 5, 3


def grid_to_pixel_center(gx, gy):
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
        print(f"  save err: {e}")


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
        'blocks': sorted([list(p) for p in st['pushable']]),
        'pieces': by_type,
        'selected': getattr(sel, 'chahdtpdoz', None) if sel else None,
        'level': int(st['level']),
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
        if changed:
            save_frame(fd.frame, os.path.join(self.out_dir, f'winpath_{self.step_idx:03d}.png'))
        marker = '*' if changed else ' '
        entry = {
            'step': self.step_idx,
            'action': action.name if hasattr(action, 'name') else str(action),
            'data': data,
            'note': note,
            'pre_N': pre['pieces']['N'],
            'post_N': post['pieces']['N'],
            'pre_B': len(pre['pieces']['B']),
            'post_B': len(post['pieces']['B']),
            'pre_blocks': pre['blocks'],
            'post_blocks': post['blocks'],
            'post_selected': post['selected'],
            'changed': changed,
            'state': str(fd.state),
            'levels_completed': int(fd.levels_completed),
        }
        self.trace.append(entry)
        print(f"  [{self.step_idx:3d}]{marker} {entry['action']:<8s}{' data='+str(data) if data else '':<20s} "
              f"{note:<40s} N={post['pieces']['N']} sel={post['selected']} state={fd.state}")
        return fd, changed

    def save(self, meta):
        out = {**meta, 'total_steps': self.step_idx, 'trace': self.trace,
               'final': summarize(self.game)}
        with open(os.path.join(self.out_dir, 'run.json'), 'w') as f:
            json.dump(out, f, indent=2, default=str)


print("=" * 76)
print("lf52 L10 Winning-Path Legitimate Execution")
print("=" * 76)

arc = Arcade(operation_mode='offline')
env = arc.make('lf52-271a04aa')
env.reset()
game = env._game
game.set_level(9)
init = summarize(game)
print(f"L10 initial: N={init['pieces']['N']} blocks={init['blocks'][:3]}...")

fd = env.step(GameAction.ACTION7)  # snapshot
save_frame(fd.frame, os.path.join(OUT_DIR, 'winpath_000_initial.png'))

tracer = Tracer(env, game, OUT_DIR)

# Sequence: UP×8, RIGHT, LEFT, DOWN, LEFT×3
DIR_ACT = {
    'UP': GameAction.ACTION1, 'DOWN': GameAction.ACTION2,
    'LEFT': GameAction.ACTION3, 'RIGHT': GameAction.ACTION4,
}
seq = ['UP']*8 + ['RIGHT', 'LEFT', 'DOWN', 'LEFT', 'LEFT', 'LEFT']
print(f"\nSequence: {seq}")
for i, d in enumerate(seq):
    tracer.step(DIR_ACT[d], note=f'{d} {i+1}/{len(seq)}')

mid = summarize(game)
print(f"\nAfter pushes:")
print(f"  blocks: {mid['blocks']}")
print(f"  blue positions: {mid['pieces']['B']}")
print(f"  N positions: {mid['pieces']['N']}")

# Verify the critical configuration
pd_blue = set(tuple(p) for p in mid['pieces']['B'])
pd_blocks = set(tuple(p) for p in mid['blocks'])
print(f"\n  Blue@(4,1)? {'YES' if (4,1) in pd_blue else 'NO'}")
print(f"  Block@(4,2)? {'YES' if (4,2) in pd_blocks else 'NO'}")
print(f"  Block@(4,1)? {'YES' if (4,1) in pd_blocks else 'NO'}")

# Inspect engine-level jump validity
eq = game.ikhhdzfmarl
print(f"\n  Engine inspection at (4,0):")
for pos, label in [((4, 0), 'N'), ((4, 1), 'mid'), ((4, 2), 'dst')]:
    names = [o.name for o in eq.hncnfaqaddg.ijpoqzvnjt(*pos)]
    print(f"    {label}@{pos}: {names}")
print(f"  qikmikecdf((4,0), (0,1)): {eq.qikmikecdf((4, 0), (0, 1))}")

# -----------------------------------------------------------------------
# Now click N@(4,0) to select
# -----------------------------------------------------------------------
print("\n[Click] N@(4,0)")
px, py = grid_to_pixel_center(4, 0)
fd, ch = tracer.step(GameAction.ACTION6, data={'x': px, 'y': py}, note=f'click N@(4,0) px=({px},{py})')

mid2 = summarize(game)
print(f"\nAfter click: selected={mid2['selected']}")

if mid2['selected']:
    # Click DOWN arrow
    # Arrow sprites are at N + 2*dir * 6 world units from sprite — but we can click (4,2) directly
    ax, ay = grid_to_pixel_center(4, 2)
    print(f"\n[Click] DOWN arrow at (4,2) pixel=({ax},{ay})")
    fd, ch = tracer.step(GameAction.ACTION6, data={'x': ax, 'y': ay}, note=f'click DOWN arrow')
    post_jump = summarize(game)
    print(f"\nAfter jump attempt:")
    print(f"  N positions: {post_jump['pieces']['N']}")
    print(f"  B count: {len(post_jump['pieces']['B'])}")
    print(f"  blocks: {post_jump['blocks']}")
    print(f"  level: {post_jump['level']}")
    print(f"  state: {fd.state}")
else:
    print("  Selection failed — N@(4,0) not selected after click.")
    # Debug: check what qikmikecdf returns for each direction
    for d in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        ok = eq.qikmikecdf((4, 0), d)
        print(f"    qikmikecdf((4,0), {d}) = {ok}")

# -----------------------------------------------------------------------
# If jump succeeded (N now at (4,2)), check if N can continue
# -----------------------------------------------------------------------
post = summarize(game)
if [4, 2] in post['pieces']['N']:
    print("\n*** N moved to (4,2)! Now check if further jumps can reduce N count ***")
    eq = game.ikhhdzfmarl
    # N@(4,2) and N@(6,9). Can N@(4,2) jump somewhere that reduces?
    for d in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        ok = eq.qikmikecdf((4, 2), d)
        print(f"    N@(4,2) jump dir {d}: {ok}")

    # Click N@(4,2)
    px2, py2 = grid_to_pixel_center(4, 2)
    print(f"\n[Click] N@(4,2) pixel ({px2},{py2})")
    tracer.step(GameAction.ACTION6, data={'x': px2, 'y': py2}, note='click N@(4,2)')
    for d, dname in [((0, 1), 'DOWN'), ((0, -1), 'UP'), ((1, 0), 'RIGHT'), ((-1, 0), 'LEFT')]:
        target = (4 + 2*d[0], 2 + 2*d[1])
        if not (0 <= target[0] < 30 and 0 <= target[1] < 30):
            continue
        apx, apy = grid_to_pixel_center(*target)
        fd, ch = tracer.step(GameAction.ACTION6, data={'x': apx, 'y': apy},
                             note=f'try {dname} arrow -> ({target[0]},{target[1]})')
        if ch:
            post = summarize(game)
            print(f"    -> N after: {post['pieces']['N']}")
            if len(post['pieces']['N']) < 2:
                print(f"    *** WIN! N count reduced to {len(post['pieces']['N'])} ***")
                break
            # Re-select if N still at same position
            # Re-click last N pos
            if post['pieces']['N']:
                nx, ny = post['pieces']['N'][0]
                cpx, cpy = grid_to_pixel_center(nx, ny)
                tracer.step(GameAction.ACTION6, data={'x': cpx, 'y': cpy}, note=f'reselect N@({nx},{ny})')

# -----------------------------------------------------------------------
# Save
# -----------------------------------------------------------------------
meta = {
    'game': 'lf52-271a04aa',
    'level': 'L10',
    'method': 'game.set_level(9) — individual-level capture',
    'purpose': 'legitimate blue-on-cart reframe — push-only BFS discovered (blue@(4,1) AND block@(4,2))',
    'key_sequence': 'UP×8, RIGHT, LEFT, DOWN, LEFT×3 (14 pushes) + click N + click arrow',
    'rules': ['no eq.win() bypass', 'only env.step()'],
    'initial_state': init,
}
tracer.save(meta)

final = summarize(game)
print(f"\n" + "=" * 76)
print("FINAL:")
print(f"  N: {final['pieces']['N']}")
print(f"  B count: {len(final['pieces']['B'])}")
print(f"  blocks: {final['blocks']}")
print(f"  level: {final['level']}")
print(f"  selected: {final['selected']}")
