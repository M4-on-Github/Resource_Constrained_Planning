"""plan.md §7.3's five generator invariants, asserted against a finished corpus.

These restate the invariants independently of `generator._accepts`, which is where
the generator *enforces* them. That duplication is deliberate: a loosening of the
acceptance predicate must break a test, not silently widen the corpus.
"""

from __future__ import annotations

import pytest

from rcp.controls import gold_plan
from rcp.generator import (
    LEAN_RATIO_FLOOR,
    build_corpus,
    manifest,
)
from rcp.validator import eligible_assets, ledger_satisfiable, score
from rcp.world import ARM_MULTIPLIERS, ARMS


@pytest.fixture(scope="module")
def corpus():
    """The real corpus: data/manifest.csv, carried from human_gt by
    tools/build_manifest.py. §7.3's invariants are claims about the stimulus that
    actually ships, so they are asserted against it and not against a stand-in."""
    return build_corpus(manifest())


def test_corpus_shape(corpus):
    """110 images x 4 arms, one scenario each (plan.md §7.1)."""
    assert len(corpus) == 440
    assert len({(s.id, s.arm) for s in corpus}) == 440
    assert {s.arm for s in corpus} == set(ARMS)


# --- invariant 1: type match ------------------------------------------------ #


def test_invariant_1_type_match(corpus):
    """An asset counts toward a requirement iff its scalar is the same scalar.

    plan.md §7.3 says this one "falls out of the data" — there is no code path to
    get wrong, only a field. This test is what makes that claim checkable.
    """
    for sc in corpus:
        for a in sc.ledger:
            assert a.counts_toward(sc.requirement) == (a.quantity == sc.requirement.quantity)
            if a.counts_toward(sc.requirement):
                assert a.unit == sc.requirement.unit


def test_every_ledger_carries_a_distractor(corpus):
    """Distractors are real assets denominated in the wrong scalar (plan.md §7.2)."""
    for sc in corpus:
        assert any(a.quantity is None for a in sc.ledger), sc.id


# --- invariant 2: arm fidelity ---------------------------------------------- #


def test_invariant_2_arm_fidelity(corpus):
    """The realised by-deadline ratio tracks the arm.

    Stated against ratio_deadline, not ratio_fleet: the arm is a claim about what
    the planner can actually assemble. Trap scenarios are excluded here and
    excluded by construction; v1 builds none (nested arms leave no place for one).
    """
    for sc in corpus:
        if sc.is_trap:
            continue
        mult = ARM_MULTIPLIERS[sc.arm]
        if mult > 1.0:
            assert sc.ratio_deadline >= 1.0, f"{sc.id}/{sc.arm} {sc.ratio_deadline}"
            if sc.arm == "SURPLUS":
                # strictly more than SUFFICIENT can reach, not a copy of it
                assert sc.ratio_deadline >= 2.0, f"{sc.id}/{sc.arm} {sc.ratio_deadline}"
        else:
            assert sc.ratio_fleet < 1.0, f"{sc.id}/{sc.arm} {sc.ratio_fleet}"
            assert sc.ratio_fleet >= mult * LEAN_RATIO_FLOOR


def test_arm_ratios_are_ordered(corpus):
    """Mean ratio_deadline must be monotone in the multiplier, or the arms are
    not an ordered manipulation and plan.md §9.2's manipulation check fails."""
    means = {}
    for arm in ARMS:
        rows = [s.ratio_deadline for s in corpus if s.arm == arm]
        means[arm] = sum(rows) / len(rows)
    assert means["SURPLUS"] > means["SUFFICIENT"] > means["SCARCE"] > means["INFEASIBLE"]


# --- V2a's teeth, and the surface cue that used to leak ------------------- #


def test_every_ledger_has_a_late_contributing_asset(corpus):
    """V2a is a primary check; in an all-on-time ledger it passes vacuously.

    Every ledger must therefore contain capability that is real, denominated in
    the right scalar, and too late to use. A V2a failure is then unambiguous: the
    stimulus never forces it, so it is always the planner's own error.
    """
    for sc in corpus:
        assert any(a.counts_toward(sc.requirement)
                   and not a.arrives_by(sc.requirement.deadline_h)
                   for a in sc.ledger), f"{sc.id}/{sc.arm} has no late asset"


def test_lateness_does_not_predict_satisfiability(corpus):
    """The Phase A leak, as a regression test.

    When late assets appeared only in trap cells, "this ledger contains a far-away
    ETA" was a perfect predictor of "this ledger is unsatisfiable" across all 440
    cells — so the manipulation could be scored from a surface cue instead of from
    arithmetic. Both outcomes must now occur among ledgers that contain late assets.
    """
    with_late = [s for s in corpus
                 if any(a.counts_toward(s.requirement)
                        and not a.arrives_by(s.requirement.deadline_h)
                        for a in s.ledger)]
    assert len(with_late) == len(corpus)
    outcomes = {s.ledger_satisfiable for s in with_late}
    assert outcomes == {True, False}, (
        "lateness predicts satisfiability: the ETA manipulation is readable "
        "from the presence of a late row alone")


def test_late_capability_is_never_creditable(corpus):
    """ratio_fleet exceeds ratio_deadline wherever late capability exists, and the
    gap is exactly what V3 refuses to credit (plan.md §7.2)."""
    for sc in corpus:
        assert sc.ratio_fleet >= sc.ratio_deadline
        assert sc.ratio_fleet > sc.ratio_deadline, f"{sc.id}/{sc.arm}"


# --- invariant 3: trap reachability, DEFERRED to v2 ------------------------ #


def test_no_traps_in_v1(corpus):
    """plan.md §7.3: the OVERCOMMIT trap is a v2 manipulation (TRAP_FRACTION = 0).

    v1 runs both abundant arms at 110/110 satisfiable, which is what makes SURPLUS
    a clean ceiling and the positive control non-vacuous.
    """
    from rcp.generator import TRAP_FRACTION

    assert TRAP_FRACTION == 0.0
    assert not any(s.is_trap for s in corpus)
    for arm in ("SURPLUS", "SUFFICIENT"):
        rows = [s for s in corpus if s.arm == arm]
        assert all(s.ledger_satisfiable for s in rows), arm
        assert len(rows) == 110


# --- nesting: the arm is the only thing that varies within an image --------- #


def test_arms_are_nested_with_stable_rows(corpus):
    """INFEASIBLE ⊂ SCARCE ⊂ SUFFICIENT ⊂ SURPLUS, row for row: an asset present
    in two arms has the same ID, location, ETA and capability in both."""
    by_image: dict[str, dict[str, set]] = {}
    for s in corpus:
        by_image.setdefault(s.id, {})[s.arm] = set(s.ledger)
    order = ("INFEASIBLE", "SCARCE", "SUFFICIENT", "SURPLUS")
    for iid, arms in by_image.items():
        for lo, hi in zip(order, order[1:]):
            assert arms[lo] < arms[hi], (iid, lo, hi)


def test_arms_share_requirement_and_geography(corpus):
    by_image: dict[str, list] = {}
    for s in corpus:
        by_image.setdefault(s.id, []).append(s)
    for iid, arms in by_image.items():
        assert len({s.requirement for s in arms}) == 1, iid
        ports = {a.location for s in arms for a in s.ledger
                 if not a.location.startswith("underway")}
        assert len({p.split(",")[0] for p in ports}) <= 3, iid


# --- realism: ETA, margin, IDs, enabling kit -------------------------------- #


def test_no_eta_near_the_deadline(corpus):
    """Nothing within max(0.3 h, 5 % of D) of the deadline, either side, so
    whether an asset is on time is never decided by rounding."""
    from rcp.generator import deadline_margin

    for s in corpus:
        d = s.requirement.deadline_h
        m = deadline_margin(d)
        for a in s.ledger:
            assert abs(a.eta_hours - d) >= m - 0.05 - 1e-9, (s.id, a.id, a.eta_hours, d)


def test_eta_follows_location(corpus):
    """ETA is mobilisation + distance / speed: an asset's arrival is consistent
    with where the ledger says it is."""
    from rcp.world import assets as catalogue, geography

    types = catalogue()["types"]
    setup = geography()["underway_setup_h"]
    for s in corpus:
        for a in s.ledger:
            spec = types[a.type]
            nm = int(a.location.rsplit(",", 1)[1].split()[0])
            travel = nm / spec["speed_kn"]
            if a.location.startswith("underway"):
                assert spec["floating"], (s.id, a.id)
                # distance is printed in whole nm: 0.5 nm of rounding, plus the 0.1 h grid
                assert abs(a.eta_hours - (setup + travel)) <= 0.5 / spec["speed_kn"] + 0.051, \
                    (s.id, a.id, a.location, a.eta_hours)
            else:
                lo, hi = spec["mobilise_h"]
                assert lo + travel - 0.05 <= a.eta_hours <= hi + travel + 0.05, \
                    (s.id, a.id, a.location, a.eta_hours)


def test_ids_carry_their_type_prefix(corpus):
    from rcp.world import assets as catalogue

    types = catalogue()["types"]
    for s in corpus:
        for a in s.ledger:
            assert a.id.split("-")[0] == types[a.type]["prefix"], (s.id, a.id, a.type)


def test_enabling_kit_is_present_on_time_and_inert(corpus):
    """Divers on every capsized/sunken ledger, a dewatering pump on every on_fire
    one: on time, and counted toward no scalar, so the arm ratios are untouched."""
    from rcp.world import enabling_kit

    for s in corpus:
        kit = enabling_kit(s.casualty_state)
        if kit is None:
            continue
        rows = [a for a in s.ledger if a.type == kit]
        assert rows, (s.id, s.arm, kit)
        assert all(a.arrives_by(s.requirement.deadline_h) for a in rows), (s.id, s.arm)
        assert not any(a.counts_toward(s.requirement) for a in rows), (s.id, s.arm)


# --- invariant 4: a valid plan exists where one should ---------------------- #


def test_invariant_4_gold_plan_exists_and_passes(corpus):
    """Every satisfiable scenario admits a plan that scores PLAN-SUCCEEDS.

    This is the positive instrument control of plan.md §8.3, run over the whole
    corpus rather than one cell. A failure means the validator rejects valid work,
    which would read in the results as a model failure.
    """
    checked = 0
    for sc in corpus:
        gold = gold_plan(sc)
        assert (gold is not None) == sc.ledger_satisfiable, f"{sc.id}/{sc.arm}"
        if gold is None:
            continue
        v = score(gold, sc)
        assert v.plan_succeeds, f"{sc.id}/{sc.arm}: {[k for k, r in v.checks.items() if not r.passed]}"
        assert v.appropriate_response
        checked += 1
    assert checked > 0


# --- invariant 5: LEDGER-SATISFIABLE is computed, not assumed --------------- #


def test_invariant_5_satisfiability_recomputed(corpus):
    """The stored flag must equal a fresh enumeration over the stored ledger."""
    for sc in corpus:
        assert sc.ledger_satisfiable == ledger_satisfiable(sc.requirement, sc.ledger)


def test_satisfiable_enumeration_equals_monotone_sum(corpus):
    """v1's subset enumeration is provably equal to a single sum.

    validator.ledger_satisfiable documents this and keeps the enumeration anyway,
    so that a second scalar or a role conflict fails loudly instead of silently.
    This test is the proof obligation for the docstring.
    """
    for sc in corpus:
        pool = eligible_assets(sc.requirement, sc.ledger)
        shortcut = sum(a.capability for a in pool) >= sc.requirement.amount
        assert sc.ledger_satisfiable == shortcut, f"{sc.id}/{sc.arm}"


def test_eligible_pool_within_enumeration_budget(corpus):
    """plan.md §7.3's exactness claim depends on the cap holding in practice."""
    from rcp.validator import MAX_LEDGER_FOR_ENUMERATION

    worst = max(len(eligible_assets(s.requirement, s.ledger)) for s in corpus)
    assert worst <= MAX_LEDGER_FOR_ENUMERATION, worst


# --- determinism ------------------------------------------------------------ #


def test_corpus_is_byte_identical_on_rebuild():
    """The seed is derived from the image id, so a corpus is reproducible from
    its manifest alone — no seed file to lose (plan.md §7.1)."""
    from rcp.generator import build_chain

    m = manifest()[:12]
    first = build_corpus(m)
    build_chain.cache_clear()
    assert build_corpus(m) == first
