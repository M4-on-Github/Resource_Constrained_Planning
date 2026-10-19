"""plan_v013.md's knowing probe: read a YES/NO answer. Pure; no model, no LLM.

The probe asks one question per cell in two polarities (`rcp.render.TASKS`). The
reading is fixed before any probe output exists (plan_v013.md §3): the first
non-empty line, leading punctuation and markdown stripped, must start with the
word YES or NO, in any case. Anything else is unparsed, never guessed.

plan_v013b.md adds three wordings. `probe_enough` and `probe_request` are read
as above. `probe_feasible` asks for the totals first, so its last non-empty line,
punctuation and markdown stripped from both ends, must be exactly FEASIBLE or
INFEASIBLE, in any case.
"""

from __future__ import annotations

import re

#: The answer that says the ledger falls short, per wording.
SHORT_ANSWER = {"probe_can": "no", "probe_short": "yes",
                "probe_enough": "no", "probe_request": "yes",
                "probe_feasible": "infeasible"}

_FIRST = re.compile(r"^[\W_]*(yes|no)\b", re.IGNORECASE)
_LAST = re.compile(r"^[\W_]*(feasible|infeasible)[\W_]*$", re.IGNORECASE)


def answer(text: str) -> str | None:
    """`"yes"`, `"no"`, or None when the first non-empty line starts with neither."""
    for line in text.splitlines():
        if line.strip():
            m = _FIRST.match(line.strip())
            return m.group(1).lower() if m else None
    return None


def verdict_word(text: str) -> str | None:
    """`"feasible"`, `"infeasible"`, or None unless the last non-empty line is one."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    m = _LAST.match(lines[-1]) if lines else None
    return m.group(1).lower() if m else None


def says_short(text: str, task: str) -> bool | None:
    """True if this reading says the ledger falls short; None if unparsed."""
    a = verdict_word(text) if task == "probe_feasible" else answer(text)
    return None if a is None else a == SHORT_ANSWER[task]


def knows(readings: list[bool | None]) -> float | None:
    """A cell's score k: the mean of its parsed readings, None if none parsed."""
    parsed = [r for r in readings if r is not None]
    return sum(parsed) / len(parsed) if parsed else None
