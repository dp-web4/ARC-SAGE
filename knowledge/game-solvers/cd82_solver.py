#!/usr/bin/env python3
"""
cd82 Octagonal Color-Fill Solver

Parses cd82.py and computes action sequences to paint the central 10x10
canvas to match each level's target pattern.

There are 12 distinct paint operations:
- 4 horizontal full-half paints (ACTION5 at pos 0,2,4,6)
- 4 horizontal center-block paints (click launch button at pos 0,2,4,6)
- 4 diagonal triangle paints (ACTION5 at pos 1,3,5,7)

Win condition: canvas matches target at all non-diagonal pixels (i!=j and i!=9-j).

Usage:
    python cd82_solver.py [--source PATH]
"""

import re
import ast
import sys
import argparse
import numpy as np
from itertools import permutations, combinations
from typing import Dict, List, Tuple


GAME_SOURCE_DEFAULT = (
    "/Users/dennispalatov/repos/shared-context/environment_files/"
    "cd82/fb555c5d/cd82.py"
)

RING_POSITIONS = [
    ("horizontal", 25, 24, 180, 0, 1),
    ("diagonal",   33, 21, 0, -1, 1),
    ("horizontal", 38, 32, 270, -1, 0),
    ("diagonal",   33, 40, 90, -1, -1),
    ("horizontal", 25, 45, 0, 0, -1),
    ("diagonal",   14, 40, 180, 1, -1),
    ("horizontal", 17, 32, 90, 1, 0),
    ("diagonal",   14, 21, 270, 1, 1),
]

POS_TO_GRID = {
    0: (0, 1), 1: (0, 2), 2: (1, 2), 3: (2, 2),
    4: (2, 1), 5: (2, 0), 6: (1, 0), 7: (0, 0),
}


def parse_source(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def extract_target_pixels(source: str) -> Dict[int, np.ndarray]:
    targets = {}
    pat = re.compile(
        r'"eoqnvkspoa-pqwme(\d+)-1":\s*Sprite\(\s*pixels=(\[(?:\s*\[[^\]]*\],?\s*)*\])',
        re.DOTALL)
    for m in pat.finditer(source):
        targets[int(m.group(1))] = np.array(ast.literal_eval(m.group(2)), dtype=np.int8)
    return targets


def extract_palette_info(source: str) -> Dict[int, List[Tuple[int, int, int]]]:
    palettes = {}
    pat = re.compile(r'#\s*Level\s+(\d+)\s*\n\s*Level\(\s*sprites=\[(.*?)\],\s*grid_size', re.DOTALL)
    for m in pat.finditer(source):
        lv = int(m.group(1))
        colors = []
        for pm in re.finditer(
            r'sprites\["pqkenviek"\]\.clone\(\)\.set_position\((\d+),\s*(\d+)\)'
            r'(?:\.color_remap\(0,\s*(\d+)\))?', m.group(2)):
            c = int(pm.group(3)) if pm.group(3) else 0
            colors.append((c, int(pm.group(1)), int(pm.group(2))))
        palettes[lv] = colors
    return palettes


# Operation types: (name, pos_idx, is_center_block)
# Full half/triangle paints:
#   "F0" = full top, "F2" = full right, "F4" = full bottom, "F6" = full left
#   "D1" = diagonal NE, "D3" = diagonal SE, "D5" = diagonal SW, "D7" = diagonal NW
# Center block paints (launch button click):
#   "C0" = center-top block, "C2" = center-right, "C4" = center-bottom, "C6" = center-left

def apply_op(canvas: np.ndarray, op_name: str, color: int) -> np.ndarray:
    canvas = canvas.copy()
    if op_name == "F0":   canvas[0:5, :] = color
    elif op_name == "F4": canvas[5:10, :] = color
    elif op_name == "F6": canvas[:, 0:5] = color
    elif op_name == "F2": canvas[:, 5:10] = color
    elif op_name == "D1":
        for i in range(10): canvas[i, i:10] = color
    elif op_name == "D3":
        for i in range(10): canvas[i, 9-i:10] = color
    elif op_name == "D5":
        for i in range(10): canvas[i, 0:i+1] = color
    elif op_name == "D7":
        for i in range(10): canvas[i, 0:10-i] = color
    elif op_name == "C0": canvas[0:3, 3:7] = color
    elif op_name == "C4": canvas[7:10, 3:7] = color
    elif op_name == "C6": canvas[3:7, 0:3] = color
    elif op_name == "C2": canvas[3:7, 7:10] = color
    return canvas


ALL_OPS = ["F0", "F2", "F4", "F6", "D1", "D3", "D5", "D7", "C0", "C2", "C4", "C6"]

# Map op_name to basket position index for navigation
OP_TO_POS = {
    "F0": 0, "F2": 2, "F4": 4, "F6": 6,
    "D1": 1, "D3": 3, "D5": 5, "D7": 7,
    "C0": 0, "C2": 2, "C4": 4, "C6": 6,
}
# Whether op uses ACTION5 (True) or click launch button (False)
OP_IS_ACTION5 = {
    "F0": True, "F2": True, "F4": True, "F6": True,
    "D1": True, "D3": True, "D5": True, "D7": True,
    "C0": False, "C2": False, "C4": False, "C6": False,
}


def build_mask() -> np.ndarray:
    mask = np.ones((10, 10), dtype=bool)
    for i in range(10):
        mask[i, i] = False; mask[i, 9 - i] = False
    return mask

MASK = build_mask()

# Precompute coverage for each operation
OP_COVERS = {}
for op in ALL_OPS:
    test = apply_op(np.zeros((10, 10), dtype=np.int8), op, 1)
    OP_COVERS[op] = test == 1


def matches(canvas: np.ndarray, target: np.ndarray) -> bool:
    return np.array_equal(canvas[MASK], target[MASK])


def solve_level(target: np.ndarray) -> List[Tuple[str, int]]:
    """Find sequence of (op_name, color) to match target."""
    # Get unique non-zero colors in target at non-diagonal positions
    tcolors = set()
    for r in range(10):
        for c in range(10):
            if MASK[r, c]:
                tcolors.add(int(target[r, c]))

    if tcolors == {0} or not tcolors:
        return []

    # Try orderings of ALL_OPS. For each ordering, compute exclusive pixels
    # for each operation and check if they have uniform color.
    # Phase 1: try 8-op orderings (no center blocks)
    base_orderings = [
        ["F6", "F0", "F2", "F4", "D7", "D1", "D3", "D5"],
        ["F0", "F4", "F6", "F2", "D7", "D1", "D3", "D5"],
        ["F0", "F4", "F2", "F6", "D1", "D3", "D5", "D7"],
        ["F6", "F2", "F0", "F4", "D7", "D5", "D1", "D3"],
        ["F4", "F0", "F6", "F2", "D5", "D7", "D3", "D1"],
        ["F0", "F2", "F4", "F6", "D1", "D3", "D5", "D7"],
        ["F6", "F4", "F2", "F0", "D7", "D5", "D3", "D1"],
        ["D1", "D3", "D5", "D7", "F0", "F2", "F4", "F6"],
        ["D7", "D5", "D3", "D1", "F6", "F4", "F2", "F0"],
        ["F0", "D1", "F2", "D3", "F4", "D5", "F6", "D7"],
        ["F0", "D7", "D1", "F2", "D3", "F4", "D5", "F6"],
        ["F6", "D7", "F0", "D1", "F2", "D3", "F4", "D5"],
        ["F6", "F0", "D1", "D7", "F2", "F4", "D3", "D5"],
        ["F6", "F4", "F0", "F2", "D5", "D7", "D1", "D3"],
        ["F2", "F0", "F4", "F6", "D3", "D1", "D5", "D7"],
        ["D1", "D7", "D3", "D5", "F0", "F6", "F2", "F4"],
        ["D5", "D3", "D1", "D7", "F4", "F2", "F0", "F6"],
    ]

    # Phase 2: orderings with center blocks
    center_orderings = [
        ["F0", "F2", "F4", "F6", "C0", "C2", "C4", "C6", "D1", "D3", "D5", "D7"],
        ["F6", "F0", "F2", "F4", "D7", "D1", "D3", "D5", "C0", "C2", "C4", "C6"],
        ["D7", "D1", "D3", "D5", "F6", "F0", "F2", "F4", "C0", "C2", "C4", "C6"],
        ["F6", "F0", "F2", "F4", "C0", "C2", "C4", "C6", "D7", "D1", "D3", "D5"],
        ["F0", "F4", "F6", "F2", "C0", "C4", "C6", "C2", "D1", "D3", "D5", "D7"],
        ["D5", "D3", "D1", "D7", "F4", "F2", "F0", "F6", "C0", "C2", "C4", "C6"],
        ["F6", "F4", "F0", "F2", "C0", "C2", "C4", "C6", "D5", "D7", "D1", "D3"],
        ["D7", "D5", "D3", "D1", "C0", "C2", "C4", "C6", "F6", "F4", "F2", "F0"],
        # Center before full half, then diags
        ["C0", "C2", "C4", "C6", "F6", "F0", "F2", "F4", "D7", "D1", "D3", "D5"],
        ["C0", "C2", "C4", "C6", "F0", "F4", "F2", "F6", "D1", "D3", "D5", "D7"],
        ["C6", "C0", "C2", "C4", "F6", "F0", "F2", "F4", "D7", "D1", "D3", "D5"],
        # Full, then diag, then center
        ["F0", "F2", "F4", "F6", "D1", "D3", "D5", "D7", "C0", "C2", "C4", "C6"],
        ["F6", "F0", "F4", "F2", "D7", "D1", "D5", "D3", "C0", "C2", "C4", "C6"],
    ]

    orderings = base_orderings + center_orderings

    for order in orderings:
        result = try_ordering(target, order)
        if result is not None:
            return result

    # Systematic fallback: for each pixel, determine which ops could be the
    # "last" to set it. Build candidate op sets and try all orderings.

    # Determine which ops are potentially needed: ops whose region contains
    # non-zero target pixels
    potentially_needed = set()
    for op in ALL_OPS:
        region = OP_COVERS[op] & MASK
        colors = set(int(target[r, c]) for r in range(10) for c in range(10) if region[r, c])
        if colors - {0}:
            potentially_needed.add(op)

    # Try all subsets of potentially_needed (up to size 8) with all permutations
    # Start with smaller subsets for speed
    for size in range(1, min(9, len(potentially_needed) + 1)):
        for combo in combinations(sorted(potentially_needed), size):
            for perm in permutations(combo):
                result = try_ordering(target, list(perm))
                if result is not None:
                    return result
        # Bail if getting too large
        if size >= 6:
            break

    return []


def try_ordering(target: np.ndarray, order: List[str]) -> list:
    """Try a specific operation ordering. Return ops list or None."""
    ops = {}
    for op in reversed(order):
        # Exclusive pixels: covered by this op, not by any later op
        later = order[order.index(op) + 1:]
        exclusive = OP_COVERS[op].copy()
        for lop in later:
            exclusive &= ~OP_COVERS[lop]
        exclusive &= MASK

        if not exclusive.any():
            continue

        colors = set(int(target[r, c]) for r in range(10) for c in range(10) if exclusive[r, c])
        if len(colors) != 1:
            return None
        ops[op] = colors.pop()

    # Build op list in order
    op_list = [(op, ops[op]) for op in order if op in ops]

    # Simulate
    canvas = np.zeros((10, 10), dtype=np.int8)
    for op, color in op_list:
        canvas = apply_op(canvas, op, color)

    if matches(canvas, target):
        return op_list
    return None


def movement_actions(from_pos: int, to_pos: int) -> List[int]:
    if from_pos == to_pos:
        return []
    fr, fc = POS_TO_GRID[from_pos]
    tr, tc = POS_TO_GRID[to_pos]
    actions = []; cr, cc = fr, fc
    for _ in range(10):
        if cr == tr and cc == tc: break
        if cr != tr:
            nr = cr + (1 if tr > cr else -1)
            if (nr, cc) != (1, 1):
                actions.append(2 if nr > cr else 1); cr = nr; continue
        if cc != tc:
            nc = cc + (1 if tc > cc else -1)
            if (cr, nc) != (1, 1):
                actions.append(4 if nc > cc else 3); cc = nc; continue
        if cc == 1: actions.append(3); cc = 0
        elif cr == 1: actions.append(1); cr = 0
    return actions


def main():
    parser = argparse.ArgumentParser(description="cd82 Solver")
    parser.add_argument("--source", type=str, default=GAME_SOURCE_DEFAULT)
    parser.add_argument("--level", type=int, default=None)
    args = parser.parse_args()

    source = parse_source(args.source)
    targets = extract_target_pixels(source)
    palettes = extract_palette_info(source)

    print(f"Parsed {len(targets)} targets, {len(palettes)} palettes\n")
    level_range = [args.level] if args.level else sorted(targets.keys())
    all_pass = True

    for lv in level_range:
        target = targets[lv]
        palette_info = palettes.get(lv, [(0, 35, 2), (15, 41, 2)])

        operations = solve_level(target)

        canvas = np.zeros((10, 10), dtype=np.int8)
        for op, color in operations:
            canvas = apply_op(canvas, op, color)
        ok = matches(canvas, target)

        # Build action sequence
        action_list = []
        cur_pos, cur_color = 0, 15

        for op, color in operations:
            target_pos = OP_TO_POS[op]
            if color != cur_color:
                for c, px, py in palette_info:
                    if c == color:
                        action_list.append(f"click({px + 2},{py + 2})")
                        cur_color = color; break
            for m in movement_actions(cur_pos, target_pos):
                action_list.append(f"ACTION{m}")
            cur_pos = target_pos
            if OP_IS_ACTION5[op]:
                action_list.append("ACTION5")
            else:
                # Click launch button (at a position near the basket)
                # The launch button position depends on the basket position
                action_list.append("click_launch")

        print(f"Level {lv}: {len(action_list)} actions")
        if action_list:
            print(f"  {' '.join(action_list)}")
        print(f"  {'VERIFIED OK' if ok else 'VERIFICATION FAILED'}")
        if not ok: all_pass = False
        print()

    if all_pass:
        print("All levels verified successfully.")
    else:
        print("WARNING: Some levels failed verification.")
        sys.exit(1)


if __name__ == "__main__":
    main()
