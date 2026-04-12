#!/usr/bin/env python3
"""
tr87 Pattern-Matching Rewrite-Rule Solver

Parses the tr87.py game source to extract:
  - Symbol sprite definitions (nxkictbbvzt{Family}{Digit})
  - Level layouts: rules (left->right pairs), input row, output row
  - Per-level flags: double_translation, alter_rules, tree_translation

For each level, determines the correct output symbols and computes the
minimal UP/DOWN/LEFT/RIGHT action sequence to set them.

Usage:
    python tr87_solver.py [--level N] [--source PATH]
"""

import re
import sys
import random
import argparse
from typing import List, Tuple, Optional, Dict

# ---------------------------------------------------------------------------
# Constants from the game source
# ---------------------------------------------------------------------------

GAME_SOURCE_DEFAULT = (
    "/Users/dennispalatov/repos/shared-context/environment_files/"
    "tr87/cd924810/tr87.py"
)

SYMBOL_SPACING = 7  # iokndxodxw
CYCLE_LEN = 7       # kjgicbtgrt


# ---------------------------------------------------------------------------
# Parse source
# ---------------------------------------------------------------------------

def parse_source(path: str) -> str:
    with open(path) as f:
        return f.read()


def extract_levels_raw(source: str) -> list:
    """Extract level blocks from the levels = [...] list."""
    levels = []
    # Find each Level() block
    pattern = re.compile(
        r'#\s*Level\s+(\d+)\s*\n\s*Level\(\s*sprites=\[(.*?)\],\s*'
        r'grid_size=\((\d+),\s*(\d+)\)',
        re.DOTALL,
    )
    for m in pattern.finditer(source):
        level_num = int(m.group(1))
        sprites_block = m.group(2)
        gw, gh = int(m.group(3)), int(m.group(4))

        # Extract data dict if present
        data_m = re.search(
            r'data=\{([^}]*)\}',
            source[m.end():m.end()+200]
        )
        data = {}
        if data_m:
            data_str = data_m.group(1)
            if 'double_translation' in data_str:
                data['double_translation'] = True
            if 'alter_rules' in data_str:
                data['alter_rules'] = True
            if 'tree_translation' in data_str:
                data['tree_translation'] = True

        # Extract sprite placements
        sp_pattern = re.compile(
            r'sprites\["(\w+)"\]\.clone\(\)\.set_position\((\d+),\s*(\d+)\)'
        )
        placements = []
        for sp_m in sp_pattern.finditer(sprites_block):
            name = sp_m.group(1)
            x, y = int(sp_m.group(2)), int(sp_m.group(3))
            placements.append((name, x, y))

        levels.append({
            'num': level_num,
            'grid': (gw, gh),
            'placements': placements,
            'data': data,
        })

    return levels


def parse_level_structure(level: dict) -> dict:
    """Parse a level into rules, input row, output row.

    Layout:
      - Separators (iqrduxrukrk, 11px wide) connect left-side to right-side symbols
      - Symbols are 5x5, positioned 2 pixels above the separator y
      - Background divider separates rule area from answer area
      - Answer area: input row (top) and output row (bottom)
      - Symbols are spaced 7px apart horizontally (iokndxodxw=7)
    """
    placements = level['placements']

    # Find background divider position
    bg_sprites = [p for p in placements if p[0] == 'background']
    bg_y = bg_sprites[0][2] if bg_sprites else None

    # Find iqrduxrukrk (rule separators)
    seps = [(p[1], p[2]) for p in placements if p[0] == 'iqrduxrukrk']
    seps.sort(key=lambda s: (s[1], s[0]))

    # Find all nxkictbbvzt symbols (the puzzle pieces)
    symbols = [(p[0], p[1], p[2]) for p in placements
               if p[0].startswith('nxkictbbvzt') and len(p[0]) > len('nxkictbbvzt')]
    # Exclude the highlight overlay
    symbols = [(n, x, y) for n, x, y in symbols if 'edxeenecwqa' not in n]

    # Separate into above-divider (rules) and below-divider (input/output)
    if bg_y is not None:
        rule_symbols = [(n, x, y) for n, x, y in symbols if y < bg_y]
        answer_symbols = [(n, x, y) for n, x, y in symbols if y >= bg_y]
    else:
        rule_symbols = symbols
        answer_symbols = []

    # Parse rules from separators using the game's logic:
    # 1. Find symbol at (sep_x, sep_y) -- this starts the LEFT side
    # 2. Walk left by SYMBOL_SPACING to find more left symbols (qrkneeaawb)
    # 3. Find symbol at (sep_x + sep_width, sep_y) -- this starts the RIGHT side
    # 4. Walk right by SYMBOL_SPACING to find more right symbols
    #
    # "get_sprite_at" checks if point is inside the sprite's bounding box.
    # Symbols are 5x5, so a symbol at (sx, sy) covers (sx..sx+4, sy..sy+4).
    rules = []

    SEP_WIDTH = 11  # iqrduxrukrk is 11px wide
    SYM_W = 5  # symbol width
    SYM_H = 5  # symbol height

    def find_symbol_at(px, py, syms):
        """Find symbol whose bounding box contains point (px, py)."""
        for n, x, y in syms:
            if x <= px < x + SYM_W and y <= py < y + SYM_H:
                return (n, x, y)
        return None

    def find_neighbor(sym, direction, syms):
        """Find adjacent symbol in given direction (+1=right, -1=left)."""
        _, sx, sy = sym
        nx = sx + direction * SYMBOL_SPACING
        for n, x, y in syms:
            if x == nx and y == sy:
                return (n, x, y)
        return None

    for sep_x, sep_y in seps:
        # Find left-side start
        left_start = find_symbol_at(sep_x, sep_y, rule_symbols)
        if not left_start:
            continue

        # Walk left to build full left side
        left = [left_start]
        while True:
            prev = find_neighbor(left[0], -1, rule_symbols)
            if prev:
                left.insert(0, prev)
            else:
                break

        # Find right-side start
        right_start = find_symbol_at(sep_x + SEP_WIDTH, sep_y, rule_symbols)
        if not right_start:
            # Try sep_x + SEP_WIDTH - 1 in case of off-by-one
            right_start = find_symbol_at(sep_x + SEP_WIDTH - 1, sep_y, rule_symbols)

        right = []
        if right_start:
            right = [right_start]
            while True:
                nxt = find_neighbor(right[-1], 1, rule_symbols)
                if nxt:
                    right.append(nxt)
                else:
                    break

        rules.append({
            'left': [n for n, x, y in left],
            'right': [n for n, x, y in right],
            'sep_x': sep_x,
            'sep_y': sep_y,
        })

    # Parse answer area
    answer_symbols.sort(key=lambda s: (s[2], s[1]))
    if answer_symbols:
        # Two rows: input (top) and output (bottom)
        ys = sorted(set(s[2] for s in answer_symbols))
        if len(ys) >= 2:
            input_y = ys[0]
            output_y = ys[1]
            input_row = [(n, x) for n, x, y in answer_symbols if y == input_y]
            output_row = [(n, x) for n, x, y in answer_symbols if y == output_y]
            input_row.sort(key=lambda s: s[1])
            output_row.sort(key=lambda s: s[1])
        else:
            input_row = [(n, x) for n, x, y in answer_symbols]
            input_row.sort(key=lambda s: s[1])
            output_row = []
    else:
        input_row = []
        output_row = []

    # Find portal connectors (tjaqvwdgkxe)
    portals = [(p[0], p[1], p[2]) for p in placements
               if 'jpafjzbfwiq' in p[0]]

    return {
        'rules': rules,
        'input_row': input_row,
        'output_row': output_row,
        'portals': portals,
        'data': level['data'],
        'num': level['num'],
    }


def symbol_family(name: str) -> str:
    """Extract family letter from symbol name like nxkictbbvztA3."""
    base = 'nxkictbbvzt'
    suffix = name[len(base):]
    return suffix[0] if suffix else '?'


def symbol_digit(name: str) -> int:
    """Extract digit from symbol name like nxkictbbvztA3."""
    return int(name[-1])


def cycle_symbol(name: str, delta: int) -> str:
    """Cycle a symbol by delta steps."""
    base = name[:-1]
    digit = int(name[-1])
    new_digit = (digit + delta - 1) % CYCLE_LEN + 1
    return base + str(new_digit)


def apply_rules_simple(input_names: List[str], rules: List[dict]) -> Optional[List[str]]:
    """Apply rewrite rules to input, return expected output.

    Greedy left-to-right matching: try each rule at current position.
    """
    output = []
    pos = 0
    while pos < len(input_names):
        matched = False
        for rule in rules:
            lhs = rule['left']
            rhs = rule['right']
            if pos + len(lhs) <= len(input_names):
                if all(input_names[pos + i] == lhs[i] for i in range(len(lhs))):
                    output.extend(rhs)
                    pos += len(lhs)
                    matched = True
                    break
        if not matched:
            return None  # No rule matches
    return output


def apply_rules_double(input_names: List[str], rules: List[dict],
                       portals: list, all_rules: List[dict]) -> Optional[List[str]]:
    """Apply rules with double_translation (portal chaining)."""
    # Build portal map: portal connectors pair rules
    # Portal A1 at position -> connects to A2 at position
    # When a rule's left side starts at a portal, follow to find chained rule

    # For simplicity, try standard rule application but with chaining
    output = []
    pos = 0
    while pos < len(input_names):
        matched = False
        for rule in rules:
            lhs = rule['left']
            rhs = rule['right']
            if pos + len(lhs) <= len(input_names):
                if all(input_names[pos + i] == lhs[i] for i in range(len(lhs))):
                    # Check if this needs double translation
                    # Find second rule whose LHS matches RHS
                    found_chain = False
                    for rule2 in all_rules:
                        if len(rule2['left']) == len(rhs):
                            if all(rhs[i] == rule2['left'][i] for i in range(len(rhs))):
                                output.extend(rule2['right'])
                                found_chain = True
                                break
                    if not found_chain:
                        output.extend(rhs)
                    pos += len(lhs)
                    matched = True
                    break
        if not matched:
            return None
    return output


def compute_target_output(level_info: dict) -> Optional[List[str]]:
    """Compute what the output row should be."""
    rules = level_info['rules']
    input_names = [n for n, x in level_info['input_row']]
    data = level_info['data']

    if data.get('alter_rules') or data.get('tree_translation'):
        # These levels require modifying the rules themselves
        # Cannot compute target from static rules alone
        return None

    if data.get('double_translation'):
        return apply_rules_double(input_names, rules, level_info['portals'], rules)
    else:
        return apply_rules_simple(input_names, rules)


def apply_random_rotations(level_info: dict, level_idx: int) -> dict:
    """Apply the random rotations that the game applies on level load.

    The game randomizes output row symbols. We need to know the initial state
    to compute the delta actions needed.
    """
    ofysoutulp = [4, 2, 1, 2, 12, 20]
    seed = ofysoutulp[level_idx]
    rng = random.Random(seed)

    # Rotations on symbols are visual only, matching uses name
    # The game randomizes symbol variants in the output row

    ripmydnety = [7, 7, 32, 18, 23, 11]
    rng2 = random.Random(ripmydnety[level_idx])

    data = level_info['data']

    if data.get('alter_rules'):
        # In alter_rules mode, ALL symbol groups get randomized
        # Each rule side gets a random offset applied to all symbols
        new_rules = []
        for rule in level_info['rules']:
            new_rule = dict(rule)
            for side_key in ['left', 'right']:
                offset = rng2.randint(0, 6)
                new_side = []
                for name in rule[side_key]:
                    new_name = name
                    for _ in range(offset):
                        new_name = cycle_symbol(new_name, 1)
                    new_side.append(new_name)
                new_rule[side_key] = new_side
            new_rules.append(new_rule)

        return {**level_info, 'rules': new_rules,
                'initial_output': [cycle_symbol(n, 0) for n, x in level_info['output_row']]}
    else:
        # Only output row gets randomized
        initial_output = []
        for name, x in level_info['output_row']:
            offset = rng2.randint(0, 6)
            new_name = name
            for _ in range(offset):
                new_name = cycle_symbol(new_name, 1)
            initial_output.append(new_name)

        return {**level_info, 'initial_output': initial_output}


def compute_actions(current_names: List[str], target_names: List[str],
                    alter_rules: bool = False) -> List[str]:
    """Compute the minimal LEFT/RIGHT + UP/DOWN action sequence.

    In normal mode: cursor starts at position 0 of output row.
    LEFT/RIGHT moves cursor. UP/DOWN cycles current symbol.
    """
    if not target_names or not current_names:
        return []

    actions = []
    cursor_pos = 0

    for i, (current, target) in enumerate(zip(current_names, target_names)):
        # Move cursor to position i
        while cursor_pos < i:
            actions.append('RIGHT')
            cursor_pos += 1
        while cursor_pos > i:
            actions.append('LEFT')
            cursor_pos -= 1

        # Compute cycling needed
        if current != target:
            cur_digit = symbol_digit(current)
            tgt_digit = symbol_digit(target)

            # Check families match
            cur_family = symbol_family(current)
            tgt_family = symbol_family(target)
            if cur_family != tgt_family:
                print(f"  WARNING: Family mismatch at pos {i}: {current} vs {target}")
                continue

            # Compute shortest cycle direction
            up_steps = (tgt_digit - cur_digit) % CYCLE_LEN
            down_steps = (cur_digit - tgt_digit) % CYCLE_LEN

            if up_steps == 0:
                continue

            # UP = +1 direction (ACTION2=DOWN key cycles +1)
            # DOWN = -1 direction (ACTION1=UP key cycles -1)
            # From source: pxdsteijos = -1 if ACTION1 else 1
            # wpbnovjwkv: (digit + direction - 1) % 7 + 1
            # So ACTION2 (DOWN) increases digit, ACTION1 (UP) decreases
            if down_steps <= up_steps:
                for _ in range(down_steps):
                    actions.append('UP')
            else:
                for _ in range(up_steps):
                    actions.append('DOWN')

    return actions


def grid_to_display(gx: int, gy: int, gw: int, gh: int) -> Tuple[int, int]:
    """Convert grid coords to 64x64 display coords."""
    ox = (64 - gw) // 2
    oy = (64 - gh) // 2
    return (gx + ox, gy + oy)


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_actions(initial_names: List[str], target_names: List[str],
                   actions: List[str]) -> bool:
    """Simulate the action sequence and verify we reach target."""
    current = list(initial_names)
    cursor = 0
    n = len(current)

    for action in actions:
        if action == 'LEFT':
            cursor = (cursor - 1) % n
        elif action == 'RIGHT':
            cursor = (cursor + 1) % n
        elif action == 'UP':
            current[cursor] = cycle_symbol(current[cursor], -1)
        elif action == 'DOWN':
            current[cursor] = cycle_symbol(current[cursor], 1)

    return current == target_names


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def solve_level(level_info: dict, level_idx: int, verbose: bool = True) -> Optional[dict]:
    """Solve a single level."""
    data = level_info['data']

    if verbose:
        print(f"  Rules: {len(level_info['rules'])}")
        for i, rule in enumerate(level_info['rules']):
            lhs = [n.split('nxkictbbvzt')[1] for n in rule['left']]
            rhs = [n.split('nxkictbbvzt')[1] for n in rule['right']]
            print(f"    Rule {i+1}: {' '.join(lhs)} -> {' '.join(rhs)}")
        inp = [n.split('nxkictbbvzt')[1] for n, x in level_info['input_row']]
        out = [n.split('nxkictbbvzt')[1] for n, x in level_info['output_row']]
        print(f"  Input:  {' '.join(inp)}")
        print(f"  Output: {' '.join(out)}")
        print(f"  Flags: {data}")

    # For levels with alter_rules or tree_translation, we need different approach
    if data.get('alter_rules') and not data.get('tree_translation'):
        # Level 5: alter_rules only
        # We can modify rule sides. Need to find a configuration where rules work.
        if verbose:
            print("  alter_rules mode - need BFS over rule modifications")
            print("  SKIPPING (complex alter_rules solver not implemented)")
        return None

    if data.get('tree_translation'):
        if verbose:
            print("  tree_translation mode - complex chaining")
            print("  SKIPPING (complex tree_translation solver not implemented)")
        return None

    # Compute target output
    target = compute_target_output(level_info)
    if target is None:
        if verbose:
            print("  Could not compute target output")
        return None

    if verbose:
        tgt = [n.split('nxkictbbvzt')[1] for n in target]
        print(f"  Target: {' '.join(tgt)}")

    # Apply random rotations to get initial state
    rotated_info = apply_random_rotations(level_info, level_idx)
    initial_output = rotated_info.get('initial_output', [])

    if not initial_output:
        # If no randomization, initial = current output names
        initial_output = [n for n, x in level_info['output_row']]

    if verbose:
        init = [n.split('nxkictbbvzt')[1] for n in initial_output]
        print(f"  Initial output (after random): {' '.join(init)}")

    # Compute actions
    actions = compute_actions(initial_output, target)

    if verbose:
        print(f"  Actions ({len(actions)}): {' '.join(actions)}")

    # Verify
    ok = verify_actions(initial_output, target, actions)
    if verbose:
        print(f"  {'VERIFIED OK' if ok else 'VERIFICATION FAILED'}")

    return {
        'level': level_info['num'],
        'actions': actions,
        'target': target,
        'initial': initial_output,
        'verified': ok,
    }


def main():
    parser = argparse.ArgumentParser(description="tr87 Rewrite-Rule Solver")
    parser.add_argument("--level", type=int, default=None)
    parser.add_argument("--source", type=str, default=GAME_SOURCE_DEFAULT)
    args = parser.parse_args()

    print("Parsing game source...")
    source = parse_source(args.source)

    print("Extracting levels...")
    raw_levels = extract_levels_raw(source)
    print(f"  Found {len(raw_levels)} levels")

    level_infos = []
    for lv in raw_levels:
        info = parse_level_structure(lv)
        level_infos.append(info)

    if args.level is not None:
        targets = [li for li in level_infos if li['num'] == args.level]
    else:
        targets = level_infos

    results = []
    for i, li in enumerate(targets):
        print(f"\n{'='*60}")
        print(f"Level {li['num']}:")
        result = solve_level(li, li['num'] - 1)
        if result:
            results.append(result)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for r in results:
        status = "VERIFIED OK" if r['verified'] else "FAILED"
        print(f"  Level {r['level']}: {len(r['actions'])} actions ... {status}")
        if r['actions']:
            # Compress consecutive identical actions
            compressed = []
            if r['actions']:
                curr = r['actions'][0]
                cnt = 1
                for a in r['actions'][1:]:
                    if a == curr:
                        cnt += 1
                    else:
                        compressed.append(f"{curr}x{cnt}")
                        curr = a
                        cnt = 1
                compressed.append(f"{curr}x{cnt}")
            print(f"    Compressed: {', '.join(compressed)}")


if __name__ == "__main__":
    main()
