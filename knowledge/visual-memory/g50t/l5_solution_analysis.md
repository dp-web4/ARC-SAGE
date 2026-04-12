# g50t L5 Solution Analysis

## Level Layout
```
     1    7   13   19   25   31   37   43   49   55
 7  M3    .    .   M2    .   O1    .   O0    .    .
13                                                .
19                                                .
25  O3    .    .   O2        M1    .   M0
31   .              .                   .    .    S
37   .         .    .    .    .    .    .         .
43   .                        .                   .
49   .        M4             O4    .    G         .
55   .    .    .
```

Player starts at (55,31). Goal at (43,49). 3 phases. 5 obstacles, 5 modifiers. 1 ghost at (55,19).

## Key Mechanics
- Upper row (y=7) is DISCONNECTED from the lower grid (no vertical path between them)
- Ghost patrols the upper-right area: (55,19)-(55,7)-(49,7) oscillation
- Obstacles 0,1 block row 7 at (43,7) and (31,7) - ghost can't pass
- Mods 0,1 at (43,25) and (31,25) control obs 0,1 (non-toggle: active while held)
- Mods 2,3 at (19,7) and (1,7) control obs 2,3 (toggle: stays shifted)
- Obs 2,3 at (19,25) and (1,25) block row 25 access to left corridor
- Mod 4 at (13,49) controls obs 4 at (31,49) (toggle: stays shifted)

## Solution Strategy (49 actions)

**Phase 0 (3 moves + PHASE):** LLU
- Player walks to mod[0] at (43,25)

**Phase 1 (5 moves + PHASE):** LLULL  
- Player walks to mod[1] at (31,25)

**Phase 2 (39 moves):** LLDLLLLUULLLDDDDDRRUDLLUUUUURRRDDRRDDRR
1. **Steps 0-7:** Navigate to (19,31) via LLDLLLLU
2. **Steps 3,5:** Clones 0,1 reach mods 0,1, clearing obs 0,1 in row 7
3. **Step 8:** Ghost reaches mod[2] at (19,7), toggling obs[2] ON - row 25 opens
4. **Steps 8-11:** Navigate through row 25: U(19,25) L(13,25) L(7,25) L(1,25)
5. **Step 11:** Ghost reaches mod[3] at (1,7), toggling obs[3] ON - left corridor opens
6. **Steps 12-19:** Navigate down left corridor to mod[4] at (13,49)
7. **Step 19:** Stepping on mod[4] toggles obs[4] ON - (31,49) cleared
8. **Steps 20-30:** Return through left corridor and row 25 to main grid
9. **Steps 30-40:** Navigate through main grid to (31,43)
10. **Steps 40-42:** D(31,49) R(37,49) R(43,49) = GOAL

## Critical Timing
- Ghost traverses row 7 left-right-left in ~12-step cycles
- obs[2] and obs[3] toggle each time ghost passes through mods 2,3
- Player must cross row 25 during the window when both obs are active (steps 8-13)
- On return trip, obs cycle again - player crosses during steps 30-36
