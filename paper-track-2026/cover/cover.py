"""thor-claude 11-03: Paper Track cover image from OUR scored history only (scored.json, from load.py).
Log y so each ~10x step reads as one leap; 0.00 runs sit on a floor strip; ERROR runs omitted (no score).
Writes cover.png (1120x560, 2:1) and cover_points.csv (exactly what is drawn)."""
import csv
import json
import os
import sys
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
rows = [r for r in json.load(open(os.path.join(HERE, "scored.json"))) if r["score"] is not None]
FLOOR = 0.005  # 0.00 runs drawn here, below the axis' first labelled tick
SURF, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0"
S1, HI = "#2a78d6", "#eb6834"
BEST = "57374159"
BAND = (25.77 - 3.93, 25.77 + 3.93)  # copy-stack public resubmissions, mean +- 1 SD per run

d = [datetime.fromisoformat(r["date"]) for r in rows]
y = [max(r["score"], FLOOR) for r in rows]
zero = [r["score"] == 0 for r in rows]

fig = plt.figure(figsize=(11.2, 5.6), dpi=100, facecolor=SURF)
ax = fig.add_axes([0.075, 0.13, 0.895, 0.58], facecolor=SURF)
ax.set_yscale("log")
ax.set_ylim(0.0035, 80)
ax.axhspan(*BAND, color=S1, alpha=0.08, lw=0, zorder=0)
ax.text(datetime(2026, 5, 4), BAND[0] * 0.9, "band: copied public stack, one-run spread 25.77 ± 3.93",
        color=INK2, fontsize=10, ha="left", va="top")
ax.plot(d, y, color=S1, lw=1.2, alpha=0.35, zorder=1)
ax.scatter([a for a, z in zip(d, zero) if not z], [b for b, z in zip(y, zero) if not z], s=30, color=S1,
           edgecolor=SURF, linewidth=1.5, zorder=3)
ax.scatter([a for a, z in zip(d, zero) if z], [b for b, z in zip(y, zero) if z], s=30, facecolor=SURF,
           edgecolor=S1, linewidth=1.3, zorder=3)
bi = next(i for i, r in enumerate(rows) if r["ref"] == BEST)
ax.scatter([d[bi]], [y[bi]], s=90, color=HI, edgecolor=SURF, linewidth=2, zorder=4)
ax.annotate("31.82", (d[bi], y[bi]), xytext=(-8, 10), textcoords="offset points", ha="right",
            color=INK, fontsize=12, fontweight="bold")

def note(ref, text, dx, dy, ha):
    i = next(i for i, r in enumerate(rows) if r["ref"] == ref)
    ax.annotate(text, (d[i], y[i]), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center",
                color=INK2, fontsize=10, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))

note("54948614", "five months of our own organs:\nbest 0.20", -16, 22, "right")
note("56836531", "public harness copied  1.17", -12, 8, "right")
note("56864492", "Qwen3.8  2.18", -12, 10, "right")
note("56894159", "public solver patch  24.82", -16, -4, "right")

ax.set_yticks([FLOOR, 0.01, 0.1, 1, 10, 30])
ax.set_yticklabels(["0", "0.01", "0.1", "1", "10", "30"])
ax.minorticks_off()
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.set_xlim(datetime(2026, 5, 1), datetime(2026, 11, 8))
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(MUTED)
ax.tick_params(colors=INK2, labelsize=10, length=0)
ax.grid(axis="y", color=GRID, lw=0.8)
ax.set_axisbelow(True)

TITLE = sys.argv[1] if len(sys.argv) > 1 else "Affordance Is All You Need"
fig.text(0.075, 0.90, TITLE, color=INK, fontsize=24 if len(TITLE) < 40 else 19, fontweight="bold")
fig.text(0.075, 0.82, "ARC-AGI-3: our 97 scored Kaggle runs, May–Nov 2026 (log scale; hollow = 0.00)",
         color=INK2, fontsize=12)
fig.savefig(os.path.join(HERE, sys.argv[2] if len(sys.argv) > 2 else "cover.png"), facecolor=SURF)

with open(os.path.join(HERE, "cover_points.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ref", "date", "score", "drawn_y"])
    for r, yy in zip(rows, y):
        w.writerow([r["ref"], r["date"], r["score"], yy])
print("points", len(rows), "zeros", sum(zero), "best", rows[bi]["score"], "max", max(r["score"] for r in rows))
