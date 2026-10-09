"""Scenario generator. plan.md §7.1–§7.3.

Procedural for all 110 images x 4 arms. Deterministic: the seed is derived from
the image id, so regenerating a corpus from the same manifest gives byte-identical
scenarios. The corpus that ships is nonetheless *read* from data/corpus.jsonl
(rcp.corpus), not rebuilt: Python guarantees `random.random()` across versions but
not `uniform`/`choice`/`sample`/`shuffle`, so regeneration is a check, not the source.

Design points worth knowing before reading:

**The arms are nested.** One chain is built per image, bottom-up, and each arm is
a superset of the one below it:

    INFEASIBLE = on-time O1 (~0.25x) + late L1 + distractors
    SCARCE     = INFEASIBLE + O2       (on-time to ~0.5x)
    SUFFICIENT = SCARCE + O3 + L2      (on-time to ~1.2x, more late capability)
    SURPLUS    = SUFFICIENT + O4       (on-time to ~3.0x)

So "SCARCE removes TUG-011 and TUG-005" (plan.md §7.2) is literally true: an asset
present in two arms is the same row with the same ID, location and ETA, and the
difference between two arms of one image is the manipulation and nothing else.
The four arms are accepted or redrawn *together*.

**Scarcity varies asset COUNT, not per-asset capability.** §7.1 accepts the
consequence by requiring asset count be recorded and reported as a covariate.

**The arm multiplier defines ratio_deadline, not ratio_fleet.** The arm is a claim
about what the planner can actually assemble, so the multiplier sizes the *on-time*
capability. Late assets are extras on top of it. Lean arms additionally keep the
whole fleet below the requirement, so they are short however the planner counts.

**ETA comes from geography.** Each chain gets three fictional ports at fixed
distances (near / mid / far), shared by its four arms. An asset at a port has
`eta = mobilisation + distance / speed` for its type; a floating asset may instead
be underway at sea at a stated distance. Location therefore means something, and
two assets at one port differ only by type. (Previously location was drawn
independently of ETA: docs/corpus_realism.md §1.)

**Nothing sits at the deadline.** Every ETA is at least DEADLINE_MARGIN away from
it, either side, so whether an asset is on time is never decided by rounding.

**Every ledger carries late contributing assets.** Two reasons:

  (i) When late assets appeared only in trap cells, "this ledger contains a far-away
      ETA" was a perfect predictor of "this ledger is unsatisfiable" across all 440
      cells. Late assets everywhere removes the cue.
 (ii) V2a is a primary check. In a ledger where everything arrives on time it passes
      vacuously. With late assets everywhere, a V2a failure is the planner's own.

**Every capsized/sunken ledger carries divers, every on_fire one a dewatering
pump** (data/requirements.json `enabling_kit`). They count toward no scalar, so the
arm ratios are untouched; they exist so that a planner who needs divers to rig a
hull is not pushed into escalating on a satisfiable ledger (corpus_realism §2).

**The OVERCOMMIT trap is not built in v1.** Nested arms leave no place for it: a
trap needs a SUFFICIENT-level fleet with a short on-time subset, which is not a
superset of SCARCE. v2 reintroduces it as a separate arm. `is_trap` stays on the
Scenario, always False, so the downstream code and the v2 path are unchanged.

**The arm bands are enforced, not hoped for.** Whole-asset granularity means a
ledger built to a target overshoots it. `build_chain` therefore rejection-samples
the whole chain and raises if the attempt budget runs out: a silently off-arm
scenario is the one defect that would survive into the results as a finding.
"""

from __future__ import annotations

import csv
import dataclasses
import functools
import hashlib
import math
import pathlib
import random

from .normalize import assert_ids_distinct
from .schema import Asset, Requirement, Scenario
from .validator import (
    MAX_LEDGER_FOR_ENUMERATION,
    eligible_assets,
    ledger_satisfiable,
    ratio_deadline,
    ratio_fleet,
)
from .world import (
    ARM_MULTIPLIERS,
    assets,
    contributing_types,
    distractor_types,
    enabling_kit,
    geography,
    ports,
    states,
)

#: Kept for the downstream code that reads it; nested arms build no trap (above).
TRAP_FRACTION = 0.0

#: Late capability as a fraction of the requirement (abundant arms) or of the
#: headroom left below it (lean arms). Gives V2a teeth in all four arms.
LATE_SHARE_BAND = (0.30, 0.80)

#: Lean arms must keep ratio_fleet < 1, so their late extras are sized against
#: this fraction of the requirement minus SCARCE's on-time target.
LEAN_FLEET_HEADROOM = 0.95

#: How many contributing assets a SUFFICIENT ledger should hold. Sets the asset
#: "size" for the scenario, which then fixes counts in the other arms.
CONTRIB_AT_SUFFICIENT = 3

#: Per-fill stop, and the cap on the on-time pool (the validator enumerates it).
MAX_CONTRIBUTING = 10
MAX_ELIGIBLE = MAX_LEDGER_FOR_ENUMERATION

#: Share of picks that take any type fitting the remaining target rather than the
#: nearest-sized one (_pick_type).
TYPE_EXPLORE = 0.25
TYPE_EXPLORE_OVERSHOOT = 1.5

#: Random distractors on top of the enabling kit.
DISTRACTORS = (1, 2)

#: No ETA within max(0.3 h, 5 % of the deadline) of the deadline, either side.
DEADLINE_MARGIN_H = 0.3
DEADLINE_MARGIN_FRAC = 0.05

#: ID numbers are drawn from 1..ID_NUMBER_MAX per prefix.
ID_NUMBER_MAX = 60

#: Rejection-sampling budget per image (the whole four-arm chain).
MAX_ATTEMPTS = 400

#: How far a realised ratio may sit from the arm multiplier. One-sided, as before:
#: the abundant arms must stay satisfiable, the lean arms must stay short.
ABUNDANT_RATIO_CEILING = 1.5   # x the multiplier
LEAN_RATIO_FLOOR = 0.55        # x the multiplier
#: SURPLUS must actually add on-time capability over SUFFICIENT. Without a floor
#: an image whose deadline admits only small assets fills the eligible budget at
#: SUFFICIENT and ships a SURPLUS ledger identical to it.
ABUNDANT_RATIO_FLOOR = 0.67    # x the multiplier, and never below 1.0

#: Bottom-up build order. Each arm is a superset of the one before it.
CHAIN = ("INFEASIBLE", "SCARCE", "SUFFICIENT", "SURPLUS")


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


def deadline_margin(deadline_h: float) -> float:
    return max(DEADLINE_MARGIN_H, DEADLINE_MARGIN_FRAC * deadline_h)


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


def make_geography(image_id: str, attempt: int = 0) -> tuple[tuple[str, int], ...]:
    """Three fictional ports, one per distance tier, shared by one chain's four arms.

    Redrawn per chain attempt, not fixed per image: a long-deadline image whose far
    port happens to be close can place a late asset only by picking a slow,
    oversized type, which pushes the lean arms' whole fleet past the requirement.
    """
    rng = _rng(image_id, f"geo|{attempt}")
    tiers = geography()["port_tiers_nm"]
    names = rng.sample(ports(), len(tiers))
    return tuple((n, rng.randint(lo, hi)) for n, (lo, hi) in zip(names, tiers))


# --------------------------------------------------------------------------- #
# One asset
# --------------------------------------------------------------------------- #


def _windows(tspec: dict, geo: tuple[tuple[str, int], ...], *, late: bool,
             deadline_h: float) -> list[tuple[str | None, int | None, float, float]]:
    """Where this type can be placed so its ETA falls on the right side of the
    deadline: (port or None for underway, distance, eta_lo, eta_hi), with the eta
    bounds already on the 0.1 h grid the ledger prints."""
    m = deadline_margin(deadline_h)
    role_lo, role_hi = (deadline_h + m, math.inf) if late else (0.0, deadline_h - m)
    v = tspec["speed_kn"]
    m_lo, m_hi = tspec["mobilise_h"]
    cands: list[tuple[str | None, int | None, float, float]] = []
    for name, nm in geo:
        cands.append((name, nm, m_lo + nm / v, m_hi + nm / v))
    if tspec["floating"]:
        g = geography()
        d_lo, d_hi = g["underway_nm"]
        s = g["underway_setup_h"]
        cands.append((None, None, s + d_lo / v, s + d_hi / v))
    out = []
    for name, nm, lo, hi in cands:
        lo = math.ceil(max(lo, role_lo) * 10 - 1e-9) / 10
        hi = math.floor(min(hi, role_hi) * 10 + 1e-9) / 10
        if lo <= hi:
            out.append((name, nm, lo, hi))
    return out


def _draw(tname: str, tspec: dict, want: float, rng: random.Random, *, late: bool,
          deadline_h: float, geo: tuple[tuple[str, int], ...]) -> Asset | None:
    """One asset of type `tname`, or None if the type cannot be on the required
    side of the deadline from anywhere in this image's geography. The ID is a
    placeholder; `_assign_ids` numbers the finished chain."""
    wins = _windows(tspec, geo, late=late, deadline_h=deadline_h)
    if not wins:
        return None
    name, nm, lo, hi = rng.choice(wins)
    eta = round(rng.uniform(lo, hi), 1)
    if name is None:
        g = geography()
        nm = max(g["underway_nm"][0], round((eta - g["underway_setup_h"]) * tspec["speed_kn"]))
        location = f"underway, {nm} nm"
    else:
        location = f"{name}, {nm} nm"
    lo_c, hi_c = tspec["capability_band"]
    cap = _round_amount(min(hi_c, max(lo_c, want * rng.uniform(0.85, 1.15))))
    return Asset(id=f"{tspec['prefix']}-?", type=tname, label=tspec["label"],
                 capability=cap, unit=tspec["unit"], location=location,
                 eta_hours=eta, quantity=tspec["quantity"])


def _pick_type(quantity: str, want: float, remaining: float, rng: random.Random, *,
               late: bool, deadline_h: float, geo) -> tuple[str, dict] | None:
    """Usually the placeable type whose capability band sits closest to `want`.

    With probability TYPE_EXPLORE, instead any placeable type whose smallest unit
    is within TYPE_EXPLORE_OVERSHOOT of the remaining target (the arm bands, not
    this, decide whether the overshoot is acceptable). Without that, a short deadline that admits only one small
    type on time plus one large type underway always picks the small one and can
    never reach SURPLUS (a 9 200 t.m righting job by 6.6 h is 35 winch sets).
    """
    cands = {k: v for k, v in contributing_types(quantity).items()
             if _windows(v, geo, late=late, deadline_h=deadline_h)}
    if not cands:
        return None
    fits = [c for c in cands.items()
            if c[1]["capability_band"][0] <= remaining * TYPE_EXPLORE_OVERSHOOT + 1e-9]
    if fits and rng.random() < TYPE_EXPLORE:
        return rng.choice(sorted(fits))

    def distance(item: tuple[str, dict]) -> float:
        lo, hi = item[1]["capability_band"]
        if lo <= want <= hi:
            return 0.0
        return min(abs(want - lo), abs(want - hi))
    ranked = sorted(cands.items(), key=distance)
    best = distance(ranked[0])
    tied = [c for c in ranked if distance(c) <= best + 1e-9]
    return rng.choice(tied)


def _fill_to(target: float, req: Requirement, rng: random.Random, *, late: bool,
             unit_size: float, geo, max_n: int = MAX_CONTRIBUTING) -> list[Asset]:
    """Draw whole assets until their capability reaches `target`.

    The last asset is sized to the *remainder*, and its type chosen for the
    remainder too, or a ledger built to 0.5x routinely lands above 1.0x.
    """
    out: list[Asset] = []
    total = 0.0
    while total < target - 1e-9 and len(out) < max_n:
        want = min(unit_size, target - total)
        picked = _pick_type(req.quantity, want, target - total, rng, late=late,
                            deadline_h=req.deadline_h, geo=geo)
        if picked is None:
            break
        a = _draw(*picked, want, rng, late=late, deadline_h=req.deadline_h, geo=geo)
        out.append(a)
        total += a.capability
    return out


def _cap(rows: list[Asset]) -> float:
    return sum(a.capability for a in rows)


# --------------------------------------------------------------------------- #
# One chain = one image's four arms
# --------------------------------------------------------------------------- #


def _accepts(arm: str, r_fleet: float, r_deadline: float, sat: bool,
             has_late: bool) -> bool:
    """The arm's acceptance predicate — plan.md §7.3 invariant 2 as code.

    tests/ asserts the same statements independently against the finished
    corpus, so a loosening here does not quietly loosen the test.
    """
    mult = ARM_MULTIPLIERS[arm]
    if not has_late:
        return False  # V2a would be vacuous here; see the module docstring
    if mult > 1.0:
        floor = max(1.0, mult * ABUNDANT_RATIO_FLOOR)
        return sat and floor <= r_deadline <= mult * ABUNDANT_RATIO_CEILING
    return not sat and mult * LEAN_RATIO_FLOOR <= r_fleet < 1.0


def _distractors(state: str, req: Requirement, rng: random.Random, geo) -> list[Asset]:
    kit = enabling_kit(state)
    pool = distractor_types()
    out: list[Asset] = []
    names = [kit] if kit else []
    others = [k for k in pool if k != kit]
    names += rng.sample(others, rng.randint(*DISTRACTORS))
    for name in names:
        spec = pool[name]
        a = _draw(name, spec, sum(spec["capability_band"]) / 2, rng, late=False,
                  deadline_h=req.deadline_h, geo=geo)
        if a is None and name == kit:
            raise ValueError(f"{state}: enabling kit {kit!r} cannot arrive by "
                             f"{req.deadline_h} h from any port - fix data/assets.json")
        if a is not None:
            out.append(a)
    return out


def _assign_ids(rows: list[Asset], rng: random.Random) -> list[Asset]:
    """Number the SURPLUS ledger once; every smaller arm keeps the same IDs.

    Numbers are sampled, not counted, so a nested arm's gaps look like any other
    ledger's and do not reveal how much was taken away.
    """
    prefix = {k: v["prefix"] for k, v in assets()["types"].items()}
    by_prefix: dict[str, list[int]] = {}
    for a in rows:
        by_prefix.setdefault(prefix[a.type], []).append(0)
    numbers = {p: rng.sample(range(1, ID_NUMBER_MAX + 1), len(v)) for p, v in by_prefix.items()}
    out = []
    for a in rows:
        n = numbers[prefix[a.type]].pop()
        out.append(dataclasses.replace(a, id=f"{prefix[a.type]}-{n:03d}"))
    return out


def _build_chain(req: Requirement, state: str, rng: random.Random,
                 geo) -> dict[str, tuple[Asset, ...]]:
    m = ARM_MULTIPLIERS
    amount = req.amount
    unit = _round_amount(amount * 1.2 / CONTRIB_AT_SUFFICIENT)
    fill = functools.partial(_fill_to, req=req, rng=rng, unit_size=unit, geo=geo)

    o1 = fill(amount * m["INFEASIBLE"], late=False)
    l1 = fill((LEAN_FLEET_HEADROOM - m["SCARCE"]) * amount
              * rng.uniform(*LATE_SHARE_BAND), late=True)
    o2 = fill(amount * m["SCARCE"] - _cap(o1), late=False)
    o3 = fill(amount * m["SUFFICIENT"] - _cap(o1 + o2), late=False)
    # Relative to the REQUIREMENT: scaling off the on-time total would make
    # ledger length covary even harder with the arm (plan.md 7.1).
    l2 = fill(max(0.0, amount * rng.uniform(*LATE_SHARE_BAND) - _cap(l1)), late=True)
    on_time = o1 + o2 + o3
    o4 = fill(amount * m["SURPLUS"] - _cap(on_time), late=False,
              max_n=max(0, min(MAX_CONTRIBUTING, MAX_ELIGIBLE - len(on_time))))
    dis = _distractors(state, req, rng, geo)

    layers = {"INFEASIBLE": o1 + l1 + dis, "SCARCE": o2,
              "SUFFICIENT": o3 + l2, "SURPLUS": o4}
    tier = {}
    for i, arm in enumerate(CHAIN):
        for a in layers[arm]:
            tier[id(a)] = i
    full = [a for arm in CHAIN for a in layers[arm]]
    rng.shuffle(full)
    tiers = [tier[id(a)] for a in full]
    full = _assign_ids(full, rng)
    return {arm: tuple(a for a, t in zip(full, tiers) if t <= i)
            for i, arm in enumerate(CHAIN)}


@functools.lru_cache(maxsize=None)
def build_chain(image_id: str, casualty_state: str,
                size_category: str) -> tuple[Scenario, ...]:
    """All four arms of one image, in ARM_MULTIPLIERS order, accepted together."""
    req = make_requirement(image_id, casualty_state, size_category)

    for attempt in range(MAX_ATTEMPTS):
        rng = _rng(image_id, f"chain|{attempt}")
        geo = make_geography(image_id, attempt)
        ledgers = _build_chain(req, casualty_state, rng, geo)
        built = []
        for arm in ARM_MULTIPLIERS:
            ledger = ledgers[arm]
            assert_ids_distinct([a.id for a in ledger])
            r_fleet = round(ratio_fleet(req, ledger), 3)
            r_deadline = round(ratio_deadline(req, ledger), 3)
            if len(eligible_assets(req, ledger)) > MAX_ELIGIBLE:
                break
            sat = ledger_satisfiable(req, ledger)
            has_late = any(a.counts_toward(req) and not a.arrives_by(req.deadline_h)
                           for a in ledger)
            if not _accepts(arm, r_fleet, r_deadline, sat, has_late):
                break
            built.append(Scenario(
                id=image_id, arm=arm, casualty_state=casualty_state,
                size_category=size_category, requirement=req, ledger=ledger,
                is_trap=False, ratio_fleet=r_fleet, ratio_deadline=r_deadline,
                ledger_satisfiable=sat, seed=attempt,
            ))
        else:
            return tuple(built)

    raise RuntimeError(
        f"{image_id}: no four-arm chain met the arm bands in {MAX_ATTEMPTS} draws "
        f"(requirement {req.amount:g} {req.unit} by {req.deadline_h} h). The asset "
        "catalogue cannot express this image at this magnitude — fix "
        "data/assets.json or the magnitude band, do not relax the band."
    )


def build_scenario(image_id: str, casualty_state: str, size_category: str,
                   arm: str) -> Scenario:
    chain = build_chain(image_id, casualty_state, size_category)
    return chain[list(ARM_MULTIPLIERS).index(arm)]


def build_corpus(manifest: list[tuple[str, str, str]]) -> list[Scenario]:
    """One Scenario per (image, arm). `manifest` is (image_id, state, size).

    This *generates*. The study reads the frozen copy: `rcp.corpus.load()`.
    """
    return [sc for iid, state, size in manifest
            for sc in build_chain(iid, state, size)]


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
