#!/usr/bin/env python3
"""
vc33 Seesaw-Balance Puzzle Solver

Parses vc33.py and computes click sequences to solve each level.

Key mechanics:
- Beams (rDn): rectangular blocks that can grow/shrink
- Pivots (UXg): vertical bars between beam segments
- ZGd triggers: click to transfer length between adjacent beams
- zHk triggers: click to rotate/swap HQB indicators between beam ends
- HQB: target indicators that must be matched
- fZK: colored indicators on pivots that must match HQB
- Win: every HQB has a matching-color fZK on the correct adjacent pivot

Direction tuple TiD controls orientation: [2,0]=right, [-2,0]=left, etc.
Grid sizes vary: 32x32, 52x52, 64x64, 48x48.

Camera: default 64x64.

Usage:
    python vc33_solver.py [--source PATH]
"""

import re
import ast
import sys
import argparse
import numpy as np
from typing import Dict, List, Tuple, Optional


GAME_SOURCE_DEFAULT = (
    "/Users/dennispalatov/repos/shared-context/environment_files/"
    "vc33/9851e02b/vc33.py"
)


def parse_source(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def extract_sprite_info(source: str) -> Dict[str, dict]:
    """Extract sprite definitions."""
    sprites = {}
    sprites_start = source.find('sprites = {')
    levels_start = source.find('\nlevels')
    if sprites_start < 0 or levels_start < 0:
        return sprites
    section = source[sprites_start:levels_start]

    pat = re.compile(
        r'"(\w+)":\s*Sprite\(\s*pixels=(\[(?:\s*\[[^\]]*\],?\s*)*\]),',
        re.DOTALL)
    tag_pat = re.compile(r'tags=\[([^\]]*)\]')
    layer_pat = re.compile(r'layer=(\d+)')

    for m in pat.finditer(section):
        name = m.group(1)
        pixels = ast.literal_eval(m.group(2))
        block_end = section.find('\n    "', m.end())
        if block_end == -1:
            block_end = len(section)
        rest = section[m.end():block_end]

        tags = []
        tags_match = tag_pat.search(rest)
        if tags_match:
            tags = [t.strip().strip('"').strip("'") for t in tags_match.group(1).split(",") if t.strip()]

        layer = 0
        layer_match = layer_pat.search(rest)
        if layer_match:
            layer = int(layer_match.group(1))

        h = len(pixels)
        w = len(pixels[0]) if pixels else 0
        sprites[name] = {"pixels": pixels, "tags": tags, "layer": layer, "width": w, "height": h}

    return sprites


def extract_levels(source: str) -> List[dict]:
    """Extract level data."""
    levels = []
    level_pat = re.compile(
        r'#\s*Level\s+(\d+)\s*\n\s*Level\(\s*sprites=\[(.*?)\],\s*'
        r'grid_size=\((\d+),\s*(\d+)\),\s*'
        r'data=\{(.*?)\},\s*'
        r'name="([^"]+)"',
        re.DOTALL)

    for m in level_pat.finditer(source):
        lv_num = int(m.group(1))
        sprites_block = m.group(2)
        gw, gh = int(m.group(3)), int(m.group(4))
        data_block = m.group(5)
        name = m.group(6)

        sprite_placements = []
        sp_pat = re.compile(
            r'sprites\["(\w+)"\]\.clone\(\)'
            r'(?:\.set_position\((-?\d+),\s*(-?\d+)\))?'
            r'(?:\.set_rotation\((\d+)\))?')
        for sp in sp_pat.finditer(sprites_block):
            sname = sp.group(1)
            x = int(sp.group(2)) if sp.group(2) else 0
            y = int(sp.group(3)) if sp.group(3) else 0
            rot = int(sp.group(4)) if sp.group(4) else 0
            sprite_placements.append({"name": sname, "x": x, "y": y, "rotation": rot})

        # Parse data
        roa_m = re.search(r'"RoA":\s*(\d+)', data_block)
        roa = int(roa_m.group(1)) if roa_m else 50
        tid_m = re.search(r'"TiD":\s*\[(-?\d+),\s*(-?\d+)\]', data_block)
        tid = (int(tid_m.group(1)), int(tid_m.group(2))) if tid_m else (2, 0)

        levels.append({
            "num": lv_num,
            "name": name,
            "sprites": sprite_placements,
            "grid_size": (gw, gh),
            "roa": roa,
            "tid": tid,
        })

    levels.sort(key=lambda lv: lv["num"])
    return levels


def solve_level(level: dict, sprite_info: Dict) -> dict:
    """
    Solve a level by analyzing beam/pivot/indicator configurations.

    The seesaw game requires transferring beam length and rotating indicators
    to match HQB targets with fZK markers on correct pivots.

    This requires deep simulation of the beam mechanics. For now, we analyze
    the initial configuration and determine the needed operations.
    """
    lv_num = level["num"]
    tid = level["tid"]

    # Identify sprites by tag
    beams = []
    pivots = []
    zgd_triggers = []
    zhk_triggers = []
    hqb_targets = []
    fzk_markers = []

    for sp in level["sprites"]:
        info = sprite_info.get(sp["name"], {})
        tags = info.get("tags", [])
        sp["tags"] = tags
        sp["width"] = info.get("width", 0)
        sp["height"] = info.get("height", 0)
        sp["pixels"] = info.get("pixels", [])

        if "rDn" in tags: beams.append(sp)
        elif "UXg" in tags: pivots.append(sp)
        elif "ZGd" in tags: zgd_triggers.append(sp)
        elif "zHk" in tags: zhk_triggers.append(sp)
        elif "HQB" in tags: hqb_targets.append(sp)
        elif "fZK" in tags: fzk_markers.append(sp)

    # Determine the axis helpers based on TiD
    horizontal = tid[0] != 0

    # For the win condition: each HQB must have a matching fZK on correct pivot
    # This requires understanding which beam each HQB sits on and which pivots
    # are adjacent to that beam.

    # The game mechanics are complex - full simulation would be needed.
    # For verification purposes, we check if the initial state already wins.

    # Check win condition
    won = check_win(beams, pivots, hqb_targets, fzk_markers, tid, sprite_info)

    actions = []
    verified = won

    if not won:
        # Need to compute operations
        # For simple levels, try clicking ZGd triggers to transfer beam length
        # and zHk triggers to swap indicators

        # Grid coordinate mapping
        gw, gh = level["grid_size"]
        offset_x = (64 - gw) // 2
        offset_y = (64 - gh) // 2

        # For each ZGd trigger, compute its display coordinates
        for trigger in zgd_triggers:
            dx = trigger["x"] + offset_x + 1
            dy = trigger["y"] + offset_y + 1

        # Without full simulation, we can't determine the optimal click sequence.
        # Mark as needing manual solution.
        verified = False

    return {
        "level": lv_num,
        "actions": actions,
        "verified": verified,
    }


def check_win(beams, pivots, hqb_targets, fzk_markers, tid, sprite_info) -> bool:
    """Check win condition: every HQB has matching fZK on correct adjacent pivot."""
    horizontal = tid[0] != 0

    for hqb in hqb_targets:
        # Get HQB color from pixels[-1][-1]
        pixels = hqb.get("pixels", [])
        if not pixels:
            return False
        hqb_color = pixels[-1][-1]

        # Find which beam the HQB sits on
        matched = False
        for fzk in fzk_markers:
            fzk_pixels = fzk.get("pixels", [])
            if not fzk_pixels:
                continue
            # Check if fZK has the matching color
            fzk_has_color = any(hqb_color in row for row in fzk_pixels)
            if not fzk_has_color:
                continue

            # Check positional relationship (simplified)
            if horizontal:
                if hqb["y"] == fzk["y"]:
                    matched = True
                    break
            else:
                if hqb["x"] == fzk["x"]:
                    matched = True
                    break

        if not matched:
            return False

    return True


def main():
    parser = argparse.ArgumentParser(description="vc33 Solver")
    parser.add_argument("--source", type=str, default=GAME_SOURCE_DEFAULT)
    parser.add_argument("--level", type=int, default=None)
    args = parser.parse_args()

    source = parse_source(args.source)
    sprite_info = extract_sprite_info(source)
    levels = extract_levels(source)

    print(f"Parsed {len(sprite_info)} sprites, {len(levels)} levels\n")
    level_range = [lv for lv in levels if args.level is None or lv["num"] == args.level]
    all_pass = True

    for level in level_range:
        result = solve_level(level, sprite_info)

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
