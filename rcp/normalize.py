"""ID normalisation — frozen with the check registry (plan.md §4).

The planner is asked to name assets by ledger ID (plan.md §13 Q11) and will not
spell them exactly: `TUG-002` arrives as `Tug 002`, `tug-002`, `TUG 002`, `tug002`,
`Tug-002 (45 t)`. Scoring those as absent marks a real asset hallucinated, in a
primary check (V1) whose claimed extraction loss is ~0.

> Loosening this after seeing results raises V1's pass rate. That is a post-freeze
> change to §4 and invalidates the pre-registration (plan.md §12.2).
"""

from __future__ import annotations

import re

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalize(token: str) -> str:
    """Case-fold, then strip every non-alphanumeric character.

    >>> [normalize(t) for t in ("TUG-002", "Tug 002", "tug_002", "tug002")]
    ['tug002', 'tug002', 'tug002', 'tug002']
    """
    return _NON_ALNUM.sub("", token.casefold())


def resolve(token: str, ledger_ids: list[str] | tuple[str, ...]) -> str | None:
    """Resolve a plan token to a ledger ID, or None.

    plan.md §4: a token names an asset only if its normalised form equals the
    normalised form of **exactly one** ledger ID. Ambiguity resolves to None —
    two candidates means the token identifies neither.
    """
    want = normalize(token)
    if not want:
        return None
    hits = [aid for aid in ledger_ids if normalize(aid) == want]
    return hits[0] if len(hits) == 1 else None


def assert_ids_distinct(ledger_ids: list[str] | tuple[str, ...]) -> None:
    """A generator invariant: IDs must stay distinct *after* normalisation.

    `TUG-002` and `tug_002` in one ledger would make every mention of either
    unresolvable. Cheap to assert at generation time, impossible to fix later.
    """
    seen: dict[str, str] = {}
    for aid in ledger_ids:
        key = normalize(aid)
        if key in seen:
            raise ValueError(
                f"ledger IDs collide under normalisation: {seen[key]!r} and {aid!r}"
            )
        seen[key] = aid
