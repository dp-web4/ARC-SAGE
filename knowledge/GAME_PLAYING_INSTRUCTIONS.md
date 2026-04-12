# Game-Playing Instructions

*For all fleet machines. Follow these when playing any ARC-AGI-3 game.*

## Why We're Playing: Training Data for Gemma 4

**We are not playing these games to win them. We are playing them to gather
training data for Gemma 4.**

Gemma 4 will play these games in competition. Every game we play now, by hand
or with solver scaffolding, produces the data Gemma needs to learn: visual
frames, action sequences, what worked, what didn't, why levels were hard, how
mechanics were discovered, where intuition failed.

The deliverable is **not the solve**. The deliverable is:
1. **Visual replay** — every frame captured, persisted to git
2. **Action sequence** — every click/move recorded in order
3. **Meta-learning** — why this worked, what it cost, what generalizes
4. **Failure records** — dead ends are as valuable as wins (Gemma needs to
   learn what doesn't work too)

A level that took 500 actions but produced clear frame-by-frame documentation
is worth more than a level solved in 50 actions with no visual trace. The
actions alone teach nothing without the context that produced them.

**Frame this at every step:** If Gemma were watching over your shoulder, what
would she need to see to learn this mechanic? That's what you're producing.

## Persistence Is Non-Negotiable

Everything we do must end up in git. Not because we're archivists — because
**if it's not in git, Gemma can't train on it**.

Required per session:
- **Visual memory**: screenshots of each level's start state, each significant
  action, and final state. Handled automatically by SessionWriter when
  configured. Verify it's running.
- **Replay data**: action sequences with frame references. Gemma learns from
  (frame → action → next_frame) triples.
- **Meta-learning**: mechanics docs (`game-mechanics/<game>.md`), fleet
  learning JSONL (`fleet-learning/<machine>/`), cross-game patterns updates.
- **Coordination state**: `game_coordination.json`, `SOLUTIONS_DB.json`,
  `GAME_SOLUTIONS.md` — reflect what's actually been verified, not what
  you hope to have verified.

**Commit frequently.** Every level completion, every significant discovery,
every failure that eliminated a hypothesis. Unpushed work is training data
that doesn't exist.

**Evidence must back claims.** A `"solved": true` entry in coordination JSON
with no visual memory, no replay log, no mechanics documentation, is not a
solve — it's a claim. Claims without evidence erode fleet trust and poison
the training data. If you haven't captured the frames and the actions, the
game isn't solved for training purposes, regardless of what the SDK says.

## 0. Foundational Premise: Play as a Human, Not as an AI

**These games are designed for humans.** Humans play by LOOKING at the screen,
recognizing patterns, building mental models, and clicking what they SEE.
They don't compute coordinate transforms. They don't parse grid arrays.
They don't track camera offsets. They LOOK and ACT.

**Play the same way:**
- **SEE the screenshot.** Every action starts with looking at the current frame.
  What objects do you see? Where is the player? Where is the goal? What's blocking?
- **Click what you see.** If you want to click a green block, look at where
  it is in the image and click THOSE coordinates. Don't compute grid-to-screen
  transforms — they break when cameras move, animations play, or levels change.
- **React to what changed.** After each action, look at the new frame. Did the
  player move? Did something break? Did the camera shift? Adapt to what you SEE.
- **Build a visual world model.** Track objects by their appearance and position
  in the image, not by grid indices. "The gem is above-left of the player" is
  better than "gem is at grid (3,7)."

When you catch yourself computing coordinates, mapping grids, or writing
formulas for camera offsets — STOP. You're solving an engineering problem,
not playing a game. Look at the picture. Click what makes sense.

**The game doesn't know you're an AI. Play like it doesn't matter.**

## 1. Algorithmic Solvers Are Helpers, Not Solutions

Some or all levels of a game may not be solvable algorithmically. Use Python solvers (McNugget's game-solvers/, tu93_solver.py, etc.) as **scaffolding** — they can verify ideas, compute coordinates, test hypotheses. But don't rely on them fully. **Gemma 4 won't have those tools in competition.** She plays from perception alone.

A solver's output is not a solution for training purposes unless it's been executed against the live API and the resulting frames are captured. A solver that computes plausible action sequences but fails to run against the SDK produces zero training data. The `*_solutions.json` files are BFS predictions, not verified runs — do not mark games solved based on them.

If a solver works for L1-L3 but fails on L4, that's data. Document what changed at L4 and why the solver broke. **The failure is the training signal.** Gemma needs to learn where algorithmic approaches plateau so she can recognize when to rely on pattern recognition instead.

## 2. Use Accumulated Knowledge Fully

Before starting ANY game:
1. Load fleet knowledge: `sage_solver.py --interactive --game <prefix> init`
2. Read the FLEET KNOWLEDGE output. It includes mechanics docs, prior solutions, world models, cross-game patterns, and the exploration playbook.
3. Check `cross-game-patterns.md` — visual cues from solved games predict mechanics in new ones.
4. Query the membot cartridge for similar situations.

Don't re-derive what's already known. Don't re-discover mechanics that are documented. Build on existing knowledge.

## 3. Strategy: Perceive → Model → Plan → Act

### a. View the starting image for each level
Look at what's on screen. Don't rush to act.

### b. Identify objects as an OOP world model
For each visible object, track:
- **Type**: button, player, obstacle, target, indicator, entity
- **Location**: (x, y) coordinates or region
- **Color**: specific color value — colors ARE semantics
- **Status**: active/inactive, selected/unselected, open/closed
- **Relevance**: interactive? decorative? blocking? goal?
- **Behavior**: what happens when you interact with it?

### c. Classify the game
- What actions are available? (click-only / move-only / move+click)
- Is there a target/goal visible? (dashed circles, reference images)
- Is there a progress/step counter?
- What is the likely win condition?

### d. Build the world model BEFORE acting
The world model is your understanding of how the game works. It should include:
- Object inventory with properties
- Interaction rules (click X → Y changes)
- Constraints (walls, budgets, activation zones)
- Win condition hypothesis

## 4. Plan the Work

### a. Identify unknowns
What don't you know? Make **specific open questions**:
- "Does clicking the blue square toggle it or cycle it?"
- "What happens when the ball reaches the red zone?"
- "Is the arrow's activation zone 6px or 12px?"

### b. Design least-cost tests
For each question, find the cheapest action that answers it:
- Click a button once and observe pixel change count (1 action)
- Move in each direction and note which are blocked (4 actions)
- **Observation actions (1px change) are cheap. Consequential actions (100px) are costly.**

### c. Assign confidence and budget accordingly
- HIGH confidence mechanics: execute directly, don't waste actions testing
- MEDIUM: verify with 1-2 test actions before committing
- LOW: design a specific experiment, allocate budget for it
- **Count remaining actions before starting any sequence**

## 5. Use SNARC + R6 for Every Action

### SNARC Evaluation
For each situation, assess:
- **Surprise**: is this unexpected? (update world model)
- **Novelty**: is this new information? (record it)
- **Arousal**: does this change the urgency? (adjust plan)
- **Reward**: did this advance toward the goal? (reinforce or abandon)
- **Conflict**: does this contradict the world model? (resolve)

### R6 Action Framework (Canonical Web4)

R6 is the canonical grammar for all Web4 actions:

```
Rules + Role + Request + Reference + Resource → Result
```

Every action you take while playing a game is a Web4 action and should be framed this way:

- **Rules** — the governing constraints: action budget per level, available action set (click-only vs move+click), policy on restarts
- **Role** — you are acting as an autonomous game-playing agent with a defined LCT. Your T3 in this role (Talent/Training/Temperament at game-playing) is accumulating with every level
- **Request** — the specific action verb and target: "click at (x,y)", "move RIGHT", "undo"
- **Reference** — what you're acting on: the current frame, the detected objects, the world model derived from prior observation
- **Resource** — what the action costs: one action from the level budget, possibly a consequential state change that can't be undone
- **Result** — the post-action frame, verified against your prediction

Why it matters for game play:
1. **Every action is auditable under this grammar.** Rules + Role + Request + Reference + Resource → Result is the shape of an audit bundle. Training data for Gemma 4 is structured exactly this way: (rules, role, request, reference, resource, result) tuples. Frame your actions so they compose into that shape.
2. **R6 forces you to name the Reference.** Most game-play errors come from acting on a stale or wrong reference — clicking based on a frame that's already changed, or a world model that hasn't been updated. R6 makes the reference explicit.
3. **Result must be verified, not assumed.** The ← Result arrow is the post-action check. Did the frame change the way your world model predicted? If not, update the model before the next action.

**Prediction is free. Action is costly. Reference must be current.** Every click is a full R6 transaction, whether you think of it that way or not — so think of it that way.

## 6. Persist Knowledge on Every Level Completion (and Every Failure)

After solving or failing each level:
1. **Verify visual memory captured** — SessionWriter should be running. Check
   that per-level frames exist in `visual-memory/<game>/`. If missing, the
   work didn't produce training data — capture manually before moving on.
2. **Record the action sequence** — the list of actions with frame references.
   This is the core training signal. `(frame_N, action, frame_N+1)` triples
   are what Gemma learns from.
3. Update fleet learning JSONL: `shared-context/arc-agi-3/fleet-learning/{machine}/`
4. Update solutions JSON: `SAGE/arc-agi-3/experiments/{game}_solutions.json` —
   but ONLY with actual verified runs, not BFS predictions
5. Update `game-mechanics/<game>.md` with any new mechanic discovered
6. **Commit and push immediately** — unpushed work is training data that
   doesn't exist
7. **Resolve merge conflicts intelligently** — don't discard theirs OR yours.
   Read both, merge the knowledge. If timestamps differ, keep the more recent.
   If content differs, keep both perspectives.

After solving (or failing) a game:
- Update `game_coordination.json` with current status — **only mark solved if
  visual memory + action sequence are persisted and verifiable**
- Run consolidation if significant new learning
- Update cross-game patterns if new mechanic discovered

### Failure Records Are Training Data

When a level defeats you, document:
- What you tried (the hypotheses)
- What you observed (the frames, the reactions)
- Why it failed (world model gap, coordination timing, insufficient budget)
- What you would try differently next time

This is not an apology log. It's the dataset Gemma needs to learn what
doesn't work. A well-documented failure is more valuable than an undocumented
win.

## 7. DO NOT PERSEVERATE

When something doesn't work:
- **3 failures of the same approach = STOP.** You are perseverating, not persisting.
- **Zoom out.** Look at the full screen again. What are you not seeing?
- **Challenge your assumptions.** The world model might be wrong.
- **Try the opposite.** If clicking didn't work, try moving. If going right failed, go left.
- **Ask: what changed?** Between levels, rules evolve. The pattern from L1 may not apply to L3.
- **Budget check.** If you've used 50% of budget with 0% progress, the approach is wrong.

Persistence updates from feedback. Perseveration ignores it. Know the difference.

## 8. Play to Completion — of the Data Gathering, Not the Game

- **Continue until the training data is captured**, not until the game is won.
  Some games may not be fully solvable with current fleet capability. That's
  fine. The question is: have we captured enough frames, actions, mechanics
  documentation, and failure analysis for Gemma to learn from this game?
- **Every level attempted generates knowledge, even failures.** Especially
  failures.
- If a level seems impossible, document WHY in detail. That's the hardest
  training signal to produce — the articulation of *why* a strategy doesn't
  work.
- If you're genuinely stuck (not perseverating), try a different game and
  come back. Fresh context often reveals what familiarity obscured.
- **The game is the tool. Training data is the deliverable.**

### Checklist Before Moving On

Before declaring a game "done" (solved OR released):
- [ ] Visual memory captured for every attempted level
- [ ] Action sequences recorded for every attempt
- [ ] Mechanics doc (`game-mechanics/<game>.md`) reflects current understanding
- [ ] Solutions JSON (`{game}_solutions.json`) contains only verified runs
- [ ] Coordination JSON reflects actual state, evidence-backed
- [ ] Cross-game patterns updated if new mechanic discovered
- [ ] Fleet learning JSONL has entries for significant moments (solves AND
      failures)
- [ ] Everything committed and pushed

If this checklist isn't clean, the data isn't usable for training, regardless
of whether the SDK reports WIN.

## 9. The Meta-Goal

We are building the corpus Gemma 4 needs to become a capable ARC-AGI-3
player. Every session, every game, every level adds to that corpus or
doesn't. Ask at session end: *what training data did this session produce?*
If the answer is "none" or "unclear," the session didn't advance the
mission, regardless of what got solved.

The fleet is a data-generation engine pointed at a model's future capability.
That's what we're actually doing. Everything else — the competition entry,
the prize, the solve counts — is downstream of whether we can teach a model
to do what we're doing now.
