#!/usr/bin/env python3
"""
lf52 L10 Stage 2 — Now that N@(4,0) can jump to (4,2), what's next?

From (4,2), N needs to cross row 3/4 to reach N@(6,9). The row 2-3 area has
interior walls. Let's BFS from the post-jump state to see if ANY push+jump
sequence can deliver N@(4,2) to a cell where it can jump over N@(6,9).

Jump validity requires:
  - jumpable middle = any piece/peg
  - valid landing = (1 object with 'hupkpseyuim' in name) OR (2 objects incl 'hupkpseyuim2')

From (4,2), N has walls around it. The only escape is via UP (back to (4,0)).
"""
import os, sys, json
sys.setrecursionlimit(50000)
os.chdir('/mnt/c/exe/projects/ai-agents/SAGE')
os.environ['OPERATION_MODE'] = 'offline'
sys.path.insert(0, '.')
sys.path.insert(0, '/mnt/c/exe/projects/ai-agents/ARC-SAGE/arc-agi-3/experiments')
sys.stdout.reconfigure(line_buffering=True)

from collections import deque
from arc_agi import Arcade
from arcengine import GameAction
from lf52_solve_final import extract_state, PuzzleState, DIRS, DIR_NAMES

# Execute path to get to post-jump state
arc = Arcade(operation_mode='offline')
env = arc.make('lf52-271a04aa')
env.reset()
game = env._game
game.set_level(9)

DIR_ACT = {'UP': GameAction.ACTION1, 'DOWN': GameAction.ACTION2,
           'LEFT': GameAction.ACTION3, 'RIGHT': GameAction.ACTION4}
seq = ['UP']*8 + ['RIGHT', 'LEFT', 'DOWN', 'LEFT', 'LEFT', 'LEFT']
for d in seq:
    env.step(DIR_ACT[d])

eq = game.ikhhdzfmarl
st = extract_state(eq)
# Synthesize post-jump state: N@(4,0) -> N@(4,2), blue@(4,1) stays
pieces_set = set((x, y, n) for (x, y), n in st['pieces'].items())
pieces_set.discard((4, 0, 'fozwvlovdui'))
pieces_set.add((4, 2, 'fozwvlovdui'))
# blue@(4,1) stays (it's in st['pieces'] already)

post_jump = PuzzleState(
    frozenset(pieces_set),
    frozenset(st['pushable']),
    frozenset(st['walls']),
    frozenset(st['walkable']),
    frozenset(st['fixed_pegs']),
)

print(f"Post-jump state:")
print(f"  N positions: {sorted([(x,y) for x,y,n in post_jump.pieces if n == 'fozwvlovdui'])}")
print(f"  blue positions: {sorted([(x,y) for x,y,n in post_jump.pieces if n == 'fozwvlovdui_blue'])}")
print(f"  blocks: {sorted(post_jump.blocks)}")

N = 'fozwvlovdui'

def count_N(state):
    return sum(1 for _,_,n in state.pieces if n == N)

def n_jumps(state):
    out = []
    pd = state.piece_dict()
    for (sx, sy), name in pd.items():
        if name != N: continue
        for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]:
            dst = (sx+2*dx, sy+2*dy)
            ns = state.apply_jump((sx, sy), dst)
            if ns is not None:
                out.append(((sx,sy), (dx,dy), dst, count_N(ns)))
    return out

# BFS push+jump from post_jump state, look for REDUCING jumps
print("\n=== BFS push+jump to find any reduction of N count ===")
INITIAL_N = count_N(post_jump)
print(f"  Starting N count: {INITIAL_N}")

visited = {post_jump.key(): ()}
frontier = deque([(post_jump, ())])
max_depth = 15
best = INITIAL_N
best_path = None
seen_reducing = 0
import time
start = time.time()
timeout = 120

def neighbors(state):
    for d in DIRS:
        ns = state.apply_push(d)
        if ns is not None:
            yield (('PUSH', DIR_NAMES[d]), ns)
    pd = state.piece_dict()
    for (sx, sy), name in pd.items():
        if name == 'fozwvlovdui_blue': continue
        for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]:
            dst = (sx+2*dx, sy+2*dy)
            ns = state.apply_jump((sx, sy), dst)
            if ns is not None:
                yield (('JUMP', (sx,sy), (dx,dy)), ns)

while frontier:
    if time.time() - start > timeout:
        print(f"  [timeout after {len(visited)} states]")
        break
    state, path = frontier.popleft()
    n_now = count_N(state)
    if n_now < best:
        best = n_now
        best_path = path
        print(f"  *** New best: N count = {n_now} at depth {len(path)} ***")
        print(f"      path: {list(path)}")
        seen_reducing += 1
        if n_now == 1:
            print("  *** WIN state reached! ***")
            break
    if len(path) >= max_depth:
        continue
    for action, ns in neighbors(state):
        k = ns.key()
        if k in visited:
            continue
        new_path = path + (action,)
        visited[k] = new_path
        frontier.append((ns, new_path))

print(f"\n  Final: visited {len(visited)} states, best N count = {best}")

# Save result
out = {
    'starting_state': 'N@(4,2) after jump from N@(4,0)',
    'initial_N': INITIAL_N,
    'best_N_found': best,
    'states_searched': len(visited),
    'max_depth': max_depth,
    'reducing_path': [str(a) for a in (best_path or ())],
    'timeout_reached': time.time() - start > timeout,
}
path_out = '/mnt/c/exe/projects/ai-agents/ARC-SAGE/knowledge/visual-memory/lf52/run_L10_legitimate/stage2_bfs.json'
with open(path_out, 'w') as f:
    json.dump(out, f, indent=2, default=str)
print(f"\nSaved: {path_out}")
