# ARC-SAGE Compliance Split Plan

## Purpose

This memo turns the current ARC-SAGE repo into two clearly separated tracks:

1. **Research track** — preserves the current work exactly for transparency, reproducibility, and scientific value.
2. **Submission track** — strips out the parts most likely to be classified as benchmark-specific preparation and rebuilds the scored path around a single general-purpose agent.

The goal is not to pretend the current repo was something else. The goal is to produce a second, cleaner package that ARC organizers would have a harder time labeling as non-compliant or legacy.

---

## Current public signals that likely trigger `LEGACY`

### ARC public docs emphasize:
- ARC-AGI-3 is meant to measure generalization in **novel, unseen environments**.
- Competition Mode for leaderboard visibility requires:
  - API interaction only
  - one `make` per environment
  - one scorecard
  - all environments counted
  - no game resets
  - no in-flight score peeking
- Recordings are available for API play and swarms, but local toolkit runs do not create official recordings.

### ARC-SAGE README currently advertises:
- “For each of the 25 games, the workflow is: read the engine source, write a world model, choose a search strategy.”
- “The result: 25 working solvers.”
- `environment_files/` contains ARC-AGI-3 game engines.
- `knowledge/` contains game mechanics docs and cross-game patterns.
- `arc-agi-3/experiments/` contains 25 game solvers and capture/submit infrastructure.

### Practical reading
The current repo openly describes:
- per-game source inspection
- per-game world-model construction
- per-game search strategy selection
- per-game solver implementation

That is strong work, but it is also very likely the exact thing ARC can point to when they want to say:
> this is benchmark-specific preparation, not a single general-purpose agent adapting online.

---

## Strategic recommendation

Do **not** mutilate the current repo to make it look compliant.

Instead:
- keep the current repo honest and intact as **ARC-SAGE Research**
- create a sibling branch or repo called something like **ARC-SAGE-General** or **ARC-SAGE-Submission**
- make the compliant submission path so clean that reviewers can inspect it without ambiguity

This avoids destroying the strongest evidence of what you actually accomplished.

---

## Compliance target

A compliant submission package should be able to say all of the following truthfully:

- Uses a **single general-purpose agent** across all environments.
- Does **not** read environment source during scored execution.
- Does **not** dispatch to a solver based on game identity.
- Does **not** load benchmark-specific world models for known public games.
- Does **not** rely on prior replay traces of the same scored environments.
- Builds hypotheses only from observations gathered during the run.
- Runs scored evaluation only in `OperationMode.COMPETITION`.

If you cannot say those things plainly, ARC can probably classify the result however they want.

---

## Repo split: what to move vs keep

## Keep in Research track
These are valuable and should stay public, but should not be part of the scored submission package.

### Top-level items to keep in `research/`
- `environment_files/`
- `knowledge/`
- `CAPTURE.md`
- `REPRODUCE.md`
- `PRUNE_NOTES.md`
- any visual capture archives
- any notes that explicitly document mechanics of named public games

### `arc-agi-3/` items to keep in `research/`
- `arc-agi-3/experiments/` if it contains per-game solvers or benchmark-specific infra
- `arc-agi-3/shared_knowledge/` if keyed to public game mechanics
- `ENVIRONMENT.md` if it discusses known public engines in a way used during solving
- `LIVED_EXPERIENCE.md` if it stores benchmark-specific priors
- `STOCHASTICGOOSE_ANALYSIS.md` if it is based on known environments
- any material describing specific public-game ontologies or mechanics

### Keep `membot/` in research by default
If `membot/` has benchmark-conditioned cartridges, keep it out of the submission track.

---

## Keep in Submission track
Only keep modules that can survive the following test:

> If a reviewer asks, “Could this same code face 25 unseen environments without knowing which ones they are?”, the answer should be yes.

That usually means keeping only generic components such as:
- frame ingestion
- generic object extraction
- generic hypothesis store
- generic planner/search engine
- generic action execution
- generic within-run memory
- competition runner

---

## Proposed directory structure for the clean submission package

```text
ARC-SAGE-Submission/
  README.md
  COMPLIANCE.md
  pyproject.toml
  src/
    sage_submission/
      __init__.py
      competition_runner.py
      agent.py
      perception/
        grid_parser.py
        object_tracker.py
        salience.py
      memory/
        episode_memory.py
        level_memory.py
        hypothesis_store.py
      reasoning/
        action_model.py
        mechanics_induction.py
        generic_planner.py
        macro_discovery.py
      policies/
        exploration_policy.py
        exploitation_policy.py
        reset_policy.py
      eval/
        scorecard_runner.py
  tests/
    test_competition_mode.py
    test_no_game_identity_routing.py
    test_no_source_access.py
  docs/
    architecture.md
    limitations.md
```

This should be boring to inspect. Boring is good.

---

## Concrete refactor rules

## Rule 1: no game-identity routing

### Remove
Anything like:
- `if game_id == ...`
- named solver registry keyed to known public IDs
- dynamic imports of per-game modules
- lookup tables mapping known games to search heuristics or ontologies

### Replace with
A single agent entrypoint, for example:
- perceive current frame
- infer entities and affordances
- form/update hypotheses about mechanics
- choose exploratory or exploitative plan
- execute next action
- revise hypotheses based on transition

### Test to add
A unit test that fails if any public game ID appears in the submission package.

---

## Rule 2: no source inspection in scored path

### Remove
Any scored-time logic that:
- opens local environment engine files
- parses environment source code
- loads prebuilt mechanic notes derived from those source files

### Replace with
Mechanics induction from transitions only:
- object persistence
- object motion patterns
- collision outcomes
- toggles and state flags inferred from action→state changes
- reward or win-state detection inferred from API responses and terminal states

### Test to add
A test that runs the submission package in an environment without `environment_files/` present.

If the agent breaks, it is not actually compliant.

---

## Rule 3: no benchmark-specific prior memory

### Remove
Any cartridge, embedding index, doc store, or cache that contains:
- public game names or IDs
- handwritten world models for known public environments
- replay-derived mechanic summaries for those exact environments

### Replace with
Two memory layers only:

1. **Within-environment memory**
   - tracks hypotheses during a single environment run
   - persists across levels if allowed by the benchmark dynamics

2. **Generic prior memory**
   - stores only domain-general abstractions such as:
     - pushing mechanics
     - toggle doors
     - projectile hazards
     - color-linked targets
     - movement constraints
   - must not reference named benchmark games

### Test to add
Search the submission tree for public game IDs and game-specific mechanic filenames.

---

## Rule 4: no replay-assisted scored solving

### Remove from submission path
Any use of:
- prior recordings of the same public environments
- trace-based behavior cloning on public tasks
- visual caps used as retrieval keys for those tasks

### Replace with
Replay use only for:
- debugging the submission agent after a scored run
- research analysis in the research repo

### Submission policy
During scored runs, the agent may only use:
- live API observations
- internal generic prior knowledge
- within-run memory generated from the current environment

---

## Rule 5: one competition-native runner

### Build a single runner
Create `competition_runner.py` that:
- sets `OperationMode.COMPETITION`
- opens one scorecard
- interacts with each environment once
- never requests in-flight score
- logs only submission-safe metadata

### Add hard fail conditions
The runner should abort if:
- local environment source files are present in the working path and accessed
- game reset is attempted
- any module requests known public game IDs for branching

### Suggested implementation guardrails
- no import path to `environment_files/`
- no dependency on `knowledge/`
- no dependency on research captures

---

## What to do with the current `knowledge/` tree

Split it into two buckets.

## Bucket A: keep only if generalized
Allowed in submission if rewritten as benchmark-agnostic abstractions:
- “objects can be color-coded affordances”
- “hazards may be dynamic and periodic”
- “success often requires subgoal sequencing”
- “pathfinding may need latent-state reasoning beyond shortest path”

## Bucket B: research only
Keep out of submission if it contains:
- any public game IDs
- screenshots or descriptions linked to exact public tasks
- mechanic notes specific to named games
- solver notes tied to exact level structures

Recommendation: physically split into:
- `knowledge_general/`
- `knowledge_public25/`

Only the first may ever be imported by the submission package.

---

## What to do with the current `experiments/` tree

This is likely the highest-risk area.

### Likely current role
From the README, `arc-agi-3/experiments/` appears to contain:
- 25 game solvers
- capture infrastructure
- submit infrastructure
- perception/world model code mixed with task-specific logic

### Refactor approach
Create three slices:

1. **`research_solvers/`**
   - all per-game solvers live here
   - never imported by submission code

2. **`submission_core/`**
   - generic perception
   - generic hypothesis updates
   - generic planner
   - generic action selector

3. **`submission_runner/`**
   - pure competition-mode wrapper

### Hard rule
No file from `research_solvers/` may be imported by `submission_core/` or `submission_runner/`.

---

## Minimal viable compliant architecture

If the submission package is going to be credible, it should probably look like this:

### Perception
- parse frame into grid / entities / motion deltas
- identify candidate object classes without game labels
- maintain uncertainty rather than forcing early ontology lock-in

### Mechanics induction
Infer hypotheses such as:
- controllable avatar candidate
- blocked vs traversable tiles
- movable vs static objects
- lethal vs neutral contact
- toggleable state transitions
- target completion signals

### Planning
Use one generic planning stack:
- shallow exploration early
- branch ranking by information gain
- macro-action discovery when repeated patterns emerge
- exploit once mechanics confidence crosses threshold

### Memory
- episodic memory for current environment
- cross-level abstraction only if inferred during current environment
- no named-game retrieval

### Reset policy
Use level reset only when:
- the information gain of continued exploration collapses
- current policy has entered low-value loops
- benchmark rules allow level reset without invalidating the run

---

## What not to optimize for

Do **not** try to preserve the exact 84.9 / 90.5 pipeline under a new label.

That will produce an ambiguous submission that still smells benchmark-specific.

The compliant version should optimize for:
- clean rules boundary
- inspectability
- single-agent narrative
- generic adaptation story

Even if the score drops sharply, it gives you a second result class they cannot dismiss for the same reason.

---

## Recommended new top-level docs

## `README.md`
Keep it short and operational:
- what the agent is
- how it runs
- what it does not use
- how to reproduce a scorecard

## `COMPLIANCE.md`
State explicitly:
- no source access during scored runs
- no per-game solvers
- no game-ID keyed logic
- no public-set replay retrieval
- competition-mode only

## `ARCHITECTURE.md`
Explain the generic loop:
- perceive
- hypothesize
- plan
- act
- revise

## `LIMITATIONS.md`
Be direct:
- this version deliberately forgoes benchmark-specific optimizations
- score may be lower than research track
- purpose is protocol cleanliness, not peak public-set score

---

## Suggested release strategy

### Release 1: freeze research repo
Tag the current repo as something like:
- `research-public25-v1`

This preserves the real historical record.

### Release 2: open submission repo
Start a new repo or branch with only the compliant package.

### Release 3: publish a comparison note
A short markdown file comparing:
- source-aware benchmark-cracking track
- source-blind general-agent track

This is strategically strong because it makes the distinction explicit instead of letting organizers imply one for you.

---

## Practical first-pass task list

## Phase A: isolate contamination
1. Create `submission/` and `research/` roots.
2. Move `environment_files/` under `research/`.
3. Move public-game mechanic notes under `research/knowledge_public25/`.
4. Move per-game solvers under `research/research_solvers/`.
5. Remove any imports from submission code into those trees.

## Phase B: make the runner clean
6. Build `submission/competition_runner.py` around `OperationMode.COMPETITION`.
7. Ensure one scorecard, one `make` per environment, no in-flight scoring.
8. Add tests to fail on source access or game-ID routing.

## Phase C: rebuild generic agent loop
9. Extract generic perception code from existing solvers.
10. Extract generic search/planner logic from existing solvers.
11. Replace per-game heuristics with hypothesis-scored generic heuristics.
12. Limit memory to within-run plus benchmark-agnostic abstractions.

## Phase D: make review easy
13. Write `COMPLIANCE.md`.
14. Add grep-based CI checks for forbidden strings and forbidden imports.
15. Produce a fresh scorecard from the clean runner.

---

## Suggested CI guardrails

Add a CI job that fails if any of the following appear in the submission tree:
- known public game IDs
- imports from `research/`
- imports from `environment_files`
- imports from benchmark-specific knowledge stores
- filesystem reads outside allowed runtime directories

Also add a test that monkeypatches file access and fails if scored code tries to open local engine sources.

---

## What success looks like

A reviewer should be able to inspect the clean submission and conclude:

- this is a single agent, not a portfolio of 25 handcrafted solvers
- this agent does not inspect the benchmark source during scored execution
- this agent adapts online using a generic loop
- whatever score it gets, it got under a defensible protocol boundary

That is the real win condition for compliance.

---

## Bottom line

The current ARC-SAGE repo is strongest as a **research artifact** and weakest as a **protocol-clean ARC submission**.

Trying to blur that line is strategically weak.

The strongest move is:
- preserve the current repo as the honest record of what you built
- create a second, visibly cleaner submission package
- make the separation so explicit that ARC cannot quietly redefine your work for you

If they still reject the clean package, the disagreement becomes about principles, not about ambiguity in your codebase.

---

## Source notes

This plan is based on:
- ARC docs describing ARC-AGI-3 as measuring generalization in novel, unseen environments
- ARC Competition Mode docs requiring API interaction, one scorecard, one `make` per environment, and no in-flight score access
- ARC docs describing where official recordings come from
- ARC-SAGE public README statements describing per-game source reading, per-game world models, and 25 solvers
