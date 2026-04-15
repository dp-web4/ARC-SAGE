#!/usr/bin/env python3
"""Solve cn04-2fe56bfb (6-level version).

Matches 8-pins with 8-pins AND 13-pins with 13-pins (same-color only).
Handles stacked sprites (multiple sprites at same position, cycled via
re-click on selected). Renders session via SessionWriter.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from arc_agi import Arcade
from arcengine import GameAction
import numpy as np
from collections import Counter
from itertools import permutations, product
import time
import traceback

from arc_session_writer import SessionWriter


def rotated_pixels(pixels, rot):
    p = pixels.copy()
    k = (rot % 360) // 90
    for _ in range(k):
        p = np.rot90(p, k=-1)  # CW
    return p


def get_marks(pixels, rot):
    p = rotated_pixels(pixels, rot)
    e8 = [(x, y) for y in range(p.shape[0]) for x in range(p.shape[1]) if p[y, x] == 8]
    e13 = [(x, y) for y in range(p.shape[0]) for x in range(p.shape[1]) if p[y, x] == 13]
    w, h = p.shape[1], p.shape[0]
    return e8, e13, w, h


def solve_level(sprite_options, grid_w, grid_h, verbose=True):
    """
    sprite_options: list of "slots", each slot is a list of (name, pix, orig_x, orig_y, orig_rot)
                    Each slot will choose ONE sprite (the active member of a stack).
                    For non-stack, list has single entry.
    Returns list of (slot_idx, chosen_name, px, py, rot) or None.
    """
    n = len(sprite_options)

    # Pre-compute all (slot, option_idx, rot, 8s, 13s, w, h)
    # For stack slots (len(opts) > 1), rotation is FIXED at orot (can't rotate stack members)
    # For single slots, try all rotations.
    slot_configs = []
    for slot_i, opts in enumerate(sprite_options):
        cfgs = []
        is_stack = len(opts) > 1
        for opt_i, (name, pix, ox, oy, orot) in enumerate(opts):
            if is_stack:
                rotations = [orot]
            else:
                rotations = [0, 90, 180, 270]
            for rot in rotations:
                e8, e13, w, h = get_marks(pix, rot)
                cfgs.append((opt_i, rot, e8, e13, w, h))
        slot_configs.append(cfgs)

    solutions = []

    def try_place(order, step, placed, existing_8, existing_13):
        """placed: list of (slot_i, opt_i, px, py, rot, world_8s, world_13s)."""
        if solutions:
            return
        if step == len(order):
            # Check all 8s paired (count==2), all 13s paired
            c8 = Counter()
            c13 = Counter()
            for _, _, _, _, _, w8, w13 in placed:
                c8.update(w8)
                c13.update(w13)
            if all(v == 2 for v in c8.values()) and all(v == 2 for v in c13.values()):
                solutions.append(list(placed))
            return

        slot_i = order[step]

        # Figure out unpaired 8s and 13s in current state
        all_w8, all_w13 = [], []
        for _, _, _, _, _, w8, w13 in placed:
            all_w8.extend(w8)
            all_w13.extend(w13)
        c8 = Counter(all_w8)
        c13 = Counter(all_w13)
        unpaired_8 = {pos for pos, cnt in c8.items() if cnt == 1}
        unpaired_13 = {pos for pos, cnt in c13.items() if cnt == 1}

        # For each option of this slot, try each rotation, candidate positions
        for opt_i, rot, e8, e13, w, h in slot_configs[slot_i]:
            # Candidate positions come from: aligning any local 8 to an unpaired 8,
            # or any local 13 to an unpaired 13. For the first placement, use the
            # orig_x, orig_y (fixed reference).
            if step == 0:
                opts = sprite_options[slot_i]
                name, pix, ox, oy, orot = opts[opt_i]
                candidate_positions = {(ox, oy)}
            else:
                candidate_positions = set()
                for cx, cy in e8:
                    for ux, uy in unpaired_8:
                        px, py = ux - cx, uy - cy
                        if 0 <= px and 0 <= py and px + w <= grid_w and py + h <= grid_h:
                            candidate_positions.add((px, py))
                for cx, cy in e13:
                    for ux, uy in unpaired_13:
                        px, py = ux - cx, uy - cy
                        if 0 <= px and 0 <= py and px + w <= grid_w and py + h <= grid_h:
                            candidate_positions.add((px, py))
                # If this slot has no pins at all, allow any position (rare)
                if not e8 and not e13:
                    # center of grid
                    candidate_positions.add((0, 0))

            for px, py in candidate_positions:
                w8_world = tuple((px + cx, py + cy) for cx, cy in e8)
                w13_world = tuple((px + cx, py + cy) for cx, cy in e13)

                # Check counts won't exceed 2
                temp_c8 = Counter(all_w8)
                temp_c8.update(w8_world)
                if any(v > 2 for v in temp_c8.values()):
                    continue
                temp_c13 = Counter(all_w13)
                temp_c13.update(w13_world)
                if any(v > 2 for v in temp_c13.values()):
                    continue

                # If last step, must have all==2
                if step == len(order) - 1:
                    if any(v != 2 for v in temp_c8.values()):
                        continue
                    if any(v != 2 for v in temp_c13.values()):
                        continue

                placed.append((slot_i, opt_i, px, py, rot, w8_world, w13_world))
                try_place(order, step + 1, placed, None, None)
                placed.pop()
                if solutions:
                    return

    # Try all orderings
    for perm in permutations(range(n)):
        if solutions:
            break
        try_place(perm, 0, [], None, None)

    if solutions:
        return solutions[0]

    # Fallback: first slot not fixed — move it
    if verbose:
        print("  Falling back to free-first search...")
    for perm in permutations(range(n)):
        if solutions:
            break
        slot_i = perm[0]
        for opt_i, rot, e8, e13, w, h in slot_configs[slot_i]:
            for px in range(grid_w - w + 1):
                for py in range(grid_h - h + 1):
                    w8_world = tuple((px + cx, py + cy) for cx, cy in e8)
                    w13_world = tuple((px + cx, py + cy) for cx, cy in e13)
                    placed = [(slot_i, opt_i, px, py, rot, w8_world, w13_world)]
                    try_place(perm, 1, placed, None, None)
                    if solutions:
                        break
                if solutions:
                    break
            if solutions:
                break

    return solutions[0] if solutions else None


def identify_stacks(level):
    """Group sprites by initial position. Returns list of slots."""
    sprites = list(level.get_sprites())
    groups = {}
    order = []
    for s in sprites:
        key = (s.x, s.y)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(s)
    slots = []
    for key in order:
        slots.append(groups[key])
    return slots


def click_display_for_sprite(cam, sprite, game):
    """Find a display coord that clicks this sprite (on a non-transparent non-8/13 pixel for select)."""
    pix = sprite.pixels  # current (possibly modified) pixels
    # sprite may be "visible" in displayed form. We need to click a pixel that renders >=0.
    rendered = sprite.render()
    # Iterate display coords; find ones that map to a sprite pixel
    for dy in range(64):
        for dx in range(64):
            r = cam.display_to_grid(dx, dy)
            if not r:
                continue
            gx, gy = r
            if sprite.x <= gx < sprite.x + sprite.width and sprite.y <= gy < sprite.y + sprite.height:
                lx, ly = gx - sprite.x, gy - sprite.y
                if 0 <= ly < rendered.shape[0] and 0 <= lx < rendered.shape[1]:
                    if rendered[ly, lx] >= 0:
                        return dx, dy
    return None


def main():
    arcade = Arcade()
    env = arcade.make('cn04-2fe56bfb')
    fd = env.reset()
    game = env._game

    avail_actions = [1, 2, 3, 4, 5, 6]
    baseline = sum([29, 54, 85, 300, 208, 113])
    writer = SessionWriter(
        game_id='cn04-2fe56bfb',
        win_levels=6,
        available_actions=avail_actions,
        baseline=baseline,
        player='cn04_solver_v2'
    )

    total_actions = 0
    for lv in range(6):
        print(f"\n{'='*60}")
        print(f"Level {lv} — state={fd.state.name} completed={fd.levels_completed}")
        level = game.current_level
        grid_w, grid_h = level.grid_size
        print(f"  Grid: {grid_w}x{grid_h}")

        slots = identify_stacks(level)
        slot_options = []
        for slot_sprites in slots:
            opts = []
            for s in slot_sprites:
                pix = game.hlxyvcmpk[s.name]
                opts.append((s.name, pix, s.x, s.y, s.rotation))
            slot_options.append(opts)

        print(f"  Slots: {len(slot_options)}")
        for i, opts in enumerate(slot_options):
            print(f"    Slot {i}: {len(opts)} option(s)")
            for nm, pix, ox, oy, orot in opts:
                e8, e13, w, h = get_marks(pix, orot)
                print(f"      {nm} pos=({ox},{oy}) rot={orot} size={w}x{h} 8s={len(e8)} 13s={len(e13)}")

        sol = solve_level(slot_options, grid_w, grid_h, verbose=True)
        if not sol:
            print("  NO SOLUTION FOUND — aborting")
            break

        print(f"  Solution:")
        # sol: list of (slot_i, opt_i, px, py, rot, w8, w13)
        # Sort by slot_i for execution order
        sol_by_slot = {item[0]: item for item in sol}

        # Plan execution actions per slot
        # Current selected sprite
        for slot_i in range(len(slot_options)):
            slot_i_sol = sol_by_slot[slot_i]
            _, opt_i, tx, ty, trot, _, _ = slot_i_sol
            chosen_name = slot_options[slot_i][opt_i][0]
            print(f"    Slot {slot_i}: choose {chosen_name} → ({tx},{ty}) rot={trot}")

        # Execution
        for slot_i in range(len(slot_options)):
            slot_i_sol = sol_by_slot[slot_i]
            _, opt_i, tx, ty, trot, _, _ = slot_i_sol
            opts = slot_options[slot_i]
            chosen_name = opts[opt_i][0]

            # Find current sprite by name (if it's the stack member), or stack
            level = game.current_level
            all_sprites = list(level.get_sprites())
            target_sprite = None
            for s in all_sprites:
                if s.name == chosen_name:
                    target_sprite = s
                    break
            if target_sprite is None:
                print(f"    CAN'T FIND {chosen_name}")
                break

            # Select: if this slot is a stack, we need to click one member and cycle
            # until chosen_name is active (visible & == game.xseexqzst).
            # If single sprite, just click it.

            # Check if selected already
            stack_sprites = opts  # list of (name, pix, ox, oy, orot)
            stack_names = {o[0] for o in stack_sprites}

            # Is the current selection already in this stack?
            cur_sel = game.xseexqzst
            if cur_sel is not None and cur_sel.name == chosen_name:
                pass  # already correct
            elif cur_sel is not None and cur_sel.name in stack_names and len(stack_sprites) > 1:
                # Cycle via ACTION5 until we reach chosen_name
                guard = 0
                while game.xseexqzst is None or game.xseexqzst.name != chosen_name:
                    if guard > len(stack_sprites) * 3:
                        print(f"    CYCLE stuck trying to reach {chosen_name}")
                        break
                    fd = env.step(GameAction.ACTION5)
                    writer.record_step(5, fd.frame[-1] if isinstance(fd.frame, list) else fd.frame,
                                       levels_completed=fd.levels_completed,
                                       state=fd.state.name)
                    total_actions += 1
                    guard += 1
                    if fd.state.name != 'NOT_FINISHED':
                        break
                    if fd.levels_completed > lv:
                        break
            else:
                # Need to click to select. For stack, click the visible member.
                if len(stack_sprites) > 1:
                    visible_member = None
                    for nm, _, _, _, _ in stack_sprites:
                        for s in all_sprites:
                            if s.name == nm and s.is_visible:
                                visible_member = s
                                break
                        if visible_member:
                            break
                    if visible_member is None:
                        print(f"    No visible member in stack for slot {slot_i}!")
                        break
                    click_coord = click_display_for_sprite(game.camera, visible_member, game)
                    if click_coord is None:
                        print(f"    Can't compute click for {visible_member.name}")
                        break
                    cx, cy = click_coord
                    fd = env.step(GameAction.ACTION6, data={'x': cx, 'y': cy})
                    writer.record_step(6, fd.frame[-1] if isinstance(fd.frame, list) else fd.frame,
                                       levels_completed=fd.levels_completed, x=cx, y=cy,
                                       state=fd.state.name)
                    total_actions += 1
                    # Now cycle to reach chosen_name
                    guard = 0
                    while game.xseexqzst is None or game.xseexqzst.name != chosen_name:
                        if guard > len(stack_sprites) * 3:
                            print(f"    CYCLE stuck trying to reach {chosen_name}")
                            break
                        fd = env.step(GameAction.ACTION5)
                        writer.record_step(5, fd.frame[-1] if isinstance(fd.frame, list) else fd.frame,
                                           levels_completed=fd.levels_completed,
                                           state=fd.state.name)
                        total_actions += 1
                        guard += 1
                        if fd.state.name != 'NOT_FINISHED':
                            break
                        if fd.levels_completed > lv:
                            break
                else:
                    click_coord = click_display_for_sprite(game.camera, target_sprite, game)
                    if click_coord is None:
                        print(f"    Can't compute click for {chosen_name}")
                        break
                    cx, cy = click_coord
                    fd = env.step(GameAction.ACTION6, data={'x': cx, 'y': cy})
                    writer.record_step(6, fd.frame[-1] if isinstance(fd.frame, list) else fd.frame,
                                       levels_completed=fd.levels_completed, x=cx, y=cy,
                                       state=fd.state.name)
                    total_actions += 1

            # Now selected sprite is chosen_name. Refresh.
            target_sprite = None
            for s in game.current_level.get_sprites():
                if s.name == chosen_name:
                    target_sprite = s
                    break

            # Rotate to target (only for single-sprite slots; stack members can't rotate)
            is_stack = len(stack_sprites) > 1
            if not is_stack:
                cur_rot = target_sprite.rotation
                rot_needed = ((trot - cur_rot) % 360) // 90
                for _ in range(rot_needed):
                    fd = env.step(GameAction.ACTION5)
                    writer.record_step(5, fd.frame[-1] if isinstance(fd.frame, list) else fd.frame,
                                       levels_completed=fd.levels_completed, state=fd.state.name)
                    total_actions += 1
                    if fd.state.name == 'WIN' or fd.levels_completed > lv:
                        break

            # Refresh
            for s in game.current_level.get_sprites():
                if s.name == chosen_name:
                    target_sprite = s
                    break

            # Move
            dx = tx - target_sprite.x
            dy = ty - target_sprite.y
            for _ in range(abs(dx)):
                act = GameAction.ACTION4 if dx > 0 else GameAction.ACTION3
                fd = env.step(act)
                writer.record_step(act.value, fd.frame[-1] if isinstance(fd.frame, list) else fd.frame,
                                   levels_completed=fd.levels_completed, state=fd.state.name)
                total_actions += 1
                if fd.state.name == 'WIN' or fd.levels_completed > lv:
                    break
            for _ in range(abs(dy)):
                act = GameAction.ACTION2 if dy > 0 else GameAction.ACTION1
                fd = env.step(act)
                writer.record_step(act.value, fd.frame[-1] if isinstance(fd.frame, list) else fd.frame,
                                   levels_completed=fd.levels_completed, state=fd.state.name)
                total_actions += 1
                if fd.state.name == 'WIN' or fd.levels_completed > lv:
                    break

            if fd.levels_completed > lv:
                print(f"  Level {lv} won at total_actions={total_actions}")
                break
            if fd.state.name != 'NOT_FINISHED':
                print(f"  Game state={fd.state.name}, stopping")
                break

        if fd.state.name == 'WIN':
            print(f"  *** GAME WIN at total_actions={total_actions} ***")
            break
        if fd.levels_completed <= lv:
            print(f"  Failed to advance past L{lv}. Debug:")
            print(f"    Final state: {fd.state.name} completed={fd.levels_completed}")
            for s in game.current_level.get_sprites():
                if not s.is_visible:
                    continue
                pix = game.hlxyvcmpk[s.name]
                e8, e13, w, h = get_marks(pix, s.rotation)
                w8 = [(s.x+x, s.y+y) for x,y in e8]
                w13 = [(s.x+x, s.y+y) for x,y in e13]
                print(f"    {s.name} pos=({s.x},{s.y}) rot={s.rotation} 8={w8} 13={w13}")
            break

    # Final
    writer.record_game_end(fd.state.name, fd.levels_completed)
    print(f"\nFinal: state={fd.state.name} levels={fd.levels_completed}/6 actions={total_actions}")
    print(f"Run dir: {writer.run_dir}")


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
