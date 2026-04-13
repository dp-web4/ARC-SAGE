#!/usr/bin/env python3
"""Frame-questioning probe for dc22 L6.

Don't trust the previous claims. Enumerate:
1. ALL sprites by tag, interaction, visibility, and collidability.
2. ALL sys_click sprites (not just jpug+sys_click — look for pure sys_click crane buttons).
3. What happens if we click at (45,35) / (49,31) / (49,39) / (53,35) / (47,17) from initial state.
4. What happens if we click AT THE CRANE BUTTON UI PANEL positions (which might differ from game coords).
5. What happens if we click every visible sys_click target.
6. What is the crane's center right now — does it match any hhxv center?
7. Walk to every reachable cell and re-probe click effects.
"""
import os, sys, json, copy
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

def main():
    arcade = Arcade(operation_mode='offline')
    env = arcade.make('dc22-4c9bff3e')
    env.reset()
    replay_to_L6(env)
    game = env._game

    print(f"\n=== L6 State ===")
    print(f"Player: ({game.fdvakicpimr.x},{game.fdvakicpimr.y})")
    print(f"Goal: ({game.bqxa.x},{game.bqxa.y})")
    print(f"Steps: {game.step_counter_ui.rdnpeqedga}")
    print(f"nxhz: {game.nxhz.name} at ({game.nxhz.x},{game.nxhz.y}) size={game.nxhz.width}x{game.nxhz.height}")
    print(f"nxhz_start: {game.nxhz_start}")
    print(f"nxhz_x={game.nxhz_x} nxhz_y={game.nxhz_y}")
    print(f"uzungcfexgf (hhxv mode): {game.uzungcfexgf}")
    print(f"dzpheqwbxaj: {game.dzpheqwbxaj}")

    # Where is the crane anchor? What hhxv can it grab?
    ax, ay = game.venypzwjkd()
    print(f"\nCrane anchor: ({ax},{ay})")
    print(f"All grabbable hhxv (kelxnkuznz):")
    for s in game.kelxnkuznz():
        cx, cy = s.x + s.width // 2, s.y + s.height // 2
        print(f"  {s.name:25s} ({s.x:3d},{s.y:3d}) {s.width}x{s.height:<3d} center=({cx:3d},{cy:3d}) interaction={s.interaction.name}")

    # List ALL sys_click sprites (any, not just visible)
    print(f"\n=== ALL sys_click sprites (regardless of visibility) ===")
    for s in game.current_level.get_sprites():
        if 'sys_click' not in s.tags:
            continue
        print(f"  {s.name:30s} ({s.x:3d},{s.y:3d}) {s.width}x{s.height:<3d} "
              f"interaction={s.interaction.name:<10s} visible={s.is_visible} collidable={s.is_collidable} tags={s.tags}")

    # What happens when we click each sys_click coord?
    init = save_game_state(game)
    print(f"\n=== Clicking each sys_click sprite center ===")
    sys_click_list = [s for s in game.current_level.get_sprites() if 'sys_click' in s.tags]
    for s in sys_click_list:
        restore_game_state(game, init)
        cx = s.x + s.width // 2
        cy = s.y + s.height // 2
        # camera offset
        cam_h = game.camera._height
        y_offset = (64 - cam_h) // 2
        click_cy = cy + y_offset
        fd = env.step(GameAction.ACTION6, data={'x': cx, 'y': click_cy})
        p_after = (game.fdvakicpimr.x, game.fdvakicpimr.y)
        nx, ny = game.nxhz_x, game.nxhz_y
        attached = game.nxhz_attached_kind
        steps = game.step_counter_ui.rdnpeqedga
        print(f"  click {s.name:30s} @ display({cx:3d},{click_cy:3d}) -> player={p_after} nxhz=({nx},{ny}) att={attached} steps={steps} state={fd.state.name}")

    # Raw click at "UI panel" grid coords that aren't occupied by any known sprite
    restore_game_state(game, init)
    print(f"\n=== Camera info ===")
    print(f"camera.width={game.camera._width}, height={game.camera._height}")
    print(f"display_to_grid((0,0)): {game.camera.display_to_grid(0, 0)}")
    print(f"display_to_grid((63,63)): {game.camera.display_to_grid(63, 63)}")
    print(f"display_to_grid((55,35)): {game.camera.display_to_grid(55, 35)}")
    print(f"display_to_grid((60,35)): {game.camera.display_to_grid(60, 35)}")

    # Reach from start and walk-reach probe
    parents = player_reachable_cells(game)
    print(f"\n=== Initial reach ({len(parents)} cells) ===")
    for y in sorted(set(p[1] for p in parents.keys())):
        xs = sorted(x for x,yy in parents.keys() if yy==y)
        print(f"  y={y}: {xs}")

    # Frame question: is there an `itki-color-cycle` effect we haven't triggered?
    print(f"\n=== itki sprites and their tags ===")
    for s in game.current_level.get_sprites():
        if 'itki' in s.tags and s.interaction != InteractionMode.REMOVED:
            print(f"  {s.name:25s} ({s.x:3d},{s.y:3d}) interaction={s.interaction.name} tags={s.tags}")

    # Check what uqbvwhliqb returns for various sprite names (variant cycling)
    print(f"\n=== Variant cycle map (qmxenejanqe) ===")
    for k, v in game.qmxenejanqe.items():
        print(f"  {k}: {v} variants")

if __name__ == "__main__":
    main()
