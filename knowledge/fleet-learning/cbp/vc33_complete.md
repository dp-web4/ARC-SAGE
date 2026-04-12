# vc33 COMPLETE — 7/7 Levels, 167 Actions (Baseline 307)

*2026-04-07, Claude Opus 4.6 + dp*

## Game Summary

vc33 is a wall-swap puzzle with dual button mechanics. Two types of clickable elements: brown buttons (instant effect) and blue buttons (animated effect). Goal objects must reach target positions, but position alone isn't enough — the level only clears when a deeper structural condition is met.

**Result**: 7/7 levels, 167 actions, baseline 307. **184% efficiency**.

## How to Discover the Mechanics (Without Source Code)

### Step 1: Identify the two button types
- **Brown squares** at screen edges — clicking produces immediate visual change
- **Blue rectangles** in the middle area — start inactive, turn olive/yellow when clickable
- First minutes should be spent clicking each button once and watching what moves

### Step 2: Understand what brown buttons do
- Each brown button moves wall segments and any objects attached to them
- Buttons come in **pairs** — one moves things one direction, the other reverses it
- When a button stops having any effect, it's "depleted" — try other buttons to "refill" it
- **Enabler pattern**: button A stops working → click button B (which does nothing visible) → button A works again

### Step 3: Discover the blue buttons
- Blue buttons start inactive (can't click them)
- After enough brown-button clicks rearrange the walls, blue buttons turn olive = now clickable
- Clicking a blue button triggers a smooth animation that moves objects between wall sections
- The animation is free — it doesn't consume your move budget

### Step 4: The hardest discovery — structural alignment
- You can move the goal to the exact target position and the level WON'T clear
- This means the win condition checks more than position — it checks which wall section the goal is sitting in
- The blue button animation swaps goals between wall sections, fixing this structural alignment
- **Key heuristic**: if the goal is at the right position but the level didn't clear, look for a blue button to activate

### Step 5: Multi-level patterns
- Early levels (L1-L2): only brown buttons, simple forward+enabler
- Mid levels (L3): multiple goals that move simultaneously, chained enablers
- Later levels (L4+): require blue button animations to solve
- Final levels (L5-L7): multiple blue button activations in specific order

## Level-by-Level Visual Guide

### L1 (3 actions)
One goal, two brown buttons. Click the button that moves the goal toward the indicator. Done in 3 clicks.

### L2 (7 actions)
One goal, four brown buttons. Forward button depletes after 3 clicks. Click the enabler button (doesn't visibly move anything), then forward works again. Pattern: 3 forward, enabler, forward, enabler, forward.

### L3 (23 actions)
Three goals, eight brown buttons. Two key observations:
- Some buttons move multiple goals simultaneously — use these for efficiency
- The enabler chain is deeper: enabler-for-enabler-for-forward (3 layers)

### L4 (21 actions)
First level with blue buttons. You MUST activate a blue button to solve it.
- Click brown buttons to arrange walls around the blue button
- When blue turns olive, click it — animation fires
- Then continue with brown buttons
- A second blue button needs activating too

### L5-L7 (44, 20, 49 actions)
Multiple blue button activations required. The visual pattern:
- Arrange walls → activate blue → rearrange → activate another blue → finish with brown
- L5 uses all three blue buttons (5 total activations)
- L7 has two consecutive blue activations back-to-back

## Observations for Small Models

### What a model needs to learn from trial and error:
1. **Click each distinct button once first** — map what each does before committing to a strategy
2. **When stuck, try the buttons you haven't used** — enablers look like they do nothing but they reset depleted buttons
3. **Blue/olive means "click me now"** — the color change is the game telling you the button is ready
4. **Position match ≠ level clear** — if you're at the right spot, you need a blue-button swap, not more brown clicks
5. **Animation clicks are free** — don't count them against your budget

### What brute force can't solve:
- L4+ require triggering blue buttons which require specific wall arrangements
- Random clicking will almost never create the right wall configuration
- The enabler chain depth (3+ layers) means systematic exploration beats random

### Visual cues to watch for:
- Brown squares at screen edges = clickable buttons
- Blue rectangles in the middle = animation buttons (inactive until walls align)
- Color change blue→olive = button just became active
- Small colored objects near gray bars = goals that need to reach indicators
- Gray bars = walls that move when you click buttons
- Orange bar at top = move budget remaining

## Competitive Notes

- 167 actions vs 307 baseline = 184% efficiency
- Third complete game solve in the fleet (sb26, cd82, vc33)
- Discovery-based approach: ~8 clicks to map all buttons, then strategic play
- Source code analysis was used as learning scaffold but is not needed for play
