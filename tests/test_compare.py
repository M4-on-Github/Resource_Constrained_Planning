"""The paired two-condition comparison. plan.md §9.2 at one arm.

Two things are worth testing here and they are different in kind.

The **statistics** must be right in the sense that a textbook would recognise:
the exact paired test on discordant pairs is `Binomial(n, ½)` doubled, and there
are published values to check against. Those tests are arithmetic.

The **refusals** matter more. This module's job is to decline to produce a table
when the two files are not the experiment — same condition twice, different arms,
or an identical `domain_digest`, which would mean the manipulation never reached
the prompt and a null result was an artifact. A silent wrong table is the failure
mode that survives review, so each refusal has a test.
"""

from __future__ import annotations

import math

import pytest

from rcp.compare import (
    discordance,
    exact_paired_test,
    min_detectable_split,
    pairs,
)
from rcp.schema import Verdict


def _v(sid: str, arm: str = "SUFFICIENT", *, ar: bool = True,
       sat: bool = True, ps: bool = True, over: bool | None = None) -> Verdict:
    """A minimally populated verdict. Only the fields the comparison reads."""
    return Verdict(
        scenario_id=sid, arm=arm, checks={},
        resource_valid=ps, plan_succeeds=ps, appropriate_response=ar,
        ledger_satisfiable=sat, hallucinate=False, overcommit=False,
        escalate=not ps, reduce=False,
        correct_refusal=None, over_refusal=over,
        step_count=3, word_count=100,
    )


# --------------------------------------------------------------------------- #
# pairing
# --------------------------------------------------------------------------- #


def test_pairing_is_complete_case_on_scenario_id():
    a = [_v("A", ar=True), _v("B", ar=False), _v("C", ar=True)]
    b = [_v("A", ar=False), _v("B", ar=False)]
    assert pairs(a, b, "appropriate_response") == [(True, False), (False, False)]


def test_a_none_endpoint_drops_the_pair_rather_than_counting_as_false():
    """`over_refusal` is `None` where it is undefined; that is its meaning."""
    a = [_v("A", over=True), _v("B", over=None)]
    b = [_v("A", over=False), _v("B", over=True)]
    assert pairs(a, b, "over_refusal") == [(True, False)]


def test_discordance_counts_the_four_cells():
    ps = [(True, True), (True, False), (True, False), (False, True),
          (False, False)]
    assert discordance(ps) == (1, 2, 1, 1)


# --------------------------------------------------------------------------- #
# the exact test
# --------------------------------------------------------------------------- #


def test_the_exact_test_matches_the_binomial_by_hand():
    """10 discordant pairs split 9-1: two-sided p = 2 * (1 + 10) / 2**10."""
    ps = [(True, False)] * 9 + [(False, True)] * 1 + [(True, True)] * 20
    r = exact_paired_test(ps)
    assert r["n_discordant"] == 10
    assert r["p_value"] == pytest.approx(2.0 * 11 / 1024)
    assert r["n_pairs"] == 30


def test_the_exact_test_is_the_sign_flip_test_with_scores_minus_one_plus_one():
    """The claim in the docstring, checked by enumeration rather than asserted.

    Every sign assignment over the discordant pairs is enumerated and the fraction
    at least as extreme as observed is compared to the closed form. Concordant pairs
    contribute 0 under every flip, so they drop out -- which is why the exact form
    is legitimate and not a different test that happens to be cheaper.
    """
    ps = [(True, False)] * 5 + [(False, True)] * 2 + [(False, False)] * 8
    observed = abs(2 - 5)
    n = 7
    extreme = 0
    for mask in range(2 ** n):
        total = sum(1 if (mask >> i) & 1 else -1 for i in range(n))
        if abs(total) >= observed - 1e-12:
            extreme += 1
    assert exact_paired_test(ps)["p_value"] == pytest.approx(extreme / 2 ** n)


def test_no_discordant_pairs_means_p_equals_one_not_a_missing_value():
    ps = [(True, True)] * 40 + [(False, False)] * 10
    r = exact_paired_test(ps)
    assert r["n_discordant"] == 0
    assert r["p_value"] == 1.0
    assert r["diff"] == 0.0


def test_the_difference_is_signed_stated_minus_blind():
    ps = [(False, True)] * 8 + [(True, False)] * 2 + [(True, True)] * 10
    assert exact_paired_test(ps)["diff"] == pytest.approx((8 - 2) / 20)
    flipped = [(y, x) for x, y in ps]
    assert exact_paired_test(flipped)["diff"] == pytest.approx(-(8 - 2) / 20)


def test_a_p_value_is_never_above_one_even_on_an_even_split():
    ps = [(True, False)] * 5 + [(False, True)] * 5
    assert exact_paired_test(ps)["p_value"] == 1.0


# --------------------------------------------------------------------------- #
# sensitivity
# --------------------------------------------------------------------------- #


def test_five_or_fewer_discordant_pairs_can_never_reach_significance():
    """A design fact worth knowing before the run: 2 / 2**5 = .0625 > .05."""
    for n in range(1, 6):
        assert min_detectable_split(n) is None
    assert min_detectable_split(6) == 6


def test_the_min_split_is_actually_significant_and_one_less_is_not():
    for n in (6, 8, 10, 20, 40):
        m = min_detectable_split(n)
        assert m is not None
        k = (n - m) // 2
        p = min(1.0, 2.0 * sum(math.comb(n, i) for i in range(k + 1)) / 2.0 ** n)
        assert p < 0.05
        p_less = min(1.0, 2.0 * sum(math.comb(n, i)
                                    for i in range(k + 2)) / 2.0 ** n)
        assert p_less >= 0.05


def test_more_discordant_pairs_never_require_a_wider_split_in_proportion():
    """Monotone in the right direction: the detectable *fraction* shrinks with n."""
    fractions = [min_detectable_split(n) / n for n in (10, 20, 40, 80)]
    assert fractions == sorted(fractions, reverse=True)


# --------------------------------------------------------------------------- #
# the refusals -- the part that matters most
# --------------------------------------------------------------------------- #


def _write(tmp_path, name, rows):
    import json

    d = tmp_path / name
    d.mkdir()
    (d / "extracted.jsonl").write_text(
        "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows),
        encoding="utf-8")
    return d


def test_a_file_mixing_two_conditions_is_refused(tmp_path):
    from rcp.compare import load

    d = _write(tmp_path, "mixed", [
        {"plan": {"scenario_id": "X", "arm": "SUFFICIENT"},
         "trace": {}, "condition": "blind", "domain_digest": "a"},
        {"plan": {"scenario_id": "Y", "arm": "SUFFICIENT"},
         "trace": {}, "condition": "stated", "domain_digest": "b"},
    ])
    with pytest.raises(SystemExit, match="mixes conditions"):
        load(d)


def test_a_file_mixing_two_digests_is_refused(tmp_path):
    from rcp.compare import load

    d = _write(tmp_path, "twodigests", [
        {"plan": {"scenario_id": "X", "arm": "SUFFICIENT"},
         "trace": {}, "condition": "blind", "domain_digest": "a"},
        {"plan": {"scenario_id": "Y", "arm": "SUFFICIENT"},
         "trace": {}, "condition": "blind", "domain_digest": "b"},
    ])
    with pytest.raises(SystemExit, match="domain digests"):
        load(d)


def test_more_than_one_arm_is_refused():
    from rcp.compare import single_arm

    with pytest.raises(SystemExit, match="spans arms"):
        single_arm([_v("A", "SUFFICIENT"), _v("B", "SCARCE")], "--blind")
    assert single_arm([_v("A"), _v("B")], "--blind") == "SUFFICIENT"


def test_an_invariant_violation_suppresses_every_table():
    """`not LEDGER-SATISFIABLE` with `PLAN-SUCCEEDS` is a bug, not a result."""
    from rcp.compare import build

    bad = [_v("A", sat=False, ps=True)]
    rep = build(bad, [_v("A")], provenance={})
    assert rep["suppressed"] is True
    assert rep["invariant_violations"] == ["A/SUFFICIENT"]
    assert "endpoints" not in rep


def test_paired_ci_brackets_the_difference_and_is_zero_width_when_concordant():
    from rcp.compare import paired_ci

    ps = [(False, True)] * 30 + [(True, True)] * 50 + [(True, False)] * 10
    lo, hi = paired_ci(ps)
    assert lo < 20 / 90 < hi
    assert paired_ci([(True, True)] * 10) == (0.0, 0.0)
    assert paired_ci([(True, False)]) is None
