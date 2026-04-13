#!/usr/bin/env python3
"""Iterative walk+click experiment. From each new position, try each click and see the reach."""
import os, sys, json
from collections import deque
os.chdir("/mnt/c/exe/projects/ai-agents/SAGE")
os.environ['OPERATION_MODE'] = 'offline'
sys.path.insert(0, ".")
sys.stdout.reconfigure(line_buffering=True)

from arc_agi import Arcade
from arcengine import GameAction, InteractionMode
sys.path.insert(0, "arc-agi-3/experiments")
from dc22_solve_final import save_game_state, restore_game_state, player_reachable_cells, reconstruct_moves

VIS = "/mnt/c/exe/projects/ai-agents/shared-context/arc-agi-3/visual-memory/dc22"

def board_hash(game):
    """Conservative board hash including player pos, all sprite positions and interactions."""
    state = []
    for s in game.current_level.get_sprites():
        if s.interaction == InteractionMode.REMOVED: continue
        state.append((s.name, s.x, s.y, s.interaction.value))
    state.sort()
    return ((game.fdvakicpimr.x, game.fdvakicpimr.y),
            (game.nxhz_x, game.nxhz_y, game.nxhz_attached_kind,
             game.attached_hhxv_prefix, game.attached_hhxv_x, game.attached_hhxv_y),
            tuple(state))

def main():
    arcade = Arcade(operation_mode='offline')
    env = arcade.make('dc22-4c9bff3e')
    env.reset()
    with open(f"{VIS}/solutions.json") as f:
        raw = json.load(f)
    am = {1: GameAction.ACTION1, 2: GameAction.ACTION2, 3: GameAction.ACTION3, 4: GameAction.ACTION4, 6: GameAction.ACTION6}
    for lvl_idx in range(5):
        for m in raw[lvl_idx]:
            env.step(am[m['action']], data=m.get('data', {}))
    game = env._game
    goal = (game.bqxa.x, game.bqxa.y)
    print(f"Goal: {goal}")

    init = save_game_state(game)
    # All visible sys_click sprites - click coords
    click_coords = []
    for s in game.current_level.get_sprites():
        if 'sys_click' in s.tags and s.interaction != InteractionMode.REMOVED and s.is_visible:
            cam_h = game.camera._height
            y_offset = (64 - cam_h) // 2
            cx = s.x + s.width // 2
            cy = s.y + s.height // 2 + y_offset
            click_coords.append((s.name, cx, cy))
    print(f"Click coords: {click_coords}")

    # BFS over (position, board_hash). Actions:
    #  1. Walk to any reachable cell
    #  2. Click each visible sys_click from current position
    # After each transition, recompute reach and hash.
    from collections import deque
    initial_parents = player_reachable_cells(game)
    frontier = deque()
    # state: (moves_list, state_snapshot, reach_parents, board_hash)
    frontier.append(([], init, initial_parents, board_hash(game)))
    visited = {board_hash(game)}
    nodes = 0
    max_nodes = 5000

    # For each position, we also want to track unique (pos, board_sprites) to prune.

    max_reach = len(initial_parents)
    best_sol_here = None

    import time
    t0 = time.time()

    while frontier and nodes < max_nodes:
        moves, saved, reach, bh = frontier.popleft()
        nodes += 1

        if goal in reach:
            # Found it!
            restore_game_state(game, saved)
            walk = reconstruct_moves(reach, goal)
            full = list(moves) + walk
            print(f"SOLUTION FOUND: {len(full)} moves, via walk to goal")
            best_sol_here = full
            break

        # Transition A: click each visible button
        for name, cx, cy in click_coords:
            restore_game_state(game, saved)
            fd = env.step(GameAction.ACTION6, data={'x': cx, 'y': cy})
            if fd.state.name == 'LOSE':
                continue
            if fd.levels_completed > 5:
                print(f"SOLVED by click {name}")
                best_sol_here = list(moves) + [(GameAction.ACTION6, {'x': cx, 'y': cy})]
                break
            bh2 = board_hash(game)
            if bh2 in visited: continue
            visited.add(bh2)
            state2 = save_game_state(game)
            reach2 = player_reachable_cells(game)
            new_moves = list(moves) + [(GameAction.ACTION6, {'x': cx, 'y': cy})]
            if len(reach2) > max_reach:
                max_reach = len(reach2)
                print(f"  [nodes={nodes}] NEW MAX REACH: {max_reach} cells after {len(new_moves)} moves, last click={name}")
                # Print reach ys
                ys = sorted(set(p[1] for p in reach2.keys()))
                for y in ys:
                    xs = sorted(x for x,yy in reach2.keys() if yy==y)
                    print(f"    y={y}: {xs}")
            if goal in reach2:
                print(f"GOAL IN REACH after clicks!")
                best_sol_here = new_moves
                break
            frontier.append((new_moves, state2, reach2, bh2))
        if best_sol_here: break

        # Transition B: walk to each stable kbqq cell in current reach
        # (So the player can be at different positions for subsequent clicks)
        # Only consider cells with different board_hash result — but first walking doesn't change board, just player pos.
        # We only need to try cells where the set of overlapping tile sprites differs (itki/zbhi).
        # To reduce branching: only walk to cells that put player on itki, zbhi, or a qgdz (for foot shifting).
        unique_walk_targets = set()
        for cell in reach:
            if cell == (game.fdvakicpimr.x, game.fdvakicpimr.y): continue
            # Restore game to current state first to probe
            restore_game_state(game, saved)
            px, py = cell
            game.fdvakicpimr.set_position(px, py)
            # Check what's under the player 2x2
            for s in game.current_level.get_sprites():
                if s.interaction == InteractionMode.REMOVED: continue
                if s.x <= px < s.x + s.width and s.y <= py < s.y + s.height:
                    if any(t in s.tags for t in ('itki','zbhi')):
                        unique_walk_targets.add(cell); break
                    if 'f' in s.tags or 'c' in s.tags:  # also walk to stairs cells
                        unique_walk_targets.add(cell); break

        for cell in unique_walk_targets:
            restore_game_state(game, saved)
            # re-get reach in case it was stale
            walk = reconstruct_moves(reach, cell)
            walk_ok = True
            for m in walk:
                fd = env.step(m)
                if fd.state.name == 'LOSE':
                    walk_ok = False; break
                if fd.levels_completed > 5:
                    print(f"SOLVED by walk to {cell}!")
                    best_sol_here = list(moves) + walk
                    break
            if not walk_ok: continue
            if best_sol_here: break
            bh2 = board_hash(game)
            if bh2 in visited: continue
            visited.add(bh2)
            state2 = save_game_state(game)
            reach2 = player_reachable_cells(game)
            new_moves = list(moves) + walk
            if goal in reach2:
                print(f"GOAL IN REACH after walk to {cell}!")
                best_sol_here = new_moves
                break
            frontier.append((new_moves, state2, reach2, bh2))
        if best_sol_here: break

    print(f"\nDone. nodes={nodes}, visited={len(visited)}, max_reach={max_reach}, {time.time()-t0:.1f}s")
    if best_sol_here:
        print(f"Solution length: {len(best_sol_here)}")
        # encode to solutions.json format
        enc = []
        for m in best_sol_here:
            if isinstance(m, tuple):
                enc.append({'action': m[0].value, 'data': m[1]})
            else:
                enc.append({'action': m.value})
        print(json.dumps(enc[:30]))

if __name__ == "__main__":
    main()
