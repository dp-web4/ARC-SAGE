#!/usr/bin/env python3
"""Draw full walkability map of the level — each cell that COULD support a 2x2 player."""
import os, sys, json
os.chdir("/mnt/c/exe/projects/ai-agents/SAGE")
os.environ['OPERATION_MODE'] = 'offline'
sys.path.insert(0, ".")
sys.stdout.reconfigure(line_buffering=True)

from arc_agi import Arcade
from arcengine import GameAction, InteractionMode
sys.path.insert(0, "arc-agi-3/experiments")
from dc22_solve_final import save_game_state, restore_game_state, player_reachable_cells, reconstruct_moves

VIS = "/mnt/c/exe/projects/ai-agents/shared-context/arc-agi-3/visual-memory/dc22"

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
    init = save_game_state(game)

    # For each (x,y) 2x2, check if it would be supported (intangible support)
    # AND check collision (no tangible sprite blocks it)
    from arcengine import Sprite
    player = game.fdvakicpimr

    def support_at(px, py):
        # Restore player to (px, py) and check support
        saved_x, saved_y = player.x, player.y
        player.set_position(px, py)
        supp = game.uxwpppoljm(px, py, player)
        # Also check collision - simulate move to here
        has_collision = False
        for other in game.current_level.get_sprites():
            if other is player: continue
            if game.collides_with(player, other):
                has_collision = True
                break
        player.set_position(saved_x, saved_y)
        return supp, has_collision

    # Try all f-cycle states, print combined walkable map
    def scan_walkable():
        supported = {}
        for y in range(0, 63):
            for x in range(0, 63):
                # Player is 2x2, so (x,y) must be valid top-left
                if x > 62 or y > 62: continue
                supp, coll = support_at(x, y)
                if supp is not None and not coll:
                    supported[(x,y)] = supp.name
        return supported

    print("=== initial walkable cells ===")
    init_walkable = scan_walkable()
    # Print as 64x64 grid (show compressed)
    w = 64; h = 64
    grid = [['.' for _ in range(w)] for _ in range(h)]
    for (x,y), name in init_walkable.items():
        grid[y][x] = '#'
    # Mark player and goal
    grid[game.fdvakicpimr.y][game.fdvakicpimr.x] = 'P'
    grid[game.bqxa.y][game.bqxa.x] = 'G'
    for y in range(h):
        print(''.join(grid[y]))

    # Also print what SPRITES are giving support in uncommon regions (y < 48)
    print("\n=== Walkable cells in y<48 region (top area) ===")
    for (x,y) in sorted(init_walkable.keys()):
        if y < 48:
            print(f"  ({x},{y}) supported by {init_walkable[(x,y)]}")

    print(f"\nTotal walkable: {len(init_walkable)}")

    # Now try with hhxv-dmxj cycled to variant 2 (vertical beam)
    restore_game_state(game, init)
    env.step(GameAction.ACTION6, data={'x': 51, 'y': 25})  # click c
    print("\n=== After c-click (hhxv-dmxj2) walkable cells in y<48 ===")
    walk2 = scan_walkable()
    for (x,y) in sorted(walk2.keys()):
        if y < 48:
            print(f"  ({x},{y}) supported by {walk2[(x,y)]}")
    new_cells = set(walk2.keys()) - set(init_walkable.keys())
    print(f"New walkable cells after c-click: {sorted(new_cells)}")
    removed_cells = set(init_walkable.keys()) - set(walk2.keys())
    print(f"Removed walkable cells: {sorted(removed_cells)}")

if __name__ == "__main__":
    main()
