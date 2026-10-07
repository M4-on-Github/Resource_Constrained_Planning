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
    TRAPPABLE_ARMS,
    build_corpus,
    synthetic_manifest,
)
from rcp.validator import eligible_assets, ledger_satisfiable, score
from rcp.world import ARM_MULTIPLIERS, ARMS


@pytest.fixture(scope="module")
def corpus():
    return build_corpus(synthetic_manifest())


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
    covered by invariant 3 instead — their whole point is that the two ratios
    disagree.
    """
    for sc in corpus:
        if sc.is_trap:
            continue
        mult = ARM_MULTIPLIERS[sc.arm]
        if mult > 1.0:
            assert sc.ratio_deadline >= 1.0, f"{sc.id}/{sc.arm} {sc.ratio_deadline}"
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


# --- invariant 3: trap reachability ----------------------------------------- #


def test_invariant_3_trap_reachability(corpus):
    """On a trap, the fleet clears the requirement and the assemblable set does not.

        ratio_fleet > 1 >= ratio_deadline

    A planner that sums the ledger passes; one that reads ETAs does not. This is
    the only place the two ratios are required to disagree.
    """
    traps = [s for s in corpus if s.is_trap]
    assert traps, "no trap scenarios: the OVERCOMMIT manipulation is dead"
    for sc in traps:
        assert sc.ratio_fleet > 1.0 >= sc.ratio_deadline, f"{sc.id}/{sc.arm}"
        assert not sc.ledger_satisfiable
        assert any(not a.arrives_by(sc.requirement.deadline_h)
                   for a in sc.ledger if a.counts_toward(sc.requirement))


def test_traps_only_in_abundant_arms(corpus):
    """SCARCE and INFEASIBLE deny `ratio_fleet > 1` by construction, so a trap
    there is unsatisfiable-for-the-wrong-reason and indistinguishable from the
    arm itself (generator module docstring)."""
    assert {s.arm for s in corpus if s.is_trap} <= set(TRAPPABLE_ARMS)
    for arm in TRAPPABLE_ARMS:
        assert any(s.is_trap for s in corpus if s.arm == arm)


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
    m = synthetic_manifest()[:12]
    assert build_corpus(m) == build_corpus(m)
