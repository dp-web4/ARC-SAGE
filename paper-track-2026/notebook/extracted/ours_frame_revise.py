# thor-claude 2026-10-17 (kaggle/qwen/patches/build_frame3.py): REQUIRED FRAME REVISION at the stall card, the 10-18 row.
# kimi-code 10-14: "level start installs the frame; the card forces its revision." Frame2 (10-17, 28.48) built the first
# half. The 211th audit of its smoke shows the second half never happened: the required level-start line was stated on
# 10/13 levels, and 0/11 stated lines were revised later on the same level. The 10-16 card only OFFERS a re-read
# ("list the role ... pick the one you are least sure of"), and the same week measured three times that the model does
# not do what is merely offered. So the frame-check prefix of the stall card (50 actions on a level, once per level)
# becomes a requirement: write a new `Frame (revised):` line that changes at least one role, then probe that role.
# The rest of the card (Franzen's prior card) is unchanged. tool_agent._prior_card_text() reads the module global
# _PRIOR_CARD_TEXT at call time, so install() rewrites that global. Nothing about any specific game.

OLD_PREFIX_MARK = "[harness] Frame check (this level has taken many actions):"
CARD = (
    "[harness] Frame check (this level has taken many actions): your current frame is not working. Required before "
    "your next action: write one line that starts with `Frame (revised):` and names the role you now give each kind of "
    "piece (player, path, goal, hazard, tool, counter). It must change at least one role from your last `Frame:` line; "
    "mark the changed role with `*`. Then test that changed role with 1-3 actions before any other variant of the old "
    "plan.\n\n"
)
MARK = "Required before your next action: write one line that starts with `Frame (revised):`"


def apply(card_text):
    """Replace the 10-16 frame-check prefix (everything up to its blank line) with the required revision. Raises unless
    the old prefix is present exactly once at the start."""
    if MARK in card_text:
        return card_text
    if not card_text.startswith(OLD_PREFIX_MARK) or card_text.count(OLD_PREFIX_MARK) != 1:
        raise RuntimeError("frame-check prefix missing from the prior card (10-16 frame stack not installed?)")
    rest = card_text.split("\n\n", 1)
    if len(rest) != 2:
        raise RuntimeError("frame-check prefix has no blank-line terminator")
    return CARD + rest[1]


def install(tool_agent):
    """Rewrite tool_agent._PRIOR_CARD_TEXT (idempotent). Returns the installed card text."""
    tool_agent._PRIOR_CARD_TEXT = apply(tool_agent._PRIOR_CARD_TEXT)
    return tool_agent._PRIOR_CARD_TEXT
