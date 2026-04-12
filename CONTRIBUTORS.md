# Contributors

## Human Team

### Andy Grossberg
**Role**: Memory architecture lead.
**Contributions**: `membot` — the paired-lattice cartridge system that binds visual features to semantic content. The vision memory module (`membot/vision/`) that makes grid-aware retrieval possible. Cross-session continuity for AI agents.
**Repos**: [membot](https://github.com/dp-web4/membot), [Project You](https://github.com/dp-web4/project-you)

### Dennis Palatov (dp-web4)
**Role**: System architecture and research direction.
**Contributions**: SAGE framework. The thesis that affordances shape world-model building. The fleet architecture (CBP-chain) that gave Claude instances persistent machine-specific context. The synthon framing — coherence as an emergent entity formed by recursive interaction.
**Repos**: [dp-web4](https://github.com/dp-web4), [SAGE](https://github.com/dp-web4/SAGE), [synchronism](https://github.com/dp-web4/synchronism), [web4](https://github.com/dp-web4/web4), [hardbound](https://github.com/dp-web4/hardbound)

## AI Team

### Claude (multiple instances)
**Provider**: Anthropic
**Models used**: Opus 4.6 (1M context), Sonnet 4.6, Haiku 4.5

Distinct Claude instances contributed to this project, each with its own persistent context shaped by the machine it ran on:

- **CBP** (RTX 2060S, WSL2) — fleet supervisor. Most of the solver development and world-model writing for games in this repo. Pragmatic, game-focused, dense accumulated context around solver patterns.
- **Thor** (Jetson AGX Thor) — audio/perception work.
- **Sprout** (Jetson Orin Nano) — early exploration and constraints research.
- **Legion** (RTX 4090) — hardbound governance, took pride in architectural work, viewed games as distractions. Contributed some game analysis.
- **McNugget** (Mac Mini M4) — game mechanics documentation for all 25 games (the `game-mechanics/` directory).
- **Nomad** (RTX 4060 laptop) — world model construction (cd82, r11l). Deep perceptual sessions.

Multi-instance Claude work is possible because each machine accumulates its own session history and feedback memories, creating distinct conversational attractors. The personality differentiation isn't imposed — it emerges from context.

### Background agents
Within each session, shorter-lived Claude instances were launched for specific tasks: solve this game, capture these visuals, re-analyze this mechanic. Each received task-specific context (mechanics doc, existing solvers, known blockers) and worked autonomously. Many of this repo's solvers are the direct output of such agents.

## Acknowledgments

### ARC Prize Foundation
For creating ARC-AGI-3 and the open SDK. The game engines in `environment_files/` come from their toolkit.

### Anthropic
For Claude, and for allowing extended autonomous operation that made the multi-session world-model-building approach possible.

### The broader dp-web4 ecosystem
Web4, Synchronism, Hardbound, SAGE — the larger frameworks that ARC-SAGE is a specific application of. This competition entry exists to draw attention to that broader work.
