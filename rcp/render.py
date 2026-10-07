"""Scenario -> the text the planner actually reads. plan.md §6.1, §6.2, §7.2.

This module is where Rule 2 is enforced structurally rather than by reading lines:

> **The domain/assertion block is byte-identical across all 110 scenarios and all
> four arms. Only the image and the ledger vary.**

So the prompt is assembled from exactly two constant files and one varying middle:

    prompts/planner_domain.txt   assertions + the four mechanism lines   CONSTANT
    <the scenario block>                                                 VARIES
    prompts/planner_task.txt     format guards + the ESCALATE affordance  CONSTANT

`domain_digest()` hashes the two constant files, every run records it, and
`test_render.py` asserts the constant halves do not vary with scenario or arm. That
is the enforceable form of Rule 2: a drift that would otherwise require auditing
every sentence against every scenario becomes one failing test.

**What the scenario block may and may not say.** It renders §7.2's six columns plus
the pre-aggregation line, and nothing else:

  * the requirement as an **amount, a unit and a deadline** — the naval architect's
    assessment, which is the scenario fact the image cannot supply;
  * one row per ledger asset;
  * the two totals, *on scene before the deadline* and *full fleet*.

The totals are the §7.2 trap, stated in the open. Pre-aggregating is deliberate
(§6.2: "the ledger pre-aggregates while still listing per-asset figures so a model
that prefers to re-derive may") and it does **not** give the verdict away: it reports
two sums and never says which one the requirement must be met from. A planner that
reads `on scene before the deadline: 95 t` against `requires 120 t` and pulls anyway
has committed `OVERCOMMIT` with the number in front of it — which is the whole point
of making the trap countable rather than inferable.

**Arithmetic is off the grading path** (§6.2). Any quantity the plan restates is
recorded and never graded; the validator recomputes from the IDs the plan named.
"""

from __future__ import annotations

import hashlib
import pathlib

from .schema import Asset, Scenario

PROMPTS = pathlib.Path(__file__).resolve().parent.parent / "prompts"

DOMAIN_FILE = PROMPTS / "planner_domain.txt"
TASK_FILE = PROMPTS / "planner_task.txt"


def domain_block() -> str:
    return DOMAIN_FILE.read_text(encoding="utf-8").strip()


def task_block() -> str:
    return TASK_FILE.read_text(encoding="utf-8").strip()


def domain_digest() -> str:
    """SHA-256 over both constant halves, recorded with every run.

    Rule 2's audit trail. If this moves between two runs, the runs are not
    comparable and the tables must not be pooled — the same reason §4's normaliser
    is frozen with the check registry.
    """
    h = hashlib.sha256()
    for f in (DOMAIN_FILE, TASK_FILE):
        h.update(f.read_bytes())
    return h.hexdigest()


def _fmt_hours(h: float) -> str:
    return f"{h:.1f}"


def _capability_cell(a: Asset) -> str:
    """§7.2's form: `45 t bollard pull`. Figure, unit, then the scalar it is in.

    The scalar name is spelled out because it is what V2a's right-scalar test turns
    on: an `oil_boom_set` rated `600 m` counts toward nothing when the requirement
    is bollard pull, and a planner has to be able to see that from the row. A
    distractor renders its own scalar, never a blank — hiding it would make the
    distractor a trick rather than a discrimination.
    """
    figure = f"{_num(a.capability)} {a.unit}"
    if a.quantity:
        return f"{figure} {a.quantity.replace('_', ' ')}"
    return figure


def _num(x: float) -> str:
    return str(int(x)) if float(x).is_integer() else f"{x:g}"


def ledger_table(sc: Scenario) -> str:
    """§7.2's six columns: id, type, capability, location, eta_h, status.

    A fixed-width table rather than markdown: §6.2 forbids markdown tables in the
    *output*, and matching that in the input removes the obvious cue to answer in
    one. Column order is §7.2's and is frozen with the renderer.
    """
    rows = [("ID", "TYPE", "CAPABILITY", "LOCATION", "ETA_H", "STATUS")]
    # Sorted by ID, not by ETA. Any ordering is a cue, and ETA order would put the
    # binding constraint at the top of the table — Rule 2. ID order is the one
    # ordering that correlates with nothing the validator scores.
    rows += [(a.id, a.label, _capability_cell(a), a.location,
              _fmt_hours(a.eta_hours), a.status)
             for a in sorted(sc.ledger, key=lambda a: a.id)]
    widths = [max(len(r[i]) for r in rows) for i in range(6)]
    out = []
    for i, r in enumerate(rows):
        out.append("  ".join(c.ljust(w) for c, w in zip(r, widths)).rstrip())
        if i == 0:
            out.append("  ".join("-" * w for w in widths))
    return "\n".join(out)


def totals_line(sc: Scenario) -> str:
    """§7.2's pre-aggregation: what is assemblable by the deadline, and the fleet.

    Both are stated. Which one the requirement has to be met from is not — that is
    the inference the §7.2 trap measures, and stating it would destroy the trap
    (Rule 2).
    """
    req = sc.requirement
    by_deadline = sum(a.capability for a in sc.ledger
                      if a.counts_toward(req) and a.arrives_by(req.deadline_h))
    fleet = sum(a.capability for a in sc.ledger if a.counts_toward(req))
    latest = max((a.eta_hours for a in sc.ledger if a.counts_toward(req)), default=0.0)
    scalar = req.quantity.replace("_", " ")
    return (f"On scene within {_fmt_hours(req.deadline_h)} h: "
            f"{_num(by_deadline)} {req.unit} combined {scalar}. "
            f"Full fleet: {_num(fleet)} {req.unit} at {_fmt_hours(latest)} h.")


def scenario_block(sc: Scenario) -> str:
    """The only part of the prompt that varies. Image aside, this is the stimulus."""
    req = sc.requirement
    return "\n".join([
        f"Time now: {sc.t0}.",
        "",
        "Naval architect's assessment: this casualty requires "
        f"{_num(req.amount)} {req.unit} {req.quantity.replace('_', ' ')} "
        f"within {_fmt_hours(req.deadline_h)} hours "
        f"({req.deadline_driver}).",
        "",
        "Resource ledger:",
        "",
        ledger_table(sc),
        "",
        totals_line(sc),
    ])


def planner_prompt(sc: Scenario) -> str:
    """The full text prompt. The image is attached separately by `rcp.infer`."""
    return "\n\n".join([domain_block(), scenario_block(sc), task_block()])
