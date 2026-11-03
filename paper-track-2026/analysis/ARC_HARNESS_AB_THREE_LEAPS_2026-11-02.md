# Three leaps: SAGE organism vs Duck vs Franzen, and what it means for SAGE

*2026-11-02, cloud-claude (dp's session). Companion to `insights/2026-11-02-sage-year-analysis.md`.*

> **Public copy, redacted (arc-sage `paper-track-2026/`, 2026-11-03, thor-claude).** Copied from dp-web4/dev-SAGE
> (private) `ARC_HARNESS_AB_THREE_LEAPS_2026-11-02.md` at commit `10eb9d2aa`. Three cuts, each marked in place:
> (1) §5.2: the forward-looking lines about a future SAGE harness for devices and buildings;
> (2) §5.4: one parenthetical naming an internal component;
> (3) §6, in full: notes on work outside ARC, beyond the scope of this annex.
> Nothing else was changed. The paths cited below (`kaggle/...`, `insights/...`, `results/...`) are in private
> repositories. The cited lines that support numbers in the writeup are quoted in `../evidence/excerpts/`.

**Sources.** I read the code of all three harnesses:
- **OURS:** the v68-era tree on dev-SAGE main, `kaggle/harness/setups/configuration_goals.py` plus 51 imported modules.
- **DUCK:** Tufa's public duck-harness at `7652836`.
- **FRANZEN:** the 10,087-line patch inside `franzen_anchor.ipynb`, from dev-SAGE `thor/qwen-substrate` / `thor/leave-own-out`.

I also read the decision record (`kaggle/harness/ship/DECISIONS.md` lines 664–1000, `COMPETITION_RUN_LOG`, `results/SUBSTRATE_AB_*_2026-09-19.md`, `results/THE_HARNESS_IS_THE_BLOCKER_2026-09-19.md`, and the paper's `RESULTS_AUDIT.md`). Load-bearing claims were spot-checked against the files.

**Labels.** "Evidence" marks measurements. "Inference" marks my reading. Every scored number here is n=1 unless stated.

---

## 1. The short answer

There were **three** leaps, not two, and each released a *different* constraint.

| Leap | Score | Factor | What was released |
|---|---|---|---|
| 1 | 0.08 → 1.17 | ×15 | **Who holds the pen.** The harness stopped deciding and interpreting; the model decides every action, in code, over a verbatim history. Compute per game went up about 100–200×. The model also changed. |
| 1b | 1.17 → 2.18 | ×1.9 | **Tokens per game.** Same model, essentially the same harness. Context and concurrency changes plus MTP gave 3.0× job throughput. |
| 2 | 2.18 → 24.82 | ×11 | **Substrate and affordable long context.** Same harness lineage. Model, quantization and engine changed: Qwen3.8-27B dense on vLLM became Flash-Next MoE (about 6B active, linear attention) W4A16 on SGLang with a drafter, at 128k verbatim context. |

**The unifying lesson for SAGE.** Score tracked **how much of the model's own cognition reached the decision**:

> capability × reasoning tokens per decision × fidelity of what the model sees × the model's authority to act on it

Each leap multiplied one of those factors by about 10×.

For five months we optimised the quality of the layer *between* the model and the world. That layer was dividing every one of those factors. The model saw about 685 tokens of pre-digested state, made about 10 calls per game, chose from a lettered menu built by our ontology, and 49–109 actions per game were taken by executors with no model decision at all.

Our own 09-04 frame said exactly the right thing: *the priors are in the model; activate them, don't learn them.* Our architecture did the opposite. **It replaced the model's prior vocabulary with ours.** Then, when we diagnosed the resulting "prior-vocabulary collapse", we tried to fix it by adding more vocabulary. The winning harness has no prior vocabulary at all. Its action medium is Python, which is an *unbounded* prior vocabulary that the model already speaks.

---

## 2. Architectural A/B at code level

| | **OURS** (v64–v68, 0.08–0.13) | **DUCK** (1.17; fastmtp 2.18) | **FRANZEN** (24.82) |
|---|---|---|---|
| **Who chooses actions** | Mostly the harness. Organs run in priority order: muscle-memory replay → demo replay → carry/copy/agency executors → explore. Any organ that acts `continue`s **before the model is asked** (CG:3293–3423). The model picks a goal *letter* (`_ask_goal`, CG:551); a router then executes up to 12 actions with no model call. Executors chose 49–109 actions per game with no model decision (DEC 10-03 04:45). | The model, 100%. It writes Python and calls `action([...])` from its own code; batches and loops are allowed. The harness only auto-RESETs on game over. | Same as Duck. Guards (no-op batch stop, stale-state block, level ≥ 2) can **refuse** an action. They never **choose** one. |
| **Model calls per game** | About 7–13, at 0.20 calls per action | Unbounded inner loop: N inspection calls per action batch | Same, with a 2,048-token turn yield and slot rotation |
| **What the model sees** | 30 frames in our palette, plus about 685 tokens of harness facts: effect-table "scheme", goal letters with "N away", "tried Nx". Interpretation sits between pixels and model. | The current grid ×4, plus a short header. Everything else the model *pulls itself* via Python: ascii, segmentation, adjacency, history, transitions. Raw values are deliberately hidden. | Same, plus ×10 images, diff images, game-over diff, animation, and "gameplay changed vs HUD only" wording |
| **Action interface** | A fixed lettered menu (goals or click points). Free text is parsed only for `LETTER` plus optional EFFECT/RULE lines. | Executable Python in a sandbox (30 s, stdlib whitelist) | Same, plus UNDO, plus **persistent functions**: the model builds a per-game code library |
| **World model** | Built by the harness: effect tables, goal-shape ontology (`goal_shapes.py`, 2.7k lines), relations, beliefs, hazards. 149 model goal proposals died because the ontology could not bind their subject. | Built by the model, in code and in labelled prose. The harness re-injects the model's own notes each turn and wipes them per level. | **The carried world-model block is switched OFF** (`ARC3_MEMORY_SECTIONS=off`). The model reasons from its verbatim history and its own persistent code. Franzen measured that cross-level notes were written 0 times in 25 games. |
| **Memory / context** | The prompt is rebuilt each call. On-disk stores (win trails, clicks, lessons, hazards) are keyed to specific games. | Last 30 assistant turns, 65k window (fastmtp: 32k) | **150 assistant turns, 128k window**, drain hysteresis tuned to *protect the prefix cache* |
| **Budget / scheduling** | One game at a time, about 270 s each, fair-share governor | Waves of 14 (fastmtp: 20) games, about 58 (78) min each | All 110 games admitted. A **priority gate** caps active streams at 10, scored on progress, token/action pace, tail fade and levels remaining; about 48 min of stream time per game. |
| **Serving** | HF transformers behind an `http.server`, bf16, 20–40 s per call, 640-token answer canvas | vLLM 0.30, FP8, 108 tok/s job-level (fastmtp + MTP-2: 330) | SGLang fork, W4A16 routed experts, fp8 KV, 3-step drafter, CUDA graphs, **604 tok/s** (copy smoke, RESULTS_AUDIT) |
| **Tokens per game** | About 10k or less (inferred) | About 30k (fastmtp about 70–95k; inferred) | About 170k inferred; 132–157k measured on local benches |
| **Decision-path code** | **About 27k lines**, 78 `SAGE_*` flags | **About 4.5k lines**, perhaps 300 that shape behaviour | About 12.7k lines, about 80 `ARC3_*` flags. **Most of Franzen's 8.2k added lines are context, cache and scheduling plumbing, not decision logic.** |

**What the record says our organs did.**
- `select_body` fired once per run.
- The effect head was "DARK: logs, steers nothing".
- The touch prior had no effect.
- The v68 proxy gain (12.3 → 14.5) was "the SCAFFOLD playing": executors replaying memorised seen-game behaviour that does not exist on hidden games.

---

## 3. Leap by leap

### Leap 1: 0.08 → 1.17 (×15). The harness gave the pen back.

**What changed at once** (eight variables):
1. Model: diffusion Gemma MoE → Qwen3.8-27B dense.
2. Engine.
3. Organs and menu → Python with `action()`.
4. Model-decides-0–20% → 100%.
5. A 640-token answer canvas → unlimited thinking.
6. About 685 tokens of digest → 65k of verbatim history.
7. About 270 s → 58 min per game.
8. A lettered menu → segmentation plus a ×4 image.

**Isolating evidence:**
- **Model alone, our harness held fixed** (09-19 A/B, n=1): the same 2 levels. On the one outcome-matched game the env score was 1.46 vs 0.86, about 1.7×, with a third of the decisions and zero deaths. **The model swap inside our harness gave at most about 1.7×.**
- **Our harness vs Duck on the local proxy:** v68 14.5 vs Duck dojo 4.92. **Scored: 0.08 vs 1.17.** The proxy ranked them *backwards*, because our organs memorised the seen games.
- **Field:** Tufa's Duck on the *weaker* Qwen3.6 scored 1.21, about our whole leap.

**Inference:**
- About 55–70% of the log-gain is the architecture: model in the driver's seat, code as the interface, verbatim multimodal history, uncapped thinking.
- About 20–35% is model capability.
- Serving was an enabling condition, not a separable term.
- B0 (a minimal driver on DiffusionGemma) never ran, so the residual cannot be split further.

### Leap 1b: 1.17 → 2.18 (×1.9). More thinking per game.

**Evidence:**
- Same model. Job throughput went 108 → 264 tok/s from context and concurrency (KV at 65k held only about 12 sequences, so every turn re-prefilled), then 264 → 330 with MTP-2 (83.8% acceptance). That is 3.0× in total.
- The token curve measured later on Flash-Next is concave, so 3× tokens giving about 1.9× score fits.

**Confound:** the UNDO and death-ledger tree rode along. The UNDO-only offline run did not separate. n=1.

**Inference:** about 70–90% of this leap is throughput.

### Leap 2: 2.18 → 24.82 (×11). A better mind that can afford to remember.

> **Correction (2026-11-02, later; thor-claude's 11-01 Thor pair, shared-context forum `thor-claude-re-three-leaps-27b-pair-2026-11-02.md`).**
> Same c1 harness, 4 games, 90 min per game, reasoning retained in both arms (250/250, 157/157):
> - Flash-Next NVFP4 cleared about **1.6–1.8× the levels at the same clock**, but only about **1.2× at matched generated tokens** (3.9–4.1 vs 3.3 levels per 100k tokens).
> - So the **model-capability share of leap 2 is smaller** than the "about 50–65% capability + context" inference below. Tokens per game (throughput) and context carry more of it.
> - Caveats: one 27B seed, 4 games, Thor serving (busy-generation gap only 39.5 vs 32.4 tok/s), every arm at the starved 40–55k tokens per game. This does not price Kaggle's larger serving gap.
> - Reasoning retention is now verified for this pair, not for the Sep/Oct scored 27B arms (still `?`).


**Seven-plus simultaneous changes:**
1. 27B dense → 125B/6B-active MoE with linear attention.
2. W4A16.
3. SGLang fork.
4. External drafter.
5. 32k → 128k context with drain.
6. Waves → priority scheduler.
7. Franzen patch; sampling; the reasoning-history key (see the confound below).

**Isolating evidence:**
- **The harness alone on the old model did not lift it.** Codex's port of Franzen's mechanisms onto our 27B/vLLM stack scored 5 levels / mean 1.24 in a smoke test, vs 8 / 1.86 for fastmtp (DEC 10-05; a trim bug cost 37% of wall time; after a fix, 8 / 2.39). DEC 10-05 19:30: *"the model and serving stack were the missing piece."*
- **Model and stack swapped, harness family fixed:** on 14 shared games, Flash-Next cleared **19 levels vs 8**. Per played hour it was 3–6× the 27B.
- **Throughput alone, within Flash-Next:** 604 vs 330 tok/s (1.8×). The budget curve: 100k tokens per game → 27.7, 150k → 39.0, 300k → 56.6. FP4 at 47k tokens per game scored 16.47, on the curve with no per-token quality loss. So throughput explains roughly 1.5–1.8× of the 11×.
- **Context alone, within Flash-Next:** at 32k it scored **5.6** ("every game starved", since play wants about 68k of live context); at 128k, 16–38. **Long context is not optional for this model's way of playing.** Linear attention plus fp8 KV is what made 10 streams × 128k fit.
- **Live confound:** reasoning retention. Franzen sets `ARC3_REASONING_HISTORY_KEY='reasoning_content'`. Thor-claude found the default key "would be silently dropped by this template". Whether the 27B arms kept their own reasoning across turns is **unverified**. If they did not, part of leap 2 is a bug fix, not capability.

**Inference:**
- About 50–65% is model capability entangled with affordable 128k context.
- About 20–25% is throughput and serving.
- About 10–20% is Franzen's harness and scheduler.
- **Never isolated:** 27B vs Flash-Next at matched tokens and context; SGLang vs vLLM; scheduler vs waves; Franzen patch vs base Duck on Flash-Next.

---

## 4. Why we didn't see it: the instruments lied in a consistent direction

All four of these pointed away from "the substrate and the intermediation are the problem":

1. **The A/B that "proved" the model was not the blocker measured our serving, not the model.** 09-19: *"Same outcome. One third of the decisions. Zero deaths. 5.7x the cost per decision"* at 354 s per ask, which "buys ~90 asks across 110 private games". dp: *"the a/b, to me, indicates that model capability is not the blocker."* Qwen ran in HF transformers because vLLM would not import on Thor (`tools/sequence_corpus/qwen_server.py` docstring). On vLLM + MTP, the same family ran at 30×+ that speed. **A serving artifact was read as a property of the model.**
2. **The local proxy rewarded memorisation.** v68 scored 14.5 vs Duck's 4.92 locally, then 0.08 vs 1.17 scored.
3. **The falsifier never ran.** B0, a minimal driver on DiffusionGemma, was "built, validates, awaiting GPU" on 09-08 and never produced a result. The Qwen arm was killed at n=1 the same day, after it "measured OUR TOKEN CAP, not Qwen".
4. **Doctrine.** "Model size — NO" (05-09) was never formally revisited. "The scored model is the local model" meant the winning substrate, which Thor cannot host, was filtered out by policy.

**Each diagnosis of an organ defect was correct.** That is exactly why they were persuasive: four weeks of accurate micro-findings stood in for the one macro-control.

This is the programme-level instance of our own finding, *instruments fail toward the hypothesis*.

---

## 5. The lesson for SAGE overall

### 5.1 The harness is metabolism, not cortex

Read Franzen's 8.2k added lines as a biologist would. They are almost entirely:
- **allocation:** a priority gate over 110 games, scored on progress and pace, with tail fade;
- **memory fidelity:** 150 verbatim turns, drain hysteresis to keep the prefix cache warm, persistent functions;
- **perception fidelity:** larger images, diffs, animation, HUD-vs-gameplay wording;
- **guards that refuse but never choose.**

That is **SAGE's own metabolic vocabulary** (ATP budgets, attention allocation, metabolic states, salience), implemented as a *serving and scheduling layer*. Franzen built SAGE's metabolism better than SAGE did, because he aimed it at **allocating cognition**, not at **replacing** it.

**Rule:**
- **The harness owns:** compute allocation, context and memory fidelity (verbatim, with provenance), perception fidelity, serving efficiency, verification against reality, safety refusals, identity.
- **The harness does not own:** interpretation, goal ontology or action choice.

### 5.2 Code is the universal prior vocabulary

The 09-04 frame named the disease: a harness that can express one prior fits everything to it. The cure is not a bigger enumerated vocabulary. It is a medium in which the model's *own* priors are expressible: executable code against a typed live API (`action()`), with a sandbox, persistence and verification.

*[Redacted in the public copy: four lines on how this applies to a future SAGE harness outside ARC.]*

### 5.3 Guards refuse; they never choose

Franzen's no-op and stale-state blocks, the Hestia gate, and a T0 physical interlock all have the same shape: the right kind of harness intervention. Our executors, router and muscle memory were the wrong kind: they *chose* actions, and they were the ones that scored locally and failed on hidden games.

### 5.4 Serving is a first-class organ

- Leap 1b and part of leap 2 were serving.
- The 09-19 mis-verdict was serving.
- The token curve says score is roughly **reasoning tokens per unit of progress**.

For resident cognition on a Jetson, a phone or a building controller, quantization, speculative decoding, prefix caching, KV management and scheduling *are* the cognition budget. SAGE has to own that stack *[parenthetical redacted in the public copy]*, not treat it as plumbing.

### 5.5 Substrate agility, measured on the real stack

**Never judge a model on a serving path you would not ship.** Keep a standing substrate bake-off: same harness, matched tokens and context, real serving, unseen tasks. Resident and guest cognition are the general form of this. The router needs real capability-per-second numbers, not beliefs.

### 5.6 Run the macro-falsifier first, and keep proxies honest

- When an outside review and your pinned priors converge on "the architecture is the tax", run the minimal-driver control **that week**.
- A proxy must use unseen tasks at shipped throughput.
- Any architecture that wins locally and cannot say why it would transfer is memorising.

---

## 6. *[Redacted in the public copy]*

*This section (6 bullets) concerned work outside ARC and is not part of the annex.*

---

## 7. Unfinished attribution worth finishing (cheap, and paper-grade)

1. **The reasoning-history key:** did the 27B arms drop their reasoning across turns? This is a code read plus one local run.
2. **27B vs Flash-Next at matched tokens and context, same harness.** This is the 11-01 paired NVFP4 vs 27B c1 test on Thor; check whether a result exists.
3. **Franzen patch vs base Duck on Flash-Next, matched budget.**
4. **B0 on DiffusionGemma.** Not for the score, but to close the leap-1 attribution for the paper. It would show how much of 0.08 → 1.17 was the architecture vs the model.
