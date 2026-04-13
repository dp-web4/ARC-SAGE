# Reproducing the 84.9% Scorecard

This repo bundles everything needed to reproduce [scorecard `c0d62617`](https://arcprize.org/scorecards/c0d62617-a0bc-4100-bb4e-982fa5d7fde7) on the ARC-AGI-3 community leaderboard: 21/25 environments, 160/183 levels, 5,159 actions, overall 84.9%.

## What you need

- Python 3.12 (3.10+ should work)
- An ARC-AGI-3 API key from <https://three.arcprize.org> (free, register your email). Put it in a `.env` file at the repo root: `ARC_API_KEY=<your key>`
- `pip install arc-agi python-dotenv pyyaml requests`

## Quick verification — does the data replay?

The safest test first. This runs every game against the SDK in NORMAL mode (local engine, no network, no scorecard), using the cached action traces in `knowledge/visual-memory/`.

```bash
cd arc-agi-3/experiments
python3 submit_competition.py --dry-run
```

Expected: `24/24 games OK, 5345 total actions` with 22 WIN states, `dc22` and `sb26` NOT_FINISHED (intentional partial solves), and `lf52` absent (no captured trace — known limitation).

If this fails for you, open an issue — it's a local environment problem, not a live-API problem.

## Real submission — live competition scorecard

```bash
python3 submit_competition.py --compete
```

This will:
1. Validate `ARC_API_KEY` is set and looks registered (not anonymous)
2. Open a COMPETITION-mode scorecard via the arcprize.org API
3. For each of 24 games, load the cached trace and replay it through the live API (~14 min total, throttled to avoid 429s)
4. Close the scorecard; your result appears at `https://arcprize.org/scorecards/<new-id>`

You'll get approximately the same 84.9% — slight variance possible from server-side rounding or level baseline updates.

**One-shot semantics.** Each `env.make()` in COMPETITION mode is one-shot per game. If your network blips, that game scores zero. The script has throttling + 429 backoff, but no magic. Run on a stable connection.

## Where the data comes from

This repo is the result of a ~2-week multi-agent development process. The action traces in `knowledge/visual-memory/` are the OUTPUT of that process, not the process itself. Reproducing the *score* uses only the cached traces. Reproducing the *development* (solving the games from scratch) requires the solvers in `arc-agi-3/experiments/` plus substantial Opus 4.6 agent time for frame-questioning and mechanic decoding.

Per-game solver files (`<game>_solve*.py`) can be re-run to verify they produce the same action sequences:

```bash
python3 arc-agi-3/experiments/wa30_solve_final.py   # re-solves wa30
python3 arc-agi-3/experiments/regen_all_visuals.py  # regenerates all visual-memory runs
```

Most solvers cache their winning sequences in `visual-memory/<game>/solutions.json` or as module-level `all_solutions` / `KNOWN_SOLUTIONS` constants.

## What's NOT here

- **`lf52` action trace** — the partial solve (6/10 legitimate) was never captured as a replayable `run.json`. The solver can re-derive it but takes ~5 min per level of search. To recover this, patch `lf52_solve_final.py` to cache winning sequences to `visual-memory/lf52/solutions.json` (same format as dc22 uses), then run `regen_all_visuals.py lf52`.

- **Live training / fleet coordination code** — the multi-machine fleet infrastructure that ran these solvers across 6 machines lives in the private `shared-context` repo. Not needed for replay or submission; relevant for understanding *how* the solves were developed.

- **SAGE cognition loop, raising framework, membot internals** — these sit in adjacent public repos (`dp-web4/SAGE` — AGPL, `dp-web4/membot` — MIT). ARC-SAGE is deliberately scoped to the game-solving surface.

## Contact

Questions or issues reproducing: open a GitHub issue on this repo or email `dp@metalinxx.io`.
