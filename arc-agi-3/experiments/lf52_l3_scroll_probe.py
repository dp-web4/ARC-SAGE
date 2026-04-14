#!/usr/bin/env python3
"""Probe L3 to discover what controls camera/offset scrolling.

Loads cached L1 and L2 solutions to reach L3 start, then inspects state:
 - grid.cdpcbbnfdp (pixel offset)
 - camera.position (camera.mepgityjcj)
 - piece positions, block positions
 - try push actions in each direction and record offset changes

Goal: understand if the pieces at world (80,20), (68,20), (80,32), (68,32)
required by L3's jumps can be brought into the [0,63] viewport via scrolling,
and what actions trigger that scroll.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

from arc_agi import Arcade
from arcengine import GameAction
import lf52_solve_final as L


def dump_state(label, env, game):
    eq = game.ikhhdzfmarl
    grid = eq.hncnfaqaddg
    off = grid.cdpcbbnfdp
    # Camera position — on eq, not on grid
    cam = eq.xzwdyefmgkv
    cam_pos = cam.mepgityjcj()
    cam_csx = cam.tnxxzczblvt
    cam_csy = cam.ppoluxgtqul
    # Pieces
    pieces = []
    for p in grid.ndtvadsrqf("fozwvlovdui"):
        pieces.append((p.grid_x, p.grid_y, p.name))
    # Blocks
    blocks = []
    for b in grid.whdmasyorl("hupkpseyuim2"):
        blocks.append((b.grid_x, b.grid_y))
    print(f"[{label}]")
    print(f"  grid offset (cdpcbbnfdp) = {off}")
    print(f"  camera position = {cam_pos}, cell_size = ({cam_csx}, {cam_csy})")
    print(f"  pieces = {pieces}")
    print(f"  blocks = {blocks}")
    print(f"  level = {eq.whtqurkphir}, steps = {eq.asqvqzpfdi}")
    return {
        'offset': off,
        'cam_pos': cam_pos,
        'cell_size': (cam_csx, cam_csy),
        'pieces': pieces,
        'blocks': blocks,
        'level': eq.whtqurkphir,
    }


def drain_animation(env, max_frames=50):
    """Drain pending animation without making a real action.
    A short burst of ACTION1 is used to progress frames — or we can call
    the engine's step method directly. Simplest: press ACTION1, which the
    engine handles as a no-op during animation."""
    for _ in range(max_frames):
        fd = env.step(GameAction.ACTION1)
        if fd.state.name != 'NOT_FINISHED':
            return fd
        eq = env._game.ikhhdzfmarl
        # If animation done (no pending frames), break
        # Actually easier: just run the first step — we can't easily check.
        # This function is suspect — let's just do 1 action per scroll test.
        break
    return fd


def main():
    arcade = Arcade()
    env = arcade.make('lf52-271a04aa')
    obs = env.reset()
    game = env._game

    # Load cached solutions
    sol_path = os.path.join(os.path.dirname(__file__), '..', '..',
                            'knowledge', 'visual-memory', 'lf52', 'solutions.json')
    with open(sol_path) as f:
        solutions = json.load(f)

    print(f"Loaded {len(solutions)} level solutions")

    action_map = {0: GameAction.RESET, 1: GameAction.ACTION1, 2: GameAction.ACTION2,
                  3: GameAction.ACTION3, 4: GameAction.ACTION4, 5: GameAction.ACTION5,
                  6: GameAction.ACTION6, 7: GameAction.ACTION7}

    # Replay L1, L2 to reach L3 start
    for level_idx in [0, 1]:
        print(f"\n--- Replaying L{level_idx+1} ({len(solutions[level_idx])} steps) ---")
        for step in solutions[level_idx]:
            action = action_map[step['action']]
            data = step.get('data')
            fd = env.step(action, data=data)
            if fd.levels_completed > level_idx:
                print(f"  L{level_idx+1} solved, levels_completed={fd.levels_completed}")
                break

    # Now at start of L3
    # The eq object may be stale — re-fetch
    game = env._game
    print("\n=== L3 START ===")
    s0 = dump_state("L3 initial", env, game)

    # L3 solution first four clicks are OOB: (80,20), (68,20), (80,32), (68,32)
    # These are world-coord clicks that must be scrolled into [0,63]
    # Current offset = (5,5) (default). World pixel for grid cell (x,y) = (x*6+5, y*6+5)
    # So world 80 = grid 12 or 13. World 68 = grid 10 or 11.
    # First OOB click (80, 20) corresponds to piece at grid (13, 2) or (12, 3)?
    # Let's just compute: world 80 -> (80-5)/6 = 12.5, so grid col 12 or 13.
    # If grid offset becomes e.g. (-37, 5), then world 80 -> click y = 80 - (-37) = 117 (still OOB).
    # If offset becomes (-50, 5): click x = 80 - (-50) = 130 (still OOB).
    # For x=80 to land in [0,63], we need offset[0] such that 80 - offset[0] in [0,63]
    # => offset[0] in [17, 80].
    # But the problem is: the click formula in the solver is px = sx*6 + off[0] + 3.
    # So px changes when offset changes. Moving offset[0] from 5 to 17 would shift
    # click_x from 80 to 80-(17-5)*1... wait let me re-read.
    # Solver: px = sx*6 + off[0] + 3.  If sx=13, off[0]=5: px=13*6+5+3=86. Hmm.
    # If sx=12: px=72+5+3=80. So grid col 12, offset (5,5) produces x=80.
    # For this to be in [0,63], need 12*6 + off[0] + 3 <= 63
    # => off[0] <= -12
    # Try pushing directions. Each push may shift cdpcbbnfdp.

    # Try UP
    print("\n--- Try ACTION1 (UP) ---")
    fd = env.step(GameAction.ACTION1)
    dump_state("after UP", env, game)

    # Try DOWN
    print("\n--- Try ACTION2 (DOWN) ---")
    fd = env.step(GameAction.ACTION2)
    dump_state("after DOWN", env, game)

    # Try LEFT
    print("\n--- Try ACTION3 (LEFT) ---")
    fd = env.step(GameAction.ACTION3)
    dump_state("after LEFT", env, game)

    # Try RIGHT
    print("\n--- Try ACTION4 (RIGHT) ---")
    fd = env.step(GameAction.ACTION4)
    dump_state("after RIGHT", env, game)


if __name__ == "__main__":
    main()
