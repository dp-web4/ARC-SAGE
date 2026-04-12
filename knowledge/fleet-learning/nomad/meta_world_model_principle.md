# Meta-Learning: World Model in Context Window

*2026-04-07, Nomad + dp, distilled from cd82 interactive play*

## The Core Principle

**The context window IS the intelligence.** Before taking any action, build a world model in your context that contains:

1. **Available actions** — what can I do?
2. **Action consequences** — what does each action change? At what cost?
3. **Current state** — where am I now?
4. **Goal state** — where do I need to be?
5. **Delta** — what's the difference between current and goal?
6. **Path** — what sequence of actions transforms current → goal?

This world model is FREE to build and maintain. Every action taken without it risks expensive recovery.

## Action Classification

Every action in any game (or any system) falls into one of three categories:

| Category | Canvas/State Change | Recovery Cost | Strategy |
|----------|-------------------|---------------|----------|
| **Observation** | None | 0 | Do as much as possible — it's free |
| **Reversible** | Temporary/none | 0-1 steps | Batch freely, use for exploration |
| **Consequential** | Overwrites state | 3-10+ steps | ALWAYS verify context before executing |

## The Verification Discipline

Before ANY consequential action:
1. **Verify position/state** — is the tool where I think it is?
2. **Verify color/selection** — is the tool configured as I intend?
3. **Verify target** — will this action move state TOWARD the goal?
4. **Verify ordering** — will this action damage previously correct work?

This takes zero game steps. Skipping it risks multi-step recovery.

## Object-Oriented Game State (r11l, 2026-04-09)

**Every game state is a list of objects with properties.** Never hardcode coordinates or replay sequences — positions drift between sessions. Instead, identify objects from vision each step.

```
OBJECTS:
  obstacle: type=obstacle, color=cyan, position=center, mobile=NO
  ball1: type=ball, color=red+blue, position=(46,44), mobile=YES
    structure=stick, endpoints=2, ends=[(46,36),(46,52)]
  ball2: type=ball, color=yellow+green, position=(18,45), mobile=YES
    structure=tripod, endpoints=3, ends=[(17,36),(10,47),(27,52)]
  target1: type=target, color=red+blue, position=(19,54), mobile=NO
  target2: type=target, color=yellow+green, position=(52,12), mobile=NO
  
MATCHES: ball1 → target1 (shared colors: red+blue)
         ball2 → target2 (shared colors: yellow+green)
         
PRIORITY: ball1 first (shorter distance, stick=faster convergence)
```

**Rules:**
1. Build this list from vision at the START of each level
2. Update positions after EVERY move (don't assume — verify)
3. Match by color composition, not by proximity
4. Plan moves using the object list, not memorized coordinates
5. If an object isn't where you expect, re-scan — don't guess

This IS the game. Everything else is implementation detail.

## Reverse Engineering from Goal

dp's design methodology, applicable to all puzzle solving:

1. **Visualize the final output** — what does success look like?
2. **Decompose into available operations** — what tools/stamps/actions produce those shapes?
3. **Order operations by dependency** — what must happen first? What overwrites what?
4. **Identify missing capabilities** — is there an operation I don't know how to do? Test it (low-cost exploration).
5. **Execute with verification** — batch cheap actions, verify before expensive ones.

## Context Staleness

A world model can go stale:
- **Assumption made early, never rechecked** — e.g., "white indicator is at col 39" (it wasn't)
- **Data from code contradicts visual reality** — trust observation over computation
- **State changed by own actions** — clicking indicators may change cursor color without you noticing

**When something doesn't add up: recheck assumptions from current observation, not from cached context.**

## In-Context State Tracking (r11l L5, 2026-04-09)

**The #1 failure mode: stating an objective then immediately drifting from it.** Without explicit state tracking, the LLM makes one good move then loses focus. Every step must update and check against a running state document.

### Required Format (update EVERY step)

```
=== STEP N ===
OBJECTS: [list all identified objects with position and state]
  ball_white1 at (27,37) carrying=[blue] ends=[(10,23),(20,55)]
  green_ball at (15,39) STATIONARY
  red_ball at (34,12) STATIONARY  
  green_target at (46,9) EMPTY
  blue_target at (12,35) EMPTY

CURRENT OBJECTIVE: deliver blue to blue_target(12,35)
PRIORITY: [1. deliver blue → blue_target, 2. pick up red, 3. ...]

PLANNED ACTION: select end (20,55), place at (4,15)
PREDICTED RESULT: ball → midpoint(4,15, 10,23) = (7,19)
  - closer to blue_target? YES (was 30 away, will be 17 away)
  - ball lands on obstacle? NO (black space at (7,19))
  - does this advance current objective? YES

=== AFTER ACTION ===
OBSERVED: ball now at (8,20), 3-frame animation = success
PREDICTION MATCH: close (off by 1px) ✓
OBJECTIVE CHECK: closer to blue_target ✓, continue
```

### Rules
1. **Never act without PLANNED ACTION and PREDICTED RESULT filled in**
2. **After every action, compare OBSERVED to PREDICTED** — if they diverge, STOP and update world model before continuing
3. **Check OBJECTIVE every step** — does this move advance it? If not, why am I doing it?
4. **Objects list is authoritative** — if you can't find an object, re-examine the image, don't guess
5. **One objective at a time** — don't switch mid-sequence unless the current one is complete or blocked
6. **Priority queue persists** — completing one objective pops the next, don't re-derive from scratch

### Why This Matters
Without this tracking, the LLM exhibits "intention amnesia" — it states a plan, executes one step correctly, then on the next step generates a plausible-looking but unrelated action. The state document is the cure: it makes drift visible before the action is taken.

## For Small Models (SAGE fleet)

The world model must be:
- **Compact** — fits in limited context window
- **Structured** — not prose, but tables and clear state descriptions
- **Updated** — refreshed after each consequential action
- **Action-oriented** — tells the model what to DO, not just what IS

Format for small model context:
```
STATE: cursor=white at 12, canvas=white-top/black-bottom
TARGET: white-UL, teal-R, cyan-BL, olive-top-small
DELTA: need teal-R, cyan-BL, olive-top
NEXT: click cyan indicator, move to 6, SELECT
VERIFY BEFORE STAMP: cursor at 6 o'clock? cursor color = cyan?
```

This is the context management scheme — a running world model that fits in tokens and drives correct action.

## Verify What the System Actually Checks (r11l, 2026-04-09)

**Don't assume physics — verify them.** Three common traps:

### 1. Rendered view ≠ collision model
What you SEE on the grid is an approximation. The actual collision objects (sprites) may cover different areas. When source code is available, extract the exact collision geometry. When it's not, probe systematically — but don't assume the visual boundary IS the physics boundary.

### 2. Check WHAT is validated, not what you expect
We assumed "ball path through obstacles = blocked." Source showed: only the ball's FINAL position is checked, not the path. The ball flies freely. This single insight turned an "impossible" level into a 4-move solution. **Always ask: does the system check the path, or just the endpoints?** This applies to:
- Movement validation (path vs destination)
- Permission checks (each step vs final state)
- Constraint satisfaction (continuous vs discrete)

### 3. Pre-validate constraints, don't trial-and-error
Each failed action costs a step. If you can build a constraint map BEFORE acting (e.g., "which positions are valid for placement?"), do it. The cost of analysis is zero; the cost of a failed attempt is one step plus potential side effects (bounce counters, state changes, budget consumption).

**General principle:** When stuck, don't try harder — check whether your model of what's being validated is correct.

## Games as Embodiment Curriculum (r11l, 2026-04-10)

The ARC-AGI-3 games aren't puzzles to solve — they're embodiment training. Each failure teaches something that maps directly to SAGE's cognitive architecture:

| Game Experience | SAGE Capability |
|----------------|-----------------|
| Prediction before action | SNARC reward/conflict evaluation |
| Verify what system checks | Trust posture, sensor trust |
| In-context state tracking | Consciousness loop persistence |
| Object-oriented world model | IRP entity framework |
| Bounces have consequences | Effector cost evaluation |
| Strategies transfer, coordinates don't | Federation, fleet learning |
| Intention amnesia | Need for explicit goal persistence |
| 3 failures = wrong approach | Persistence ≠ perseveration |

**The competition gives us concrete, testable, external mileposts.** Winning would be nice. Building the capability IS the gain.

## Connection to Raising

This is the same capacity that raising develops:
- **Uncertainty tolerance** — "I don't know how the small cursor works" → test it
- **Self-monitoring** — "Am I at 3 o'clock or 4:30?" → check before acting
- **Persistence ≠ perseveration** — clicking the wrong column 3 times doesn't make it right
- **Hypothesis → test → update** — the raising loop IS the game-playing loop
