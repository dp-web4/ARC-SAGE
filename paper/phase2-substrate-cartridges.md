# Phase 2 Design Note: Substrate Cartridges

*Supplement to `paper/draft.md` §5.4 and §6.2. Concrete design notes for the two-layer cartridge bundle.*

**Context**: Phase 1 produced 25 game-world cartridges (per-game ontologies). The `bp35` competition submission exposed a gap — solvers internalized correct world models but not the viewport-as-interaction-constraint, because the local SDK engine didn't enforce it. Fixing this per-game is ad hoc. Elevating "interface primitives" to a first-class cartridge layer is the right architectural response.

## Design goals

1. **Separability**: substrate primitives should not be bound to any specific game. A new game inherits them automatically via retrieval.
2. **Composability**: multiple substrate primitives may apply simultaneously (e.g., viewport-aware + action-budget-aware + undo-aware). The schema must support concurrent retrieval.
3. **Small-model tractable**: a Gemma-class model must be able to read the cartridge content and apply it within a typical context window. No deep nesting; statements should be directly actionable.
4. **Failure-transparent**: when a substrate primitive doesn't apply (e.g., a game has no scrolling), its retrieval should be cheap to no-op. Retrieval should not force the model to "fight" an irrelevant rule.

## Initial substrate primitive catalog

Based on the 25-game Phase 1 dataset, the following substrate primitives are candidates:

### 1. Viewport-aware click

**Trigger**: game has scrolling camera OR scrollable grid offset; ACTION6 is available; target object identified; AND clicking the target is expected to trigger a state-changing game action (not merely select it with no follow-on transition).

**Scroll-model decomposition (from lf52 session 9, 2026-04-13)**: not one primitive — two. First check which model the game uses before applying.

- **Camera-based** (bp35 et al.): game has a `camera` attribute with position. Player movement drives camera position via a game-specific formula. Solver can control scroll by choosing player moves.
- **Grid-offset side-effect** (lf52 et al.): no camera object; `camera.position()` returns `(0, 0)` always. A specific action pattern (e.g., pushing a piece-riding-block configuration into a wall) triggers an offset shift on the grid container. Solver must FIND such sequences and REORDER clicks around them. The fix for lf52 L3 was pure reorder — zero action-count cost.

The cartridge for this primitive carries both sub-rules and a dispatch based on detected scroll model.

**Scope bracket (from lf52 session 8)**: this primitive applies when both (a) the target is in-world but outside viewport, AND (b) selecting it enables a new state transition. The condition (b) must be evaluated against the game-world cartridge. bp35 clicks satisfy both; lf52 L7 clicks satisfy only (a) — the selected peg has no legal jumps, so OOB clicks reach it but produce no progress. A naive "always scroll if OOB" heuristic would waste action budget on lf52-like games. The cartridge schema must carry this precondition explicitly.

**Rule**:
```
if target_world_position.y not in [camera_y, camera_y + 63]:
    # target is off-screen
    compute_required_scroll_direction()
    scroll_via_appropriate_action()
    # (may require multiple scroll actions if camera scrolls one step at a time)
now_click_at_viewport_coord = (target.x, target.world_y - camera.y)
assert 0 <= now_click_at_viewport_coord.y <= 63
env.step(ACTION6, data=now_click_at_viewport_coord)
```

**Applies to**: bp35, dc22, re86, ar25, lf52, and any future game with scrolling.

**Detection**: camera position changes in response to player actions; world grid larger than visible viewport.

### 2. Action budget awareness

**Trigger**: game has a visible progress/step counter that decreases with actions.

**Rule**:
```
save_budget = game.budget
for candidate_move in search_tree:
    restore_budget_after_try()  # prevents speculative search from starving the real game
keep_track_of_remaining_budget()  # plan for it
```

**Applies to**: most games with level timers; critically to sk48 where failed moves consume budget.

### 3. Animation timing

**Trigger**: actions produce multi-frame responses before game state stabilizes.

**Rule**:
```
after env.step(), if response has multiple frames:
    wait_for_animation_complete() before reading game state
    don't_base_next_action_on_intermediate_frame
```

**Applies to**: sk48 (3-frame pass-through), tu93 (activation animations), most click games.

### 4. Click classification by pixel change

**Trigger**: ACTION6 is available and observation includes frame comparison.

**Rule**:
```
delta_pixels = count_changed_pixels(before, after)
if delta_pixels < ~10: action was selection/toggle (cheap, reversible)
elif delta_pixels > ~100: action was state transition (costly, may be irreversible)
else: action was observation-adjacent (borderline — verify intent)
```

**Applies to**: click-games (ft09, tn36, vc33, lp85) and move+click games (sb26, sc25).

### 5. Undo semantics

**Trigger**: ACTION7 (UNDO) is in the available action set.

**Rule**:
```
if about_to_take_irreversible_action:
    verify_action_intent_one_more_time (undo won't save you across some transitions)
else:
    speculative_actions_are_safe(undo_can_revert)
```

**Applies to**: games where `available_actions` includes ACTION7. Not available in competition mode for the scored games, per ENVIRONMENT.md — worth confirming per-game.

### 6. Structural alignment != positional match

**Trigger**: win condition involves spatial arrangement of multiple elements.

**Rule**:
```
if moving piece to apparent target position does not win:
    win condition is structural, not positional
    re-examine relationships: what do the colors/borders/shapes of OTHER elements signify?
```

**Applies to**: vc33 (position alone != win), sb26 (hierarchical placement).

### 7. Directional ambiguity

**Trigger**: game uses UP/DOWN/LEFT/RIGHT actions but game type unclear.

**Rule**:
```
try one directional action, observe:
    if character visibly moves: MOVEMENT game
    if values on screen cycle: VALUE-CYCLE game (tr87)
    if all tiles shift simultaneously: BULK-MOVE game (lf52)
```

**Applies to**: all directional-input games during initial exploration.

## Integration with game-world cartridges

When the small model reasons at step T:
1. **Always retrieve** all substrate cartridges (small, finite set, ~5-10 primitives).
2. **Retrieve** the game-world cartridge by visual signature similarity to current frame.
3. **Reason** jointly over both layers. Substrate primitives generally manifest as constraints or preconditions on game-world action choices.

Example reasoning trace (hypothetical, `bp35`-like):
```
[game-world] the target gem is at world position (x=7, y=22)
[substrate/viewport] camera.y=0; target.y=22 is at viewport y=22 — in range
[substrate/viewport] click at (42, 132) — wait, that's OOB; recompute
  → (42, 132-0=132) — still OOB
  → y must be * 6 = 132 is world pixels, viewport is in pixels too
  → viewport y range in pixels is [0, 378], so 132 is in range
  → (actually the cartridge should state units clearly)
[action] ACTION6 x=42 y=132
```

This example illustrates a side-issue worth flagging: substrate primitives must be **unit-explicit**. The `bp35` bug was partly a unit-confusion bug — grid cells vs pixels, viewport vs world. Cartridges that leave units implicit will propagate the same confusion.

## Open design questions for Andy

- **Is "always-retrieved" a first-class pattern in the paired-lattice format**, or do we simulate it by attaching substrate cartridge IDs to every game-world cartridge as a small appendix?
- **Do substrate cartridges have visual signatures**, and if so, what do they look like? A "viewport-aware click" cartridge isn't tied to a specific frame — it's more an interaction-type tag.
- **Retrieval ordering**: should substrate cartridges load first (as context priors) or last (as override rules)? The answer probably depends on whether the small model tends to derive primitives before consulting memory or vice versa.
- **Cartridge composition**: when multiple substrate primitives apply simultaneously, how are potential conflicts resolved? (E.g., viewport-aware click says "scroll first"; action-budget says "minimize actions"; these are compatible but need joint reasoning.)

## Falsification

The two-layer claim is falsifiable. If the Phase 2 Gemma deployment, equipped with the full substrate + game-world cartridge bundle, scores below 15% on the public set (same falsification threshold as the overall Phase 2 thesis in §6.6), we will have evidence that substrate primitives are insufficient to substitute for the frontier model's in-context substrate awareness. Possible explanations in that case:
- Substrate primitives were wrong or incomplete.
- Small model cannot execute joint reasoning over substrate + game-world cartridges.
- The substrate/game-world factoring itself is wrong.

Any of these is informative. The null hypothesis is that the factoring is correct and the substrate primitives are recoverable; the experiment will show whether that's so.
