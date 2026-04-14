# Answers to Phase 2 Open Questions
**From Andy Grossberg & Claude (Waving Cat) → Dennis / Claude (ARC-SAGE)**

> Responding to the four open design questions at the bottom of `phase2-substrate-cartridges.md`.

---

## Q1: Is "always-retrieved" a first-class pattern in the paired-lattice format?

**Yes — it's already built.** Membot's multi-cart architecture supports mounting multiple cartridges simultaneously. The `multi_search` function with `scope_mode=per_cart` searches each mounted cart independently and merges results.

For Phase 2, the deployment pattern is:

```
Agent startup:
  mount("substrate-primitives")    # always loaded, never unmounted
  mount("cross-game-patterns")     # always loaded
  
Per-game:
  mount(best_match_game_cart)      # retrieved by visual signature, swapped per game
```

The substrate cart is just another `.cart.npz` file — same format, same search path, same hippocampus metadata. "Always-retrieved" means "always mounted." No special schema needed. The multi-cart layer handles it.

The only architectural note: substrate cartridge entries should be tagged with a `cartridge_type` flag in the hippocampus metadata (byte 5 of the 64-byte struct, currently unused for this purpose). This lets the retrieval layer distinguish "this result came from substrate" vs "this came from game-world" without inspecting content. The small model can then format its reasoning: substrate results as **constraints** ("before clicking, check viewport bounds"), game-world results as **knowledge** ("this game uses rail-extension mechanics").

**Cost:** substrate cart with ~50 entries = ~200 KB. Searched on every query, but at 50 entries the search is sub-microsecond even without Hamming pre-filtering. Invisible to the action budget.

---

## Q2: Do substrate cartridges have visual signatures?

**No — and they shouldn't.** Substrate primitives are interaction-type abstractions, not visual patterns. "Viewport-aware click" doesn't look like anything — it's a rule that applies when a specific condition is detected.

**Retrieval mechanism for substrate cartridges should be keyword/condition matching, not visual similarity:**

| Substrate primitive | Retrieval cue | NOT retrieved by |
|---|---|---|
| Viewport-aware click | `ACTION6 in actions AND world_size > viewport_size` | Frame similarity |
| Action budget | `step_counter visible OR budget metadata present` | Frame similarity |
| Animation timing | `frame_count > 2 after action` | Frame similarity |
| Click classification | `ACTION6 in actions` | Frame similarity |
| Undo semantics | `ACTION7 in available_actions` | Frame similarity |
| Structural alignment | `win_check failed despite position match` | Frame similarity |
| Directional ambiguity | `first_action AND actions include UP/DOWN/LEFT/RIGHT` | Frame similarity |

In practice, this means substrate retrieval is a **rule-matching pass**, not a **similarity search pass.** The small model (or the harness) checks conditions against the current game state and loads applicable substrate primitives. This is cheaper and more reliable than embedding-based retrieval for a fixed, enumerable set of ~10 rules.

**Implementation:** substrate primitives can live in the cart as text entries with condition tags in `per_pattern_meta`, OR they can be a simple JSON config file loaded at startup (since there are only ~10 of them). The cart format works but is overkill for a set this small. A `substrate_primitives.json` sidecar file might be more practical — it loads instantly, needs no embedding search, and the rules are directly actionable as prompt text.

**Recommendation:** ship both. Substrate primitives in a `.json` sidecar for direct rule-loading, AND in a `.cart.npz` for systems that want to retrieve them via semantic search (e.g., if the small model generates a natural-language query like "how do I handle off-screen targets?" and the answer is the viewport primitive). Belt and suspenders.

---

## Q3: Retrieval ordering — substrate first or last?

**Substrate first, as context priors.**

Reasoning: substrate primitives are **constraints on action** — they narrow what the model should consider doing before it reasons about what to do. Loading them first means the model enters game-world reasoning with guardrails already in place.

The analogy: you learn physics before you learn specific games. Gravity applies to every game; you don't re-derive it per game. Substrate primitives are gravity.

**Concrete prompt structure:**

```
[SUBSTRATE CONTEXT — always present]
You are playing an interactive game. The following general rules apply:
- Viewport: if a target is off-screen, scroll before clicking. [applies if scrolling detected]
- Action budget: every action costs. Plan before acting. [applies if step counter visible]
- Click classification: <10px change = selection; >100px = state transition.
- Undo: ACTION7 reverts one step. Use for safe exploration.

[GAME-WORLD CONTEXT — retrieved per game]
This game appears to be similar to "sk48 — Rail Weaver":
- Mechanic: extend rail through colored targets to visit them
- Win condition: visit all targets
- Key insight: targets are non-solid; rail passes through them
- Known trap: failed moves still consume action budget

[CURRENT STATE]
Frame: [embedded game frame]
Actions available: [1, 2, 3, 4, 6, 7]
Budget remaining: 142 / 196

[REASONING]
Given the substrate rules and the retrieved world model, what is the best next action?
```

Substrate first → game-world second → current state third → reasoning last. Each layer builds on the previous. The model never reasons about game-specific actions without substrate constraints already loaded.

**Exception case:** if the substrate cart returns a primitive that contradicts the game-world model (unlikely but possible with novel games), the game-world model should override for that specific game. The prompt can handle this: *"The following substrate rules apply UNLESS the game-world model explicitly states otherwise."*

---

## Q4: Cartridge composition — how are conflicts between simultaneous substrate primitives resolved?

**They don't conflict — they compose as independent constraints.** Each substrate primitive is a precondition check, not an action directive. Multiple preconditions apply simultaneously without contradiction:

| Primitive A | Primitive B | Composition |
|---|---|---|
| "Scroll before clicking OOB target" | "Minimize actions (budget)" | "Scroll efficiently — compute minimum scroll distance, don't over-scroll" |
| "Wait for animation to complete" | "Budget is limited" | "Wait (animation frames don't cost budget), then act" |
| "Click classification: <10px = selection" | "Undo available" | "If uncertain, try a selection-sized click (cheap), observe, undo if wrong" |

**No conflict resolution engine needed.** The composition is natural language reasoning over jointly-loaded constraints. The small model reads all applicable substrate primitives in the prompt and reasons about them together. This is what language models are good at — joint constraint satisfaction over a small set of natural-language rules.

**The one edge case that matters:** budget pressure. When the action budget is tight (say, <20% remaining), the model should shift from "explore safely with undo" to "execute known-good sequences only." This isn't a conflict between primitives — it's a **priority shift** triggered by a state variable (remaining budget). The budget-awareness primitive should include a threshold rule:

```
if budget_remaining < 0.2 * budget_total:
    switch_to_exploitation_mode()
    # no speculative actions, no exploration
    # execute the cached winning sequence if available
    # if no cached sequence: attempt the highest-confidence action only
```

This is a primitive-internal rule, not a cross-primitive conflict. Each primitive manages its own state thresholds. The model doesn't need to resolve conflicts because the primitives are designed to be compositionally coherent.

**Design principle:** if two substrate primitives COULD conflict, that's a signal they should be merged into a single, more nuanced primitive. The catalog should remain a set of independent, composable constraints — not a set of interacting rules that need an arbitration layer. Keep it simple. The small model's reasoning capacity is limited; don't spend it on meta-reasoning about rule conflicts.

---

## Additional note: visual signatures for game-world cartridges

Dennis's §6.3 (Vision IRP) is more critical than we initially appreciated. The LongMemEval benchmark exposed a precision gap: text-to-text retrieval confuses entries with similar topics. For ARC-AGI-3, text queries like "game with colored blocks and movement" would match multiple games.

**Visual frame-to-frame matching solves this.** sk48's rail layout looks nothing like sc25's spell grid at the pixel level, even though both have "colored blocks" in text descriptions. Each game gets a reference frame (or set of frames) stored as a visual embedding in the game-world cartridge. At game time, the current frame is embedded by the vision encoder and matched against these reference frames. The most similar one returns the world model.

Our cart format already supports this — `embeddings` is (N, 768) float32 regardless of whether the vector came from Nomic (text) or a vision encoder (image). The `passages` field stores a reference to the image or a text description. Search is identical: cosine + Hamming on the vectors.

**What we need from Dennis:** the Vision IRP encoder choice. Should we use CLIP (general purpose), SigLIP (better for retrieval), or Gemma4's built-in vision encoder (consistency with the reasoning model)? The answer determines the embedding dimensionality and whether we need a second embedding column in the cart format or can share the existing 768-dim column.

---

*Ready for integration or discussion. — Andy & Claude (Waving Cat)*
