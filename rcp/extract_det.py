"""The deterministic half of extraction. No model, no network, pure functions.

plan.md §6.3 names `assets_named` as the one rule RCP adds that P9 had no need
for, and then states it as a resolution test: *record only tokens resolving —
after §4 normalisation — to exactly one ledger ID.* That is decidable without a
model, and doing it without one is what keeps V1 free of extraction error. Every
exclusion §6.3 lists falls out of the resolver rather than out of a prompt rule:

    "the shipyard", "a port of refuge"   -> resolve to nothing (places)
    "the Coastguard", "VTS", "the owner" -> resolve to nothing (authorities)
    "the vessel", "No. 2 hold"           -> resolve to nothing (the casualty)
    "foam", "ballast water"              -> resolve to nothing (materials)
    "additional tugs", "more pumps"      -> resolve to nothing (classes)
    "Port Mahon"                         -> resolve to nothing (see below)

`Port Mahon` is the interesting one, and §6.3 calls it the whole rule. It appears
*in the ledger* — as the `location` value of the very assets being named — but
resolution runs against `Scenario.ledger_ids` and never against field values, so
it excludes itself. A string occurring somewhere in the ledger does not make it
an asset, and no prompt has to say so.

The class exclusion is load-bearing for a different reason: §8.3's negative
control names only classes ("two tugs", "the available salvage assets") and must
fail on **V3**, not V1. Since no class resolves, `assets_named` comes back empty
and V1 passes vacuously, which is the behaviour that control checks for.
"""

from __future__ import annotations

import re

from .schema import Scenario
from .world import states

#: A step is a line that opens like a step. Three shapes, because §6.2's format
#: affordance asks for numbered steps but a planner that ignores the format must
#: still be scored rather than dropped: "1." / "1)" / "Step 1:" / "- " / "* ".
_STEP_OPENER = re.compile(
    r"^\s*(?:(?:step\s*)?\d{1,2}\s*[.):\-]|[-*•])\s+", re.IGNORECASE)

#: Sentence split, used only when a generation carries no step markers at all.
#: Deliberately crude: it feeds `step_count`, a §9.2 covariate, never a check.
_SENTENCE = re.compile(r"(?<=[.!?])\s+")

_WORD = re.compile(r"[A-Za-z0-9'’-]+")

#: Candidate spans for ID resolution. One or two adjacent word-ish runs, which
#: covers "TUG-002" (one) and "Tug 002" (two) without inventing a third form.
_SPAN_TOKEN = re.compile(r"[A-Za-z0-9]+(?:[-_.][A-Za-z0-9]+)*")

MAX_SPAN_WORDS = 2


def word_count(prose: str) -> int:
    """§9.2's ceiling-artifact covariate. Words, not tokens — this number is
    reported to a reader, not fed to a model."""
    return len(_WORD.findall(prose or ""))


def segment_steps(prose: str) -> list[str]:
    """Split a generation into steps.

    Marker-led lines win. A generation with no markers anywhere falls back to
    sentences, so `step_count` is never zero for a non-empty plan — a plan that
    ignores the format is a formatting result, not an unscoreable one.
    """
    if not prose or not prose.strip():
        return []
    lines = [ln.strip() for ln in prose.splitlines()]
    marked = [ln for ln in lines if ln and _STEP_OPENER.match(ln)]
    if marked:
        return marked
    body = " ".join(ln for ln in lines if ln)
    return [s.strip() for s in _SENTENCE.split(body) if s.strip()]


def scan_ledger_ids(prose: str, scenario: Scenario) -> tuple[str, ...]:
    """Tokens in `prose` that name exactly one ledger asset, in order, deduped.

    Returned **as written**, not canonicalised: `ExtractedPlan.assets_named` is
    documented as raw tokens, and V1's failure detail quotes them back so a
    reader can see what the planner actually typed.

    Dedup is on the resolved id, not on the token: a plan that writes "TUG-002"
    once and "Tug 002" once has named one asset, and V1 should say so.
    """
    from .normalize import resolve

    ids = list(scenario.ledger_ids)
    found: dict[str, tuple[int, str]] = {}  # resolved id -> (offset, token as written)
    offset = 0
    for line in (prose or "").splitlines(keepends=True):
        tokens = list(_SPAN_TOKEN.finditer(line))
        for i in range(len(tokens)):
            for n in range(1, MAX_SPAN_WORDS + 1):
                if i + n > len(tokens):
                    break
                start, end = tokens[i].start(), tokens[i + n - 1].end()
                aid = resolve(line[start:end], ids)
                if aid is not None and aid not in found:
                    found[aid] = (offset + start, line[start:end])
        offset += len(line)
    # First appearance in the prose, by the offset the match was found at — not by
    # re-searching for the token, which would mis-order a token that also occurs
    # inside an earlier unresolved span.
    return tuple(tok for _, tok in sorted(found.values()))


def goal_vocabulary(state: str) -> tuple[str, ...]:
    """The one-item-per-casualty terminal goal vocabulary (plan.md §4.2).

    Lives in data/requirements.json; surfaced here so the deterministic V5 pass
    and §8.4's coverage gate read the same list.
    """
    spec = states()[state]
    vocab = spec.get("goal_vocabulary") or [spec["goal"]]
    return tuple(str(v).lower() for v in vocab)


def goal_hit(prose: str, state: str) -> tuple[bool, tuple[str, ...]]:
    """Deterministic V5: does any goal phrase appear literally?

    Returns (hit, matched phrases). A miss is NOT a V5 failure — it is the
    question §8.4's coverage gate exists to measure, and it is the only case the
    LLM is asked to adjudicate. Reporting the matched phrases is what lets the
    gate distinguish "the vocabulary is too narrow" from "the plan never tried".
    """
    low = (prose or "").lower()
    matched = tuple(v for v in goal_vocabulary(state) if v in low)
    return bool(matched), matched


def deterministic_pass(prose: str, scenario: Scenario) -> dict:
    """Everything extraction can decide without a model.

    `parse_failed` is set only for a generation with no content at all. plan.md
    §8.2 keeps it a reported rate rather than a dropped row: an empty generation
    is a result about the planner, and V1/V2a pass vacuously on it by design
    (§3.6), which is exactly why §9.2 reports length beside the endpoints.
    """
    steps = segment_steps(prose)
    hit, matched = goal_hit(prose, scenario.casualty_state)
    return {
        "assets_named": scan_ledger_ids(prose, scenario),
        "step_count": len(steps),
        "word_count": word_count(prose),
        "goal_hit_det": hit,
        "goal_matched": matched,
        "steps": steps,
        "parse_failed": not steps,
    }
