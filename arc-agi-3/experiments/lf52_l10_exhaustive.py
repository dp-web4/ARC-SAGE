#!/usr/bin/env python3
"""
lf52 L10 exhaustive legitimate search — try every reachable state (pushes only)
to see if ANY gets a valid reducing jump for N count.

Strategy:
  - BFS over (blocks, pieces, level) state from L10 initial
  - 4 push actions per state (UP/DOWN/LEFT/RIGHT)
  - At each state, probe: does the engine allow any click+arrow jump that
    reduces an N piece (via N-over-N jump)?
  - Report best states found.

Uses only env.step()-equivalent push actions at the engine level. Click jumps
are tested conceptually through the extracted state's "would be valid" check
(matching engine's posalhhmjq / pymqmlkgzs semantics, already validated).
"""
import os, sys, json, heapq, time
from collections import deque
sys.setrecursionlimit(50000)
os.chdir('/mnt/c/exe/projects/ai-agents/SAGE')
os.environ['OPERATION_MODE'] = 'offline'
sys.path.insert(0, '.')
sys.path.insert(0, '/mnt/c/exe/projects/ai-agents/ARC-SAGE/arc-agi-3/experiments')
sys.stdout.reconfigure(line_buffering=True)

from arc_agi import Arcade
from arcengine import GameAction
from lf52_solve_final import extract_state, PuzzleState, DIRS, DIR_NAMES, DIR_ACTIONS

arc = Arcade(operation_mode='offline')
env = arc.make('lf52-271a04aa')
env.reset()
game = env._game
game.set_level(9)
eq = game.ikhhdzfmarl
st = extract_state(eq)

# Build a PuzzleState to use the already-validated push simulation
pieces = frozenset((x, y, n) for (x, y), n in st['pieces'].items())
blocks = frozenset(st['pushable'])
walls = frozenset(st['walls'])
walkable = frozenset(st['walkable'])
fixed_pegs = frozenset(st['fixed_pegs'])

initial = PuzzleState(pieces, blocks, walls, walkable, fixed_pegs)
print(f"Initial: {len(pieces)} pieces, {len(blocks)} blocks, {len(walls)} walls")

N_name = 'fozwvlovdui'
BLUE_name = 'fozwvlovdui_blue'

def count_N(state):
    return sum(1 for _, _, n in state.pieces if n == N_name)

def n_positions(state):
    return [(x, y) for x, y, n in state.pieces if n == N_name]

def find_reducing_jumps(state):
    """Return list of (src, direction, dst) valid jumps that reduce N count."""
    found = []
    pd = state.piece_dict()
    for (sx, sy), name in pd.items():
        if name != N_name:
            continue
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            mid = (sx + dx, sy + dy)
            dst = (sx + 2*dx, sy + 2*dy)
            new_state = state.apply_jump((sx, sy), dst)
            if new_state is not None:
                new_count = count_N(new_state)
                if new_count < count_N(state):
                    found.append((sx, sy, dx, dy, dst))
    return found

# Also check "getting N onto a block" which could move it
def find_any_valid_jump_for_N(state):
    """Any valid jump where an N moves (even if not reducing)."""
    found = []
    pd = state.piece_dict()
    for (sx, sy), name in pd.items():
        if name != N_name:
            continue
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            dst = (sx + 2*dx, sy + 2*dy)
            new_state = state.apply_jump((sx, sy), dst)
            if new_state is not None:
                found.append((sx, sy, dx, dy, dst))
    return found

# -----------------------------------------------------------------------
# Round 1: pushes-only reachability. For each reachable state, test N jumps.
# -----------------------------------------------------------------------
print("\n=== Round 1: push-only BFS to find states with N jumps ===")
start = time.time()
visited = {initial.key(): []}
frontier = deque([(initial, [])])
best_states = []  # (depth, state, path, jumps)
max_depth = 20
states_with_n_jumps = 0
states_with_reducing = 0

while frontier:
    state, path = frontier.popleft()
    if len(path) > max_depth:
        continue
    # Check for N jumps
    red = find_reducing_jumps(state)
    any_nj = find_any_valid_jump_for_N(state)
    if red:
        states_with_reducing += 1
        best_states.append((len(path), state, path, 'REDUCING', red))
        print(f"  [d={len(path)}] REDUCING JUMP FOUND: path={[DIR_NAMES[d] for d in path]}")
        for j in red:
            print(f"      jump src=({j[0]},{j[1]}) dir=({j[2]},{j[3]}) dst={j[4]}")
        if states_with_reducing >= 5:
            break
    elif any_nj:
        states_with_n_jumps += 1
        if states_with_n_jumps <= 10:
            best_states.append((len(path), state, path, 'ANY_N', any_nj))
    # Expand
    for d in DIRS:
        new_state = state.apply_push(d)
        if new_state is None:
            continue
        k = new_state.key()
        if k in visited:
            continue
        new_path = path + [d]
        visited[k] = new_path
        frontier.append((new_state, new_path))

elapsed = time.time() - start
print(f"\nBFS complete: {len(visited)} states visited in {elapsed:.1f}s")
print(f"  States with reducing N jumps: {states_with_reducing}")
print(f"  States with any N jump: {states_with_n_jumps}")

# -----------------------------------------------------------------------
# Dump best states found
# -----------------------------------------------------------------------
print("\n=== Top 10 reachable states with N-jumps ===")
for depth, state, path, kind, jumps in best_states[:10]:
    print(f"\n  depth={depth} kind={kind} path={[DIR_NAMES[d] for d in path]}")
    print(f"    N positions: {n_positions(state)}")
    print(f"    jumps: {jumps[:5]}")

# -----------------------------------------------------------------------
# Deep: chain pushes + jumps (PuzzleState unified BFS)
# -----------------------------------------------------------------------
print("\n=== Round 2: push+jump BFS, up to depth 15 ===")
start = time.time()

def neighbors(state):
    """Generate all (action_label, next_state)."""
    for d in DIRS:
        ns = state.apply_push(d)
        if ns is not None:
            yield (('PUSH', DIR_NAMES[d]), ns)
    # Enumerate all jumps from every piece (non-blue source)
    pd = state.piece_dict()
    for (sx, sy), name in pd.items():
        if name == BLUE_name:
            continue  # blue can jump per engine, but for N reduction we jump N
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            dst = (sx + 2*dx, sy + 2*dy)
            ns = state.apply_jump((sx, sy), dst)
            if ns is not None:
                yield (('JUMP', (sx, sy), (dx, dy)), ns)

INITIAL_N = count_N(initial)
print(f"  Initial N count: {INITIAL_N}")

visited2 = {initial.key(): ('INIT',)}
frontier2 = deque([(initial, ())])
max_depth2 = 18
best_reduction = 0
first_reducing = None
explored = 0
timeout = 60
while frontier2:
    state, path = frontier2.popleft()
    explored += 1
    if time.time() - start > timeout:
        print(f"  (timeout at explored={explored}, depth<={len(path)})")
        break
    if len(path) > max_depth2:
        continue
    n_now = count_N(state)
    reduction = INITIAL_N - n_now
    if reduction > best_reduction:
        best_reduction = reduction
        first_reducing = (path, state)
        print(f"  [explored={explored}] N count reduced to {n_now} at depth {len(path)}: path={list(path)[:20]}")
        if n_now == 1:
            print(f"  *** WIN STATE (N count = 1) ***")
            break
    for action, ns in neighbors(state):
        k = ns.key()
        if k in visited2:
            continue
        new_path = path + (action,)
        visited2[k] = new_path
        frontier2.append((ns, new_path))

elapsed2 = time.time() - start
print(f"\nRound 2 complete: {len(visited2)} states visited in {elapsed2:.1f}s")
print(f"  Best reduction: {best_reduction} (from N={INITIAL_N})")

# -----------------------------------------------------------------------
# Save summary
# -----------------------------------------------------------------------
summary = {
    'initial_N': INITIAL_N,
    'round1_states': len(visited),
    'round1_reducing_jumps': states_with_reducing,
    'round1_any_N_jumps': states_with_n_jumps,
    'round1_best_states': [
        {
            'depth': d,
            'path': [DIR_NAMES[dd] for dd in p],
            'kind': k,
            'n_positions': n_positions(s),
            'jumps': [list(j) for j in js[:5]],
        }
        for d, s, p, k, js in best_states[:20]
    ],
    'round2_states': len(visited2),
    'round2_best_reduction': best_reduction,
    'round2_path_to_best': [str(a) for a in (first_reducing[0] if first_reducing else ())],
    'timeout_reached': time.time() - start > timeout,
}
out = '/mnt/c/exe/projects/ai-agents/ARC-SAGE/knowledge/visual-memory/lf52/run_L10_legitimate/exhaustive_search.json'
with open(out, 'w') as f:
    json.dump(summary, f, indent=2, default=str)
print(f"\nSaved summary: {out}")
