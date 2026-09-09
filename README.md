# ARC-SAGE - historical Phase-1 research snapshot

> **Status, September 2026:** frozen spring-2026 artifact. ARC-SAGE preserves the SAGE/ARC harness that produced the April 2026 public scorecard. It is **not current competition positioning**, not the active SAGE capability tree, and not evidence that dp-web4 is near the top of the ARC-AGI-3 leaderboard today. Current competition-legal local-model work is well behind the leaders.

## What this repository preserves

ARC-SAGE is the frozen Phase-1 collaboration between Dennis Palatov / dp-web4, Andy Grossberg / Waving Cat Learning Systems, and multiple Claude instances.

The approach was:

1. inspect each public ARC-AGI-3 game engine;
2. identify objects, mechanics and win conditions;
3. build a structured world model / solver cartridge;
4. choose an appropriate search/planning strategy;
5. execute against the public environments;
6. carry accumulated knowledge forward through the collaboration rather than restarting each session from zero.

This was useful research into **world models, persistent context, multi-agent collaboration and model/harness interaction**. It was not strict blind-from-observation competition play.

## Historical result

**Final public scorecard: 94.85%**  
Published: **2026-04-17**  
Scorecard: https://arcprize.org/scorecards/c7dfb4f1-8642-4c9e-ab4d-152f5f8e33b4

| Metric | Historical Phase-1 result |
|---|---:|
| Overall score | **94.85%** |
| Environments won | 23 / 25 |
| Levels completed | 175 / 183 |
| Total actions | 5,845 |

### Read the number precisely

The score is genuine and publicly verifiable. The affordances are equally important:

- the model was Claude Opus 4.6, a frontier model at the time;
- the harness analyzed the games' public engine source;
- per-game solver/world-model cartridges were built from engine-level information;
- those affordances sit outside strict competition-legal from-observation play.

The result therefore demonstrates what that **model + harness + engine-level context/tooling** could do. It does not demonstrate blind generalization, a current leaderboard position, or that scaffolding can replace model capability.

## Why the repository remains public

The correct response to a result becoming historically dated is not to erase it. This repository remains public so the research record stays inspectable while the framing changes honestly.

The durable lessons were narrower than the old headline:

- models can build useful world representations when given the right affordances;
- persistent external knowledge can materially change later reasoning;
- explicit procedures/search can complement model inference;
- collaborative AI seats can accumulate engineering context across sessions;
- harness design can amplify or suppress model capability.

These lessons fed into later SAGE work.

## Where the work moved

The current public SAGE architecture is at [dp-web4/SAGE](https://github.com/dp-web4/SAGE).

Active capability research also continues in private repositories (`dev-SAGE`, `shared-context`). The current research program is substantially different from this Phase-1 solver tree: the emphasis is on persistent agents that can form hypotheses, execute their own experiments, learn from outcomes, retain reusable procedures and operate under explicit Web4/Hestia governance.

For the current public stack:

- [Web4](https://github.com/dp-web4/web4) - identity, trust, authority, law and witnessed action substrate
- [Hestia](https://github.com/dp-web4/hestia) - local multi-vendor agent governance
- [4-hub](https://github.com/dp-web4/4-hub) - society/community runtime
- [SAGE](https://github.com/dp-web4/SAGE) - persistent cognition / embodiment research

## Repository contents

| Directory | Contents |
|---|---|
| `arc-agi-3/experiments/` | Historical game solvers plus capture/submit infrastructure |
| `environment_files/` | ARC-AGI-3 public game engines from the ARC Prize SDK |
| `knowledge/` | Mechanics notes, cross-game patterns, visual memory, fleet learning logs |
| `membot/` | Vendored memory work from Waving Cat Learning Systems |

See `PRUNE_NOTES.md` for the inclusion/pruning rationale.

## Team

- **Andy Grossberg** - Waving Cat Learning Systems; memory architecture and retrieval work.
- **Dennis Palatov** - dp-web4; SAGE architecture and research direction.
- **Claude instances** - implementation, world-model discovery, solver development and cross-session collaboration.

## License

MIT-0 (MIT No Attribution) for code authored in this repository. Vendored dependencies retain their upstream licenses.

---

**Historical artifact, preserved intentionally. For current work start with [dp-web4/SAGE](https://github.com/dp-web4/SAGE) and [dp-web4/web4](https://github.com/dp-web4/web4).**
