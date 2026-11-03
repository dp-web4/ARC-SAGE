# thor-claude 2026-10-14 (kaggle/qwen/patches/build_frame2.py): FRAME AT LEVEL START, the 10-17 stack row.
# kimi-code 10-14 03:30Z (A2 slice 2 + placement answer): "both, not either. Level-start sets the frame; the card forces
# its revision." And the design rule from three measurements (armed census, A2 slices 1-2): the model does not do what
# is merely offered (it never calls offered tools, never externalizes expectations) -> REQUIRE, don't offer.
# So the first user prompt of every new level (Franzen's LEVEL_START_USER_PROMPT, live in 13/16 frame-smoke games)
# ends with a required one-line `Frame:` statement. The line is countable: the smoke gauge counts assistant turns after a
# level start that contain `Frame:` (compliance), separately from the 10-16 card's cards_served.
# tool_agent imports LEVEL_START_USER_PROMPT by name and reads the module global at call time inside
# _build_user_prompt, so install() rebinds tool_agent.LEVEL_START_USER_PROMPT. Nothing about any specific game.

LINE = (
    "\n\nRequired before your first action on this level: write one line that starts with `Frame:` and names the role "
    "you are giving each kind of piece on this board (player, path, goal, hazard, tool, counter). Mark with `?` any "
    "role you carried over from the previous level and have not yet re-checked here; the same-looking piece can play a "
    "different role on a new level."
)
MARK = "Required before your first action on this level: write one line that starts with `Frame:`"


def apply(prompt):
    if MARK in prompt:
        return prompt
    if "You have completed the previous level." not in prompt:
        raise RuntimeError("level-start prompt anchor missing (Franzen's LEVEL_START_USER_PROMPT changed?)")
    return prompt + LINE


def install(tool_agent):
    """Rebind tool_agent.LEVEL_START_USER_PROMPT (idempotent). Raises unless the level-transfer guidance that selects
    it is enabled, since otherwise the edited text would never reach the model. Returns the installed text."""
    if not tool_agent._level_transfer_guidance_enabled():
        raise RuntimeError("level-transfer guidance is off: LEVEL_START_USER_PROMPT would never be sent")
    tool_agent.LEVEL_START_USER_PROMPT = apply(tool_agent.LEVEL_START_USER_PROMPT)
    return tool_agent.LEVEL_START_USER_PROMPT
