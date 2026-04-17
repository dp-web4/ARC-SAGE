#!/usr/bin/env python3
"""
dc22 Level 6 - Replayable Action Trace

Translates the documented solution from dc22_l6_crane_exploration.md
into a step-by-step replay that captures every env.step() call.

Solution by CBP Agent 3 (crane exploration), 2026-04-16.

Game: dc22-4c9bff3e (4c9bff3e engine available locally;
      fdcac232 uses same coordinates, different sprite names)

Click coordinate map (screen coords, y_offset=0):
  Yellow (f):      (56, 8)   - sprite-6
  Magenta (c):     (51, 25)  - jpug-bjuk
  Color cycle (d): (51, 48)  - gkrr-jpug (after key d)
  Crane UP (b):    (51, 33)  - nxhz-zmjbupyjfyb-1
  Crane LEFT (e):  (47, 37)  - nxhz-vbdduyutyiw-1
  Crane RIGHT (a): (55, 37)  - nxhz-ghqmfnmmgrz-1
  Crane DOWN (h):  (51, 41)  - nxhz-vbdduyutyiw-2
  Crane GRAB (g):  (51, 18)  - nxhz-bynyvtuepbt-1 (after key g)

Pressure plates (game coords):
  (34,56) = b -> activates crane UP
  (32,58) = e -> activates crane LEFT
  (36,58) = a -> activates crane RIGHT
  (34,60) = h -> activates crane DOWN
"""

import os, sys, json

os.chdir("/mnt/c/exe/projects/ai-agents/ARC-SAGE")
os.environ['OPERATION_MODE'] = 'offline'
sys.path.insert(0, ".")
sys.path.insert(0, "arc-agi-3/experiments")
sys.stdout.reconfigure(line_buffering=True)

from arc_agi import Arcade
from arcengine import GameAction, GameState

# Click coordinates (screen space)
YELLOW  = {'x': 56, 'y':  8}   # f-button
MAGENTA = {'x': 51, 'y': 25}   # c-button
COLOR_CYCLE = {'x': 51, 'y': 48}  # d-button (after key d)
CRANE_UP    = {'x': 51, 'y': 33}  # b-button
CRANE_LEFT  = {'x': 47, 'y': 37}  # e-button
CRANE_RIGHT = {'x': 55, 'y': 37}  # a-button
CRANE_DOWN  = {'x': 51, 'y': 41}  # h-button
CRANE_GRAB  = {'x': 51, 'y': 18}  # g-button (after key g)

SOL_PATH = "/mnt/c/exe/projects/ai-agents/ARC-SAGE/knowledge/visual-memory/dc22/solutions.json"
OUT_DIR  = "/mnt/c/exe/projects/ai-agents/ARC-SAGE/knowledge/visual-memory/dc22/run_L6_solution"

ACTION_MAP = {
    1: GameAction.ACTION1,  # UP
    2: GameAction.ACTION2,  # DOWN
    3: GameAction.ACTION3,  # LEFT
    4: GameAction.ACTION4,  # RIGHT
    6: GameAction.ACTION6,  # CLICK
}

ACTION_NAMES = {
    GameAction.ACTION1: "UP",
    GameAction.ACTION2: "DOWN",
    GameAction.ACTION3: "LEFT",
    GameAction.ACTION4: "RIGHT",
    GameAction.ACTION6: "CLICK",
}


def replay_l1_to_l5(env, solutions):
    """Replay levels 1-5 from stored solutions."""
    for lvl_idx in range(5):
        for m in solutions[lvl_idx]:
            env.step(ACTION_MAP[m['action']], data=m.get('data', {}))
    game = env._game
    print(f"After L1-L5 replay: player=({game.fdvakicpimr.x},{game.fdvakicpimr.y})")
    print(f"Goal=({game.bqxa.x},{game.bqxa.y})")
    return game


class ActionTracer:
    """Records every env.step() call as a run.json entry."""

    def __init__(self, env, level):
        self.env = env
        self.game = env._game
        self.level = level
        self.step_num = 0
        self.trace = []

    def pos(self):
        return (self.game.fdvakicpimr.x, self.game.fdvakicpimr.y)

    def do(self, action, data=None, label=""):
        """Execute one action and record it."""
        if data is None:
            data = {}
        fd = self.env.step(action, data=data)
        self.step_num += 1
        name = ACTION_NAMES.get(action, str(action))

        entry = {
            "step": self.step_num,
            "action": name,
            "x": self.game.fdvakicpimr.x,
            "y": self.game.fdvakicpimr.y,
            "level": self.level,
        }
        if data:
            entry["click_x"] = data.get("x", 0)
            entry["click_y"] = data.get("y", 0)

        self.trace.append(entry)

        state_name = fd.state.name if hasattr(fd.state, 'name') else str(fd.state)
        if label:
            print(f"  [{self.step_num:3d}] {name:5s} -> ({entry['x']:2d},{entry['y']:2d}) {label}  state={state_name}")
        else:
            print(f"  [{self.step_num:3d}] {name:5s} -> ({entry['x']:2d},{entry['y']:2d})  state={state_name}")

        if state_name == 'WIN':
            print(f"  >>> LEVEL WON at step {self.step_num}!")
        elif state_name == 'LOSE':
            print(f"  >>> LOST at step {self.step_num}!")

        return fd

    def up(self, n=1, label=""):
        for i in range(n):
            self.do(GameAction.ACTION1, label=label if i == n-1 else "")

    def down(self, n=1, label=""):
        for i in range(n):
            self.do(GameAction.ACTION2, label=label if i == n-1 else "")

    def left(self, n=1, label=""):
        for i in range(n):
            self.do(GameAction.ACTION3, label=label if i == n-1 else "")

    def right(self, n=1, label=""):
        for i in range(n):
            self.do(GameAction.ACTION4, label=label if i == n-1 else "")

    def click(self, coords, label=""):
        self.do(GameAction.ACTION6, data=coords, label=label)

    def yellow(self, label="yellow"):
        self.click(YELLOW, label=label)

    def magenta(self, label="magenta"):
        self.click(MAGENTA, label=label)

    def color_cycle(self, label="color_cycle"):
        self.click(COLOR_CYCLE, label=label)

    def crane_up(self, label="crane_UP"):
        self.click(CRANE_UP, label=label)

    def crane_down(self, label="crane_DOWN"):
        self.click(CRANE_DOWN, label=label)

    def crane_left(self, label="crane_LEFT"):
        self.click(CRANE_LEFT, label=label)

    def crane_right(self, label="crane_RIGHT"):
        self.click(CRANE_RIGHT, label=label)

    def crane_grab(self, label="crane_GRAB"):
        self.click(CRANE_GRAB, label=label)

    def assert_pos(self, expected_x, expected_y, context=""):
        actual = self.pos()
        if actual != (expected_x, expected_y):
            print(f"  !!! POSITION MISMATCH at step {self.step_num}: "
                  f"expected ({expected_x},{expected_y}), got {actual}. {context}")
            return False
        return True

    def get_solution_actions(self):
        """Convert trace to solutions.json format."""
        actions = []
        for entry in self.trace:
            a = {"action": {"UP": 1, "DOWN": 2, "LEFT": 3, "RIGHT": 4, "CLICK": 6}[entry["action"]]}
            if "click_x" in entry:
                a["data"] = {"x": entry["click_x"], "y": entry["click_y"]}
            actions.append(a)
        return actions


def solve_l6(tracer):
    """Execute the 8-phase L6 solution from the crane exploration doc."""

    # ========================================
    # Phase 1: Bridge + Key "d" (44 actions documented)
    # ========================================
    print("\n=== Phase 1: Bridge crossing + Key d ===")

    # Yellow x4 -> bridge state 4
    for i in range(4):
        tracer.yellow(label=f"yellow_{i+1}")

    # Walk LEFT x5 to (18,52)
    tracer.left(5, label="-> (18,52)")
    tracer.assert_pos(18, 52, "after LEFT x5")

    # DOWN x2 to (18,56)
    tracer.down(2, label="-> (18,56)")
    tracer.assert_pos(18, 56, "after DOWN x2")

    # LEFT x2 to (14,56)
    tracer.left(2, label="-> (14,56)")
    tracer.assert_pos(14, 56, "after LEFT x2")

    # Yellow (state 5)
    tracer.yellow(label="yellow_5 (state 5)")

    # DOWN to (14,58)
    tracer.down(1, label="-> (14,58)")
    tracer.assert_pos(14, 58, "after DOWN")

    # LEFT to (12,58)
    tracer.left(1, label="-> (12,58)")
    tracer.assert_pos(12, 58, "after LEFT")

    # Yellow (state 0)
    tracer.yellow(label="yellow_6 (state 0)")

    # UP to (12,56)
    tracer.up(1, label="-> (12,56)")
    tracer.assert_pos(12, 56, "after UP")

    # LEFT x2 to (8,56)
    tracer.left(2, label="-> (8,56)")
    tracer.assert_pos(8, 56, "after LEFT x2")

    # UP x6 to (8,44)
    tracer.up(6, label="-> (8,44)")
    tracer.assert_pos(8, 44, "after UP x6")

    # Magenta 1 (toggles dmxj, activates vertical bridge)
    tracer.magenta(label="magenta_1 (toggle dmxj)")

    # UP x12 to (8,20) -- through orange column
    tracer.up(12, label="-> (8,20)")
    tracer.assert_pos(8, 20, "after UP x12")

    # LEFT to (6,20)
    tracer.left(1, label="-> (6,20)")
    tracer.assert_pos(6, 20, "after LEFT")

    # UP to (6,18) - KEY "d"
    tracer.up(1, label="-> (6,18) KEY d")
    tracer.assert_pos(6, 18, "after UP to key d")

    # Color cycle x3 (upry -> bgeg -> zfrq -> jbyz)
    for i in range(3):
        tracer.color_cycle(label=f"color_cycle_{i+1}")

    print(f"  Phase 1 complete: {tracer.step_num} actions, pos={tracer.pos()}")

    # ========================================
    # Phase 2: Return + Bridge RIGHT + Teleport Chain
    # ========================================
    print("\n=== Phase 2: Return + Teleport chain ===")

    # RIGHT to (8,18)
    tracer.right(1, label="-> (8,18)")
    tracer.assert_pos(8, 18, "after RIGHT")

    # DOWN x17 to (8,52)
    tracer.down(17, label="-> (8,52)")
    tracer.assert_pos(8, 52, "after DOWN x17")

    # Magenta 2 (toggles dmxj back to horizontal)
    tracer.magenta(label="magenta_2 (toggle dmxj)")

    # Walk DOWN x2 to (8,56), RIGHT x2 to (12,56) on bridge
    tracer.down(2, label="-> (8,56)")
    tracer.assert_pos(8, 56, "after DOWN x2")
    tracer.right(2, label="-> (12,56)")
    tracer.assert_pos(12, 56, "after RIGHT x2")

    # Walk RIGHT across bridge with yellow clicks
    # Bridge state 0: y=56 at x=8-12 AND x=16-20
    # Need to walk from (12,56) to reach (18,48) eventually.
    # Pattern: yellow, RIGHT, yellow, RIGHT, yellow, RIGHT, yellow
    # (4 yellow clicks + 3 RIGHTs, ending at state 4 at (18,56))
    # State 0->1: yellow. y=56 at x=6-14. Player (12,56) ok. RIGHT to (14,56).
    # State 1->2: yellow. y=56 at x=8-16. Player (14,56) ok. RIGHT to (16,56).
    # State 2->3: yellow. y=56 at x=10-18. Player (16,56) ok. RIGHT to (18,56).
    # State 3->4: yellow. y=54 at x=14-18 includes x=18 for UP path.
    # Player stays at (18,56), but can now walk UP via y=54.
    for i in range(3):
        tracer.yellow(label=f"yellow (bridge state {i+1})")
        tracer.right(1, label=f"RIGHT across bridge")
    tracer.yellow(label="yellow (bridge state 4)")

    print(f"  After bridge RIGHT: pos={tracer.pos()}")

    # Walk UP to (18,48) -- state 4: y=54 at x=14-18, y=52 is floor
    # (18,56) -> (18,54) bridge -> (18,52) floor -> (18,50) -> (18,48)
    tracer.up(4, label="-> (18,48)")
    tracer.assert_pos(18, 48, "at itki (18,48)")

    # Magenta 3 -> TELEPORT to (34,58)
    # itki at (18,48) is now jbyz variant, teleports to (34,58)
    tracer.magenta(label="magenta_3 -> TELEPORT to (34,58)")
    print(f"  After magenta 3: pos={tracer.pos()}")

    # Magenta 4 -> TELEPORT to (18,48)
    tracer.magenta(label="magenta_4 -> TELEPORT to (18,48)")
    print(f"  After magenta 4: pos={tracer.pos()}")

    # 1 color cycle + Magenta 5 -> TELEPORT to (32,52)
    # Color cycle: jbyz -> upry. upry at (18,48) teleports to (32,52)
    tracer.color_cycle(label="color_cycle (jbyz->upry)")
    tracer.magenta(label="magenta_5 -> TELEPORT to (32,52)")
    print(f"  After magenta 5: pos={tracer.pos()}")

    print(f"  Phase 2 complete: {tracer.step_num} actions, pos={tracer.pos()}")

    # ========================================
    # Phase 3: Key "g" + Return (9 actions documented)
    # ========================================
    print("\n=== Phase 3: Key g + Return ===")

    # Walk to (34,48) for key "g"
    # From (32,52): RIGHT x1 to (34,52), UP x2 to (34,48)
    tracer.right(1, label="-> (34,52)")
    tracer.up(2, label="-> (34,48) KEY g")
    tracer.assert_pos(34, 48, "at key g")

    # Back to (32,52)
    tracer.down(2, label="-> (34,52)")
    tracer.left(1, label="-> (32,52)")
    tracer.assert_pos(32, 52, "back at (32,52)")

    # Magenta 6 -> to (18,48)
    tracer.magenta(label="magenta_6 -> to (18,48)")
    print(f"  After magenta 6: pos={tracer.pos()}")

    # 3 color cycles + Magenta 7 -> to (34,58)
    for i in range(3):
        tracer.color_cycle(label=f"color_cycle_{i+1}")
    tracer.magenta(label="magenta_7 -> to (34,58)")
    print(f"  After magenta 7: pos={tracer.pos()}")

    print(f"  Phase 3 complete: {tracer.step_num} actions, pos={tracer.pos()}")

    # ========================================
    # Phase 4: dmxj Toggle (3 actions documented)
    # ========================================
    print("\n=== Phase 4: dmxj Toggle ===")

    # Walk UP to (34,56) pressure plate
    tracer.up(1, label="-> (34,56) pressure plate b")
    tracer.assert_pos(34, 56, "on UP pressure plate")

    # Magenta 8 -> toggle dmxj to dmxj1 (NO teleport - not on itki)
    tracer.magenta(label="magenta_8 (toggle dmxj, no teleport)")
    print(f"  After magenta 8: pos={tracer.pos()}")

    # Walk DOWN to (34,58)
    tracer.down(1, label="-> (34,58)")
    tracer.assert_pos(34, 58, "back at (34,58)")

    print(f"  Phase 4 complete: {tracer.step_num} actions, pos={tracer.pos()}")

    # ========================================
    # Phase 5: Crane Operations (6 actions documented)
    # ========================================
    print("\n=== Phase 5: Crane Operations ===")

    # Walk LEFT to (32,58) = LEFT plate
    tracer.left(1, label="-> (32,58) LEFT plate")
    tracer.assert_pos(32, 58, "on LEFT pressure plate")

    # Crane LEFT x4 -> grid(-4,0) aligns with cross center
    for i in range(4):
        tracer.crane_left(label=f"crane_LEFT_{i+1}")

    # Click grab -> crane grabs hhxv-dmxj1!
    tracer.crane_grab(label="crane_GRAB!")

    print(f"  Phase 5 complete: {tracer.step_num} actions, pos={tracer.pos()}")
    print(f"  Crane: nxhz_x={tracer.game.nxhz_x}, nxhz_y={tracer.game.nxhz_y}")
    print(f"  Attached: {tracer.game.nxhz_attached_kind}")

    # ========================================
    # Phase 6: Crane Navigation (25 actions documented)
    # ========================================
    print("\n=== Phase 6: Crane Navigation ===")

    # Navigate crane from (-4,0) to (-1,6) via valid grid path.
    # Each crane move requires standing on the correct pressure plate.
    #
    # Sequence from doc:
    # RIGHT x3: (-4,0) -> (-1,0)
    # UP x1: (-1,0) -> (-1,1)
    # RIGHT x2: (-1,1) -> (1,1)
    # UP x2: (1,1) -> (1,3)
    # LEFT x2: (1,3) -> (-1,3)
    # UP x3: (-1,3) -> (-1,6)

    # Step 1: Move to RIGHT plate (36,58)
    tracer.right(2, label="-> (36,58) RIGHT plate")
    tracer.assert_pos(36, 58, "on RIGHT pressure plate")

    # Crane RIGHT x3: (-4,0) -> (-1,0)
    for i in range(3):
        tracer.crane_right(label=f"crane_RIGHT_{i+1}")

    # Step 2: Move to UP plate (34,56)
    tracer.left(1, label="-> (34,58)")
    tracer.up(1, label="-> (34,56) UP plate")
    tracer.assert_pos(34, 56, "on UP pressure plate")

    # Crane UP x1: (-1,0) -> (-1,1)
    tracer.crane_up(label="crane_UP_1")

    # Step 3: Move to RIGHT plate (36,58)
    tracer.down(1, label="-> (34,58)")
    tracer.right(1, label="-> (36,58) RIGHT plate")
    tracer.assert_pos(36, 58, "on RIGHT pressure plate")

    # Crane RIGHT x2: (-1,1) -> (1,1)
    for i in range(2):
        tracer.crane_right(label=f"crane_RIGHT_{i+1}")

    # Step 4: Move to UP plate (34,56)
    tracer.left(1, label="-> (34,58)")
    tracer.up(1, label="-> (34,56) UP plate")
    tracer.assert_pos(34, 56, "on UP pressure plate")

    # Crane UP x2: (1,1) -> (1,3)
    for i in range(2):
        tracer.crane_up(label=f"crane_UP_{i+1}")

    # Step 5: Move to LEFT plate (32,58)
    tracer.down(1, label="-> (34,58)")
    tracer.left(1, label="-> (32,58) LEFT plate")
    tracer.assert_pos(32, 58, "on LEFT pressure plate")

    # Crane LEFT x2: (1,3) -> (-1,3)
    for i in range(2):
        tracer.crane_left(label=f"crane_LEFT_{i+1}")

    # Step 6: Move to UP plate (34,56)
    tracer.right(1, label="-> (34,58)")
    tracer.up(1, label="-> (34,56) UP plate")
    tracer.assert_pos(34, 56, "on UP pressure plate")

    # Crane UP x3: (-1,3) -> (-1,6)
    for i in range(3):
        tracer.crane_up(label=f"crane_UP_{i+1}")

    print(f"  Phase 6 complete: {tracer.step_num} actions, pos={tracer.pos()}")
    print(f"  Crane: nxhz_x={tracer.game.nxhz_x}, nxhz_y={tracer.game.nxhz_y}")

    # ========================================
    # Phase 7: Teleport to (4,4) (5 actions documented)
    # ========================================
    print("\n=== Phase 7: Teleport to (4,4) ===")

    # Walk DOWN to (34,58)
    tracer.down(1, label="-> (34,58)")
    tracer.assert_pos(34, 58, "at (34,58)")

    # Magenta 9 -> (18,48)
    tracer.magenta(label="magenta_9 -> (18,48)")
    print(f"  After magenta 9: pos={tracer.pos()}")

    # 3 color cycles + Magenta 10 -> (4,4)
    # jbyz -> upry -> bgeg -> zfrq. zfrq teleports to (4,4).
    for i in range(3):
        tracer.color_cycle(label=f"color_cycle_{i+1}")
    tracer.magenta(label="magenta_10 -> (4,4)")
    print(f"  After magenta 10: pos={tracer.pos()}")

    print(f"  Phase 7 complete: {tracer.step_num} actions, pos={tracer.pos()}")

    # ========================================
    # Phase 8: Walk to Goal (27 actions documented)
    # ========================================
    print("\n=== Phase 8: Walk to Goal ===")

    # Walk DOWN x2 to (4,8) - bridge arm level
    tracer.down(2, label="-> (4,8) bridge level")
    tracer.assert_pos(4, 8, "at bridge level")

    # Walk RIGHT x17 to (38,8) across bridge
    tracer.right(17, label="-> (38,8) across bridge")
    tracer.assert_pos(38, 8, "across bridge")

    # Walk DOWN to (38,10) - wall transparent level
    tracer.down(1, label="-> (38,10)")
    tracer.assert_pos(38, 10, "at wall transparent level")

    # Walk RIGHT x4 to (46,10) through wall
    tracer.right(4, label="-> (46,10) through wall")
    tracer.assert_pos(46, 10, "through wall")

    # Walk UP x2 to (46,6) - GOAL!
    tracer.up(2, label="-> (46,6) GOAL!")

    print(f"  Phase 8 complete: {tracer.step_num} actions, pos={tracer.pos()}")

    return tracer


def main():
    # Load solutions
    with open(SOL_PATH) as f:
        solutions = json.load(f)

    # Initialize game
    arcade = Arcade(operation_mode='offline')
    env = arcade.make('dc22-4c9bff3e')
    env.reset()

    # Replay L1-L5
    print("Replaying L1-L5...")
    game = replay_l1_to_l5(env, solutions)

    # Solve L6
    print("\nSolving L6...")
    tracer = ActionTracer(env, level=6)
    tracer = solve_l6(tracer)

    # Save run.json
    os.makedirs(OUT_DIR, exist_ok=True)
    run_path = os.path.join(OUT_DIR, "run.json")
    with open(run_path, 'w') as f:
        json.dump(tracer.trace, f, indent=2)
    print(f"\nSaved {len(tracer.trace)} steps to {run_path}")

    # Update solutions.json with L6
    l6_actions = tracer.get_solution_actions()
    if len(solutions) < 6:
        solutions.append(l6_actions)
    else:
        solutions[5] = l6_actions
    with open(SOL_PATH, 'w') as f:
        json.dump(solutions, f, indent=2)
    print(f"Updated {SOL_PATH} with L6 ({len(l6_actions)} actions)")

    print(f"\nTotal L6 actions: {tracer.step_num}")
    print(f"Final position: {tracer.pos()}")


if __name__ == "__main__":
    main()
