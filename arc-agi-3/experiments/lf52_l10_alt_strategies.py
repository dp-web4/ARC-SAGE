#!/usr/bin/env python3
"""
lf52 L10 Alternative Strategies — try to position simultaneously:
  - blue at (4,1) — to be the jumpable middle
  - block at (4,2) — to form a valid (wall+block) landing

Key insight: in the verified 8UP+4LEFT path, the block originally at (4,2)
gets pushed up to (4,1), so (4,2) becomes empty.

Alternative: can we transport a BLUE piece to (4,1) WITHOUT displacing the
block at (4,2)? Try approaches:
  A) Pre-push blocks at row 2 downward first to preserve them somewhere else
  B) Use only blocks from the x=8 column (they come from rows 9-13 — leaves
     row 2 untouched) — BUT pushing UP moves ALL blocks including row-2 ones.
  C) Push LEFT or DOWN first to move row-2 blocks off column 4.

Test each.
"""
import os, sys, json
sys.setrecursionlimit(50000)
os.chdir('/mnt/c/exe/projects/ai-agents/SAGE')
os.environ['OPERATION_MODE'] = 'offline'
sys.path.insert(0, '.')
sys.path.insert(0, '/mnt/c/exe/projects/ai-agents/ARC-SAGE/arc-agi-3/experiments')
sys.stdout.reconfigure(line_buffering=True)

from arc_agi import Arcade
from arcengine import GameAction
from lf52_solve_final import extract_state, PuzzleState, DIRS, DIR_NAMES


def fresh_state():
    arc = Arcade(operation_mode='offline')
    env = arc.make('lf52-271a04aa')
    env.reset()
    game = env._game
    game.set_level(9)
    eq = game.ikhhdzfmarl
    st = extract_state(eq)
    return PuzzleState(
        frozenset((x, y, n) for (x, y), n in st['pieces'].items()),
        frozenset(st['pushable']),
        frozenset(st['walls']),
        frozenset(st['walkable']),
        frozenset(st['fixed_pegs']),
    )

BLUE = 'fozwvlovdui_blue'
N = 'fozwvlovdui'

def describe(state, tag):
    blue_positions = sorted([(x, y) for x, y, n in state.pieces if n == BLUE])
    n_positions = sorted([(x, y) for x, y, n in state.pieces if n == N])
    blocks = sorted(state.blocks)
    print(f"  [{tag}] N={n_positions} blue={blue_positions[:5]}... blocks={blocks}")

def apply_seq(state, seq):
    """Apply a sequence of push directions."""
    for d in seq:
        ns = state.apply_push(d)
        if ns is None:
            return None
        state = ns
    return state

def check_n_down_jump_possible(state):
    """Can N@(4,0) jump DOWN to (4,2)?"""
    pd = state.piece_dict()
    if (4, 0) not in pd or pd[(4, 0)] != N:
        return False, "N not at (4,0)"
    # middle (4,1) jumpable?
    mid_piece = pd.get((4, 1))
    if mid_piece is None:
        return False, "no piece at middle (4,1)"
    # landing (4,2) valid? need block there
    landing_has_block = (4, 2) in state.blocks
    landing_has_wall = (4, 2) in state.walls
    landing_walkable = (4, 2) in state.walkable
    piece_at_land = (4, 2) in state.piece_positions()
    if piece_at_land:
        return False, "piece at landing (4,2)"
    # Rule: len==2 with block; wall+block should work
    if landing_has_block and landing_has_wall:
        return True, "block+wall at (4,2)"
    if landing_has_block and landing_walkable:
        return True, "block+walkable at (4,2) — need to check"
    return False, f"landing (4,2): block={landing_has_block} wall={landing_has_wall} walkable={landing_walkable}"


initial = fresh_state()
describe(initial, "INITIAL")

# Sanity: check (4,2) initial state
print(f"\n  (4,2) initial: wall={'y' if (4,2) in initial.walls else 'n'} "
      f"walkable={'y' if (4,2) in initial.walkable else 'n'} "
      f"block={'y' if (4,2) in initial.blocks else 'n'}")
print(f"  (4,1) initial: wall={'y' if (4,1) in initial.walls else 'n'} "
      f"walkable={'y' if (4,1) in initial.walkable else 'n'} "
      f"block={'y' if (4,1) in initial.blocks else 'n'}")

# -----------------------------------------------------------------------
# Attempt A: alternate pushes. Maybe push DOWN first to move (4,2) block
# away so later when we push UP, only the x=8 block moves (not (4,2)).
# BUT: (4,2) block surrounded by walls, can it go DOWN? (4,3) has wall-t.
# Let's check.
# -----------------------------------------------------------------------
print("\n=== A: DOWN first (to preserve row-2 blocks out of y=2) ===")
s = initial.apply_push((0, 1))  # DOWN
if s:
    describe(s, "DOWN")
else:
    print("  DOWN failed")

print("\n=== B: LEFT first to move row-2 blocks off column 4 ===")
s = initial.apply_push((-1, 0))  # LEFT
if s:
    describe(s, "LEFT")

print("\n=== C: Combined — LEFT then RIGHT to cycle row-2 blocks ===")
s = initial
for d, name in [((-1, 0), 'LEFT'), ((-1, 0), 'LEFT'), ((1, 0), 'RIGHT'), ((1, 0), 'RIGHT'), ((1, 0), 'RIGHT')]:
    ns = s.apply_push(d)
    if ns is None:
        print(f"  {name} blocked")
        break
    s = ns
    describe(s, name)

# -----------------------------------------------------------------------
# Attempt D: Use BFS to find ANY state where both (4,1) has blue AND (4,2) has block
# -----------------------------------------------------------------------
print("\n=== D: BFS for (blue@(4,1) AND block@(4,2)) configuration ===")
from collections import deque
visited = {initial.key(): ()}
frontier = deque([(initial, ())])
found_configs = []
max_depth = 15
while frontier:
    state, path = frontier.popleft()
    if len(path) > max_depth:
        continue
    pd = state.piece_dict()
    has_blue_at_41 = pd.get((4, 1)) == BLUE
    has_block_at_42 = (4, 2) in state.blocks
    if has_blue_at_41 and has_block_at_42:
        found_configs.append((len(path), path, state))
        if len(found_configs) <= 5:
            print(f"  [d={len(path)}] path={[DIR_NAMES[d] for d in path]}")
        if len(found_configs) >= 10:
            break
    for d in DIRS:
        ns = state.apply_push(d)
        if ns is None:
            continue
        k = ns.key()
        if k in visited:
            continue
        visited[k] = path + (d,)
        frontier.append((ns, path + (d,)))

print(f"\nTotal (blue@(4,1) AND block@(4,2)) configs found: {len(found_configs)}")

# Also try: jumpable middle at (4,1) AND block+wall at (4,2) — the full jump condition
print("\n=== E: BFS for any jumpable-middle at (4,1) AND valid landing at (4,2) ===")
visited2 = {initial.key(): ()}
frontier2 = deque([(initial, ())])
found_jumps = []
while frontier2:
    state, path = frontier2.popleft()
    if len(path) > max_depth:
        continue
    ok, reason = check_n_down_jump_possible(state)
    if ok:
        found_jumps.append((len(path), path, state, reason))
        if len(found_jumps) <= 5:
            print(f"  [d={len(path)}] ({reason}) path={[DIR_NAMES[d] for d in path]}")
        if len(found_jumps) >= 10:
            break
    for d in DIRS:
        ns = state.apply_push(d)
        if ns is None:
            continue
        k = ns.key()
        if k in visited2:
            continue
        visited2[k] = path + (d,)
        frontier2.append((ns, path + (d,)))

print(f"\nTotal valid N@(4,0) DOWN jump configs (push-only): {len(found_jumps)}")

# Save analysis
out = {
    'initial_42_wall': (4, 2) in initial.walls,
    'initial_42_walkable': (4, 2) in initial.walkable,
    'initial_42_block': (4, 2) in initial.blocks,
    'initial_41_wall': (4, 1) in initial.walls,
    'initial_41_walkable': (4, 1) in initial.walkable,
    'bfs_blue_at_41_and_block_at_42': len(found_configs),
    'bfs_valid_down_jump_configs': len(found_jumps),
    'max_depth_searched': max_depth,
    'states_searched': len(visited2),
}
with open('/mnt/c/exe/projects/ai-agents/ARC-SAGE/knowledge/visual-memory/lf52/run_L10_legitimate/alt_strategies.json', 'w') as f:
    json.dump(out, f, indent=2)
print(f"\nSummary: {out}")
