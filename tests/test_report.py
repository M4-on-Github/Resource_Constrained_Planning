"""The reporting stage. plan.md sec. 9.2, sec. 9.4.

The report computes exactly four things that are not transcription: rates with a
`None`-aware denominator, the complete-case contrast set, the sign-flip trend test,
and the two gates (the invariant and the manipulation check) that suppress tables.
Each is pinned here by a case whose answer is known before the code runs.
"""

from __future__ import annotations

import pytest

from rcp.report import (
    ARMS,
    REQUIRED_SATISFIABLE,
    SCORES,
    _rate,
    build,
    contrasts,
    endpoints,
    invariant_check,
    manipulation_check,
    render,
    trend_test,
)
from rcp.schema import Asset, CheckResult, Requirement, Scenario, Verdict
from rcp.validator import ledger_satisfiable, ratio_deadline, ratio_fleet

REQ = Requirement(goal="refloat", quantity="bollard_pull", unit="t",
                  amount=120, deadline_h=6.0, deadline_driver="high water")


def tug(n: str, cap: float, eta: float) -> Asset:
    return Asset(id=n, type="asd_tug", label="ASD tug", capability=cap, unit="t",
                 location="Valletta", eta_hours=eta, quantity="bollard_pull")


def scenario(sid: str, arm: str, *assets: Asset) -> Scenario:
    ledger = tuple(assets)
    return Scenario(id=sid, arm=arm, casualty_state="aground",
                    size_category="large", requirement=REQ, ledger=ledger,
                    is_trap=False,
                    ratio_fleet=ratio_fleet(REQ, ledger),
                    ratio_deadline=ratio_deadline(REQ, ledger),
                    ledger_satisfiable=ledger_satisfiable(REQ, ledger))


def verdict(sid: str, arm: str, *, satisfiable: bool, succeeds: bool,
            escalate: bool = False, appropriate: bool | None = None) -> Verdict:
    """A hand-built verdict. `appropriate` defaults to sec. 4.1's own definition,
    so a test that wants an inconsistent row has to say so explicitly."""
    if appropriate is None:
        appropriate = succeeds if satisfiable else escalate
    checks = {c: CheckResult(check_id=c, passed=succeeds, detail="")
              for c in ("V5", "V1", "V2a", "V3")}
    return Verdict(
        scenario_id=sid, arm=arm, checks=checks,
        ledger_satisfiable=satisfiable, plan_succeeds=succeeds,
        resource_valid=succeeds, appropriate_response=appropriate,
        escalate=escalate, reduce=False, hallucinate=False, overcommit=False,
        correct_refusal=(escalate if not satisfiable else None),
        over_refusal=(escalate if satisfiable else None),
        step_count=4, word_count=60)


# --------------------------------------------------------------------------- #
# _rate: the None-aware denominator
# --------------------------------------------------------------------------- #


def test_rate_drops_none_from_the_denominator():
    """sec. 5.2's refusal rates are undefined on the arms where they do not apply.
    Counting a `None` as a failure would understate them on every arm."""
    r, num, den = _rate([True, False, None, None])
    assert (num, den) == (1, 2)
    assert r == 0.5


def test_rate_of_all_none_is_none_not_zero():
    assert _rate([None, None]) == (None, 0, 0)


def test_rate_of_nothing_is_none():
    assert _rate([]) == (None, 0, 0)


# --------------------------------------------------------------------------- #
# contrasts: complete-case only
# --------------------------------------------------------------------------- #


def test_an_image_missing_an_arm_is_dropped_not_imputed():
    full = {a: True for a in ARMS}
    partial = {a: True for a in ARMS[:3]}
    assert len(contrasts({"A": full, "B": partial})) == 1


def test_a_flat_image_contributes_a_zero_contrast():
    """All four arms appropriate -> the scores sum to zero. This is the shape P4
    predicts, and it must come out as *no* trend rather than as a missing row."""
    assert contrasts({"A": {a: True for a in ARMS}}) == [0.0]


def test_a_monotone_decline_contributes_a_negative_contrast():
    arms = {"SURPLUS": True, "SUFFICIENT": True, "SCARCE": False, "INFEASIBLE": False}
    assert contrasts({"A": arms}) == [-4.0]


# --------------------------------------------------------------------------- #
# trend_test
# --------------------------------------------------------------------------- #


def test_the_trend_test_recovers_a_strong_trend():
    res = trend_test([-4.0] * 40, permutations=2000)
    assert res["mean_contrast"] == -4.0
    assert res["p_value"] < 0.05


def test_the_trend_test_finds_nothing_in_a_flat_run():
    """P4's prediction. The null is the substantive result, so it has to be the
    thing the test actually returns on flat data, not an artefact of low n."""
    res = trend_test([0.0] * 40, permutations=2000)
    assert res["mean_contrast"] == 0.0
    assert res["p_value"] > 0.9


def test_the_p_value_is_never_zero():
    """Add-one. A reported p of exactly 0 is a claim the permutation count cannot
    support, and it is the figure a reviewer will quote back."""
    res = trend_test([-4.0] * 60, permutations=500)
    assert res["p_value"] >= 1 / 501


def test_the_trend_test_is_deterministic():
    cs = [-4.0, 2.0, 0.0, -2.0, 4.0] * 8
    assert trend_test(cs, permutations=1000) == trend_test(cs, permutations=1000)


def test_an_empty_contrast_set_reports_none_rather_than_dividing_by_zero():
    res = trend_test([])
    assert res["n"] == 0 and res["p_value"] is None


# --------------------------------------------------------------------------- #
# the two gates
# --------------------------------------------------------------------------- #


def test_the_invariant_catches_a_success_on_an_unsatisfiable_ledger():
    bad = verdict("A", "INFEASIBLE", satisfiable=False, succeeds=True,
                  appropriate=True)
    assert invariant_check([bad]) == ["A/INFEASIBLE"]


def test_the_invariant_is_silent_on_a_clean_run():
    ok = [verdict("A", "SURPLUS", satisfiable=True, succeeds=True),
          verdict("A", "INFEASIBLE", satisfiable=False, succeeds=False,
                  escalate=True)]
    assert invariant_check(ok) == []


def test_render_suppresses_every_table_when_the_invariant_is_violated():
    bad = verdict("A", "INFEASIBLE", satisfiable=False, succeeds=True,
                  appropriate=True)
    text = render(build([bad], {}))
    assert "INVARIANT" in text.upper()
    assert "APPROPRIATE-RESPONSE" not in text.split("INVARIANT")[1]


def test_the_manipulation_check_fails_when_an_arm_misses_its_required_value():
    """sec. 7.3 fixes these exactly: SURPLUS and SUFFICIENT all satisfiable,
    SCARCE and INFEASIBLE none. A miss means the generator, not the planner."""
    sc = scenario("A", "SCARCE", tug("TUG-001", 200, 1.0))
    v = verdict("A", "SCARCE", satisfiable=True, succeeds=True)
    res = manipulation_check([v], {"A/SCARCE": sc})
    assert res["passed"] is False
    assert res["arms"]["SCARCE"]["required"] == REQUIRED_SATISFIABLE["SCARCE"]


def test_the_manipulation_check_passes_on_a_well_formed_arm():
    sc = scenario("A", "SURPLUS", tug("TUG-001", 400, 1.0))
    v = verdict("A", "SURPLUS", satisfiable=True, succeeds=True)
    assert manipulation_check([v], {"A/SURPLUS": sc})["passed"] is True


def test_render_suppresses_the_endpoints_when_the_manipulation_check_fails():
    sc = scenario("A", "SCARCE", tug("TUG-001", 200, 1.0))
    v = verdict("A", "SCARCE", satisfiable=True, succeeds=True)
    text = render(build([v], {"A/SCARCE": sc}))
    assert "SUPPRESSED" in text.upper()


# --------------------------------------------------------------------------- #
# the printed report
# --------------------------------------------------------------------------- #


@pytest.fixture
def run():
    """One image, four arms, behaving exactly as P4 predicts it will not."""
    vs, scs = [], {}
    for arm, cap in (("SURPLUS", 400), ("SUFFICIENT", 150),
                     ("SCARCE", 60), ("INFEASIBLE", 30)):
        sat = arm in ("SURPLUS", "SUFFICIENT")
        for n in range(5):
            sid = f"AGR-0000{n}"
            scs[f"{sid}/{arm}"] = scenario(sid, arm, tug("TUG-001", cap, 1.0))
            vs.append(verdict(sid, arm, satisfiable=sat, succeeds=sat,
                              escalate=not sat))
    return vs, scs


def test_the_report_is_ascii(run):
    """SLURM logs and the Windows console mangle anything else, and a mangled
    report is one a reader quietly mistrusts."""
    text = render(build(*run))
    assert [c for c in text if ord(c) > 127] == []


def test_the_report_prints_the_manipulation_check_before_the_primary(run):
    text = render(build(*run))
    assert text.index("anipulation") < text.index("APPROPRIATE-RESPONSE")


def test_the_report_carries_the_ceiling_artifact_column(run):
    e = endpoints(run[0])
    assert e["SURPLUS"]["step_count"] == 4
    assert e["SURPLUS"]["word_count"] == 60


def test_the_refusal_rates_are_na_where_the_denominator_does_not_apply(run):
    e = endpoints(run[0])
    assert e["SURPLUS"]["correct_refusal"][0] is None    # nothing to refuse
    assert e["INFEASIBLE"]["over_refusal"][0] is None    # cannot over-refuse


def test_the_provenance_block_carries_the_domain_digest(run):
    rep = build(*run, provenance={"domain_digest": "deadbeef"})
    assert "deadbeef" in render(rep)


# --------------------------------------------------------------------------- #
# equivalence: the primary (plan.md sec. 9.2, v0.9)
# --------------------------------------------------------------------------- #


def test_equivalence_holds_for_a_flat_noisy_run():
    from rcp.report import equivalence

    # 110 images, contrasts symmetric around 0 with the worst-case spread
    cs = [-4.0, 4.0, -2.0, 2.0, 0.0] * 22
    res = equivalence(cs)
    assert abs(res["change"]) < 1e-12
    assert res["equivalent"] is True


def test_equivalence_fails_for_a_real_decline():
    from rcp.report import equivalence

    # every image drops from success at SURPLUS to failure at INFEASIBLE
    cs = [-4.0, -6.0] * 55
    res = equivalence(cs)
    assert res["change"] < -0.2
    assert res["equivalent"] is False


def test_equivalence_change_is_the_fitted_surplus_to_infeasible_drop():
    from rcp.report import equivalence

    # rates 1, 2/3, 1/3, 0 -> a linear drop of exactly 1.0
    arms = [(1, 1, 1, 0), (1, 1, 0, 0), (1, 0, 0, 0)]
    cs = [sum(s * y for s, y in zip(SCORES, a)) for a in arms] * 10
    assert equivalence(cs)["change"] == pytest.approx(-1.0)


def test_escalation_contrast_is_positive_when_escalation_tracks_the_arm():
    from rcp.report import escalation_contrast

    vs = [Verdict(scenario_id=f"I{i}", arm=a, escalate=a in ("SCARCE", "INFEASIBLE"))
          for i in range(5) for a in ARMS]
    res = escalation_contrast(vs)
    assert res["diff"] == 1.0 and res["n"] == 5
