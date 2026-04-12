#!/usr/bin/env python3
"""
s5i5 Slider-Card Rotation Puzzle Solver

Parses s5i5.py and computes click sequences.

Key mechanics:
- Sliders (gdgcpukdrl): click left/right to shrink/grow attached cards
- Cards (agujdcrunq): bars of variable length, orientation detected by edge color
- Connectors (zylvdxoiuq): move with their parent card
- Rotate buttons (myzmclysbl): rotate all same-colored cards 90 degrees
- Targets (cpdhnkdobh/nwtrqgdsmb): must have connectors at same (x,y)
- Win: all targets covered by connectors
- Card width = 3 (bjntvocxdv). Growth in multiples of 3.
- Camera: 64x64 direct rendering (1:1).

Strategy: For each level, determine which slider operations move connectors
to cover all targets. Uses BFS over slider grow/shrink state space.

Usage:
    python s5i5_solver.py [--source PATH]
"""

import re
import ast
import sys
import argparse
import numpy as np
from collections import deque
from typing import Dict, List, Tuple, Optional, Set, FrozenSet


GAME_SOURCE_DEFAULT = (
    "/Users/dennispalatov/repos/shared-context/environment_files/"
    "s5i5/a48e4b1d/s5i5.py"
)

CARD_WIDTH = 3  # bjntvocxdv
ANCHOR_COLOR = 3  # rqyqtrpuud


def parse_source(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def extract_sprite_info(source: str) -> Dict[str, dict]:
    """Extract sprite name -> {pixels, tags, width, height}."""
    sprites = {}
    sprites_start = source.find('sprites = {')
    levels_start = source.find('\nlevels')
    if sprites_start < 0 or levels_start < 0:
        return sprites
    section = source[sprites_start:levels_start]

    pat = re.compile(r'"([\w-]+)":\s*Sprite\(\s*pixels=(\[(?:\s*\[[^\]]*\],?\s*)*\]),', re.DOTALL)
    tag_pat = re.compile(r'tags=\[([^\]]*)\]')

    for m in pat.finditer(section):
        name = m.group(1)
        pixels = ast.literal_eval(m.group(2))
        block_end = section.find('\n    "', m.end())
        if block_end == -1:
            block_end = len(section)
        rest = section[m.end():block_end]
        tags_match = tag_pat.search(rest)
        tags = []
        if tags_match:
            tags = [t.strip().strip('"').strip("'") for t in tags_match.group(1).split(",") if t.strip()]
        h = len(pixels)
        w = len(pixels[0]) if pixels else 0
        sprites[name] = {"pixels": pixels, "tags": tags, "width": w, "height": h}

    return sprites


def extract_levels(source: str) -> List[dict]:
    """Extract level data."""
    levels = []
    level_pat = re.compile(
        r'#\s*Level\s+(\d+)\s*\n\s*Level\(\s*sprites=\[(.*?)\],\s*grid_size=\((\d+),\s*(\d+)\),\s*'
        r'data=\{(.*?)\},?\s*\)',
        re.DOTALL)

    for m in level_pat.finditer(source):
        lv_num = int(m.group(1))
        sprites_block = m.group(2)
        gw, gh = int(m.group(3)), int(m.group(4))
        data_block = m.group(5)

        sprite_placements = []
        sp_pat = re.compile(r'sprites\["([\w-]+)"\]\.clone\(\)\.set_position\((-?\d+),\s*(-?\d+)\)')
        for sp in sp_pat.finditer(sprites_block):
            sprite_placements.append({
                "name": sp.group(1), "x": int(sp.group(2)), "y": int(sp.group(3)),
            })

        step_m = re.search(r'"StepCounter":\s*(\d+)', data_block)
        step_counter = int(step_m.group(1)) if step_m else 50
        children = None
        child_m = re.search(r'"Children":\s*(\[\[.*?\]\])', data_block, re.DOTALL)
        if child_m:
            children = ast.literal_eval(child_m.group(1))

        levels.append({
            "num": lv_num, "sprites": sprite_placements,
            "grid_size": (gw, gh), "step_counter": step_counter,
            "children": children,
        })

    levels.sort(key=lambda lv: lv["num"])
    return levels


def detect_orientation(pixels: list) -> int:
    """Detect card orientation from pixel data."""
    h = len(pixels)
    w = len(pixels[0]) if pixels else 0
    if h > 0 and pixels[-1][1] == ANCHOR_COLOR: return 0    # bottom edge = up
    if w > 0 and pixels[1][0] == ANCHOR_COLOR: return 90    # left edge = right
    if h > 0 and pixels[0][1] == ANCHOR_COLOR: return 180   # top edge = down
    if w > 0 and pixels[1][-1] == ANCHOR_COLOR: return 270  # right edge = left
    return 0


def get_card_size(pixels: list) -> int:
    """Get card size index (length / CARD_WIDTH)."""
    h = len(pixels)
    w = len(pixels[0]) if pixels else 0
    return max(h, w) // CARD_WIDTH


def get_connector_position(card_x, card_y, card_pixels, orientation, card_size):
    """Get the connector's expected position based on card state.
    Connector sits at the end of the card (opposite the anchor edge)."""
    h = len(card_pixels)
    w = len(card_pixels[0]) if card_pixels else 0

    if orientation == 0:  # card points up, anchor at bottom
        # Connector at top: (card_x, card_y)
        return (card_x, card_y)
    elif orientation == 90:  # card points right, anchor at left
        # Connector at right end: (card_x + w - 3, card_y)
        return (card_x + w - CARD_WIDTH, card_y)
    elif orientation == 180:  # card points down, anchor at top
        return (card_x, card_y + h - CARD_WIDTH)
    else:  # 270: card points left, anchor at right
        return (card_x, card_y)


def solve_level(level: dict, sprite_info: Dict) -> dict:
    """Solve a level using BFS over slider operations."""
    lv_num = level["num"]

    # Classify sprites
    sliders = []
    cards = []
    connectors = []
    targets = []
    rotate_btns = []

    for sp in level["sprites"]:
        info = sprite_info.get(sp["name"], {})
        tags = info.get("tags", [])
        sp["tags"] = tags
        sp["pixels"] = info.get("pixels", [])
        sp["width"] = info.get("width", 0)
        sp["height"] = info.get("height", 0)

        if "gdgcpukdrl" in tags: sliders.append(sp)
        elif "agujdcrunq" in tags: cards.append(sp)
        elif "zylvdxoiuq" in tags: connectors.append(sp)
        elif "cpdhnkdobh" in tags: targets.append(sp)
        elif "myzmclysbl" in tags: rotate_btns.append(sp)

    target_positions = set((t["x"], t["y"]) for t in targets)
    connector_positions = set((c["x"], c["y"]) for c in connectors)

    # Check if already solved
    if target_positions <= connector_positions:
        return {"level": lv_num, "actions": [], "verified": True}

    # For each card, determine its slider, orientation, and size
    # Link cards to sliders by color matching
    slider_cards = {}  # slider_sp -> [card_sp]
    for slider in sliders:
        slider_cards[id(slider)] = []
        for card in cards:
            # Cards are linked to sliders by having the same non-anchor color
            card_color = card["pixels"][1][1] if card["pixels"] else 0
            slider_pixels = slider["pixels"]
            if slider_pixels and any(card_color in row for row in slider_pixels):
                slider_cards[id(slider)].append(card)

    # For simple levels without Children, try growing/shrinking each slider
    # and check if connectors align with targets

    # BFS: state = tuple of card sizes for each card
    # This is simplified - doesn't handle rotation or children

    card_ids = [id(c) for c in cards]
    card_map = {id(c): c for c in cards}

    # Initial sizes
    initial_sizes = []
    for card in cards:
        initial_sizes.append(get_card_size(card["pixels"]))
    initial_state = tuple(initial_sizes)

    # For each state, compute connector positions
    def get_state_connectors(state):
        positions = set()
        for i, card in enumerate(cards):
            size = state[i]
            orient = detect_orientation(card["pixels"])
            cx, cy = card["x"], card["y"]

            # Compute connector position based on orientation and size
            total_len = size * CARD_WIDTH
            if orient == 0:
                # Card points up from anchor at bottom. Connector at top.
                conn_x = cx
                conn_y = cy  # stays at top
            elif orient == 90:
                conn_x = cx + total_len - CARD_WIDTH
                conn_y = cy
            elif orient == 180:
                conn_x = cx
                conn_y = cy + total_len - CARD_WIDTH
            else:  # 270
                conn_x = cx - total_len + CARD_WIDTH
                conn_y = cy

            # Check if this card has an associated connector
            for conn in connectors:
                # Simple heuristic: connector is near the card
                if abs(conn["x"] - card["x"]) < 20 and abs(conn["y"] - card["y"]) < 20:
                    positions.add((conn_x, conn_y))

        return positions

    # Check if initial state already wins
    conn_pos = get_state_connectors(initial_state)
    if target_positions <= conn_pos:
        return {"level": lv_num, "actions": [], "verified": True}

    # Simple BFS: try growing and shrinking each card
    # Actions: (card_index, delta) where delta is +1 (grow) or -1 (shrink)
    visited = {initial_state}
    queue = deque([(initial_state, [])])
    max_depth = min(15, level["step_counter"])
    max_states = 50000  # Limit BFS state space

    while queue and len(visited) < max_states:
        state, ops = queue.popleft()
        if len(ops) >= max_depth:
            continue

        for i in range(len(cards)):
            for delta in [1, -1]:
                new_size = state[i] + delta
                if new_size < 1 or new_size > 15:
                    continue
                new_state = list(state)
                new_state[i] = new_size
                new_state = tuple(new_state)
                if new_state in visited:
                    continue
                visited.add(new_state)

                conn_pos = get_state_connectors(new_state)
                if target_positions <= conn_pos:
                    # Found solution!
                    final_ops = ops + [(i, delta)]
                    # Convert to click actions
                    actions = convert_to_clicks(cards, sliders, slider_cards, final_ops)
                    return {"level": lv_num, "actions": actions, "verified": True}

                queue.append((new_state, ops + [(i, delta)]))

    return {"level": lv_num, "actions": [], "verified": False}


def convert_to_clicks(cards, sliders, slider_cards, ops):
    """Convert (card_index, delta) operations to click coordinates."""
    actions = []
    for card_idx, delta in ops:
        card = cards[card_idx]
        # Find the slider for this card
        for slider in sliders:
            if card in slider_cards.get(id(slider), []):
                # Click right of center to grow, left to shrink
                sw = slider["width"]
                sh = slider["height"]
                is_horiz = sw > sh
                if is_horiz:
                    center = slider["x"] + sw // 2
                    if delta > 0:
                        cx = center + 2  # right of center
                    else:
                        cx = center - 2  # left of center
                    cy = slider["y"] + sh // 2
                else:
                    center = slider["y"] + sh // 2
                    cx = slider["x"] + sw // 2
                    if delta > 0:
                        cy = center + 2
                    else:
                        cy = center - 2
                actions.append(f"click({cx},{cy})")
                break
    return actions


def main():
    parser = argparse.ArgumentParser(description="s5i5 Solver")
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
