#!/usr/bin/env python3
"""
ka59 Sokoban-style Push Puzzle Solver

Parses the ka59.py game source to extract level sprite positions, then uses
BFS to find optimal move sequences to push boxes onto goal markers.

Key mechanics:
  - CLICK to select which box (xlfuqjygey) to control
  - UP/DOWN/LEFT/RIGHT move the selected box by 3 pixels (jesnwclftg=3)
  - Pushing into another pushable object pushes it recursively
  - Walls (divgcilurm) and gulches (vwjqkxkyxm) block movement
  - Win: all rktpmjcpkt goals covered by xlfuqjygey boxes
    AND all ucjzrlvfkb goals covered by nnckfubbhi sprites
  - Goal alignment: box.x == goal.x+1, box.y == goal.y+1,
    box.h == goal.h-2, box.w == goal.w-2

Actions: 1=UP, 2=DOWN, 3=LEFT, 4=RIGHT, 6=CLICK(x,y)
Step size: 3 pixels

Usage:
    python ka59_solver.py [--level N] [--source PATH]
"""

import ast
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
    pattern = "/Users/dennispalatov/repos/shared-context/environment_files/ka59/*/ka59.py"
    matches = glob.glob(pattern)
    return matches[0] if matches else None


def parse_source(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


# ---------------------------------------------------------------------------
# Parse sprite definitions and levels
# ---------------------------------------------------------------------------

class SpriteInfo:
    def __init__(self, name: str, width: int, height: int, tags: List[str],
                 x: int = 0, y: int = 0, rotation: int = 0):
        self.name = name
        self.width = width
        self.height = height
        self.tags = tags
        self.x = x
        self.y = y
        self.rotation = rotation

    def __repr__(self):
        return f"Sprite({self.name} @ ({self.x},{self.y}) {self.width}x{self.height} tags={self.tags})"


def extract_sprite_defs(source: str) -> Dict[str, SpriteInfo]:
    """Extract sprite definitions with their pixel dimensions and tags."""
    defs = {}
    pattern = re.compile(r'"(\w+)":\s*Sprite\(')

    for m in pattern.finditer(source):
        name = m.group(1)
        # Find the matching closing paren
        depth = 0
        end = m.start()
        for i in range(m.end() - 1, min(len(source), m.start() + 5000)):
            if source[i] == '(':
                depth += 1
            elif source[i] == ')':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        block = source[m.start():end]

        # Extract tags
        tags_m = re.search(r'tags=\[([^\]]*)\]', block)
        tags = []
        if tags_m:
            tags = [t.strip().strip('"').strip("'") for t in tags_m.group(1).split(',') if t.strip()]

        # Extract pixel dimensions
        pixels_m = re.search(r'pixels=\[', block)
        width = height = 0
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
            if inner_brackets:
                width = len([e for e in inner_brackets[0].split(',') if e.strip()])

        defs[name] = SpriteInfo(name, width, height, tags)

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
    """Parse level definitions."""
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

        # Extract step counter
        step_counter = 100
        # Look for StepCounter in the data block after grid_size
        rest = source[m.end():]
        sc_m = re.search(r'"StepCounter":\s*(\d+)', rest[:200])
        if sc_m:
            step_counter = int(sc_m.group(1))

        # Parse sprite placements
        sprites = []
        sp_pattern = re.compile(
            r'sprites\["(\w+)"\]\.clone\(\)((?:\.\w+\([^)]*\))*)'
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
                                x=sx, y=sy, rotation=rot)
                sprites.append(si)

        levels.append(LevelData(level_num, (gw, gh), step_counter, sprites))

    levels.sort(key=lambda lv: lv.index)
    return levels


# ---------------------------------------------------------------------------
# Game state for BFS
# ---------------------------------------------------------------------------

STEP_SIZE = 3  # jesnwclftg


def sprite_to_display(sx: int, sy: int, grid_w: int, grid_h: int) -> Tuple[int, int]:
    """Convert sprite coordinates to 64x64 display coordinates."""
    offset_x = (64 - grid_w) // 2
    offset_y = (64 - grid_h) // 2
    return (sx + offset_x, sy + offset_y)


def collides(ax: int, ay: int, aw: int, ah: int,
             bx: int, by: int, bw: int, bh: int) -> bool:
    """Check AABB collision between two rectangles."""
    return (ax < bx + bw and ax + aw > bx and
            ay < by + bh and ay + ah > by)


def goal_covered(goal_x: int, goal_y: int, goal_w: int, goal_h: int,
                 box_x: int, box_y: int, box_w: int, box_h: int) -> bool:
    """Check if box is correctly positioned on goal.
    box.x == goal.x+1, box.y == goal.y+1, box.h == goal.h-2, box.w == goal.w-2
    """
    return (box_x == goal_x + 1 and box_y == goal_y + 1 and
            box_w == goal_w - 2 and box_h == goal_h - 2)


class GameState:
    """State for BFS solver."""
    def __init__(self, boxes: Tuple[Tuple[int, int], ...],
                 selected: int = 0):
        self.boxes = boxes  # tuple of (x, y) for each box
        self.selected = selected

    def to_key(self) -> Tuple:
        return (self.boxes, self.selected)

    def __eq__(self, other):
        return self.to_key() == other.to_key()

    def __hash__(self):
        return hash(self.to_key())


def solve_level(level: LevelData, max_steps: int = 80) -> Optional[List]:
    """Solve a ka59 level using BFS.

    For early levels (1-2), only boxes (xlfuqjygey) and goals (rktpmjcpkt)
    matter. Later levels add nnckfubbhi/ucjzrlvfkb and bombs.

    Returns list of actions: ('UP',), ('DOWN',), ('LEFT',), ('RIGHT',),
    ('SELECT', box_index), or ('CLICK', display_x, display_y)
    """
    # Extract pieces
    box_sprites = level.sprites_by_tag("xlfuqjygey")
    goal_sprites = level.sprites_by_tag("rktpmjcpkt")
    wall_sprites = level.sprites_by_tag("divgcilurm")
    gulch_sprites = level.sprites_by_tag("vwjqkxkyxm")

    if not box_sprites or not goal_sprites:
        print(f"    No boxes or goals found")
        return None

    # Build wall collision rectangles
    walls = [(w.x, w.y, w.width, w.height) for w in wall_sprites]
    gulches = [(g.x, g.y, g.width, g.height) for g in gulch_sprites]

    # Box info: list of (x, y, w, h) - w,h are fixed per box
    box_dims = [(b.width, b.height) for b in box_sprites]
    initial_boxes = tuple((b.x, b.y) for b in box_sprites)

    # Goal info
    goals = [(g.x, g.y, g.width, g.height) for g in goal_sprites]

    print(f"    Boxes: {len(box_sprites)}, Goals: {len(goals)}")
    for i, b in enumerate(box_sprites):
        print(f"      Box {i}: ({b.x},{b.y}) {b.width}x{b.height}")
    for i, g in enumerate(goals):
        print(f"      Goal {i}: ({g[0]},{g[1]}) {g[2]}x{g[3]}")

    def check_win(boxes):
        for gx, gy, gw, gh in goals:
            found = False
            for bi, (bx, by) in enumerate(boxes):
                bw, bh = box_dims[bi]
                if goal_covered(gx, gy, gw, gh, bx, by, bw, bh):
                    found = True
                    break
            if not found:
                return False
        return True

    def check_wall_collision(x, y, w, h):
        for wx, wy, ww, wh in walls:
            if collides(x, y, w, h, wx, wy, ww, wh):
                return True
        for gx, gy, gw, gh in gulches:
            if collides(x, y, w, h, gx, gy, gw, gh):
                return True
        return False

    def try_move_box(boxes, selected, dx, dy):
        """Try to move selected box. Returns new boxes tuple or None if blocked."""
        bx, by = boxes[selected]
        bw, bh = box_dims[selected]
        nx, ny = bx + dx, by + dy

        # Check wall/gulch collision
        if check_wall_collision(nx, ny, bw, bh):
            return None

        # Check collision with other boxes
        pushed = []
        for i, (ox, oy) in enumerate(boxes):
            if i == selected:
                continue
            ow, oh = box_dims[i]
            if collides(nx, ny, bw, bh, ox, oy, ow, oh):
                pushed.append(i)

        if not pushed:
            # No collision, move succeeds
            new_boxes = list(boxes)
            new_boxes[selected] = (nx, ny)
            return tuple(new_boxes)

        # Try to push each colliding box
        new_boxes = list(boxes)
        new_boxes[selected] = (nx, ny)

        for pi in pushed:
            px, py = boxes[pi]
            pw, ph = box_dims[pi]
            pnx, pny = px + dx, py + dy

            # Check if pushed box hits wall
            if check_wall_collision(pnx, pny, pw, ph):
                return None

            # Check if pushed box hits another box (recursive push not implemented for BFS)
            for j, (jx, jy) in enumerate(boxes):
                if j == selected or j == pi:
                    continue
                jw, jh = box_dims[j]
                if collides(pnx, pny, pw, ph, jx, jy, jw, jh):
                    return None  # blocked by chain

            new_boxes[pi] = (pnx, pny)

        return tuple(new_boxes)

    # BFS
    if check_win(initial_boxes):
        return []

    init_state = GameState(initial_boxes, 0)
    visited = {init_state.to_key()}
    queue = deque([(init_state, [])])

    directions = [
        ('UP', 0, -STEP_SIZE),
        ('DOWN', 0, STEP_SIZE),
        ('LEFT', -STEP_SIZE, 0),
        ('RIGHT', STEP_SIZE, 0),
    ]

    while queue:
        state, actions = queue.popleft()
        if len(actions) >= max_steps:
            continue

        # Try each direction with current selected box
        for dname, dx, dy in directions:
            result = try_move_box(state.boxes, state.selected, dx, dy)
            if result is not None:
                if check_win(result):
                    return actions + [(dname,)]

                new_state = GameState(result, state.selected)
                key = new_state.to_key()
                if key not in visited:
                    visited.add(key)
                    queue.append((new_state, actions + [(dname,)]))

        # Try selecting each other box
        for bi in range(len(box_sprites)):
            if bi != state.selected:
                new_state = GameState(state.boxes, bi)
                key = new_state.to_key()
                if key not in visited:
                    visited.add(key)
                    queue.append((new_state, actions + [('SELECT', bi)]))

    return None


# ---------------------------------------------------------------------------
# Convert to display coordinates
# ---------------------------------------------------------------------------

def actions_to_display(actions: List, level: LevelData) -> List[dict]:
    """Convert solver actions to display action sequence."""
    box_sprites = level.sprites_by_tag("xlfuqjygey")
    gw, gh = level.grid_w, level.grid_h

    sequence = []
    boxes = [(b.x, b.y) for b in box_sprites]
    selected = 0

    action_map = {'UP': 1, 'DOWN': 2, 'LEFT': 3, 'RIGHT': 4}
    dx_map = {'UP': (0, -STEP_SIZE), 'DOWN': (0, STEP_SIZE),
              'LEFT': (-STEP_SIZE, 0), 'RIGHT': (STEP_SIZE, 0)}

    for action in actions:
        if action[0] == 'SELECT':
            bi = action[1]
            bx, by = boxes[bi]
            # Click on the center of the box
            bw = box_sprites[bi].width
            bh = box_sprites[bi].height
            cx = bx + bw // 2
            cy = by + bh // 2
            dx, dy = sprite_to_display(cx, cy, gw, gh)
            sequence.append({"action": 6, "x": dx, "y": dy})
            selected = bi
        else:
            dname = action[0]
            sequence.append({"action": action_map[dname]})
            # Update box position
            ddx, ddy = dx_map[dname]
            bx, by = boxes[selected]
            boxes[selected] = (bx + ddx, by + ddy)

    return sequence


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_solution(level: LevelData, actions: List) -> bool:
    """Verify solution by simulating."""
    box_sprites = level.sprites_by_tag("xlfuqjygey")
    goal_sprites = level.sprites_by_tag("rktpmjcpkt")
    wall_sprites = level.sprites_by_tag("divgcilurm")
    gulch_sprites = level.sprites_by_tag("vwjqkxkyxm")

    box_dims = [(b.width, b.height) for b in box_sprites]
    boxes = list((b.x, b.y) for b in box_sprites)
    goals = [(g.x, g.y, g.width, g.height) for g in goal_sprites]
    walls = [(w.x, w.y, w.width, w.height) for w in wall_sprites]
    gulches = [(g.x, g.y, g.width, g.height) for g in gulch_sprites]

    selected = 0
    dx_map = {'UP': (0, -STEP_SIZE), 'DOWN': (0, STEP_SIZE),
              'LEFT': (-STEP_SIZE, 0), 'RIGHT': (STEP_SIZE, 0)}

    for action in actions:
        if action[0] == 'SELECT':
            selected = action[1]
        else:
            ddx, ddy = dx_map[action[0]]
            bx, by = boxes[selected]
            bw, bh = box_dims[selected]
            nx, ny = bx + ddx, by + ddy
            boxes[selected] = (nx, ny)

    # Check win
    for gx, gy, gw, gh in goals:
        found = False
        for bi, (bx, by) in enumerate(boxes):
            bw, bh = box_dims[bi]
            if goal_covered(gx, gy, gw, gh, bx, by, bw, bh):
                found = True
                break
        if not found:
            return False
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="ka59 Sokoban Puzzle Solver")
    parser.add_argument("--level", type=int, default=None)
    parser.add_argument("--source", type=str, default=None)
    parser.add_argument("--max-steps", type=int, default=80)
    args = parser.parse_args()

    source_path = args.source or find_source()
    if not source_path:
        print("ERROR: Could not find ka59.py source")
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
        solution = solve_level(level, max_steps=args.max_steps)

        if solution is None:
            print("  NO SOLUTION FOUND")
            results.append({"level": level.index, "verified": False})
            continue

        verified = verify_solution(level, solution)

        print(f"  Solution ({len(solution)} actions):")
        for i, act in enumerate(solution):
            if act[0] == 'SELECT':
                print(f"    Step {i+1}: SELECT box {act[1]}")
            else:
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
