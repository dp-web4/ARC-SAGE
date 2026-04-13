"""Full reachability analysis for L7: exhaustive BFS over (pieces, blocks, pegs)
state, track ALL jump-reachable piece positions for each piece.

Key question: can any piece reach (8,8)? That's the first scroll trigger.
If yes, test whether scroll+continue opens up new connectivity.
"""
import os
os.chdir("/mnt/c/exe/projects/ai-agents/SAGE")
os.environ['OPERATION_MODE'] = 'offline'
import arc_agi
from arcengine import GameAction
from collections import deque
import time

import sys
sys.path.insert(0, '/mnt/c/exe/projects/ai-agents/ARC-SAGE/arc-agi-3/experiments')
from lf52_solve_final import extract_state, make_puzzle_state, PuzzleState


def reachable_piece_positions(ps_init: PuzzleState, time_limit=60):
    """BFS over (pieces, blocks, pegs) state. Track set of positions each
    piece label has ever occupied."""
    visited = set()
    # Collect: for each piece type (N1/N2/R), all positions reached
    positions = {}
    landings_reached = set()

    start = ps_init.key()
    visited.add(start)
    queue = deque([ps_init])
    t0 = time.time()

    # Identify pieces by their initial positions
    # For L7: N@(0,1), R@(6,1), N@(22,6)
    # Track each uniquely

    jump_configs_seen = set()  # (jumper_pos, middle_pos, landing_pos, jumper_name)

    while queue and time.time() - t0 < time_limit:
        ps = queue.popleft()
        # Record positions
        for x, y, name in ps.pieces:
            positions.setdefault(name, set()).add((x, y))
            landings_reached.add((x, y))

        # Record all valid jumps from here
        jumps = ps.get_valid_jumps()
        for src, dst in jumps:
            # find middle
            mx, my = (src[0]+dst[0])//2, (src[1]+dst[1])//2
            jumper_name = ps.piece_dict().get(src, '?')
            jump_configs_seen.add((src, (mx,my), dst, jumper_name))

            # apply the jump
            new_pieces = set()
            for x, y, name in ps.pieces:
                if (x, y) == src:
                    new_pieces.add((dst[0], dst[1], name))
                elif (x, y) == (mx, my):
                    # removed if same name as jumper (non-blue N-over-N or R-over-R)
                    if name == jumper_name and 'blue' not in name:
                        continue  # removed
                    new_pieces.add((x, y, name))
                else:
                    new_pieces.add((x, y, name))
            new_ps = PuzzleState(frozenset(new_pieces), ps.blocks, ps.walls,
                                  ps.walkable, ps.fixed_pegs)
            k = new_ps.key()
            if k not in visited:
                visited.add(k)
                queue.append(new_ps)

        # Try all 4 pushes
        for direction in [(-1,0),(1,0),(0,-1),(0,1)]:
            new_ps = ps.apply_push(direction)
            if new_ps is None:
                continue
            k = new_ps.key()
            if k not in visited:
                visited.add(k)
                queue.append(new_ps)

    return positions, landings_reached, jump_configs_seen, len(visited), time.time() - t0


def main():
    arcade = arc_agi.Arcade(operation_mode='offline')
    env = arcade.make('lf52-271a04aa')
    env.reset()
    g = env._game
    g.set_level(6)
    eq = g.ikhhdzfmarl
    state_dict = extract_state(eq)
    ps = make_puzzle_state(state_dict)
    print(f"Initial pieces: {sorted(ps.pieces)}")
    print(f"Initial blocks: {sorted(ps.blocks)}")
    print(f"Walkable cells: {len(ps.walkable)}")

    # Small time limit — we want a characterization, not exhaustive
    positions, landings, jumps_seen, n_states, elapsed = reachable_piece_positions(ps, time_limit=60)
    print(f"\nExplored {n_states} states in {elapsed:.1f}s")
    print(f"Total unique piece positions: {len(landings)}")
    print(f"Total unique jump configurations: {len(jumps_seen)}")

    # Group positions by column to see right-side reachability
    by_col = {}
    for (x, y) in landings:
        by_col.setdefault(x, set()).add(y)
    print("\nPiece positions by column:")
    for col in sorted(by_col):
        print(f"  col {col}: rows {sorted(by_col[col])}")

    # Key: does any piece reach (8, 8)?
    if (8, 8) in landings:
        print(f"\n!!! (8, 8) IS REACHABLE !!!")
    else:
        print(f"\n(8, 8) NOT reachable under push+jump only")

    # Does any piece reach col 16, 17, ..., 22?
    for target_col in range(15, 23):
        if target_col in by_col:
            print(f"Col {target_col} reachable: rows {sorted(by_col[target_col])}")


if __name__ == '__main__':
    main()
