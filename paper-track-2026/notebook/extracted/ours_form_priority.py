# D' slot-priority scheduler, vendored VERBATIM from the public Kaggle notebook
#   shiiin9/affectify-arc-31-54-in-a-single-sub (Affectify ARC, 31.54 in a single sub), cell 21 `_FP_SOURCE`
#   (same module in amatlas/dfranzen-fork-d-prime); the authors name its source arceval/duck/form_priority.py.
# Licence: Kaggle notebooks default to Apache 2.0; their docstring/attribution below is kept unchanged. It builds on
#   Daniel Franzen's ARC-AGI-3 Milestone 2 solution and Tufa Labs' Duck harness (credit to both).
# thor-claude 2026-10-13 (kaggle/qwen/patches/build_dprime.py): the ONLY change is a d_priority call counter
#   (CALLS, lines marked "thor-claude") so a played log can show the scheduler fired.
#   sha256 of the original bytes: 6456efdd7500d67c2851d2b6474b12bd1c41b5138c0b6f3de603299e63d9fcb2
"""dfranzen の配分の優先度を、模擬で見つけた式に差し替える（本番でも効かせる）。

彼の配分の流れ（まだ始めていないゲームが先、動いているゲームは履歴を削るときだけ
入れ替える）はそのまま使い、**優先度の値を出す関数だけ**を替える。

    優先度 = e^{lp·(ℓ-1)}·norm(N) × 2^{-a/ec} × ペース × 2^{-(t/ts)²} × (1 + 伸びしろ/8)

    ℓ  挑戦中のレベル（1始まり）      N  総レベル数（分からなければ10）。norm は 6〜10 に丸めて
                                         55/(N(N+1)/2)（彼と同じ）
    a  このレベルで打った手数          t  このレベルで生成したトークン
    ペース = clip((ref / これまでの1レベルあたりの平均トークン)^pp, 0.25, 4)。
             1レベルも越えていなければ 1
    伸びしろ = 残りのレベル数で 3以上→b3, 2→b2, 1→b1, 0→0

arceval/sim/simulate.py の Form（level_form=2, eff_form=1, shape=0, c_action=0,
combine=2, fade=0）と同じ値を出す（テストで見張る）。

## 取り付け

    install(tool_agent_module)

  - `tool_agent.priority_value` を差し替える（彼の `_snapshot_priority` はこの名前で呼ぶ）
  - `tool_agent.ProgressPace` を差し替える。各ゲームの分析役は作られるときにこの名前で
    ペースの入れ物を作り、レベルを越えるたびに `record_completion(そのレベルのトークン, 基準)`
    を呼ぶ。我々の入れ物は「これまでの1レベルあたりの平均トークン」を返す
  - `ARC3_PRIORITY_PACE=1` にする。そうしないと彼のコードはペースを記録せず、優先度の
    材料（PrioritySnapshot.cost_multiplier）にも載せない

★ 本番の提出でも効かせる（そのための差し替え）。取り付けに失敗したら raise する ――
  提出の前の Save & Run で必ず同じコードが走るので、そこで見つかる。
"""
from __future__ import annotations

import math
import os
import threading
import time

# 模擬で選んだ式（data/datarun/forms-joint、2026-10-02）
CHOSEN = {"level_pow": 0.2, "eff_const": 100.0, "pace_pow": 0.25, "pace_ref": 30_000.0,
          "token_scale": 124_000.0, "b1": 2.5, "b2": 3.5, "b3": 4.0}
SCALE = 1000.0   # 彼の優先度は整数。帯（100万）より十分小さく、順位が潰れない桁にする


class FormPace:
    """これまでに越えたレベルの、1レベルあたりの平均生成トークン。

    彼の ProgressPace と同じ呼ばれ方をする（`record_completion`, `cost_multiplier`）。
    `cost_multiplier()` は倍率ではなく**平均トークンそのもの**を返す（0 なら、まだ無い）。
    これを読むのは差し替えた `form_priority` だけ。
    """

    def __init__(self):
        self.completed = 0
        self.tokens = 0.0

    def record_completion(self, tokens_used: float, reference_tokens: float = 0.0) -> None:
        self.completed += 1
        self.tokens += max(0.0, float(tokens_used))

    def cost_multiplier(self) -> float:
        return self.tokens / self.completed if self.completed else 0.0


def _levels(total) -> int | None:
    try:
        n = int(total)
    except (TypeError, ValueError):
        return None
    return n if n > 0 else None


def form_value(level: int, actions: float, tokens: float, pace: float, total_levels,
               params: dict = CHOSEN) -> float:
    """優先度（小数）。pace はこれまでの1レベルあたりの平均トークン（0 ならまだ無い）。"""
    level = max(1, int(level))
    n = _levels(total_levels) or 10
    n_clamped = min(10, max(6, n))
    norm = 55 / (n_clamped * (n_clamped + 1) / 2)
    a = max(0.0, float(actions))
    t = max(0.0, float(tokens))
    value = math.exp(params["level_pow"] * (level - 1)) * norm
    value *= 2 ** (-(a / params["eff_const"]))
    if pace > 0:
        value *= min(4.0, max(0.25, (params["pace_ref"] / max(1.0, pace)) ** params["pace_pow"]))
    value *= 2 ** (-((t / params["token_scale"]) ** 2))
    remaining = max(0, n - level)
    bonus = (0.0, params["b1"], params["b2"], params["b3"])[min(remaining, 3)]
    return value * (1.0 + bonus / 8.0)


def form_priority(state, **_ignored) -> int:
    """彼の `priority_value(state, ...)` と同じ呼ばれ方で、整数の優先度を返す。

    state は PrioritySnapshot（level, actions, tokens, cost_multiplier, total_levels）。
    彼の寄せ（tail_fraction）や係数の引数は使わない（この式は寄せを持たない）。
    """
    value = form_value(state.level, state.actions, state.tokens,
                       float(getattr(state, "cost_multiplier", 0.0) or 0.0),
                       getattr(state, "total_levels", None))
    return max(1, int(value * SCALE))


# ---- D′（2026-10-03、data/datarun/refine-fine。LB の v1 から模擬で +1.5 前後） ----
#
#     優先度 = A·M·C + B·φ
#
#     A = (1 + 0.5·(ℓ-1))·norm(N) × (300/(300+a))^2.5          深さ（線形）× 手数の効率
#     M = clip((3万 / ペース)^0.4, 0.25, 4)（1レベルも越えていなければ 1）
#     C = 0.1·max(0.1, 1 - a/115) + 0.9·max(0.1, 1 - t/T)        詰まりの減衰（線形、下限 0.1）
#         T = 22.5万 × clip(ペース/3万, 0.5, 2)^0.5（遅いゲームほど我慢を長く。越えていなければ ×1）
#     B = 残りのレベル数で 3以上→16, 2→14, 1→10, 0→0（伸びしろ。足し算）
#     φ = 寄せ。走行の最後の4割で 1 → 0（彼の tail_fraction をそのまま使う）
#
#   加えて「全員まず1回」をやめる: まだ始めていないゲームも、この式の値（ℓ=1, a=t=0）で並べる。
#
# arceval/sim/simulate.py の Form（D_PRIME_FORM）と同じ値を出す（テストで見張る）。

D_PRIME = {"level_pow": 0.5, "eff_const": 300.0, "eff_pow": 2.5, "pace_pow": 0.4,
           "pace_ref": 30_000.0, "c_action": 0.1, "action_scale": 115.0, "c_token": 0.9,
           "token_scale": 225_000.0, "lin_floor": 0.1, "rel_pow": 0.5,
           "b1": 10.0, "b2": 14.0, "b3": 16.0, "fade": 0.4}
# 模擬の Form の引数で書いた同じ式（テストで突き合わせる）
D_PRIME_FORM = {"fade": 0.4, "level_form": 3, "level_pow": 0.5, "eff_form": 0, "eff_const": 300.0,
                "eff_pow": 2.5, "shape": 3, "c_action": 0.1, "c_token": 0.9, "token_scale": 225000.0,
                "combine": 1, "b1": 10.0, "b2": 14.0, "b3": 16.0, "pace_pow": 0.4, "form_fresh": 0,
                "lin_floor": 0.1, "eff_floor": 0.2, "rel_pow": 0.5}


def d_parts(level: int, actions: float, tokens: float, pace: float, total_levels,
            params: dict = D_PRIME) -> tuple:
    """(A·M·C, B)。pace はこれまでの1レベルあたりの平均トークン（0 ならまだ無い）。"""
    level = max(1, int(level))
    n = _levels(total_levels) or 10
    n_clamped = min(10, max(6, n))
    norm = 55 / (n_clamped * (n_clamped + 1) / 2)
    a = max(0.0, float(actions))
    t = max(0.0, float(tokens))
    A = (1.0 + params["level_pow"] * (level - 1)) * norm
    A *= (params["eff_const"] / (params["eff_const"] + a)) ** params["eff_pow"]
    if pace > 0:
        A *= min(4.0, max(0.25, (params["pace_ref"] / max(1.0, pace)) ** params["pace_pow"]))
    scale = params["token_scale"]
    rel = pace if pace > 0 else params["pace_ref"]
    scale *= min(2.0, max(0.5, rel / params["pace_ref"])) ** params["rel_pow"]
    floor = params["lin_floor"]
    C = (params["c_action"] * max(floor, 1.0 - a / params["action_scale"])
         + params["c_token"] * max(floor, 1.0 - t / scale))
    remaining = max(0, n - level)
    B = (0.0, params["b1"], params["b2"], params["b3"])[min(remaining, 3)]
    return A * C, B


def d_value(level, actions, tokens, pace, total_levels, phi: float = 1.0) -> float:
    u, v = d_parts(level, actions, tokens, pace, total_levels)
    return u + v * phi


CALLS = {"d_priority": 0}  # thor-claude 10-13: fire gauge (calls of d_priority)
_CALLS_LOCK = threading.Lock()  # thor-claude 10-13


def d_priority(state, *, tail_fraction=None, **_ignored) -> int:
    """彼の `priority_value(state, tail_fraction=..., ...)` と同じ呼ばれ方。

    寄せ φ は彼が渡す tail_fraction（残り時間 ÷ 寄せの窓。窓の外では 1 より大きい）を
    0〜1 に切って使う。渡されなければ 1（寄せ無し）。
    """
    with _CALLS_LOCK:  # thor-claude 10-13: fire gauge
        CALLS["d_priority"] += 1
    phi = 1.0 if tail_fraction is None else min(1.0, max(0.0, float(tail_fraction)))
    value = d_value(state.level, state.actions, state.tokens,
                    float(getattr(state, "cost_multiplier", 0.0) or 0.0),
                    getattr(state, "total_levels", None), phi)
    return max(1, int(value * SCALE))


FRESH = {"replaced": 0}
_TL = threading.local()


def install_d(tool_agent, solver) -> str:
    """D′ を取り付ける。v1 の install と違い、「全員まず1回」も外す。

    彼のコードで、まだ始めていないゲームは `gate.acquire(200万 − 待ち順)` で並ぶ（どの
    優先度より上の帯）。これを、この式の値（ℓ=1, a=t=0、そのゲームの総レベル数）と、
    寄せで値が変わるようにスナップショットつきで並べ直す。総レベル数は、その遊びを
    走らせているスレッドで `_HarnessGameSession.play` が始まるときに覚えておく。
    """
    for name in ("priority_value", "ProgressPace", "_PriorityGate", "PrioritySnapshot",
                 "_PRIORITY_UNTRIMMED_BASE", "_PRIORITY_BAND"):
        if not hasattr(tool_agent, name):
            raise RuntimeError(f"tool_agent に {name} が無い。彼の版が変わった。")
    session_cls = getattr(solver, "_HarnessGameSession", None)
    if session_cls is None or not callable(getattr(session_cls, "play", None)):
        raise RuntimeError("solver に _HarnessGameSession.play が無い。彼の版が変わった。")
    gate_cls = tool_agent._PriorityGate
    for name in ("acquire", "_enqueue_and_wait", "_snapshot_priority"):
        if not callable(getattr(gate_cls, name, None)):
            raise RuntimeError(f"_PriorityGate に {name} が無い。彼の版が変わった。")

    tool_agent.priority_value = d_priority
    tool_agent.ProgressPace = FormPace
    os.environ["ARC3_PRIORITY_PACE"] = "1"
    os.environ["ARC3_PRIORITY_REFRESH_QUEUE"] = "1"
    os.environ["ARC3_PRIORITY_TAIL_FADE"] = "1"
    os.environ["ARC3_PRIORITY_TAIL_FADE_FRACTION"] = str(D_PRIME["fade"])

    if not getattr(session_cls.play, "_ours_d", False):
        orig_play = session_cls.play

        def play(self, *args, **kwargs):
            run = getattr(getattr(self, "game", None), "game_run", None)
            _TL.n = getattr(run, "number_of_levels", None)
            try:
                return orig_play(self, *args, **kwargs)
            finally:
                _TL.n = None

        play._ours_d = True
        session_cls.play = play

    if not getattr(gate_cls.acquire, "_ours_d", False):
        orig_acquire = gate_cls.acquire
        fresh_floor = tool_agent._PRIORITY_UNTRIMMED_BASE - tool_agent._PRIORITY_BAND
        snapshot_cls = tool_agent.PrioritySnapshot

        def acquire(self, priority):
            if priority < fresh_floor:
                return orig_acquire(self, priority)
            # まだ始めていないゲーム: 帯で先頭に並べず、この式の値で並べる
            snap = snapshot_cls(1, 0, 0.0, 0.0, getattr(_TL, "n", None))
            value = self._snapshot_priority(snap, time.monotonic())
            with self._cond:
                self._enqueue_and_wait(value, snap)
            FRESH["replaced"] += 1

        acquire._ours_d = True
        gate_cls.acquire = acquire

    line = ("#OURS_FORM ok version=d_prime priority_value replaced; fresh-first removed; "
            "tail fade " + str(D_PRIME["fade"]) + "; "
            + " ".join(f"{k}={v:g}" for k, v in D_PRIME.items() if k != "fade"))
    print(line, flush=True)
    return line


def install(tool_agent) -> str:
    for name in ("priority_value", "ProgressPace", "_PriorityGate"):
        if not hasattr(tool_agent, name):
            raise RuntimeError(f"tool_agent に {name} が無い。彼の版が変わった。")
    tool_agent.priority_value = form_priority
    tool_agent.ProgressPace = FormPace
    os.environ["ARC3_PRIORITY_PACE"] = "1"
    line = ("#OURS_FORM ok priority_value replaced; pace=mean tokens per cleared level; "
            + " ".join(f"{k}={v:g}" for k, v in CHOSEN.items()))
    print(line, flush=True)
    return line
