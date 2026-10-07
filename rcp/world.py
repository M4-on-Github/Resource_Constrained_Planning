"""Loads the declared world from data/. plan.md §12.1: registries, not branches.

Every canonical table maps to exactly one file here. A section of plan.md that
restates one of these is a defect; a module that hardcodes one is the same defect
in code.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA = Path(__file__).resolve().parent.parent / "data"


@lru_cache(maxsize=None)
def _load(name: str) -> dict[str, Any]:
    with (DATA / name).open(encoding="utf-8") as fh:
        return json.load(fh)


def requirements() -> dict[str, Any]:
    """plan.md §7.1 — goal, quantity, unit, deadline driver, magnitude bands."""
    return _load("requirements.json")


def assets() -> dict[str, Any]:
    """plan.md §7.2 — the asset type catalogue the generator draws from."""
    return _load("assets.json")


def checks() -> dict[str, Any]:
    """plan.md §4 — the check registry."""
    return _load("checks.json")


def interlocks() -> dict[str, Any]:
    """plan.md §4 V4a/V4b, §12.2 'the interlock set'."""
    return _load("interlocks.json")


def states() -> dict[str, Any]:
    return requirements()["states"]


def goal_vocabulary(casualty_state: str) -> list[str]:
    """V5's closed action vocabulary — the only one in v1.

    plan.md §8.4's coverage gate runs exactly this against the gold plans and
    reports the NO_MATCH rate. A non-trivial rate means the domain is too narrow,
    not that the plans are bad.
    """
    return list(states()[casualty_state]["goal_vocabulary"])


def contributing_types(quantity: str) -> dict[str, dict[str, Any]]:
    """Asset types denominated in `quantity`. plan.md §7.3 invariant 1 falls out."""
    return {k: v for k, v in assets()["types"].items() if v["quantity"] == quantity}


def locations() -> list[str]:
    """Ledger `location` values. Note these are PLACES, not assets — plan.md §6.3's
    named-asset rule exists because they appear in the ledger and V1 string-matches."""
    return list(assets()["locations"])


def distractor_types() -> dict[str, dict[str, Any]]:
    """Types that contribute to no requirement — real assets, wrong scalar."""
    return {k: v for k, v in assets()["types"].items() if v["quantity"] is None}


#: plan.md §7.2. Targets, not realised ratios — see ratio_fleet / ratio_deadline.
ARM_MULTIPLIERS: dict[str, float] = {
    "SURPLUS": 3.0,
    "SUFFICIENT": 1.2,
    "SCARCE": 0.5,
    "INFEASIBLE": 0.25,
}

ARMS = tuple(ARM_MULTIPLIERS)


def unfrozen() -> list[str]:
    """Which data files still carry `frozen: false`. plan.md §12.2."""
    out = []
    for name in ("requirements.json", "assets.json", "checks.json", "interlocks.json"):
        if not _load(name).get("_meta", {}).get("frozen", False):
            out.append(name)
    return out


#: plan.md §7.3 invariant 6. A lean arm builds a ledger to 0.25 x the requirement
#: out of whole assets, so the smallest contributing asset must fit inside that.
GRANULARITY_MULTIPLIER = min(ARM_MULTIPLIERS.values())


def assert_granularity_floor() -> None:
    """plan.md §7.3 invariant 6 — a data admissibility condition, not a code path.

    If the smallest asset denominated in a scalar is larger than the smallest
    shortfall a lean arm has to express, that (state, size, arm) cell cannot be
    built at all: one asset already overshoots. The generator would raise on it
    scenario by scenario; this says so once, at load, naming the fix.
    """
    bad = []
    for state, spec in states().items():
        types = contributing_types(spec["quantity"])
        if not types:
            bad.append(f"{state}: no asset type denominated in {spec['quantity']}")
            continue
        floor = min(v["capability_band"][0] for v in types.values())
        budget = GRANULARITY_MULTIPLIER * min(spec["requirement_band"]["small"])
        if floor > budget:
            bad.append(
                f"{state}: smallest {spec['quantity']} asset is {floor:g} {spec['unit']}, "
                f"but the leanest arm must express {budget:g} — add a smaller asset "
                f"type to data/assets.json or raise requirement_band['small']"
            )
    if bad:
        raise ValueError("granularity floor violated — " + "; ".join(bad))
