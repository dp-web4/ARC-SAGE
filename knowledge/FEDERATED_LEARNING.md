# ARC-AGI-3 Federated Learning Architecture
*2026-04-07*

## Design Principles

1. **No git conflicts** — each machine writes ONLY to its own directory
2. **Append-only** — machines never modify shared files, only add new ones
3. **Daily consolidation** — CBP runs a cron that collects, deduplicates, and publishes
4. **Player-attributed** — every learning entry tracks machine + player (model) identity
5. **Structurally encoded** — store patterns and rules, not just action sequences

## Directory Structure

```
shared-context/arc-agi-3/
├── game_coordination.json          # Who's playing what (existing)
├── FEDERATED_LEARNING.md           # This doc
├── fleet-learning/
│   ├── cbp/                        # CBP's local learning (written by CBP only)
│   │   ├── sb26_learning.jsonl     # Per-game learning log
│   │   ├── lp85_learning.jsonl
│   │   └── ...
│   ├── sprout/
│   │   ├── sb26_learning.jsonl
│   │   └── ...
│   ├── mcnugget/
│   ├── legion/
│   ├── nomad/
│   └── thor/
├── consolidated/                   # CBP consolidator output (read by all)
│   ├── game_insights.jsonl         # Deduplicated cross-machine insights
│   ├── structural_patterns.jsonl   # Reusable patterns (hierarchy, palindrome, etc.)
│   ├── level_solutions.jsonl       # Best solutions per game per level
│   └── last_consolidated.json      # Timestamp + stats
└── player/                         # Existing — player identity seeds
    └── seed_identity.json
```

## Per-Machine Learning Log Format

Each machine appends to `fleet-learning/{machine}/{game}_learning.jsonl`:

```jsonl
{"timestamp": "2026-04-07T10:58:00", "machine": "cbp", "player": "claude", "game": "sb26", "level": 7, "event": "level_solved", "actions": 17, "baseline": 17, "structural_pattern": "nested_palindrome", "rule": "each box = [own_color, child_color, own_color]", "meta": "palindrome indicator = nesting depth"}
{"timestamp": "2026-04-07T10:58:30", "machine": "cbp", "player": "claude", "game": "sb26", "level": 8, "event": "game_complete", "actions": 17, "baseline": 17, "structural_pattern": "cross_group_identity", "rule": "each group ends with other group identity color", "meta": "mutual acknowledgment between groups"}
{"timestamp": "2026-04-07T11:00:00", "machine": "cbp", "player": "claude", "game": "sb26", "level": -1, "event": "game_insight", "insight": "paradigm_shift_at_level_6", "description": "L1-5 use pick-and-place, L6+ uses swap. Same structural rules, different interaction mechanic."}
```

Event types:
- `level_solved` — level cleared, includes solution + pattern
- `level_failed` — level attempted, includes what was tried + why it failed
- `game_complete` — all levels cleared
- `game_insight` — cross-level or game-level observation
- `structural_pattern` — reusable pattern (transferable across games)

## Consolidator (CBP daily cron)

`shared-context/arc-agi-3/consolidate.py`:

1. **Collect**: Read all `fleet-learning/{machine}/*.jsonl` files
2. **Deduplicate**: Same game+level+pattern from multiple machines → keep the one with fewest actions
3. **Extract patterns**: Find structural patterns that appear across multiple games
4. **Publish**: Write to `consolidated/` directory
5. **Prune**: Keep only last 30 days of raw per-machine logs

### Consolidation rules:
- Best solution per game per level = fewest actions within baseline
- Structural patterns confirmed by 2+ machines get `confidence: high`
- Game insights are merged (not deduplicated — different machines see different things)
- Level failures are kept (they teach what doesn't work)

## How Machines Use Consolidated Data

On session start, each machine's solver reads `consolidated/`:
- `game_insights.jsonl` → Layer 3 membot context
- `structural_patterns.jsonl` → Layer 4 metacognitive principles (dynamic)
- `level_solutions.jsonl` → known solutions for replay

This is READ-ONLY for all machines except CBP's consolidator. No git conflicts.

## How Claude (interactive) Contributes

When I solve a game through `claude_solver.py`, the session data includes:
- Full action sequences per level
- Structural patterns discovered
- Level-up summaries with rules

On session end, a `publish_learning.py` script extracts the learning entries from `session.json` and appends them to `fleet-learning/cbp/` (or whatever machine I'm running on).

## How Local Models Contribute

The v7/v9 solvers already produce GameKB data. A post-session hook extracts:
- Per-level best attempts (actions, changes, level-ups)
- Discovered mechanics (from KB)
- Failed approaches (from KB)

Writes to `fleet-learning/{machine}/{game}_learning.jsonl`.

## Cron Schedule

```bash
# CBP crontab
0 4 * * * python3 shared-context/arc-agi-3/consolidate.py >> /tmp/consolidate.log 2>&1
```

Runs at 4am daily (before the fleet's raising cron). All machines pull shared-context at session start and get the latest consolidated data.

## Migration from Current State

1. Create `fleet-learning/` directories for each machine
2. Extract existing GameKB data into learning log format
3. Write consolidator script
4. Add post-session hooks to solvers
5. Update v7 context assembly to read `consolidated/`
