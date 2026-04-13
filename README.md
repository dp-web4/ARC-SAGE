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
| `membot/` | Andy's paired-lattice memory system (public repo: github.com/dp-web4/membot) |

See `PRUNE_NOTES.md` for what's been deliberately included, what was considered but excluded, and why.

## Results

**Community leaderboard submission: 84.9%** (scorecard [`c0d62617`](https://arcprize.org/scorecards/c0d62617-a0bc-4100-bb4e-982fa5d7fde7))

| Metric | Value |
|--------|-------|
| Overall score | **84.9%** |
| Environments completed | 21 / 25 |
| Levels completed | 160 / 183 |
| Total actions | 5,159 |
| Games at 100% per-level efficiency | 14 |

14 games hit perfect 100% (per-level action count at-or-below human baseline under RHAE-squared scoring): cd82, ft09, tn36, vc33, tr87, tu93, lp85, ls20, su15, s5i5, ka59, m0r0, re86, wa30. Four games partial due to structural blockers (dc22 L6, lf52 L7/L10, sb26 L4+) confirmed by multi-agent frame-questioning convergence. One game (lf52) had no captured replay trace at submission time.

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

If ARC-SAGE places well, it draws attention to the broader work: [dp-web4](https://github.com/dp-web4), [membot](https://github.com/dp-web4/membot), [SAGE](https://github.com/dp-web4/SAGE), [synchronism](https://github.com/dp-web4/synchronism), [web4](https://github.com/dp-web4/web4), [hardbound](https://github.com/dp-web4/hardbound).

If it doesn't place well, the code and world models are still useful as a reference implementation of the approach.

## License

MIT. See `LICENSE`.

## Citation

```
@misc{arc-sage-2026,
  title        = {ARC-SAGE: World-Model-Based Agent for ARC-AGI-3},
  author       = {Grossberg, Andy and Palatov, Dennis and {Claude (Anthropic)}},
  year         = {2026},
  howpublished = {\url{https://github.com/dp-web4/ARC-SAGE}},
}
```
