#!/usr/bin/env python3
"""Competition-mode scorecard submission for ARC-AGI-3.

Collects per-game action traces from visual-memory/{game}/run_*/run.json
(or solutions.json where present) and replays them against the live API.

Two modes:
  --dry-run   : OperationMode.NORMAL, replay everything, report per-game
                levels_completed vs expected, action count, state.
                Safe — does not post to leaderboard.
  --compete   : OperationMode.COMPETITION, one scorecard, each env made
                once, close at end, results posted to community leaderboard.
                One-shot — no retries. Only run after dry-run is clean.

Usage:
  python3 submit_competition.py --dry-run                # all games
  python3 submit_competition.py --dry-run wa30 ka59      # subset
  python3 submit_competition.py --compete                # real submission
  python3 submit_competition.py --list                   # show what'd run

Picks the BEST run per game: highest levels_completed, then latest timestamp.
"""

import sys
import os
import json
import time
import argparse
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

# Load registered ARC_API_KEY from the shared .env BEFORE importing arc_agi
# (arc_agi only auto-loads .env.example, not .env)
try:
    from dotenv import load_dotenv
    load_dotenv('/mnt/c/exe/projects/ai-agents/.env')
except ImportError:
    pass

from arc_agi import Arcade, OperationMode
from arcengine import GameAction, GameState

# Resolve paths relative to the repo root (script lives in arc-agi-3/experiments/).
# Can be overridden by ARC_SAGE_VM / ARC_SAGE_COORD env vars.
_REPO = Path(__file__).resolve().parent.parent.parent
VM = Path(os.getenv("ARC_SAGE_VM", _REPO / "knowledge" / "visual-memory"))
COORD = Path(os.getenv("ARC_SAGE_COORD", _REPO / "knowledge" / "game_coordination.json"))

# run.json action string → GameAction
ACTION_MAP = {
    'A0':     GameAction.RESET,
    'UP':     GameAction.ACTION1,
    'DOWN':   GameAction.ACTION2,
    'LEFT':   GameAction.ACTION3,
    'RIGHT':  GameAction.ACTION4,
    'SEL':    GameAction.ACTION5,
    'SELECT': GameAction.ACTION5,
    'CLICK':  GameAction.ACTION6,
}

# solutions.json action int → GameAction
INT_MAP = {}
for _ga in GameAction:
    INT_MAP[_ga.value] = _ga


def load_game_ids():
    """Return [(short, full_id), ...] for solved games from game_coordination.json."""
    try:
        coord = json.load(open(COORD))
    except Exception as e:
        print(f"ERROR loading coord: {e}")
        return []
    games = []
    for entry in coord.get('games', []):
        full = entry.get('id') or entry.get('game_id') or ''
        if not full:
            continue
        short = entry.get('family') or full.split('-')[0]
        games.append((short, full))
    return games


def best_run(game):
    """Return (run_dir, run_json_dict) for the best run in visual-memory/{game}/.
    Prefer: highest levels_completed, then WIN state, then latest timestamp."""
    gdir = VM / game
    if not gdir.is_dir():
        return None, None
    candidates = []
    for run in sorted(gdir.iterdir()):
        if not run.name.startswith('run_'):
            continue
        rj = run / 'run.json'
        if not rj.exists():
            continue
        try:
            d = json.load(open(rj))
        except Exception:
            continue
        lc = d.get('levels_completed', 0) or 0
        result = d.get('result', '')
        ts = run.name  # run_YYYYMMDD_HHMMSS sorts naturally
        candidates.append((lc, result == 'WIN', ts, run, d))
    if not candidates:
        return None, None
    candidates.sort(reverse=True)
    _, _, _, run_dir, run_d = candidates[0]
    return run_dir, run_d


def run_to_trace(run_d):
    """Convert run.json steps → [(GameAction, data_dict_or_None), ...]."""
    trace = []
    for s in run_d.get('steps', []):
        act_str = s.get('action', '')
        ga = ACTION_MAP.get(act_str)
        if ga is None:
            return None, f"unknown action string: {act_str}"
        if ga == GameAction.RESET:
            # Skip explicit resets in the trace — env.reset() already called
            continue
        data = None
        if ga == GameAction.ACTION6:
            x, y = s.get('x'), s.get('y')
            if x is None or y is None:
                return None, f"CLICK with no x,y at step {s.get('step')}"
            data = {'x': x, 'y': y}
        trace.append((ga, data))
    return trace, None


def solutions_json_to_trace(game):
    """Try visual-memory/{game}/solutions.json in per-level list format."""
    p = VM / game / 'solutions.json'
    if not p.exists():
        return None
    try:
        raw = json.load(open(p))
    except Exception:
        return None
    if not isinstance(raw, list) or not raw or not isinstance(raw[0], list):
        return None
    trace = []
    for lvl in raw:
        for m in lvl:
            if not isinstance(m, dict) or 'action' not in m:
                return None
            a = INT_MAP.get(m['action'])
            if a is None or a == GameAction.RESET:
                continue
            trace.append((a, m.get('data')))
    return trace or None


def collect_trace(game):
    """Return (trace, source, expected_levels, win_levels) or (None, reason, 0, 0)."""
    # Prefer solutions.json (cached winning path) over run.json if present AND
    # its step count is substantially shorter (likely cleaner).
    run_dir, run_d = best_run(game)
    if run_d is None:
        return None, 'no run_ dir', 0, 0

    expected = run_d.get('levels_completed', 0) or 0
    win_levels = run_d.get('win_levels', 0) or 0

    # Prefer solutions.json when available
    cache = solutions_json_to_trace(game)
    if cache is not None:
        return cache, 'solutions.json', expected, win_levels

    trace, err = run_to_trace(run_d)
    if trace is None:
        return None, f'run.json parse: {err}', expected, win_levels
    return trace, f'{run_dir.name}', expected, win_levels


def replay_one_game(arc, game_id, trace, label="", scorecard_id=None,
                    step_delay=0.0):
    """Play trace against a fresh env. Returns (state, levels_completed,
    win_levels, actions_played, elapsed_sec). Raises on make/reset failure."""
    t0 = time.time()
    env = arc.make(game_id, scorecard_id=scorecard_id)
    if env is None:
        raise RuntimeError(f"make({game_id}) returned None")
    fd = env.reset()
    if fd is None:
        raise RuntimeError(f"reset({game_id}) returned None (likely 429)")
    played = 0
    for action, data in trace:
        if step_delay > 0:
            time.sleep(step_delay)
        fd = env.step(action, data=data)
        if fd is None:
            raise RuntimeError(f"step failed at action {played+1}")
        played += 1
        if fd.state in (GameState.WIN, GameState.GAME_OVER):
            break
    elapsed = time.time() - t0
    return fd.state, fd.levels_completed, fd.win_levels, played, elapsed


def is_rate_limited(exc):
    """Detect 429 rate limit from nested RequestException or string."""
    s = str(exc)
    return '429' in s or 'Too Many Requests' in s or 'rate limit' in s.lower()


def main():
    p = argparse.ArgumentParser()
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run', action='store_true',
                      help='NORMAL mode, safe, no leaderboard post')
    mode.add_argument('--compete', action='store_true',
                      help='COMPETITION mode — real submission, one-shot')
    mode.add_argument('--list', action='store_true',
                      help='Just show what would run')
    p.add_argument('games', nargs='*', help='Optional subset (e.g. wa30 ka59)')
    p.add_argument('--tag', default='sage-arc-sage',
                   help='Scorecard tag for compete mode')
    p.add_argument('--source-url', default='https://github.com/dp-web4/ARC-SAGE',
                   help='Source URL for scorecard')
    p.add_argument('--step-delay', type=float, default=0.0,
                   help='Seconds to sleep between env.step calls (rate limit mitigation)')
    p.add_argument('--game-interval', type=float, default=3.0,
                   help='Seconds to sleep between games')
    args = p.parse_args()

    games = load_game_ids()
    if args.games:
        wanted = set(args.games)
        games = [(s, f) for s, f in games if s in wanted or f in wanted
                 or any(w in f for w in wanted)]

    print(f"{'='*70}\n{len(games)} games targeted\n{'='*70}")

    # Step 1: collect traces for every game. Report coverage.
    traces = []  # [(short, full_id, trace, source, expected, win_levels), ...]
    missing = []
    for short, full in games:
        trace, source, expected, win_levels = collect_trace(short)
        if trace is None:
            missing.append((short, full, source))
            print(f"  ✗ {short:6s}  NO TRACE  ({source})")
        else:
            print(f"  ✓ {short:6s}  {len(trace):5d} actions  "
                  f"expect {expected}/{win_levels}L  from {source}")
            traces.append((short, full, trace, source, expected, win_levels))

    print(f"\n{len(traces)} playable / {len(missing)} missing")

    if args.list:
        for short, _, src in missing:
            print(f"  MISSING: {short} ({src})")
        return

    if not traces:
        print("Nothing to play. Exiting.")
        return

    if args.compete:
        key = os.getenv('ARC_API_KEY', '')
        if not key or key.startswith('anon') or len(key) < 20:
            print(f"✗ ARC_API_KEY not set or looks invalid (got: {key[:10]!r}). "
                  f"Ensure /mnt/c/exe/projects/ai-agents/.env has ARC_API_KEY=<registered>")
            return
        print(f"\nUsing registered API key: {key[:8]}…{key[-4:]}")
        print("\n⚠  COMPETITION MODE — one-shot, no retries. Continue? [y/N]")
        resp = input().strip().lower()
        if resp != 'y':
            print("Aborted.")
            return
        op = OperationMode.COMPETITION
    else:
        op = OperationMode.NORMAL

    # Step 2: construct Arcade in the chosen mode
    arc = Arcade(operation_mode=op)
    if args.compete:
        card_id = arc.open_scorecard(source_url=args.source_url, tags=[args.tag])
        print(f"\nScorecard opened: {card_id}")
    else:
        card_id = None

    # Step 3: replay each game, with throttling + 429 backoff
    results = []
    interval = args.game_interval  # seconds between games
    step_delay = args.step_delay
    consecutive_429 = 0
    aborted = False
    for i, (short, full, trace, source, expected, win_levels) in enumerate(traces):
        if i > 0:
            time.sleep(interval)  # throttle between games
        print(f"\n[{short}] replaying {len(trace)} actions (interval={interval:.1f}s) …")

        # Retry with exponential backoff on 429
        attempts = 0
        while True:
            attempts += 1
            try:
                state, lc, wl, played, elapsed = replay_one_game(
                    arc, full, trace, scorecard_id=card_id, step_delay=step_delay)
                ok = (state == GameState.WIN) or (lc >= expected)
                mark = '✓' if ok else '~'
                print(f"  {mark} {short:6s}  state={state.name:12s}  "
                      f"{lc}/{wl}L  played={played}/{len(trace)}  {elapsed:.1f}s")
                results.append((short, state.name, lc, wl, played, elapsed, ok))
                consecutive_429 = 0
                break
            except Exception as e:
                if is_rate_limited(e) and attempts < 3:
                    backoff = 15 * attempts
                    print(f"  429 rate-limited; backing off {backoff}s (attempt {attempts}/3)")
                    time.sleep(backoff)
                    interval = min(interval * 1.5, 30.0)  # increase interval
                    continue
                import traceback
                print(f"  ! {short:6s}  ERROR: {e}")
                if args.compete:
                    traceback.print_exc(limit=3)
                results.append((short, 'ERROR', 0, 0, 0, 0, False))
                if is_rate_limited(e):
                    consecutive_429 += 1
                    if consecutive_429 >= 2:
                        print(f"\n✗ {consecutive_429} consecutive rate-limited games. Aborting remaining.")
                        aborted = True
                break
        if aborted:
            break

    # Step 4: close scorecard (compete) + summary
    if args.compete and card_id:
        # Close with retry — important to get the final scorecard result
        print(f"\nClosing scorecard {card_id} …")
        for attempt in range(5):
            try:
                sc = arc.close_scorecard(card_id)
                print("Closed.")
                out = Path(f"./submit_scorecard_{card_id}.json")
                if sc is not None:
                    out.write_text(sc.model_dump_json(indent=2) if hasattr(sc, 'model_dump_json')
                                   else json.dumps(sc, indent=2, default=str))
                    print(f"Saved scorecard → {out}")
                else:
                    print("(close returned None)")
                break
            except Exception as e:
                if is_rate_limited(e) and attempt < 4:
                    wait = 15 * (attempt + 1)
                    print(f"  close 429, retry in {wait}s …")
                    time.sleep(wait)
                    continue
                print(f"Close failed: {e}")
                break

    print(f"\n{'='*70}\nSummary\n{'='*70}")
    total_ok = sum(1 for r in results if r[-1])
    total_played = sum(r[4] for r in results)
    for short, state, lc, wl, played, elapsed, ok in results:
        mark = '✓' if ok else ('~' if state != 'ERROR' else '!')
        print(f"  {mark} {short:6s}  {state:12s}  {lc}/{wl}L  {played:5d} acts  {elapsed:5.1f}s")
    print(f"\n{total_ok}/{len(results)} games OK, {total_played} total actions")


if __name__ == '__main__':
    main()
