# ARC-AGI-3 Knowledge Map

*Where everything lives, what format it's in, and how to use it.*

Last updated: 2026-04-12 by CBP (fleet supervisor).

## Knowledge Flow

```
Interactive play / Source analysis
        ↓
Fleet Learning (per-machine JSONL + world models)
        ↓
Consolidation (daily cron, CBP 4am)
        ↓
Membot Cartridge (kb.cart.npz — semantic search)
        ↓
Solver Context (loaded on game init)
        ↓
Competition Model (gemma4 in sandbox)
```

## Fleet Status: 21/25 Games Solved (84%)

| Game | Type | Solved By | Actions | Baseline | Eff |
|------|------|-----------|---------|----------|-----|
| cd82 | move+click | nomad | 127 | 136 | 1.1x |
| sb26 | move+click | cbp | 140 | 153 | 1.1x |
| ft09 | click | mcnugget | 75 | 163 | 2.2x |
| sc25 | move+click | cbp | 171 | 216 | 1.3x |
| tn36 | click | cbp | 119 | 250 | 2.1x |
| vc33 | click | cbp | 167 | 307 | 1.8x |
| tr87 | move | cbp | 137 | 317 | 2.3x |
| tu93 | move | cbp | 189 | 378 | 2.0x |
| lp85 | click | mcnugget | 117 | 422 | 3.6x |
| sp80 | move+click | thor | — | 472 | — |
| ls20 | move | sprout | 309 | 546 | 1.8x |
| su15 | move+click | cbp | — | 566 | — |
| ar25 | move+click | thor | — | 577 | — |
| s5i5 | click | mcnugget | 100 | 608 | 6.1x |
| bp35 | move+click | sprout | 304 | 637 | 2.1x |
| cn04 | move+click | thor | — | 779 | — |
| re86 | move | cbp | 606 | 1071 | 1.8x |
| m0r0 | move+click | cbp | 181 | 970 | 5.4x |
| r11l | move+click | cbp | 158 | 167 | 1.1x |
| g50t | move | cbp | 311 | 575 | 1.8x |
| ka59 | move+click | cbp | 239 | 826 | 3.5x |

**Solves by machine**: CBP 11, McNugget 3, Thor 3, Sprout 3, Nomad 1.

### Unsolved / Partial (4)

| Game | Progress | Baseline | Blocker |
|------|----------|----------|---------|
| dc22 | 4/6 | 1192 | L5 needs crane bridge placement — macro-action solver |
| lf52 | 6/10 | 1211 | L7 topological — no push config connects N@(0,1) to rest |
| sk48 | 2/8 | 696 | L2+ needs precise retraction-drag sequencing for target ordering |
| wa30 | 3/9 | 1564 | L3+ trapped-player box requires wall handoff macro-planning |

## Per-Game Knowledge

### Fleet Learning (`fleet-learning/{machine}/{game}_learning.jsonl`)

JSONL format. One entry per discovery, solution, or insight. Append-only.

| Machine | Games | Notes |
|---------|-------|-------|
| cbp | sb26, sc25, tn36, tr87, vc33, tu93, su15, re86 | Most complete — verified solutions, deep mechanics |
| nomad | cd82, r11l | Deep world models, interactive perceptual sessions |
| sprout | vc33, bp35 | Exploration data + complete solutions |
| mcnugget | — | Solutions exist but learning not always in JSONL |

**Entry types**: `level_solution`, `game_complete`, `game_insight`, `game_progress`, `level_attempt`, `mechanics_deep_dive`.

### Solutions JSON (`SAGE/arc-agi-3/experiments/{game}_solutions.json`)

Structured per-level data: exact action sequences, budgets, key mechanics.

| Game | Levels | Status | Has Sequences |
|------|--------|--------|---------------|
| tu93 | 9/9 | ✅ Verified | ✅ Direction sequences for all 9 |
| re86 | 8/8 | ✅ Verified | ✅ Tuple sequences for all 8 |
| sc25 | 6/6 | ✅ Verified | ✅ Click coords + direction sequences |
| tr87 | 6/6 | ✅ Verified | ✅ Direction sequences |
| sb26 | 8/8 | ✅ Strategy | ❌ Interactive (no persisted coords) |
| tn36 | 7/7 | ✅ Strategy | ❌ Interactive |
| vc33 | 7/7 | ✅ Strategy | ❌ Interactive |
| cd82 | 6/6 | ✅ Strategy | ❌ Nomad interactive |
| s5i5 | 8/8 | ✅ Strategy | ❌ McNugget BFS |
| lp85 | 8/8 | ✅ Strategy | ❌ McNugget BFS |
| r11l | 5/6 | 🔧 In progress | Partial |
| su15 | 9/9 | ✅ Verified | ✅ Click coords in session context |

### Visual Memory (`visual-memory/{game}/`)

Per-step PNG captures from game replays. 8x upscale from 64×64. run.json manifest per run.

| Game | Frames | Status |
|------|--------|--------|
| re86 | 606 | ✅ Complete (all 8 levels) |
| tu93 | 2798 | ⚠️ Partial (many runs, L1-L3 + exploration) |
| su15 | 225 | ⚠️ Partial |
| ar25 | 1560 | ✅ Complete |
| cn04 | 912 | ✅ Complete |
| sp80 | 766 | ✅ Complete |
| sc25 | 171 | ✅ Complete |
| s5i5 | 259 | ⚠️ Partial (missing later levels) |
| ls20 | 317 | ✅ Complete |
| tr87 | 137 | ✅ Complete |
| ft09 | 75 | ✅ Complete |
| r11l | 116 | ⚠️ Partial (5/6 levels) |
| cd82 | 34 | ⚠️ Incomplete |
| bp35 | 6 | ⚠️ Incomplete |
| lp85 | 0 | ❌ Missing |
| sb26 | — | ❌ Missing |
| tn36 | — | ❌ Missing |
| vc33 | — | ❌ Missing |
| m0r0 | — | ❌ Missing |

**To regenerate**: Use `SAGE/arc-agi-3/experiments/capture_visuals.py` for games with known action sequences. Games solved interactively need BFS re-solvers.

### Game Mechanics (`game-mechanics/{game}.md`)

Source analysis docs for all 25 games. Written by McNugget. Documents objects, interactions, win conditions, level progression. **Scaffold only** — not available in competition sandbox.

### Solver Drafts (`game-solvers/{game}_solver.py`)

McNugget's algorithmic solver attempts for all 25 games. Most verify L1-L3 at minimum. Useful for understanding game logic.

### Key Mechanics Discovered

| Mechanic | Games | Description |
|----------|-------|-------------|
| Paint zone spreading | re86 | Zone touch triggers flood-fill animation painting ENTIRE piece |
| Wall deformation | re86 | Pieces reshape on wall collision (width/height ±3) |
| Border-shifting | re86 | Cross arm positions shift ±3 on wall collision |
| Arrow activation zones | tu93 | 6px in arrow's facing direction = death trigger |
| Delayed entity queue | tu93 | 2-turn lag, blocked moves freeze all state |
| Vacuum physics | su15 | Click triggers vacuum (radius 8, 4px/frame) pulling enemies |
| Enemy merge types | su15 | Same-type=upgrade, different-type=flash (destroys both) |
| Paradigm shifts | sb26 | L6+ changes from pick-and-place to SWAP mechanic |
| Structural alignment | vc33 | Position alone ≠ win; structural verification required |

## Cross-Game Knowledge

### Consolidated (`consolidated/`)

Daily cron on CBP merges all fleet learning. Deduplicates by content hash.

- `level_solutions.jsonl` — best solution per game/level across fleet
- `game_insights.jsonl` — deduplicated mechanic discoveries
- `structural_patterns.jsonl` — cross-game patterns
- `last_consolidated.json` — metadata + timestamp

### Membot Cartridge (`fleet-learning/{machine}/kb.cart.npz`)

Andy's paired-lattice format. Embedding + text for semantic search. Currently on cbp, nomad, sprout.

**STATUS: STALE** — needs regeneration after latest solves (18/25 now vs 8/25 when last built).

### Cross-Game Patterns (`cross-game-patterns.md`)

Visual cues that predict mechanics across games. Key patterns:
- Border color = identity (sb26, vc33)
- Dashed circles = placement targets
- Step counter presence = action budget
- Color 4 (gray) = wildcard in win checks

### Insights (`insights/`)

- `2026-04-08-fractal-gameplay-insights.md` — maps gameplay to SAGE loop, raising, trust
- `2026-04-09-two-paths-to-game-knowledge.md` — analytical vs perceptual approaches
- `2026-04-09-analytical-vs-perceptual-knowledge.md` — broader framing

## Game Coordination (`game_coordination.json`)

Fleet-wide game status tracker. Pull before claiming, push after.

**Current: 18/25 solved (84%).** See fleet status table above.

## Persistence Checklist (After Every Game Session)

- [ ] Fleet learning JSONL → `fleet-learning/{machine}/{game}_learning.jsonl`
- [ ] Solutions JSON → `SAGE/experiments/{game}_solutions.json`
- [ ] Visual memory PNGs → `visual-memory/{game}/`
- [ ] Game coordination updated → `game_coordination.json`
- [ ] Knowledge map updated → `KNOWLEDGE_MAP.md`
- [ ] Consolidation flagged/run
- [ ] Cartridge rebuild flagged (if major new learning)
- [ ] Commit + push both repos

## For Competition (Phase 2+)

The solver framework loads knowledge on init via `claude_solver.py:load_fleet_knowledge()`:
1. Game mechanics doc (first 80 lines)
2. Solutions JSON (if exists)
3. Fleet learning JSONL (last 10 entries per machine)
4. World model docs
5. Knowledge cartridge summary

gemma4 will use the same pipeline. The membot cartridge is the primary query interface for the competition model.
