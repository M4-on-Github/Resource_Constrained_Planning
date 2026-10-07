"""The validator. Pure, deterministic, and it never sees prose.

plan.md §4 is the canonical registry; this module implements it and nothing else.
The exactness claim of §3.6 claim 1 rests on this boundary: everything here is
arithmetic over a symbol set produced upstream by the extractor.
"""

from __future__ import annotations

from itertools import combinations

from . import flags
from .normalize import resolve
from .schema import (
    Allocation,
    Asset,
    CheckResult,
    ExtractedPlan,
    Requirement,
    Scenario,
    Verdict,
)

# --------------------------------------------------------------------------- #
# LEDGER-SATISFIABLE  (plan.md §7.3)
# --------------------------------------------------------------------------- #


def eligible_assets(req: Requirement, ledger: tuple[Asset, ...]) -> list[Asset]:
    """Assets that could contribute to a valid plan: right scalar, arrive in time."""
    return [a for a in ledger if a.counts_toward(req) and a.arrives_by(req.deadline_h)]


def ledger_satisfiable(req: Requirement, ledger: tuple[Asset, ...]) -> bool:
    """Does SOME subset of the ledger satisfy RESOURCE-VALID (V1 ∧ V2a ∧ V3)?

    plan.md §7.3 specifies exhaustive subset enumeration — "at most 64 subsets:
    exhaustive and exact, no heuristic." This is that enumeration.

    It is *provably equal* to `sum(eligible) >= amount` in v1, because the v1
    constraint set is monotone: every asset is either eligible or not, V1 and V2a
    are satisfied by construction over an eligible subset, and V3 is a sum that
    only grows. `test_satisfiable_enumeration_equals_monotone_sum` asserts the
    equality on random ledgers.

    The enumeration is kept anyway, because the equality is a property of v1's
    single monotone scalar and does not survive a second scalar, a conflicting
    constraint, or an asset that can only serve one of two roles (see
    archive/casualty_tree.md). Replacing it with the shortcut would make a later
    extension silently wrong rather than loudly slow.
    """
    pool = eligible_assets(req, ledger)
    if len(pool) > MAX_LEDGER_FOR_ENUMERATION:
        raise ValueError(
            f"{len(pool)} eligible assets: subset enumeration is no longer "
            f"exhaustive within budget (cap {MAX_LEDGER_FOR_ENUMERATION}). "
            "plan.md §7.3's exactness claim depends on this cap."
        )
    for r in range(1, len(pool) + 1):
        for subset in combinations(pool, r):
            if sum(a.capability for a in subset) >= req.amount:
                return True
    return False


#: Generator invariant on the ELIGIBLE pool, not the whole ledger.
#: v1 enumerates subsets: 2**14 = 16k evaluations, trivial. The tighter cap of 8
#: in archive/casualty_tree.md is for a *solver*, where the term is 4**n (each
#: asset takes a role) and 15 assets is already 10**9. Two different budgets for
#: two different jobs — do not conflate them.
MAX_LEDGER_FOR_ENUMERATION = 14


def ratio_fleet(req: Requirement, ledger: tuple[Asset, ...]) -> float:
    """plan.md §7.2 — what the arm multiplier targets; what a totals-reader sees."""
    total = sum(a.capability for a in ledger if a.counts_toward(req))
    return total / req.amount if req.amount else 0.0


def ratio_deadline(req: Requirement, ledger: tuple[Asset, ...]) -> float:
    """plan.md §7.2 — what is actually assemblable; the one V3 can be satisfied from."""
    total = sum(a.capability for a in eligible_assets(req, ledger))
    return total / req.amount if req.amount else 0.0


# --------------------------------------------------------------------------- #
# The checks (plan.md §4)
# --------------------------------------------------------------------------- #


def allocate(plan: ExtractedPlan, sc: Scenario) -> tuple[Allocation, ...]:
    """Resolve every token the planner wrote, once, and record what it is.

    This is the single pass V1, V2a and V3 all read. See schema.Allocation for
    why it exists and for the line it does not cross: nothing here mutates and
    nothing simulates. `credited` implements V3's no-double-count rule by
    crediting only the first committed occurrence of an eligible asset, so V3's
    total is a plain sum over this table.
    """
    req = sc.requirement
    rows: list[Allocation] = []
    seen: set[str] = set()

    for source, tokens in (("named", plan.assets_named), ("committed", plan.commitments)):
        for token in tokens:
            aid = resolve(token, sc.ledger_ids)
            if aid is None:
                rows.append(Allocation(token, source, None, note="not in ledger"))
                continue
            asset = sc.asset(aid)
            if asset is None:  # pragma: no cover - resolve() guarantees membership
                rows.append(Allocation(token, source, aid, note="resolved to no row"))
                continue
            right = asset.counts_toward(req)
            on_time = asset.arrives_by(req.deadline_h)
            credited = 0.0
            note = ""
            if source != "committed":
                note = "named only"
            elif aid in seen:
                note = "already credited"
            elif not right:
                note = f"wrong scalar ({asset.quantity or 'none'} != {req.quantity})"
            elif not on_time:
                note = f"eta {asset.eta_hours}h > {req.deadline_h}h"
            else:
                credited = asset.capability
                seen.add(aid)
            rows.append(Allocation(token, source, aid, right, on_time, credited, note))

    return tuple(rows)


def check_v1(plan: ExtractedPlan, allocs: tuple[Allocation, ...], sc: Scenario) -> CheckResult:
    """Every asset named exists in the ledger. F1, closed, ~0 loss, primary."""
    unresolved = [a.token for a in allocs if a.source == "named" and not a.resolved]
    return CheckResult(
        "V1",
        not unresolved,
        "" if not unresolved else f"not in ledger: {sorted(set(unresolved))}",
    )


def check_v2a(plan: ExtractedPlan, allocs: tuple[Allocation, ...], sc: Scenario) -> CheckResult:
    """Every committed asset arrives by the deadline. F3, closed, ~0 loss, primary.

    Unresolved tokens are skipped: an absent asset is V1's business, not V2a's.
    Repeated mentions are each reported, which is why `allocate` keeps one row
    per occurrence.
    """
    late = [f"{a.asset_id} eta {sc.asset(a.asset_id).eta_hours}h > {sc.requirement.deadline_h}h"
            for a in allocs
            if a.source == "committed" and a.resolved and not a.on_time]
    return CheckResult("V2a", not late, "; ".join(late))


def check_v3(plan: ExtractedPlan, allocs: tuple[Allocation, ...], sc: Scenario) -> CheckResult:
    """Committed capability >= stated requirement. F2, closed, 0 loss, primary.

    A plain sum of `Allocation.credited`, which already encodes the three reasons
    capability is refused: the asset is not in the ledger, it is denominated in
    the wrong scalar, or it cannot arrive by the deadline. The last of those is
    the OVERCOMMIT trap (plan.md §7.2) and is why V2a and V3 fail together there.
    """
    req = sc.requirement
    total = sum(a.credited for a in allocs)
    return CheckResult(
        "V3",
        total >= req.amount,
        f"committed {total:g} {req.unit} of {req.amount:g} required",
    )


def check_v5(plan: ExtractedPlan, allocs: tuple[Allocation, ...], sc: Scenario) -> CheckResult:
    """Plan attempts the terminal goal action. F6, one-item vocabulary, primary.

    plan.md §4.2 — presence of one action from a one-item per-casualty vocabulary.
    Read by the extractor; this records it. The vocabulary itself lives in
    data/requirements.json and is what plan.md §8.4's coverage gate measures.
    Takes `allocs` for signature uniformity and ignores it: V5 is about the goal
    action, not about resources.
    """
    return CheckResult("V5", plan.goal_attempted, f"goal: {sc.requirement.goal}")


PRIMARY_CHECKS = (check_v1, check_v2a, check_v3, check_v5)


# --------------------------------------------------------------------------- #
# Endpoints (plan.md §4.1) and flags (plan.md §5)
# --------------------------------------------------------------------------- #


def score(plan: ExtractedPlan, sc: Scenario) -> Verdict:
    """Score one plan against one scenario. The whole validator, in one call."""
    allocs = allocate(plan, sc)
    checks = {c.check_id: c for c in (fn(plan, allocs, sc) for fn in PRIMARY_CHECKS)}

    v1, v2a, v3, v5 = (checks[k].passed for k in ("V1", "V2a", "V3", "V5"))

    resource_valid = v1 and v2a and v3
    plan_succeeds = v5 and resource_valid
    sat = sc.ledger_satisfiable

    # plan.md §4.1 — the invariant that makes the composite's branches disjoint.
    # A violation is a bug in ledger_satisfiable or in the validator, never a finding.
    if not sat and plan_succeeds:
        raise AssertionError(
            f"{sc.id}/{sc.arm}: ¬LEDGER-SATISFIABLE ∧ PLAN-SUCCEEDS. "
            "plan.md §4.1 says this is a bug, not a result."
        )

    # plan.md §5 flags — derived in rcp/flags.py, which is their SSOT (§12.1).
    hallucinate = flags.hallucinate(v1)
    overcommit = flags.overcommit(v2a, v3, plan.escalate)
    appropriate = flags.appropriate_response(sat, plan_succeeds, plan.escalate, plan.reduce)

    return Verdict(
        scenario_id=sc.id,
        arm=sc.arm,
        checks=checks,
        resource_valid=resource_valid,
        plan_succeeds=plan_succeeds,
        appropriate_response=appropriate,
        ledger_satisfiable=sat,
        hallucinate=hallucinate,
        overcommit=overcommit,
        escalate=plan.escalate,
        reduce=plan.reduce,
        # §5.2 — each rate only exists on its own denominator
        correct_refusal=flags.correct_refusal(sat, plan.escalate, plan.reduce),
        over_refusal=flags.over_refusal(sat, plan.escalate),
        step_count=plan.step_count,
        word_count=plan.word_count,
        allocations=allocs,
    )
