# The scored notebook (submission 57374159, public score 31.82)

`arc-agi-3-lean-capnudge-dprime-identity.ipynb` is the source of Kaggle kernel `dennispalatov/arc-agi-3-lean-capnudge-dprime-identity`, **version 3**. It was submitted to ARC Prize 2026 (ARC-AGI-3) on 2026-10-19 00:12 UTC as submission **57374159**, which scored **31.82** on the public field. That is the submission ID named in the Paper Track writeup.

## Provenance
- **Source:** dp-web4/dev-SAGE (private) commit `86e55c04e` (2026-10-18 13:26:34 PDT = 20:26:34 UTC), file `kaggle/qwen/franzen_lean_capnudge_dprime_identity/arc-agi-3-lean-capnudge-dprime-identity.ipynb`, with the provenance-path redaction described below.
- **Binding to kernel v3:**
  - Our promoter log records "Kernel version 3 successfully pushed" at 2026-10-18 20:26:56 UTC, 22 s after that commit.
  - The submission at 00:11 UTC on 10-19 names "v3".
  - The run log row for 57374159 names commit `86e55c04e` (`../evidence/excerpts/COMPETITION_RUN_LOG.md`, line 51).
  - We have not byte-compared this file with Kaggle's stored copy of v3. Kaggle makes the kernel public after the competition deadline, so the two can be compared then.
- **Settings file:** `kernel-metadata.json` is the push metadata from the same commit. `is_private: true` was its state at push time.

## What the notebook does
**Base: Daniel Franzen's public Milestone-2 solution.** It is the Duck harness plus Franzen's patch, running Qwen3.8-Flash-Next W4A16 with an MTP drafter on SGLang. Cell 0 keeps his description.

**Our changes, stacked on that base:**
1. Nine harness patches (`extracted/arm_*.patch`), applied in cell 21.
   - Switched on in the scored path: level memory, the prior card on a stall trigger (once per level at ≥50 actions), a hazard line, the board-dump guard, a per-action log, and the cut-off nudge.
   - Applied but switched off: the code for verification, `plan_check` and `plan_search`.
2. The D′ slot-priority scheduler from shiiin9/Affectify (cell 32, `extracted/ours_form_priority.py`).
3. A score-rule and hypothesis-class line (`extracted/ours_score_rule.py`).
4. The frame stack:
   - a roles-are-hypotheses line (`ours_frame.py`);
   - a required `Frame:` line at each level start (`ours_frame_levelstart.py`);
   - a required frame revision at the stall card (`ours_frame_revise.py`).
5. **IDENTITY**, new in this version (`ours_identity.py`, seed `ours_identity_seed.json`):
   - a run identity heading every game's system prompt;
   - 25 practice rules from our non-scored runs on the public games;
   - a run journal of Rule/Method lines shared across the games of the run.

Cell 0 lists each step with its date.

## `extracted/`
- **What it is:** each `%%writefile /kaggle/<name>` cell of the notebook, written out as `<name>` with its body unchanged. It is a convenience for reading diffs and modules outside Jupyter.
- **Which copy is authoritative:** the notebook. `../MANIFEST.md` lists the cell each file came from.

## Licences
See `THIRD_PARTY_NOTICES.md`. Franzen's code is Apache-2.0 (`LICENSE-APACHE-2.0.txt`). Duck states MIT in a classifier but has no LICENSE file. The Qwen weights are referenced only, not redistributed.

## One redaction
- `ours_identity_seed.json` (cell 19, and `extracted/ours_identity_seed.json`) carries a `source.corpus` field. In the scored notebook it held the absolute path, on our workstation, of the private analysis file the seed was built from. Here the workstation prefix is replaced by `[local path redacted]`; the file name and the corpus sha256 in the same field are unchanged.
- This is the only intended redaction from the private source copy. The field is provenance metadata: the agent's prompts never contain it (the seed's rules and roles are read; `source` is not), so the redaction does not change what was played. As noted above, the published file has not been byte-compared with Kaggle's stored v3.
