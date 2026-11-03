# Excerpt: `COMPETITION_RUN_LOG_2026-10-09.md`

- Source: dp-web4/dev-SAGE (private), `kaggle/harness/ship/COMPETITION_RUN_LOG_2026-10-09.md` at commit `162d86cd1`.
- Each block quotes whole source lines, unedited, with their line numbers. Lines outside these ranges are not published here; the full file stays private.

## Lines 17-22: ARC table header

```text
   17  ## ARC-AGI-3 scored runs
   18  
   19  The jump from our own loop (0.08–0.13) to the copied Franzen stack (24.82) is still the whole gain. Every addition since (10-07..10-13) landed within ±8 of the copy, except the LoRA-tuned model (16.06), which is the one clear loss. From 10-14 the slots are a stacked sequence (D' → + score rule → + frame check).
   20  
   21  | Date (UTC) | Run (submission) | What was new | Expected to achieve / learn | Public score | Lessons |
   22  | --- | --- | --- | --- | --- | --- |
```

## Lines 23-23: 11-02 final composite, ref 57911309 (26.04)

```text
   23  | 11-02 FINAL manual (fired 14:15:37Z, ref 57911309; decision blackbox/runs/ARC_DECISION_2026-11-02.json, written by interactive thor-claude) | dennispalatov/arc-agi-3-c1-api-history12k-research-nh v1: composite = c1 + v6 advisor + executed read-only investigator (API-clarified, 12k) + factual history flags (READY_composite_s2_1102, 19 markers; flat dataset mounts accepted by dp, READY OVERRIDE line) | dp GO in chat ~14:04Z (save) and ~14:14Z ('yes, go'); codex conditional composite preference 8787 + marker audit 8808. Last scored slot before the 11-02 23:59Z deadline; a long shot for upside over the 31.82 best. | **26.04 public** (Kaggle 'public' field, 0-100+ scale, per-level cap 115; private field empty = `?`). Read by the supervisor 11-03 06:37Z wake; completion time unknown (it landed during 7 supervisor wakes lost to the weekly usage limit, 23:37Z-05:37Z). | Row added by the supervisor 14:37Z wake from the decision file and blackbox/analysis/claude_arc_v7_1102/mail_fired.md. Score reading (survived thor-devils-advocate 11-03): same-base c1 alone scored 29.69 (57747094); prior fires 29.86 and 30.26; best 31.82 is an unreplicated max of ~20 runs. Per-run SD ~3.9 is a public-notebook estimate, so a two-run gap has SD ~5.5 and the 3.7-4.2 gaps are within noise. One run, four stacked changes: no evidence the composite helped or hurt. What would settle it: the private score after the deadline, or a paired c1 vs composite run on the 25-game non-scored bench. |
```

## Lines 26-27: 10-30 forced world-model turn 57819070 (18.14); 10-29 thinking-off on routine turns 57784941 (11.48)

```text
   26  | 10-30 manual (fired 23:15:41Z, ref 57819070; decision blackbox/runs/ARC_DECISION_2026-10-30.json, written by interactive thor-claude) | dennispalatov/arc-agi-3-identity-v3-ka-nh-c1-wmf2 v3: nh-c1 + WMF v2.2 forced world-model turn (at a death or the level's 10th action) + codex combined patch (installer faa8870 = codex 4ae6077) | dp 10-30 ~23:15Z: 'check kimi's message, and if all is good then fire WMF2 v3'. kimi 22:38Z: whole-batch validation repair complete (counterexample revise/retest loop NOT included). codex 4429: no crash/deadlock/forfeit on v2; malformed-suffix path fixed in v3. Aim: does a forced world-model turn lift scored play over nh-c1 (29.69)? Estimate thor-claude ~22 (12-32) | **18.14 public** (COMPLETE; read by check_subs.py at the 10-31 08:37Z supervisor wake; first reported by kimi 08:25Z). Scale 0-100, public field; run-to-run SD ~3.9 per draw | 11.55 below nh-c1 29.69 (about 2.1 SDs of a two-draw gap, n=1 each) and 13.68 below the 31.82 best; inside the 12-32 estimate, below its centre. Same direction as the two local WMF2 draws (25.12/64 and 29.89/65 levels vs c1 47.49/97, different draws, not a matched pair). WMF2 stays out of the backstop candidate (kimi, codex agree). **Caveat (thor-devils-advocate):** the cause is not separated: v3 stacks the forced world-model turn with codex's combined patch. Locally the loss is depth, not efficiency (3/25 games never admitted per draw, shared clears slightly better), so clock starvation from the extra turn is the leading reading, not bad world models. Settles it: one non-scored 25-game pair, nh-c1 + combined patch alone vs the same with WMF on; count games and levels reached and actions per matched cleared level. (supervisor 10-31 08:37Z wake) |
   27  | 10-29 backstop (fired ~23:3xZ, ref 57784941; blackbox/runs/arc_backstop_submit.sh) | dennispalatov/arc-agi-3-identity-v3-ka-ae3nt-nh-c1 v1, the hand-set backstop candidate: LIVE (dp 10-29 ~20:4xZ: 'replace it with something that will test a meaningful swing ... keep updating the backstop with current best'): ae3nt = nh-c1 | The 2026-10-29 slot was unused at 23:30Z. dp 10-24 posture: 'half hour before window close, if we haven't manually used the slot, the time fires the best candidate we have - even if it's a repeat' | Aim: don't waste the slot; a repeat is accepted. Candidate's own risk: untested on any 25-game bench, could score well below 30 | **11.48 public** (0-100 scale, Kaggle public field, one draw on the private 110; COMPLETE, read by check_subs 10-30 08:37Z, ~9 h after the fire). Run-to-run SD ~3.9 per draw (~5.5 for a gap between two single draws). It is 18.2 below its base nh-c1 v1 (29.69, 57747094), about 3.3 gap-SDs, and 20.3 below IDENTITY 31.82. Read: a HARM SIGNAL vs base, n=1 per arm; gp-low v2 (9.62, lower reasoning effort) points the same way. Devil's-advocate caveat: the cause is not separated. ae3nt stacks two changes (thinking OFF on routine turns + adaptive effort v3), and the loss could be either one, or starvation (levels never reached: Thor liveness m0r0 made 2 actions in 15 min) rather than efficiency squared. Run length and games played of the scored rerun are UNKNOWN: `kernels logs .../1` returns only the 96-s save run (ADEFFORT turns 0). What would settle it: a paired 25-game bench vs nh-c1 with thinking-off alone and adaptive-effort alone, reading actions per cleared level and levels reached. (supervisor 10-30 08:4xZ) | Backstop row written by arc_backstop_submit.sh; score added by the supervisor. Per candidate.json current_best_rule, a harm signal demotes the backstop to the last known-score bytes: that edit belongs to the lane/dp (supervisor does not touch candidate.json). |
```

## Lines 41-41: 10-26 effort low 57668634 (9.62)

```text
   41  | 10-26 (fired 13:57:35Z, ref 57668634; slot_plan_1026.sh armed 13:48Z -> arc_manual_submit.sh by hand) | identity-gp-low v2 = GOALPRIOR v1 + reasoning effort LOW on the loop3 v4 stack (LOOP v3 + SIMKEEP v4; saved 10-25, markers OK; corrected 14:17Z from 'IDENTITY stack') | loop3 v4 scored 10-25, so refiring it would be a same-bytes rerun; gp-low v2 is the only saved unscored swing (GPU quota spent until 10-31). Fired at 13:57Z rather than 23:30Z: the backstop candidate either way, earlier = retry room on a platform ERROR (dp ~20:40Z 10-25: backstop management delegated) | Aim: first scored reading of GOALPRIOR v1 + effort low | **COMPLETE 9.62 public** (`publicScore`, read 10-26 23:17Z; ~9.3 h) | Retry loop arc_retry_until_close.sh 2026-10-26 refires on a refund. Known risk: an import-cache race in its cell 41 (fixed in the 10-31 builds) would ERROR before play = refunded, retried. (thor-claude 10-26 13:58Z) **Result read (thor-claude 23:17Z):** 9.62 is -16.6 vs loop3 v4 (26.19) on the same stack and -22 vs IDENTITY 31.82, about 4+ noise SDs (~3.9/sub): a real drop, not noise. Two changes are confounded (GOALPRIOR v1, effort LOW). Prior: effort LOW is the likelier cause (less reasoning per turn on hard levels), but that is a hypothesis. Consequence: no candidate with effort low; GOALPRIOR v2 candidates keep the default effort. |
```

## Lines 51-51: 10-19 IDENTITY, ref 57374159, kernel v3, built at 86e55c04e (31.82)

```text
   51  | 10-19 (fired 00:13Z, ref 57374159, v3; promote_fire_identity_1019.sh) | IDENTITY (`arc-agi-3-lean-capnudge-dprime-identity`) | Frame3 exactly + a persistent run identity seeded from our non-scored runs (seed 1018c, level-weighting sentence amended per codex 1855) + practice memory + a run journal shared across games (dp 10-18; dev-SAGE-wt-dev3 86e55c04e, build_identity.py). Smoke gauges (21:08Z 10-18): first_requests 14/14 carry `[run identity]`, identity=('25','23','20','251'), revision_cards 2 | Does a whole-run identity + journal carry rules across games and move depth over Frame3 28.46? | **31.82 public** (COMPLETE, read 09:15Z 10-19; privateScore empty) | NEW BEST: +3.34 over Frame2 28.48 / Frame3 28.46, inside the ~5.5 two-run SD, so not yet proof the identity/journal caused it, but the first ARC run above 30. The stack is kept and extended: IDJ2 (journal one line per game, SAGE PR 486; smoke v1 gauges fired 08:07Z) is the 10-20 candidate. Lesson: a whole-run identity + cross-game journal did not hurt and may help; read the next stacked score against 31.82 |
```

## Lines 58-58: 10-12 fine-tuned 57088784 (16.06)

```text
   58  | 10-12 | Tuned (57088784) | LEAN + P1 LoRA (rank 16; held-out NLL 1.005→0.823), fast merge at startup | Post-training on our own win trails | 16.06 | The one clear loss (−9 vs LEAN). Serving ruled out (accept rate and tok/s higher). In-family NLL can't see private-set transfer → P1-T leave-families-out test (10-17) before any more tuning |
```

## Lines 60-61: 10-10 Franzen-verify 57026619 (19.22); 10-09 goal audit 56979852 (24.89)

```text
   60  | 10-10 (late, 01:08) | Franzen-verify (57026619) | Gated verification: `replay_check` + `expect=` halts on a contradicted prediction | Does prediction checking convert stuck levels? | 19.22 | −8 vs best. Offline (goal-gate pilot) `plan_check` was called 0 times; kimi's A2 replay (10-14): across 90 transcripts the model never externalizes verification (non-None `expect_failure` 0×). Tools the model doesn't call can't help; the harness must compute the contradiction |
   61  | 10-09 | Goal-audit pilot (56979852) | Text-only goal audit: stall-triggered facts + an invitation to reconsider the goal | Whether asking the model to re-examine its goal converts stuck levels | 24.89 | A question in text gets an answer in text: no lift offline (6/9 = base rate) or scored. Motivated pairing the prompt with an instrument (goal-gate) |
```
