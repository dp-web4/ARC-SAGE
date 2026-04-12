#!/usr/bin/env python3
"""
Fleet Learning Consolidator — runs on CBP daily at 4am.

Collects per-machine learning logs, deduplicates, extracts patterns,
publishes consolidated insights for the fleet.

Usage:
    python3 consolidate.py              # Full consolidation
    python3 consolidate.py --dry-run    # Show what would be consolidated
    python3 consolidate.py --stats      # Show fleet learning stats

Cron: 0 4 * * * cd /path/to/shared-context && python3 arc-agi-3/consolidate.py
"""

import json
import os
import time
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent
FLEET_DIR = BASE_DIR / "fleet-learning"
CONSOLIDATED_DIR = BASE_DIR / "consolidated"
CONSOLIDATED_DIR.mkdir(exist_ok=True)


def load_all_entries():
    """Load all learning entries across all machines."""
    entries = []
    for machine_dir in sorted(FLEET_DIR.iterdir()):
        if not machine_dir.is_dir():
            continue
        machine = machine_dir.name
        for jsonl_file in sorted(machine_dir.glob("*.jsonl")):
            with open(jsonl_file) as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        entry["_source_machine"] = machine
                        entry["_source_file"] = jsonl_file.name
                        entries.append(entry)
                    except json.JSONDecodeError:
                        print(f"  WARN: bad JSON in {machine}/{jsonl_file.name}:{line_num}")
    return entries


def consolidate_solutions(entries):
    """Find best solution per game per level (fewest actions within baseline)."""
    solutions = {}  # (game, level) → best entry
    for e in entries:
        if e.get("event") != "level_solved":
            continue
        key = (e.get("game"), e.get("level"))
        actions = e.get("actions", 999)
        current_best = solutions.get(key)
        if current_best is None or actions < current_best.get("actions", 999):
            solutions[key] = e
    return sorted(solutions.values(), key=lambda x: (x.get("game", ""), x.get("level", 0)))


def consolidate_patterns(entries):
    """Extract structural patterns, boost confidence if seen by multiple machines."""
    patterns = {}  # pattern_name → {entry, machines}
    for e in entries:
        if e.get("event") != "structural_pattern":
            continue
        name = e.get("pattern", "")
        if not name:
            continue
        if name not in patterns:
            patterns[name] = {"entry": e, "machines": set(), "games": set()}
        patterns[name]["machines"].add(e.get("_source_machine", ""))
        for g in e.get("games_confirmed", []):
            patterns[name]["games"].add(g)

    result = []
    for name, data in sorted(patterns.items()):
        entry = dict(data["entry"])
        entry["machines_confirmed"] = sorted(data["machines"])
        entry["games_confirmed"] = sorted(data["games"])
        entry["confidence"] = "high" if len(data["machines"]) >= 2 else entry.get("confidence", "medium")
        # Remove internal fields
        entry.pop("_source_machine", None)
        entry.pop("_source_file", None)
        result.append(entry)
    return result


def consolidate_insights(entries):
    """Collect game insights, deduplicate by description similarity."""
    insights = []
    seen_descriptions = set()
    for e in entries:
        if e.get("event") not in ("game_insight", "game_complete"):
            continue
        desc = e.get("description", e.get("insight", ""))[:100]
        if desc in seen_descriptions:
            continue
        seen_descriptions.add(desc)
        entry = dict(e)
        entry.pop("_source_machine", None)
        entry.pop("_source_file", None)
        insights.append(entry)
    return insights


def write_jsonl(path, entries):
    with open(path, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry, default=str) + "\n")


def consolidate(dry_run=False):
    entries = load_all_entries()
    print(f"Loaded {len(entries)} entries from fleet")

    # Count by machine
    by_machine = defaultdict(int)
    by_game = defaultdict(int)
    by_event = defaultdict(int)
    for e in entries:
        by_machine[e.get("_source_machine", "?")] += 1
        by_game[e.get("game", "?")] += 1
        by_event[e.get("event", "?")] += 1

    print(f"\nBy machine: {dict(by_machine)}")
    print(f"By game: {dict(by_game)}")
    print(f"By event: {dict(by_event)}")

    solutions = consolidate_solutions(entries)
    patterns = consolidate_patterns(entries)
    insights = consolidate_insights(entries)

    print(f"\nConsolidated: {len(solutions)} solutions, {len(patterns)} patterns, {len(insights)} insights")

    if dry_run:
        print("\n[DRY RUN — not writing files]")
        for s in solutions:
            print(f"  Solution: {s.get('game')} L{s.get('level')} = {s.get('actions')} actions ({s.get('player')})")
        for p in patterns:
            print(f"  Pattern: {p.get('pattern')} — {p.get('confidence')} ({p.get('machines_confirmed')})")
        return

    write_jsonl(CONSOLIDATED_DIR / "level_solutions.jsonl", solutions)
    write_jsonl(CONSOLIDATED_DIR / "structural_patterns.jsonl", patterns)
    write_jsonl(CONSOLIDATED_DIR / "game_insights.jsonl", insights)

    meta = {
        "last_consolidated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_entries": len(entries),
        "machines": dict(by_machine),
        "games": dict(by_game),
        "solutions": len(solutions),
        "patterns": len(patterns),
        "insights": len(insights),
    }
    with open(CONSOLIDATED_DIR / "last_consolidated.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\nWritten to {CONSOLIDATED_DIR}/")


def show_stats():
    meta_path = CONSOLIDATED_DIR / "last_consolidated.json"
    if not meta_path.exists():
        print("No consolidation yet. Run: python3 consolidate.py")
        return
    with open(meta_path) as f:
        meta = json.load(f)
    print(f"Last consolidated: {meta.get('last_consolidated')}")
    print(f"Total entries: {meta.get('total_entries')}")
    print(f"Machines: {meta.get('machines')}")
    print(f"Games: {meta.get('games')}")
    print(f"Solutions: {meta.get('solutions')}")
    print(f"Patterns: {meta.get('patterns')}")
    print(f"Insights: {meta.get('insights')}")


if __name__ == "__main__":
    import sys
    if "--dry-run" in sys.argv:
        consolidate(dry_run=True)
    elif "--stats" in sys.argv:
        show_stats()
    else:
        consolidate()
