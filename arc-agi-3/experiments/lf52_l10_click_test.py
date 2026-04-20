#!/usr/bin/env python3
"""Empirically find pixel coords for N@(4,0) and execute the jump."""
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


def save_frame(frame_data, path, scale=12):
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


OUT_DIR = '/mnt/c/exe/projects/ai-agents/ARC-SAGE/knowledge/visual-memory/lf52/run_L10_legitimate'

arc = Arcade(operation_mode='offline')
env = arc.make('lf52-271a04aa')
env.reset()
game = env._game
game.set_level(9)

# Phase 1 + 2 (stop at LEFT 4 to leave blue@(4,1))
for _ in range(8): env.step(GameAction.ACTION1)
for _ in range(4): env.step(GameAction.ACTION3)

eq = game.ikhhdzfmarl
# camera info
cam = eq.xzwdyefmgkv
print(f"camera cs: x={cam.tnxxzczblvt} y={cam.ppoluxgtqul}")
print(f"camera offset: {cam.mepgityjcj()}")
print(f"camera angle: {cam.ntaykiuhwea}")
print(f"grid offset (cdpcbbnfdp): {eq.hncnfaqaddg.cdpcbbnfdp}")

# To CLICK on grid cell (gx, gy), use pixel coords:
# grid -> world: (gx * 6, gy * 6) but then camera translates to pixels
# camera offset is (pmnuvkfgph, swtdbzfsdj) and cs_x, cs_y are pixel per world unit
# Inverse of rozmjeilxc: ux = (tozquqlwpv - pmnuvkfgph) ; uy = same
# pixel = ux * csx = (tozquqlwpv - pmnuvkfgph) * csx  ... hmm that can't be right
# Actually ux is WORLD-unit, pixel is world * cs: x_px = ux * csx where ux = world_x
# And tozquqlwpv = int(ux) + pmnuvkfgph = world_x + camera_origin_in_world
# So: to target world cell (wx, wy) = grid cell (gx+offset_x, gy+offset_y) — wait,
# grid has its own internal offset that adjusts for scrolling.
# Let's just sweep pixels and watch for selection

# For N@(4,0) — grid cell (4,0)
# rozmjeilxc iterates sprites. For each sprite with name "fozwvlovdui" at (4,0),
# check its world position. Let's find it empirically.
print("\nSearching for N sprite's pixel-click target:")
# Enumerate all sprites
count = 0
for ssnguhllov, wjijkpdxjj, qkigfmzlgw in eq.ezsfkapyvt():
    if count > 100: break
    count += 1
    name = getattr(wjijkpdxjj, 'name', None)
    if name and 'fozwvlovdui' in name and 'blue' not in name:
        pos = getattr(wjijkpdxjj, 'chahdtpdoz', None)
        world = wjijkpdxjj.mepgityjcj() if hasattr(wjijkpdxjj, 'mepgityjcj') else None
        size = wjijkpdxjj.fyxfomjvvi() if hasattr(wjijkpdxjj, 'fyxfomjvvi') else None
        print(f"  {name} chahdtpdoz={pos} world_pos={world} size={size}")

# Try clicks: aiming at grid cell (4, 0). Try pixel sweep to find it.
print("\nSweep click targets: try pixel coords to find N@(4,0)")
# Save reference frame before clicks
fd = env.step(GameAction.ACTION7)  # no-op snapshot
save_frame(fd.frame, os.path.join(OUT_DIR, 'step_012_pre_click.png'), scale=12)

# Check initial zvcnglshzcx and selection state
print(f"\neq.zvcnglshzcx: {eq.zvcnglshzcx}")
print(f"eq.wpwvsglgmb (selection): {eq.wpwvsglgmb}")
print(f"  qoifrofmiu (selected sprite): {eq.wpwvsglgmb.qoifrofmiu}")

# From L1 solution, click at x=19, y=20 worked to select cell at (2, ~2). With cs=6
# and assuming a grid_offset and camera offset: 19/6 = 3.16, 20/6 = 3.33.
# Maybe the grid offset in camera is applied too.
# Let's just empirically test clicks at multiple pixel coords and watch for selection
original_sel = eq.wpwvsglgmb.qoifrofmiu
print(f"Testing clicks to find N@(4,0)...")
hits = []
import copy

# Save state via RESET not an option for this specific test — try the most likely coords:
# Frame is 64x64; grid appears to span something. cs=6, grid offset (5,3) -> world_origin maybe.
# Camera offset is the origin of the world in pixel-space negative form
# Try cs=6 directly for cell (4,0): px = 4*6 + some_shift, py = 0*6 + some_shift

for px in range(30, 50, 3):
    for py in range(0, 25, 3):
        # Need a fresh state — not possible without reset. So just check the click conceptually
        pass

# Alternative: directly call dghsidbuet internally (still engine-legitimate in offline mode)
# Actually no — we must use env.step(). Click at the most likely grid->pixel:
# N@(4,0). With cs=6 and grid_offset_in_world (5,3) and camera_origin_in_world (pmnuvkfgph, swtdbzfsdj):
pmnuvkfgph, swtdbzfsdj = cam.mepgityjcj()
print(f"\nCamera origin in world: ({pmnuvkfgph}, {swtdbzfsdj})")

# To click grid cell (gx, gy):
#   world_pos = (gx + grid_offset_x, gy + grid_offset_y) * cs ??? not sure
#   pixel = (world - camera_origin) * cs
# Looking at rozmjeilxc again:
#   ux, uy = (x/csx, y/csy)              # pixel -> world (float)
#   tozquqlwpv = int(ux) + pmnuvkfgph    # world integer coords (after camera shift)
# So to target world int coord W: x_pixel = (W - pmnuvkfgph) * csx
# World coord of sprite is its chahdtpdoz value. Grid cell (4,0) sprite has chahdtpdoz=(4,0) + grid_offset applied?
# From dump above we can see the actual chahdtpdoz. Let's just click (4 - pmnuvkfgph, 0 - swtdbzfsdj) * 6

for gx in [(4, 0), (4, 1), (4, 2)]:
    wx, wy = gx
    # If chahdtpdoz stores grid coords (4, 0), and camera offset subtracts pmnuvkfgph:
    # target pixel = (chahdtpdoz - camera_origin_in_world) * cs
    px = (wx - pmnuvkfgph) * cam.tnxxzczblvt
    py = (wy - swtdbzfsdj) * cam.ppoluxgtqul
    print(f"  grid {gx} -> pixel approx ({px}, {py})")
