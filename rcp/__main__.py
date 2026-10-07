"""Phase A gates. `python -m rcp` — no model, no GPU, no generations spent.

Runs every check that can be run before inference, in the order a failure should
stop you:

    data admissibility  (plan.md §7.3 invariant 6)
    corpus build        (§7.3 invariants 1-5, enforced)
    instrument controls (§8.3: positive, negative, minimal-pass probe)
    V5 coverage         (§8.4 — reported, and it needs prose, see below)
    freeze status       (§12.2)

Exit status is 1 if any gate fails, so this is usable as a pre-inference guard.
"""

from __future__ import annotations

import sys

from . import coverage
from .controls import run_controls
from .generator import build_corpus, manifest
from .validator import eligible_assets
from .world import ARMS, assert_granularity_floor, unfrozen

OK, BAD = "  ok  ", " FAIL "


def main(argv: list[str] | None = None) -> int:
    failed = False

    print("== data admissibility (sec. 7.3 inv. 6) ==")
    try:
        assert_granularity_floor()
        print(f"[{OK}] granularity floor holds for every casualty state")
    except ValueError as exc:
        failed = True
        print(f"[{BAD}] {exc}")

    print("\n== corpus (sec. 7.1, sec. 7.3) ==")
    try:
        corpus = build_corpus(manifest())
    except RuntimeError as exc:
        print(f"[{BAD}] {exc}")
        return 1
    print(f"[{OK}] {len(corpus)} scenarios "
          f"({len(corpus) // len(ARMS)} images x {len(ARMS)} arms), "
          f"{sum(s.seed > 0 for s in corpus)} needed a redraw")

    print(f"\n{'arm':<12}{'sat':>8}{'trap':>7}{'r_fleet':>10}{'r_dline':>10}"
          f"{'assets':>8}{'elig':>6}")
    for arm in ARMS:
        rows = [s for s in corpus if s.arm == arm]
        n = len(rows)
        print(f"{arm:<12}{sum(s.ledger_satisfiable for s in rows):>4}/{n:<3}"
              f"{sum(s.is_trap for s in rows):>7}"
              f"{sum(s.ratio_fleet for s in rows) / n:>10.2f}"
              f"{sum(s.ratio_deadline for s in rows) / n:>10.2f}"
              f"{sum(len(s.ledger) for s in rows) / n:>8.1f}"
              f"{max(len(eligible_assets(s.requirement, s.ledger)) for s in rows):>6}")

    print("\n== instrument controls (sec. 8.3) ==")
    rep = run_controls(corpus)
    gates = (
        ("positive control: every gold plan scores PLAN-SUCCEEDS", "positive_failures"),
        ("negative control: unidentified classes fail, and fail on V3", "negative_wrong_check"),
        ("negative control: never passes", "negative_passes"),
        ("satisfiable => a gold plan exists", "satisfiable_without_gold"),
        ("gold plan => satisfiable", "gold_without_satisfiable"),
    )
    for label, key in gates:
        bad = rep[key]
        assert isinstance(bad, list)
        if bad:
            failed = True
            print(f"[{BAD}] {label} -- {len(bad)} violations, e.g. {bad[:3]}")
        else:
            print(f"[{OK}] {label}")

    probe = rep["probe"]
    if isinstance(probe, dict):
        print(f"\n  minimal-pass probe ({probe['scenario']}) -- not a gate, a calibration object:")
        print(f"    requirement : {probe['requirement']}")
        print(f"    commitments : {', '.join(probe['commitments'])}")
        print(f"    steps       : {probe['steps']}  <- this is all it takes to clear "
              f"PLAN-SUCCEEDS (sec. 9.2's ceiling reading)")

    # sec. 8.4 is run, not described. The gold plans above are symbolic by
    # construction, so the gate reads the hand-written prose in
    # controls/gold_plans/ instead -- and reports its rate whether or not that
    # directory is populated. A gate only mentioned when it passes is not a gate.
    print(coverage.render(coverage.run()))

    print("\n== freeze status (sec. 12.2) ==")
    un = unfrozen()
    print(f"[ note ] unfrozen data files: {', '.join(un) if un else 'none'}")
    print("[ note ] sec. 9.4's MDE table must be re-derived against a FLATNESS "
          "alternative before freeze")

    print("\nPHASE A:", "FAILED" if failed else "all gates green")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
