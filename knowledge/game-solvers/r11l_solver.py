#!/usr/bin/env python3
"""
r11l Pick-and-Place Creature Assembly Solver

Parses r11l.py and computes click sequences to move limbs so that each
creature's body lands on its matching target.

Key mechanics:
- Bodies auto-position at centroid of their limbs
- Click a limb to select it, click empty space to move it
- Body collides with wall = move rejected (no cost)
- Body collides with danger zone = penalty (5 = lose)
- Win: all bodies overlap their targets with matching colors
- For yukft bodies: must absorb correct stamp sprites first
- Groups named "anqcf" excluded from win check
- 60 action limit total

Strategy:
- For each color group, compute the target body position
- Determine limb positions that place the body centroid at the target
- Output click sequences: select limb, click destination

Display coords: Camera 64x64 default, grid_size=64x64, so 1:1.

Usage:
    python r11l_solver.py [--source PATH]
"""

import re
import ast
import sys
import argparse
import numpy as np
from typing import Dict, List, Tuple, Optional


GAME_SOURCE_DEFAULT = (
    "/Users/dennispalatov/repos/shared-context/environment_files/"
    "r11l/aa269680/r11l.py"
)


def parse_source(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def extract_sprite_pixels(source: str) -> Dict[str, list]:
    """Extract sprite name -> pixels from source."""
    pixels_map = {}
    pat = re.compile(
        r'"([\w-]+)":\s*Sprite\(\s*pixels=(\[(?:\s*\[[^\]]*\],?\s*)*\])',
        re.DOTALL)
    for m in pat.finditer(source):
        name = m.group(1)
        pixels_map[name] = ast.literal_eval(m.group(2))
    return pixels_map


def extract_levels(source: str) -> List[dict]:
    """Extract level data."""
    levels = []
    level_pat = re.compile(
        r'#\s*Level\s+(\d+)\s*\n\s*Level\(\s*sprites=\[(.*?)\],\s*grid_size=\((\d+),\s*(\d+)\)',
        re.DOTALL)
    for m in level_pat.finditer(source):
        lv_num = int(m.group(1))
        sprites_block = m.group(2)
        gw, gh = int(m.group(3)), int(m.group(4))

        sprite_placements = []
        sp_pat = re.compile(
            r'sprites\["([\w-]+)"\]\.clone\(\)'
            r'(?:\.set_position\((-?\d+),\s*(-?\d+)\))?'
            r'(?:\.set_rotation\((\d+)\))?'
            r'(?:\.set_mirror_lr\((\w+)\))?'
            r'(?:\.color_remap\(None,\s*(\d+)\))?'
        )
        for sp in sp_pat.finditer(sprites_block):
            name = sp.group(1)
            x = int(sp.group(2)) if sp.group(2) else 0
            y = int(sp.group(3)) if sp.group(3) else 0
            rot = int(sp.group(4)) if sp.group(4) else 0
            mirror = sp.group(5) == "True" if sp.group(5) else False
            color_remap = int(sp.group(6)) if sp.group(6) else None
            sprite_placements.append({
                "name": name, "x": x, "y": y,
                "rotation": rot, "mirror": mirror,
                "color_remap": color_remap,
            })

        levels.append({
            "num": lv_num,
            "sprites": sprite_placements,
            "grid_size": (gw, gh),
        })

    levels.sort(key=lambda lv: lv["num"])
    return levels


def get_color_groups(level: dict) -> Dict[str, dict]:
    """Build color groups: body, limbs, target for each color."""
    groups = {}
    for sp in level["sprites"]:
        name = sp["name"]
        # Extract color suffix
        if name.startswith("bdkaz-"):
            color = name[6:]  # e.g., "kpaac", "yukft", etc.
            groups.setdefault(color, {"body": None, "limbs": [], "target": None, "stamps": []})
            groups[color]["body"] = sp
        elif name.startswith("bdkazLeg-"):
            color = name[9:]
            groups.setdefault(color, {"body": None, "limbs": [], "target": None, "stamps": []})
            groups[color]["limbs"].append(sp)
        elif name.startswith("kzeze-"):
            color = name[6:]
            groups.setdefault(color, {"body": None, "limbs": [], "target": None, "stamps": []})
            groups[color]["target"] = sp
        elif name.startswith("xigcb-"):
            groups.setdefault("stamps", {"body": None, "limbs": [], "target": None, "stamps": []})
            groups["stamps"]["stamps"].append(sp)

    return groups


def compute_centroid(limbs: List[dict], limb_size: int = 5) -> Tuple[int, int]:
    """Compute body centroid from limb positions."""
    if not limbs:
        return (0, 0)
    sum_x, sum_y = 0, 0
    for limb in limbs:
        cx = limb["x"] + limb_size // 2
        cy = limb["y"] + limb_size // 2
        sum_x += cx
        sum_y += cy
    avg_x = sum_x // len(limbs)
    avg_y = sum_y // len(limbs)
    body_size = 5
    return (avg_x - body_size // 2, avg_y - body_size // 2)


def solve_level(level: dict, sprite_pixels: Dict) -> dict:
    """
    Solve a level by computing limb movements.

    For simple levels (1-3): move limbs so body centroid lands on target.
    For stamp levels (5-6): need to absorb stamps first.

    Strategy: for each color group with a target, compute where the limbs
    need to be placed so the body centroid matches the target position.
    The simplest approach: move all limbs by the same delta as the body needs
    to move from its current position to the target.
    """
    lv_num = level["num"]
    groups = get_color_groups(level)

    actions = []
    limb_size = 5
    body_size = 5

    # Process each color group that has a target
    for color, group in groups.items():
        if color == "stamps" or "anqcf" in color:
            continue
        if group["target"] is None:
            continue

        target = group["target"]
        limbs = group["limbs"]
        body = group["body"]

        if not limbs:
            continue

        # Target position for the body
        target_x, target_y = target["x"], target["y"]

        # Current body position (centroid of limbs)
        current_bx, current_by = compute_centroid(limbs, limb_size)

        # Delta to move the body
        dx = target_x - current_bx
        dy = target_y - current_by

        # Move each limb by the same delta
        for i, limb in enumerate(limbs):
            new_x = limb["x"] + dx
            new_y = limb["y"] + dy

            # Select this limb (click on it)
            lx = limb["x"] + limb_size // 2
            ly = limb["y"] + limb_size // 2
            actions.append(f"click({lx},{ly})")

            # Click destination (center of where limb should go)
            dest_x = new_x + limb_size // 2
            dest_y = new_y + limb_size // 2
            actions.append(f"click({dest_x},{dest_y})")

            # Update limb position for subsequent centroid calculations
            limb["x"] = new_x
            limb["y"] = new_y

    # Verify
    verified = True
    for color, group in groups.items():
        if color == "stamps" or "anqcf" in color:
            continue
        if group["target"] is None:
            continue
        limbs = group["limbs"]
        if not limbs:
            continue
        target = group["target"]
        bx, by = compute_centroid(limbs, limb_size)
        if bx != target["x"] or by != target["y"]:
            verified = False

    return {
        "level": lv_num,
        "actions": actions,
        "verified": verified,
    }


def main():
    parser = argparse.ArgumentParser(description="r11l Solver")
    parser.add_argument("--source", type=str, default=GAME_SOURCE_DEFAULT)
    parser.add_argument("--level", type=int, default=None)
    args = parser.parse_args()

    source = parse_source(args.source)
    levels = extract_levels(source)
    sprite_pixels = extract_sprite_pixels(source)

    print(f"Parsed {len(levels)} levels\n")
    level_range = [lv for lv in levels if args.level is None or lv["num"] == args.level]
    all_pass = True

    for level in level_range:
        result = solve_level(level, sprite_pixels)

        print(f"Level {result['level']}: {len(result['actions'])} actions")
        if result["actions"]:
            print(f"  {' '.join(result['actions'])}")
        print(f"  {'VERIFIED OK' if result['verified'] else 'VERIFICATION FAILED'}")
        if not result["verified"]:
            all_pass = False
        print()

    if all_pass:
        print("All levels verified successfully.")
    else:
        print("WARNING: Some levels failed verification.")
        sys.exit(1)


if __name__ == "__main__":
    main()
