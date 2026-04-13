#!/usr/bin/env python3
"""Explore from expanded reach after 4 f-clicks.

Walk to various reachable cells, see which ones:
- Step onto zbhi (triggers d/g gate opens)
- Step onto itki (enables teleport)
- Touch anything else notable
"""
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

    # 4 f-clicks to expand reach
    for _ in range(4):
        env.step(GameAction.ACTION6, data={'x': 56, 'y': 8})

    print(f"After 4 f-clicks: player @ ({game.fdvakicpimr.x},{game.fdvakicpimr.y})")
    parents = player_reachable_cells(game)
    print(f"Reach: {len(parents)} cells")
    state_after_f4 = save_game_state(game)

    # Find zbhi, itki, bqxa-related sprites intersecting reach
    print("\n=== Interesting sprites in reach ===")
    for s in game.current_level.get_sprites():
        if s.interaction == InteractionMode.REMOVED: continue
        if s.name.startswith('bg') or 'path' in s.tags or 'ignore' in s.tags: continue
        for cell in parents:
            cx, cy = cell
            if s.x <= cx < s.x + s.width and s.y <= cy < s.y + s.height:
                pixels = s.render()
                if pixels[cy - s.y][cx - s.x] >= -1:
                    tags = [t for t in s.tags if t in ('zbhi','itki','bqxa','wbze','kbqq','jpug','pressure-plate','bynyvtuepbt-object')]
                    if tags or 'pressure-plate' in s.tags:
                        print(f"  cell ({cx},{cy}) on {s.name} tags={s.tags}")
                        break

    # Test: walk to (8, 58) - far-left staircase
    restore_game_state(game, state_after_f4)
    parents = player_reachable_cells(game)
    if (8, 58) in parents:
        walk = reconstruct_moves(parents, (8, 58))
        for m in walk: env.step(m)
        print(f"\nWalked to (8,58): player at ({game.fdvakicpimr.x},{game.fdvakicpimr.y})")
        parents2 = player_reachable_cells(game)
        print(f"Reach from here: {len(parents2)} cells")
        # Try clicking everything again
        for act_name, cx, cy in [('c', 51, 25), ('f', 56, 8)]:
            s2 = save_game_state(game)
            env.step(GameAction.ACTION6, data={'x': cx, 'y': cy})
            p3 = (game.fdvakicpimr.x, game.fdvakicpimr.y)
            r3 = player_reachable_cells(game)
            print(f"  After click {act_name}: player @ {p3}, reach={len(r3)}")
            restore_game_state(game, s2)

    # Try walking to each cell near the bottom and see what's possible
    restore_game_state(game, state_after_f4)
    bottom_cells = [c for c in parents if c[1] >= 54]
    print(f"\n=== Walking to each bottom cell and checking what's under player ===")
    for cell in sorted(bottom_cells):
        restore_game_state(game, state_after_f4)
        parents = player_reachable_cells(game)
        walk = reconstruct_moves(parents, cell)
        walk_ok = True
        for m in walk:
            fd = env.step(m)
            if fd.state.name == 'LOSE':
                walk_ok = False; break
        if not walk_ok:
            print(f"  {cell}: walk failed")
            continue
        p = (game.fdvakicpimr.x, game.fdvakicpimr.y)
        # Check what sprites player overlaps
        overlaps = []
        for s in game.current_level.get_sprites():
            if s.interaction == InteractionMode.REMOVED: continue
            if s.name.startswith('bg'): continue
            if s.x <= p[0] < s.x + s.width and s.y <= p[1] < s.y + s.height:
                interesting = [t for t in s.tags if t in ('zbhi','itki','pressure-plate','wbze') or len(t)==1]
                if interesting:
                    overlaps.append(f"{s.name}({','.join(interesting)})")
        if overlaps:
            print(f"  cell={cell} player@{p}: {overlaps}")

if __name__ == "__main__":
    main()
