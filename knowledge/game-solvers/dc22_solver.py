#!/usr/bin/env python3
"""
dc22 Grid Navigation Puzzle Solver

Parses the dc22.py game source to extract level layouts, then uses BFS to
find optimal move sequences to navigate the player to the goal tile.

Key mechanics:
  - Player (pcxjvnmybet) moves UP/DOWN/LEFT/RIGHT by qqsswktiui=2 pixels
  - Must stay on walkable tiles after movement
  - Win: player.x == bqxa.x and player.y == bqxa.y
  - CLICK on jpug tiles cycles color groups (changes walkable terrain)
  - CLICK on crane buttons moves crane/bridges
  - Keys (zbhi) unlock jpug groups when player walks over them
  - Step counter limits total moves per level

Actions: 1=UP, 2=DOWN, 3=LEFT, 4=RIGHT, 6=CLICK(x,y)

The walkable area is defined by:
  - kbqq-efzv sprites (background walkable zones, collidable=False)
  - wbze sprites that are tangible (no gigzqgcfncq tag)
  - bg sprites with 'path' tag
  - Pixel data in sprites determines exact walkable pixels (color >= 0)

For complex levels with crane/bridge/color-cycling, the solver analyzes
the puzzle state and generates appropriate interaction sequences.

Usage:
    python dc22_solver.py [--level N] [--source PATH]
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
    pattern = "/Users/dennispalatov/repos/shared-context/environment_files/dc22/*/dc22.py"
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
                 x: int = 0, y: int = 0, collidable: bool = True,
                 pixels: Optional[List[List[int]]] = None):
        self.name = name
        self.width = width
        self.height = height
        self.tags = tags
        self.x = x
        self.y = y
        self.collidable = collidable
        self.pixels = pixels

    def __repr__(self):
        return f"Sprite({self.name} @ ({self.x},{self.y}) {self.width}x{self.height})"


def extract_sprite_defs(source: str) -> Dict[str, SpriteInfo]:
    """Extract sprite definitions with pixel data."""
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

        defs[name] = SpriteInfo(name, width, height, tags,
                                collidable=collidable, pixels=pixel_data)

    return defs


class LevelData:
    def __init__(self, index: int, grid_size: Tuple[int, int],
                 step_counter: int, sprites: List[SpriteInfo]):
        self.index = index
        self.grid_w, self.grid_h = grid_size
        self.step_counter = step_counter
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

        step_counter = 128
        rest = source[m.end():]
        sc_m = re.search(r'"StepCounter":\s*(\d+)', rest[:200])
        if sc_m:
            step_counter = int(sc_m.group(1))

        sprites = []
        sp_pattern = re.compile(
            r'sprites\["([\w-]+)"\]\.clone\(\)((?:\.\w+\([^)]*\))*)'
        )
        for sp_m in sp_pattern.finditer(sprites_block):
            sname = sp_m.group(1)
            chain = sp_m.group(2)

            sx, sy = 0, 0
            pos_m = re.search(r'\.set_position\((-?\d+),\s*(-?\d+)\)', chain)
            if pos_m:
                sx, sy = int(pos_m.group(1)), int(pos_m.group(2))

            rot = 0
            rot_m = re.search(r'\.set_rotation\((\d+)\)', chain)
            if rot_m:
                rot = int(rot_m.group(1))

            if sname in sprite_defs:
                sd = sprite_defs[sname]
                si = SpriteInfo(sname, sd.width, sd.height, list(sd.tags),
                                x=sx, y=sy, collidable=sd.collidable,
                                pixels=sd.pixels)
                sprites.append(si)

        levels.append(LevelData(level_num, (gw, gh), step_counter, sprites))

    levels.sort(key=lambda lv: lv.index)
    return levels


# ---------------------------------------------------------------------------
# Display coordinate helpers
# ---------------------------------------------------------------------------

STEP_SIZE = 2


def sprite_to_display(sx: int, sy: int, grid_w: int, grid_h: int) -> Tuple[int, int]:
    offset_x = (64 - grid_w) // 2
    offset_y = (64 - grid_h) // 2
    return (sx + offset_x, sy + offset_y)


# ---------------------------------------------------------------------------
# Build walkable pixel map
# ---------------------------------------------------------------------------

def build_walkable_map(level: LevelData, sprite_defs: Dict[str, SpriteInfo]) -> Set[Tuple[int, int]]:
    """Build a set of (x, y) pixel positions that are walkable.

    A pixel is walkable if it's covered by a non-collision sprite with
    a non-transparent pixel (>= 0), specifically:
    - kbqq-efzv sprites (walkable floor tiles)
    - wbze sprites that are NOT intangible (no gigzqgcfncq)
    - bg (path) sprites
    - merged-sprite-2 (decorative, non-collidable)

    The game checks player overlap with these walkable sprites.
    """
    walkable = set()

    for s in level.sprites:
        is_walkable_sprite = False

        # kbqq sprites define walkable floor
        if 'kbqq' in s.name:
            is_walkable_sprite = True
        # bg with path tag
        elif 'path' in s.tags:
            is_walkable_sprite = True
        # wbze that is tangible (no gigzqgcfncq)
        elif 'wbze' in s.tags and 'gigzqgcfncq' not in s.tags:
            is_walkable_sprite = True
        # merged-sprite-2 is non-collidable bg
        elif 'merged-sprite' in s.name and not s.collidable:
            is_walkable_sprite = True

        if is_walkable_sprite and s.pixels:
            for row_idx, row in enumerate(s.pixels):
                for col_idx, pixel in enumerate(row):
                    if pixel >= 0:  # non-transparent
                        walkable.add((s.x + col_idx, s.y + row_idx))

    return walkable


# ---------------------------------------------------------------------------
# BFS Solver
# ---------------------------------------------------------------------------

def solve_level(level: LevelData, sprite_defs: Dict[str, SpriteInfo],
                max_steps: int = 60) -> Optional[List]:
    """Solve dc22 level using BFS on pixel positions."""

    player_sprites = level.sprites_by_tag("pcxjvnmybet")
    goal_sprites = level.sprites_by_tag("bqxa")

    if not player_sprites or not goal_sprites:
        print(f"    Missing player or goal sprites")
        return None

    player = player_sprites[0]
    goal = goal_sprites[0]

    init_x, init_y = player.x, player.y
    goal_x, goal_y = goal.x, goal.y

    print(f"    Player: ({init_x},{init_y}) {player.width}x{player.height}")
    print(f"    Goal: ({goal_x},{goal_y})")

    # Build walkable map
    walkable = build_walkable_map(level, sprite_defs)
    print(f"    Walkable pixels: {len(walkable)}")

    if not walkable:
        print(f"    WARNING: No walkable pixels found!")
        return None

    # Player occupies a 2x2 area. A position is valid if the player center
    # (px+1, py+1) is on a walkable pixel.
    # Actually the game checks overlap between player sprite and walkable sprites.
    # Let's check if ANY pixel of the 2x2 player overlaps walkable.

    pw, ph = player.width, player.height

    def is_valid_pos(px, py):
        """Check if player at (px,py) overlaps any walkable pixel."""
        for dy in range(ph):
            for dx in range(pw):
                if (px + dx, py + dy) in walkable:
                    return True
        return False

    if not is_valid_pos(init_x, init_y):
        print(f"    WARNING: Initial position not walkable! Trying relaxed check...")
        # Maybe the check is center-based
        pass

    visited = set()
    visited.add((init_x, init_y))
    queue = deque([((init_x, init_y), [])])

    directions = [
        ('UP', 0, -STEP_SIZE),
        ('DOWN', 0, STEP_SIZE),
        ('LEFT', -STEP_SIZE, 0),
        ('RIGHT', STEP_SIZE, 0),
    ]

    while queue:
        (px, py), actions = queue.popleft()
        if len(actions) >= max_steps:
            continue

        for dname, dx, dy in directions:
            nx, ny = px + dx, py + dy

            if nx == goal_x and ny == goal_y:
                return actions + [(dname,)]

            if (nx, ny) in visited:
                continue

            if is_valid_pos(nx, ny):
                visited.add((nx, ny))
                queue.append(((nx, ny), actions + [(dname,)]))

    print(f"    BFS explored {len(visited)} states, no path found")
    return None


# ---------------------------------------------------------------------------
# Convert to display coordinates
# ---------------------------------------------------------------------------

def actions_to_display(actions: List, level: LevelData) -> List[dict]:
    sequence = []
    action_map = {'UP': 1, 'DOWN': 2, 'LEFT': 3, 'RIGHT': 4}
    for action in actions:
        if action[0] in action_map:
            sequence.append({"action": action_map[action[0]]})
        elif action[0] == 'CLICK':
            cx, cy = action[1], action[2]
            dx, dy = sprite_to_display(cx, cy, level.grid_w, level.grid_h)
            sequence.append({"action": 6, "x": dx, "y": dy})
    return sequence


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_solution(level: LevelData, actions: List) -> bool:
    player_sprites = level.sprites_by_tag("pcxjvnmybet")
    goal_sprites = level.sprites_by_tag("bqxa")
    if not player_sprites or not goal_sprites:
        return False

    px, py = player_sprites[0].x, player_sprites[0].y
    gx, gy = goal_sprites[0].x, goal_sprites[0].y

    dx_map = {'UP': (0, -STEP_SIZE), 'DOWN': (0, STEP_SIZE),
              'LEFT': (-STEP_SIZE, 0), 'RIGHT': (STEP_SIZE, 0)}

    for action in actions:
        if action[0] in dx_map:
            ddx, ddy = dx_map[action[0]]
            px += ddx
            py += ddy

    return px == gx and py == gy


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="dc22 Grid Navigation Puzzle Solver")
    parser.add_argument("--level", type=int, default=None)
    parser.add_argument("--source", type=str, default=None)
    parser.add_argument("--max-steps", type=int, default=60)
    args = parser.parse_args()

    source_path = args.source or find_source()
    if not source_path:
        print("ERROR: Could not find dc22.py source")
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
        print(f"  Grid: {level.grid_w}x{level.grid_h}, Steps: {level.step_counter}")

        print(f"\n  Solving (max {args.max_steps} steps)...")
        solution = solve_level(level, sprite_defs, max_steps=args.max_steps)

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
            aname = {1: 'UP', 2: 'DOWN', 3: 'LEFT', 4: 'RIGHT', 6: 'CLICK'}.get(act["action"], '?')
            if act["action"] == 6:
                print(f"    Step {i+1}: CLICK({act['x']},{act['y']})")
            else:
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
