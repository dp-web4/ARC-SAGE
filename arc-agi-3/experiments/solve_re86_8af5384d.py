#!/usr/bin/env python3
"""
Solve re86-8af5384d (current server version) using local engine.

Old trace (run_20260412_092533) won L1+L2 on new server but died in L3
because L3's deformation/target pattern changed from the 22x4 corridor
in the old version. This run re-plans L3 and L5 against the new engine.

L1, L2: unchanged solutions replay cleanly.
L3 (NEW): 3 pieces (X-cross 23x23, diamond 25x25, line 43x1), 8 target
    centers scattered. Set-cover solver found MOV0@(31,13), MOV1@(6,18),
    MOV2@(6,6). MOV2 active at start so move it first.
L4: unchanged.
L5 (NEW): 3 pieces (plus cross 29x29, X-cross 23x23, diamond 19x19),
    target mixes color 9 (6 positions) + color 8 (4 positions).
    Solver found: MOV0 paints to 9 via zone (3,52); MOV1 paints to 9;
    MOV2 (deformable color-14) paints to 8 via zone (54,52).
    Path re-routed to avoid 29x29-wide MOV0 hitting zone 8 during descent.
L6, L7: unchanged cached solutions still work.
L8: cached 190-action sequence fails on new engine — pieces reshaped,
    zones reorganized. Skipped; partial trace ends at L8 start.

Writes into knowledge/visual-memory/re86/run_YYYYMMDD_HHMMSS/ via
SessionWriter. Uses local re86.py (no live server connection).
"""
import os
import sys
import time
import json
import numpy as np

# Use the new local re86.py
LOCAL_RE86 = "/mnt/c/exe/projects/ai-agents/ARC-SAGE/environment_files/re86/8af5384d"
sys.path.insert(0, LOCAL_RE86)
sys.path.insert(0, os.path.join(
    "/mnt/c/exe/projects/ai-agents/ARC-SAGE/arc-agi-3/experiments"))

from re86 import Re86  # noqa
from arcengine import GameAction, ActionInput  # noqa
from arc_session_writer import SessionWriter  # noqa

UP, DOWN, LEFT, RIGHT, SEL = (GameAction.ACTION1, GameAction.ACTION2,
                              GameAction.ACTION3, GameAction.ACTION4,
                              GameAction.ACTION5)

# Action int values for SessionWriter (1..5)
A_INT = {UP: 1, DOWN: 2, LEFT: 3, RIGHT: 4, SEL: 5}

SOLUTIONS = {
    # L1: old solution still works (20 actions).
    1: [RIGHT]*4 + [UP]*7 + [SEL] + [LEFT]*2 + [UP]*6,
    # L2: old solution still works (36 actions).
    2: ([LEFT]*3 + [DOWN]*10 + [SEL] + [LEFT]*6 + [UP]*6
        + [SEL] + [LEFT]*7 + [DOWN]*2),
    # L3 NEW: MOV2 (line) active first. Place: M2@(6,6), M0@(31,13),
    # M1@(6,18). Move M2 LEFT1 UP13, SEL, M0 RIGHT8 UP8, SEL, M1 LEFT9 UP6.
    3: ([LEFT]*1 + [UP]*13 + [SEL] + [RIGHT]*8 + [UP]*8
        + [SEL] + [LEFT]*9 + [UP]*6),
    # L4: old solution works.
    4: ([UP]*7 + [LEFT]*13 + [DOWN]*5 + [SEL] + [RIGHT]*8 + [DOWN]*8
        + [UP]*5 + [LEFT]*3),
    # L5 NEW: M1 active. Paint MOV1 via zone9 (down+left), position (19,4).
    # SEL -> MOV2. Paint via zone8 (right+down), position (42,27).
    # SEL -> MOV0. Paint MOV0 via zone9 (LEFT first to avoid zone8 at x>=25
    # with 29-wide piece), then position (19,37).
    5: ([DOWN]*7 + [LEFT]*2 + [RIGHT]*4 + [UP]*16
        + [SEL]
        + [RIGHT]*11 + [DOWN]*15 + [LEFT]*4 + [UP]*9
        + [SEL]
        + [LEFT]*11 + [DOWN]*7 + [RIGHT]*4 + [UP]*1),
    # L6: cached solution from re86_solutions.json (51 actions).
    # Still works against new engine.
    6: ([UP]*4 + [RIGHT]*4 + [DOWN]*5 + [RIGHT]*9 + [UP]*2
        + [SEL]
        + [LEFT]*7 + [DOWN]*1 + [RIGHT]*2 + [DOWN]*5 + [LEFT]*5 + [UP]*6),
    # L7: cached solution from re86_solutions.json (128 actions).
    # Still works against new engine.
    7: ([UP]*10 + [RIGHT]*5 + [UP]*1 + [DOWN]*1 + [LEFT]*3 + [DOWN]*6
        + [RIGHT]*4 + [UP]*3 + [DOWN]*6 + [RIGHT]*6 + [UP]*2
        + [SEL]
        + [LEFT]*1 + [UP]*13 + [DOWN]*1 + [RIGHT]*6 + [DOWN]*3 + [DOWN]*1
        + [RIGHT]*4 + [UP]*1
        + [SEL]
        + [LEFT]*5 + [UP]*12 + [RIGHT]*9 + [UP]*1 + [DOWN]*1 + [LEFT]*3
        + [DOWN]*1 + [RIGHT]*4 + [DOWN]*3 + [LEFT]*6 + [UP]*4),
}


def grid_snapshot(game):
    """Return 64x64 grid from camera."""
    return np.asarray(game.get_pixels(0, 0, 64, 64), dtype=np.int8)


def main():
    game = Re86()

    sw = SessionWriter(
        game_id="re86-8af5384d",
        win_levels=8,
        available_actions=[1, 2, 3, 4, 5],
        baseline=sum([26, 42, 86, 108, 189, 139, 424, 241]),  # from metadata
        player="re86-replan-L3-L5",
    )

    total_actions = 0
    levels_won = 0
    result = "PLAYING"

    for lnum in sorted(SOLUTIONS.keys()):
        actions = SOLUTIONS[lnum]
        won_this = False
        for i, a in enumerate(actions):
            prev = game.level_index
            game.perform_action(ActionInput(id=a))
            total_actions += 1
            grid = grid_snapshot(game)
            new_level_count = game.level_index  # 0-indexed level
            # "levels_completed" semantics: number of levels finished
            levels_completed = (new_level_count if new_level_count > prev
                                else levels_won)
            if new_level_count != prev:
                levels_completed = new_level_count  # level_index advanced
            sw.record_step(
                action=A_INT[a],
                grid=grid,
                levels_completed=levels_completed,
                state="PLAYING",
            )
            if new_level_count != prev:
                levels_won = new_level_count
                won_this = True
                print(f"L{lnum}: WIN at step {i+1} "
                      f"(total={total_actions}, level_idx={new_level_count})")
                break

            # Check for game over
            if game.xikvflgqgp.current_steps <= 0:
                result = "GAME_OVER"
                print(f"L{lnum}: GAME_OVER at step {i+1}")
                break

        if not won_this:
            print(f"L{lnum}: did not advance (tried {len(actions)} actions). "
                  f"Stopping trace.")
            break

    # If we won all 7 we planned for, we'd be at index 7 (L8). No L8 solution.
    if levels_won >= 7:
        print("L1-L7 complete. L8 not attempted (no working solution).")
        result = result if result != "PLAYING" else "STOPPED_AT_L8"

    sw.record_game_end(result, levels_completed=levels_won)

    print(f"\nSummary:")
    print(f"  Levels won: {levels_won} / 8")
    print(f"  Total actions: {total_actions}")
    print(f"  Run dir: {sw.run_dir}")


if __name__ == "__main__":
    main()
