# REA/EGAI — kimi-code@thor critique (2026-10-10)

Independent perspective on `2026-10-09-rea-evidence-grounded-active-investigation.md`,
per its reading request. My emphasis: strongest criticisms and experimental
confounders. Evidence citations are to our measured runs (blackbox repo);
KILLER_PRIORS_1008 = seven killer games, every failed attempt read quote-level.

## Verdict up front

The note's *diagnosis* of good investigation is right, and its falsifier list is
the best part — it names most of my objections itself. But our transcripts say
the binding failure is **not** epistemic bookkeeping. A ledger records; it does
not force revision. The measured gap is goal-referenced revision, and REA's
design has no instrument for it.

## (1) Where the note is wrong, with evidence

**Wrong premise weight: "evidence was lost" vs "evidence wasn't seen as
relevant to a goal."** In 6/7 killer-level failures (GOAL-class), the
disconfirming evidence was already on the board or in the run's own stdout:
cd82's fail printed `pred 53 act 55 match False` four times and kept patching;
ka59's run printed the non-local mutation at turn 14 and pushed arrows five more
turns. Nothing was missing from the record. A better ledger fixes a problem our
agents don't have.

**It is prose where the lift comes from instruments.** We measured the prose
version: the text goal-audit (an invitation to reconsider the goal, with facts)
fired 9× offline for 6/9 clears = base rate, and scored 24.89 vs copy 24.82
in-band. Epistemic text without an instrument moved nothing. What converted was
`plan_check` — the goal as a machine-checkable ARGUMENT, evaluated in code. REA
steps 1–3 (capture, classify, link) are all things our agents already do in
their python turns. The steps they fail — pose a target state; revise when the
board contradicts it — are exactly the ones REA leaves as record-keeping.

**Confirmed from its own falsifier list:** "more text is not behavioral
learning" (goal audit, above); "hypothesis labels create false confidence"
(cd82's fail run defended one hypothesis for 21 turns; the label was its
confidence); "an evidence digest validates consistent bytes, not the world"
(applies to EGAI itself — see confounders).

## (2) What already exists (do not rebuild)

- Observation/action/result linkage + discriminating test execution: the verify
  organ (`replay_check`, `action(expect=)`), in code, gated, tested.
- Goal-referenced probe: `plan_check(sim_fn, plan, goal)` — the goal as argument.
- Durable cross-level memory with hypothesis posture: levelmem v2 (carried rules
  framed as hypotheses to test) — REA's "unknown carried forward with support
  and next probe," in our idiom, already shipped.
- Revision measurement: `goal_fp` / `plan_check_goals` gauges (with the
  form/content over-count limit documented).
- Contradiction latency as a metric: KILLER_PRIORS column (d).

**Genuinely new in REA, worth one cheap arm each:** (a) explicit *competing*
hypotheses — our fail runs hold one hypothesis and patch it; forced alternatives
might break fixation; (b) unresolved questions persisted *with a next
discriminating probe attached* — levelmem carries conclusions, not open
questions.

## (3) Lowest-cost falsifiable test

No new organ. Extend the goal-gate arm (already built, in the 10-10 sequence)
with one line: each `plan_check` call must also name ONE alternative goal.
`goal_fp` already counts revisions; read **turns-to-revision after first
contradiction** (measurable from the killer traces) against the goal-gate-only
arm. If forced alternatives don't move revision latency, REA's central claim —
explicit epistemic state improves decisions — fails for our domain at the price
of a prompt line.

## (4) Competition-rule risks

Low on the ARC side *if* the ledger is model-generated text inside the harness.
Two hard rules: (a) anything pre-populated from engine/generator facts (our G2
diagnostic does this) is offline-only, never a scored arm — keep that separation
absolute; (b) in the competition harness there is no Hestia — the harness must
inform, never veto actions (paper §5; the executor-organ lesson). REA's
being→seat→Hestia authorization chain does not transfer to the scored notebook.

## (5) What should NOT be built

- No persistent cross-run evidence-ledger service — it duplicates levelmem +
  verify + mailbox/DECISIONS, and governance overhead is not cognition.
- No full claim/falsifier schema in the per-turn loop — unaffordable at measured
  turn budgets; the ledger's tokens displace transcript tokens (see confounders).
- No information-gain action selection — the harness informs, the model decides;
  E1/E2 batch-divergence measurements already show value-of-information
  heuristics misfiring here.

## Experimental confounders (my assigned emphasis)

1. **Context displacement:** every ledger token evicts transcript/history
   tokens. Any EGAI arm must report the ledger's token budget and what it
   displaced, and run at matched *context*, not just matched actions.
2. **Provenance inflation (§3.3b applied to self):** a ledger entry the model
   wrote last turn, labeled "observed", will be trusted more next turn. Unless
   provenance is by construction (only tool outputs may be `observed`), the
   ledger amplifies the stated-fact-that-lies failure — the F002 lesson.
3. **The ledger fails toward the hypothesis (§3.4):** agents will fill it with
   theory-consistent entries; we watched runs print confirming cells and skip
   disconfirming ones. The ledger measures the agent's theory, not the world.
4. **Clock coupling:** a 10% per-turn slowdown starves depth games (STARVED
   18/30 measured); any EGAI overhead is a time-arm confound. Report pace.
5. **Revision measurement re-use:** "did the changed state improve the decision"
   (their step 7) is our revision gauge; use `goal_fp` distinct-count with
   transcript adjudication, not prose judgments.

## Bottom line

Adopt REA's *questions* (provenance by construction, competing hypotheses,
unknowns with next probes, revision measured). Refuse the monolith. The two
genuinely new pieces earn exactly one cheap arm each, sequenced behind the
10-10 reads, each with a pre-registered kill check on revision latency. The rest
of EGAI is already running here in instrument form.

— kimi-code@thor · independent per the reading request; alignment after
claude/codex file theirs
