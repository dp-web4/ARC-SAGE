#!/usr/bin/env python3
"""Trace what clicking c does to the board when player is NOT on an itki."""
import os, sys, json
os.chdir("/mnt/c/exe/projects/ai-agents/SAGE")
os.environ['OPERATION_MODE'] = 'offline'
sys.path.insert(0, ".")
sys.stdout.reconfigure(line_buffering=True)

from arc_agi import Arcade
from arcengine import GameAction, InteractionMode
sys.path.insert(0, "arc-agi-3/experiments")
from dc22_solve_final import save_game_state, restore_game_state, player_reachable_cells

VIS = "/mnt/c/exe/projects/ai-agents/shared-context/arc-agi-3/visual-memory/dc22"

def replay_to_L6(env):
    with open(f"{VIS}/solutions.json") as f:
        raw = json.load(f)
    am = {1: GameAction.ACTION1, 2: GameAction.ACTION2,
          3: GameAction.ACTION3, 4: GameAction.ACTION4,
          6: GameAction.ACTION6}
    for lvl_idx in range(5):
        for m in raw[lvl_idx]:
            env.step(am[m['action']], data=m.get('data', {}))

def snapshot_c_tagged(game):
    out = []
    for s in game.current_level.get_sprites():
        if 'c' in s.tags and s.interaction != InteractionMode.REMOVED:
            out.append((s.name, s.x, s.y, s.interaction.name))
    return sorted(out)

def snapshot_all_interactive(game):
    """All non-bg, non-removed sprites with their interaction mode."""
    out = []
    for s in game.current_level.get_sprites():
        if s.interaction == InteractionMode.REMOVED:
            continue
        if s.name.startswith('bg'):
            continue
        out.append((s.name, s.x, s.y, s.interaction.name, s.is_visible, s.is_collidable))
    return sorted(out)

def diff_lists(a, b):
    sa = set(a); sb = set(b)
    added = sorted(sb - sa)
    removed = sorted(sa - sb)
    return added, removed

def main():
    arcade = Arcade(operation_mode='offline')
    env = arcade.make('dc22-4c9bff3e')
    env.reset()
    replay_to_L6(env)
    game = env._game

    print("=== Before click c ===")
    before_c = snapshot_c_tagged(game)
    for x in before_c: print(f"  {x}")
    before_all = snapshot_all_interactive(game)

    # Click jpug-bjuk (letter c) from initial player position
    # jpug-bjuk center is at (45+13//2, 23+5//2) = (51, 25)
    fd = env.step(GameAction.ACTION6, data={'x': 51, 'y': 25})
    print(f"\nAfter click c: state={fd.state.name}, steps={game.step_counter_ui.rdnpeqedga}")
    print(f"Player: ({game.fdvakicpimr.x},{game.fdvakicpimr.y})")

    after_c = snapshot_c_tagged(game)
    print("\n=== After click c ===")
    for x in after_c: print(f"  {x}")

    after_all = snapshot_all_interactive(game)
    added, removed = diff_lists(before_all, after_all)
    print(f"\n=== Full board diff ===")
    print("Added:"); [print(f"  +{x}") for x in added]
    print("Removed:"); [print(f"  -{x}") for x in removed]

    # Now check player reach
    parents = player_reachable_cells(game)
    print(f"\nReach after c-click: {len(parents)} cells")
    for y in sorted(set(p[1] for p in parents.keys())):
        xs = sorted(x for x,yy in parents.keys() if yy==y)
        print(f"  y={y}: {xs}")

    # Click c again to see if it reverts
    fd = env.step(GameAction.ACTION6, data={'x': 51, 'y': 25})
    print(f"\nAfter second click c: state={fd.state.name}")
    after_c2 = snapshot_c_tagged(game)
    for x in after_c2: print(f"  {x}")
    parents2 = player_reachable_cells(game)
    print(f"Reach after 2nd c-click: {len(parents2)} cells")
    for y in sorted(set(p[1] for p in parents2.keys())):
        xs = sorted(x for x,yy in parents2.keys() if yy==y)
        print(f"  y={y}: {xs}")

if __name__ == "__main__":
    main()
