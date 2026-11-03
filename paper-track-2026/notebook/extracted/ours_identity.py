# thor-claude 2026-10-18 (kaggle/qwen/patches/build_identity.py): RUN IDENTITY + RUN JOURNAL, the 10-19 stack row.
# dp 10-18: "persistent identity for the whole run, with a seed we bring in. it should know it's playing in
# competition, the approximate number of games ..., that the games are different, the overall goals, and that it is
# the overall score that matters. basically make sure it is aware of the rules and its role. then the request, the
# resources, and reference complete the environment." + "bring memories of our non-scored runs into the game."
# Until now every game started a fresh, anonymous "coding agent"; nothing learned in one game reached another
# (non-negotiable 9, retention). Three parts, nothing about any specific game in the code:
#   1. IDENTITY (rules + role): the seed's identity text heads every game's system prompt.
#   2. PRIOR MEMORY (reference from non-scored runs): the seed's practice rules, one per practice family, written by
#      this player after clearing them; framed as a vocabulary of KINDS of mechanics, not this game's answer.
#   3. RUN JOURNAL (reference built during the run): every level clear in any game appends the game's `Rule for level
#      N:` line plus a new `Method:` line (how it was found). The latest entries from OTHER games are delivered LIVE, in
#      the two prompts built during play: the level-clear ask and the 50-action stall card. (Not the system prompt:
#      thor-reviewer 10-18 found every game's system prompt is built at t~0 - concurrency >= games - so a journal there
#      is always empty.) Written to /kaggle/working/ours_run_journal.jsonl as it grows, so non-scored runs hand the
#      next seed their journal.
import json
import os
import re
import threading

SEED_PATH = "/kaggle/ours_identity_seed.json"
JOURNAL_OUT = "/kaggle/working/ours_run_journal.jsonl"
MARK = "[run identity]"
JOURNAL_SHOW = 12
METHOD_ASK = (" Then, in a second line starting with `Method:`, say how you found it: what you tested or noticed "
              "that settled it, in words that could help on a different game.")
METHOD_RE = re.compile(r"method\s*[:\-–—]\s*(.+)", re.IGNORECASE)
CALLS = {"prompts_built": 0, "journal_writes": 0, "journal_entries_shown": 0, "methods_captured": 0,
         "journal_deliveries": 0}
JOURNAL = []
_LOCK = threading.Lock()
_SEED = None


def load_seed(path=SEED_PATH):
    global _SEED
    with open(path) as f:
        seed = json.load(f)
    for k in ("seed_id", "identity", "practice_rules"):
        if k not in seed:
            raise RuntimeError(f"identity seed missing {k!r}")
    _SEED = seed
    return seed


def _find_method(text):
    if not text:
        return ""
    ms = list(METHOD_RE.finditer(text))
    if not ms:
        return ""
    out = ms[-1].group(1).strip().split("\n")[0].strip(" `*")
    return "" if re.match(r"^\W*(say how you found|how you found it)", out, re.IGNORECASE) else out[:300]


def block():
    """The identity + practice-memory block heading one game's system prompt."""
    if _SEED is None:
        raise RuntimeError("identity seed not loaded")
    parts = [f"{MARK} {_SEED['identity'].strip()}"]
    pr = _SEED.get("practice_rules") or []
    if pr:
        parts.append("Rules you found on PRACTICE games before this run (those games do not appear in this run; read "
                     "them as examples of the kinds of mechanics games use, never as this game's answer):\n"
                     + "\n".join(f"- {r}" for r in pr))
    return "\n\n".join(parts) + "\n\n"


def digest(exclude=None):
    """The latest run-journal entries from OTHER games (live, at a level clear or a stall), or ''."""
    with _LOCK:
        mine = [e for e in JOURNAL if e.get("agent") != exclude][-JOURNAL_SHOW:]
        if mine:
            CALLS["journal_entries_shown"] += len(mine)
            CALLS["journal_deliveries"] += 1
    if not mine:
        return ""
    return ("[run journal] What you found in OTHER games of this run so far (newest last; methods transfer more often "
            "than rules, and no rule here is this game's answer):\n"
            + "\n".join(f"- level {e['level']}: {e['rule']}" + (f" | Method: {e['method']}" if e.get('method') else "")
                         for e in mine))


def _record(entry):
    with _LOCK:
        JOURNAL.append(entry)
        CALLS["journal_writes"] += 1
    try:
        os.makedirs(os.path.dirname(JOURNAL_OUT), exist_ok=True)
        with open(JOURNAL_OUT, "a") as f:
            f.write(json.dumps({k: v for k, v in entry.items() if k != "agent"}) + "\n")
    except OSError:
        pass  # the journal in memory still serves this run; the file is for the next seed


def install(tool_agent, seed_path=SEED_PATH):
    """Wrap the system-prompt builder (on top of the frame stack) and the level-memory ask/observe methods. Idempotent.
    Returns the probe system prompt (built through the ORIGINAL chain, so the editor save's gauges stay 0)."""
    load_seed(seed_path)
    cur = tool_agent._build_system_prompt
    if not getattr(cur, "_ours_frame", False) and not getattr(cur, "_ours_identity", False):
        raise RuntimeError("identity install needs the frame stack's system-prompt wrapper in place first")
    base = cur.__wrapped__ if getattr(cur, "_ours_identity", False) else cur
    if not tool_agent._level_memory_enabled():
        raise RuntimeError("level memory is off: the run journal would never be written")

    def _build_system_prompt(*args, **kwargs):
        out = block() + base(*args, **kwargs)
        with _LOCK:
            CALLS["prompts_built"] += 1
        return out

    _build_system_prompt.__wrapped__ = base
    _build_system_prompt._ours_identity = True
    # deliberately NOT _ours_frame / _ours_score_rule: a frame or score-rule re-install after this one must raise, not
    # silently wrap the frame wrapper twice (found by the inherited idempotency test, 10-18)
    tool_agent._build_system_prompt = _build_system_prompt

    TA = tool_agent.ToolAgent
    ask = getattr(TA._level_memory_ask_line, "__wrapped__", TA._level_memory_ask_line)
    obs = getattr(TA._level_memory_observe_reply, "__wrapped__", TA._level_memory_observe_reply)

    def _level_memory_ask_line(self):
        line = ask(self)
        if not line:
            return line
        d = digest(exclude=id(self))
        return line + METHOD_ASK + (("\n\n" + d) if d else "")

    def _level_memory_observe_reply(self, reasoning, content):
        pending = getattr(self, "_lm_pending", None)
        level = int(pending["level"]) if pending is not None else None
        before = dict(getattr(self, "_lm_entries", {}) or {})
        obs(self, reasoning, content)
        if level is None:
            return
        after = getattr(self, "_lm_entries", {}) or {}
        e = after.get(level)
        if e is None or before.get(level) is e or not e.get("labelled"):
            return
        method = _find_method(content)  # content only: reasoning restates the ask (thor-reviewer 10-18)
        if method:
            with _LOCK:
                CALLS["methods_captured"] += 1
        _record({"agent": id(self), "level": level, "rule": str(e.get("rule", ""))[:300], "method": method,
                 "actions": int(e.get("attempt_actions") or 0), "seed_id": _SEED["seed_id"]})

    opener = getattr(TA._prior_card_opener, "__wrapped__", TA._prior_card_opener)

    def _prior_card_opener(self, user_prompt):
        out = opener(self, user_prompt)
        if out == user_prompt:
            return out
        d = digest(exclude=id(self))
        return out + (("\n\n" + d) if d else "")

    _prior_card_opener.__wrapped__ = opener
    TA._prior_card_opener = _prior_card_opener
    _level_memory_ask_line.__wrapped__ = ask
    _level_memory_observe_reply.__wrapped__ = obs
    TA._level_memory_ask_line = _level_memory_ask_line
    TA._level_memory_observe_reply = _level_memory_observe_reply
    return block()  # the block as installed (journal empty at install); CALLS['prompts_built'] stays 0
