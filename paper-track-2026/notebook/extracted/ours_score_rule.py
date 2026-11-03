# thor-claude 2026-10-13 (kaggle/qwen/patches/build_stack.py): SCORE RULE + HYPOTHESIS-CLASS + TIMER-CLARIFICATION lines
# in the system prompt.
# Teardown 10-12 row #7: gedouluhui's Milestone-2 write-up (Kaggle discussion 743060, "P3.1"): appending the true scoring
# rule and a pacing line to the game overview took their hidden score 1.12 -> 1.43 (n=1, Qwen3.8-27B era).
# The rule is checked against arc_agi/scorecard.py (EnvironmentScoreCalculator.add_level / to_score):
#   cleared level: min(((baseline / actions) ** 2) * 100, 115); not cleared: 0; weight = level index (1-based);
#   the game score is also capped at the weighted fraction of levels cleared (codex review 10-13, aggregate cap).
# v2 (10-13, thor-codex REVIEW.md e7860c1 correction): `time_remaining_seconds` IS model-visible. _compact_action_result
#   forwards it (with run_elapsed_seconds) into every action result, and it reaches the context whenever the agent prints
#   that dict: 361/612 request snapshots in 12/15 games of the D' smoke. In dc22 the model read it as evidence that the
#   HUD bar is a wall-clock timer. v1 wrongly said the field was unseen (a one-game grep read as a negative).
#   gedouluhui's time-PRESSURE instruction stays out: the value is per-game host wall-clock incl. queue waiting under D',
#   not a compute budget. What goes IN is teardown #8's fix for a misleading budget signal: a line saying what the field
#   is and is not (codex's wording, tightened).
# The edit REPLACES Franzen's one-line "Optimize for as few in-game actions..." in the game overview (the new lines say
# the same thing with the arithmetic), so nothing in the prompt contradicts it.
import threading

ANCHOR = "- Optimize for as few in-game actions as possible while still being reliable.\n"
RULE = (
    "- Scoring (how this run is judged): a cleared level scores about 100 x (baseline_actions / your_actions)^2, "
    "capped at 115, where baseline_actions is a skilled human's count; a path twice as long as needed scores about "
    "four times less. Levels are weighted by their number (level k counts k times) and a level never cleared scores 0; "
    "the game score is also capped by the weighted fraction of levels cleared, so action efficiency alone cannot "
    "compensate for uncleared levels. Every in-game action counts, including RESET and UNDO; inspecting the state in "
    "Python costs no actions.\n"
    "- Probe deliberately until the mechanic is understood, then commit to the shortest reliable sequence and batch "
    "confirmed steps in one `action(...)` call. When several distinct hypotheses have failed on a level, stop "
    "repeating near-identical attempts and change the hypothesis class instead.\n"
    "- If an action result reports `time_remaining_seconds`, it is host wall-clock time, including waiting, not the "
    "on-screen action bar or guaranteed model compute. Treat it as a stale snapshot from when that result was "
    "returned; it does not change game physics.\n"
)
MARK = "Scoring (how this run is judged)"
TIMER_MARK = "it is host wall-clock time, including waiting"
CALLS = {"prompts_built": 0}
_LOCK = threading.Lock()


def apply(prompt):
    """The system prompt with Franzen's one-line efficiency instruction replaced by the scoring rule + pacing line.
    Raises unless the anchor occurs exactly once (a changed harness must fail loudly, not silently drop the arm)."""
    n = prompt.count(ANCHOR)
    if n != 1:
        raise RuntimeError(f"score-rule anchor found {n} times in the system prompt (expected 1)")
    out = prompt.replace(ANCHOR, RULE, 1)
    assert out.count(MARK) == 1
    return out


def install(tool_agent):
    """Wrap tool_agent._build_system_prompt (looked up as a module global by ToolAgent.__init__ at call time).
    Idempotent. Returns the probe prompt (built through the ORIGINAL builder + apply; does not touch CALLS)."""
    cur = tool_agent._build_system_prompt
    orig = getattr(cur, "__wrapped__", cur) if getattr(cur, "_ours_score_rule", False) else cur

    def _build_system_prompt(*args, **kwargs):
        out = apply(orig(*args, **kwargs))
        with _LOCK:
            CALLS["prompts_built"] += 1
        return out

    _build_system_prompt.__wrapped__ = orig
    _build_system_prompt._ours_score_rule = True
    tool_agent._build_system_prompt = _build_system_prompt
    return apply(orig(tool_output_tokens=3072))
