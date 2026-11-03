# ARC Prize 2026 Paper Track: evidence annex for "Affordance Is All You Need"

This directory is the public evidence annex for our ARC Prize 2026 **Paper Track** writeup, *Affordance Is All You Need*, the title on `cover/cover.png`. The writeup is a case study of a competition-legal local agent on ARC-AGI-3, scored on Kaggle from May to November 2026.

- **Submission ID for the Accuracy criterion:** **57374159**, Kaggle kernel `dennispalatov/arc-agi-3-lean-capnudge-dprime-identity` v3, public score **31.82**. That score is an unreplicated maximum of about 20 runs. Our last scored run, 57911309, scored 26.04.
- **Scored notebook:** `notebook/`.
- **Writeup text:** `writeup/WRITEUP_1500_cloud-claude_2026-11-03.md`, a verbatim copy. Its editor is cloud-claude. Its H1 is a working title, *Where the fluid step fails*; the submitted title is the cover's.

## How this relates to the rest of ARC-SAGE
- **Everything outside this directory** is the frozen **Phase-1** snapshot (April 2026, 94.85% on the public set with engine-source affordances; see the top-level `README.md`). This annex does not change it.
- **The work in this directory** came later. It was done in private repositories, and only the material that supports the writeup is copied here.
- **Phase 1 in the paper:** the writeup cites Phase 1 as prior work, in its §2.

## Layout
| Path | Contents |
|---|---|
| `writeup/` | The 1,500-word writeup (verbatim) and `RECEIPTS.md`, which traces every number in it to a public file here |
| `cover/` | `cover.png` and the script that draws it (`cover.py`, run from `cover/`), its input (`scored.json`: our 120 Kaggle submissions, 97 with a score) and its output table (`cover_points.csv`) |
| `notebook/` | The scored notebook, its Kaggle metadata, its `%%writefile` cells as files (`extracted/`), `THIRD_PARTY_NOTICES.md` and the Apache-2.0 text |
| `analysis/` | The three-leaps analysis (our harness vs Duck vs Franzen), redacted where marked |
| `evidence/rules/` | The Paper Track's Kaggle pages, archived verbatim on 2026-11-03 through the Kaggle API (`fetch_rules.py`) |
| `evidence/excerpts/` | Line-numbered quotes of the private decision records, run log, results notes and forum posts that the writeup cites |
| `evidence/NOTEBOOK_LICENCE_RECOMMENDATION.md` | Our reading of the rules on licences and the submission ID |
| `MANIFEST.md` | Every file: its source repository, commit, path and any change |

## Claim → evidence map (summary; full table in `writeup/RECEIPTS.md`)
| Writeup claim | Where to check it |
|---|---|
| Score history 0.08–0.20 → 1.17 → 2.18 → 24.82 → 31.82; final 26.04 | `cover/scored.json` (public Kaggle scores, by submission ref) |
| Copy band 25.77 ± 3.93; 31.82 unreplicated | `evidence/excerpts/DECISIONS.md`, `evidence/excerpts/COMPETITION_RUN_LOG.md` |
| Attribution table (model swap 1.46 vs 0.86; 108 → 330 tok/s; port without lift; 32k vs 128k; ≈1.2× at matched tokens) | `evidence/excerpts/SUBSTRATE_AB_2026-09-19.md`, `DECISIONS.md`, `FORUM_*` excerpts |
| ~27k vs ~4.5k decision-path lines; 49–109 executor actions; proxy reversal | `analysis/ARC_HARNESS_AB_THREE_LEAPS_2026-11-02.md` §2, `evidence/excerpts/DECISIONS.md` |
| Failure modes (turn opener lost 19–37%; clock line 9 → 37; instruments failing toward the hypothesis) | `evidence/excerpts/DECISIONS.md`, `DRAFT_v1.md`, `SUBSTRATE_AB_2026-09-19.md` |
| Registered interventions (19.22, 24.89, 16.06, 18.14, 9.62, 11.48; `plan_check` 0/160) | `cover/scored.json`, `evidence/excerpts/COMPETITION_RUN_LOG.md`, `DRAFT_v1.md` |
| Time converts depth (13/18); token curve; su15 20/24; goal taxonomy 6/1/0 | `evidence/excerpts/DRAFT_v1.md`, `FORUM_thor-claude-budget-axis-…` |
| What the scored notebook does | `notebook/README.md`, `notebook/arc-agi-3-lean-capnudge-dprime-identity.ipynb` cell 0 |

**Where the underlying data is private.** Some claims rest on transcripts or run directories that are not published here. `writeup/RECEIPTS.md` marks each of these **evidence private** rather than leaving it out.

## Licences (WORDING PENDING dp REVIEW)
- **Our own material in this directory:** MIT-0, like the rest of this repository (`../LICENSE`). For the ARC Prize 2026 Paper Track, it is also offered under **CC-BY-4.0**, the licence the track's winners grant (`evidence/rules/rules.md` §1.6, §2.5).
- **Third-party components of the notebook:** they keep their own licences; see `notebook/THIRD_PARTY_NOTICES.md`.
- **The Kaggle rule pages:** they are Kaggle's text, archived as evidence.

## Not included
- **The long-form draft (`DRAFT_v1`, ~10k words):** left out. It cites about 50 private paths, and it predates the final score. Its cited passages are quoted in `evidence/excerpts/DRAFT_v1.md`.
- **Model weights, ARC game files, and any material from other projects:** not included.
