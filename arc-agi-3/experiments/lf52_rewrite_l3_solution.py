#!/usr/bin/env python3
"""Rewrite the L3 entry in solutions.json with a 0-OOB reordered version.

Strategy: the current L3 cached solution has 4 OOB clicks at the very start
(world pixel x=80, 68 at offset (5,5) maps to grid col 12, 10). After jumps +
piece-on-block + RIGHT x3 push, offset shifts to (-19, 5), making those same
grid targets land at x=56, 44 (in-bounds).

So we replay steps [4..15] first (left-side work + scroll), then emit the 4
original OOB clicks recomputed for the new offset, then replay steps [16..].

Verified live on the engine: this yields L3 WIN with 0 OOB clicks.
"""
import sys, os, json

sol_path = os.path.join(os.path.dirname(__file__), '..', '..',
                        'knowledge', 'visual-memory', 'lf52', 'solutions.json')

with open(sol_path) as f:
    sols = json.load(f)

L3_original = sols[2]
print(f"Original L3: {len(L3_original)} steps")
oob_original = [(i,s) for i,s in enumerate(L3_original)
                if s.get('action')==6 and s.get('data') and
                (s['data'].get('x',0)<0 or s['data'].get('x',0)>63 or
                 s['data'].get('y',0)<0 or s['data'].get('y',0)>63)]
print(f"Original OOB count: {len(oob_original)}")

# Build reordered L3:
#   phase A: steps 4..15 unchanged (includes 3 RIGHT pushes that scroll -24 in x)
#   phase B: the 4 originally-OOB clicks, recomputed for offset (-19, 5):
#       old (80,20) -> (56,20)   (click piece grid 12,2)
#       old (68,20) -> (44,20)   (arrow LEFT-2 lands grid 10,2)
#       old (80,32) -> (56,32)   (click piece grid 12,4)
#       old (68,32) -> (44,32)   (arrow LEFT-2 lands grid 10,4)
#   phase C: steps 16..end unchanged

phase_a = L3_original[4:16]
phase_b = [
    {'action': 6, 'data': {'x': 56, 'y': 20}},
    {'action': 6, 'data': {'x': 44, 'y': 20}},
    {'action': 6, 'data': {'x': 56, 'y': 32}},
    {'action': 6, 'data': {'x': 44, 'y': 32}},
]
phase_c = L3_original[16:]

L3_reordered = phase_a + phase_b + phase_c
print(f"Reordered L3: {len(L3_reordered)} steps "
      f"(phase A={len(phase_a)}, B={len(phase_b)}, C={len(phase_c)})")

# Sanity: no OOB
oob_new = [(i,s) for i,s in enumerate(L3_reordered)
           if s.get('action')==6 and s.get('data') and
           (s['data'].get('x',0)<0 or s['data'].get('x',0)>63 or
            s['data'].get('y',0)<0 or s['data'].get('y',0)>63)]
print(f"Reordered OOB count: {len(oob_new)}")
assert len(oob_new) == 0, f"Still have OOB: {oob_new}"

sols[2] = L3_reordered

# Write back
with open(sol_path, 'w') as f:
    json.dump(sols, f, indent=2)

# Summary of all levels
for i, s in enumerate(sols):
    oob = [(j,x) for j,x in enumerate(s)
           if x.get('action')==6 and x.get('data') and
           (x['data'].get('x',0)<0 or x['data'].get('x',0)>63 or
            x['data'].get('y',0)<0 or x['data'].get('y',0)>63)]
    print(f"  L{i+1}: {len(s)} steps, {len(oob)} OOB")

print(f"\nWrote reordered solutions to {sol_path}")
