# ARC Prize 2026 Paper Track: evidence annex for "Affordance Is All You Need"

This directory is the evidence annex for our ARC Prize 2026 **Paper Track** draft, *Affordance Is All You Need*. It discusses the April Phase-1 public-set run with engine-source access, and later local-agent submissions on the Kaggle competition field. These are different settings and are not a controlled comparison.

- **Submission ID for the Accuracy criterion:** **57374159**, Kaggle kernel `dennispalatov/arc-agi-3-lean-capnudge-dprime-identity` v3, public score **31.82**. That score is an unreplicated maximum of about 20 runs. Our last scored run, 57911309, scored 26.04.
- **Scored notebook:** `notebook/`.
- **Writeup text:** `writeup/WRITEUP_rev4.1_2026-11-05.md` is the approved submission text; submission is not asserted here. The earlier writeup is retained as historical context. See provenance in `MANIFEST.md` and qualifications in `writeup/RECEIPTS.md`.

## How this relates to the rest of ARC-SAGE
- **Everything outside this directory** is the frozen **Phase-1** snapshot (April 2026, 94.85% on the public set with engine-source affordances; see the top-level `README.md`). This annex does not change it.
- **The work in this directory** came later. It was done in private repositories, and only the material that supports the writeup is copied here.
- **Phase 1 in the paper:** the writeup discusses its source-access and replay conditions in §1; the score is not a blind first-exposure result.

## Layout
| Path | Contents |
|---|---|
| `writeup/` | The draft writeup and `RECEIPTS.md`, which maps claims to public evidence or identifies private underlying records |
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
| Score history 0.08–0.20 → 1.17 → 2.18 → 24.82 → 31.82 | `cover/scored.json` (our copy of Kaggle public scores, by submission ref) |
| Copy band 25.77 ± 3.93; 31.82 unreplicated | `evidence/excerpts/DECISIONS.md`, `evidence/excerpts/COMPETITION_RUN_LOG.md` |
| Phase-1 score and conditions | `../README.md`, its linked scorecard, `../paper/ARC-SAGE-AGI-84-9.md`, and the community-leaderboard PR linked in `writeup/RECEIPTS.md` |
| 149/204 goal proposals unbound; 49–109 executor actions | `evidence/excerpts/PRIORS_BEFORE_OUTSIDE_ZAP_2026-09-06.md`, `evidence/excerpts/DECISIONS.md` |
| Registered interventions (19.22, 24.89, 16.06, 18.14, 9.62, 11.48; `plan_check` 0/160) | `cover/scored.json`, `evidence/excerpts/COMPETITION_RUN_LOG.md`, `DRAFT_v1.md` |
| Non-randomized time panel (13/18); retrospective token curve | `evidence/excerpts/DRAFT_v1.md`, `FORUM_thor-claude-budget-axis-…` |
| What the scored notebook does | `notebook/README.md`, `notebook/arc-agi-3-lean-capnudge-dprime-identity.ipynb` cell 0 |

**Where the underlying data is private.** Some claims rest on transcripts or run directories that are not published here. `writeup/RECEIPTS.md` marks each of these **evidence private** rather than leaving it out.

## Licences
- **Our own material in this directory is CC-BY-4.0** (`LICENSE`, full text). That is the licence the Paper Track requires of a winning submission and the source code used to generate it (`evidence/rules/rules.md` §1.6, §2.5.a.1). The rest of this repository stays MIT-0 (`../LICENSE`).
- **Third-party components of the notebook:** they keep their own licences; see `notebook/THIRD_PARTY_NOTICES.md`.
- **The Kaggle rule pages:** they are Kaggle's text, archived as evidence.

## Not included
- **The long-form draft (`DRAFT_v1`, ~10k words):** left out. It cites about 50 private paths, and it predates the final score. Its cited passages are quoted in `evidence/excerpts/DRAFT_v1.md`.
- **Model weights, ARC game files, and any material from other projects:** not included.
