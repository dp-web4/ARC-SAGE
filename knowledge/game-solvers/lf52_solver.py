#!/usr/bin/env python3
"""
lf52 Tile-Merging Puzzle Solver

Parses the lf52.py grid definitions and computes click/action sequences
to solve each of the 10 levels.

Game mechanics:
- Grid of 6x6 pixel tiles. Multiple tile types on a scene graph.
- 'x' = green fozwvlovdui tile on open cell
- 'r' = red fozwvlovdui_red tile
- 'b' = blue fozwvlovdui_blue tile (static obstacle in L8+)
- 'o' = jmbixtieild target cell
- '.' = hupkpseyuim open cell
- ',' = hupkpseyuim2 + kraubslpehi (pushable wall cell)
- 'p' = dgxfozncuiz portal on open cell
- Wall chars: '-','|','L','3','<','>','T','t' = boundary walls
- ';','?','D','P','7' = special wall+push/portal combos

Interactions:
- ACTION6(x,y) = CLICK at pixel coords
  - Click a tile: selects it, shows directional arrows
  - Click an arrow: slides selected tile 2 grid cells in that direction
    If a same-colored tile is at the midpoint, they merge (midpoint tile removed)
  - Validity: intermediate cell needs a fozwvlovdui or dgxfozncuiz,
              destination cell must be empty hupkpseyuim
- ACTION1-4 = UP/DOWN/LEFT/RIGHT: moves all hupkpseyuim2 tiles simultaneously
- ACTION7 = UNDO

Win: all non-blue fozwvlovdui tiles merged to 1 (L1-5,8-10) or 2 (L6-7: green+red).

The solver uses BFS over tile positions to find merge sequences.
Grid coord -> display coord: px = gx*6 + cam_offset_x + 3, py = gy*6 + cam_offset_y + 3

Usage:
    python lf52_solver.py [--level N]
"""

import sys
import argparse
from collections import deque
from typing import Dict, List, Optional, Tuple, Set, FrozenSet


# ---------------------------------------------------------------------------
# Grid definitions (from source kciatvszkc dict)
# ---------------------------------------------------------------------------

GRIDS = {
    1: [
        "",
        ".......",
        ".xx.x..",
        ".....x.",
        "    ...",
        "    .x.",
        "    ...",
        "    ...",
    ],
    2: [
        "....... ",
        ".xx.x.x->",
        "....... |",
        "        |",
        " <--,---3",
        " |      ",
        " |    ..",
        " L----x.",
    ],
    3: [
        ".. ..     ..",
        ".x .x-,--x..",
        ".x.x      .xx.",
        "..x.      ..",
        "          .xx.",
        "      <-> ..",
        "      | | x..",
        ".x.x-,3 L-.x",
        "...       ..",
    ],
    4: [
        "",
        "",
        ".......",
        ".xp.p.x-,---x...x.",
        ".......     .p..p.",
        "            ......",
        "            .p..p.",
        "        <---,..p..",
        "        |",
        "    .x. | ",
        "   .p p.p..",
        "   .----,-.",
        "   .p p....",
        "    .x.",
    ],
    5: [
        " -,-T-P-      ..p..x",
        "    |        <---T-P>",
        " ...|  <--> .|...|. |",
        " xp.|.x|  Lx.|.p.|..|",
        " ...|  |    .|..p|x.|",
        "    |  |     L---t--3",
        "  <-t--3       .",
        "  |            p",
        "  |           ..x",
    ],
    6: [
        "",
        " ....         ....   ",
        " .r..         .x.........>. ",
        " .x..         p..p     p |x",
        " ....         |  |    .?.|.",
        " ......       |  |    x| |",
        " ......,,-----t--3  ...L-3",
        " x.....             x",
        "   x                .",
    ],
    7: [
        "                 <--->",
        "x     r    <-->  |   |",
        "p     p    |  ; <tTPTt>",
        "L--T--3  <-t-p. | D D |",
        "   |     |    .   | | ;",
        " <-t-,> <t->  .p.p. | .",
        " |    | |  |  .p.p.   x",
        " p    p L->p           ",
        " .p.p.....3.",
    ],
    8: [
        "       ",
        "",
        " ........",
        " xp...p..",
        " ......p.",
        "<-p...p..",
        "|...b....",
        "|...b...x",
        "|       |",
        "L-,>   <3",
        "   |   ;",
        " ......bb",
        " L--P,P-3",
    ],
    9: [
        "       ",
        "           x..p.p......",
        "  ..b..    .........bb.",
        "  ...b.    .p.....p.p..",
        "  .....              ..",
        "  ....,--------------..",
        "  xb..   ",
        "  .b..x  ",
    ],
    10: [
        "   .x. ",
        "<-T-T-T->",
        "| ; ; ; |",
        "| L-t-3 |",
        "|       |",
        "| ...bb |",
        "L--b... |",
        "  ..b.. |",
        "  b.... |",
        "  ....x 7",
        "        7",
        "        7",
        "        7",
        "        7",
    ],
}

# Camera offsets per level
CAMERA_OFFSETS = {
    1: (10, 5), 2: (6, 8), 3: (5, 5), 4: (5, 5), 5: (5, 5),
    6: (5, 5), 7: (5, 5), 8: (5, 5), 9: (5, 5), 10: (5, 3),
}

TILE_SIZE = 6
OPEN_CHARS = set("xrbo.p,;DP?7")
TILE_COLORS = {"x": "green", "r": "red", "b": "blue"}
PORTAL_CHARS = set("pPD")
DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
DIR_NAMES = {(0,-1): "UP", (1,0): "RIGHT", (0,1): "DOWN", (-1,0): "LEFT"}


def parse_grid(grid_lines):
    """Parse grid into cells, tiles, open cells."""
    cells = {}
    tiles = []
    open_cells = set()
    for gy, line in enumerate(grid_lines):
        for gx, ch in enumerate(line):
            if ch == ' ':
                continue
            cells[(gx, gy)] = ch
            if ch in TILE_COLORS:
                tiles.append((gx, gy, TILE_COLORS[ch]))
                open_cells.add((gx, gy))
            elif ch in OPEN_CHARS:
                open_cells.add((gx, gy))
    return cells, tiles, open_cells


def grid_to_display(gx, gy, cam_offset):
    """Grid coord -> display pixel coord (center of 6x6 tile)."""
    return (gx * TILE_SIZE + cam_offset[0] + 3,
            gy * TILE_SIZE + cam_offset[1] + 3)


def apply_move(state, tile_to_move, direction, open_cells, cells):
    """Apply click-arrow move: slide tile 2 cells. Merge if same-colored at midpoint."""
    tx, ty, tc = tile_to_move
    dx, dy = direction
    ix, iy = tx + dx, ty + dy  # intermediate
    dest_x, dest_y = tx + dx * 2, ty + dy * 2  # destination

    # Destination must be open and empty
    if (dest_x, dest_y) not in open_cells:
        return None
    for (ttx, tty, ttc) in state:
        if (ttx, tty) == (dest_x, dest_y):
            return None

    # Intermediate must have a tile or be a portal cell
    intermediate_tile = None
    for t in state:
        if t != tile_to_move and (t[0], t[1]) == (ix, iy):
            intermediate_tile = t
            break
    if intermediate_tile is None:
        ch = cells.get((ix, iy), ' ')
        if ch not in PORTAL_CHARS:
            return None

    # Build new state
    new_tiles = set()
    for t in state:
        if t == tile_to_move:
            new_tiles.add((dest_x, dest_y, tc))
        elif (intermediate_tile is not None and t == intermediate_tile
              and t[2] == tc and tc != "blue"):
            continue  # merged
        else:
            new_tiles.add(t)
    return frozenset(new_tiles)


def is_won(state, level_num):
    """Check win condition."""
    non_blue = [t for t in state if t[2] != "blue"]
    if level_num in [6, 7]:
        return len(non_blue) <= 2
    return len(non_blue) <= 1


def bfs_solve(level_num, grid_lines, max_depth=40):
    """BFS to find merge sequence."""
    cells, tiles, open_cells = parse_grid(grid_lines)
    movable_colors = {"green", "red"}
    init_state = frozenset(tiles)

    if is_won(init_state, level_num):
        return []

    visited = set()
    visited.add(init_state)
    queue = deque()
    queue.append((init_state, []))

    while queue:
        state, path = queue.popleft()
        if len(path) >= max_depth:
            continue
        for (tx, ty, tc) in state:
            if tc not in movable_colors:
                continue
            for (dx, dy) in DIRECTIONS:
                new_state = apply_move(state, (tx, ty, tc), (dx, dy),
                                       open_cells, cells)
                if new_state is None or new_state in visited:
                    continue
                visited.add(new_state)
                action = (tx, ty, tc, dx, dy)
                new_path = path + [action]
                if is_won(new_state, level_num):
                    return new_path
                queue.append((new_state, new_path))
    return None


def verify_solution(level_num, grid_lines, solution):
    """Replay solution and verify win."""
    cells, tiles, open_cells = parse_grid(grid_lines)
    state = frozenset(tiles)
    for action in solution:
        tx, ty, tc, dx, dy = action
        tile = (tx, ty, tc)
        if tile not in state:
            print(f"  ERROR: Tile {tile} not found")
            return False
        new_state = apply_move(state, tile, (dx, dy), open_cells, cells)
        if new_state is None:
            print(f"  ERROR: Invalid move {tile} dir=({dx},{dy})")
            return False
        state = new_state
    return is_won(state, level_num)


def moves_to_clicks(solution, cam_offset):
    """Convert solution moves to ACTION6 click sequence."""
    clicks = []
    for (tx, ty, tc, dx, dy) in solution:
        # Click tile to select
        clicks.append(("ACTION6", *grid_to_display(tx, ty, cam_offset)))
        # Click arrow (2 cells away)
        ax, ay = tx + dx * 2, ty + dy * 2
        clicks.append(("ACTION6", *grid_to_display(ax, ay, cam_offset)))
    return clicks


def main():
    parser = argparse.ArgumentParser(description="lf52 Tile-Merging Puzzle Solver")
    parser.add_argument("--level", type=int, default=None)
    args = parser.parse_args()

    print("lf52 Tile-Merging Puzzle Solver")
    print("=" * 60)

    target_levels = [args.level] if args.level else list(range(1, 11))
    all_ok = True

    for lv in target_levels:
        grid_lines = GRIDS[lv]
        cam_offset = CAMERA_OFFSETS[lv]
        cells, tiles, open_cells = parse_grid(grid_lines)
        non_blue = [t for t in tiles if t[2] != "blue"]
        blue = [t for t in tiles if t[2] == "blue"]

        print(f"\nLevel {lv}:")
        print(f"  Camera: {cam_offset}, Tiles: {len(non_blue)} movable, {len(blue)} blue")
        for tx, ty, tc in tiles:
            px, py = grid_to_display(tx, ty, cam_offset)
            print(f"    {tc} at grid({tx},{ty}) -> display({px},{py})")

        max_d = 30 if lv <= 3 else 40
        print(f"  Solving (BFS max_depth={max_d})...")
        solution = bfs_solve(lv, grid_lines, max_d)

        if solution is None:
            print(f"  BFS found no solution (grid may have push corridors)")
            all_ok = False
            continue

        print(f"  Solution: {len(solution)} moves")
        for i, (tx, ty, tc, dx, dy) in enumerate(solution):
            print(f"    {i+1}. {tc}({tx},{ty}) -> {DIR_NAMES[(dx,dy)]}")

        ok = verify_solution(lv, grid_lines, solution)
        status = "VERIFIED OK" if ok else "VERIFICATION FAILED"
        print(f"  {status}")
        if not ok:
            all_ok = False

        clicks = moves_to_clicks(solution, cam_offset)
        print(f"  Click sequence ({len(clicks)} actions):")
        for i, (act, px, py) in enumerate(clicks):
            print(f"    {i+1}: {act}({px},{py})")

    print()
    print("ALL LEVELS VERIFIED OK" if all_ok else "SOME LEVELS NEED PUSH MECHANICS")


if __name__ == "__main__":
    main()
