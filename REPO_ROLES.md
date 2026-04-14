# Repository Roles

This project spans multiple repositories. Each has a distinct role. Contributors
should know which is authoritative for what.

## Primary repos

### ARC-SAGE (this repo) — source of truth for games
**License**: MIT-0 (MIT No Attribution — public-domain-effective, required for ARC Prize 2026 Paper Track eligibility)
**Public**: yes (flipped public 2026-04-13)
**Authoritative for**:
- Game solvers (`arc-agi-3/experiments/*.py`)
- Visual memory (`knowledge/visual-memory/`)
- Per-game mechanics docs (`knowledge/game-mechanics/`)
- Game coordination state (`knowledge/game_coordination.json`)
- Solutions JSON files
- Capture infrastructure (`arc-agi-3/experiments/capture_visuals.py`, `game_viewer.py`)
- Documentation scoped to ARC-AGI-3

Game work happens here first. Milestones flow outward to SAGE.

### dp-web4/SAGE — milestone mirror for games, primary for core research
**License**: AGPL-3.0
**Public**: yes
**Authoritative for**:
- SAGE kernel, IRP plugin framework, consciousness loop
- Raising / training / daemon / identity / federation
- Cross-machine fleet coordination
- Broader research infrastructure

**Mirror role for games**: Receives milestone updates from ARC-SAGE (completed solves,
tagged versions of `capture_visuals.py` / `game_viewer.py`, curated world-model docs).
Not the place to do day-to-day game solver development.

### dp-web4/shared-context — fleet coordination
**License**: private
**Authoritative for**:
- Fleet-wide plans, strategic docs, insights
- Cross-machine learning logs per instance
- Fleet broadcasts
- Anything that coordinates multiple machines

Game coordination JSON lives here canonically but is mirrored into ARC-SAGE's
`knowledge/` for readers who only clone ARC-SAGE.

### dp-web4/private-context — local-only
**License**: private
**Authoritative for**:
- Per-machine session logs
- Strategy documents (competition plans, outreach plans)
- Collaborator profiles and internal notes
- Insights that shouldn't leave the core team

Never syncs outward. Git-ignored contents include machine-specific credentials.

### project-you-apps/membot — memory subsystem
**License**: MIT
**Owner**: Andy Grossberg / Waving Cat Learning Systems
**Authoritative for**:
- Paired-lattice cartridge format
- Grid-aware visual retrieval (`vision/grid_cartridge.py`)
- Federation protocol

ARC-SAGE vendors a curated subset in `membot/` for competition submission
self-containment. Master copy remains Andy's repo.

## Flow rules

### Game solver work
1. Develop in ARC-SAGE (`arc-agi-3/experiments/`)
2. Visual memory + solutions land here first
3. On milestone (new game solved, major mechanic decoded), mirror to SAGE
4. On tagged release, mirror to SAGE with a version tag

### Core SAGE work
1. Develop in SAGE
2. On milestone that affects game capture/replay (e.g., IRP framework changes),
   mirror relevant files to ARC-SAGE

### Shared infrastructure (game_viewer.py, capture_visuals.py)
Lives in both. Use `arc-agi-3/experiments/sync_viewer.sh` or manual copy.
ARC-SAGE is authoritative — if they diverge, ARC-SAGE wins.

## Why split like this?

**Competition submission requires public-domain-permissive licensing** (ARC Prize 2026
mandates CC0 or MIT-0 for paper-track-eligible code). SAGE is AGPL because it's part
of the broader dp-web4 research ecosystem that's intentionally share-alike. Can't
submit AGPL code to the ARC Prize. So we split: the submittable slice lives in
ARC-SAGE under MIT-0; the broader research stays AGPL in SAGE.

**Scoping keeps each repo focused.** ARC-SAGE is "here's a working ARC-AGI-3
agent." SAGE is "here's the research framework that produced it." Different
audiences, different contributor pools, different update cadences.
