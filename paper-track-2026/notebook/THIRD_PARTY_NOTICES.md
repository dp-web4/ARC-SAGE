# Third-party notices: the scored notebook

These notices cover `arc-agi-3-lean-capnudge-dprime-identity.ipynb` and the files in `extracted/`.

They record what we found, read-only, on 2026-10-06 and 2026-11-03. They are not legal clearance. The licence findings come from dp-web4/dev-SAGE (private), `paper/arc3-paper-track-2026/evidence/licenses/LICENSE_FINDINGS.md` on branch `thor/qwen-substrate`.

## Components in this notebook

### 1. Tufa Labs, Duck harness (Jeroen Cottaar and Tufa Labs)
- **Upstream:** https://github.com/Tufalabs/duck-harness, commit `7652836`. The notebook does not contain the Duck source. It applies patches to the Duck source bundle attached as a Kaggle dataset (`dfranzen/taaf-kaggle-source-bundle-copy`, "an unchanged copy of Tufa Labs' original bundle").
- **Licence:** **none stated in a LICENSE file.**
  - GitHub reports `license: null`, and the tree has no LICENSE, COPYING or NOTICE file (rechecked 2026-11-03).
  - `ARC3-Inference/pyproject.toml` declares the classifier `License :: OSI Approved :: MIT License`.
  - `tufa-arc-agi-framework/pyproject.toml` declares no licence.
- **What we redistribute:** only diffs against these files, as context lines in `extracted/harness-changes.patch` and the `extracted/arm_*.patch` files. We treat the Duck-derived lines as MIT, on the strength of that classifier. That is our reading; Tufa Labs has not confirmed it.

### 2. Daniel Franzen, ARC-AGI-3 Milestone 2 solution
- **Upstream:**
  - Kaggle notebook: https://www.kaggle.com/code/dfranzen/arc-agi-3-milestone-2-solution (v3). Public Kaggle notebooks default to Apache-2.0.
  - Write-up: https://www.kaggle.com/writeups/dfranzen/arc-agi-3-milestone-2
  - Repository: https://github.com/da-fr/arc-agi-3-solution
  - A mirror of his solution, https://github.com/tonghuikang/daniel-franzen-arc-agi-3, reports **Apache-2.0** through the GitHub API.
- **What we redistribute:**
  - Franzen's harness patch over Duck, verbatim (notebook cell 2, `extracted/harness-changes.patch`).
  - His notebook structure: the setup, serving, benchmark and diagnostics cells, plus his "About this notebook" text in cell 0.
  - Our changes to those cells are marked with `thor-claude` comments.
- **Licence:** Apache License 2.0. The full text is in `LICENSE-APACHE-2.0.txt` in this directory.
  - Apache-2.0 §4 requires a copy of the licence, prominent notices on changed files, and retained attribution notices. This file and the `thor-claude` markers inside the notebook serve as those notices.
- **Credit:** Daniel Franzen. His notebook credits Jeroen Cottaar and Tufa Labs. Its serving stack credits John Pezzulli (Pennyroyal SGLang fork), Mamy Ratsimbazafy and Gabriel Olympie (SGLang patches), and Albucino (MTP draft checkpoint).

### 3. shiiin9 / Affectify: D′ slot-priority scheduler
- **Upstream:** the public Kaggle notebook `shiiin9/affectify-arc-31-54-in-a-single-sub`, cell 21 (`_FP_SOURCE`). The same module appears in `amatlas/dfranzen-fork-d-prime`.
- **What we redistribute:** that module, vendored verbatim, with one change: a call counter, on lines marked `thor-claude`. It is notebook cell 13, `extracted/ours_form_priority.py`. Its header records the sha256 of the original bytes and keeps the original docstring and attribution unchanged.
- **Licence:** Apache-2.0, the Kaggle default for public notebooks. We found no other licence statement.

### 4. SGLang (Pennyroyal fork, John Pezzulli)
- **Upstream:** https://github.com/jpezzulli/sglang-rtxpro6000, v2.5.3. GitHub reports **Apache-2.0**. It is used as the Kaggle dataset `dfranzen/pennyroyal-v253` ("Bundled packages retain their respective upstream licenses").
- **What we redistribute:** nothing. The notebook installs it at run time from the attached dataset.

### 5. Model weights: Qwen3.8-Flash-Next (W4A16 AutoRound, Intel) and MTP drafter (Albucino)
- **Used as:** Kaggle model sources `dfranzen/intel-qwen3.8-flash-next-w4a16-autoround` and `dfranzen/albucino-qwen3-8-flash-next-drafter` (see `kernel-metadata.json`).
- **What we redistribute:** **nothing.** The weights are referenced only, and no weights are in this repository.
- **Licence:** Qwen Community License 1.0 ("remains subject to the original"). The Paper Track rules exempt pretrained models with an incompatible licence from the open-source grant (`../evidence/rules/rules.md` §2.5.a.3).

### 6. ARC Prize runtime and games
- The notebook installs `arc-agi` from the competition's offline wheelhouse and plays the competition games through the Kaggle gateway.
- No game files are in this directory.
- The practice rules in `extracted/ours_identity_seed.json` are our own one-line descriptions of the **25 public** ARC-AGI-3 games.

## Our additions
These are the files and cells marked `thor-claude`, `thor-codex` or `kimi-code`:
- `extracted/ours_*.py`, `extracted/ours_identity_seed.json`, and the `extracted/arm_*.patch` files;
- the install cells in the notebook (sections 6 and 7);
- the change notes in cell 0.

**Licence for our additions:**
- They are licensed under **CC-BY-4.0** (`../LICENSE`), as the Paper Track requires of a winner's submission and source code (`../evidence/rules/rules.md` §1.6, §2.5.a.1).
- That licence covers only what we wrote. It does not change the licences of the third-party components above, which keep their own terms.
- Known gap, stated rather than hidden: Duck has no LICENSE file (only an MIT classifier), so the right to sublicense the Duck-derived lines rests on that classifier and on Franzen's public Apache-2.0 notebook, not on an explicit upstream licence.
