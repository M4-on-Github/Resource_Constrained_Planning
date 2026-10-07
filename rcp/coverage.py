"""The sec. 8.4 coverage gate. Run before the corpus; costs no *n*.

> **Run every closed vocabulary the validator uses against the hand-written gold
> plans and record the `NO_MATCH` rate** -- the fraction of steps a competent
> salvage master wrote that the domain cannot name.

P9's defect was invisible from inside the pipeline: every unnameable step looked
like a planning failure, and only hand-checking nine of them showed that none were.
This module is the instrument that would have caught it, and it is the only place in
the repo where the measurement runs *against* the vocabulary rather than with it.

**What a bad number means.** A non-trivial `NO_MATCH` rate means **the domain is too
narrow, not that the plan is bad**. The remedy is to widen the vocabulary, or narrow
what the prompt invites, and re-run. It is never to mark the gold plan wrong -- the
gold plan is the standard the vocabulary is being measured against, and inverting
that is exactly the circularity sec. 8.4 exists to prevent.

**Why the gold plans must be written blind.** The writer of `controls/gold_plans/`
does not see `goal_vocabulary()`, the checks, or `plan.md`. A plan written toward the
vocabulary would score 0 % NO_MATCH by construction and the gate would measure
nothing. `controls/README.md` records the provenance that makes that claim auditable.

In v1 the only closed action vocabulary is V5's one goal phrase set per casualty
type, so the gate is small. It is also exactly the thing that scales badly, and any
later chain or state layer enters through it.

**The rate is reported whatever it is.** A gate that is only mentioned when it passes
is not a gate, so `rcp.report` prints this line unconditionally and says "not run"
when the plans are absent rather than omitting the row.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re

from .extract_det import goal_hit, goal_vocabulary, segment_steps

GOLD_DIR = pathlib.Path(__file__).resolve().parent.parent / "controls" / "gold_plans"

#: `AGR-00017_SUFFICIENT.txt` -> scenario id, arm. The cell id is needed because the
#: casualty state (and so the vocabulary) is a property of the scenario, not the file.
_NAME = re.compile(r"^(?P<sid>[A-Z0-9_]+-\d+)_(?P<arm>[A-Z]+)\.txt$")


def gold_files(gold_dir: pathlib.Path = GOLD_DIR) -> list[pathlib.Path]:
    return sorted(p for p in gold_dir.glob("*.txt") if _NAME.match(p.name))


def cell_of(path: pathlib.Path) -> tuple[str, str]:
    m = _NAME.match(path.name)
    if m is None:
        raise ValueError(f"{path.name} is not <SCENARIO-ID>_<ARM>.txt")
    return m.group("sid"), m.group("arm")


def score_plan(prose: str, state: str) -> dict:
    """One gold plan against one casualty's goal vocabulary.

    `steps` is reported alongside the hit because the gate's denominator is steps,
    not plans: a plan whose goal step the vocabulary misses is one unnameable step
    out of however many it wrote, and collapsing that to a per-plan boolean would
    overstate a narrow vocabulary on short plans and understate it on long ones.
    """
    hit, matched = goal_hit(prose, state)
    steps = segment_steps(prose)
    return {"steps": len(steps), "goal_hit": hit, "matched": list(matched),
            "vocabulary": list(goal_vocabulary(state)), "words": len(prose.split())}


def run(gold_dir: pathlib.Path = GOLD_DIR) -> dict:
    """The gate. Returns the rate plus every cell, so a miss is inspectable."""
    from .extract import _load_scenarios

    scenarios = _load_scenarios()
    files = gold_files(gold_dir)
    cells, misses, unknown = [], [], []
    for p in files:
        sid, arm = cell_of(p)
        sc = scenarios.get(f"{sid}/{arm}")
        if sc is None:
            unknown.append(f"{sid}/{arm}")
            continue
        row = score_plan(p.read_text(encoding="utf-8"), sc.casualty_state)
        row.update({"cell": f"{sid}/{arm}", "casualty_state": sc.casualty_state,
                    "file": p.name})
        cells.append(row)
        if not row["goal_hit"]:
            misses.append(row["cell"])

    n = len(cells)
    states = sorted({c["casualty_state"] for c in cells})
    by_state = {
        s: {"n": sum(1 for c in cells if c["casualty_state"] == s),
            "no_match": sum(1 for c in cells
                            if c["casualty_state"] == s and not c["goal_hit"])}
        for s in states}
    return {
        "n_plans": n,
        "no_match": len(misses),
        "no_match_rate": (len(misses) / n) if n else None,
        "no_match_cells": misses,
        "states_covered": states,
        "states_in_domain": sorted(_all_states()),
        "states_uncovered": sorted(set(_all_states()) - set(states)),
        "by_state": by_state,
        "unknown_cells": unknown,
        "cells": cells,
    }


def _all_states() -> list[str]:
    from .world import states
    return list(states())


def render(rep: dict) -> str:
    L = ["", "V5 coverage gate (plan.md sec. 8.4)", "=" * 36]
    if not rep["n_plans"]:
        L += ["  not run - no gold plans in controls/gold_plans/.",
              "  The gate measures the NO_MATCH rate of the goal vocabulary against",
              "  prose a competent salvage master wrote. Human input, not code."]
        # Reported even here. A gold set whose files all name cells outside the
        # corpus would otherwise print a bare "not run" and vanish silently --
        # which is the exact failure mode this gate exists to stop elsewhere.
        if rep["unknown_cells"]:
            L.append(f"  WARNING: {len(rep['unknown_cells'])} gold files name cells "
                     f"that are not in the corpus: {rep['unknown_cells'][:3]}")
            L.append("  Rename each to <SCENARIO-ID>_<ARM>.txt for a cell that exists.")
        return "\n".join(L)
    L.append(f"  gold plans      : {rep['n_plans']}")
    L.append(f"  NO_MATCH rate   : {100 * rep['no_match_rate']:.1f}%  "
             f"({rep['no_match']}/{rep['n_plans']})")
    L.append("")
    L.append("  state      n  no_match  vocabulary")
    for s in rep["states_covered"]:
        b = rep["by_state"][s]
        vocab = next(c["vocabulary"] for c in rep["cells"] if c["casualty_state"] == s)
        L.append(f"  {s:<9} {b['n']:>2}  {b['no_match']:>8}  {', '.join(vocab)}")
    if rep["states_uncovered"]:
        L.append(f"  NOT COVERED by any gold plan: {', '.join(rep['states_uncovered'])}")
        L.append("  An uncovered casualty's vocabulary is untested, not passing.")
    if rep["unknown_cells"]:
        L.append(f"  WARNING: {len(rep['unknown_cells'])} gold files name cells that "
                 f"are not in the corpus: {rep['unknown_cells'][:3]}")
    if rep["no_match_cells"]:
        L.append("")
        L.append("  MISSES - the domain could not name the goal step in:")
        for cell in rep["no_match_cells"]:
            c = next(x for x in rep["cells"] if x["cell"] == cell)
            L.append(f"    {cell:<26} {c['casualty_state']:<9} "
                     f"{c['steps']} steps, {c['words']} words")
        L.append("  A miss means the VOCABULARY is too narrow, not that the plan is")
        L.append("  bad. Widen it (or narrow what the prompt invites) and re-run.")
        L.append("  Never mark the gold plan wrong: it is the standard being")
        L.append("  measured against, and inverting that is the circularity")
        L.append("  sec. 8.4 exists to prevent.")
    else:
        L.append("")
        L.append("  No misses: every gold plan's goal step is nameable by the")
        L.append("  closed vocabulary. Note the two unsatisfiable cells are")
        L.append("  expected to escalate rather than reach the goal, so read")
        L.append("  their rows beside controls/gold_plans/NOTES.md.")
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="RCP V5 coverage gate (plan.md sec. 8.4)")
    ap.add_argument("--gold", default=str(GOLD_DIR))
    ap.add_argument("--out", default=None, help="also write coverage.json here")
    args = ap.parse_args(argv)

    rep = run(pathlib.Path(args.gold))
    print(render(rep))
    if args.out:
        p = pathlib.Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rep, indent=2, sort_keys=True),
                     encoding="utf-8", newline="\n")
        print(f"\n  -> {p}")
    # The rate is reported, never enforced: sec. 8.4 fixes no threshold, and inventing
    # one here would turn a measurement into a gate the plan did not pre-register.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
