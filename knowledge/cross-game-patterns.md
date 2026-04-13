# Cross-Game Patterns — Distilled from 8 Solved Games

*For competition models. These patterns transfer across game instances.*

## 1. Visual Cue → Mechanic Mapping

What you SEE tells you what it DOES:

| Visual Cue | Meaning | Confidence | Games |
|------------|---------|------------|-------|
| Colored border on a box/slot | Border color = identity. Match indicators to border colors. | HIGH | sb26 |
| Small colored dot at center of a cross/marker | Ownership indicator. The dot color tells you which entity this belongs to. | HIGH | r11l |
| 3×3 grid of toggle cells | Spell/program system. Toggle patterns auto-trigger actions. | HIGH | sc25, tn36 |
| Dashed circle outline | Target position. Move your entity here to win. | HIGH | r11l, tu93 |
| Horizontal bar connecting two groups | Rewrite rule. Left side → Right side transformation. | HIGH | tr87 |
| Checkered square pattern | Waypoint/checkpoint. Landing here saves your position. | HIGH | tn36 |
| Bracket/cursor pair (top+bottom) | Selection indicator. Shows which element you're editing. | HIGH | tr87 |
| Color palette row at edge of screen | Color selector. Click to change active color. | HIGH | cd82, ft09 |
| Orange/progress bar at screen edge | Action budget. Depletes with each action. When empty = lose. | HIGH | sc25, tn36, tu93 |
| Arrow/direction indicator pixel on entity | Entity facing direction. Determines movement and activation. | HIGH | tu93 |
| Gray vs white endpoint markers | Selection state. White = selected/active, gray = available. | HIGH | r11l |

## 2. Interaction Model Patterns

How different game types work:

### Click-Only Games (ft09, tn36, vc33, lp85)
- **No cursor movement** — every click is an action
- Click targets are usually colored regions that respond to clicks
- **Observation trick**: click each distinct colored object once, observe pixel change count
  - 1px change = selection/toggle (cheap, reversible)
  - 10-100px = significant state change (action)
  - 0px = invalid target or already in correct state

### Move+Click Games (cd82, sb26, sc25)
- Movement (UP/DOWN/LEFT/RIGHT) navigates a cursor or character
- Click (ACTION6) acts on the current position or selected target
- **Spell/program systems**: click to set pattern, auto-executes when pattern matches
- **Two-phase interaction**: select target → act on target

### Move-Only Games (tr87, tu93)
- All reasoning through directional input
- UP/DOWN may cycle values (tr87) or move character (tu93)
- LEFT/RIGHT may navigate positions (tr87) or move character (tu93)
- **Key distinction**: are directions MOVEMENT or VALUE CYCLING?

## 3. Win Condition Patterns

| Pattern | Description | Games |
|---------|-------------|-------|
| Position matching | Entity at target position | tu93, r11l |
| Pattern matching | Canvas/grid matches target | cd82, ft09 |
| Structural alignment | Not just position — structural relationship matters | vc33, sb26 |
| Rule satisfaction | Output row satisfies rewrite rules applied to input | tr87 |
| All constraints met | Multiple simultaneous constraints (color, position, etc.) | sc25 |

**CRITICAL**: Position != Win. In vc33, goal at target position did NOT clear the level. The game checks structural alignment, not just coordinates. Always check: did the level actually advance?

## 4. Level Progression Patterns

Every game teaches incrementally:

| Phase | What Levels Teach | Example |
|-------|-------------------|---------|
| L1-2 | Core mechanic in isolation | sb26 L1: flat 1:1 mapping |
| L3-4 | Combinations and constraints | sb26 L3: multi-group hierarchy |
| L5+ | Paradigm shift or new mechanic | sb26 L6: swap instead of pick-place |
| Final | Everything combined | tr87 L6: tree+double+alter all at once |

**Carry patterns across levels.** If a rule worked on L1, it's the first hypothesis for L2. Test it before exploring alternatives. But **rules EVOLVE** — don't assume the pattern is fixed.

## 5. Failure Patterns (What Kills You)

| Failure | Symptom | Correct Response | Games |
|---------|---------|------------------|-------|
| Action budget exhaustion | Progress bar empty, game over | Plan efficient routes. Count before acting. | all |
| Entity activation death | 15-frame animation, entity kills player | Identify activation zones, approach from safe angle | tu93 |
| Wrong assumption perseveration | Repeating same failed approach | If 3 attempts fail, change hypothesis entirely | all |
| Coordinate/position error | Click registers but nothing useful happens | Verify by observing pixel change, not by assuming | sc25 |
| Premature action | Acting before understanding | Observe first. Prediction is free, action is costly. | r11l |

## 6. Exploration Heuristics

When encountering a NEW game:

### Phase 1: Observe (0 actions)
- What's on the screen? Identify distinct colored regions.
- Is there a target/goal visible? (dashed circles, highlighted areas, reference images)
- Is there a progress/step counter?
- What action types are available? (moves only? clicks? both?)

### Phase 2: Probe (2-5 actions)
- Try each available action once. Observe pixel changes.
- For click games: click each distinct colored object. Measure change.
- For move games: try all 4 directions. Which ones work? Which are blocked?
- **Key**: observation actions that produce 1px change are usually reversible and cheap.

### Phase 3: Model (0 actions)
- Classify the game type (click/move/both)
- Identify interactive vs decorative elements
- Form a hypothesis: "clicking brown buttons moves walls"
- Predict what will happen on the NEXT action

### Phase 4: Test (1-3 actions)
- Execute the prediction. Did reality match?
- YES → increase confidence in the model
- NO → update the model. What did you miss?

### Phase 5: Execute
- Use the verified model to plan a full solution
- Count actions before committing
- Verify each step produces the expected result

## 7. Universal Principles

1. **The context window IS the intelligence.** Build a world model before acting.
2. **Prediction is free, action is costly.** Calculate before clicking.
3. **Uncertainty is information.** Not knowing what a button does = click it once to learn.
4. **Persistence ≠ perseveration.** Persistence updates from feedback. Perseveration ignores it.
5. **Small pixel changes are selections. Large changes are actions.** Use pixel count to classify.
6. **Border colors are semantic.** They encode identity, not just decoration.
7. **Direction indicators predict movement.** An arrow or indicator pixel tells you where something will go.
8. **Rules evolve between levels.** The pattern from L1 may change at L3.
9. **Everything visible is information.** There are no decorative elements — if you see it, it matters.
10. **Verify before trusting.** Click, observe, update. Don't assume.
11. **Objects may not be solid to tools.** In sk48, the rail passes THROUGH target blocks instead of pushing them. The visual signature is a 3-frame animation (vs 2-frame normal) and reduced pixel change. Don't assume collision — test it. If an extension produces fewer pixels changed than expected, the tool may have passed through an object. | NEW | sk48 |
12. **Animation frame count encodes interaction type.** Normal actions produce 2-frame animations. Object interactions (pass-through, embed, crush) produce 3+ frame animations. Use frame count as a classifier for what kind of interaction occurred. | NEW | sk48 |
13. **Retraction can pull, not just shorten.** In rail/track games, retracting the tool may pull embedded objects toward the head. This is a second use of the same action — the tool doubles as both a pusher (extend) and a puller (retract). | NEW | sk48 |

## Engine Budget Exhaustion Masquerading as State-Space Exhaustion

**Discovered**: sk48 session 2026-04-12

Every ARC-AGI-3 game has an action budget (`game.qiercdohl` or equivalent) that ticks down on each action — INCLUDING failed moves (blocked extensions, out-of-bounds slides, invalid clicks). Once the budget hits 0, the game enters `GAME_OVER` and silently rejects further state changes.

**Symptom**: Beam search or BFS "gets stuck" at suspiciously small reachable state count (e.g. 33 states on sk48 L2). Heuristic stops dropping. Search declares exhaustion.

**Root cause**: The 34th expansion hits budget=0 → GAME_OVER → subsequent state reads return stale/invalid data → dedup thinks the state is already visited → search believes it's explored everything.

**Fix**: Save `init_budget = game.qiercdohl` at search start, restore `game.qiercdohl = init_budget` after each beam expansion. This unlocks thousands of reachable states.

**Lesson**: When engine-backed search "feels stuck" at a low state count, check whether failed moves consume resources that terminate the game. The signature of budget exhaustion is: "my beam keeps returning the same N states, heuristic won't drop, but my code looks correct." Always save/restore budget around expansions.

**Games this might silently affect**: any game where previous solvers concluded "beam search is ineffective" at low state count. Worth auditing: dc22 (snapshot corruption noted by earlier agent — possibly same root cause), wa30 L7 10/13 ceiling, lf52 L7 2.2M state search (probably real, budget restoration applied).
