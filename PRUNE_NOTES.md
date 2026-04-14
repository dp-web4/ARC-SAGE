# Prune Notes

This repo was created by copying relevant material from multiple private/internal
sources, organized here as a single source of truth, with the intent to prune
toward a clean public release.

The full-copy-then-prune approach preserves provenance: what was considered
worth including, and what was removed and why.

## Sources

| Source | License | Path in ARC-SAGE | Notes |
|--------|---------|------------------|-------|
| dp-web4/SAGE (arc-agi-3/) | AGPL-3.0 (private) | `arc-agi-3/` | Solvers, agent infrastructure, world models |
| dp-web4/SAGE (environment_files/) | MIT (via arc-agi SDK) | `environment_files/` | ARC-AGI-3 game engines |
| dp-web4/SAGE (sage/irp/) | AGPL-3.0 (private) | `sage-infrastructure/irp/` | IRP plugin framework |
| dp-web4/shared-context (arc-agi-3/) | Private | `knowledge/` | Fleet learning, game mechanics, visual memory |
| project-you-apps/membot | MIT (public) | `membot/` | Memory system (Andy Grossberg's work, curated subset) |

## What Was Included

Everything currently in this repo should be traceable to one of the sources above.
See git log for the initial import commit — the initial state is the full copy.

## What Was Explicitly Excluded

### From shared-context (private repo)
- `plans/` — Strategic plans for competition, research direction
- `arc-agi-3/insights/` — Cross-game strategic analysis documents
- `arc-agi-3/COMPETITION_PLAN.md` — Competition strategy document
- `arc-agi-3/DISPUTED_CLAIMS.md` — Internal team dispute records

### From membot (public but too large)
- `data/` — Training data and cached cartridges
- `cartridges/` (large files) — Pre-built cartridges from other projects
- `machines/` — Machine-specific configuration
- `__pycache__/` — Python cache
- `*.log` — Log files
- Large model weights

### From SAGE (AGPL, not ARC-relevant)
- `sage/raising/` — Model training pipeline
- `sage/daemon/` — Autonomous operation daemon
- `sage/identity/` — Identity protection system
- `sage/instances/` — Per-machine SAGE instance data
- `sage/federation/` — Fleet coordination
- `sage/web4/` — Web4 trust infrastructure
- Most of `sage/` not directly related to ARC-AGI-3 gameplay

## Pruning Plan

The following phases are planned before public release:

### Phase 1: Verify inclusion (done by initial import)
- [x] Copy everything plausibly relevant
- [x] Document exclusions
- [x] Make private GitHub repo

### Phase 2: Scrub
- [ ] Review every file for machine-specific IPs, internal URLs, credentials
- [ ] Review fleet-learning/ for references to private infrastructure
- [ ] Check consolidate.py and related scripts for private paths
- [ ] Audit game_coordination.json (names, disputes)

### Phase 3: Structural reorganization
- [ ] Decide: per-game directories (`games/re86/`) vs flat (current)
- [ ] Move solver files into coherent structure
- [ ] Create `arc_sage/` package layout for importability
- [ ] Separate runtime code from research notes

### Phase 4: Remove duplicates
- [ ] Many solvers exist in multiple versions (e.g., `re86_solve.py`, `re86_l8_solution.py`, `re86_solutions.json`)
- [ ] Keep the verified final versions, archive or delete obsolete ones

### Phase 5: Membot subset
- [ ] With Andy's input, decide which membot components are actually used by ARC-SAGE
- [ ] Replace full copy with minimal interface + pointer to main repo

### Phase 6: Documentation
- [ ] Per-game README linking solver to mechanics doc to visual memory
- [ ] Top-level architecture diagram
- [ ] "How to run" instructions verified on a clean install

### Phase 7: Review
- [ ] Andy's review (collaborator access)
- [ ] dp's final review
- [ ] Flip to public

## Provenance Discipline

Every time we prune something, add a one-line note here explaining what was
removed and why. The goal is that a future reader (including our future selves)
can understand not just what's in the repo, but the process that shaped it.

## Initial Import Commit

The very first git commit in this repo represents the full unfiltered copy.
Everything after is pruning, reorganization, or new development.

## Prune Log

### 2026-04-14 — License switch MIT → MIT-0

Switched top-level LICENSE from MIT to MIT-0 (MIT No Attribution) to meet
ARC Prize 2026 Paper Track eligibility requirement (CC0 or MIT-0 — public
domain). Dropped the "above copyright notice … shall be included" clause.
Vendored dependencies retain their own upstream licenses: `membot/` stays
MIT per Andy Grossberg's upstream; SDK-sourced `environment_files/` stay MIT
per arc-agi SDK upstream. Submitter-authored code (everything else) is now
effectively public domain.

### 2026-04-13 — AGPL removal for MIT compatibility

Removed AGPL-licensed SAGE research code and every file that imported from
`sage.*` or `sage.irp.*`. ARC-SAGE is MIT; bundling AGPL code would be a
license conflict. These files were scaffolding used during world-model
discovery but are not part of the submission pipeline (which uses per-game
solvers → `solutions.json` / `run.json` → `submit_competition.py`).

- `sage-infrastructure/` (97 files, 1.1MB) — IRP plugin framework (AGPL)
- `arc-agi-3/experiments/deprecated/` (13 files) — archived solver versions
- `arc-agi-3/experiments/sage_game_runner*.py` — historical SAGE-integrated runners
- `arc-agi-3/experiments/sage_solver.py` + `solver_*.py` + `model_backend.py` — v11 interactive solver stack
- `arc-agi-3/experiments/sweep_all_games.py`, `test_imports.py`, `thor_game_runner.py`, `mcnugget_grid_vision_test.py` — sage.irp-dependent utilities

The actual submission pipeline (regen_all_visuals, submit_competition,
per-game solvers, SessionWriter) uses none of the removed code.

### 2026-04-13 — README updates

- Replaced stale "SAGE Entry" framing in arc-agi-3/README.md with
  ARC-SAGE-specific scope
- Removed references to private `shared-context/` paths in favor of
  local `knowledge/` mirror
- Added scorecard result (84.9%) to top-level README
- Removed links to `private-context/` insights
