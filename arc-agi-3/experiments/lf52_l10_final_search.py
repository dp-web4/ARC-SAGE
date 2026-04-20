#!/usr/bin/env python3
"""Final deep push+jump BFS from L10 initial."""
import os, sys, json, time
from collections import deque
sys.setrecursionlimit(50000)
os.chdir('/mnt/c/exe/projects/ai-agents/SAGE')
os.environ['OPERATION_MODE'] = 'offline'
sys.path.insert(0, '.')
sys.path.insert(0, '/mnt/c/exe/projects/ai-agents/ARC-SAGE/arc-agi-3/experiments')
sys.stdout.reconfigure(line_buffering=True)

from arc_agi import Arcade
from arcengine import GameAction
from lf52_solve_final import extract_state, PuzzleState, DIRS, DIR_NAMES

arc = Arcade(operation_mode='offline')
env = arc.make('lf52-271a04aa')
env.reset()
game = env._game
game.set_level(9)
eq = game.ikhhdzfmarl
st = extract_state(eq)

initial = PuzzleState(
    frozenset((x, y, n) for (x, y), n in st['pieces'].items()),
    frozenset(st['pushable']),
    frozenset(st['walls']),
    frozenset(st['walkable']),
    frozenset(st['fixed_pegs']),
)

N = 'fozwvlovdui'
BLUE = 'fozwvlovdui_blue'

def count_N(s):
    return sum(1 for _, _, n in s.pieces if n == N)

def neighbors(state):
    for d in DIRS:
        ns = state.apply_push(d)
        if ns is not None:
            yield (('PUSH', DIR_NAMES[d]), ns)
    pd = state.piece_dict()
    for (sx, sy), name in pd.items():
        if name == BLUE: continue
        for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]:
            dst = (sx+2*dx, sy+2*dy)
            ns = state.apply_jump((sx, sy), dst)
            if ns is not None:
                yield (('JUMP', (sx,sy), (dx,dy)), ns)

INITIAL_N = count_N(initial)
print(f"Initial N count: {INITIAL_N}")

visited = {initial.key(): ()}
frontier = deque([(initial, ())])
max_depth = 30
best = INITIAL_N
best_path = None
start = time.time()
timeout = 300
states_at_depth = [0] * (max_depth + 1)

while frontier:
    if time.time() - start > timeout:
        print(f"  [timeout at {len(visited)} states]")
        break
    state, path = frontier.popleft()
    states_at_depth[len(path)] = states_at_depth[len(path)] + 1 if len(path) <= max_depth else 0
    n_now = count_N(state)
    if n_now < best:
        best = n_now
        best_path = path
        print(f"  *** depth {len(path)}: N count = {n_now} ***")
        if n_now == 1:
            print("  *** WIN! ***")
            break
    if len(path) >= max_depth:
        continue
    for action, ns in neighbors(state):
        k = ns.key()
        if k in visited:
            continue
        visited[k] = path + (action,)
        frontier.append((ns, path + (action,)))

print(f"\nFinal: visited={len(visited)}, best N = {best}")
print(f"States at each depth (samples): {[(d, states_at_depth[d]) for d in range(0, min(max_depth+1, len(states_at_depth)), 3)]}")

out = {
    'initial_N': INITIAL_N,
    'best_N': best,
    'states_visited': len(visited),
    'max_depth_searched': max_depth,
    'timeout_hit': time.time() - start > timeout,
    'elapsed_sec': time.time() - start,
    'best_path': [str(a) for a in (best_path or ())],
}
with open('/mnt/c/exe/projects/ai-agents/ARC-SAGE/knowledge/visual-memory/lf52/run_L10_legitimate/final_search.json', 'w') as f:
    json.dump(out, f, indent=2, default=str)
print(f"\n{json.dumps(out, indent=2, default=str)}")
