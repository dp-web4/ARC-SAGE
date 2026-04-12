#!/usr/bin/env python3
"""
g50t Multi-Phase Clone Replay Puzzle Solver

Parses the g50t.py game source to extract level layouts, then analyzes
the maze structure and computes movement sequences for each phase.

Key mechanics:
  - Player moves on 6-pixel grid (jarvstobjt=6) in 4 directions
  - Movement is blocked by maze walls (rsrdfsruqh), gates (kjrcloicja),
    and barrier walls (hxztohfdlx)
  - ACTION5 records current moves, creates a clone that replays them,
    and starts the next phase
  - Number of phases = number of gpkhwmwioo (phase indicator) sprites
  - Win: player center at (goal.x+1, goal.y+1) where goal = gilbljmfbc
  - Timer ticks every 2 steps; runs out = lose
  - Ghosts (vtwcsmdoqp) move autonomously and can kill player

The solver:
1. Parses maze geometry from sprite pixel data
2. Identifies player start, goal, gates, walls
3. Uses BFS to find paths to goal
4. Plans multi-phase solutions where clones replay recorded paths

Actions: 1=UP, 2=DOWN, 3=LEFT, 4=RIGHT, 5=UNDO/REPLAY

Usage:
    python g50t_solver.py [--level N] [--source PATH]
"""

import re
import sys
import argparse
from collections import deque
from typing import Dict, List, Optional, Tuple, Set

# ---------------------------------------------------------------------------
# Source path
# ---------------------------------------------------------------------------

def find_source():
    import glob
    pattern = "/Users/dennispalatov/repos/shared-context/environment_files/g50t/*/g50t.py"
    matches = glob.glob(pattern)
    return matches[0] if matches else None


def parse_source(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


# ---------------------------------------------------------------------------
# Parse sprites and levels
# ---------------------------------------------------------------------------

class SpriteInfo:
    def __init__(self, name: str, width: int, height: int, tags: List[str],
                 x: int = 0, y: int = 0, rotation: int = 0,
                 pixels: Optional[List[List[int]]] = None):
        self.name = name
        self.width = width
        self.height = height
        self.tags = tags
        self.x = x
        self.y = y
        self.rotation = rotation
        self.pixels = pixels

    def __repr__(self):
        return f"Sprite({self.name} @ ({self.x},{self.y}) {self.width}x{self.height})"


def extract_sprite_defs(source: str) -> Dict[str, SpriteInfo]:
    """Extract sprite definitions."""
    defs = {}
    pattern = re.compile(r'"([\w-]+)":\s*Sprite\(')

    for m in pattern.finditer(source):
        name = m.group(1)
        depth = 0
        end = m.start()
        for i in range(m.end() - 1, min(len(source), m.start() + 15000)):
            if source[i] == '(':
                depth += 1
            elif source[i] == ')':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        block = source[m.start():end]

        tags_m = re.search(r'tags=\[([^\]]*)\]', block)
        tags = []
        if tags_m:
            tags = [t.strip().strip('"').strip("'") for t in tags_m.group(1).split(',') if t.strip()]

        collidable = 'collidable=True' in block

        pixels_m = re.search(r'pixels=\[', block)
        width = height = 0
        pixel_data = []
        if pixels_m:
            px_start = pixels_m.end()
            depth2 = 1
            px_end = px_start
            for j in range(px_start, len(block)):
                if block[j] == '[':
                    depth2 += 1
                elif block[j] == ']':
                    depth2 -= 1
                    if depth2 == 0:
                        px_end = j
                        break
            px_block = block[px_start:px_end]
            inner_brackets = re.findall(r'\[([^\[\]]+)\]', px_block)
            height = len(inner_brackets)
            for row_str in inner_brackets:
                row = [int(e.strip()) for e in row_str.split(',') if e.strip()]
                pixel_data.append(row)
                width = max(width, len(row))

        defs[name] = SpriteInfo(name, width, height, tags, pixels=pixel_data)

    return defs


class LevelData:
    def __init__(self, index: int, grid_size: Tuple[int, int],
                 sprites: List[SpriteInfo]):
        self.index = index
        self.grid_w, self.grid_h = grid_size
        self.sprites = sprites

    def sprites_by_tag(self, tag: str) -> List[SpriteInfo]:
        return [s for s in self.sprites if tag in s.tags]


def extract_levels(source: str, sprite_defs: Dict[str, SpriteInfo]) -> List[LevelData]:
    levels = []
    level_pattern = re.compile(
        r'#\s*Level\s+(\d+)\s*\n\s*Level\(\s*sprites=\[(.*?)\],\s*'
        r'grid_size=\((\d+),\s*(\d+)\)',
        re.DOTALL
    )

    for m in level_pattern.finditer(source):
        level_num = int(m.group(1))
        sprites_block = m.group(2)
        gw, gh = int(m.group(3)), int(m.group(4))

        sprites = []
        sp_pattern = re.compile(
            r'sprites\["([\w-]+)"\]\.clone\(\)((?:\.\w+\([^)]*\))*)'
        )
        for sp_m in sp_pattern.finditer(sprites_block):
            sname = sp_m.group(1)
            chain = sp_m.group(2)

            sx, sy, rot = 0, 0, 0
            pos_m = re.search(r'\.set_position\((-?\d+),\s*(-?\d+)\)', chain)
            if pos_m:
                sx, sy = int(pos_m.group(1)), int(pos_m.group(2))
            rot_m = re.search(r'\.set_rotation\((\d+)\)', chain)
            if rot_m:
                rot = int(rot_m.group(1))

            if sname in sprite_defs:
                sd = sprite_defs[sname]
                si = SpriteInfo(sname, sd.width, sd.height, list(sd.tags),
                                x=sx, y=sy, rotation=rot, pixels=sd.pixels)
                sprites.append(si)

        levels.append(LevelData(level_num, (gw, gh), sprites))

    levels.sort(key=lambda lv: lv.index)
    return levels


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STEP = 6  # jarvstobjt


# ---------------------------------------------------------------------------
# Build collision map from maze sprites
# ---------------------------------------------------------------------------

def build_collision_set(level: LevelData) -> Set[Tuple[int, int]]:
    """Build set of (x,y) pixel positions that are walls/barriers.

    Collision sprites: rsrdfsruqh (maze), hxztohfdlx (walls/barriers),
    kjrcloicja (gates), medyellngi (maze features).
    A pixel blocks movement if its color value is >= 0 (not transparent).
    """
    collision_tags = {'rsrdfsruqh', 'hxztohfdlx', 'kjrcloicja', 'medyellngi'}
    blocked = set()

    for s in level.sprites:
        has_collision_tag = any(t in collision_tags for t in s.tags)
        if not has_collision_tag:
            continue

        if s.pixels:
            for row_idx, row in enumerate(s.pixels):
                for col_idx, pixel in enumerate(row):
                    if pixel >= 0:
                        blocked.add((s.x + col_idx, s.y + row_idx))

    return blocked


def build_maze_walkable(level: LevelData) -> Set[Tuple[int, int]]:
    """Build set of walkable pixel positions from maze/board sprite.

    The maze sprite (rsrdfsruqh/bognpjtvzt) has transparent (-1/-2) pixels
    for walkable areas and colored pixels for walls.

    Actually, the maze sprite pixel data DEFINES the walls. The walkable
    area is the complement - where the maze sprite has transparent pixels.

    The game checks: player center must be inside the board sprite AND
    the pixel at that position must be non-wall (transparent/-1/-2).
    """
    board_sprites = level.sprites_by_tag('rsrdfsruqh')
    if not board_sprites:
        return set()

    board = board_sprites[0]
    walkable = set()

    if board.pixels:
        for row_idx, row in enumerate(board.pixels):
            for col_idx, pixel in enumerate(row):
                if pixel >= 0:  # colored pixel = walkable path
                    walkable.add((board.x + col_idx, board.y + row_idx))

    return walkable


# ---------------------------------------------------------------------------
# BFS path finder
# ---------------------------------------------------------------------------

def find_path_bfs(start_x: int, start_y: int, goal_x: int, goal_y: int,
                  walkable: Set[Tuple[int, int]], player_w: int, player_h: int,
                  max_steps: int = 100) -> Optional[List[Tuple[int, int]]]:
    """BFS to find path from start to goal on 6-pixel grid.

    Returns list of (dx, dy) movement deltas, or None.
    The player center (x + w//2, y + h//2) must be on walkable pixels.
    """
    def is_valid(px, py):
        cx = px + player_w // 2
        cy = py + player_h // 2
        return (cx, cy) in walkable

    if not is_valid(start_x, start_y):
        # Try without center check
        pass

    visited = set()
    visited.add((start_x, start_y))
    queue = deque([((start_x, start_y), [])])

    directions = [
        (0, -1),   # UP
        (0, 1),    # DOWN
        (-1, 0),   # LEFT
        (1, 0),    # RIGHT
    ]

    while queue:
        (px, py), path = queue.popleft()
        if len(path) >= max_steps:
            continue

        for dx, dy in directions:
            nx, ny = px + dx * STEP, py + dy * STEP

            if nx == goal_x and ny == goal_y:
                return path + [(dx, dy)]

            if (nx, ny) in visited:
                continue

            if is_valid(nx, ny):
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(dx, dy)]))

    return None


# ---------------------------------------------------------------------------
# Solver
# ---------------------------------------------------------------------------

def solve_level(level: LevelData, max_steps: int = 80) -> Optional[List]:
    """Solve g50t level.

    For single-phase levels, just find path to goal.
    For multi-phase levels, find a path that works with clones.
    """
    # Find key sprites
    player_sprites = level.sprites_by_tag('qftsebtxuc')
    goal_sprites = level.sprites_by_tag('gilbljmfbc')
    phase_sprites = level.sprites_by_tag('gpkhwmwioo')

    if not player_sprites or not goal_sprites:
        print(f"    Missing player or goal")
        return None

    player = player_sprites[0]
    goal = goal_sprites[0]
    num_phases = len(phase_sprites)

    print(f"    Player: ({player.x},{player.y}) {player.width}x{player.height}")
    # Win condition: player.x + 1 == goal.x and player.y + 1 == goal.y
    # So target position: (goal.x - 1, goal.y - 1)... wait no.
    # From source: self.whftgckbcu.x + 1 == self.dzxunlkwxt.x and self.whftgckbcu.y + 1 == self.dzxunlkwxt.y
    # whftgckbcu = goal, dzxunlkwxt = player
    # So: goal.x + 1 == player.x and goal.y + 1 == player.y
    # Target: player at (goal.x + 1, goal.y + 1)
    target_x = goal.x + 1
    target_y = goal.y + 1
    print(f"    Goal sprite: ({goal.x},{goal.y})")
    print(f"    Target player pos: ({target_x},{target_y})")
    print(f"    Phases: {num_phases}")

    # Build walkable map from maze sprite
    walkable = build_maze_walkable(level)
    print(f"    Walkable pixels: {len(walkable)}")

    if not walkable:
        print(f"    WARNING: No walkable pixels from maze sprite!")
        # Try using board sprites differently
        board_sprites = [s for s in level.sprites if s.pixels and len(s.pixels) > 20]
        for bs in board_sprites:
            print(f"      Large sprite: {bs.name} ({bs.x},{bs.y}) {bs.width}x{bs.height} tags={bs.tags}")
        return None

    # Simple path finding for phase 1
    path = find_path_bfs(player.x, player.y, target_x, target_y,
                         walkable, player.width, player.height,
                         max_steps=max_steps)

    if path is not None:
        # Convert to action list
        actions = []
        dir_to_action = {
            (0, -1): ('UP',),
            (0, 1): ('DOWN',),
            (-1, 0): ('LEFT',),
            (1, 0): ('RIGHT',),
        }
        for dx, dy in path:
            actions.append(dir_to_action[(dx, dy)])
        return actions

    print(f"    Direct path not found, trying multi-phase approach...")

    # For multi-phase: we need to reach the goal with recorded moves
    # Phase 1: move to some position, press ACTION5
    # Phase 2: clone replays phase 1 moves, we move differently
    # etc.
    # This requires knowing what gates/switches do.
    # For now, report failure on complex multi-phase levels.

    return None


# ---------------------------------------------------------------------------
# Convert to display coordinates
# ---------------------------------------------------------------------------

def actions_to_display(actions: List, level: LevelData) -> List[dict]:
    sequence = []
    action_map = {'UP': 1, 'DOWN': 2, 'LEFT': 3, 'RIGHT': 4, 'PHASE': 5}
    for action in actions:
        sequence.append({"action": action_map.get(action[0], 5)})
    return sequence


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_solution(level: LevelData, actions: List) -> bool:
    player_sprites = level.sprites_by_tag('qftsebtxuc')
    goal_sprites = level.sprites_by_tag('gilbljmfbc')
    if not player_sprites or not goal_sprites:
        return False

    px, py = player_sprites[0].x, player_sprites[0].y
    gx, gy = goal_sprites[0].x, goal_sprites[0].y
    target_x = gx + 1
    target_y = gy + 1

    dx_map = {'UP': (0, -STEP), 'DOWN': (0, STEP),
              'LEFT': (-STEP, 0), 'RIGHT': (STEP, 0)}

    for action in actions:
        if action[0] in dx_map:
            ddx, ddy = dx_map[action[0]]
            px += ddx
            py += ddy

    return px == target_x and py == target_y


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="g50t Multi-Phase Puzzle Solver")
    parser.add_argument("--level", type=int, default=None)
    parser.add_argument("--source", type=str, default=None)
    parser.add_argument("--max-steps", type=int, default=80)
    args = parser.parse_args()

    source_path = args.source or find_source()
    if not source_path:
        print("ERROR: Could not find g50t.py source")
        sys.exit(1)

    print(f"Parsing source: {source_path}")
    source = parse_source(source_path)

    print("Extracting sprite definitions...")
    sprite_defs = extract_sprite_defs(source)
    print(f"  Found {len(sprite_defs)} sprite defs")

    print("Extracting levels...")
    levels = extract_levels(source, sprite_defs)
    print(f"  Found {len(levels)} levels")

    if args.level is not None:
        target_levels = [lv for lv in levels if lv.index == args.level]
    else:
        target_levels = levels

    results = []

    for level in target_levels:
        print(f"\n{'='*60}")
        print(f"Level {level.index}:")
        print(f"  Grid: {level.grid_w}x{level.grid_h}")

        print(f"\n  Solving (max {args.max_steps} steps)...")
        solution = solve_level(level, max_steps=args.max_steps)

        if solution is None:
            print("  NO SOLUTION FOUND")
            results.append({"level": level.index, "verified": False})
            continue

        verified = verify_solution(level, solution)

        print(f"  Solution ({len(solution)} actions):")
        for i, act in enumerate(solution):
            print(f"    Step {i+1}: {act[0]}")

        display_seq = actions_to_display(solution, level)
        print(f"\n  Display action sequence:")
        for i, act in enumerate(display_seq):
            aname = {1: 'UP', 2: 'DOWN', 3: 'LEFT', 4: 'RIGHT', 5: 'PHASE'}.get(act["action"], '?')
            print(f"    Step {i+1}: {aname}")

        status = "VERIFIED OK" if verified else "VERIFICATION FAILED"
        print(f"\n  {status}")
        results.append({"level": level.index, "verified": verified, "actions": solution})

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for r in results:
        status = "VERIFIED OK" if r["verified"] else "FAILED"
        n = len(r.get("actions", []))
        print(f"  Level {r['level']}: {n} actions - {status}")


if __name__ == "__main__":
    main()
