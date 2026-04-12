# g50t L6 Analysis (SOLVED — 69 actions, 2026-04-12)

## Solution (69 actions, 3 phases)
```
Phase 0 (16): D U D U D U L L R R D D R L U U   + UNDO
Phase 1 (24): D D L R U U D D U U D D R R U U U U L U U R R R   + UNDO
Phase 2 (27): D D R R U U U U R R D D D D U D U D U D U D U D L L L
```

Key insight — the prior agent's blocker assumption ("no clone available to hold mod[3]") was wrong.
Phase 0's purpose is NOT to build a clone that parks somewhere immediately useful;
its purpose is to build a clone whose REPLAY, driven by Phase 2's move cadence,
reaches portal pad (13,25) at exactly the right step so it gets teleported to (13,13)
by the left portal swap (which fires when the wild ghost reaches mod[0] at (1,25)),
then walks UU to mod[3] at (13,1) — and parks there for the rest of Phase 2 holding
obs[0] open. So ghost0 IS the mod[3] holder. The "3 phases consumed" framing missed
that Phase 0's clone can be repurposed via portal teleport during Phase 2 replay.

Chain of events during Phase 2 playback:
1. Player walks to portal pad (49,37); ghost0 replay walks to portal pad (13,25).
2. Ghost1 (Phase 1 replay) hits mod[2] toggling obs[1] off.
3. Wild ghost patrols up through now-open (1,37), reaches mod[0] at (1,25).
4. Mod[0] fires left portal swap (13,13)↔(13,25) — ghost0 teleports to (13,13).
5. Ghost0 walks UU to mod[3] at (13,1), holding obs[0] open at (31,1).
6. Ghost1 walks through now-open (31,1), reaches mod[1] at (49,1).
7. Mod[1] fires right portal swap (49,37)↔(49,49) — player teleports to (49,49).
8. Player walks LLL to goal at (31,49).

Phase 2 has a UDUDUDUD pacing segment because player must wait for ghost1 to reach mod[1]
before stepping onto the portal pad — the swap must fire after player arrives, not before.

---

# g50t L6 Analysis (ORIGINAL — blocker was incorrect)

## Level Layout
```
     1    7   13   19   25   31   37   43   49
 1            M3             O0    .    .   M1
 7             .              .
13            M4         .    .    .    .    .
19                                 .         .
25  M0        M5    .    S         .         .
31   .                   .         .         .
37  O1             M2    .    .    .        M6
43   .              .
49   .                        G    .    .   M7
55   .    .    .    E
```

Player starts at (25,25). Goal at (31,49). 3 phases. 2 obstacles, 8 modifiers. 1 ghost at (19,55).

## Entity Types
- **obs[0]** at (31,1): NON-toggle gate, shifts LEFT. Controlled by mod[3] at (13,1).
- **obs[1]** at (1,37): TOGGLE gate, shifts RIGHT. Controlled by mod[2] at (19,37).
- **mod[0]** at (1,25): Relay -> triggers portal swap (13,25)-(13,13)
- **mod[1]** at (49,1): Relay -> triggers portal swap (49,37)-(49,49)
- **mod[2]** at (19,37): Relay -> controls obs[1]
- **mod[3]** at (13,1): Relay -> controls obs[0]
- **mod[4-7]** at (13,13), (13,25), (49,37), (49,49): Portal pads (ulhhdeoyok)
  - Pair 1: (13,13) and (13,25) - swap triggered by mod[0] at (1,25)
  - Pair 2: (49,37) and (49,49) - swap triggered by mod[1] at (49,1)

## Ghost Behavior
- Starts at (19,55), patrols bottom-left: (19,55)-(1,55)-(1,43) bounce
- Blocked by obs[1] at (1,37) - can't go higher
- With obs[1] cleared: ghost can reach (1,25)=mod[0] triggering portal swap

## Discovered Strategy (Partially Working)
1. Phase 0: LL (go to portal pad at (13,25))
2. Phase 1: DDRRUUDDLLL (11-step detour path to mod[2] at (19,37))
3. Phase 2:
   - Clone 0 reaches (13,25) at step 2
   - Clone 1 reaches mod[2] at step 11, toggling obs[1] OFF
   - Until step 11: obs[1] is ON (from phase transition)
   - Ghost reaches (1,25)=mod[0] at step 8, triggering swap
   - Player (at (13,25)) gets swapped to (13,13)
   - Player goes UU to (13,1)=mod[3], activating obs[0] for ONE step
   - obs[0] deactivates when player steps off mod[3]

## Blocker
obs[0] at (31,1) is NON-toggle: only active while someone stands on mod[3] at (13,1).
All 3 phases are consumed before reaching mod[3]. No clone available to hold it.

Path to goal requires: (31,1) cleared -> (31,7) U -> (31,1) R -> (37,1) R -> (43,1) R -> (49,1)=mod[1] -> triggers second swap (49,37)-(49,49) -> player at (49,49) -> LLL -> goal.

## Possible Approaches (Untried)
1. Find a way to reach (49,1) WITHOUT clearing obs[0]
2. Use the ghost to hold mod[3] (requires ghost reaching (13,1) - currently impossible)
3. Different phase structure that leaves a clone at mod[3]
4. Check if obs[0] can be bypassed with a different gate direction
5. Check if there's a direct path to (49,49) or (31,49) not discovered yet
