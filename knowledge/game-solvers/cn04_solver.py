#!/usr/bin/env python3
"""
cn04 Jigsaw Connector Solver

Parses cn04.py to extract sprite definitions with connector pins (color 8),
then for each level determines optimal placement (position + rotation) for
each sprite so that all grey pins (8) overlap with another sprite's grey pin.

Actions: CLICK to select, ARROWS to move, ROTATE (ACTION5) to rotate 90 CW.

Usage:
    python cn04_solver.py [--level N] [--source PATH]
"""

import re
import sys
import ast
import argparse
import numpy as np
from itertools import permutations
from collections import deque
from typing import List, Tuple, Optional, Dict, Set, FrozenSet

GAME_SOURCE_DEFAULT = (
    "/Users/dennispalatov/repos/shared-context/environment_files/"
    "cn04/65d47d14/cn04.py"
)

# ---------------------------------------------------------------------------
# Parse source
# ---------------------------------------------------------------------------

def parse_source(path: str) -> str:
    with open(path) as f:
        return f.read()


def extract_sprite_pixels(source: str) -> Dict[str, list]:
    """Extract pixel arrays for all sprites."""
    sprites = {}
    # Match sprite definitions
    pattern = re.compile(
        r'"(\w+)":\s*Sprite\(\s*pixels=(\[.*?\]),\s*name=',
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


def extract_sprite_tags(source: str) -> Dict[str, List[str]]:
    """Extract tags for each sprite."""
    tag_map = {}
    pattern = re.compile(
        r'"(\w+)":\s*Sprite\([^)]*?tags=\[([^\]]*)\]',
        re.DOTALL,
    )
    for m in pattern.finditer(source):
        name = m.group(1)
        tags_raw = m.group(2)
        tags = [t.strip().strip('"').strip("'") for t in tags_raw.split(",") if t.strip()]
        tag_map[name] = tags
    return tag_map


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

        bg_m = re.search(r'"BackgroundColour":\s*(\d+)', data_block)
        bg_color = int(bg_m.group(1)) if bg_m else 0

        placements = []
        sp_pattern = re.compile(
            r'sprites\["(\w+)"\]\.clone\(\)'
            r'(?:\.set_position\((\d+),\s*(\d+)\))?'
            r'(?:\.set_rotation\((\d+)\))?'
        )
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
            'bg_color': bg_color,
        })

    return levels


# ---------------------------------------------------------------------------
# Sprite geometry helpers
# ---------------------------------------------------------------------------

def get_pin_positions(pixels: list, rotation: int = 0) -> Set[Tuple[int, int]]:
    """Get the positions of grey pins (color 8) after rotation.

    Returns set of (local_x, local_y) positions in the RENDERED coordinate system.
    """
    arr = np.array(pixels)
    # Apply rotation
    if rotation == 90:
        arr = np.rot90(arr, k=-1)  # CW 90
    elif rotation == 180:
        arr = np.rot90(arr, k=-2)
    elif rotation == 270:
        arr = np.rot90(arr, k=-3)

    pins = set()
    for y in range(arr.shape[0]):
        for x in range(arr.shape[1]):
            if arr[y, x] == 8:
                pins.add((x, y))
    return pins


def get_all_visible_positions(pixels: list, rotation: int = 0) -> Set[Tuple[int, int]]:
    """Get all visible (non-transparent) pixel positions after rotation."""
    arr = np.array(pixels)
    if rotation == 90:
        arr = np.rot90(arr, k=-1)
    elif rotation == 180:
        arr = np.rot90(arr, k=-2)
    elif rotation == 270:
        arr = np.rot90(arr, k=-3)

    positions = set()
    for y in range(arr.shape[0]):
        for x in range(arr.shape[1]):
            if arr[y, x] >= 0:
                positions.add((x, y))
    return positions


def get_world_pins(pixels: list, x: int, y: int, rotation: int) -> Set[Tuple[int, int]]:
    """Get world-coordinate pin positions."""
    local_pins = get_pin_positions(pixels, rotation)
    return {(px + x, py + y) for px, py in local_pins}


def get_sprite_size(pixels: list, rotation: int = 0) -> Tuple[int, int]:
    """Get (width, height) of sprite after rotation."""
    arr = np.array(pixels)
    if rotation in (90, 270):
        return (arr.shape[0], arr.shape[1])
    return (arr.shape[1], arr.shape[0])


# ---------------------------------------------------------------------------
# Solver: BFS over sprite positions/rotations
# ---------------------------------------------------------------------------

class SpriteState:
    """State of a single sprite: position and rotation."""
    def __init__(self, name: str, x: int, y: int, rot: int, pixels: list):
        self.name = name
        self.x = x
        self.y = y
        self.rot = rot
        self.pixels = pixels

    def world_pins(self) -> Set[Tuple[int, int]]:
        return get_world_pins(self.pixels, self.x, self.y, self.rot)

    def key(self) -> Tuple:
        return (self.name, self.x, self.y, self.rot)


def check_all_pins_matched(sprites_states: List[SpriteState]) -> bool:
    """Check if all grey pins are matched (overlapping with another sprite's pin)."""
    # Collect all world pins per sprite
    all_pins = {}
    for ss in sprites_states:
        pins = ss.world_pins()
        for p in pins:
            if p not in all_pins:
                all_pins[p] = []
            all_pins[p].append(ss.name)

    # Check: every pin position must have exactly 2 sprites
    for ss in sprites_states:
        pins = ss.world_pins()
        for p in pins:
            if len(all_pins.get(p, [])) < 2:
                return False
    return True


def count_unmatched_pins(sprites_states: List[SpriteState]) -> int:
    """Count unmatched pins."""
    all_pins = {}
    for ss in sprites_states:
        pins = ss.world_pins()
        for p in pins:
            if p not in all_pins:
                all_pins[p] = 0
            all_pins[p] += 1

    unmatched = 0
    for ss in sprites_states:
        pins = ss.world_pins()
        for p in pins:
            if all_pins.get(p, 0) < 2:
                unmatched += 1
    return unmatched


def solve_level_bfs(level: dict, sprite_pixels: dict, sprite_tags: dict,
                    verbose: bool = True) -> Optional[dict]:
    """Solve a level by trying all position/rotation combos for movable sprites."""
    placements = level['placements']
    gw, gh = level['grid']

    # Only consider clickable sprites (sys_click tag)
    clickable = []
    for name, x, y, rot in placements:
        tags = sprite_tags.get(name, [])
        if 'sys_click' in tags and name in sprite_pixels:
            clickable.append(SpriteState(name, x, y, rot, sprite_pixels[name]))

    if not clickable:
        if verbose:
            print("  No clickable sprites found")
        return None

    if verbose:
        print(f"  {len(clickable)} clickable sprites")
        for ss in clickable:
            pins = ss.world_pins()
            print(f"    {ss.name} at ({ss.x},{ss.y}) rot={ss.rot}, pins={len(pins)}")

    # Check if already solved
    if check_all_pins_matched(clickable):
        if verbose:
            print("  Already solved!")
        return {'level': level['num'], 'actions': [], 'verified': True}

    # For small number of sprites, try BFS on position adjustments
    # For each sprite, try moving it and rotating it

    # Strategy: for each pair of sprites, find positions where their pins align
    # Then check if all pins are matched

    best_actions = None
    best_len = float('inf')

    # Try brute force: for each sprite, try all 4 rotations and reasonable positions
    if len(clickable) <= 4:
        result = solve_incremental(clickable, gw, gh, verbose)
        if result:
            return {'level': level['num'], **result}

    if verbose:
        print("  Could not find solution")
    return None


def solve_incremental(sprites: List[SpriteState], gw: int, gh: int,
                      verbose: bool = True) -> Optional[dict]:
    """Solve by trying to match each sprite's pins incrementally.

    Fix the first sprite, then for each subsequent sprite, find position/rotation
    that matches some pins.
    """
    if len(sprites) == 0:
        return None

    # For each sprite, enumerate positions where its pins could match with others
    # Strategy: fix first sprite, move others to match

    # First, collect all pins from sprite 0
    fixed = sprites[0]
    fixed_pins = fixed.world_pins()

    if verbose:
        print(f"  Fixing {fixed.name} at ({fixed.x},{fixed.y}) rot={fixed.rot}")
        print(f"    Pins: {sorted(fixed_pins)}")

    # For remaining sprites, find position+rotation that matches pins
    remaining = sprites[1:]

    # BFS over states: (positions of all sprites)
    # State = tuple of (x, y, rot) for each remaining sprite
    # This is too expensive for general case

    # Instead, use greedy: for each remaining sprite, find best position
    all_solutions = []

    def search(placed: List[SpriteState], to_place: List[SpriteState]):
        if not to_place:
            if check_all_pins_matched(placed):
                all_solutions.append([ss.key() for ss in placed])
            return

        sprite = to_place[0]
        rest = to_place[1:]

        # Collect all existing pins from placed sprites
        existing_pins = set()
        for ss in placed:
            existing_pins.update(ss.world_pins())

        # For each rotation, find positions that overlap some pins
        for rot in [0, 90, 180, 270]:
            local_pins = get_pin_positions(sprite.pixels, rot)
            if not local_pins:
                continue

            # For each of this sprite's pins, try to align it with each existing pin
            for lp in local_pins:
                for ep in existing_pins:
                    # Position sprite so that local pin lp aligns with world pin ep
                    sx = ep[0] - lp[0]
                    sy = ep[1] - lp[1]

                    # Check bounds
                    size = get_sprite_size(sprite.pixels, rot)
                    if sx < 0 or sy < 0 or sx + size[0] > gw or sy + size[1] > gh:
                        continue

                    new_ss = SpriteState(sprite.name, sx, sy, rot, sprite.pixels)
                    new_pins = new_ss.world_pins()

                    # Check that all of this sprite's pins either match or
                    # will be matched by future sprites
                    placed_list = placed + [new_ss]

                    # Quick check: no pins overlap with non-pin positions of other sprites
                    # (This is a simplification)

                    if len(all_solutions) < 1:  # Find first solution
                        search(placed_list, rest)

                    if all_solutions:
                        return

    search([fixed], remaining)

    if all_solutions:
        sol = all_solutions[0]
        # Compute actions to move sprites to solution positions
        actions = compute_movement_actions(sprites, sol, gw, gh)

        # Verify
        final_states = []
        for i, (name, x, y, rot) in enumerate(sol):
            final_states.append(SpriteState(name, x, y, rot, sprites[i].pixels))
        ok = check_all_pins_matched(final_states)

        if verbose:
            print(f"  Solution found!")
            for name, x, y, rot in sol:
                print(f"    {name}: ({x},{y}) rot={rot}")
            print(f"  {'VERIFIED OK' if ok else 'VERIFICATION FAILED'}")

        return {'actions': actions, 'verified': ok,
                'solution': sol}
    return None


def compute_movement_actions(original: List[SpriteState],
                             solution: List[Tuple], gw: int, gh: int) -> List[str]:
    """Compute click/move/rotate actions to reach solution from initial state.

    Output format: sequence of action descriptions.
    """
    actions = []
    offset_x = (64 - gw) // 2
    offset_y = (64 - gh) // 2

    for i, (name, tx, ty, trot) in enumerate(solution):
        orig = original[i]
        if orig.x == tx and orig.y == ty and orig.rot == trot:
            continue  # No change needed

        # Click to select this sprite
        # Display coordinates for click
        click_x = orig.x + offset_x
        click_y = orig.y + offset_y
        actions.append(f"click({click_x},{click_y})")

        # Rotate if needed
        cur_rot = orig.rot
        while cur_rot != trot:
            actions.append("ACTION5")  # Rotate 90 CW
            cur_rot = (cur_rot + 90) % 360

        # Move
        dx = tx - orig.x
        dy = ty - orig.y

        # After rotation, the sprite's bounding box may change
        # Need to account for position shift due to rotation
        # For simplicity, compute moves from original position
        cur_x, cur_y = orig.x, orig.y

        # Move in x
        while cur_x < tx:
            actions.append("RIGHT")
            cur_x += 1
        while cur_x > tx:
            actions.append("LEFT")
            cur_x -= 1

        # Move in y
        while cur_y < ty:
            actions.append("DOWN")
            cur_y += 1
        while cur_y > ty:
            actions.append("UP")
            cur_y -= 1

    return actions


def grid_to_display(gx: int, gy: int, gw: int, gh: int) -> Tuple[int, int]:
    ox = (64 - gw) // 2
    oy = (64 - gh) // 2
    return (gx + ox, gy + oy)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="cn04 Jigsaw Connector Solver")
    parser.add_argument("--level", type=int, default=None)
    parser.add_argument("--source", type=str, default=GAME_SOURCE_DEFAULT)
    args = parser.parse_args()

    print("Parsing game source...")
    source = parse_source(args.source)

    print("Extracting sprites...")
    sprite_pixels = extract_sprite_pixels(source)
    sprite_tags = extract_sprite_tags(source)
    print(f"  Found {len(sprite_pixels)} sprites")

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
        print(f"  Grid: {lv['grid']}")
        result = solve_level_bfs(lv, sprite_pixels, sprite_tags)
        if result:
            results.append(result)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for r in results:
        status = "VERIFIED OK" if r['verified'] else "FAILED"
        n_actions = len(r['actions'])
        print(f"  Level {r['level']}: {n_actions} actions ... {status}")
        if r['actions']:
            for a in r['actions']:
                print(f"    {a}")


if __name__ == "__main__":
    main()
