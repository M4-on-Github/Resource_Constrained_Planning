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

**But resolution alone made V1 unfalsifiable.** If only tokens that resolve are
recorded, no recorded token can fail to resolve, so V1 passed on every plan and
`HALLUCINATE` was 0 by construction (found on the exploratory run; plan.md §4,
docs/deviations.md). A planner that writes `TUG-012` against a ledger with no such
row has named an asset that does not exist, and that is exactly V1's question. So
`scan_ledger_ids` also records **ID-shaped** tokens that do not resolve: a
catalogue prefix followed by digits, in the shape the ledger prints. A shape test,
not a meaning test: "two tugs" and "Port Haldane" are still not names, and a
token like "Tug 1" (a prefix-word plus a bare ordinal) is not ID-shaped either.
"""

from __future__ import annotations

import functools
import re

from .schema import Scenario
from .world import assets, states

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

#: A step carries a branch if it contains one of these. Counted, never graded:
#: plan.md §6.2 forbids conditional steps in the prompt, and this records how
#: often the planner wrote one anyway (reported per arm).
_CONDITIONAL = re.compile(
    r"\b(?:if|unless|in case|in the event|otherwise|failing that|"
    r"as a (?:contingency|backup|fallback)|should (?:\w+\s+){0,6}?fail)\b",
    re.IGNORECASE)


@functools.lru_cache(maxsize=1)
def _id_shape() -> re.Pattern:
    """`<PREFIX>-<digits>` in any case, or `<PREFIX><digits>` / `<PREFIX> <digits>`
    with the prefix in capitals and three digits, as the ledger prints it. The
    second form is what a planner types when it drops the hyphen; requiring the
    capitals and the full width keeps "FT 30" and "Tug 1" out."""
    prefixes = sorted({t["prefix"] for t in assets()["types"].values()},
                      key=len, reverse=True)
    alt = "|".join(map(re.escape, prefixes))
    return re.compile(
        rf"(?<![A-Za-z0-9])(?:(?i:(?:{alt})[-_]\d{{1,4}})|(?:{alt}) ?\d{{3}})(?![A-Za-z0-9])")


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
    """Tokens in `prose` that name an asset, in order of first appearance, deduped.

    Two kinds, both returned **as written** (`ExtractedPlan.assets_named` is raw
    tokens, and V1's failure detail quotes them back):

      * tokens resolving to exactly one ledger ID — deduped on the resolved id,
        so "TUG-002" once and "Tug 002" once is one asset;
      * ID-shaped tokens resolving to none — deduped on their normalised form.
        These are what V1 exists to catch (module docstring).
    """
    from .normalize import normalize, resolve

    ids = list(scenario.ledger_ids)
    found: dict[str, tuple[int, str]] = {}  # resolved id / unresolved key -> (offset, token)
    end_of_text = len((prose or "").rstrip())
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
        for m in _id_shape().finditer(line):
            if offset + m.end() >= end_of_text and _cut_off(m.group(0), ids):
                continue
            if resolve(m.group(0), ids) is None and not _zero_padded_match(m.group(0), ids):
                key = "?" + normalize(m.group(0))
                if key not in found:
                    found[key] = (offset + m.start(), m.group(0))
        offset += len(line)
    # First appearance in the prose, by the offset the match was found at — not by
    # re-searching for the token, which would mis-order a token that also occurs
    # inside an earlier unresolved span.
    return tuple(tok for _, tok in sorted(found.values()))


def _unpad(token: str) -> str:
    from .normalize import normalize

    return re.sub(r"0+(?=\d)", "", normalize(token))


def _zero_padded_match(token: str, ids: list[str]) -> bool:
    """`WIN-6` against a ledger holding `WIN-006`: not resolvable under the frozen
    §4 rule (so never credited), but not an invented asset either, so V1 is not
    failed for it."""
    want = _unpad(token)
    return any(_unpad(aid) == want for aid in ids)


def _cut_off(token: str, ids: list[str]) -> bool:
    """A generation truncated mid-ID ends in `RGT-00`. The exploratory run's only
    unresolved ID-shaped tokens were exactly this, so the last token of the prose
    is not counted as invented when it is a strict prefix of a ledger ID."""
    from .normalize import normalize

    want = normalize(token)
    return any(normalize(aid).startswith(want) and normalize(aid) != want for aid in ids)


def unresolved_named(named: tuple[str, ...], scenario: Scenario) -> tuple[str, ...]:
    """The ID-shaped tokens in `named` that are not in this ledger — V1's failures."""
    from .normalize import resolve

    return tuple(t for t in named if resolve(t, scenario.ledger_ids) is None)


def _step_body(line: str) -> str:
    return re.sub(r"\s+", " ", _STEP_OPENER.sub("", line)).strip().lower()


def trim_repeated_steps(prose: str) -> tuple[str, int]:
    """Cut a plan at its first step that repeats an earlier one word for word.

    Greedy decoding loops: once a step has been written twice the same step is the
    likeliest continuation, and the plan runs to the token cap reprinting it with a
    new number (docs/deviations.md D9). Everything before the first repeat is the
    plan; the rest is the loop. Because decoding is greedy, this is exactly what a
    stop-on-repeat rule at generation time would have produced, so it is applied
    here rather than by regenerating. Returns the kept prose and the number of
    marker-led lines dropped (0 = untouched). Unmarked prose is never cut.
    """
    if not prose:
        return prose, 0
    lines = prose.splitlines()
    seen = set()
    for i, ln in enumerate(lines):
        if not _STEP_OPENER.match(ln.strip()):
            continue
        body = _step_body(ln.strip())
        if not body:
            continue
        if body in seen:
            dropped = sum(1 for x in lines[i:] if _STEP_OPENER.match(x.strip()))
            return "\n".join(lines[:i]).rstrip(), dropped
        seen.add(body)
    return prose, 0


def conditional_steps(steps: list[str]) -> int:
    """How many steps carry an if/unless/otherwise/should-…-fail branch."""
    return sum(1 for st in steps if _CONDITIONAL.search(st))


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
    named = scan_ledger_ids(prose, scenario)
    return {
        "assets_named": named,
        "assets_unresolved": unresolved_named(named, scenario),
        "conditional_steps": conditional_steps(steps),
        "step_count": len(steps),
        "word_count": word_count(prose),
        "goal_hit_det": hit,
        "goal_matched": matched,
        "steps": steps,
        "parse_failed": not steps,
    }
