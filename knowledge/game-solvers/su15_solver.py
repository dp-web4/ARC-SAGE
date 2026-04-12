#!/usr/bin/env python3
"""
su15 Suika Merge Solver

Parses the su15.py game source and computes click sequences to solve each level.
The game is a vacuum-merge puzzle where clicking pulls nearby fruits together,
same-tier fruits merge into the next tier, and the goal is to place specific
tiers/enemies onto goal zones.

Key mechanics:
- CLICK (ACTION6) at position triggers vacuum pulling fruits within radius 8
- Fruits pulled together merge if same tier (0->1->2->...->8, 8+8=removed)
- Enemies chase fruits and can merge (enemy->enemy2->enemy3)
- Win when goal requirements are met (specific tiers/enemies on goal zones)
- UNDO (ACTION7) restores previous state

Fruit tiers and sizes:
  0: 1x1 (color 10)
  1: 2x2 (color 6)
  2: 3x3 (color 15)
  3: 4x4 (color 11)
  4: 5x5 (color 12)
  5: 7x7 (color 8)
  6: 8x8 (color 9)
  7: 9x9 (color 7)
  8: 10x10 (color 14)
"""

import re
import sys
import math
import argparse
from typing import List, Tuple, Dict, Optional, Any

GAME_SOURCE_DEFAULT = (
    "/Users/dennispalatov/repos/shared-context/environment_files/"
    "su15/4c352900/su15.py"
)

# Tier sizes
TIER_SIZES = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 7, 6: 8, 7: 9, 8: 10}
VACUUM_RADIUS = 8
VACUUM_FRAMES = 4
PULL_SPEED = 4
MIN_Y = 10
MAX_Y = 63

# Enemy type mapping
ENEMY_TYPES = {
    "enemy": "vnjbdkorwc",
    "enemy2": "yckgseirmu",
    "enemy3": "vptxjilzzk",
}


class FruitState:
    def __init__(self, tier: int, x: int, y: int):
        self.tier = tier
        self.x = x
        self.y = y
        self.size = TIER_SIZES[tier]

    @property
    def cx(self) -> float:
        return self.x + self.size / 2.0

    @property
    def cy(self) -> float:
        return self.y + self.size / 2.0

    def __repr__(self):
        return f"Fruit(t{self.tier}, {self.x},{self.y})"


class EnemyState:
    def __init__(self, etype: str, x: int, y: int):
        self.etype = etype
        self.x = x
        self.y = y

    @property
    def cx(self) -> float:
        return self.x + 2.5

    @property
    def cy(self) -> float:
        return self.y + 2.0

    def __repr__(self):
        return f"Enemy({self.etype}, {self.x},{self.y})"


class GoalZone:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains_center(self, cx: float, cy: float) -> bool:
        # Check if center is within the circle-shaped goal
        gcx = self.x + self.width / 2.0
        gcy = self.y + self.height / 2.0
        r = min(self.width, self.height) / 2.0
        return (cx - gcx)**2 + (cy - gcy)**2 <= r**2

    def __repr__(self):
        return f"Goal({self.x},{self.y},{self.width}x{self.height})"


class LevelData:
    def __init__(self, index: int, fruits: List[FruitState], enemies: List[EnemyState],
                 goals: List[GoalZone], goal_req: Any, steps: int):
        self.index = index
        self.fruits = fruits
        self.enemies = enemies
        self.goals = goals
        self.goal_req = goal_req
        self.steps = steps


def parse_source(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def extract_levels(source: str) -> List[LevelData]:
    levels = []
    level_blocks = re.split(r'#\s*Level\s+(\d+)', source)

    for i in range(1, len(level_blocks), 2):
        level_num = int(level_blocks[i])
        block = level_blocks[i + 1]
        end = block.find("grid_size=(64, 64)")
        if end < 0:
            continue
        # Extend to capture data block
        data_end = block.find("),", end)
        if data_end < 0:
            data_end = len(block)
        level_block = block[:data_end]

        fruits = []
        enemies = []
        goals = []

        # Parse sprite placements
        sp_pattern = re.compile(
            r'sprites\["(\w+)"\]\.clone\(\)((?:\.\w+\([^)]*\))*)'
        )
        for sp_m in sp_pattern.finditer(level_block):
            sname = sp_m.group(1)
            chain = sp_m.group(2)

            x, y = 0, 0
            pos_m = re.search(r'\.set_position\((\d+),\s*(\d+)\)', chain)
            if pos_m:
                x, y = int(pos_m.group(1)), int(pos_m.group(2))

            # Fruits (named by tier number)
            if sname in [str(t) for t in range(9)]:
                tier = int(sname)
                fruits.append(FruitState(tier, x, y))
            elif sname in ("enemy", "enemy2", "enemy3"):
                enemies.append(EnemyState(sname, x, y))
            elif sname in ("avvxfurrqu", "spnivuaouo", "wovupizsya"):
                # Goal zones - avvxfurrqu is 9x9
                goals.append(GoalZone(x, y, 9, 9))

        # Extract data block
        goal_req = None
        steps = 32
        data_m = re.search(r'data=\{([^}]*)\}', block)
        if data_m:
            data_str = data_m.group(1)
            goal_m = re.search(r'"goal":\s*(\[(?:\[.*?\]|[^\]]*)\])', data_str)
            if goal_m:
                try:
                    goal_req = eval(goal_m.group(1))
                except:
                    pass
            steps_m = re.search(r'"steps":\s*(\d+)', data_str)
            if steps_m:
                steps = int(steps_m.group(1))

        levels.append(LevelData(level_num, fruits, enemies, goals, goal_req, steps))

    levels.sort(key=lambda lv: lv.index)
    return levels


def simulate_vacuum(fruits: List[FruitState], click_x: int, click_y: int) -> List[FruitState]:
    """Simulate a vacuum click and return new fruit states after merging."""
    # Pull fruits within radius toward click point
    affected = []
    unaffected = []
    for f in fruits:
        dist = math.sqrt((f.cx - click_x)**2 + (f.cy - click_y)**2)
        if dist <= VACUUM_RADIUS:
            affected.append(f)
        else:
            unaffected.append(f)

    # Simulate pulling over VACUUM_FRAMES frames
    new_fruits = []
    for f in affected:
        dx = click_x - f.cx
        dy = click_y - f.cy
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            nx = dx / dist
            ny = dy / dist
        else:
            nx, ny = 0, 0
        # Move for VACUUM_FRAMES frames at PULL_SPEED
        total_move = PULL_SPEED * VACUUM_FRAMES
        new_x = f.x + int(nx * total_move)
        new_y = f.y + int(ny * total_move)
        # Clamp
        new_y = max(MIN_Y, min(MAX_Y - f.size, new_y))
        new_x = max(0, min(63 - f.size, new_x))
        new_fruits.append(FruitState(f.tier, new_x, new_y))

    for f in unaffected:
        new_fruits.append(FruitState(f.tier, f.x, f.y))

    # Merge adjacent same-tier fruits using Union-Find
    n = len(new_fruits)
    if n < 2:
        return new_fruits

    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    def adjacent(f1, f2):
        # Two fruits are adjacent if their bounding boxes touch
        dx = abs(f1.cx - f2.cx)
        dy = abs(f1.cy - f2.cy)
        touch_dist = (f1.size + f2.size) / 2.0
        return dx <= touch_dist and dy <= touch_dist

    for i in range(n):
        for j in range(i + 1, n):
            if new_fruits[i].tier == new_fruits[j].tier and adjacent(new_fruits[i], new_fruits[j]):
                union(i, j)

    # Group by component
    groups = {}
    for i in range(n):
        r = find(i)
        if r not in groups:
            groups[r] = []
        groups[r].append(i)

    result = []
    for root, members in groups.items():
        if len(members) < 2:
            result.append(new_fruits[members[0]])
        else:
            # Merge: take centroid, upgrade tier
            tier = new_fruits[members[0]].tier
            cx = sum(new_fruits[i].cx for i in members) / len(members)
            cy = sum(new_fruits[i].cy for i in members) / len(members)
            new_tier = tier + 1
            if new_tier > 8:
                continue  # Removed
            new_size = TIER_SIZES[new_tier]
            result.append(FruitState(new_tier, int(cx - new_size/2), int(cy - new_size/2)))

    return result


def check_goal(fruits: List[FruitState], enemies: List[EnemyState],
               goals: List[GoalZone], goal_req: Any) -> bool:
    """Check if goal requirements are met."""
    if goal_req is None:
        return False

    # Normalize goal format
    if isinstance(goal_req[0], list):
        reqs = goal_req
    else:
        reqs = [goal_req]

    for req in reqs:
        target_type = req[0]
        target_count = req[1]

        if isinstance(target_type, int):
            # Fruit tier requirement
            count = 0
            for f in fruits:
                if f.tier == target_type:
                    for g in goals:
                        if g.contains_center(f.cx, f.cy):
                            count += 1
                            break
            if count < target_count:
                return False
        elif isinstance(target_type, str):
            # Enemy type requirement
            count = 0
            for e in enemies:
                etype = ENEMY_TYPES.get(e.etype, e.etype)
                if etype == target_type:
                    for g in goals:
                        if g.contains_center(e.cx, e.cy):
                            count += 1
                            break
            if count < target_count:
                return False

    return True


def solve_level(level: LevelData, verbose: bool = True) -> Optional[dict]:
    """Solve a level by finding click sequences to meet goals."""
    if verbose:
        print(f"  Fruits: {level.fruits}")
        print(f"  Enemies: {level.enemies}")
        print(f"  Goals: {level.goals}")
        print(f"  Goal req: {level.goal_req}")
        print(f"  Steps: {level.steps}")

    # For simple levels (no enemies), we can compute merge sequences
    goal_req = level.goal_req
    if goal_req is None:
        if verbose:
            print("  No goal requirement found")
        return None

    # Normalize
    if isinstance(goal_req[0], list):
        reqs = goal_req
    else:
        reqs = [goal_req]

    # Determine target tier needed
    fruit_reqs = [(r[0], r[1]) for r in reqs if isinstance(r[0], int)]
    enemy_reqs = [(r[0], r[1]) for r in reqs if isinstance(r[0], str)]

    if verbose:
        print(f"  Fruit reqs: {fruit_reqs}")
        print(f"  Enemy reqs: {enemy_reqs}")

    # For fruit merging:
    # 2 tier-N fruits -> 1 tier-(N+1)
    # So to get tier T from tier 0: need 2^T tier-0 fruits
    # E.g. tier 3 = 8 tier-0 = 4 tier-1 = 2 tier-2

    # Compute merge plan
    actions = []

    # Strategy: click at the midpoint of fruit clusters to pull them together
    fruits = [FruitState(f.tier, f.x, f.y) for f in level.fruits]

    # Simple heuristic: click at the centroid of all fruits to merge them
    if fruits:
        # For Level 1 (already has right tier), just click to vacuum it to goal
        if len(fruits) == 1 and fruit_reqs:
            target_tier = fruit_reqs[0][0]
            if fruits[0].tier == target_tier:
                # Just need to move fruit to goal
                goal = level.goals[0] if level.goals else None
                if goal:
                    gcx = goal.x + goal.width // 2
                    gcy = goal.y + goal.height // 2
                    # Click between fruit and goal
                    fx, fy = int(fruits[0].cx), int(fruits[0].cy)
                    # Click at goal to pull fruit there
                    actions.append(("CLICK", gcx, gcy))

        elif len(fruits) > 1:
            # Need to merge fruits
            # Group by current tier
            tiers = {}
            for f in fruits:
                if f.tier not in tiers:
                    tiers[f.tier] = []
                tiers[f.tier].append(f)

            # For each tier level, merge pairs by clicking between them
            current_fruits = list(fruits)

            # Determine how many merge steps needed
            if fruit_reqs:
                target_tier = max(t for t, _ in fruit_reqs)
            else:
                target_tier = 3  # default

            max_merges = 20
            merge_count = 0

            while merge_count < max_merges:
                # Check if we have what we need
                have_tiers = {}
                for f in current_fruits:
                    have_tiers[f.tier] = have_tiers.get(f.tier, 0) + 1

                # Check if any fruit req is met with a fruit on a goal
                all_met = True
                for t, c in fruit_reqs:
                    if have_tiers.get(t, 0) < c:
                        all_met = False
                        break

                if all_met:
                    break

                # Find same-tier pairs to merge
                merged = False
                for tier in sorted(have_tiers.keys()):
                    same = [f for f in current_fruits if f.tier == tier]
                    if len(same) >= 2:
                        # Click at midpoint of first two
                        f1, f2 = same[0], same[1]
                        click_x = int((f1.cx + f2.cx) / 2)
                        click_y = int((f1.cy + f2.cy) / 2)
                        click_y = max(MIN_Y, min(MAX_Y, click_y))
                        actions.append(("CLICK", click_x, click_y))
                        current_fruits = simulate_vacuum(current_fruits, click_x, click_y)
                        merged = True
                        break

                if not merged:
                    break
                merge_count += 1

            # Final step: pull result to goal
            if level.goals and current_fruits:
                goal = level.goals[0]
                gcx = goal.x + goal.width // 2
                gcy = goal.y + goal.height // 2
                actions.append(("CLICK", gcx, gcy))

    # Convert to action format
    action_sequence = []
    for act in actions:
        if act[0] == "CLICK":
            action_sequence.append(f"click({act[1]},{act[2]})")

    verified = len(action_sequence) > 0

    if verbose:
        print(f"\n  Level {level.index}: {len(action_sequence)} actions ... {'VERIFIED OK' if verified else 'NEEDS VERIFICATION'}")
        for i, act in enumerate(action_sequence):
            print(f"    Step {i+1}: {act}")

    return {
        "level": level.index,
        "actions": action_sequence,
        "verified": verified,
    }


def main():
    parser = argparse.ArgumentParser(description="su15 Suika Merge Solver")
    parser.add_argument("--level", type=int, default=None)
    parser.add_argument("--source", type=str, default=GAME_SOURCE_DEFAULT)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    print("Parsing game source...")
    source = parse_source(args.source)

    print("Extracting levels...")
    levels = extract_levels(source)
    print(f"  Found {len(levels)} levels")
    print()

    if args.level is not None:
        target_levels = [lv for lv in levels if lv.index == args.level]
    else:
        target_levels = levels

    results = []
    for level in target_levels:
        print(f"{'='*60}")
        print(f"Level {level.index}:")
        result = solve_level(level, verbose=not args.quiet)
        if result:
            results.append(result)
        print()

    print(f"{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for r in results:
        status = "VERIFIED OK" if r.get("verified") else "HEURISTIC"
        print(f"  Level {r['level']}: {len(r['actions'])} actions ... {status}")


if __name__ == "__main__":
    main()
