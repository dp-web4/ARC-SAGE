#!/usr/bin/env python3
"""
BP35 LEGITIMATE CHAIN: continuous replay from L1 through L5.

Goal: capture the FULL LEGITIMATE path — no eq.win() bypass, no OOB clicks.
L1-L4 from run_fixed.json (proven legit). On L5: try every viewport-legal
approach; record what happens; save trace and frames.

Output:
  run.json   — full action log (normalized to offline engine calls)
  frames/    — PNG snapshots at level transitions and L5 probe points
  report.md  — human-readable summary
"""
import sys, os, json
EXPDIR = '/mnt/c/exe/projects/ai-agents/ARC-SAGE/arc-agi-3/experiments'
sys.path.insert(0, EXPDIR)
os.chdir(EXPDIR)  # Arcade expects environment_files/ to be relative to cwd
sys.stdout.reconfigure(line_buffering=True)

from arc_agi import Arcade
from arcengine import GameAction

LEFT = GameAction.ACTION3
RIGHT = GameAction.ACTION4
CLICK = GameAction.ACTION6
UNDO = GameAction.ACTION7

OUTDIR = '/mnt/c/exe/projects/ai-agents/ARC-SAGE/knowledge/visual-memory/bp35/run_legitimate_chain'
os.makedirs(f'{OUTDIR}/frames', exist_ok=True)

# ----------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------
arc = Arcade(operation_mode='offline')
env = arc.make('bp35-0a0ad940')
fd = env.reset()
game = env._game

SYM = {'xcjjwqfzjfe':'W', 'yuuqpmlxorv':'B', 'oonshderxef':'O',
       'ubhhgljbnpu':'^', 'fjlzdjxhant':'*', 'etlsaqqtjvn':'E',
       'lrpkmzabbfa':'G', 'hzusueifitk':'v', 'qclfkhjnaac':'D',
       'aknlbboysnc':'c'}

def engine():
    return env._game.oztjzzyqoek

def player_pos():
    e = engine()
    return tuple(e.twdpowducb.qumspquyus)

def grav_up():
    return engine().vivnprldht

def cam():
    c = engine().camera.rczgvgfsfb
    return (c[0], c[1])

def level():
    return env._game.level_index

def sym_at(x, y):
    items = engine().hdnrlfmyrj.jhzcxkveiw(x, y)
    return SYM.get(items[0].name, '?') if items else '.'

def print_grid(yr=(18, 33), xr=(-1, 12)):
    p = player_pos()
    for y in range(yr[0], yr[1]):
        row = ""
        for x in range(xr[0], xr[1]):
            if (x, y) == p:
                row += 'P'
            else:
                row += sym_at(x, y)
        print(f"    y={y:2d}: {row}")

def in_view(vp_x, vp_y):
    return 0 <= vp_x <= 63 and 0 <= vp_y <= 63

def vp_coords(gx, gy):
    cx, cy = cam()
    return gx * 6 - cx, gy * 6 - cy

# ----------------------------------------------------------------------
# Action wrapper — captures every env.step() call
# ----------------------------------------------------------------------
TRACE = []   # list of step dicts
STEP_I = 0
OOB_COUNT = 0
LAST_LEVEL = 0

def record_step(action, x=None, y=None, note=None, was_oob=False):
    global STEP_I
    STEP_I += 1
    entry = {
        "step": STEP_I,
        "level": level(),
        "action": action,
    }
    if x is not None:
        entry["x"] = x
        entry["y"] = y
    if note:
        entry["note"] = note
    if was_oob:
        entry["oob"] = True
    # Level transition detection
    global LAST_LEVEL
    if entry["level"] != LAST_LEVEL:
        entry["level_up"] = True
        entry["new_level"] = entry["level"]
        LAST_LEVEL = entry["level"]
    TRACE.append(entry)
    return entry

LAST_FD = fd  # seeded from reset

def act_right():
    global LAST_FD
    LAST_FD = env.step(RIGHT)
    record_step("RIGHT")

def act_left():
    global LAST_FD
    LAST_FD = env.step(LEFT)
    record_step("LEFT")

def act_click_vp(vp_x, vp_y, note=None):
    """Click at raw viewport coords. Rejects OOB."""
    global OOB_COUNT, LAST_FD
    if not in_view(vp_x, vp_y):
        OOB_COUNT += 1
        print(f"    [SKIP OOB] click vp=({vp_x},{vp_y}) — out of viewport")
        record_step("CLICK_OOB_SKIPPED", x=vp_x, y=vp_y, note=(note or "OOB rejected"), was_oob=True)
        return False
    LAST_FD = env.step(CLICK, data={"x": vp_x, "y": vp_y})
    record_step("CLICK", x=vp_x, y=vp_y, note=note)
    return True

def act_click_world(gx, gy, note=None):
    """Click at world grid coords (converted to vp based on current camera)."""
    vpx, vpy = vp_coords(gx, gy)
    return act_click_vp(vpx, vpy, note=note or f"world({gx},{gy})")

def act_undo():
    global LAST_FD
    LAST_FD = env.step(UNDO)
    record_step("UNDO")

# ----------------------------------------------------------------------
# Replay L0-L4 from run_fixed.json
# ----------------------------------------------------------------------
with open('/mnt/c/exe/projects/ai-agents/ARC-SAGE/knowledge/visual-memory/bp35/run_20260413_111605/run_fixed.json') as f:
    run_fixed = json.load(f)

print(f"=== Replaying L0-L4 from run_fixed.json ({len(run_fixed['steps'])} steps total) ===\n")

# Take all steps that are at level 0-4 only.
L0_4_steps = [s for s in run_fixed['steps'] if s['level'] <= 4]
print(f"L0-L4 steps: {len(L0_4_steps)}")

SDK_PALETTE = {
    0: (255,255,255), 1: (204,204,204), 2: (153,153,153), 3: (102,102,102),
    4: (51,51,51), 5: (0,0,0), 6: (229,58,163), 7: (255,123,204),
    8: (249,60,49), 9: (30,147,255), 10: (136,216,241), 11: (255,220,0),
    12: (255,133,27), 13: (146,18,49), 14: (79,204,48), 15: (163,86,214),
}

def save_frame(label):
    """Save current viewport frame as PNG using LAST_FD.frame."""
    try:
        import numpy as np
        from PIL import Image
        if LAST_FD is None or not hasattr(LAST_FD, 'frame'):
            return False
        arr = np.array(LAST_FD.frame)
        if arr.ndim == 3:
            arr = arr[-1]
        if arr.ndim != 2 or arr.size == 0:
            print(f"    [save_frame] {label} skipped: unexpected shape {arr.shape}")
            return False
        h, w = arr.shape
        scale = 6
        img = np.zeros((h*scale, w*scale, 3), dtype=np.uint8)
        for r in range(h):
            for c in range(w):
                color = SDK_PALETTE.get(int(arr[r, c]), (128,128,128))
                img[r*scale:(r+1)*scale, c*scale:(c+1)*scale] = color
        Image.fromarray(img).save(f'{OUTDIR}/frames/{label}.png')
        return True
    except Exception as e:
        print(f"    [save_frame] {label} skipped: {e}")
    return False

# Save initial frame
save_frame(f"L0_start_p{player_pos()[0]}_{player_pos()[1]}")

for i, s in enumerate(L0_4_steps):
    act = s['action']
    if act == 'RIGHT':
        act_right()
    elif act == 'LEFT':
        act_left()
    elif act == 'CLICK':
        act_click_vp(s['x'], s['y'], note=f"replay[{s['step']}]")
    else:
        print(f"    [?] unknown action {act} at step {s['step']}")
        continue
    # Level transition?
    if level() != LAST_LEVEL - (1 if TRACE[-1].get('level_up') else 0):
        # handled in record_step
        pass

print(f"\n  After L0-L4 replay: level={level()}, player={player_pos()}, grav={'UP' if grav_up() else 'DN'}")
print(f"  Trace steps so far: {STEP_I}, OOB skipped: {OOB_COUNT}")

if level() != 5:
    print(f"\n  !!! Expected level=5 after L0-L4 replay, got level={level()}")
    print(f"  !!! Check replay integrity. Continuing to L5 probe anyway.")

save_frame(f"L5_start_p{player_pos()[0]}_{player_pos()[1]}")

# ----------------------------------------------------------------------
# L5 PROBE — try every viewport-legal option
# ----------------------------------------------------------------------
print("\n=== L5 PROBE ===\n")
print(f"  Start: player={player_pos()}, grav={'UP' if grav_up() else 'DN'}, cam={cam()}")
print()
print("  Initial L5 grid (y=18..33, x=-1..11):")
print_grid()

# Reset note: we replayed L5's first 5 RIGHTS as part of L0-L4 cutoff? No —
# L0-L4 cutoff means we don't have L5 actions. Player should be at L5 spawn.
assert level() == 5, f"Expected L5, got {level()}"

L5_START = player_pos()
print(f"\n  L5 spawn confirmed: {L5_START}")

# We'll try multiple approaches. Between each approach, if player dies or
# transitions to L6 unexpectedly, document and stop.

PROBE_LOG = []

def probe(label, actions_fn):
    """Run a probe. actions_fn takes env and does stuff. Captures outcome."""
    global OOB_COUNT
    pre_step = STEP_I
    pre_oob = OOB_COUNT
    pre_pos = player_pos()
    pre_grav = grav_up()
    pre_level = level()

    print(f"\n  --- Probe: {label} ---")
    print(f"    Before: p={pre_pos} grav={'U' if pre_grav else 'D'} lvl={pre_level}")

    try:
        actions_fn()
    except Exception as e:
        print(f"    EXCEPTION: {e}")
        import traceback; traceback.print_exc()

    post_pos = player_pos()
    post_grav = grav_up()
    post_level = level()
    delta_steps = STEP_I - pre_step
    delta_oob = OOB_COUNT - pre_oob

    print(f"    After:  p={post_pos} grav={'U' if post_grav else 'D'} lvl={post_level} "
          f"(+{delta_steps} steps, +{delta_oob} oob)")

    PROBE_LOG.append({
        "label": label,
        "pre": {"pos": list(pre_pos), "grav": "U" if pre_grav else "D", "level": pre_level},
        "post": {"pos": list(post_pos), "grav": "U" if post_grav else "D", "level": post_level},
        "steps": delta_steps,
        "oob_skipped": delta_oob,
        "won": post_level > pre_level,
    })

    return post_level > pre_level  # True if we advanced

# ------ Walk to (8, 23) and observe clickable ------
# L5 spawn is (3, 23). Walk RIGHT 5 to reach (8, 23).

def probe_walk_right():
    for _ in range(5):
        act_right()

if probe("walk R x5 to (8,23)", probe_walk_right):
    print("  !!! Walking right won L5 somehow. Stopping.")
else:
    save_frame(f"L5_at_{player_pos()[0]}_{player_pos()[1]}")
    # enumerate what's clickable in view
    cx, cy = cam()
    print(f"    cam=({cx},{cy})")
    # List in-view G and O/B tiles
    G_tiles = [(8,1), (6,22), (4,31)]
    OB_tiles = [(2,13),(3,13),(4,13),(5,13),(6,13),(7,13),(8,13),
                (2,20),(3,20),(4,20),(6,25),(7,25)]
    print("    In-view tiles of interest:")
    for (gx, gy) in G_tiles:
        vpx, vpy = vp_coords(gx, gy)
        inv = in_view(vpx, vpy)
        s = sym_at(gx, gy)
        print(f"      G-cand ({gx},{gy})={s} vp=({vpx},{vpy}) {'IN' if inv else 'OOB'}")
    for (gx, gy) in OB_tiles:
        vpx, vpy = vp_coords(gx, gy)
        inv = in_view(vpx, vpy)
        s = sym_at(gx, gy)
        if inv:
            print(f"      OB ({gx},{gy})={s} vp=({vpx},{vpy}) IN")

# ------ Click G(6,22) to flip gravity DOWN ------
def probe_click_g622():
    act_click_world(6, 22, note="flip gravity DOWN via G(6,22)")

probe("click G(6,22) → grav DN", probe_click_g622)
save_frame(f"L5_after_G622_p{player_pos()[0]}_{player_pos()[1]}")
print_grid()

# Player should now be at (8, 31) with grav DN (fell down col 8).
# Gem at (2, 31). G(4,31) blocks left walk.
# The ONLY known paths forward all fail: we'll enumerate them.

# Quick sanity: can we walk LEFT from (8,31) without clicking G(4,31)?
# Expected: no — G(4,31) blocks at x=4.

# Save current state so we can try many branches? The engine doesn't have a
# clean snapshot, but ACTION7 is UNDO. Let's use UNDO between experiments.

# APPROACH A: walk LEFT and see how far we get (should stop at x=5)
def probe_walk_left_from_831():
    for _ in range(10):
        p1 = player_pos()
        act_left()
        p2 = player_pos()
        if p1 == p2:
            print(f"    blocked at {p2}")
            break

probe("A: walk L from (8,31) until blocked", probe_walk_left_from_831)
save_frame(f"L5_A_blocked_p{player_pos()[0]}_{player_pos()[1]}")

# APPROACH B: click G(4,31) — the fatal flip per analysis.
# Per the docs: G(4,31) is in view from (8,31) at vp=(24,26). Consuming it
# flips gravity to UP, player falls up through col 4 (removed G(4,31), then
# (4,30) is wall — so just fly up from (5,31) if we're there).
# Actually player is at (5,31) now from walk-left-blocked.

def probe_click_g431():
    act_click_world(4, 31, note="click G(4,31) — the game-design dead end")

probe("B: click G(4,31) from current pos", probe_click_g431)
save_frame(f"L5_B_after_G431_p{player_pos()[0]}_{player_pos()[1]}")
print_grid()

# After: player should be at y=23 (or wherever falls up) with grav UP.
# Try walking LEFT to see what happens.
def probe_walk_left_after_B():
    for _ in range(8):
        p1 = player_pos()
        act_left()
        p2 = player_pos()
        if p1 == p2:
            print(f"    blocked at {p2}")
            break

probe("B2: walk L after G(4,31)", probe_walk_left_after_B)
save_frame(f"L5_B2_p{player_pos()[0]}_{player_pos()[1]}")

# APPROACH C: Now try clicking G(8,1) — is it in view?
def probe_try_g81():
    vpx, vpy = vp_coords(8, 1)
    print(f"    G(8,1) vp=({vpx},{vpy}) inview={in_view(vpx, vpy)}")
    act_click_world(8, 1, note="try G(8,1) — walled per docs")

probe("C: try G(8,1) third gravity flip", probe_try_g81)

# APPROACH D: try clicking all O/B tiles in view
def probe_try_all_ob():
    OB_tiles = [(2,13),(3,13),(4,13),(5,13),(6,13),(7,13),(8,13),
                (2,20),(3,20),(4,20),(6,25),(7,25)]
    for (gx, gy) in OB_tiles:
        vpx, vpy = vp_coords(gx, gy)
        if in_view(vpx, vpy):
            s = sym_at(gx, gy)
            print(f"    OB ({gx},{gy})={s} vp=({vpx},{vpy})")
            act_click_world(gx, gy, note=f"OB toggle ({gx},{gy})")
            p_now = player_pos()
            if level() > 5:
                print(f"    !!! Won L5 via OB click! player={p_now}")
                return

probe("D: toggle every in-view O/B tile", probe_try_all_ob)
save_frame(f"L5_D_p{player_pos()[0]}_{player_pos()[1]}")

# APPROACH E: click the gem directly (won't work but try)
def probe_click_gem():
    act_click_world(2, 31, note="click gem directly")

probe("E: click gem tile directly", probe_click_gem)

# APPROACH F: click the player position (many games treat as no-op)
def probe_click_player():
    p = player_pos()
    act_click_world(p[0], p[1], note=f"click player at {p}")

probe("F: click player tile", probe_click_player)

# APPROACH G: click empty space in the gem chamber at (1,31),(3,31),(1,30),(2,30),(3,30)
def probe_click_empty_chamber():
    for (gx, gy) in [(1,31),(3,31),(1,30),(2,30),(3,30)]:
        vpx, vpy = vp_coords(gx, gy)
        if in_view(vpx, vpy):
            s = sym_at(gx, gy)
            print(f"    chamber cell ({gx},{gy})={s} vp=({vpx},{vpy})")
            act_click_world(gx, gy, note=f"chamber ({gx},{gy})")
            if level() > 5:
                return

probe("G: click empty chamber cells", probe_click_empty_chamber)

# APPROACH H: click walls near the gem
def probe_click_walls_near_gem():
    for (gx, gy) in [(4,30),(0,31),(0,30),(5,30),(6,30),(7,30)]:
        vpx, vpy = vp_coords(gx, gy)
        if in_view(vpx, vpy):
            s = sym_at(gx, gy)
            print(f"    wall ({gx},{gy})={s} vp=({vpx},{vpy})")
            act_click_world(gx, gy, note=f"wall ({gx},{gy})")
            if level() > 5:
                return

probe("H: click walls near gem", probe_click_walls_near_gem)

# APPROACH I: UNDO — can we rewind?
def probe_undo():
    pre = player_pos()
    act_undo()
    post = player_pos()
    print(f"    undo: {pre} → {post}")
    # try a few more undos
    for _ in range(3):
        pre = player_pos()
        act_undo()
        post = player_pos()
        print(f"    undo: {pre} → {post}")

probe("I: try UNDO repeatedly", probe_undo)
save_frame(f"L5_I_undo_p{player_pos()[0]}_{player_pos()[1]}")

# APPROACH J: click spikes (usually lethal or no-op)
def probe_click_spikes():
    # y=26 spikes cols 2-7: "..WWvvvvvv.WW...."
    for (gx, gy) in [(2,26),(3,26),(5,26),(6,26),(7,26)]:
        vpx, vpy = vp_coords(gx, gy)
        if in_view(vpx, vpy):
            s = sym_at(gx, gy)
            print(f"    spike ({gx},{gy})={s} vp=({vpx},{vpy})")
            act_click_world(gx, gy, note=f"spike ({gx},{gy})")
            if level() > 5:
                return

probe("J: click spikes", probe_click_spikes)

# APPROACH K: a LONG walk sequence to drain animation and see if anything
# happens — e.g. walk right-left-right for many turns
def probe_walk_loop():
    for i in range(10):
        p1 = player_pos()
        if i % 2 == 0:
            act_right()
        else:
            act_left()
        p2 = player_pos()
        if level() > 5:
            return

probe("K: walk oscillation R/L x10", probe_walk_loop)

# APPROACH L: try G(6,22) even though it's consumed — catch the no-op
def probe_click_g622_again():
    act_click_world(6, 22, note="re-click consumed G(6,22)")

probe("L: re-click G(6,22) (consumed)", probe_click_g622_again)

# APPROACH M: walk RIGHT from (5,30) to see if gravity resolves differently
def probe_walk_right_post_G431():
    for _ in range(6):
        p1 = player_pos()
        act_right()
        p2 = player_pos()
        if p1 == p2:
            print(f"    blocked at {p2}")
            break
        if level() > 5:
            return

probe("M: walk R from (5,30) after G(4,31)", probe_walk_right_post_G431)
save_frame(f"L5_M_p{player_pos()[0]}_{player_pos()[1]}")

# APPROACH N: from wherever we are, click G(4,31) again (it's now consumed=. at y=31)
# — this is a no-op test, confirms no double-consumption mechanic
def probe_click_consumed_g431():
    act_click_world(4, 31, note="re-click consumed G(4,31) at y=31 (now empty)")

probe("N: re-click consumed G(4,31)", probe_click_consumed_g431)

# APPROACH O: try clicking every tile in the viewport systematically
# (maybe something we haven't identified acts like a gravity anchor)
def probe_exhaustive_viewport():
    tried = set()
    cx, cy = cam()
    # Scan every 6px within viewport
    hits = 0
    for vy in range(0, 64, 6):
        for vx in range(0, 64, 6):
            gx = (vx + cx) // 6
            gy = (vy + cy) // 6
            if (gx, gy) in tried:
                continue
            tried.add((gx, gy))
            s = sym_at(gx, gy)
            # Only click novel tile types we haven't touched
            if s in ('?', '.'):  # empty or unknown
                continue
            if s in ('W', 'v', '^'):  # walls/spikes — already tested
                continue
            # G, O, B, D, c, E, *
            if s not in ('G', 'O', 'B', 'D', 'E'):
                continue
            print(f"    exhaustive click ({gx},{gy})={s} vp=({vx},{vy})")
            act_click_world(gx, gy, note=f"exhaustive-scan ({gx},{gy})={s}")
            hits += 1
            if level() > 5:
                print(f"    !!! WON via ({gx},{gy})={s}!")
                return
            if hits > 20:
                print(f"    stopping after {hits} hits")
                return

probe("O: exhaustive viewport scan", probe_exhaustive_viewport)
save_frame(f"L5_O_p{player_pos()[0]}_{player_pos()[1]}")

# APPROACH P: starting with a brand new L5 attempt via UNDO spam (if supported)
# — this probably doesn't work since UNDO was a no-op, but try hard
def probe_undo_spam():
    for i in range(20):
        pre = player_pos()
        act_undo()
        if player_pos() != pre:
            print(f"    undo moved us to {player_pos()}")

probe("P: undo spam (20x)", probe_undo_spam)

# APPROACH Q: try ACTION1, ACTION2, ACTION5 — might be UP/DOWN/SPECIAL
def probe_alt_actions():
    from arcengine import GameAction as GA
    for name, act in [('ACTION1', GA.ACTION1), ('ACTION2', GA.ACTION2), ('ACTION5', GA.ACTION5)]:
        pre = player_pos()
        pre_g = grav_up()
        try:
            env.step(act)
            post = player_pos()
            post_g = grav_up()
            moved = pre != post
            gravchg = pre_g != post_g
            print(f"    {name}: {pre}→{post} grav {'U' if pre_g else 'D'}→{'U' if post_g else 'D'} "
                  f"{'MOVED' if moved else 'still'} {'GRAV-FLIP' if gravchg else ''}")
            # Record
            global STEP_I
            STEP_I += 1
            TRACE.append({"step": STEP_I, "level": level(), "action": name,
                          "note": f"alt-action probe pre={pre} post={post}"})
            if level() > 5:
                print(f"    !!! WON via {name}!")
                return
        except Exception as e:
            print(f"    {name}: ERROR {e}")

probe("Q: try ACTION1/ACTION2/ACTION5", probe_alt_actions)

# APPROACH R: UNDO ALL the way back to L5 fresh spawn, then try
# alternate path: toggle O tiles FIRST before G flip
def probe_undo_to_spawn():
    for _ in range(100):
        pre = player_pos()
        pre_l = level()
        act_undo()
        if level() < pre_l:
            print(f"    undo dropped us below L5 to {level()} — too far, stop")
            break
        if player_pos() == pre and level() == pre_l:
            # also check g-state
            break

probe("R1: UNDO all the way back", probe_undo_to_spawn)
print(f"    After undo chain: p={player_pos()} grav={'U' if grav_up() else 'D'} level={level()}")

# Check if gem chamber walls/Gs are restored
print("    Grid after undo (should be L5 fresh):")
print_grid(yr=(18, 33))

# APPROACH S: O/B toggle first, THEN G flip
def probe_ob_then_g():
    # From whatever state we're in, first toggle the OB tiles we can
    # (6,25) and (7,25) need to be in view. Initial cam y depends on player pos.
    cx, cy = cam()
    print(f"    cam=({cx},{cy}) starting state for approach S")
    # Walk right 5 to get to (8,23)
    for _ in range(5):
        act_right()
    # Now cam_y should be 23*6 - 36 = 102
    # O(6,25) vp = 36, 25*6-102 = 48  → in view
    # O(7,25) vp = 42, 48            → in view
    # Toggle O→B at both
    print(f"    At {player_pos()} cam={cam()}")
    act_click_world(6, 25, note="S: toggle O(6,25) to B")
    act_click_world(7, 25, note="S: toggle O(7,25) to B")
    print(f"    After OB toggle: sym(6,25)={sym_at(6,25)}, sym(7,25)={sym_at(7,25)}")
    # Now click G(6,22) to flip gravity DOWN
    act_click_world(6, 22, note="S: G(6,22) → grav DN after OB toggle")
    print(f"    After G(6,22): p={player_pos()} grav={'U' if grav_up() else 'D'}")
    # Now with B(6,25)(7,25) solid, grav DN falling from (8,23) → (8,31) still
    # but we could walk LEFT along y=23? Check — we'd need a different path

probe("S: OB toggle first, then G(6,22)", probe_ob_then_g)
save_frame(f"L5_S_p{player_pos()[0]}_{player_pos()[1]}")
print_grid(yr=(18, 33))

# From wherever we landed, try to navigate towards gem
def probe_S_continue():
    # We're probably at (8,31) grav DN with B(6,25)(7,25) solid.
    # With B solid, player could potentially fall-stop at y=24 on col 6 or 7.
    # But we're at y=31 already; to get to y=24, we need to flip grav UP again
    # but G(6,22) is consumed, and G(4,31) is still there.
    # Clicking G(4,31): flips to UP, player flies UP from (8,31):
    #   (8,30) open, (8,29) wall → stop at (8,30). Hmm, still stuck.
    # Try it anyway.
    act_click_world(4, 31, note="S2: click G(4,31) to flip UP")
    print(f"    After G(4,31): p={player_pos()} grav={'U' if grav_up() else 'D'}")
    # Now walk LEFT at whatever y we are
    for _ in range(10):
        pre = player_pos()
        act_left()
        if player_pos() == pre:
            print(f"    blocked at {player_pos()}")
            break
        if level() > 5:
            return

probe("S2: continue after OB+G path", probe_S_continue)
save_frame(f"L5_S2_p{player_pos()[0]}_{player_pos()[1]}")
print_grid(yr=(18, 33))

# APPROACH T: reset the state — try clicking G(4,31) FIRST (while still at spawn)
# before any other action. The click might not work if (4,31) is OOB from spawn,
# but worth checking.
def probe_undo_all_again():
    for _ in range(200):
        pre = player_pos()
        pre_l = level()
        pre_g = grav_up()
        act_undo()
        if level() < pre_l or (player_pos() == pre and grav_up() == pre_g and level() == pre_l):
            break

probe("T1: UNDO back again", probe_undo_all_again)
print(f"    p={player_pos()} grav={'U' if grav_up() else 'D'} level={level()} cam={cam()}")

def probe_try_g431_direct():
    vpx, vpy = vp_coords(4, 31)
    print(f"    G(4,31) vp=({vpx},{vpy}) inview={in_view(vpx, vpy)}")
    act_click_world(4, 31, note="T: try G(4,31) directly from spawn")

probe("T: try G(4,31) from spawn", probe_try_g431_direct)

# APPROACH U: fresh env reset — try alternate ordering from clean state
# (toggle O→B at y=25 FIRST, then G(6,22), then see if new path exists)
print("\n=== FRESH RESET: alternate ordering test ===")
# Fresh L5 via replaying L0-L4 on a new arcade instance
arc2 = Arcade(operation_mode='offline')
env2 = arc2.make('bp35-0a0ad940')
fd2 = env2.reset()

def engine2(): return env2._game.oztjzzyqoek
def player_pos2():
    e = engine2()
    return tuple(e.twdpowducb.qumspquyus)
def grav_up2(): return engine2().vivnprldht
def cam2():
    c = engine2().camera.rczgvgfsfb
    return (c[0], c[1])
def sym_at2(x, y):
    items = engine2().hdnrlfmyrj.jhzcxkveiw(x, y)
    return SYM.get(items[0].name, '?') if items else '.'
def level2(): return env2._game.level_index
def vp_coords2(gx, gy):
    cx, cy = cam2()
    return gx * 6 - cx, gy * 6 - cy

ALT_LOG = []

def alt_step(action, x=None, y=None, note=None):
    entry = {"level": level2(), "action": action, "player_before": list(player_pos2()),
             "grav_before": "U" if grav_up2() else "D"}
    if action == 'RIGHT': env2.step(RIGHT)
    elif action == 'LEFT': env2.step(LEFT)
    elif action == 'CLICK':
        if not in_view(x, y):
            entry["oob"] = True
            print(f"    [alt OOB skip] vp=({x},{y})")
            ALT_LOG.append(entry)
            return False
        env2.step(CLICK, data={"x": x, "y": y})
        entry["x"] = x; entry["y"] = y
    elif action == 'UNDO': env2.step(UNDO)
    entry["player_after"] = list(player_pos2())
    entry["grav_after"] = "U" if grav_up2() else "D"
    entry["level_after"] = level2()
    if note: entry["note"] = note
    ALT_LOG.append(entry)
    return True

def alt_click_world(gx, gy, note=None):
    vpx, vpy = vp_coords2(gx, gy)
    return alt_step('CLICK', x=vpx, y=vpy, note=note or f"world({gx},{gy})")

# Replay L0-L4 on env2
for s in L0_4_steps:
    act = s['action']
    if act == 'RIGHT': env2.step(RIGHT)
    elif act == 'LEFT': env2.step(LEFT)
    elif act == 'CLICK':
        env2.step(CLICK, data={"x": s['x'], "y": s['y']})

assert level2() == 5, f"alt env expected L5, got {level2()}"
print(f"  alt env at L5: p={player_pos2()} grav={'U' if grav_up2() else 'D'} cam={cam2()}")

# Alternate-order path: walk right to (8,23), toggle O(6,25)(7,25) → B,
# then click G(6,22) to flip grav DN. Now player should fall col 8 — but
# check if the B tiles actually change fall destination.
print("  Walking R x5 to (8,23)...")
for _ in range(5):
    alt_step('RIGHT')
print(f"    now p={player_pos2()} cam={cam2()}")

# Toggle O→B at (6,25) and (7,25)
print("  Toggle O(6,25)→B, O(7,25)→B...")
alt_click_world(6, 25, note="toggle O→B")
alt_click_world(7, 25, note="toggle O→B")
print(f"    sym(6,25)={sym_at2(6,25)}, sym(7,25)={sym_at2(7,25)}")
print(f"    p={player_pos2()} grav={'U' if grav_up2() else 'D'}")

# Click G(6,22) → grav DN; player at (8,23), falls DN through col 8
print("  Click G(6,22) → grav DN...")
alt_click_world(6, 22, note="grav DN flip")
print(f"    p={player_pos2()} grav={'U' if grav_up2() else 'D'}")

# Now player is at (8,31) grav DN (same as before, since col 8 is open all the way).
# Walk LEFT — where do we stop?
print("  Walk LEFT until blocked...")
for i in range(10):
    pre = player_pos2()
    alt_step('LEFT')
    if player_pos2() == pre:
        print(f"    blocked at {pre}")
        break

print(f"    Final alt state: p={player_pos2()} grav={'U' if grav_up2() else 'D'} level={level2()}")
print("    Grid after alt path:")
# print grid from env2
pp2 = player_pos2()
for y in range(22, 33):
    row = ""
    for x in range(-1, 12):
        if (x, y) == pp2: row += 'P'
        else: row += sym_at2(x, y)
    print(f"      y={y:2d}: {row}")

# APPROACH V: one more — try toggling O(2,20),(3,20),(4,20) also.
# These affect y=20 layout. Initial state: cols 2,3,4 = O (passable).
# If toggled to B, player walking along y=21 grav UP would have floor at y=20.
# But player currently at (5,31) post-path. Let me just note we can't test this.

print("\n  !!! Alt path also ends at same (5,31)-ish state — no new path found.")

# Final state
print("\n\n=== FINAL L5 STATE ===")
p = player_pos()
g = grav_up()
c = cam()
print(f"  player: {p}")
print(f"  grav: {'UP' if g else 'DN'}")
print(f"  camera: {c}")
print(f"  level: {level()}")
print(f"  moves on level: {getattr(engine(), 'wzrfpakeylb', '?')}")

# Snapshot remaining G tiles
print("\n  G tile status:")
for (gx, gy) in [(8,1),(6,22),(4,31)]:
    s = sym_at(gx, gy)
    vpx, vpy = vp_coords(gx, gy)
    print(f"    G({gx},{gy})={s}  vp=({vpx},{vpy})  {'IN' if in_view(vpx,vpy) else 'OOB'}")

print("\n  Full grid around gem (y=22..33, x=-1..11):")
print_grid(yr=(22, 33))

save_frame(f"L5_final_p{p[0]}_{p[1]}")

# ----------------------------------------------------------------------
# Save trace
# ----------------------------------------------------------------------
out = {
    "game_id": "bp35-0a0ad940",
    "player": "bp35-legitimate-chain",
    "started": "20260416",
    "win_levels": 9,
    "baseline": 0,
    "notes": "Continuous legitimate-only replay: L0-L4 from run_fixed.json, then exhaustive L5 probing. NO eq.win() bypass. NO OOB clicks accepted.",
    "total_steps": STEP_I,
    "oob_skipped": OOB_COUNT,
    "final_level": level(),
    "final_player": list(player_pos()),
    "final_grav": "UP" if grav_up() else "DN",
    "steps": TRACE,
    "probes": PROBE_LOG,
    "alt_ordering_test": {
        "description": "Fresh env: toggle O(6,25)/(7,25)→B FIRST, then G(6,22), then walk L",
        "actions": ALT_LOG,
        "final_player_alt": list(player_pos2()),
        "final_grav_alt": "U" if grav_up2() else "D",
        "final_level_alt": level2(),
    },
}

with open(f'{OUTDIR}/run.json', 'w') as f:
    json.dump(out, f, indent=2)

print(f"\n\nTrace saved: {OUTDIR}/run.json ({STEP_I} steps, {OOB_COUNT} OOB rejected)")
print(f"Frames saved to: {OUTDIR}/frames/")
