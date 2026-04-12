# Exploration Playbook — How to Approach Any ARC-AGI-3 Game

*For competition models. Step-by-step protocol for unknown games.*

## Before Your First Action

1. **Check available actions.** The action list tells you the game type:
   - `[6]` = click only → spatial puzzle, click colored regions
   - `[1,2,3,4]` = move only → maze/navigation or value cycling
   - `[1,2,3,4,6]` = move + click → hybrid, may have cursor + targets
   - `[1,2,3,4,5,6]` = move + select + click → complex interaction (stamps, programs)

2. **Scan the screen.** Identify:
   - Large colored regions (background/maze)
   - Small colored objects (interactive elements)
   - Reference images/patterns (target to match)
   - Progress bars or counters (action budget)
   - Grid patterns or repeated structures (puzzle board)

3. **Query the cartridge.** Search for this game's known mechanics and strategies.

## Click-Only Games (`[6]`)

### Discovery Protocol (5-8 actions)
1. Click the LARGEST non-background colored object. Observe pixel change count.
2. Click a DIFFERENT colored object. Compare changes.
3. Click the SAME object again. Does it toggle? Cycle? Deplete?
4. If you see a grid of similar objects, click several — does a pattern emerge?

### Classify the Mechanic
- **Toggle/cycle**: clicking rotates through states (ft09: color cycling)
- **Select + act**: first click selects, second click places/activates (r11l)
- **Program + execute**: set up a pattern, then confirm (tn36)
- **Direct effect**: each click changes the game state immediately (vc33)

### Key Heuristics
- **1px change = selection.** You toggled something, it's reversible.
- **100+ px change = action.** Something significant happened.
- **0px change = invalid target.** Try a different spot.
- If buttons seem to "stop working" after several clicks, look for an **enabler** — a different button that resets the depleted one. (vc33 pattern)

## Move-Only Games (`[1,2,3,4]`)

### Discovery Protocol (4 actions)
1. Press each direction once: UP, DOWN, LEFT, RIGHT.
2. For each, observe: did something move? How much? What direction?
3. **If cursor moved**: this is navigation. Find the path to the goal.
4. **If values changed**: this is cycling. UP/DOWN cycle values, LEFT/RIGHT navigate.

### Classify the Mechanic
- **Maze navigation**: character moves through corridors to reach an exit (tu93)
- **Value cycling**: arrows cycle symbols, cursor selects which symbol to edit (tr87)
- **Orbital navigation**: entity orbits around a ring or pattern (cd82)

### Key Heuristics
- **Check for entities that move AFTER you.** If the game has arrows, bouncers, or delayed entities, they move during your turn. Avoid their activation zones.
- **Grid alignment matters.** Many games snap to grid nodes. Movement may be in fixed increments.
- **Dead ends exist.** If you can't go back, plan the full path before committing.

## Move+Click Games (`[1,2,3,4,6]`)

### Discovery Protocol (6-10 actions)
1. Try all 4 directions first — establish if movement works.
2. Click somewhere on the game board. Did something happen?
3. Click a different location. Compare.
4. Try: move, THEN click. Does position affect what click does?

### Common Patterns
- **Spell systems**: move sets up facing direction, click activates spell (sc25)
- **Pick and place**: click to select object, move to position, click to place (sb26)
- **Navigate + stamp**: move to position, action to apply effect (cd82)

### Key Heuristics
- **Your position matters for clicks.** Many games check WHERE you are when you click.
- **Direction matters for actions.** Spells/stamps often fire in the player's facing direction.
- **Click on colored UI elements** (palette bars, toggle grids) to change modes/tools.

## When You're Stuck

1. **Have you clicked everything once?** Hidden enablers look inactive until clicked.
2. **Have you tried all directions?** Some paths only appear from certain positions.
3. **Is the obstacle removable?** Walk into enemies to damage them. Use spells/tools on barriers.
4. **Is your assumption wrong?** The most common failure is persisting with a wrong model. If 3 attempts fail, re-examine your core assumption.
5. **Look at what you're NOT seeing.** The answer is usually in what you haven't noticed, not in what you haven't tried.

## Per-Game-Type Quick Reference

| Game Type | First Action | What to Watch | Common Win |
|-----------|-------------|---------------|------------|
| Click-only | Click largest colored region | Pixel change count | All constraints satisfied |
| Move-only | Press all 4 directions | What moved, how far | Reach target or match pattern |
| Move+click | Move first, then click | Does position affect click | Navigate + interact with targets |
| Spell/program | Find the toggle grid | Pattern matching triggers | Set correct program + execute |

## Budget Management

- **Observation costs nothing.** Study the screen before acting.
- **Each action depletes budget.** Count remaining before starting a sequence.
- **Blocked moves still cost.** Moving into a wall uses an action but does nothing.
- **Animations don't cost extra.** Multi-frame responses are free — the action already counted.
- **Failed attempts teach.** A dead end that eliminates a possibility is valuable data.
