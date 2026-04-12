#!/usr/bin/env python3
"""
bp35 Platformer Puzzle Solver

Parses the bp35.py game source to extract ASCII grid levels, then uses BFS
to find optimal sequences of LEFT/RIGHT/CLICK actions to reach the gem.

Key mechanics:
  - Player moves horizontally (LEFT/RIGHT). Gravity is upward by default.
  - vivnprldht=True => gravity dy=-1 (fall upward toward lower row indices).
  - CLICK on 'x' (ground) tile destroys it.
  - CLICK on 'g' (lrpkmzabbfa) flips gravity direction.
  - Player falls through empty/passthrough cells.
  - Landing on gem = win. Landing on spikes = lose.

Actions: 3=LEFT, 4=RIGHT, 6=CLICK(x,y), 7=UNDO

Usage:
    python bp35_solver.py [--level N] [--source PATH]
"""

import re
import sys
import argparse
from collections import deque
from typing import Dict, List, Optional, Tuple, Set, FrozenSet

# ---------------------------------------------------------------------------
# Source path
# ---------------------------------------------------------------------------

def find_source():
    import glob
    pattern = "/Users/dennispalatov/repos/shared-context/environment_files/bp35/*/bp35.py"
    matches = glob.glob(pattern)
    return matches[0] if matches else None


def parse_source(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def extract_grids(source: str) -> Dict[str, List[List[str]]]:
    """Extract grid maps from tjdtolkmxo dict."""
    grids = {}
    grid_pattern = re.compile(r'"(grid\d+)":\s*qipeamczaw\(\s*\[', re.DOTALL)

    for m in grid_pattern.finditer(source):
        grid_name = m.group(1)
        start = m.end() - 1
        bracket_depth = 0
        pos = start
        for i in range(start, len(source)):
            if source[i] == '[':
                bracket_depth += 1
            elif source[i] == ']':
                bracket_depth -= 1
                if bracket_depth == 0:
                    pos = i + 1
                    break

        list_str = source[start:pos]
        reversed_grid = "[::-1]" in source[pos:pos+10]
        rows = re.findall(r'"([^"]*)"', list_str)
        if reversed_grid:
            rows = rows[::-1]
        grid = [list(row) for row in rows]
        grids[grid_name] = grid

    return grids


# ---------------------------------------------------------------------------
# Level data
# ---------------------------------------------------------------------------

class LevelData:
    def __init__(self, index: int, grid: List[List[str]]):
        self.index = index
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0]) if grid else 0
        self.player_pos = None
        self.gem_pos = None
        self.clickable_x = set()  # positions of 'x' tiles
        self.gravity_flips = set()  # positions of 'g' tiles
        self.clickable_1 = set()  # positions of '1' tiles

        for r, row in enumerate(grid):
            for c, ch in enumerate(row):
                if ch == 'n':
                    self.player_pos = (c, r)
                elif ch == '+':
                    self.gem_pos = (c, r)
                elif ch == 'x':
                    self.clickable_x.add((c, r))
                elif ch == 'g':
                    self.gravity_flips.add((c, r))
                elif ch == '1':
                    self.clickable_1.add((c, r))

    def cell_at(self, col: int, row: int) -> str:
        if row < 0 or row >= self.height or col < 0 or col >= self.width:
            return 'o'
        return self.grid[row][col]


def is_air(ch: str, destroyed: frozenset, col: int, row: int) -> bool:
    """Check if cell is passable (player falls through)."""
    if (col, row) in destroyed:
        return True
    return ch in (' ', '2', 'm', 'n')  # air, passthrough, moving platform, player start


def is_walkable_into(ch: str, destroyed: frozenset, col: int, row: int) -> bool:
    """Check if player can move horizontally into this cell."""
    if (col, row) in destroyed:
        return True
    return ch in (' ', '2', 'm', 'n', '+', 'v', 'u')  # air, passthrough, gem, spikes


def simulate_fall(level: LevelData, col: int, row: int, grav_up: bool,
                  destroyed: frozenset) -> Tuple[Tuple[int, int], str]:
    """Simulate gravity fall. Returns (final_pos, outcome).
    outcome: 'land', 'gem', 'spike'
    """
    dy = -1 if grav_up else 1
    prev = (col, row)
    nr = row + dy

    while True:
        if nr < 0 or nr >= level.height:
            return prev, 'land'
        ch = level.cell_at(col, nr)
        if is_air(ch, destroyed, col, nr):
            prev = (col, nr)
            nr += dy
            continue
        if ch == '+':
            return (col, nr), 'gem'
        if ch in ('v', 'u'):
            return prev, 'spike'
        # Solid - land on prev
        return prev, 'land'


def try_horizontal_move(level: LevelData, col: int, row: int, dcol: int,
                        grav_up: bool, destroyed: frozenset):
    """Try moving player horizontally.
    Returns: ('win',) or ('dead',) or ('ok', new_col, new_row) or None (blocked).
    """
    nc = col + dcol
    if nc < 0 or nc >= level.width:
        return None

    ch = level.cell_at(nc, row)
    if (nc, row) in destroyed:
        ch = ' '

    if not is_walkable_into(ch, destroyed, nc, row):
        return None  # blocked

    if ch == '+':
        return ('win',)

    # Player moved to (nc, row), now apply gravity
    final_pos, outcome = simulate_fall(level, nc, row, grav_up, destroyed)
    if outcome == 'gem':
        return ('win',)
    if outcome == 'spike':
        return ('dead',)
    return ('ok', final_pos[0], final_pos[1])


# ---------------------------------------------------------------------------
# BFS Solver
# ---------------------------------------------------------------------------

def solve_level(level: LevelData, max_steps: int = 50) -> Optional[List]:
    """BFS to find solution.

    State: (col, row, gravity_up, destroyed_tiles_frozen)
    Actions: LEFT, RIGHT, CLICK on specific tile
    """
    if level.player_pos is None or level.gem_pos is None:
        return None

    start_col, start_row = level.player_pos
    grav_up = True
    destroyed = frozenset()

    init_state = (start_col, start_row, grav_up, destroyed)
    visited: Set = set()
    visited.add(init_state)
    queue = deque()
    queue.append((init_state, []))

    while queue:
        state, actions = queue.popleft()
        if len(actions) >= max_steps:
            continue

        col, row, grav_up, dest = state

        # Try LEFT
        result = try_horizontal_move(level, col, row, -1, grav_up, dest)
        if result is not None:
            if result[0] == 'win':
                return actions + [('LEFT',)]
            elif result[0] == 'ok':
                new_state = (result[1], result[2], grav_up, dest)
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, actions + [('LEFT',)]))

        # Try RIGHT
        result = try_horizontal_move(level, col, row, 1, grav_up, dest)
        if result is not None:
            if result[0] == 'win':
                return actions + [('RIGHT',)]
            elif result[0] == 'ok':
                new_state = (result[1], result[2], grav_up, dest)
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, actions + [('RIGHT',)]))

        # Try CLICK on 'x' tiles (destroy ground)
        # Only consider tiles in player's column or adjacent columns,
        # and tiles that are below/above player (in gravity direction)
        dy_grav = -1 if grav_up else 1
        relevant_x = [(cc, cr) for (cc, cr) in level.clickable_x
                       if (cc, cr) not in dest and
                       (abs(cc - col) <= 2 or  # near player column
                        cr == row + dy_grav or  # directly below/above
                        (cc == col and ((dy_grav < 0 and cr < row) or
                                        (dy_grav > 0 and cr > row))))]
        for (cc, cr) in relevant_x:
            new_dest = dest | frozenset([(cc, cr)])

            # After destroying, check if player falls
            final_pos, outcome = simulate_fall(level, col, row, grav_up, new_dest)
            if outcome == 'gem':
                return actions + [('CLICK', cc, cr)]
            if outcome == 'spike':
                continue
            new_state = (final_pos[0], final_pos[1], grav_up, new_dest)
            if new_state not in visited:
                visited.add(new_state)
                queue.append((new_state, actions + [('CLICK', cc, cr)]))

        # Try CLICK on '1' tiles (boundary toggle - acts like destroy)
        relevant_1 = [(cc, cr) for (cc, cr) in level.clickable_1
                       if (cc, cr) not in dest and abs(cc - col) <= 3]
        for (cc, cr) in relevant_1:
            new_dest = dest | frozenset([(cc, cr)])
            final_pos, outcome = simulate_fall(level, col, row, grav_up, new_dest)
            if outcome == 'gem':
                return actions + [('CLICK', cc, cr)]
            if outcome == 'spike':
                continue
            new_state = (final_pos[0], final_pos[1], grav_up, new_dest)
            if new_state not in visited:
                visited.add(new_state)
                queue.append((new_state, actions + [('CLICK', cc, cr)]))

        # Try CLICK on 'g' tiles (gravity flip)
        for (cc, cr) in level.gravity_flips:
            new_grav = not grav_up
            final_pos, outcome = simulate_fall(level, col, row, new_grav, dest)
            if outcome == 'gem':
                return actions + [('CLICK', cc, cr)]
            if outcome == 'spike':
                continue
            new_state = (final_pos[0], final_pos[1], new_grav, dest)
            if new_state not in visited:
                visited.add(new_state)
                queue.append((new_state, actions + [('CLICK', cc, cr)]))

    return None


# ---------------------------------------------------------------------------
# Convert solution to display coordinates
# ---------------------------------------------------------------------------

def actions_to_display_sequence(actions: List, level: LevelData) -> List[dict]:
    """Convert solver actions to display action sequence.

    For CLICK, camera_y = player.grid_y * 6 - 31 + tprcybckbl
    tprcybckbl = -5 if gravity_up else 5
    Click display: pixel_x = cc*6 + 3, pixel_y = cr*6 - camera_y + 3
    """
    sequence = []
    col, row = level.player_pos
    grav_up = True
    destroyed = set()

    for action in actions:
        if action[0] == 'LEFT':
            sequence.append({"action": 3})
            result = try_horizontal_move(level, col, row, -1, grav_up, frozenset(destroyed))
            if result and result[0] == 'ok':
                col, row = result[1], result[2]
        elif action[0] == 'RIGHT':
            sequence.append({"action": 4})
            result = try_horizontal_move(level, col, row, 1, grav_up, frozenset(destroyed))
            if result and result[0] == 'ok':
                col, row = result[1], result[2]
        elif action[0] == 'CLICK':
            cc, cr = action[1], action[2]
            tprcybckbl = -5 if grav_up else 5
            camera_y = row * 6 - 31 + tprcybckbl
            pixel_x = cc * 6 + 3
            pixel_y = cr * 6 - camera_y + 3
            pixel_x = max(0, min(63, pixel_x))
            pixel_y = max(0, min(63, pixel_y))
            sequence.append({"action": 6, "x": pixel_x, "y": pixel_y})

            ch = level.cell_at(cc, cr)
            if ch in ('x', '1'):
                destroyed.add((cc, cr))
            elif ch == 'g':
                grav_up = not grav_up

            final_pos, outcome = simulate_fall(level, col, row, grav_up, frozenset(destroyed))
            if outcome != 'spike':
                col, row = final_pos

    return sequence


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_solution(level: LevelData, actions: List) -> bool:
    col, row = level.player_pos
    grav_up = True
    destroyed = set()

    for action in actions:
        if action[0] == 'LEFT':
            result = try_horizontal_move(level, col, row, -1, grav_up, frozenset(destroyed))
            if result is None:
                continue
            if result[0] == 'win':
                return True
            if result[0] == 'dead':
                return False
            col, row = result[1], result[2]
        elif action[0] == 'RIGHT':
            result = try_horizontal_move(level, col, row, 1, grav_up, frozenset(destroyed))
            if result is None:
                continue
            if result[0] == 'win':
                return True
            if result[0] == 'dead':
                return False
            col, row = result[1], result[2]
        elif action[0] == 'CLICK':
            cc, cr = action[1], action[2]
            ch = level.cell_at(cc, cr)
            if ch in ('x', '1'):
                destroyed.add((cc, cr))
            elif ch == 'g':
                grav_up = not grav_up
            final_pos, outcome = simulate_fall(level, col, row, grav_up, frozenset(destroyed))
            if outcome == 'gem':
                return True
            if outcome == 'spike':
                return False
            col, row = final_pos

    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="bp35 Platformer Puzzle Solver")
    parser.add_argument("--level", type=int, default=None)
    parser.add_argument("--source", type=str, default=None)
    parser.add_argument("--max-steps", type=int, default=50)
    args = parser.parse_args()

    source_path = args.source or find_source()
    if not source_path:
        print("ERROR: Could not find bp35.py source")
        sys.exit(1)

    print(f"Parsing source: {source_path}")
    source = parse_source(source_path)

    print("Extracting grids...")
    grids = extract_grids(source)
    print(f"  Found {len(grids)} grids: {', '.join(sorted(grids.keys()))}")

    level_grids = {}
    for i in range(1, 11):
        gname = f"grid{i}"
        if gname in grids:
            level_grids[i] = grids[gname]

    if args.level is not None:
        target_levels = [args.level]
    else:
        target_levels = sorted(level_grids.keys())

    results = []

    for lvl_idx in target_levels:
        if lvl_idx not in level_grids:
            print(f"\nLevel {lvl_idx}: grid not found")
            continue

        grid = level_grids[lvl_idx]
        level = LevelData(lvl_idx, grid)

        print(f"\n{'='*60}")
        print(f"Level {lvl_idx}:")
        print(f"  Grid size: {level.width}x{level.height}")
        print(f"  Player: {level.player_pos}")
        print(f"  Gem: {level.gem_pos}")
        print(f"  Clickable x tiles: {len(level.clickable_x)}")
        print(f"  Gravity flips: {len(level.gravity_flips)}")

        print(f"\n  Solving (max {args.max_steps} steps)...")
        solution = solve_level(level, max_steps=args.max_steps)

        if solution is None:
            print("  NO SOLUTION FOUND")
            results.append({"level": lvl_idx, "verified": False, "actions": []})
            continue

        verified = verify_solution(level, solution)

        print(f"  Solution ({len(solution)} actions):")
        for i, act in enumerate(solution):
            if act[0] in ('LEFT', 'RIGHT'):
                print(f"    Step {i+1}: {act[0]}")
            elif act[0] == 'CLICK':
                ch = level.cell_at(act[1], act[2])
                print(f"    Step {i+1}: CLICK({act[1]},{act[2]}) [{ch}]")

        display_seq = actions_to_display_sequence(solution, level)

        print(f"\n  Display action sequence:")
        for i, act in enumerate(display_seq):
            if act["action"] == 3:
                print(f"    Step {i+1}: ACTION3 (LEFT)")
            elif act["action"] == 4:
                print(f"    Step {i+1}: ACTION4 (RIGHT)")
            elif act["action"] == 6:
                print(f"    Step {i+1}: ACTION6 CLICK({act['x']},{act['y']})")

        status = "VERIFIED OK" if verified else "VERIFICATION FAILED"
        print(f"\n  {status}")

        results.append({
            "level": lvl_idx,
            "actions": solution,
            "display_sequence": display_seq,
            "verified": verified,
        })

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for r in results:
        status = "VERIFIED OK" if r["verified"] else "FAILED"
        n = len(r.get("actions", []))
        print(f"  Level {r['level']}: {n} actions - {status}")


if __name__ == "__main__":
    main()
