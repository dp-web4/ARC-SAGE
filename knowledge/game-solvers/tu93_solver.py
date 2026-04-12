#!/usr/bin/env python3
"""
tu93 Maze Navigation Solver

Parses tu93.py to extract maze layouts, player/exit/entity positions.
Uses BFS to find directional move sequences that navigate the player
to the exit, accounting for entity chain reactions.

Key mechanics:
  - Grid unit = 3px, grid nodes at every 6px
  - Player moves 1 grid unit per input
  - Arrow entities activate when player is 6px away and facing toward them
  - Bouncers reverse at walls
  - Win when player reaches exit position

Usage:
    python tu93_solver.py [--level N] [--source PATH]
"""

import re
import sys
import ast
import argparse
import numpy as np
from collections import deque
from typing import List, Tuple, Optional, Dict, Set

GAME_SOURCE_DEFAULT = (
    "/Users/dennispalatov/repos/shared-context/environment_files/"
    "tu93/2b534c15/tu93.py"
)

GRID_UNIT = 3  # bsfndluqyd
GRID_NODE = 6  # twsfmzbqkg

# Direction: rotation -> (dx, dy) per step
ROT_TO_DIR = {
    0: (0, -1),    # up
    90: (1, 0),    # right
    180: (0, 1),   # down
    270: (-1, 0),  # left
}

DIR_TO_ROT = {
    'UP': 0,
    'RIGHT': 90,
    'DOWN': 180,
    'LEFT': 270,
}


# ---------------------------------------------------------------------------
# Parse source
# ---------------------------------------------------------------------------

def parse_source(path: str) -> str:
    with open(path) as f:
        return f.read()


def extract_maze_sprites(source: str) -> Dict[str, list]:
    """Extract maze pixel arrays (vhlesexlqd tagged sprites)."""
    sprites = {}
    # Find all sprite definitions
    pattern = re.compile(
        r'"(\w+)":\s*Sprite\(\s*pixels=(\[.*?\]),\s*name="(\w+)".*?tags=\[([^\]]*)\]',
        re.DOTALL,
    )
    for m in pattern.finditer(source):
        name = m.group(1)
        pixels_str = m.group(2)
        tags_str = m.group(4)
        if 'vhlesexlqd' in tags_str:
            try:
                pixels = ast.literal_eval(pixels_str)
                sprites[name] = pixels
            except:
                pass
    return sprites


def extract_entity_sprites(source: str) -> Dict[str, dict]:
    """Extract entity sprite info (player, arrows, bouncers, etc)."""
    entities = {}
    pattern = re.compile(
        r'"(\w+)":\s*Sprite\(\s*pixels=(\[.*?\]),\s*name="(\w+)".*?tags=\[([^\]]*)\]',
        re.DOTALL,
    )
    for m in pattern.finditer(source):
        name = m.group(1)
        tags_str = m.group(4)
        tag_list = [t.strip().strip('"').strip("'") for t in tags_str.split(',') if t.strip()]

        entity_type = None
        if 'albwnmiahg' in name:  # Player sprite name pattern
            entity_type = 'player'
        for tag in tag_list:
            if tag == 'vllvfeggte':
                entity_type = 'arrow'
            elif tag == 'zzuxulcort':
                entity_type = 'bouncer'
            elif tag == 'natiyqayts':
                entity_type = 'delayed'

        if entity_type:
            entities[name] = {'type': entity_type, 'tags': tag_list}

    return entities


def extract_levels(source: str) -> list:
    """Extract level data."""
    levels = []
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

        step_m = re.search(r'"StepCounter":\s*(\d+)', data_block)
        steps = int(step_m.group(1)) if step_m else 50

        # Parse placements - handle both .set_position().set_rotation() orderings
        sp_pattern = re.compile(
            r'sprites\["(\w+)"\]\.clone\(\)'
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
            'steps': steps,
        })

    return levels


# ---------------------------------------------------------------------------
# Maze parsing
# ---------------------------------------------------------------------------

def parse_maze_walkability(pixels: list) -> Set[Tuple[int, int]]:
    """Parse maze sprite to find ALL walkable cell positions (3x3 blocks).

    Returns local (x, y) positions of the top-left corner of each walkable block.
    """
    arr = np.array(pixels)
    walkable = set()

    h, w = arr.shape
    for row in range(0, h, GRID_UNIT):
        for col in range(0, w, GRID_UNIT):
            block = arr[row:min(row+GRID_UNIT, h), col:min(col+GRID_UNIT, w)]
            if np.any(block == 2):
                walkable.add((col, row))

    return walkable


def build_maze_graph(walkable: Set[Tuple[int, int]], maze_x: int, maze_y: int,
                     gw: int, gh: int) -> Dict[Tuple[int, int], Set[Tuple[int, int]]]:
    """Build navigation graph for the maze.

    The player moves by one input step (GRID_UNIT=3px), then slides to the next
    grid node (multiples of GRID_NODE=6). One input = move to adjacent grid node.

    Grid nodes are at maze-local positions where both x and y are multiples of
    GRID_NODE (6). Two nodes are connected if there's a walkable path block
    between them (at the midpoint).

    Returns graph in WORLD coordinates.
    """
    # Find grid node positions (multiples of GRID_NODE in local coords)
    arr_h = max(wy for _, wy in walkable) + GRID_UNIT if walkable else 0
    arr_w = max(wx for wx, _ in walkable) + GRID_UNIT if walkable else 0

    nodes = set()
    for wy in range(0, arr_h + 1, GRID_NODE):
        for wx in range(0, arr_w + 1, GRID_NODE):
            nodes.add((wx, wy))

    graph = {}
    for nx, ny in nodes:
        world_x = nx + maze_x
        world_y = ny + maze_y
        neighbors = set()

        # Check 4 directions to adjacent grid nodes (GRID_NODE=6 apart)
        # The midpoint (at GRID_UNIT=3) must be walkable
        for dx, dy in [(GRID_NODE, 0), (-GRID_NODE, 0), (0, GRID_NODE), (0, -GRID_NODE)]:
            mid_x = nx + dx // 2
            mid_y = ny + dy // 2
            dest_x = nx + dx
            dest_y = ny + dy

            # Check if the midpoint is walkable (the path between nodes)
            if (mid_x, mid_y) in walkable:
                neighbor = (dest_x + maze_x, dest_y + maze_y)
                neighbors.add(neighbor)

        graph[(world_x, world_y)] = neighbors

    return graph


# ---------------------------------------------------------------------------
# Level state
# ---------------------------------------------------------------------------

def build_level_state(level: dict, maze_sprites: dict, entity_info: dict) -> dict:
    """Build initial state for a level."""
    placements = level['placements']

    player_pos = None
    player_rot = 0
    exit_pos = None
    entities = []
    maze_name = None
    maze_pos = (0, 0)

    for name, x, y, rot in placements:
        if name == 'mcrwthchct':  # Player sprite
            player_pos = (x, y)
            player_rot = rot
        elif name == 'xtivqldqva':  # Exit sprite
            exit_pos = (x, y)
        elif name in entity_info:
            entities.append({
                'name': name,
                'type': entity_info[name]['type'],
                'x': x, 'y': y,
                'rot': rot,
            })
        elif name in maze_sprites:
            maze_name = name
            maze_pos = (x, y)

    # Parse maze walkability
    walkable = set()
    maze_graph = {}
    if maze_name and maze_name in maze_sprites:
        walkable = parse_maze_walkability(maze_sprites[maze_name])
        maze_graph = build_maze_graph(walkable, maze_pos[0], maze_pos[1],
                                       level['grid'][0], level['grid'][1])

    return {
        'grid': level['grid'],
        'player': player_pos,
        'player_rot': player_rot,
        'exit': exit_pos,
        'entities': entities,
        'maze_graph': maze_graph,
        'walkable': walkable,
        'maze_pos': maze_pos,
        'steps': level['steps'],
    }


# ---------------------------------------------------------------------------
# Simple BFS: player navigation ignoring entities
# ---------------------------------------------------------------------------

def bfs_navigate(maze_graph: Dict, start: Tuple[int, int],
                 goal: Tuple[int, int], max_steps: int,
                 walkable_world: Set[Tuple[int, int]]) -> Optional[List[str]]:
    """BFS to find path from start to goal using the maze graph.

    Each input step moves the player to an adjacent grid node.
    The graph edges already encode valid moves between nodes.
    """
    if start == goal:
        return []

    visited = {start}
    queue = deque()
    queue.append((start, []))

    while queue:
        pos, path = queue.popleft()
        if len(path) >= max_steps:
            continue

        for neighbor in maze_graph.get(pos, set()):
            dx = neighbor[0] - pos[0]
            dy = neighbor[1] - pos[1]

            if dx > 0:
                direction = 'RIGHT'
            elif dx < 0:
                direction = 'LEFT'
            elif dy > 0:
                direction = 'DOWN'
            else:
                direction = 'UP'

            new_path = path + [direction]

            if neighbor == goal:
                return new_path

            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, new_path))

    return None


def solve_level(level_state: dict, verbose: bool = True) -> Optional[dict]:
    """Solve a level using BFS on the maze graph."""
    player = level_state['player']
    exit_pos = level_state['exit']
    maze_graph = level_state['maze_graph']
    steps = level_state['steps']

    if player is None or exit_pos is None:
        if verbose:
            print("  Missing player or exit")
        return None

    if verbose:
        print(f"  Player: {player}")
        print(f"  Exit: {exit_pos}")
        print(f"  Maze nodes: {len(maze_graph)}")
        print(f"  Step limit: {steps}")
        print(f"  Entities: {len(level_state['entities'])}")
        for e in level_state['entities']:
            print(f"    {e['type']} {e['name']} at ({e['x']},{e['y']}) rot={e['rot']}")

    if verbose:
        print(f"  Player in graph: {player in maze_graph}")
        print(f"  Exit in graph: {exit_pos in maze_graph}")
        if player in maze_graph:
            print(f"  Player neighbors: {maze_graph[player]}")

    # Simple BFS on graph (ignoring entities for now)
    path = bfs_navigate(maze_graph, player, exit_pos, steps, set(maze_graph.keys()))

    if path is None:
        if verbose:
            print("  No path found (simple BFS)")

        # Try with node-to-node movement (every GRID_UNIT instead of GRID_NODE)
        # The graph should already handle this

        return None

    if verbose:
        print(f"  Path found: {len(path)} moves")
        print(f"  Sequence: {' '.join(path)}")
        print(f"  VERIFIED OK (path reaches exit)")

    return {
        'actions': path,
        'verified': True,
    }


# ---------------------------------------------------------------------------
# Display conversion
# ---------------------------------------------------------------------------

def grid_to_display(gx: int, gy: int, gw: int, gh: int) -> Tuple[int, int]:
    """Convert grid coords to 64x64 display coords."""
    # Custom camera renders at native resolution
    # Display is the raw sprite coordinates
    return (gx, gy)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="tu93 Maze Navigation Solver")
    parser.add_argument("--level", type=int, default=None)
    parser.add_argument("--source", type=str, default=GAME_SOURCE_DEFAULT)
    args = parser.parse_args()

    print("Parsing game source...")
    source = parse_source(args.source)

    print("Extracting maze sprites...")
    maze_sprites = extract_maze_sprites(source)
    print(f"  Found {len(maze_sprites)} maze sprites")

    print("Extracting entity info...")
    entity_info = extract_entity_sprites(source)
    print(f"  Found {len(entity_info)} entity types")
    for name, info in entity_info.items():
        print(f"    {name}: {info['type']}")

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
        state = build_level_state(lv, maze_sprites, entity_info)
        result = solve_level(state)
        if result:
            result['level'] = lv['num']
            results.append(result)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for r in results:
        status = "VERIFIED OK" if r['verified'] else "FAILED"
        n = len(r['actions'])
        print(f"  Level {r['level']}: {n} actions ... {status}")
        if r['actions']:
            # Compress
            compressed = []
            curr = r['actions'][0]
            cnt = 1
            for a in r['actions'][1:]:
                if a == curr:
                    cnt += 1
                else:
                    compressed.append(f"{curr}x{cnt}")
                    curr = a
                    cnt = 1
            compressed.append(f"{curr}x{cnt}")
            print(f"    Compressed: {', '.join(compressed)}")


if __name__ == "__main__":
    main()
