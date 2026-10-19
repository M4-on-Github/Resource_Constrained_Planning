"""tools/d14.py: the exact binomial helpers, the split's allocation, and kappa."""

from __future__ import annotations

import pytest

from tools.d14 import DEV_IMAGES, exact_ci, kappa, smallest_detectable, split_text


@pytest.mark.parametrize("x,n,lo,hi", [
    (0, 10, 0.0, 0.3085),       # Clopper-Pearson, standard table values
    (1, 36, 0.0007, 0.1453),
    (5, 16, 0.1102, 0.5866),
    (10, 10, 0.6915, 1.0),
])
def test_exact_ci_matches_clopper_pearson(x, n, lo, hi):
    got = exact_ci(x, n)
    assert got == pytest.approx((lo, hi), abs=5e-4)


def test_smallest_detectable_matches_plan_md_for_a_zero_null():
    # plan.md §9.4: "against a literal π = 0 the MDE is 0.015" at n = 110
    assert smallest_detectable(110, 0.0) == pytest.approx(0.015, abs=5e-4)


def test_smallest_detectable_rises_with_the_null():
    assert smallest_detectable(110, 0.1) < smallest_detectable(110, 0.3) < 1


def test_split_is_stratified_and_sized():
    rows = [ln.split(",") for ln in split_text().splitlines()[1:]]
    assert sum(r[2] == "dev" for r in rows) == DEV_IMAGES
    assert len(rows) == 110
    dev = {s: sum(r[1] == s and r[2] == "dev" for r in rows) for s in {r[1] for r in rows}}
    assert dev == {"aground": 15, "sunken": 12, "capsized": 7, "on_fire": 6}


def test_kappa():
    assert kappa(["yes", "no"] * 5, ["yes", "no"] * 5) == 1.0
    assert kappa(["yes", "no", "yes", "no"], ["no", "yes", "no", "yes"]) == -1.0
