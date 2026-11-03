# thor-claude 2026-10-13 (kaggle/qwen/patches/build_frame.py): FRAME CHECK, the 10-16 stack row.
# Two independent reads converged on one mechanism the same day:
#   kimi-code SU15_MERGE_CENSUS_1013.md: parents wall and variants clear on the SAME mechanics because the entry level
#     installs the ontology (parent L1 teaches "dots are a path", so on L2 merges read as loss; the variant's tutorial
#     teaches "pieces move by clicking, the basket is the destination" and the run herds pieces and wins 3/3).
#     "A note pointing AT the frame ('what did L1 teach you to see?') may be worth more than a note about the mechanic."
#   thor-codex 10-13: a generic prior-level-assumption challenge as the next stacked candidate.
# Franzen's level-start wording says the opposite thing by default ("Start from the mechanics you established on the
# previous level; do not rediscover them without reason"): carrying MECHANICS forward is right, carrying ROLES forward
# unexamined is what walls su15. These lines name the roles as a hypothesis, and on a stall ask for one probe of the
# least-sure role. Nothing about any specific game.
#   1. system prompt: one line after the score rule's hypothesis-class line (wraps tool_agent._build_system_prompt
#      on top of ours_score_rule's wrapper; raises unless the score rule is already installed).
#   2. the stall prior card (ARC3_PRIOR_CARD_TRIGGER=stall, 50 actions on a level, once per level) is prefixed with a
#      frame check. tool_agent._prior_card_text() reads the module global _PRIOR_CARD_TEXT at call time.
import threading

SYS_ANCHOR = "change the hypothesis class instead.\n"
SYS_LINE = (
    "- Roles are hypotheses too. When a new level starts, name in one line what the previous level taught you to see: "
    "which pieces you are treating as the player, a path, the goal, a hazard, a tool or a counter. Keep the mechanics "
    "that still hold, but on a new level the same-looking pieces can play a different role; if progress stalls, test "
    "the role you are least sure of with a short probe before trying more variants of the old plan.\n"
)
SYS_MARK = "Roles are hypotheses too."
CARD = (
    "[harness] Frame check (this level has taken many actions): what did the earlier levels, or your first look at "
    "this one, teach you to see here? List the role you are giving each kind of piece (player, path, goal, hazard, "
    "tool, counter). Pick the role you are least sure of, assume a different one, and test it with 1-3 actions before "
    "another variant of the current plan.\n\n"
)
CARD_MARK = "[harness] Frame check"
CALLS = {"prompts_built": 0, "cards_served": 0}
_LOCK = threading.Lock()


def apply(prompt):
    """The system prompt with the frame line after the hypothesis-class line. Raises unless that anchor occurs once."""
    n = prompt.count(SYS_ANCHOR)
    if n != 1:
        raise RuntimeError(f"frame anchor found {n} times in the system prompt (expected 1)")
    out = prompt.replace(SYS_ANCHOR, SYS_ANCHOR + SYS_LINE, 1)
    assert out.count(SYS_MARK) == 1
    return out


def install(tool_agent, score_rule):
    """Wrap the (score-rule-wrapped) system prompt builder and prefix the prior card. Idempotent.
    Returns (probe prompt, card text). The probe goes through the ORIGINAL builder + score_rule.apply + apply, so
    neither module's CALLS counter moves (the editor save's gauges stay 0)."""
    cur = tool_agent._build_system_prompt
    if not getattr(cur, "_ours_score_rule", False) and not getattr(cur, "_ours_frame", False):
        raise RuntimeError("frame install needs the score-rule wrapper in place first")
    base = cur.__wrapped__ if getattr(cur, "_ours_frame", False) else cur

    def _build_system_prompt(*args, **kwargs):
        out = apply(base(*args, **kwargs))
        with _LOCK:
            CALLS["prompts_built"] += 1
        return out

    _build_system_prompt.__wrapped__ = base
    _build_system_prompt._ours_frame = True
    _build_system_prompt._ours_score_rule = True
    tool_agent._build_system_prompt = _build_system_prompt
    if not tool_agent._PRIOR_CARD_TEXT.startswith(CARD_MARK):
        tool_agent._PRIOR_CARD_TEXT = CARD + tool_agent._PRIOR_CARD_TEXT
    cur_card = tool_agent._prior_card_text
    card_base = cur_card.__wrapped__ if getattr(cur_card, "_ours_frame", False) else cur_card

    def _prior_card_text():
        out = card_base()
        if CARD_MARK in out:
            with _LOCK:
                CALLS["cards_served"] += 1
        return out

    _prior_card_text.__wrapped__ = card_base
    _prior_card_text._ours_frame = True
    tool_agent._prior_card_text = _prior_card_text
    probe = apply(score_rule.apply(base.__wrapped__(tool_output_tokens=3072)))
    return probe, card_base()
