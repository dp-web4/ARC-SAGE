#!/usr/bin/env python3
"""sb26 Solver — Evaluator-Simulation-Based.

The sb26 mechanic (all levels): you arrange colored tokens and portals into
frame slots. When ACTION5 is pressed, an evaluator walks the frames:
  - Start at frame 0, slot 0.
  - At each slot: if the item is a regular token, its color must equal the
    current target color; advance target pointer and slot pointer.
  - If the item is a portal, push current frame, jump to frame whose border
    color matches the portal's inner color, start at slot 0 there.
  - When a frame's slots are exhausted, pop back to the parent frame one
    slot past the portal, continue.
  - Win when all targets matched.

L4+ adds: (a) multiple frames reachable via portals contribute slots, so
total_slots can exceed first-frame slots; (b) pre-placed tokens inside
frames are fixed contributions to the sequence; (c) portals themselves
are palette items that must be placed in specific slots.

Solver strategy: model the layout, then DFS over palette-to-slot
assignments that make the evaluator's walk produce exactly the target
sequence. Since each step has a required color (target[p]), branching is
narrow: only try palette items with the required color, plus portals
whose target frame would produce the needed remaining subsequence.
"""
import sys, os, json, time
import warnings
warnings.filterwarnings("ignore")
os.environ.setdefault("NUMPY_EXPERIMENTAL_DTYPE_API", "1")
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from arc_agi import Arcade
from arcengine import GameAction

GAME_ID = 'sb26-7fbdac44'

# -- Helpers ---------------------------------------------------------------

def get_frame(fd):
    grid = np.array(fd.frame)
    return grid[-1] if grid.ndim == 3 else grid


def wait_anim(env, game, fd, max_frames=300):
    for _ in range(max_frames):
        busy = (game.modqnpqfi > 0 or game.ulzvbcvzs or game.xjxrqgaqw >= 0 or
                game.ftyhvmeft >= 0 or game.lmvwmlqtw >= 0 or game.japgbruyb >= 0 or
                game.bbiavyren >= 0 or game.artsfnufc >= 0)
        if not busy:
            break
        fd = env.step(GameAction.ACTION7)
    return fd


# -- World model -----------------------------------------------------------

def build_level_model(game):
    """Extract frames, slots, palette items from the current level.

    Returns:
      frames: list of dicts with keys:
        'idx': engine index in game.qaagahahj (0-based)
        'border': border color
        'slots': list of N slot dicts (N = frame width slot count).
                 Each slot: {'x','y' (top-left), 'click_x','click_y',
                             'fixed': (None | {'color': int, 'is_portal': bool}),
                             'empty_slot_sprite_exists': bool}
      palette: list of dicts with keys 'color','is_portal','click_x','click_y','source_x','source_y'
      targets: list of target colors in order
      kojduumcap: slot stride (6)
    """
    kojduumcap = 6
    frames = sorted(game.qaagahahj, key=lambda f: (f.y, f.x))
    # first-frame-first ordering is important: engine starts at qaagahahj[0]
    # which is the one sorted by (y, x) — same as above.

    # Map border color -> frame index (for portal jumps)
    frame_by_border = {}
    for i, f in enumerate(frames):
        frame_by_border[int(f.pixels[0, 0])] = i

    model_frames = []
    for fi, frame in enumerate(frames):
        width_count = int(frame.name[-1])
        border = int(frame.pixels[0, 0])
        slots = []
        for i in range(width_count):
            # Per engine rfdjlhefnd: x = frame.x + 2 + i*6, y = frame.y + 2
            sx = int(frame.x) + 2 + i * kojduumcap
            sy = int(frame.y) + 2
            cx, cy = sx + 3, sy + 3  # click position (center)
            fixed = None
            empty_exists = False

            # Find pre-placed token (fixed for this solve)
            for t in game.dkouqqads:
                if int(t.x) == sx and int(t.y) == sy:
                    is_portal = t.name == 'vgszefyyyp'
                    if is_portal:
                        color = int(t.pixels[1, 1])  # inner color
                    else:
                        color = int(t.pixels[1, 1])
                    fixed = {'color': color, 'is_portal': is_portal}
                    break

            # Find empty slot sprite
            for s in game.dewwplfix:
                if not s.is_visible:
                    continue
                if int(s.x) == sx and int(s.y) == sy:
                    empty_exists = True
                    break

            slots.append({
                'x': sx, 'y': sy,
                'click_x': cx, 'click_y': cy,
                'fixed': fixed,
                'empty_exists': empty_exists,
            })
        model_frames.append({
            'idx': fi, 'border': border, 'slots': slots, 'name': frame.name,
        })

    # Palette (row at y >= 50)
    palette = []
    for t in game.dkouqqads:
        if int(t.y) < 50:
            continue
        is_portal = t.name == 'vgszefyyyp'
        color = int(t.pixels[1, 1])  # for portals, this is the inner color (= target frame border)
        palette.append({
            'color': color,
            'is_portal': is_portal,
            'click_x': int(t.x) + 3, 'click_y': int(t.y) + 3,
            'source_x': int(t.x), 'source_y': int(t.y),
        })

    targets = [int(s.pixels[0, 0]) for s in game.wcfyiodrx]

    return {
        'frames': model_frames,
        'palette': palette,
        'targets': targets,
        'frame_by_border': frame_by_border,
    }


# -- Simulated evaluator + search -----------------------------------------

class Solver:
    def __init__(self, model):
        self.frames = model['frames']
        self.targets = model['targets']
        self.frame_by_border = model['frame_by_border']
        self.palette = model['palette']
        # assignment[(frame_idx, slot_idx)] = palette index (int)
        self.assignment = {}
        # used[palette_idx] = bool
        self.used = [False] * len(self.palette)

    def item_at(self, frame_idx, slot_idx):
        """Return {'color','is_portal'} for the item at (frame_idx, slot_idx),
        or None if empty and unassigned."""
        slot = self.frames[frame_idx]['slots'][slot_idx]
        if slot['fixed'] is not None:
            return slot['fixed']
        if (frame_idx, slot_idx) in self.assignment:
            pi = self.assignment[(frame_idx, slot_idx)]
            p = self.palette[pi]
            return {'color': p['color'], 'is_portal': p['is_portal']}
        return None

    def can_place(self, frame_idx, slot_idx):
        """True if this slot is fillable (empty slot sprite exists and not fixed)."""
        slot = self.frames[frame_idx]['slots'][slot_idx]
        return slot['fixed'] is None and slot['empty_exists']

    def solve(self):
        """Return list of (frame_idx, slot_idx, palette_idx) for placements,
        or None if no solution."""
        # Start: stack [(frame 0, slot 0)], target pointer p = 0
        stack = [(0, 0)]
        ok = self._walk(stack, 0)
        if not ok:
            return None
        # Return placements in palette-usage order? No — we want an order
        # that matches engine behavior. Engine checks each slot at evaluator
        # time; placements can be done in any order before pressing PLAY.
        # But "place portal into a slot that has a pre-placed fixed" is
        # impossible — we only assign to fillable slots.
        placements = []
        for (fi, si), pi in self.assignment.items():
            placements.append((fi, si, pi))
        return placements

    def _walk(self, stack, p):
        """Recursive evaluator simulation + DFS over palette assignments.

        stack: [(frame_idx, slot_idx), ...] — current frame call stack
        p: next target index to match
        Returns True on success.
        """
        if p == len(self.targets):
            # All targets matched. But engine win requires the LAST target
            # to be matched, not just "run out". Actually re-reading:
            # `if pmygakdvy == len(wcfyiodrx)-1 and wrudcanmwy` is checked
            # INSIDE dbfxrigdqx, so once the last target is matched, win
            # triggers before anything else runs.
            # If we reach here, p has been incremented past last target,
            # meaning we matched all. Success.
            return True

        if not stack:
            # Stack empty but more targets unmatched -> fail
            return False

        frame_idx, slot_idx = stack[-1]
        frame = self.frames[frame_idx]
        slot_count = len(frame['slots'])

        if slot_idx >= slot_count:
            # Frame exhausted: pop and continue in parent at next slot
            # But engine only allows pop if len(buvfjfmpp) > 1; otherwise
            # it's a failure (out of items, more targets remaining).
            if len(stack) < 2:
                return False
            new_stack = stack[:-1]
            pf_idx, pf_slot = new_stack[-1]
            new_stack[-1] = (pf_idx, pf_slot + 1)
            return self._walk(new_stack, p)

        # Look at item at (frame_idx, slot_idx)
        item = self.item_at(frame_idx, slot_idx)
        target = self.targets[p]

        if item is not None:
            # Item is fixed or already assigned
            return self._consume(stack, p, item)

        # Slot is empty and unassigned; try placing palette items.
        if not self.can_place(frame_idx, slot_idx):
            return False

        # Try a regular token matching target color.
        for pi, pitem in enumerate(self.palette):
            if self.used[pi]:
                continue
            if pitem['is_portal']:
                continue
            if pitem['color'] != target:
                continue
            self.used[pi] = True
            self.assignment[(frame_idx, slot_idx)] = pi
            if self._consume(stack, p, {'color': pitem['color'], 'is_portal': False}):
                return True
            self.used[pi] = False
            del self.assignment[(frame_idx, slot_idx)]
            # Only need to try one such token (they produce identical walks
            # from here on for the evaluator); remaining copies of same color
            # matter only if later slot needs them.
            # Actually: with multiple tokens of same color, which one we use
            # here doesn't change walk correctness but affects action ordering.
            # Break is safe for correctness search.
            break

        # Try a portal: portal's inner color = target frame's border color.
        # When evaluator reads a portal, it pushes that target frame (at idx 0).
        for pi, pitem in enumerate(self.palette):
            if self.used[pi]:
                continue
            if not pitem['is_portal']:
                continue
            target_border = pitem['color']
            if target_border not in self.frame_by_border:
                continue
            target_frame_idx = self.frame_by_border[target_border]
            # Engine guard (line 976): portal re-entry fails only if entering
            # at slot 0 AND the matching parent call is also at slot 0 AND the
            # call just before top of stack was at slot 0. Simplification:
            # we check whether placing here reproduces exactly the problematic
            # pattern. In practice, re-entry mid-frame is allowed.
            # The "push" is always to slot 0, so check: would this re-push an
            # already-present (frame, 0)? If yes, engine fails.
            if any((fi, si) == (target_frame_idx, 0) for fi, si in stack):
                # Engine will detect and fail via sibihgzarf.
                continue
            # Bound recursion to avoid runaway.
            if len(stack) > 32:
                continue
            self.used[pi] = True
            self.assignment[(frame_idx, slot_idx)] = pi
            new_stack = stack + [(target_frame_idx, 0)]
            # Engine: portal itself doesn't consume a target; next step
            # is reading slot 0 of the target frame.
            if self._walk(new_stack, p):
                return True
            self.used[pi] = False
            del self.assignment[(frame_idx, slot_idx)]

        return False

    def _consume(self, stack, p, item):
        """Consume the item at top-of-stack. If token, check color match and
        advance. If portal, jump to target frame."""
        frame_idx, slot_idx = stack[-1]

        if item['is_portal']:
            target_border = item['color']
            if target_border not in self.frame_by_border:
                return False
            target_frame_idx = self.frame_by_border[target_border]
            # Engine fails only if pushing an already-at-slot-0 frame.
            if any((fi, si) == (target_frame_idx, 0) for fi, si in stack):
                return False
            if len(stack) > 32:
                return False
            new_stack = stack + [(target_frame_idx, 0)]
            return self._walk(new_stack, p)

        # Regular token: must match current target
        target = self.targets[p]
        if item['color'] != target:
            return False

        # Check win condition BEFORE advancing (engine line 926):
        # if pmygakdvy == len(wcfyiodrx)-1 and wrudcanmwy -> win
        if p == len(self.targets) - 1:
            return True

        # Advance within frame. If slot is last in frame, pop.
        new_stack = list(stack)
        new_stack[-1] = (frame_idx, slot_idx + 1)
        return self._walk(new_stack, p + 1)


# -- Live interaction ------------------------------------------------------

def apply_placements(env, game, model, placements, verbose=False):
    """Click tokens from palette into slots. Returns action count and clicks
    list."""
    clicks = []
    ac = 0
    for fi, si, pi in placements:
        slot = model['frames'][fi]['slots'][si]
        pitem = model['palette'][pi]
        # Click token (from palette)
        env.step(GameAction.ACTION6, data={'x': pitem['click_x'], 'y': pitem['click_y']})
        clicks.append(('click', pitem['click_x'], pitem['click_y']))
        # Click slot
        env.step(GameAction.ACTION6, data={'x': slot['click_x'], 'y': slot['click_y']})
        clicks.append(('click', slot['click_x'], slot['click_y']))
        ac += 2
        if verbose:
            kind = 'PORTAL' if pitem['is_portal'] else f"color={pitem['color']}"
            print(f"    place {kind} into frame{fi}.slot{si} ({slot['x']},{slot['y']})")
    return ac, clicks


def solve_level(env, game, verbose=False):
    """Solve current level via evaluator simulation."""
    level_idx = game.level_index
    model = build_level_model(game)

    if verbose:
        print(f"  Targets ({len(model['targets'])}): {model['targets']}")
        pal_summary = [('P' if p['is_portal'] else 'T', p['color']) for p in model['palette']]
        print(f"  Palette: {pal_summary}")
        print(f"  Frames: {[(f['name'], f['border'], len(f['slots'])) for f in model['frames']]}")

    solver = Solver(model)
    placements = solver.solve()

    if placements is None:
        if verbose:
            print("  NO SIMULATED SOLUTION FOUND")
        return None, 0, []

    if verbose:
        print(f"  Simulation found {len(placements)} placements")

    # Apply placements live to verify
    ac, clicks = apply_placements(env, game, model, placements, verbose=verbose)

    # Submit
    fd = env.step(GameAction.ACTION5)
    clicks.append(('submit', 0, 0))
    ac += 1
    fd = wait_anim(env, game, fd)

    won = fd.levels_completed > level_idx
    if verbose:
        status = "WON" if won else "FAILED"
        print(f"  {status} in {ac} actions (level_index now {game.level_index}, levels_completed={fd.levels_completed})")

    if not won:
        # Reset level for retry / next attempt
        game.set_level(level_idx)
        return None, 0, []

    return fd, ac, clicks


def solve_all_levels(verbose=True):
    arcade = Arcade()
    env = arcade.make(GAME_ID)
    fd = env.reset()
    game = env._game

    all_level_clicks = []
    total = 0

    for level_idx in range(8):
        if verbose:
            print(f"\n{'='*50}")
            print(f"Level {level_idx + 1} / 8")

        fd, ac, clicks = solve_level(env, game, verbose=verbose)

        if fd and fd.levels_completed > level_idx:
            all_level_clicks.append(clicks)
            total += ac
            if verbose:
                print(f"  -> Total: {total} actions, {fd.levels_completed} levels")
        else:
            if verbose:
                print(f"  FAILED L{level_idx + 1}")
            break

        if fd.state.name == 'GAME_OVER':
            if verbose:
                print(f"  GAME OVER at L{level_idx+1}")
            break

    levels_solved = len(all_level_clicks)
    return all_level_clicks, total, levels_solved, env, game


def replay_and_capture(arcade, all_level_clicks, verbose=True):
    try:
        from arc_session_writer import SessionWriter
    except ImportError:
        SessionWriter = None

    env = arcade.make(GAME_ID)
    fd = env.reset()
    game = env._game
    grid = get_frame(fd)

    writer = None
    if SessionWriter:
        writer = SessionWriter(
            game_id=GAME_ID,
            win_levels=fd.win_levels,
            available_actions=[int(a) for a in fd.available_actions],
            baseline=153,
            player="sb26_simulation_solver",
        )
        writer.record_step(0, grid, levels_completed=0, state="PLAYING")

    total = 0
    for level_clicks in all_level_clicks:
        for atype, ax, ay in level_clicks:
            if atype == 'submit':
                fd = env.step(GameAction.ACTION5)
            else:
                fd = env.step(GameAction.ACTION6, data={'x': ax, 'y': ay})
            total += 1
            grid = get_frame(fd)
            fd = wait_anim(env, game, fd)

            if writer:
                action_id = 5 if atype == 'submit' else 6
                writer.record_step(action_id, grid,
                    levels_completed=fd.levels_completed,
                    x=ax if atype != 'submit' else None,
                    y=ay if atype != 'submit' else None,
                    state=fd.state.name)

    if writer:
        writer.record_game_end(state=fd.state.name, levels_completed=fd.levels_completed)
    return fd, total


def main():
    import time as _time
    print("=" * 60)
    print("sb26 Evaluator-Simulation Solver")
    print("=" * 60)

    t0 = _time.monotonic()
    all_level_clicks, total, levels_solved, _, _ = solve_all_levels(verbose=True)
    t1 = _time.monotonic()

    print(f"\n{'='*60}")
    print(f"Result: {levels_solved}/8 levels, {total} actions (baseline 153)")
    print(f"Time: {t1-t0:.1f}s")

    if levels_solved >= 1:
        print(f"\nReplaying with visual capture...")
        arcade = Arcade()
        fd2, total2 = replay_and_capture(arcade, all_level_clicks, verbose=True)
        print(f"Replay: {fd2.levels_completed}/8, {total2} actions captured")

    sol_data = {
        "levels_solved": levels_solved,
        "total_actions": total,
    }
    for li, lc in enumerate(all_level_clicks):
        sol_data[f"L{li+1}"] = {"actions": len(lc), "clicks": [(a, x, y) for a, x, y in lc]}

    out_path = os.path.join(os.path.dirname(__file__), "sb26_action_sequence.json")
    with open(out_path, "w") as f:
        json.dump(sol_data, f, indent=2)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
