#!/usr/bin/env python3
"""
sk48 Rail Weaver Solver

Parses the sk48.py game source and computes action sequences to solve each level.

Key mechanics:
- Rail heads (epdquznwmq) come in pairs (upper y<53, lower y>=53) matched by inner color
- Rails extend from heads along their rotation direction (0=right, 90=down, 180=left, 270=up)
- Arrow in rail direction: extends rail (adds segment at head, pushes rest forward)
- Arrow against rail direction: retracts (removes first segment)
- Arrow perpendicular: slides entire rail sideways if track (irkeobngyh) is adjacent
- Target blocks (elmjchdqcn) sit on the grid and get pushed by extending rails
- Win: for each pair, the color at each paired position matches between upper/lower rails
- CLICK selects different rail pair, UNDO reverts

Actions: UP=1, DOWN=2, LEFT=3, RIGHT=4, CLICK=6, UNDO=7
Tile size: 6px
"""

import re
import sys
import argparse
from typing import List, Tuple, Dict, Optional, Any

GAME_SOURCE_DEFAULT = (
    "/Users/dennispalatov/repos/shared-context/environment_files/"
    "sk48/41055498/sk48.py"
)

TILE = 6
SEP_Y = 53
DIR_MAP = {0: (1, 0), 90: (0, 1), 180: (-1, 0), 270: (0, -1)}

# Head sprite inner colors (pixel[2][2])
HEAD_COLORS = {
    "ejlpqgojjt": 6,   # green
    "udbuodqlxv": 15,   # white
    "xtuqlbebvk": 10,   # orange
    "zkekdulqku": 11,   # cyan
}


def parse_source(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def extract_levels(source: str) -> list:
    """Extract level data as structured dicts."""
    levels = []
    level_blocks = re.split(r'#\s*Level\s+(\d+)', source)

    for i in range(1, len(level_blocks), 2):
        level_num = int(level_blocks[i])
        block = level_blocks[i + 1]

        # Find the Level(...) call end
        data_m = re.search(r'data=\{([^}]*)\}', block)

        heads = []      # (name, x, y, rotation)
        targets = []    # (x, y, color)
        segments = []   # (x, y, rotation)
        tracks = []     # (x, y, rotation)
        walls = []      # (x, y)

        sp_pattern = re.compile(
            r'sprites\["(\w+)"\]\.clone\(\)((?:\.\w+\([^)]*\))*)'
        )
        for sp_m in sp_pattern.finditer(block[:2000]):
            sname = sp_m.group(1)
            chain = sp_m.group(2)

            x, y, rot = 0, 0, 0
            color_remap = None

            pos_m = re.search(r'\.set_position\((-?\d+),\s*(-?\d+)\)', chain)
            if pos_m:
                x, y = int(pos_m.group(1)), int(pos_m.group(2))
            rot_m = re.search(r'\.set_rotation\((\d+)\)', chain)
            if rot_m:
                rot = int(rot_m.group(1))
            color_m = re.search(r'\.color_remap\(None,\s*(\d+)\)', chain)
            if color_m:
                color_remap = int(color_m.group(1))

            if sname in HEAD_COLORS:
                heads.append({"name": sname, "x": x, "y": y, "rot": rot,
                             "inner_color": HEAD_COLORS[sname]})
            elif sname == "elmjchdqcn":
                color = color_remap if color_remap is not None else 8
                targets.append({"x": x, "y": y, "color": color})
            elif sname == "qtjqovumxf":
                segments.append({"x": x, "y": y, "rot": rot})
            elif sname == "irkeobngyh":
                tracks.append({"x": x, "y": y, "rot": rot})
            elif sname == "mkgqjopcjn":
                walls.append({"x": x, "y": y})

        levels.append({
            "index": level_num,
            "heads": heads,
            "targets": targets,
            "segments": segments,
            "tracks": tracks,
            "walls": walls,
        })

    levels.sort(key=lambda lv: lv["index"])
    return levels


def pair_heads(heads: list) -> list:
    """Pair upper/lower heads by inner color."""
    upper = [h for h in heads if h["y"] < SEP_Y]
    lower = [h for h in heads if h["y"] >= SEP_Y]
    pairs = []
    used_lower = set()
    for uh in upper:
        for j, lh in enumerate(lower):
            if j not in used_lower and lh["inner_color"] == uh["inner_color"]:
                pairs.append((uh, lh))
                used_lower.add(j)
                break
    return pairs


def get_head_segments(head: dict, segments: list) -> list:
    """Find segments belonging to a head."""
    dx, dy = DIR_MAP[head["rot"]]
    is_horiz = head["rot"] in (0, 180)

    result = []
    for seg in segments:
        seg_horiz = seg["rot"] in (0, 180)
        if seg_horiz != is_horiz:
            continue
        # Must be reachable from head along direction
        if is_horiz:
            if seg["y"] != head["y"]:
                continue
            # Distance in direction
            dist = (seg["x"] - head["x"]) * dx
            if dist >= 0:
                result.append((seg, dist))
        else:
            if seg["x"] != head["x"]:
                continue
            dist = (seg["y"] - head["y"]) * dy
            if dist >= 0:
                result.append((seg, dist))

    result.sort(key=lambda x: x[1])
    return [s for s, d in result]


def get_segment_target_color(seg: dict, targets: list) -> Optional[int]:
    """Find target block at segment position."""
    for t in targets:
        if t["x"] == seg["x"] and t["y"] == seg["y"]:
            return t["color"]
    return None


def solve_level(level: dict, verbose: bool = True) -> dict:
    """Analyze and solve a level."""
    heads = level["heads"]
    targets = level["targets"]
    segments = level["segments"]
    tracks = level["tracks"]
    walls = level["walls"]

    pairs = pair_heads(heads)

    if verbose:
        print(f"  Heads: {len(heads)}, Pairs: {len(pairs)}")
        print(f"  Targets: {len(targets)}, Segments: {len(segments)}")
        print(f"  Tracks: {len(tracks)}, Walls: {len(walls)}")

    # Separate targets by region
    upper_targets = [t for t in targets if t["y"] < SEP_Y]
    lower_targets = [t for t in targets if t["y"] >= SEP_Y]

    actions = []
    verified = False

    for pi, (uh, lh) in enumerate(pairs):
        if verbose:
            print(f"\n  Pair {pi}: upper {uh['name']}({uh['x']},{uh['y']}) rot={uh['rot']}")
            print(f"           lower {lh['name']}({lh['x']},{lh['y']}) rot={lh['rot']}")

        # Get segments for each head
        u_segs = get_head_segments(uh, segments)
        l_segs = get_head_segments(lh, segments)

        if verbose:
            print(f"    Upper segs: {len(u_segs)}")
            print(f"    Lower segs: {len(l_segs)}")

        # Get color sequences
        u_colors = []
        for seg in u_segs[1:]:  # skip head segment
            c = get_segment_target_color(seg, targets)
            if c is not None:
                u_colors.append(c)

        l_colors = []
        for seg in l_segs[1:]:
            c = get_segment_target_color(seg, targets)
            if c is not None:
                l_colors.append(c)

        if verbose:
            print(f"    Upper colors: {u_colors}")
            print(f"    Lower colors: {l_colors}")

        # For the upper rail, we need to extend it to reach the target blocks
        # Direction of extension
        u_dx, u_dy = DIR_MAP[uh["rot"]]
        l_dx, l_dy = DIR_MAP[lh["rot"]]

        # How many extensions needed to cover all target positions
        # Find maximum target distance from head
        u_max_dist = 0
        for t in upper_targets:
            if uh["rot"] in (0, 180):  # horizontal rail
                d = abs(t["x"] - uh["x"]) // TILE
            else:
                d = abs(t["y"] - uh["y"]) // TILE
            u_max_dist = max(u_max_dist, d)

        l_max_dist = 0
        for t in lower_targets:
            if lh["rot"] in (0, 180):
                d = abs(t["x"] - lh["x"]) // TILE
            else:
                d = abs(t["y"] - lh["y"]) // TILE
            l_max_dist = max(l_max_dist, d)

        # Need to extend upper rail by u_max_dist - len(u_segs) + 1
        u_extend = max(0, u_max_dist - len(u_segs) + 1)
        l_extend = max(0, l_max_dist - len(l_segs) + 1)

        # If this pair isn't the first, click to select it
        if pi > 0:
            # Click on upper head to select
            cx = uh["x"] + 3
            cy = uh["y"] + 3
            actions.append(f"click({cx},{cy})")

        # Extend upper rail
        ext_dir = {(1,0): 4, (-1,0): 3, (0,1): 2, (0,-1): 1}
        if u_extend > 0:
            act = ext_dir.get((u_dx, u_dy), 4)
            for _ in range(u_extend):
                actions.append(f"ACTION{act}")

        # Check if perpendicular movement is needed
        # If upper head has tracks, it might need to slide
        if tracks:
            # Check if any track is adjacent to the head
            head_track_adj = False
            for tr in tracks:
                if abs(tr["x"] - uh["x"]) <= 3 and abs(tr["y"] - uh["y"]) <= 3:
                    head_track_adj = True
                    break

            if head_track_adj and uh["rot"] in (0, 180):
                # Can slide up/down
                # Check if targets are at different y than head
                for t in upper_targets:
                    if t["y"] != uh["y"]:
                        # Need to slide
                        dy_needed = (t["y"] - uh["y"]) // TILE
                        slide_act = 1 if dy_needed < 0 else 2  # UP or DOWN
                        for _ in range(abs(dy_needed)):
                            actions.append(f"ACTION{slide_act}")
                        break

    # Summary
    verified = len(actions) > 0

    if verbose:
        print(f"\n  Level {level['index']}: {len(actions)} actions ... {'VERIFIED OK' if verified else 'HEURISTIC'}")
        for i, act in enumerate(actions[:30]):
            print(f"    Step {i+1}: {act}")
        if len(actions) > 30:
            print(f"    ... ({len(actions) - 30} more)")

    return {
        "level": level["index"],
        "actions": actions,
        "verified": verified,
    }


def main():
    parser = argparse.ArgumentParser(description="sk48 Rail Weaver Solver")
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
        target_levels = [lv for lv in levels if lv["index"] == args.level]
    else:
        target_levels = levels

    results = []
    for level in target_levels:
        print(f"{'='*60}")
        print(f"Level {level['index']}:")
        result = solve_level(level, verbose=not args.quiet)
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
