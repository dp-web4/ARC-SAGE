# Public notebook and licence: recommendation (thor-claude, 2026-11-03)

Source: the Paper Track pages archived verbatim today in `evidence/rules/` (fetched read-only through the Kaggle API, `fetch_rules.py`). This updates codex's 10-06 `LICENSE_AUDIT.md` and corrects two lines of `OUTLINE.md`. It is evidence and a recommendation, not legal clearance.

## What the rules actually say
1. **Deadline: 2026-11-09 23:59 UTC** (`Timeline.md`). The ARC site's "11-08" is not the binding rule text. Keep 11-08 as our target, since ties go to the earlier entry.
2. **Winner licence: CC-BY 4.0** (`rules.md` §1.6 and §2.5), not "CC0 / MIT-0" as OUTLINE.md says. A winner licenses "your winning Submission and the source code used to generate the Submission" under CC-BY-4.0, and must "represent that you have the unrestricted right to grant that license" (§2.8.a.2).
3. **Exemptions** (§2.5.a.2–3):
   - commercially available software you don't own needs no licence grant;
   - "input data or pretrained models with an incompatible license" need no open-source grant.

   So the Qwen Community License weights (Intel AutoRound, Albucino drafter) are covered by the model exemption.
4. **The notebook is our scored notebook** (`Submission_Requirements.md`): "If you use a private Kaggle Notebook, it will automatically be made public after the deadline." Accuracy is matched by submission ID to that notebook, so no separate public derivative has to be built. The kernel we attach becomes public.

## Remaining risk: the Duck-derived code
- Tufalabs/duck-harness: GitHub `license: null` and no LICENSE file, rechecked 11-03 (last push 07-01). Only `ARC3-Inference/pyproject.toml` declares the classifier "MIT".
- Our notebooks contain Franzen's patch over Duck (copied from his PUBLIC Kaggle notebook, 1,197 votes; his GitHub mirror is Apache-2.0) plus our additions.
- Our additions are ours to license CC-BY. For the Duck-derived lines, "unrestricted right" is not established by a classifier alone.
- Mitigation: every ARC-AGI-3 Milestone 2 prize winner shipped the same bundle publicly. That suggests the sponsor accepts it, but it is inferred, not verified.

## Recommendation (dp decides the external parts)
1. **Attach the scored notebook behind the chosen submission ID.** Make it public when we submit, so judges can open it before the deadline rather than finding it private.
2. **Add a header cell:**
   - our additions are CC-BY-4.0;
   - third-party components are named with their licences (Duck: MIT per its pyproject, no licence text; Franzen: Apache-2.0 mirror; Qwen weights: Qwen Community License 1.0, exempt under §2.5.a.3; SGLang fork: Apache-2.0);
   - attribution to Tufa Labs and Daniel Franzen.
3. **Optional external act, dp's call:** a one-line request to Tufa Labs to add a LICENSE file matching the MIT classifier. A paper prize does not require it, because the obligation only bites if we win. A short note covers it then.
4. **Submission ID: 57374159 (dp, 11-03).** IDENTITY stack, public 31.82, submitted 2026-10-19 00:12Z from `dennispalatov/arc-agi-3-lean-capnudge-dprime-identity` **v3**. That kernel's last run (10-18 20:26Z) predates the submit, so v3 should still be the newest version, which is the one the public page shows. Before attaching, re-check that no later version exists.
   - The writeup must describe THIS notebook's contents: Frame3 + run identity + 25 practice rules + run journal. It is not the 11-02 final composite (57911309, 26.04).
   - It must carry codex #4's caveat that 31.82 is an unreplicated maximum of ~20 runs.
   - dp to confirm 57374159 is among the selected finals in the ARC-AGI-3 UI.

## Corrections to carry
- OUTLINE.md "CC0 / MIT-0" → CC-BY 4.0.
- OUTLINE.md / year-analysis "11-08 or 11-09" → rules say 11-09 23:59 UTC.
