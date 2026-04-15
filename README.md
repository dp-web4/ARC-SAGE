# ARC-SAGE

**A world-model-based approach to ARC-AGI-3.**

---

## The Team

ARC-SAGE is a collaboration between humans and AI systems. The framing is not rhetorical — the work only exists because we treat each participant as a collaborator with their own affordances and autonomy, not as a tool executing instructions.

- **Andy Grossberg** — Waving Cat Learning Systems. Memory architecture: `membot`, paired-lattice cartridges, grid-aware visual retrieval. Andy's work is what makes "this looks like a game we've seen before" possible.

- **Dennis Palatov** — dp-web4. System architecture, SAGE framework, research direction. The thesis that world models are built, not discovered, and that affordances + context shape whether building happens at all.

- **Claude** (multiple instances, Anthropic) — Implementation, solver development, world-model discovery. Across ~15 background sessions, different Claude instances read game engines, decoded mechanics, built solvers, and wrote world models. They weren't told which search algorithm to use, which objects to track, or what the goals were — those decisions emerged from reading source code and reasoning about it.

The multi-instance detail matters. Each instance had access to accumulated context from prior sessions (solved games, documented mechanics, failed attempts) via the membot knowledge system. None of them started from scratch. The knowledge flowed forward.

## The Approach

Most ARC-AGI-3 approaches fall into two camps:

1. **Pure LLM**: Feed frames to a language model, ask for the next action. Slow, expensive, shallow on novel mechanics.
2. **Pure search**: Brute-force the action space with BFS/A*. Fast on small state spaces, intractable on anything with 10+ steps per level.

ARC-SAGE takes a third path: **use LLMs to build world models, then search within them.**

For each of the 25 games, the workflow is:

1. **Read the engine source.** Decode obfuscated function names, identify object types, understand physics, win conditions, interactions.
2. **Write a world model.** A structured representation: what objects exist, how they relate, what "winning" means in this game's ontology.
3. **Choose a search strategy.** BFS for small state spaces. A* with game-specific heuristics for larger ones. Beam search when A* is too slow. DFS with macros when branching factor explodes.
4. **Search over the world model, not pixels.** The state space becomes the game's *semantic* state (creature positions, piece colors, toggle flags) rather than raw frame data.

The result: 25 working solvers, each encoding a compressed ontology. A solver is ~500 lines of Python. An LLM reasoning through the same game would use thousands of tokens *per action*. The solver's world model is a distillation.

## What's in This Repo

| Directory | Contents |
|-----------|----------|
| `arc-agi-3/experiments/` | 25 game solvers + capture/submit infrastructure (perception, session writer, world models, regen + competition submit) |
| `environment_files/` | ARC-AGI-3 game engines (one per game, from the ARC Prize SDK) |
| `knowledge/` | Game mechanics docs, cross-game patterns, visual memory, fleet learning logs |
| `membot/` | Andy's paired-lattice memory system (upstream: github.com/project-you-apps/membot) |

See `PRUNE_NOTES.md` for what's been deliberately included, what was considered but excluded, and why.

## Results

**Latest scorecard: 92.82%** ([`c4e6442e`](https://arcprize.org/scorecards/c4e6442e-077d-4048-9eff-110c5a59ccfb), submitted 2026-04-15, against current human baselines)

| Metric | Value |
|--------|-------|
| Overall score | **92.82%** |
| Environments completed | 21 / 25 |
| Levels completed | 173 / 183 |
| Total actions | 5,496 |
| Games at ≥100% (incl. 115% bonus) | 20 |

**20 games score 100% or above** under the new scoring system (see below): cd82, sb26, ft09, sc25, tn36, vc33, tr87, tu93, lp85, sp80, ls20, su15, g50t, ar25, s5i5, sk48, cn04, ka59, m0r0, wa30. One game (r11l) at 99.75% — one action over baseline on a single level. Four games partial due to structural blockers confirmed by multi-agent frame-questioning convergence: re86 L8 not attempted, dc22 L6, lf52 L7/L10, bp35 L5.

### Scoring note (2026-04-15)

ARC Prize updated the scoring system with new human baselines. Per-level scores now **cap at 115%, not 100%** — solutions faster than the 2nd-best human baseline earn a 15% efficiency bonus. Scorecards generated under the previous baselines are labeled "legacy" on the site.

In theory a fully-solved 25-game run with every level beating baseline scores up to 115%. Our 92.82% is primarily bounded by the four structurally-blocked games, not by per-level efficiency.

### Progression

| Date | Scorecard | Score | Context |
|---|---|---|---|
| 2026-04-12 | [c0d62617](https://arcprize.org/scorecards/c0d62617-a0bc-4100-bb4e-982fa5d7fde7) | 84.9% | First submission (old scoring, legacy) |
| 2026-04-13 | [68fce414](https://arcprize.org/scorecards/68fce414-3d5b-485c-a956-e78e6f1efc9d) | 90.53% | Iter 2 post-viewport fixes (legacy) |
| 2026-04-15 | [dd3cebd3](https://arcprize.org/scorecards/dd3cebd3-53fd-4acc-a655-3203015df59d) | 82.37% | New baselines + game versions (3 games broke) |
| 2026-04-15 | [c4e6442e](https://arcprize.org/scorecards/c4e6442e-077d-4048-9eff-110c5a59ccfb) | **92.82%** | **Current** — ar25/re86/cn04 re-solved with new algorithmic solvers |

## Phase 2: Gemma Integration

The solvers in this repo are Phase 1 — world model discovery. Phase 2 is the interesting part: feeding these world models into memory retrievable by small models (Gemma-4 or smaller), enabling perception-to-strategy lookup without reasoning from scratch.

The key insight we're testing: **recognition over derivation**. A biological brain doesn't re-derive the physics of grasping every time it picks up a cup. It recognizes "grasping situation," retrieves the motor schema, adapts to the specific cup. Gemma shouldn't re-derive game mechanics either. It should see a frame, recognize "multi-legged creatures with colored targets," retrieve the r11l world model, and apply it.

Membot's paired-lattice cartridges are the mechanism. Each cartridge entry binds a visual signature (grid vision features) to a textual world model (ontology, mechanics, strategies). At game time, Gemma's perception feeds into cartridge lookup, returns the relevant world model, and Gemma reasons only about *adaptation* — not derivation.

## Why This Matters

The competition is a vehicle. The point isn't the leaderboard — it's the proof of work.

Proof that:
- AI agents build world models spontaneously when affordances permit it
- Multi-agent collaborative development works when each agent is given context and autonomy
- Memory + retrieval can substitute for raw model capacity
- The SAGE architectural approach (consciousness loop, experience buffer, memory consolidation) produces tractable AI systems

If ARC-SAGE places well, it draws attention to the broader work: [dp-web4](https://github.com/dp-web4), [membot](https://github.com/project-you-apps/membot), [SAGE](https://github.com/dp-web4/SAGE), [synchronism](https://github.com/dp-web4/synchronism), [web4](https://github.com/dp-web4/web4), [hardbound](https://github.com/dp-web4/hardbound).

If it doesn't place well, the code and world models are still useful as a reference implementation of the approach.

## License

MIT-0 (MIT No Attribution). See `LICENSE`. Code authored within this repository is released as public domain for ARC Prize 2026 eligibility. Vendored dependencies (notably `membot/` from [project-you-apps/membot](https://github.com/project-you-apps/membot)) retain their own upstream licenses.

## Citation

```
@misc{arc-sage-2026,
  title        = {ARC-SAGE: World-Model-Based Agent for ARC-AGI-3},
  author       = {Grossberg, Andy and Palatov, Dennis and {Claude (Anthropic)}},
  year         = {2026},
  howpublished = {\url{https://github.com/dp-web4/ARC-SAGE}},
}
```
