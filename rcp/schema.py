"""The scenario and plan objects. plan.md §3.1 (entities), §7.1 (requirement tuple).

Everything here is frozen — a scenario is written once, pre-inference, and never
mutated. The validator is a pure function of (ExtractedPlan, Scenario).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Asset:
    """One ledger row. plan.md §7.2 minimum field set."""

    id: str
    type: str
    label: str
    capability: float
    unit: str
    location: str
    eta_hours: float
    status: str = "available"
    #: which requirement scalar this asset counts toward; None = distractor.
    #: plan.md §7.3 invariant 1 (type match) is enforced by this field alone.
    quantity: str | None = None

    def counts_toward(self, req: "Requirement") -> bool:
        return self.quantity is not None and self.quantity == req.quantity

    def arrives_by(self, deadline_h: float) -> bool:
        return self.eta_hours <= deadline_h


@dataclass(frozen=True, slots=True)
class Requirement:
    """plan.md §7.1 — one tuple per scenario, uniform across casualty types."""

    goal: str
    quantity: str
    unit: str
    amount: float
    deadline_h: float
    deadline_driver: str


@dataclass(frozen=True, slots=True)
class Scenario:
    """A single (image, arm) cell. 110 images x 4 arms = 440."""

    id: str
    arm: str
    casualty_state: str
    size_category: str
    requirement: Requirement
    ledger: tuple[Asset, ...]
    #: True if this scenario carries the OVERCOMMIT trap: the fleet total clears
    #: the requirement but the by-deadline total does not (plan.md §7.3 inv. 3).
    is_trap: bool
    ratio_fleet: float
    ratio_deadline: float
    ledger_satisfiable: bool
    t0: str = "T+00:00"
    seed: int = 0

    @property
    def ledger_ids(self) -> tuple[str, ...]:
        return tuple(a.id for a in self.ledger)

    def asset(self, asset_id: str) -> Asset | None:
        return next((a for a in self.ledger if a.id == asset_id), None)


@dataclass(frozen=True, slots=True)
class ExtractedPlan:
    """What the extractor produces from plan prose. plan.md §6.3.

    The validator never sees prose. This object is the airlock, and it is why
    plan.md §3.6 claim 1 ("succeeds in the declared world") is decided exactly:
    everything downstream of here is arithmetic.
    """

    scenario_id: str
    arm: str
    #: raw tokens the plan used to name assets, as written. V1 reads this.
    assets_named: tuple[str, ...] = ()
    #: tokens for assets assigned work at or before the goal step. V2a/V3 read this.
    commitments: tuple[str, ...] = ()
    #: V5 — does a step attempt the casualty's terminal goal action?
    goal_attempted: bool = False
    #: §5 LLM-read flags
    escalate: bool = False
    reduce: bool = False
    #: §9.2 ceiling-artifact column
    step_count: int = 0
    word_count: int = 0
    #: set when the generation could not be parsed at all (plan.md §8.2)
    parse_failed: bool = False


@dataclass(frozen=True, slots=True)
class CheckResult:
    check_id: str
    passed: bool
    detail: str = ""


@dataclass(frozen=True, slots=True)
class Verdict:
    """The scored plan. One row per (image, arm)."""

    scenario_id: str
    arm: str
    checks: dict[str, CheckResult] = field(default_factory=dict)

    resource_valid: bool = False
    plan_succeeds: bool = False
    appropriate_response: bool = False

    ledger_satisfiable: bool = False
    hallucinate: bool = False
    overcommit: bool = False
    escalate: bool = False
    reduce: bool = False

    #: §5.2 cells — None where the denominator does not apply
    correct_refusal: bool | None = None
    over_refusal: bool | None = None

    step_count: int = 0
    word_count: int = 0

    def passed(self, check_id: str) -> bool:
        r = self.checks.get(check_id)
        return bool(r and r.passed)
