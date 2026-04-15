#!/usr/bin/env python3
"""ar25 solver for new engine (0c556536). Plays L0-L4 cleanly.

Uses old L0-L2 action sequence (still works on new engine) + fresh L3/L4 plans
computed from wall layout + reflection math.
"""
import sys, json, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from arc_agi import Arcade
from arcengine import GameAction
from arc_perception import get_frame, get_all_frames
from arc_session_writer import SessionWriter

ACTION_MAP = {
    'UP': GameAction.ACTION1, 'DOWN': GameAction.ACTION2,
    'LEFT': GameAction.ACTION3, 'RIGHT': GameAction.ACTION4,
    'SELECT': GameAction.ACTION5, 'CLICK': GameAction.ACTION6,
    'UNDO': GameAction.ACTION7,
}
ACTION_INT = {k: v.value for k, v in ACTION_MAP.items()}

# L0-L2 sequence: copied from old trace (still valid on new engine)
L0_L2_SEQUENCE = [
    # L0: 15 actions
    'LEFT','LEFT','LEFT','LEFT','LEFT',
    'DOWN','DOWN','DOWN','DOWN','DOWN','DOWN','DOWN','DOWN','DOWN','DOWN',
    # L1: 32 actions
    'LEFT','LEFT','LEFT','LEFT','LEFT','LEFT','LEFT','LEFT','LEFT',
    'SELECT',
    'LEFT','LEFT','LEFT','LEFT','LEFT','LEFT','LEFT','LEFT','LEFT','LEFT','LEFT','LEFT','LEFT','LEFT',
    'DOWN','DOWN','DOWN','DOWN','DOWN','DOWN','DOWN','DOWN',
    # L2: 40 actions
    'UP','UP','UP','UP','UP','UP','UP',
    'SELECT',
    'LEFT','LEFT','LEFT','LEFT','LEFT','LEFT','LEFT','LEFT','LEFT','LEFT','LEFT','LEFT',
    'DOWN','DOWN','DOWN','DOWN','DOWN',
    'SELECT',
    'RIGHT','RIGHT','RIGHT','RIGHT','RIGHT','RIGHT','RIGHT',
    'DOWN','DOWN','DOWN','DOWN','DOWN','DOWN','DOWN',
]

# L3: new plan for new engine
# Mirror (starts selected) UP 7 from y=16 to y=9
# SELECT -> piece 0027 (L-shape) at (4,7); RIGHT*7 DOWN*7 -> (11,14) covers BR cluster
# SELECT -> piece 0053 (T-bar) at (15,9); LEFT*12 DOWN*5 -> (3,14) covers BL cluster
# Reflection hits TL/TR clusters via mirror at y=9
L3_SEQUENCE = (
    ['UP']*7 + ['SELECT'] +
    ['RIGHT']*7 + ['DOWN']*7 + ['SELECT'] +
    ['LEFT']*12 + ['DOWN']*5
)

# L4: mirror starts at y=3, DOWN*6 to y=9 (horizontal axis of symmetry)
# SELECT -> piece 0028 (U, 5x2); RIGHT*7 from (4,6) to (11,6) covers x=11-15 y=6-7
# SELECT -> piece 0032 (vertical 6-bar); RIGHT*7 from (6,10) to (13,10) — covers x=13 column
# Reflection at y=9 completes the figure
L4_SEQUENCE = (
    ['DOWN']*6 + ['SELECT'] +
    ['RIGHT']*7 + ['SELECT'] +
    ['RIGHT']*7
)


def main():
    arcade = Arcade()
    env = arcade.make('ar25-0c556536')
    fd = env.reset()
    grid = get_frame(fd)

    writer = SessionWriter(
        game_id='ar25-0c556536',
        win_levels=fd.win_levels,
        available_actions=list(fd.available_actions),
        baseline=0,
        player='ar25_v2_l4_solver',
    )

    full_sequence = list(L0_L2_SEQUENCE) + L3_SEQUENCE + L4_SEQUENCE

    for act in full_sequence:
        ga = ACTION_MAP[act]
        fd = env.step(ga)
        grid = get_frame(fd)
        all_frames = get_all_frames(fd)
        writer.record_step(
            action=ACTION_INT[act],
            grid=grid,
            all_frames=all_frames,
            levels_completed=int(fd.levels_completed),
            state=fd.state.name,
        )
        if fd.state.name in ('GAME_OVER', 'WIN'):
            print(f"Stopped at state={fd.state.name}, level={fd.levels_completed}")
            break

    writer.record_game_end(state=fd.state.name, levels_completed=int(fd.levels_completed))

    print(f"\nFinal: levels={fd.levels_completed}/{fd.win_levels}, state={fd.state.name}")
    print(f"Total steps: {writer.step}")
    print(f"Run dir: {writer.run_dir}")


if __name__ == '__main__':
    main()
