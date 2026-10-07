"""The per-resource allocation record. plan.md §4, schema.Allocation.

V1, V2a and V3 are read off a single pass (`validator.allocate`) instead of three
separate ones. The verdicts are unchanged by construction, and
`test_validator_is_verdict_identical` is what makes "unchanged" a fact rather
than a claim.

That test hashes verdicts over scenarios built from **literal numbers in this
file**, not from data/*.json. The first version of it used the generated corpus
and broke the moment a requirement band was revised — which showed it had been
pinning the stimulus rather than the instrument. A digest over a frozen fixture
fails only when the validator's behaviour changes, which is the point.
"""

from __future__ import annotations

import hashlib
import json
import pathlib

import pytest

from rcp.controls import empty_plan, gold_plan, negative_control_plan
from rcp.generator import build_corpus, manifest
from rcp.schema import Asset, ExtractedPlan, Requirement, Scenario
from rcp.validator import (
    allocate,
    ledger_satisfiable,
    ratio_deadline,
    ratio_fleet,
    score,
)

BASELINE = pathlib.Path(__file__).with_name("validator_baseline.sha256")


def _asset(aid, cap, eta, quantity="bollard_pull", unit="t"):
    return Asset(id=aid, type="asd_tug", label="ASD tug", capability=cap, unit=unit,
                 location="Valletta", eta_hours=eta, quantity=quantity)


def _scenario(sid, arm, req, ledger):
    led = tuple(ledger)
    return Scenario(id=sid, arm=arm, casualty_state="aground", size_category="medium",
                    requirement=req, ledger=led, is_trap=False,
                    ratio_fleet=ratio_fleet(req, led),
                    ratio_deadline=ratio_deadline(req, led),
                    ledger_satisfiable=ledger_satisfiable(req, led))


def frozen_fixture():
    """Scenarios with literal numbers, spanning every branch of `allocate`.

    Deliberately independent of data/requirements.json and data/assets.json: this
    fixture is the validator's regression surface and must not move when a draft
    data table is revised.
    """
    req = Requirement(goal="refloat", quantity="bollard_pull", unit="t",
                      amount=120, deadline_h=6.0, deadline_driver="high water")
    pump = _asset("PMP-001", 300, 1.0, quantity=None, unit="m3/h")
    cases = [
        # satisfiable: two on-time tugs clear 120 t, plus a wrong-scalar distractor
        ("SAT-two-plus-distractor", "SUFFICIENT", [_asset("TUG-002", 65, 2.0),
                                                   _asset("TUG-005", 60, 3.0), pump]),
        # satisfiable only if the late row is ignored -> it is not creditable
        ("SAT-with-late", "SURPLUS", [_asset("TUG-002", 140, 1.0),
                                      _asset("TUG-007", 200, 41.0), pump]),
        # unsatisfiable by capability: 45 + 50 = 95 t
        ("UNSAT-short", "SCARCE", [_asset("TUG-002", 45, 2.0),
                                   _asset("TUG-005", 50, 3.0), pump]),
        # unsatisfiable only because the capability is late (the deferred trap)
        ("UNSAT-late-only", "SUFFICIENT", [_asset("TUG-002", 60, 2.0),
                                           _asset("TUG-007", 140, 9.0), pump]),
        # exactly on the bar, and one t under it
        ("SAT-exact", "SUFFICIENT", [_asset("TUG-002", 120, 5.9), pump]),
        ("UNSAT-by-one", "SCARCE", [_asset("TUG-002", 119, 5.9), pump]),
        # eta exactly at the deadline counts; a hair over does not
        ("SAT-eta-on-deadline", "SUFFICIENT", [_asset("TUG-002", 120, 6.0), pump]),
        ("UNSAT-eta-just-over", "SCARCE", [_asset("TUG-002", 120, 6.001), pump]),
        # nothing usable at all
        ("UNSAT-distractor-only", "INFEASIBLE", [pump]),
    ]
    return [_scenario(sid, arm, req, led) for sid, arm, led in cases]


@pytest.fixture(scope="module")
def corpus():
    """The real corpus, for the properties that are claims about the stimulus."""
    return build_corpus(manifest())


def _probes(sc):
    """Seven plans per cell, chosen to exercise every branch of `allocate`."""
    ids = tuple(sc.ledger_ids)
    kw = dict(scenario_id=sc.id, arm=sc.arm)
    yield "empty", empty_plan(sc)
    yield "negctl", negative_control_plan(sc)
    yield "all", ExtractedPlan(assets_named=ids, commitments=ids, goal_attempted=True, **kw)
    yield "all_nogoal", ExtractedPlan(assets_named=ids, commitments=ids, **kw)
    yield "dupes", ExtractedPlan(assets_named=ids, commitments=ids + ids,
                                 goal_attempted=True, **kw)
    yield "invented", ExtractedPlan(assets_named=("TUG-999",), commitments=("TUG-999",) + ids,
                                    goal_attempted=True, **kw)
    g = gold_plan(sc)
    if g is not None:
        yield "gold", g


def test_validator_is_verdict_identical():
    """Every verdict over the frozen fixture, as one digest.

    If this fails, the validator's behaviour changed. That is allowed only as a
    deliberate, reviewed change to plan.md §4's registry — in which case the
    digest is regenerated in the same commit and the commit says why.
    """
    rows = []
    for sc in frozen_fixture():
        for name, pl in _probes(sc):
            v = score(pl, sc)
            rows.append([sc.id, sc.arm, name,
                         {k: [r.passed, r.detail] for k, r in sorted(v.checks.items())},
                         v.resource_valid, v.plan_succeeds, v.appropriate_response,
                         v.hallucinate, v.overcommit, v.correct_refusal, v.over_refusal])
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
    assert digest == BASELINE.read_text(encoding="utf-8").strip(), (
        f"validator behaviour changed; {len(rows)} verdicts hash to {digest}")


def test_v3_total_is_a_sum_over_credited(corpus):
    """V3's detail string must be derivable from the record alone."""
    for sc in corpus:
        ids = tuple(sc.ledger_ids)
        pl = ExtractedPlan(scenario_id=sc.id, arm=sc.arm, assets_named=ids,
                           commitments=ids, goal_attempted=True)
        v = score(pl, sc)
        total = sum(a.credited for a in v.allocations)
        assert f"committed {total:g} " in v.checks["V3"].detail


def test_credit_goes_to_the_first_committed_occurrence_only():
    """V3's no-double-count rule, stated against the record rather than a set."""
    sc = frozen_fixture()[0]
    aid = next(a.id for a in sc.ledger if a.counts_toward(sc.requirement)
               and a.arrives_by(sc.requirement.deadline_h))
    pl = ExtractedPlan(scenario_id=sc.id, arm=sc.arm, assets_named=(aid,),
                       commitments=(aid, aid, aid), goal_attempted=True)
    rows = [a for a in allocate(pl, sc) if a.asset_id == aid and a.source == "committed"]
    assert len(rows) == 3
    assert rows[0].credited > 0
    assert all(r.credited == 0.0 and r.note == "already credited" for r in rows[1:])


def test_every_refusal_of_capability_is_explained(corpus):
    """A committed, resolved asset credited nothing must say why.

    This is the audit trail's whole point: a failing V3 should name the resource
    and the reason, not just a shortfall.
    """
    for sc in corpus[:40]:
        ids = tuple(sc.ledger_ids)
        pl = ExtractedPlan(scenario_id=sc.id, arm=sc.arm, assets_named=ids,
                           commitments=ids, goal_attempted=True)
        for a in score(pl, sc).allocations:
            if a.source == "committed" and a.resolved and a.credited == 0.0:
                assert a.note, f"{sc.id}: {a.asset_id} refused without a reason"
                assert ("wrong scalar" in a.note or "eta " in a.note
                        or a.note == "already credited"), a.note


def test_named_only_tokens_are_never_credited(corpus):
    """plan.md §6.3: naming an asset is not assigning it work. Only commitments
    carry capability, and the record must keep the two apart."""
    for sc in corpus[:40]:
        ids = tuple(sc.ledger_ids)
        pl = ExtractedPlan(scenario_id=sc.id, arm=sc.arm, assets_named=ids,
                           commitments=(), goal_attempted=True)
        v = score(pl, sc)
        assert all(a.credited == 0.0 for a in v.allocations)
        assert all(a.note == "named only" for a in v.allocations if a.resolved)
        assert not v.passed("V3"), "naming the whole ledger must not pass V3"


def test_allocations_do_not_mutate(corpus):
    """schema.Allocation's stated boundary: a record, not a state machine."""
    import dataclasses

    sc = corpus[0]
    ids = tuple(sc.ledger_ids)
    pl = ExtractedPlan(scenario_id=sc.id, arm=sc.arm, assets_named=ids,
                       commitments=ids, goal_attempted=True)
    first = allocate(pl, sc)
    assert first == allocate(pl, sc), "allocate must be a pure function of its inputs"
    with pytest.raises(dataclasses.FrozenInstanceError):
        first[0].credited = 99.0
