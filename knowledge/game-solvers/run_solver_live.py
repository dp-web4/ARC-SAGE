#!/usr/bin/env python3
"""
Run a game solver against the live ARC-AGI-3 API and verify it wins.

Usage:
    python3 run_solver_live.py <game_prefix>          # Run one game
    python3 run_solver_live.py --all                   # Run all games with solvers
    python3 run_solver_live.py --all --update-db       # Run all and update SOLUTIONS_DB.json
"""

import sys, os, json, time, importlib.util, traceback
import numpy as np

# Ensure we can import SDK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "SAGE"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "SAGE", "arc-agi-3", "experiments"))

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

SOLVER_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(SOLVER_DIR), "SOLUTIONS_DB.json")

ALL_GAMES = [
    "sb26", "vc33", "cd82", "lp85", "ft09", "s5i5", "tn36", "r11l",
    "sc25", "tr87", "tu93", "sp80", "ls20", "su15", "g50t", "ar25",
    "bp35", "sk48", "cn04", "ka59", "m0r0", "re86", "dc22", "lf52", "wa30"
]


def load_solver(game_prefix):
    """Dynamically load a game solver module."""
    solver_path = os.path.join(SOLVER_DIR, f"{game_prefix}_solver.py")
    if not os.path.exists(solver_path):
        return None
    spec = importlib.util.spec_from_file_location(f"{game_prefix}_solver", solver_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def find_game_id(arcade, prefix):
    """Find full game ID from prefix."""
    for env_info in arcade.get_environments():
        if prefix in env_info.game_id:
            return env_info.game_id, env_info
    return None, None


def get_frame(fd):
    """Extract the last frame from frame data."""
    frame = np.array(fd.frame)
    if len(frame.shape) == 3:
        return frame[-1]
    return frame


def run_solver_live(game_prefix, verbose=True):
    """Run a solver against the live API. Returns dict with results."""
    from arc_agi import Arcade
    from arcengine import GameAction

    INT_TO_GA = {a.value: a for a in GameAction}

    result = {
        "game": game_prefix,
        "solver": f"{game_prefix}_solver.py",
        "success": False,
        "levels_won": 0,
        "total_levels": 0,
        "actions_used": 0,
        "state": "NOT_STARTED",
        "error": None,
        "per_level": [],
    }

    # Load solver
    solver = load_solver(game_prefix)
    if solver is None:
        result["error"] = "No solver found"
        return result

    # Get solution from solver (it prints to stdout, we capture)
    if verbose:
        print(f"\n{'='*60}")
        print(f"Running {game_prefix} solver against live API...")

    # The solver outputs lines like "Level N: K clicks\n  click(x,y) click(x,y)..."
    # We need to capture its output. Most solvers print when run as __main__.
    # Let's try to call a solve function or capture stdout.

    import io
    from contextlib import redirect_stdout

    old_stdout = sys.stdout
    capture = io.StringIO()
    try:
        sys.stdout = capture
        # Try running the solver's main logic
        if hasattr(solver, 'main'):
            solver.main()
        elif hasattr(solver, 'solve_all'):
            solver.solve_all()
        else:
            # Execute the module-level code by re-running it
            exec(open(os.path.join(SOLVER_DIR, f"{game_prefix}_solver.py")).read(),
                 {"__name__": "__main__"})
    except Exception as e:
        result["error"] = f"Solver execution error: {e}"
        sys.stdout = old_stdout
        if verbose:
            print(f"  Solver failed: {e}")
            traceback.print_exc()
        return result
    finally:
        sys.stdout = old_stdout

    solver_output = capture.getvalue()

    # Parse solver output for click sequences per level
    # Format: "Level N: K clicks\n  click(x,y) click(x,y)..."
    level_actions = {}
    current_level = None
    for line in solver_output.split("\n"):
        line = line.strip()
        if line.startswith("Level "):
            parts = line.split(":")
            try:
                level_num = int(parts[0].replace("Level ", "").strip())
                current_level = level_num
                level_actions[current_level] = []
            except ValueError:
                pass
        elif "click(" in line and current_level is not None:
            # Parse click(x,y) sequences
            import re
            clicks = re.findall(r'click\((\d+),\s*(\d+)\)', line)
            for x, y in clicks:
                level_actions[current_level].append(("click", int(x), int(y)))
        elif any(d in line for d in ["UP", "DOWN", "LEFT", "RIGHT", "SELECT"]) and current_level is not None:
            # Parse directional actions
            action_map = {"UP": 1, "DOWN": 2, "LEFT": 3, "RIGHT": 4, "SELECT": 5}
            for word in line.split():
                if word in action_map:
                    level_actions[current_level].append(("action", action_map[word], 0))

    if not level_actions:
        result["error"] = "Solver produced no action sequences"
        if verbose:
            print(f"  No actions parsed from solver output ({len(solver_output)} chars)")
            print(f"  First 500 chars: {solver_output[:500]}")
        return result

    # Now play the game with the computed actions
    arcade = Arcade()
    game_id, env_info = find_game_id(arcade, game_prefix)
    if not game_id:
        result["error"] = f"Game {game_prefix} not found in API"
        return result

    env = arcade.make(game_id)
    fd = env.reset()
    result["total_levels"] = fd.win_levels
    total_actions = 0

    if verbose:
        print(f"  Game: {game_id}, {fd.win_levels} levels")
        print(f"  Solver produced actions for levels: {sorted(level_actions.keys())}")

    for level_num in sorted(level_actions.keys()):
        actions = level_actions[level_num]
        level_start = fd.levels_completed
        level_actions_used = 0

        if verbose:
            print(f"  Level {level_num+1}: {len(actions)} actions to execute...")

        for action_type, x, y in actions:
            if fd.state.name in ("WON", "LOST", "GAME_OVER"):
                break

            if action_type == "click":
                ga = INT_TO_GA.get(6)
                fd = env.step(ga, data={"x": x, "y": y})
            else:
                ga = INT_TO_GA.get(x)  # x is the action number for non-click
                if ga:
                    fd = env.step(ga)

            total_actions += 1
            level_actions_used += 1

            # Check for level-up
            if fd.levels_completed > level_start:
                if verbose:
                    print(f"    ★ Level {level_num+1} complete after {level_actions_used} actions!")
                result["per_level"].append({
                    "level": level_num + 1,
                    "actions": level_actions_used,
                    "result": "LEVEL_UP"
                })
                break

        if fd.state.name == "WON":
            if verbose:
                print(f"  ★★★ GAME WON! {fd.levels_completed}/{fd.win_levels} levels in {total_actions} actions ★★★")
            result["success"] = True
            result["levels_won"] = fd.levels_completed
            result["actions_used"] = total_actions
            result["state"] = "WON"
            return result

        if fd.state.name in ("LOST", "GAME_OVER"):
            if verbose:
                print(f"  Game over at level {fd.levels_completed + 1} after {total_actions} actions")
            result["levels_won"] = fd.levels_completed
            result["actions_used"] = total_actions
            result["state"] = fd.state.name
            return result

        # If we used all actions for this level but didn't level up
        if fd.levels_completed == level_start:
            if verbose:
                print(f"    Level {level_num+1}: {level_actions_used} actions used, no level-up")
            result["per_level"].append({
                "level": level_num + 1,
                "actions": level_actions_used,
                "result": "NOT_FINISHED"
            })

    result["levels_won"] = fd.levels_completed
    result["actions_used"] = total_actions
    result["state"] = fd.state.name
    if fd.levels_completed == fd.win_levels:
        result["success"] = True
        result["state"] = "WON"

    if verbose:
        status = "WON" if result["success"] else f"{result['levels_won']}/{result['total_levels']}"
        print(f"  Final: {status} in {total_actions} actions")

    return result


def update_db(results):
    """Update SOLUTIONS_DB.json with live verification results."""
    if os.path.exists(DB_PATH):
        with open(DB_PATH) as f:
            db = json.load(f)
    else:
        db = {"_description": "ARC-AGI-3 solution database", "games": {}}

    db["_updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")

    for r in results:
        game = r["game"]
        if game not in db["games"]:
            db["games"][game] = {"levels": r["total_levels"], "solves": []}

        # Add algorithmic solve entry
        entry = {
            "method": "algorithmic",
            "by": "mcnugget",
            "solver": r["solver"],
            "levels_won": r["levels_won"],
            "total_levels": r["total_levels"],
            "actions_used": r["actions_used"],
            "verified_live": r["success"],
            "state": r["state"],
            "date": time.strftime("%Y-%m-%d"),
            "per_level": r.get("per_level", []),
        }
        if r.get("error"):
            entry["error"] = r["error"]

        # Replace existing algorithmic entry or append
        existing = db["games"][game].get("solves", [])
        replaced = False
        for i, s in enumerate(existing):
            if s.get("method") == "algorithmic" and s.get("solver") == r["solver"]:
                existing[i] = entry
                replaced = True
                break
        if not replaced:
            existing.append(entry)
        db["games"][game]["solves"] = existing

    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)
        f.write("\n")

    print(f"\nDatabase updated: {DB_PATH}")


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--all" in args:
        do_update = "--update-db" in args
        results = []
        for game in ALL_GAMES:
            solver_path = os.path.join(SOLVER_DIR, f"{game}_solver.py")
            if not os.path.exists(solver_path):
                print(f"\nSkipping {game} — no solver")
                continue
            try:
                r = run_solver_live(game)
                results.append(r)
            except Exception as e:
                print(f"\n{game}: CRASHED — {e}")
                traceback.print_exc()
                results.append({
                    "game": game, "solver": f"{game}_solver.py",
                    "success": False, "levels_won": 0, "total_levels": 0,
                    "actions_used": 0, "state": "CRASH", "error": str(e)
                })

        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        won = [r for r in results if r["success"]]
        partial = [r for r in results if not r["success"] and r["levels_won"] > 0]
        failed = [r for r in results if not r["success"] and r["levels_won"] == 0]

        print(f"\nFULL WINS ({len(won)}):")
        for r in won:
            print(f"  ✓ {r['game']} {r['levels_won']}/{r['total_levels']} in {r['actions_used']} actions")

        print(f"\nPARTIAL ({len(partial)}):")
        for r in partial:
            print(f"  ~ {r['game']} {r['levels_won']}/{r['total_levels']} in {r['actions_used']} actions")

        print(f"\nFAILED ({len(failed)}):")
        for r in failed:
            err = r.get('error', r.get('state', '?'))
            print(f"  ✗ {r['game']}: {err}")

        if do_update:
            update_db(results)
    elif args:
        game = args[0]
        r = run_solver_live(game)
        if "--update-db" in args:
            update_db([r])
    else:
        print("Usage: python3 run_solver_live.py <game> | --all [--update-db]")
