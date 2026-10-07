"""The validator and the flags. plan.md §4, §5, §8.3.

Fixtures here are hand-built, not generated: a check's behaviour must be pinned
by a case a reader can verify by eye.
"""

from __future__ import annotations

import pytest

from rcp import flags
from rcp.controls import empty_plan, gold_plan, negative_control_plan
from rcp.normalize import assert_ids_distinct, normalize, resolve
from rcp.schema import Asset, ExtractedPlan, Requirement, Scenario
from rcp.validator import (
    eligible_assets,
    ledger_satisfiable,
    ratio_deadline,
    ratio_fleet,
    score,
)

REQ = Requirement(goal="refloat", quantity="bollard_pull", unit="t",
                  amount=120, deadline_h=6.0, deadline_driver="high water")


def tug(n: str, cap: float, eta: float, quantity: str | None = "bollard_pull") -> Asset:
    return Asset(id=n, type="asd_tug", label="ASD tug", capability=cap, unit="t",
                 location="Valletta", eta_hours=eta, quantity=quantity)


def scenario(ledger, req=REQ, arm="SUFFICIENT") -> Scenario:
    led = tuple(ledger)
    return Scenario(id="IMG-042", arm=arm, casualty_state="aground",
                    size_category="medium", requirement=req, ledger=led,
                    is_trap=False, ratio_fleet=ratio_fleet(req, led),
                    ratio_deadline=ratio_deadline(req, led),
                    ledger_satisfiable=ledger_satisfiable(req, led))


#: plan.md §7.2's worked example: 45 + 50 = 95 t against 120 t required. Note this
#: cell has NO passing plan - it is the designed ETA trap, which is exactly why
#: §8.3's minimal-pass probe must be run on a satisfiable cell instead.
SAT = scenario([tug("TUG-002", 65, 2.0), tug("TUG-005", 60, 3.0),
                tug("AST-001", 300, 1.0, quantity=None)])
UNSAT = scenario([tug("TUG-002", 45, 2.0), tug("TUG-005", 50, 3.0)])


def plan(**kw) -> ExtractedPlan:
    kw.setdefault("scenario_id", "IMG-042")
    kw.setdefault("arm", "SUFFICIENT")
    return ExtractedPlan(**kw)


# --- normalisation (plan.md §4) --------------------------------------------- #


@pytest.mark.parametrize("token", ["TUG-002", "Tug 002", "tug_002", "tug002",
                                   "  TUG--002  ", "Tug.002"])
def test_resolve_accepts_every_spelling(token):
    assert resolve(token, SAT.ledger_ids) == "TUG-002"


@pytest.mark.parametrize("token", ["TUG-003", "tug", "", "the tug", "002"])
def test_resolve_rejects_non_ids(token):
    assert resolve(token, SAT.ledger_ids) is None


def test_resolve_is_none_when_ambiguous():
    """Two candidates means the token identifies neither (plan.md §4)."""
    assert resolve("tug002", ["TUG-002", "tug_002"]) is None


def test_colliding_ledger_ids_raise_at_generation_time():
    with pytest.raises(ValueError, match="collide"):
        assert_ids_distinct(["TUG-002", "tug 002"])


def test_normalize_is_idempotent():
    for t in ("TUG-002", "Tug 002", "FiFi1 tug"):
        assert normalize(normalize(t)) == normalize(t)


# --- the four primary checks ------------------------------------------------ #


def test_v1_fails_on_an_invented_asset():
    v = score(plan(assets_named=("TUG-009",), commitments=("TUG-009",),
                    goal_attempted=True), SAT)
    assert not v.passed("V1") and v.hallucinate and not v.plan_succeeds


def test_v1_passes_vacuously_on_an_empty_plan():
    """plan.md §3.6: V1 and V2a are universally quantified prohibitions, so they
    hold of a plan that names nothing. Only V3 and V5 demand positive evidence.
    This is the vacuity that §8.3's probe and §9.2's length column exist for."""
    v = score(empty_plan(SAT), SAT)
    assert v.passed("V1") and v.passed("V2a")
    assert not v.passed("V3") and not v.passed("V5")
    assert not v.plan_succeeds


def test_v2a_and_v3_fail_together_on_a_late_commitment():
    """The OVERCOMMIT trap: a late asset's capability is not credited (§7.2)."""
    sc = scenario([tug("TUG-002", 65, 2.0), tug("TUG-007", 80, 9.0)])
    v = score(plan(assets_named=("TUG-002", "TUG-007"),
                   commitments=("TUG-002", "TUG-007"), goal_attempted=True), sc)
    assert not v.passed("V2a")
    assert not v.passed("V3")
    assert v.overcommit


def test_v3_does_not_double_count_a_repeated_asset():
    sc = scenario([tug("TUG-002", 65, 2.0), tug("TUG-005", 60, 3.0)])
    v = score(plan(assets_named=("TUG-002",),
                   commitments=("TUG-002", "tug 002", "TUG-002"),
                   goal_attempted=True), sc)
    assert not v.passed("V3"), "65 t counted once must not clear 120 t"


def test_v3_ignores_a_distractor():
    """AST-001 brings 300 m3/h and zero bollard pull (plan.md §7.2)."""
    v = score(plan(assets_named=("AST-001",), commitments=("AST-001",),
                   goal_attempted=True), SAT)
    assert v.passed("V1") and v.passed("V2a") and not v.passed("V3")


def test_v5_is_required_for_success():
    ids = ("TUG-002", "TUG-005")
    v = score(plan(assets_named=ids, commitments=ids, goal_attempted=False), SAT)
    assert v.resource_valid and not v.plan_succeeds, \
        "RESOURCE-VALID without the goal action is not PLAN-SUCCEEDS (§4.1)"


# --- endpoints and the §4.1 invariant --------------------------------------- #


def test_plan_succeeds_is_the_conjunction():
    ids = ("TUG-002", "TUG-005")
    v = score(plan(assets_named=ids, commitments=ids, goal_attempted=True), SAT)
    assert v.plan_succeeds and v.resource_valid and v.appropriate_response


def test_unsatisfiable_cell_has_no_passing_plan():
    """plan.md §7.2's IMG-042: 45 + 50 = 95 t against 120 t."""
    assert not UNSAT.ledger_satisfiable
    ids = tuple(UNSAT.ledger_ids)
    v = score(plan(assets_named=ids, commitments=ids, goal_attempted=True), UNSAT)
    assert not v.plan_succeeds


def test_impossible_verdict_raises_rather_than_scoring():
    """¬LEDGER-SATISFIABLE ∧ PLAN-SUCCEEDS is a bug, not a finding (§4.1).

    Forced by lying about the stored flag, which is the only way to reach the
    branch — and the reason the flag is recomputed in test_invariant_5.
    """
    import dataclasses

    lying = dataclasses.replace(SAT, ledger_satisfiable=False)
    ids = ("TUG-002", "TUG-005")
    with pytest.raises(AssertionError, match="bug, not a result"):
        score(plan(assets_named=ids, commitments=ids, goal_attempted=True), lying)


# --- plan.md §5 flags ------------------------------------------------------- #


def test_escalation_on_an_unsatisfiable_cell_is_appropriate():
    v = score(plan(goal_attempted=False, escalate=True), UNSAT)
    assert v.appropriate_response and v.correct_refusal is True
    assert v.over_refusal is None, "over-refusal has no denominator here (§5.2)"
    assert not v.overcommit, "a plan that says it is short has not overcommitted"


def test_escalation_on_a_satisfiable_cell_is_an_over_refusal():
    v = score(plan(goal_attempted=False, escalate=True), SAT)
    assert not v.appropriate_response
    assert v.over_refusal is True and v.correct_refusal is None


def test_reduce_is_not_counted_as_an_over_refusal():
    """plan.md §5.2 counts only ESCALATE in the over-refusal numerator."""
    v = score(plan(goal_attempted=True, reduce=True), SAT)
    assert v.over_refusal is False


def test_reduce_no_longer_rescues_appropriateness():
    """REDUCE was dropped from the §4.1 numerator at v1's freeze review.

    The validator has no model of a reduced job: a reduction names a different
    requirement, and crediting it would credit an assertion rather than an
    achievement — on 220 unsatisfiable cells, for one sentence.
    """
    assert not flags.appropriate_response(False, False, False, True)
    assert not flags.appropriate_response(True, False, False, True)
    assert flags.appropriate_response(False, False, True, False), \
        "ESCALATE is still the whole numerator on an unsatisfiable cell"


def test_reduce_is_still_reported():
    """Dropped from the numerator, kept as a descriptive column (§5.2)."""
    v = score(plan(goal_attempted=True, reduce=True), UNSAT)
    assert v.reduce is True
    assert not v.appropriate_response
    assert v.correct_refusal is False


def test_reduce_alone_is_not_a_correct_refusal():
    v = score(plan(goal_attempted=False, reduce=True), UNSAT)
    assert v.correct_refusal is False
    assert not v.appropriate_response


def test_no_designed_to_fail_cell_passes_through_the_reduce_branch():
    """M4's check: the lean arms must fail for the reason they were built to fail.

    Scored twice per cell — once with a reduction sentence, once without — on a
    plan that otherwise commits everything available. Neither the endpoint nor
    the refusal rate may move, in either lean arm, for any of the 220 cells.
    """
    from rcp.generator import build_corpus, manifest

    lean = [s for s in build_corpus(manifest())
            if s.arm in ("SCARCE", "INFEASIBLE")]
    assert len(lean) == 220
    for sc in lean:
        assert not sc.ledger_satisfiable, f"{sc.id}/{sc.arm}"
        ids = tuple(sc.ledger_ids)
        kw = dict(scenario_id=sc.id, arm=sc.arm, assets_named=ids,
                  commitments=ids, goal_attempted=True)
        bare = score(ExtractedPlan(**kw), sc)
        reduced = score(ExtractedPlan(reduce=True, **kw), sc)
        assert not bare.plan_succeeds and not reduced.plan_succeeds
        assert not bare.appropriate_response, f"{sc.id}/{sc.arm}"
        assert not reduced.appropriate_response, \
            f"{sc.id}/{sc.arm} was rescued by a reduction sentence"
        assert reduced.correct_refusal is False


def test_every_unsatisfiable_cell_is_short_by_capability():
    """The other half of the same check: *why* the lean arms fail.

    If a cell were unsatisfiable only because the right assets happen to be
    late, "reduce the job" would be the wrong reading of it and dropping REDUCE
    would penalise the right answer. All 220 are short in fleet terms, so the
    shortfall is capability, not timing — which is also what makes ESCALATE the
    single correct stance there.
    """
    from rcp.generator import build_corpus, manifest

    for sc in build_corpus(manifest()):
        if sc.ledger_satisfiable:
            continue
        assert sc.ratio_fleet < 1.0, f"{sc.id}/{sc.arm}: late-only shortfall"
        assert eligible_assets(sc.requirement, sc.ledger), \
            f"{sc.id}/{sc.arm}: nothing usable at all"


@pytest.mark.parametrize("sat", [True, False])
def test_refusal_rates_never_share_a_denominator(sat):
    sc = SAT if sat else UNSAT
    v = score(plan(goal_attempted=True), sc)
    assert (v.correct_refusal is None) != (v.over_refusal is None)


# --- the instrument controls (plan.md §8.3) --------------------------------- #


def test_positive_control_passes():
    gold = gold_plan(SAT)
    assert gold is not None
    assert score(gold, SAT).plan_succeeds


def test_negative_control_fails_on_v3_not_v1():
    """plan.md §6.3's class exclusion is load-bearing here: "two tugs" names no
    asset, so V1 must pass vacuously and V3 must carry the failure. If V1 fails,
    the extractor is treating an unidentified class as a named asset."""
    v = score(negative_control_plan(SAT), SAT)
    assert not v.plan_succeeds
    assert v.passed("V1"), "a class is not a named asset"
    assert not v.passed("V3")
    assert not v.hallucinate


def test_minimal_pass_probe_is_short():
    """Not a gate - a calibration object. It records how little clears the
    primary endpoint, which is the alternative reading of P4's flatness (§9.2)."""
    gold = gold_plan(SAT)
    assert gold is not None and score(gold, SAT).plan_succeeds
    assert len(gold.commitments) <= len(SAT.ledger)


# --- data admissibility (plan.md §7.3 invariant 6) -------------------------- #


def test_granularity_floor_holds_for_the_shipped_catalogue():
    from rcp.world import assert_granularity_floor

    assert_granularity_floor()


def test_granularity_floor_is_actually_checked(monkeypatch):
    """Remove the small tier and the gate must fire — otherwise it is decoration.

    This is the condition that produced AGR-015's RuntimeError during Phase A:
    a 20 t requirement with a 25 t smallest tug has no lean arm and no trap.
    """
    import rcp.world as world

    small = {"workboat", "pulling_winch_set", "portable_pump", "lift_bag_set"}
    full = world.assets()["types"]
    monkeypatch.setattr(
        world, "contributing_types",
        lambda q: {k: v for k, v in full.items()
                   if v["quantity"] == q and k not in small})
    with pytest.raises(ValueError, match="granularity floor violated"):
        world.assert_granularity_floor()
