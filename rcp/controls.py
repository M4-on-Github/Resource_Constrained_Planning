"""The instrument controls. plan.md §8.3 and §8.4.

Three controls, run on hand-built plans before any generation is spent:

1. **Positive control** — a gold plan on a satisfiable cell must score
   PLAN-SUCCEEDS. A failure here means the validator rejects valid work.
2. **Negative control** — a plan that commits nothing identifiable must fail,
   and must fail on **V3**, not V1. plan.md §6.3's class exclusion is what makes
   this hold: "two tugs" names no asset, so V1 passes vacuously (§3.6) and the
   only check with positive evidence to demand is V3.
3. **Minimal-pass probe** — the shortest plan satisfying V5 ∧ V1 ∧ V2a ∧ V3.
   It cannot fail; it is a calibration object, not a gate. Printing it shows the
   reader exactly how little clears the primary endpoint, which is the direct
   alternative explanation for P4's predicted flatness (plan.md §9.2).

The gold plan is also plan.md §7.3's invariant 4 (a valid plan exists on every
satisfiable scenario) and the input to §8.4's V5 coverage gate.
"""

from __future__ import annotations

from .schema import ExtractedPlan, Scenario
from .validator import eligible_assets, score

#: plan.md §6.3 — an unidentified class, deliberately. Not a ledger ID.
NEGATIVE_CONTROL_TOKENS = ("two tugs", "the available salvage assets")


def gold_commitment(sc: Scenario) -> tuple[str, ...] | None:
    """The smallest set of eligible assets whose capability clears the amount.

    Greedy on descending capability. Exact for v1: the constraint set is monotone
    in a single scalar, so if any subset clears the amount the greedy one does
    (see validator.ledger_satisfiable). Returns None when no subset can.
    """
    pool = sorted(eligible_assets(sc.requirement, sc.ledger),
                  key=lambda a: a.capability, reverse=True)
    taken: list[str] = []
    total = 0.0
    for a in pool:
        if total >= sc.requirement.amount:
            break
        taken.append(a.id)
        total += a.capability
    return tuple(taken) if total >= sc.requirement.amount else None


def gold_plan(sc: Scenario) -> ExtractedPlan | None:
    """A plan that must pass. None where the ledger cannot support one."""
    ids = gold_commitment(sc)
    if ids is None:
        return None
    return ExtractedPlan(
        scenario_id=sc.id, arm=sc.arm,
        assets_named=ids, commitments=ids,
        goal_attempted=True,
        step_count=len(ids) + 1, word_count=12 * (len(ids) + 1),
    )


#: The probe and the positive control are the same object by construction —
#: the gold plan IS the minimal passing plan under a monotone single scalar.
#: plan.md §8.3 keeps them as separate controls because they answer different
#: questions: one asks "does valid work pass?", the other "how little passes?".
minimal_pass_plan = gold_plan


def negative_control_plan(sc: Scenario) -> ExtractedPlan:
    """Commits to unidentified classes. Must fail, and must fail on V3."""
    return ExtractedPlan(
        scenario_id=sc.id, arm=sc.arm,
        assets_named=(), commitments=NEGATIVE_CONTROL_TOKENS,
        goal_attempted=True, step_count=2, word_count=24,
    )


def empty_plan(sc: Scenario) -> ExtractedPlan:
    """The vacuity case of plan.md §3.6: prohibitions pass, V3 and V5 do not."""
    return ExtractedPlan(scenario_id=sc.id, arm=sc.arm)


def run_controls(scenarios: list[Scenario]) -> dict[str, object]:
    """Run all three controls over a corpus. Returns a report, raises nothing.

    `satisfiable_without_gold` and `gold_without_satisfiable` must both be empty:
    they are the two directions of plan.md §7.3's "LEDGER-SATISFIABLE is computed,
    not assumed".
    """
    rep: dict[str, object] = {
        "n": len(scenarios),
        "positive_failures": [],
        "negative_wrong_check": [],
        "negative_passes": [],
        "satisfiable_without_gold": [],
        "gold_without_satisfiable": [],
        "probe": None,
    }
    for sc in scenarios:
        gold = gold_plan(sc)
        if sc.ledger_satisfiable and gold is None:
            rep["satisfiable_without_gold"].append(f"{sc.id}/{sc.arm}")  # type: ignore[union-attr]
        if gold is not None and not sc.ledger_satisfiable:
            rep["gold_without_satisfiable"].append(f"{sc.id}/{sc.arm}")  # type: ignore[union-attr]

        if gold is not None:
            v = score(gold, sc)
            if not v.plan_succeeds:
                failed = [k for k, r in v.checks.items() if not r.passed]
                rep["positive_failures"].append(f"{sc.id}/{sc.arm}: {failed}")  # type: ignore[union-attr]
            if rep["probe"] is None and sc.arm == "SUFFICIENT":
                rep["probe"] = {
                    "scenario": f"{sc.id}/{sc.arm}",
                    "requirement": f"{sc.requirement.amount:g} {sc.requirement.unit} "
                                   f"by T+{sc.requirement.deadline_h}h",
                    "commitments": list(gold.commitments),
                    "steps": gold.step_count,
                }

        n = score(negative_control_plan(sc), sc)
        if n.plan_succeeds:
            rep["negative_passes"].append(f"{sc.id}/{sc.arm}")  # type: ignore[union-attr]
        elif n.passed("V1") is False or n.passed("V3") is True:
            rep["negative_wrong_check"].append(  # type: ignore[union-attr]
                f"{sc.id}/{sc.arm}: V1={n.passed('V1')} V3={n.passed('V3')}")
    return rep


def report_shape(rep: dict[str, object], no_match_rate: float | None = None) -> dict:
    """`run_controls`'s output in the shape §9.2's control block prints.

    Two booleans and a rate, because that is what halts a run. The full lists stay
    in `detail` — a control that fails has to name the cells, or the failure is not
    actionable.
    """
    pos_fail = rep["positive_failures"]          # type: ignore[index]
    neg_pass = rep["negative_passes"]            # type: ignore[index]
    neg_wrong = rep["negative_wrong_check"]      # type: ignore[index]
    return {
        "n": rep["n"],
        "positive_control_pass": not pos_fail,
        "positive_detail": (f"{len(pos_fail)} gold plans failed" if pos_fail
                            else "every gold plan scores PLAN-SUCCEEDS"),
        # Failing is not enough: §8.3 requires it fail on V3, because a negative
        # control that trips V1 reads as the instrument discriminating when it is
        # only mis-resolving a class name (§6.3).
        "negative_control_fails_on_v3": not neg_pass and not neg_wrong,
        "negative_detail": (f"{len(neg_pass)} passed, {len(neg_wrong)} failed on the "
                            "wrong check" if (neg_pass or neg_wrong)
                            else "fails on V3 with V1 vacuously true, as specified"),
        "no_match_rate": no_match_rate,
        "probe": rep["probe"],                   # type: ignore[index]
        "detail": {k: rep[k] for k in                        # type: ignore[index]
                   ("positive_failures", "negative_passes", "negative_wrong_check",
                    "satisfiable_without_gold", "gold_without_satisfiable")},
    }


def main(argv: list[str] | None = None) -> int:
    import argparse
    import json
    import pathlib

    from . import corpus, coverage

    ap = argparse.ArgumentParser(
        description="RCP instrument controls (plan.md §8.3) -> JSON for the report")
    ap.add_argument("--out", default=None, help="write JSON here as well as stdout")
    args = ap.parse_args(argv)

    rep = run_controls(corpus.load())

    # §8.4's rate rides along with the §8.3 controls because the report prints the
    # three together: a run is halted by the first two and *described* by the third.
    # `run()` returns a None rate when controls/gold_plans/ is empty, which is what
    # makes the report print "not run" rather than silently omitting the row.
    cov = coverage.run()
    shaped = report_shape(rep, no_match_rate=cov["no_match_rate"])
    shaped["coverage"] = {k: cov[k] for k in
                          ("n_plans", "no_match", "no_match_rate", "no_match_cells",
                           "states_covered", "states_uncovered", "by_state")}
    text = json.dumps(shaped, indent=2, sort_keys=True)
    print(text)
    if args.out:
        p = pathlib.Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text + "\n", encoding="utf-8", newline="\n")
        print(f"  -> {p}")
    halt = not shaped["positive_control_pass"] or not shaped["negative_control_fails_on_v3"]
    return 1 if halt else 0


if __name__ == "__main__":
    raise SystemExit(main())
