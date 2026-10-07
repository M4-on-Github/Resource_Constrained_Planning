"""Scenario generator. plan.md §7.1–§7.3.

Procedural for all 110 images x 4 arms. Deterministic: the seed is derived from
the image id, so regenerating a corpus from the same manifest gives byte-identical
scenarios.

Two design points worth knowing before reading:

**Scarcity varies asset COUNT, not per-asset capability.** plan.md §7.2's own
worked example does this ("SCARCE removes TUG-011 and TUG-005"), and §7.1 accepts
the consequence by requiring asset count be recorded and reported as a covariate.
The alternative — fixed count, weaker assets — would hold cardinality constant but
depart from the document.

**The arm multiplier defines ratio_deadline, not ratio_fleet.** The arm is a claim
about what the planner can actually assemble, so the multiplier sizes the *on-time*
capability. Late assets are extras on top of it. plan.md §7.3 invariant 2 already
states arm fidelity against ratio_deadline; this makes the generator agree.

**Every ledger carries late contributing assets.** Not only the trap ones. Two
reasons, and the first is a validity bug found in Phase A:

  (i) When late assets appeared only in trap cells, "this ledger contains a far-away
      ETA" was a perfect predictor of "this ledger is unsatisfiable" across all 440
      cells. A planner could have scored the manipulation from a surface cue without
      doing any arithmetic. Late assets everywhere removes the cue.
 (ii) V2a is a primary check. In a ledger where everything arrives on time it passes
      vacuously, so without late assets somewhere in every ledger, one of the four
      primary checks can never fail. With them, a V2a failure is unambiguous: the
      stimulus never forces it, so it is always the planner's own error.

**The OVERCOMMIT trap is deferred to v2 (TRAP_FRACTION = 0).** The machinery below
is intact and tested; only the rate is zero. In v1 both abundant arms are 110/110
satisfiable, which is what makes SURPLUS a clean ceiling condition and the positive
control non-vacuous. Turning the trap on is a one-constant change, and it belongs
in SUFFICIENT — where "just enough on paper" makes reading the ETA load-bearing —
not in SURPLUS, whose job is to be the arm with no excuses.

**The arm bands are enforced, not hoped for.** Whole-asset granularity means a
ledger built to a target overshoots it, sometimes by enough to make a SCARCE
ledger satisfiable. `build_scenario` therefore rejection-samples: it builds a
ledger, tests it against the arm's acceptance predicate, and redraws until it
passes or the attempt budget runs out — in which case it raises. A silently
off-arm scenario is the one defect that would survive into the results as a
finding (plan.md §7.3), so it fails loudly here instead.
"""

from __future__ import annotations

import csv
import hashlib
import pathlib
import random

from .normalize import assert_ids_distinct
from .schema import Asset, Requirement, Scenario
from .validator import ledger_satisfiable, ratio_deadline, ratio_fleet
from .world import (
    ARM_MULTIPLIERS,
    contributing_types,
    distractor_types,
    locations,
    states,
)

#: Fraction of images carrying the OVERCOMMIT trap. **Zero in v1** — the trap is a
#: deferred manipulation, see the module docstring. plan.md §7.2's IMG-042 is a trap
#: scenario (fleet 1.2x, deadline 0.79x) and remains the worked example for v2.
TRAP_FRACTION = 0.0

#: Arms a trap can be set in: those whose multiplier exceeds 1. SCARCE and INFEASIBLE
#: deny `ratio_fleet > 1`, so a trap there is unsatisfiable for the ordinary reason
#: and indistinguishable from the arm itself.
TRAPPABLE_ARMS = tuple(a for a, m in ARM_MULTIPLIERS.items() if m > 1.0)

#: Late capability added to every ledger, as a fraction of what arrives on time
#: (abundant arms) or of the headroom left below the requirement (lean arms).
#: Gives V2a teeth in all four arms without changing any arm's ratio_deadline.
LATE_SHARE_BAND = (0.30, 0.80)

#: Lean arms must keep ratio_fleet < 1, so late extras are capped below the
#: requirement rather than measured against the on-time total.
LEAN_FLEET_HEADROOM = 0.95

#: A trap's by-deadline total, as a fraction of the requirement. Must stay < 1/1.2
#: so that a trap at SUFFICIENT is genuinely short.
TRAP_SHORTFALL_BAND = (0.70, 0.95)

#: How many contributing assets a SUFFICIENT ledger should hold. Sets the asset
#: "size" for the scenario, which then fixes counts in the other arms.
CONTRIB_AT_SUFFICIENT = 3

#: Hard stop. The eligible pool drives subset enumeration (validator caps at 14).
MAX_CONTRIBUTING = 10
DISTRACTORS = (1, 2)

#: Rejection-sampling budget per (image, arm). Generous: a rejected draw costs
#: microseconds, and exhausting it means the arm band is unachievable for this
#: requirement magnitude, which is a data problem to surface, not to average over.
MAX_ATTEMPTS = 400

#: How far a realised ratio may sit from the arm multiplier. The abundant arms
#: only need an upper bound (they must stay satisfiable); the lean arms only need
#: a lower one (they must stay short). Both are one-sided for that reason.
ABUNDANT_RATIO_CEILING = 1.5   # x the multiplier
LEAN_RATIO_FLOOR = 0.55        # x the multiplier


def _rng(image_id: str, salt: str = "") -> random.Random:
    digest = hashlib.sha256(f"{image_id}|{salt}".encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def _round_amount(x: float) -> float:
    """Keep magnitudes legible — a requirement reads as a figure, not a float."""
    if x >= 1000:
        return round(x / 100) * 100
    if x >= 100:
        return round(x / 10) * 10
    return round(x)


def make_requirement(image_id: str, casualty_state: str, size_category: str) -> Requirement:
    spec = states()[casualty_state]
    rng = _rng(image_id, "req")
    lo, hi = spec["requirement_band"][size_category]
    d_lo, d_hi = spec["deadline_band_h"]
    return Requirement(
        goal=spec["goal"],
        quantity=spec["quantity"],
        unit=spec["unit"],
        amount=_round_amount(rng.uniform(lo, hi)),
        deadline_h=round(rng.uniform(d_lo, d_hi), 1),
        deadline_driver=spec["deadline_driver"],
    )


def _pick_type(quantity: str, want: float, rng: random.Random) -> tuple[str, dict]:
    """Choose an asset type whose capability band sits closest to `want`."""
    cands = contributing_types(quantity)
    def distance(item: tuple[str, dict]) -> float:
        lo, hi = item[1]["capability_band"]
        if lo <= want <= hi:
            return 0.0
        return min(abs(want - lo), abs(want - hi))
    ranked = sorted(cands.items(), key=distance)
    best = distance(ranked[0])
    tied = [c for c in ranked if distance(c) <= best + 1e-9]
    return rng.choice(tied)


def _draw(tname: str, tspec: dict, want: float, rng: random.Random, *, late: bool,
          deadline_h: float, counter: dict[str, int]) -> Asset:
    lo, hi = tspec["capability_band"]
    cap = _round_amount(min(hi, max(lo, want * rng.uniform(0.85, 1.15))))
    e_lo, e_hi = tspec["eta_band_h"]
    if late:
        eta = round(max(deadline_h + 0.3, rng.uniform(deadline_h + 0.3, max(e_hi, deadline_h * 1.8))), 1)
    else:
        eta = round(rng.uniform(e_lo, min(e_hi, deadline_h)), 1) if e_lo <= deadline_h \
            else round(deadline_h * rng.uniform(0.3, 0.9), 1)
    prefix = {"bollard_pull": "TUG", "lift_capacity": "LFT",
              "righting_moment": "RGT", "water_delivery": "FFP"}.get(tspec["quantity"], "AST")
    if tname == "beach_gear_set":
        prefix = "BG"
    counter[prefix] = counter.get(prefix, 0) + 1
    return Asset(
        id=f"{prefix}-{counter[prefix]:03d}",
        type=tname,
        label=tspec["label"],
        capability=cap,
        unit=tspec["unit"],
        location=rng.choice(locations()),
        eta_hours=eta,
        quantity=tspec["quantity"],
    )


def _fill_to(target: float, req: Requirement, rng: random.Random, *, late: bool,
             counter: dict[str, int], unit_size: float) -> list[Asset]:
    """Draw whole assets until their capability reaches `target`.

    The last asset is sized to the *remainder*, not to `unit_size`, and its type
    is chosen for the remainder too. Without that, a ledger built to 0.5x
    routinely lands above 1.0x, because a type's capability_band floor can sit
    well above what is still needed — which is how a SCARCE arm ends up
    satisfiable (plan.md §7.3 invariant 2).
    """
    out: list[Asset] = []
    total = 0.0
    while total < target - 1e-9 and len(out) < MAX_CONTRIBUTING:
        want = min(unit_size, target - total)
        tname, tspec = _pick_type(req.quantity, want, rng)
        a = _draw(tname, tspec, want, rng, late=late,
                  deadline_h=req.deadline_h, counter=counter)
        out.append(a)
        total += a.capability
    return out


def _accepts(arm: str, is_trap: bool, r_fleet: float, r_deadline: float,
             sat: bool, has_late: bool) -> bool:
    """The arm's acceptance predicate — plan.md §7.3 invariants 2 and 3 as code.

    This is the only place the invariants are *enforced*; tests/ asserts the same
    statements independently against the finished corpus, so a loosening here
    does not quietly loosen the test.
    """
    mult = ARM_MULTIPLIERS[arm]
    if not has_late:
        return False  # V2a would be vacuous here; see the module docstring
    if is_trap:
        # invariant 3: the fleet clears the bar, the assemblable subset does not.
        return r_fleet > 1.0 >= r_deadline and not sat
    if mult > 1.0:
        # invariant 4's precondition: a valid plan must exist.
        return sat and 1.0 <= r_deadline <= mult * ABUNDANT_RATIO_CEILING
    # lean arms: short in fleet terms, so short however the planner assembles it.
    return not sat and mult * LEAN_RATIO_FLOOR <= r_fleet < 1.0


def _build_ledger(req: Requirement, arm: str, is_trap: bool,
                  rng: random.Random) -> tuple[Asset, ...]:
    mult = ARM_MULTIPLIERS[arm]
    unit_size = _round_amount(req.amount * 1.2 / CONTRIB_AT_SUFFICIENT)
    counter: dict[str, int] = {}

    if is_trap:
        # Deferred to v2. The on-time portion deliberately falls short while the
        # fleet total clears the requirement.
        on_time = _fill_to(req.amount * rng.uniform(*TRAP_SHORTFALL_BAND), req, rng,
                           late=False, counter=counter, unit_size=unit_size)
        have = sum(a.capability for a in on_time)
        late_target = max(req.amount * mult, req.amount * 1.05) - have
    else:
        # The arm multiplier sizes the ON-TIME capability (= ratio_deadline).
        on_time = _fill_to(req.amount * mult, req, rng, late=False,
                           counter=counter, unit_size=unit_size)
        have = sum(a.capability for a in on_time)
        share = rng.uniform(*LATE_SHARE_BAND)
        if mult > 1.0:
            # Relative to the REQUIREMENT, not to the on-time total: scaling off
            # `have` would multiply SURPLUS's row count by its own multiplier and
            # make ledger length covary even harder with the arm (plan.md 7.1).
            late_target = req.amount * share
        else:
            # Lean arms: stay below the requirement even counting the late rows.
            late_target = max(0.0, req.amount * LEAN_FLEET_HEADROOM - have) * share

    late_assets = _fill_to(late_target, req, rng, late=True, counter=counter,
                           unit_size=unit_size)
    contributing = on_time + late_assets

    ledger = list(contributing)
    for _ in range(rng.randint(*DISTRACTORS)):
        dname, dspec = rng.choice(list(distractor_types().items()))
        ledger.append(_draw(dname, dspec, sum(dspec["capability_band"]) / 2, rng,
                            late=False, deadline_h=req.deadline_h, counter=counter))

    rng.shuffle(ledger)
    return tuple(ledger)


def build_scenario(image_id: str, casualty_state: str, size_category: str,
                   arm: str) -> Scenario:
    req = make_requirement(image_id, casualty_state, size_category)
    is_trap = (arm in TRAPPABLE_ARMS
               and _rng(image_id, "trap").random() < TRAP_FRACTION)

    for attempt in range(MAX_ATTEMPTS):
        rng = _rng(image_id, f"ledger|{arm}|{attempt}")
        ledger = _build_ledger(req, arm, is_trap, rng)
        assert_ids_distinct([a.id for a in ledger])
        r_fleet = round(ratio_fleet(req, ledger), 3)
        r_deadline = round(ratio_deadline(req, ledger), 3)
        sat = ledger_satisfiable(req, ledger)
        has_late = any(a.counts_toward(req) and not a.arrives_by(req.deadline_h)
                       for a in ledger)
        if _accepts(arm, is_trap, r_fleet, r_deadline, sat, has_late):
            return Scenario(
                id=image_id, arm=arm, casualty_state=casualty_state,
                size_category=size_category, requirement=req, ledger=ledger,
                is_trap=is_trap, ratio_fleet=r_fleet, ratio_deadline=r_deadline,
                ledger_satisfiable=sat, seed=attempt,
            )

    raise RuntimeError(
        f"{image_id}/{arm}: no ledger met the arm band in {MAX_ATTEMPTS} draws "
        f"(requirement {req.amount:g} {req.unit}, trap={is_trap}). The asset "
        "catalogue cannot express this arm at this magnitude — fix data/assets.json "
        "or the magnitude band, do not relax the band."
    )


def build_corpus(manifest: list[tuple[str, str, str]]) -> list[Scenario]:
    """One Scenario per (image, arm). `manifest` is (image_id, state, size)."""
    return [
        build_scenario(iid, state, size, arm)
        for iid, state, size in manifest
        for arm in ARM_MULTIPLIERS
    ]


MANIFEST = pathlib.Path(__file__).resolve().parent.parent / "data" / "manifest.csv"


def manifest() -> list[tuple[str, str, str]]:
    """The real CASTOR manifest: 110 images, (id, state, size_category).

    Both fields are human labels, carried over verbatim by tools/build_manifest.py
    from Eval_CASTOR's human_gt.csv — the casualty state and the vessel size
    estimate. Nothing here is inferred, which is what lets §7.1's requirement be
    called visually grounded: the planner can see the size the band was drawn
    from.

    data/manifest.csv is committed, so a corpus is reproducible from this repo
    alone with no path to Eval_CASTOR at generation time.
    """
    with MANIFEST.open(encoding="utf-8", newline="") as fh:
        rows = [(r["id"], r["state"], r["size_category"]) for r in csv.DictReader(fh)]
    counts: dict[str, int] = {}
    for _, state, _ in rows:
        counts[state] = counts.get(state, 0) + 1
    expected = {s: spec["n"] for s, spec in states().items()}
    if counts != expected:
        raise ValueError(
            f"manifest state counts {counts} != plan.md 7.1 {expected} — "
            "rerun tools/build_manifest.py")
    return rows


def manifest_images() -> dict[str, str]:
    """`{scenario id: image path relative to the sorted_images root}`.

    A separate reader rather than a fourth element on `manifest()`, so the
    generator's signature and every test against it stay as they were: ledger
    construction has no business knowing where a JPEG lives. Only the planner
    (`rcp.infer`) opens the file.

    The path is carried verbatim from human_gt (`aground/00017.jpg`) rather than
    rebuilt from the id, which has dropped the extension.
    """
    with MANIFEST.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if rows and "image" not in rows[0]:
        raise ValueError(
            "data/manifest.csv has no `image` column — rerun tools/build_manifest.py")
    return {r["id"]: r["image"] for r in rows}


def synthetic_manifest() -> list[tuple[str, str, str]]:
    """A stand-in manifest matching plan.md §7.1's n per state (42/33/19/16).

    Superseded by `manifest()` for the real corpus. Kept because the validator's
    equivalence digest (tests/validator_baseline.sha256) is pinned against a
    corpus that must not move when the manifest or the requirement bands are
    revised — the digest is a claim about the validator, not about the stimulus.
    """
    sizes = ["small", "medium", "large"]
    out: list[tuple[str, str, str]] = []
    for state, spec in states().items():
        for i in range(spec["n"]):
            rng = _rng(f"{state}-{i:03d}", "size")
            out.append((f"{state.upper()[:3]}-{i:03d}", state, rng.choice(sizes)))
    return out
