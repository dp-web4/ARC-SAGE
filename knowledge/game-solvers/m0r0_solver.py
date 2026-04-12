#!/usr/bin/env python3
"""
m0r0 Mirrored Maze Solver

Parses m0r0.py to extract maze walls, paired token positions, obstacles,
traps, doors/switches for each level. Uses BFS to find move sequences
that merge all paired tokens.

Key mechanics:
  - ubwff-idtiq moves (dx, dy), ubwff-crkfz moves (-dx, dy)
  - kncqr-idtiq moves (dx, -dy), kncqr-crkfz moves (-dx, -dy)
  - Tokens merge when they occupy the same cell
  - Traps reset positions on contact
  - Doors open when a paired token sits on matching switch

Usage:
    python m0r0_solver.py [--level N] [--source PATH]
"""

import re
import sys
import ast
import argparse
from collections import deque
from typing import List, Tuple, Optional, Dict, Set, FrozenSet

GAME_SOURCE_DEFAULT = (
    "/Users/dennispalatov/repos/shared-context/environment_files/"
    "m0r0/dadda488/m0r0.py"
)


# ---------------------------------------------------------------------------
# Parse source
# ---------------------------------------------------------------------------

def parse_source(path: str) -> str:
    with open(path) as f:
        return f.read()


def extract_sprite_pixels(source: str) -> Dict[str, list]:
    """Extract pixel arrays for maze sprites."""
    sprites = {}
    pattern = re.compile(
        r'"(jggua-\w+)":\s*Sprite\(\s*pixels=(\[.*?\]),\s*name=',
        re.DOTALL,
    )
    for m in pattern.finditer(source):
        name = m.group(1)
        pixels_str = m.group(2)
        try:
            pixels = ast.literal_eval(pixels_str)
            sprites[name] = pixels
        except:
            pass
    return sprites


def extract_levels(source: str) -> list:
    """Extract level data from levels list."""
    levels = []
    # Find level blocks
    pattern = re.compile(
        r'#\s*Level\s+(\d+)\s*\n\s*Level\(\s*sprites=\[(.*?)\],\s*'
        r'grid_size=\((\d+),\s*(\d+)\),\s*'
        r'data=\{([^}]*)\}',
        re.DOTALL,
    )

    for m in pattern.finditer(source):
        level_num = int(m.group(1))
        sprites_block = m.group(2)
        gw, gh = int(m.group(3)), int(m.group(4))
        data_block = m.group(5)

        # Parse sprite placements
        sp_pattern = re.compile(
            r'sprites\["([\w-]+)"\]\.clone\(\)'
            r'(?:\.set_position\((\d+),\s*(\d+)\))?'
            r'(?:\.set_rotation\((\d+)\))?'
        )
        placements = []
        for sp_m in sp_pattern.finditer(sprites_block):
            name = sp_m.group(1)
            x = int(sp_m.group(2)) if sp_m.group(2) else 0
            y = int(sp_m.group(3)) if sp_m.group(3) else 0
            rot = int(sp_m.group(4)) if sp_m.group(4) else 0
            placements.append((name, x, y, rot))

        levels.append({
            'num': level_num,
            'grid': (gw, gh),
            'placements': placements,
        })

    return levels


# ---------------------------------------------------------------------------
# Level state
# ---------------------------------------------------------------------------

def parse_maze(pixels: list, rotation: int = 0) -> Set[Tuple[int, int]]:
    """Parse maze sprite to get wall positions (color 0).

    Returns wall positions as (x, y) in local sprite coordinates after rotation.
    """
    import numpy as np
    arr = np.array(pixels)
    if rotation == 90:
        arr = np.rot90(arr, k=-1)
    elif rotation == 180:
        arr = np.rot90(arr, k=-2)
    elif rotation == 270:
        arr = np.rot90(arr, k=-3)

    walls = set()
    for y in range(arr.shape[0]):
        for x in range(arr.shape[1]):
            if arr[y, x] == 0:
                walls.add((x, y))
    return walls


def build_level_state(level: dict, maze_pixels: dict) -> dict:
    """Build initial state for a level."""
    placements = level['placements']
    gw, gh = level['grid']

    # Find maze
    maze_walls = set()
    maze_offset = (0, 0)
    for name, x, y, rot in placements:
        if name.startswith('jggua-'):
            if name in maze_pixels:
                walls = parse_maze(maze_pixels[name], rot)
                # Offset walls by sprite position
                maze_walls = {(wx + x, wy + y) for wx, wy in walls}
                maze_offset = (x, y)
                break

    # Find paired tokens
    tokens = {}
    for name, x, y, rot in placements:
        if name.startswith('qzfkx-'):
            tokens[name] = (x, y)

    # Find obstacles (cvcer)
    obstacles = []
    for name, x, y, rot in placements:
        if name == 'cvcer':
            obstacles.append((x, y))

    # Find traps (wyiex)
    traps = set()
    for name, x, y, rot in placements:
        if name == 'wyiex':
            traps.add((x, y))

    # Find doors and switches
    doors = {}  # color_key -> [(x, y, rot)]
    switches = {}  # color_key -> [(x, y)]
    for name, x, y, rot in placements:
        if name.startswith('dfnuk-'):
            color_key = name.split('-')[1]
            if color_key not in doors:
                doors[color_key] = []
            # Door is 3x1 vertical, but rotation 90 makes it 1x3 horizontal
            doors[color_key].append((x, y, rot))
        elif name.startswith('hnutp-'):
            color_key = name.split('-')[1]
            if color_key not in switches:
                switches[color_key] = []
            switches[color_key].append((x, y))

    return {
        'grid': (gw, gh),
        'walls': maze_walls,
        'tokens': tokens,
        'obstacles': obstacles,
        'traps': traps,
        'doors': doors,
        'switches': switches,
    }


def get_door_cells(doors: dict) -> Set[Tuple[int, int]]:
    """Get all cells occupied by active doors."""
    cells = set()
    for color_key, door_list in doors.items():
        for x, y, rot in door_list:
            if rot == 90 or rot == 270:
                # Horizontal: 1x3 -> 3 cells along x
                for dx in range(3):
                    cells.add((x + dx, y))
            else:
                # Vertical: 1x3 -> 3 cells along y
                for dy in range(3):
                    cells.add((x, y + dy))
    return cells


# ---------------------------------------------------------------------------
# BFS Solver
# ---------------------------------------------------------------------------

# State: tuple of token positions (sorted) + obstacle positions + active doors
# For simplicity, represent as tuple of (token_name, x, y) sorted

DIRECTIONS = {
    'UP': (0, -1),
    'DOWN': (0, 1),
    'LEFT': (-1, 0),
    'RIGHT': (1, 0),
}


def can_move(x: int, y: int, dx: int, dy: int, gw: int, gh: int,
             walls: Set, obstacles: Set, door_cells: Set) -> bool:
    """Check if moving from (x,y) by (dx,dy) is valid."""
    nx, ny = x + dx, y + dy
    if nx < 0 or ny < 0 or nx >= gw or ny >= gh:
        return False
    if (nx, ny) in walls:
        return False
    if (nx, ny) in obstacles:
        return False
    if (nx, ny) in door_cells:
        return False
    return True


def check_doors(token_positions: dict, switches: dict) -> Set[str]:
    """Check which door colors should be open (removed).

    A door opens when ANY paired token sits on a matching switch.
    """
    open_colors = set()
    token_pos_set = set(token_positions.values())
    for color_key, switch_list in switches.items():
        for sx, sy in switch_list:
            if (sx, sy) in token_pos_set:
                open_colors.add(color_key)
                break
    return open_colors


def solve_level(level_state: dict, verbose: bool = True) -> Optional[dict]:
    """BFS to find movement sequence that merges all tokens."""
    gw, gh = level_state['grid']
    walls = level_state['walls']
    traps = level_state['traps']
    initial_tokens = level_state['tokens']
    initial_obstacles = tuple(sorted(level_state['obstacles']))
    doors = level_state['doors']
    switches = level_state['switches']

    # Identify token pairs
    token_names = sorted(initial_tokens.keys())
    if not token_names:
        return None

    # Determine which pairs exist
    ubwff_idtiq = 'qzfkx-ubwff-idtiq' if 'qzfkx-ubwff-idtiq' in initial_tokens else None
    ubwff_crkfz = 'qzfkx-ubwff-crkfz' if 'qzfkx-ubwff-crkfz' in initial_tokens else None
    kncqr_idtiq = 'qzfkx-kncqr-idtiq' if 'qzfkx-kncqr-idtiq' in initial_tokens else None
    kncqr_crkfz = 'qzfkx-kncqr-crkfz' if 'qzfkx-kncqr-crkfz' in initial_tokens else None

    active_tokens = [n for n in token_names if n in initial_tokens]

    if verbose:
        print(f"  Grid: {gw}x{gh}")
        print(f"  Walls: {len(walls)}")
        print(f"  Tokens: {len(active_tokens)}")
        for n in active_tokens:
            print(f"    {n}: {initial_tokens[n]}")
        print(f"  Obstacles: {len(initial_obstacles)}")
        print(f"  Traps: {len(traps)}")
        print(f"  Doors: {list(doors.keys())}")
        print(f"  Switches: {list(switches.keys())}")

    # State: positions of active tokens + obstacle positions
    # For levels without obstacles/doors, simplified BFS

    has_obstacles = len(initial_obstacles) > 0
    has_doors = len(doors) > 0

    def make_state(token_pos: dict, obs_pos: tuple, merged: frozenset):
        # Sorted token positions for hashing
        items = []
        for n in token_names:
            if n in merged:
                items.append((n, -1, -1))
            else:
                x, y = token_pos.get(n, (-1, -1))
                items.append((n, x, y))
        return (tuple(items), obs_pos, merged)

    def is_won(token_pos: dict, merged: frozenset) -> bool:
        active = [n for n in token_names if n not in merged]
        return len(active) == 0

    # BFS
    init_merged = frozenset()
    init_token_pos = dict(initial_tokens)
    init_state = make_state(init_token_pos, initial_obstacles, init_merged)

    if is_won(init_token_pos, init_merged):
        return {'actions': [], 'verified': True}

    visited = {init_state}
    queue = deque()
    queue.append((init_token_pos, initial_obstacles, init_merged, []))

    max_depth = 50  # Reasonable limit

    while queue:
        token_pos, obs_pos, merged, path = queue.popleft()

        if len(path) >= max_depth:
            continue

        for dir_name, (dx, dy) in DIRECTIONS.items():
            # Apply group movement
            new_token_pos = dict(token_pos)
            new_merged = set(merged)
            obs_set = set(obs_pos)

            # Check which doors are open
            open_colors = check_doors(token_pos, switches)
            active_doors = {k: v for k, v in doors.items() if k not in open_colors}
            door_cells = get_door_cells(active_doors)

            # Move each active token with mirrored directions
            moved = {}
            for name in token_names:
                if name in new_merged:
                    continue
                x, y = token_pos[name]
                # Compute mirrored direction
                if 'ubwff-idtiq' in name:
                    mdx, mdy = dx, dy
                elif 'ubwff-crkfz' in name:
                    mdx, mdy = -dx, dy
                elif 'kncqr-idtiq' in name:
                    mdx, mdy = dx, -dy
                elif 'kncqr-crkfz' in name:
                    mdx, mdy = -dx, -dy
                else:
                    mdx, mdy = dx, dy

                if can_move(x, y, mdx, mdy, gw, gh, walls, obs_set, door_cells):
                    moved[name] = (x + mdx, y + mdy)
                else:
                    moved[name] = (x, y)

            # Check for traps
            trap_hit = False
            for name, (nx, ny) in moved.items():
                if name not in new_merged and (nx, ny) in traps:
                    trap_hit = True
                    break

            if trap_hit:
                continue  # Skip this move (would reset)

            # Check for merges
            new_token_pos = dict(moved)
            # Merge check: tokens at same position
            positions = {}
            for name in token_names:
                if name in new_merged:
                    continue
                pos = new_token_pos[name]
                if pos not in positions:
                    positions[pos] = []
                positions[pos].append(name)

            for pos, names in positions.items():
                if len(names) >= 2:
                    for n in names:
                        new_merged.add(n)

            # Also check swap/adjacent merge (midpoint merge)
            active_names = [n for n in token_names if n not in new_merged]
            for i in range(len(active_names)):
                ni = active_names[i]
                if ni in new_merged:
                    continue
                for j in range(i+1, len(active_names)):
                    nj = active_names[j]
                    if nj in new_merged:
                        continue
                    # Check if they were adjacent before and swapped
                    old_i = token_pos.get(ni, (-1,-1))
                    old_j = token_pos.get(nj, (-1,-1))
                    new_i = new_token_pos.get(ni, (-1,-1))
                    new_j = new_token_pos.get(nj, (-1,-1))
                    if (abs(old_i[0] - old_j[0]) == 1 and old_i[1] == old_j[1]):
                        if (new_i == old_j and new_j == old_i):
                            mid_x = (new_i[0] + new_j[0]) // 2
                            mid_y = (new_i[1] + new_j[1]) // 2
                            new_token_pos[ni] = (mid_x, mid_y)
                            new_token_pos[nj] = (mid_x, mid_y)
                            new_merged.add(ni)
                            new_merged.add(nj)

            new_merged_frozen = frozenset(new_merged)
            new_path = path + [dir_name]

            if is_won(new_token_pos, new_merged_frozen):
                return {
                    'actions': new_path,
                    'verified': True,
                }

            state = make_state(new_token_pos, obs_pos, new_merged_frozen)
            if state not in visited:
                visited.add(state)
                queue.append((new_token_pos, obs_pos, new_merged_frozen, new_path))

    if verbose:
        print(f"  No solution found within {max_depth} moves (explored {len(visited)} states)")
    return None


# ---------------------------------------------------------------------------
# Display coordinate conversion
# ---------------------------------------------------------------------------

def grid_to_display(gx: int, gy: int, gw: int, gh: int) -> Tuple[int, int]:
    """Convert grid coords to 64x64 display coords."""
    scale_x = 64 // gw
    scale_y = 64 // gh
    scale = min(scale_x, scale_y)
    scaled_w = gw * scale
    scaled_h = gh * scale
    ox = (64 - scaled_w) // 2
    oy = (64 - scaled_h) // 2
    return (gx * scale + ox, gy * scale + oy)


def action_to_display(action: str) -> str:
    """Convert action name to display action."""
    return {
        'UP': 'ACTION1',
        'DOWN': 'ACTION2',
        'LEFT': 'ACTION3',
        'RIGHT': 'ACTION4',
    }.get(action, action)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="m0r0 Mirrored Maze Solver")
    parser.add_argument("--level", type=int, default=None)
    parser.add_argument("--source", type=str, default=GAME_SOURCE_DEFAULT)
    args = parser.parse_args()

    print("Parsing game source...")
    source = parse_source(args.source)

    print("Extracting maze sprites...")
    maze_pixels = extract_sprite_pixels(source)
    print(f"  Found {len(maze_pixels)} maze sprites")

    print("Extracting levels...")
    levels = extract_levels(source)
    print(f"  Found {len(levels)} levels")

    if args.level is not None:
        targets = [lv for lv in levels if lv['num'] == args.level]
    else:
        targets = levels

    results = []
    for lv in targets:
        print(f"\n{'='*60}")
        print(f"Level {lv['num']}:")
        state = build_level_state(lv, maze_pixels)
        result = solve_level(state)
        if result:
            result['level'] = lv['num']
            results.append(result)
        print()

    print(f"{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for r in results:
        status = "VERIFIED OK" if r['verified'] else "FAILED"
        n = len(r['actions'])
        print(f"  Level {r['level']}: {n} actions ... {status}")
        if r['actions']:
            print(f"    Sequence: {' '.join(r['actions'])}")


if __name__ == "__main__":
    main()
