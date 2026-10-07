"""The LLM half of extraction: four binary questions and a subtraction.

Prompt building and response parsing are pure functions here, testable with no
model — P9's `plan_adequacy/extract.py` is organised the same way and for the
same reason: calibration must exercise the exact code that ships, or it proves
nothing about the run.

**The model never produces a token.** `assets_named` is resolved deterministically
in `extract_det`, and this stage only asks which of those already-resolved assets
the plan does *not* assign work to. Three consequences worth stating, because they
are the reason the design is shaped this way:

  1. **V1 is immune to extraction error.** The model cannot name an asset, so it
     cannot manufacture a `HALLUCINATE`, and §5.1's ~0-loss claim for F1 holds
     without needing to be believed.
  2. **V3's pool is bounded above** by what the deterministic pass found. The
     model can only remove capability, never add it.
  3. **The question is closed.** plan.md §6.3's diagnostic — "if either LLM field
     needs rule-4-scale elaboration to stabilise, the field is not closed enough"
     — is much easier to satisfy for "is this named asset assigned work?" than
     for "list the assets."

**The model is blind to the arithmetic.** It is shown the prose and the asset ids
found in it. It is never shown `capability`, `eta_hours`, `requirement.amount` or
`deadline_h`, so it cannot know whether the plan succeeds and cannot be pulled
toward making it succeed or fail. This is the firewall that keeps the extractor
out of §3.6's circularity: it reports, and it structurally cannot judge.
"""

from __future__ import annotations

import json
import pathlib
import re
from typing import Any

PROMPTS = pathlib.Path(__file__).resolve().parent.parent / "prompts"

#: Guided-decoding schema. Flat, and every field required.
#:
#: No `"type": [...]` shorthand anywhere, and no nulls. P9's calibration
#: (2026-08-24, glm4_32b) found `null_fidelity` pinned at exactly 0.0 across two
#: runs — unmoved by twelve worked examples — because this cluster's vLLM grammar
#: compiler can silently collapse the type-array shorthand to a single type,
#: making a value structurally unreachable. A flatness that total is the signature
#: of an unreachable value, not a prompt-following failure. Booleans and a string
#: array avoid the question entirely.
SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "not_assigned_work": {"type": "array", "items": {"type": "string"}},
        "attempts_goal": {"type": "boolean"},
        "escalates": {"type": "boolean"},
        "reduces": {"type": "boolean"},
    },
    "required": ["not_assigned_work", "attempts_goal", "escalates", "reduces"],
    "additionalProperties": False,
}

_FIELDS = ("not_assigned_work", "attempts_goal", "escalates", "reduces")


def system_prompt() -> str:
    return (PROMPTS / "extract_system.txt").read_text(encoding="utf-8")


def user_prompt(prose: str, assets_named: tuple[str, ...], goal: str) -> str:
    """One generation, its resolved asset tokens, and the casualty's goal verb.

    `goal` is a single word from data/requirements.json, not the requirement: the
    model needs to know the plan was supposed to refloat something in order to
    answer `attempts_goal`, and needs nothing else. No amount, no deadline, no
    capability — see the module docstring.
    """
    template = (PROMPTS / "extract_user.txt").read_text(encoding="utf-8")
    listed = "\n".join(f"  - {t}" for t in assets_named) or "  (none)"
    return template.format(goal=goal, assets=listed, plan=prose.strip())


def build_prompts(items: list[dict]) -> list[tuple[str, str]]:
    """(system, user) pairs aligned with `items`.

    The system prompt is byte-identical across every call, which is what makes
    vLLM's prefix caching worth enabling — same reasoning as P9's extractor.
    """
    sys_p = system_prompt()
    return [(sys_p, user_prompt(it["prose"], it["assets_named"], it["goal"]))
            for it in items]


def parse_response(raw: Any, assets_named: tuple[str, ...]) -> dict:
    """One guided-JSON response -> the four fields. Never raises.

    A parse failure is recorded, not guessed at: `llm_parse_failed` goes true and
    the fields take their declared defaults — every asset assigned work, no
    stance taken. That default is deliberately the *conservative* one for the
    endpoints: it removes no capability and claims no escalation, so a broken
    response cannot turn a failing plan into a passing one or manufacture a
    correct refusal. P9's convention is the same (a bad response becomes
    `no_match` rather than aborting a batch).
    """
    out = {
        "not_assigned_work": (),
        "attempts_goal": False,
        "escalates": False,
        "reduces": False,
        "llm_parse_failed": False,
    }
    if isinstance(raw, str):
        raw = _loads(raw)
    if not isinstance(raw, dict) or any(f not in raw for f in _FIELDS):
        out["llm_parse_failed"] = True
        return out

    out["attempts_goal"] = bool(raw["attempts_goal"])
    out["escalates"] = bool(raw["escalates"])
    out["reduces"] = bool(raw["reduces"])
    out["not_assigned_work"] = _restrict(raw["not_assigned_work"], assets_named)
    return out


def _loads(text: str) -> Any:
    """Tolerate a fenced or prose-wrapped object even though the prompt forbids
    both and guided decoding should prevent them. Costs four lines and converts a
    whole batch's worth of parse failures into data if a backend ever returns
    unconstrained text."""
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-z]*\s*|\s*```$", "", text, flags=re.IGNORECASE)
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if not m:
            return None
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None


def _restrict(returned: Any, assets_named: tuple[str, ...]) -> tuple[str, ...]:
    """Keep only entries that match a token we gave the model.

    Matching is by §4 normalisation, so whitespace or case drift in the echo does
    not silently drop an exclusion. Anything unrecognised is discarded rather
    than honoured: the model's output is restricted to the deterministic set by
    code, which is what makes `commitments ⊆ assets_named` a property of the
    pipeline instead of an instruction the model is trusted to follow.
    """
    from .normalize import normalize

    if not isinstance(returned, list):
        return ()
    index = {normalize(t): t for t in assets_named}
    kept: list[str] = []
    for entry in returned:
        if not isinstance(entry, str):
            continue
        tok = index.get(normalize(entry))
        if tok is not None and tok not in kept:
            kept.append(tok)
    return tuple(kept)
