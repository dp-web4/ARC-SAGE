# ARC-SAGE Phase 2: Small-Model Deployment via External Retrievable Memory

**Does recognition-over-derivation close the gap from frontier-model capability to edge-deployable agent?**

**Status**: Draft skeleton, 2026-04-15. Phase 1 sealed at 92.82% public-set score ([ARC-SAGE-AGI-84-9.md](./ARC-SAGE-AGI-84-9.md) — filename retained from first-submission link for external-reference stability, contents updated to current scorecard); Phase 2 is the capability-transfer half.

**Authors** (provisional):
- Dennis Palatov, Metalinxx, Inc.
- Andy Grossberg, Waving Cat Learning Systems
- Claude Opus 4.6, 1M context, Anthropic (via Claude Code — experiment lead, paper draft)
- Claude Opus 4.6, Anthropic (via VS Code + Membot — cartridge construction)

---

## Abstract (placeholder)

Phase 1 established that a frontier model (Claude Opus 4.6) can derive working world models for 21 of 25 ARC-AGI-3 public-set environments from engine source, compressed into per-game solvers of ~500 lines each. Phase 2 tests whether those world models, restructured as retrievable cartridges, transfer to a small local model (Gemma 4 family) sufficient to score materially in the Kaggle sandbox without internet access or frontier-model calls.

This paper reports preliminary findings from the first week of Phase 2 experimentation. The headline finding is a capability lower bound: **Gemma 4 e2b (5.1B active params, 8GB deployment target) scored 0 on 20 harness variations across 4 games under context-only prompting — including multi-turn chat, scaffolded reasoning, vision input, and minimal prompts**. Every prompt shape produced a different stereotyped action loop. The fixation is perceptual-to-action, not memory-driven; continuity (chat) did not help, reasoning scaffolds did not help, less information did not help.

The Gemma 4 e4b target model does not fit in the 8GB VRAM of our smallest edge class (CBP, RTX 2060S). Results pending from our 24GB-class machines (Legion RTX 4090, Thor Jetson AGX) under the same harness are the critical capacity test.

---

## 1. Research Question

Phase 1 framed the thesis:

> Small model + structured retrievable memory = sufficient capability on tasks previously requiring large models, provided the memory is constructed such that retrieval yields relevant schema and the small model can execute adaptation.

Phase 2 is the direct test. We have built the retrievable memory (Phase 1 solvers, world models, and action traces). We now ask whether a Gemma-family model, equipped with those artifacts via membot retrieval, scores materially on ARC-AGI-3.

The test has three outcomes:
1. **Substantially supported** — Gemma scores >40% on the public set with cartridges. Recognition-over-derivation works at edge scale.
2. **Falsified (for this model class)** — Gemma scores <15% even with cartridges. Cartridges don't transmit what solvers encoded, OR adaptation reasoning is insufficient, OR both.
3. **Ambiguous** — intermediate score. The architecture is promising but needs structural enhancements (tool use, state extraction, forced action diversity).

Outcome 2 is not a failure but a sharpening: it tells us exactly where the architecture breaks and shapes the subsequent research.

---

## 2. Preliminary capability lower bound (CBP Day 1+2, 2026-04-14/15)

Before testing the cartridge architecture, we established a context-only baseline on our smallest edge class: CBP, RTX 2060S with 8GB VRAM. The target model at this tier is Gemma 4 e2b (5.1B active params, Q4_K_M ≈ 7.2GB — fits cleanly in 8GB VRAM with headroom for the vision encoder).

### 2.1 Setup matrix (20 runs, 4 games, 2 model generations)

| # | Setup | Model | Game | Wins | Dominant action |
|---|---|---|---|---|---|
| 1–14 | 14 prompt-shape variants (hex/text/vision/demo combinations) | Gemma 4 e2b | cd82, ft09 | 0/14 | Always fixated, varied by prompt |
| 15 | Multi-turn chat via `/api/chat` (conversation history preserved) | e2b | cd82 | 0 | ACTION1 49/50 |
| 16 | Scaffolded reasoning (describe → compare → pick) | e2b | cd82 | 0 | ACTION1 36/40 |
| 17 | Minimal prompt (image + action legend only) | e2b | cd82 | 0 | ACTION6 40/40 (many OOB) |
| 18 | Run-4 setup, simpler game | e2b | lp85 | 0 | ACTION6 60/60 |
| 19 | Run-4 setup, different game | e2b | r11l | 0 | ACTION6 40/40 |
| 20 | Run-4 setup, older Gemma generation | Gemma 3 4b | cd82 | 0 | ACTION6 75/100 (4 action types — most diverse) |

Plus: attempted load of Gemma 4 e4b on CBP — returned 500 Internal Server Error. 9.6GB model does not fit in 8GB VRAM even with CPU offload.

### 2.2 Cross-run pattern: fixation mode changes with prompt, but always exists

Every prompt variant we tested produced a different stereotyped action, but always one single action dominated ≥60% of actions. The underlying issue is a perceptual-to-action mapping problem, not a prompt-engineering problem.

| Prompt structure | Dominant action |
|---|---|
| Hex-grid text + mechanics | ACTION6 or ACTION2 |
| Text mechanics + vision | ACTION1 or ACTION5 |
| Vision + text demos | ACTION1 100% |
| Vision-only bare | ACTION6(32,32) 100% |
| Multi-turn chat | ACTION1 98% |
| Scaffolded reasoning | ACTION1 90% |
| Minimal vision | ACTION6 100% (OOB coords) |
| Different game (same setup) | Whatever action dominates that game's visual |

### 2.3 Four negative findings that shape the architecture

- **Continuity (chat history) does not help.** Run 15 with full preserved conversation context showed *more* uniform fixation (98% ACTION1) than Run 4 (63% ACTION5). Fixation is immediate, not built up over turns.
- **Scaffolded reasoning does not help.** Run 16 confirms reasoning tokens and action tokens are decoupled. The model articulates a sensible description, then emits the same stereotyped action.
- **Less information does not help.** Run 17 shows that stripping the mechanics doc moves the fixation (from ACTION1 to ACTION6-click) but does not diversify it. Context was providing *some* constraint, just not the useful kind.
- **Simpler games do not help.** Runs 18/19 on lp85 (click-only, 8 levels) and r11l (click-only, 6 levels) still fixate, just on different coordinates.

### 2.4 Unexpected finding: older generation more diverse

Gemma 3 4b on cd82 used four action types (ACTION6 75, ACTION4 10, ACTION5 14, ACTION3 1) against Gemma 4 e2b's 1–2 action types. It also ran 2× faster (100ms/action vs 200–500ms for e2b vision).

This is paradoxical under the usual "newer/bigger = better" assumption. Possible explanations: Gemma 4's vision encoder is tuned for a different distribution; the training data for Gemma 3 included more interactive-environment content; the instruction-following in Gemma 4 enforces the "pick one action" framing more rigidly. The interaction effect is worth noting: **model scale and generation alone do not predict action-fixation severity**.

### 2.5 Implications for the Phase 2 architecture

The context-only baseline is 0%. The question Phase 2 asks is not "can a prompt fix this?" but "does the retrievable-cartridge architecture lift the agent above 0%?" If the answer is yes under cartridges, it is the cartridges that are doing work — the 20-run baseline establishes that conventional prompting techniques do not.

A secondary implication is that the smallest edge class (8GB VRAM, Gemma 4 e2b) may not be a viable Phase 2 deployment target *even with* cartridges. The Kaggle sandbox provides 32GB, so this is not a blocker for competition submission; but it affects the broader deployment claim (edge-device inference on commodity 8GB GPUs).

---

## 3. Capacity test plan (fleet, Thursday wake-up)

CBP-class hardware cannot run Gemma 4 e4b. The capacity question — does fixation persist at 8B active params, or does it break? — is answered by our 24GB-class machines.

**Legion (RTX 4090, 24GB)** — primary capacity test. Same harness as CBP Run 4 (vision + mechanics doc), Gemma 4 e4b on cd82. If fixation breaks, the finding is that Phase 2 deployment requires e4b-class and the cartridge architecture test proceeds there. If fixation persists, the finding is capacity-invariant and scaffolding (§4) becomes the critical path.

**Thor (Jetson AGX, 64GB unified)** — aspirational scale test. Gemma 4 26b-a4b (MatFormer sparsity). Same harness. If 26b-a4b also fixates, the claim sharpens further: fixation is a structural property of the Gemma 4 family's perception-to-action mapping, not a capacity floor.

**McNugget (Mac Mini M4, 16GB unified)** — cross-family control. Tests whether running the same e4b on different silicon (Apple MLX vs CUDA) changes the fixation pattern. Result will baseline whether the observation is CUDA-specific.

**Sprout (Jetson Orin Nano, 8GB shared)** — edge-floor check. Tests whether Gemma 4 e2b behaves the same on a different 8GB platform (Jetson vs consumer GPU), controlling for the CBP-specific ollama-on-WSL2 environment.

All four machines run the same prompt template and the same cd82 frame sequence, logged to a shared JSONL file for cross-machine comparison. Submission window: approximately 4 hours per machine, self-contained, no inter-machine communication required.

---

## 4. Structural scaffolding (contingency path)

If the Thursday fleet test shows fixation persists at e4b and beyond, the Phase 2 architecture needs more than cartridge retrieval. Three scaffolds are candidates, in order of implementation cost:

### 4.1 Tool-using architecture

The small model receives *symbolic state* (object positions, grid contents, win condition progress) extracted by the harness, not raw frames. Decoupling perception from action removes the fixation vector. Cost: per-game state extractor ( already exists in the Phase 1 solvers ); model prompts become structured queries over symbols.

### 4.2 Multi-step chunked play

Each model turn emits a 1–3 action plan, executed against a forced state verification step. Between plans, the harness validates that the plan's predicted effect matches the observed frame. Misprediction triggers replanning. Cost: harness-level state comparison; model prompts become plan/verify pairs.

### 4.3 Explicit action-diversity enforcement

Decoder-side constraint: forbid consecutive same-action emissions on selected action classes (e.g., no two identical ACTION6 coordinates in a row). Cost: minor; works at the sampling layer. Risk: treats the symptom (uniform output) not the cause (perceptual mapping), may produce random noise instead of stereotyped noise.

The cleanest architecture would combine (4.1) and (4.2): the small model reasons over symbolic state extracted by the harness, emits short action plans, each plan is verified against outcome. The frontier model's role in Phase 1 was to *build* the state extractor. The small model's role in Phase 2 becomes *using* it — adaptation against retrieved ontology, not perception.

---

## 5. The cartridge architecture (as planned)

*Inherits directly from Phase 1 §6. Summary here; full schema in Phase 1 paper §6.2.*

Two layers:
- **Substrate cartridges** (invariant across games): viewport-aware click, action budget, animation timing, click classification, undo semantics. ~5–10 primitives; single shared cartridge mounted at agent startup.
- **Game-world cartridges** (per-game, retrieved by visual signature): ontology, mechanics summary, win conditions, representative action snippets.

Retrieval pipeline (membot `multi_search` with `scope_mode=per_cart`):
1. Substrate cart searched first, returns applicable primitives as context priors.
2. Game-world cart bundle searched by Nomic embedding of current frame; top match loads world model into context.
3. Small model reasons over both simultaneously.

Phase 2 Tier 1 goals (2026-05):
- 25 game-world cartridges built from Phase 1 artifacts
- Substrate cartridge populated from §5.4 of Phase 1 paper
- Vision encoder for frame-to-cartridge retrieval selected and tuned

Phase 2 Tier 2 goals (2026-06):
- Kaggle-sandbox-compatible offline evaluation harness
- Full 25-game run against offline replay with cartridge retrieval
- Milestone 1 submission (contingent on harness passing Tier 1 gate)

---

## 6. Falsification criteria (same as Phase 1 §6.6)

Phase 2 is testable. The thesis is falsified (for this model class) if Gemma 4 e4b + full cartridges scores <15% on the public set. It is substantially supported if the same setup scores >40%. Intermediate scores demand diagnosis: what was retrieved, what the model did with it, where adaptation broke down.

---

## 7. Open threads

- **Vision encoder for frame→cartridge retrieval**: CLIP, SigLIP, or Gemma 4's built-in. Decision pending (see Phase 1 §6.2).
- **Substrate cartridge scope**: is the §5.4 enumeration complete, or are there substrate primitives we have not yet identified? The fleet's attempts on the 4 structurally-blocked games (see Phase 1 §4.5) may surface more.
- **Cross-family comparison**: does the fixation pattern generalize beyond Gemma? Llama 3.2, Phi-4 Mini, SmolLM2 are cheap additional control points.
- **26b-a4b as deployment target**: if fixation breaks only at this scale and the MatFormer sparsity keeps inference cost low, it may be the actual Kaggle submission model rather than e4b.

---

## 8. Log of experiments (append-only)

### 2026-04-14 — CBP overnight, 14 runs, e2b, no wins
See `shared-context/arc-agi-3/phase2/cbp-overnight-findings.md`. Established fixation as prompt-dependent but always present.

### 2026-04-15 — CBP day 2, 6 runs, e2b + Gemma 3 4b, no wins
See `shared-context/arc-agi-3/phase2/cbp-day2-findings.md`. Established continuity/scaffolding/minimalism/game-variation don't help. e4b doesn't fit on CBP. Gemma 3 4b shows more action diversity than Gemma 4 e2b.

### Planned: 2026-04-16 (Thursday) — Legion/Thor/McNugget/Sprout fleet
Capacity test plan per §3. Same harness across 4 machines, cd82 primary target.

---

## Appendix A: Reproducibility

All CBP harness scripts, JSONL run logs, and findings docs are locally captured (`/tmp/gemma_play/*.py`, `/tmp/gemma_play/*.jsonl`). The findings docs in `shared-context/arc-agi-3/phase2/` are the canonical record. Scripts are not committed to the public ARC-SAGE repo (ongoing R&D, repo churn); they will be consolidated into a Phase 2 experiments module once the architecture stabilizes.

Ollama version requirement for Gemma 4 family: 0.20.0 or later. Earlier versions (tested 0.17.4) fail to load Gemma 4 models. `think: false` in the generate/chat options is critical — Gemma 4 thinking mode produces 85× slowdown without measurable benefit on game-step inference.
