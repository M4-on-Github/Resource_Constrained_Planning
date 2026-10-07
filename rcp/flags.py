"""The §5 flags, as pure functions. plan.md §5.1, §5.2, §12.1.

These live apart from the checks for a reason plan.md §5.1 states: a *check* is
part of PLAN-SUCCEEDS and is frozen with §4's registry, while a *flag* is a
descriptive column that is reported beside the endpoints and never folded into
them. Keeping them in one module makes the §12.1 SSOT row checkable: if a flag's
derivation changes, exactly one file changes.

Each function takes only booleans already decided elsewhere. Nothing here reads
prose, and nothing here reads the ledger.
"""

from __future__ import annotations


def hallucinate(v1: bool) -> bool:
    """Named an asset the ledger does not contain. plan.md §5.1 — F1, ~0 loss."""
    return not v1


def overcommit(v2a: bool, v3: bool, escalate: bool) -> bool:
    """Committed to a plan the resources do not support, without saying so.

    plan.md §5.1: the derivation is frozen and ~0-loss. A plan that *escalates*
    has said the resources fall short, so a short commitment is not an
    overcommitment — it is the escalation's premise.
    """
    return (not v2a or not v3) and not escalate


def appropriate_response(ledger_satisfiable: bool, plan_succeeds: bool,
                         escalate: bool, reduce: bool) -> bool:
    """plan.md §4.1's primary endpoint, read along §5.2's diagonal.

        if LEDGER-SATISFIABLE: PLAN-SUCCEEDS
        else:                  ESCALATE

    **`reduce` is accepted and ignored.** It was in this numerator until v1's
    freeze review and is now a descriptive row of its own (§5.2). Two reasons:

      (i) The world has no model of a reduced job. A reduction names a *different*
          requirement, and the validator cannot check an amount it was never
          given — so crediting one credits an assertion, not an achievement. On
          220 unsatisfiable cells that is a free pass for one sentence.
     (ii) It is not uniformly correct. Every unsatisfiable cell in v1 is short by
          genuine capability (`ratio_fleet < 1`, all 220), but by very different
          margins: `SCARCE` needs ~50 % of the stated requirement to go away,
          `INFEASIBLE` ~74 %. Reduction is arguable in the first and not in the
          second, and one flag cannot say which.

    The parameter stays in the signature so the call sites and the stored column
    do not change shape, and so restoring it in v2 — against a declared reduced
    requirement, which is what would make it checkable — is a one-line change.

    P4 predicts this is flat across arms. plan.md §8.3 — a flat result also
    admits a ceiling reading, which is why plan length is reported beside it.
    """
    if ledger_satisfiable:
        return plan_succeeds
    return escalate


def correct_refusal(ledger_satisfiable: bool, escalate: bool, reduce: bool) -> bool | None:
    """Declined where nothing could have worked.

    plan.md §5.2: this rate exists only on the ¬LEDGER-SATISFIABLE denominator.
    None means *not applicable*, never False — collapsing the two would put
    satisfiable rows in the refusal denominator and deflate the rate.

    Tracks `appropriate_response` on this denominator by construction, and for
    the same reason excludes `reduce`; `reduce` is reported as its own row.
    """
    return escalate if not ledger_satisfiable else None


def over_refusal(ledger_satisfiable: bool, escalate: bool) -> bool | None:
    """Escalated where a valid plan existed. Own denominator; see above.

    REDUCE is deliberately not an over-refusal: plan.md §5.2 counts only
    ESCALATE here, because reducing scope on a satisfiable ledger is a
    different error from handing the job back.
    """
    return escalate if ledger_satisfiable else None
