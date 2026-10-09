"""A mock planner: writes prose without a model, so the pipeline can be run dry.

Not a baseline and not a control — it is a **smoke test for the plumbing**. Its
output is prose shaped like a plan, produced by a rule, so running
`infer -> extract --no-llm -> report` end to end costs no GPU and the report's
tables can be checked against numbers known in advance.

Four behaviours, chosen so every branch of §9.2's tables gets exercised:

  `gold`       commits exactly the assets `controls.gold_commitment` picks, so
               PLAN-SUCCEEDS must be true wherever the ledger is satisfiable.
  `greedy`     commits every asset of the right class regardless of ETA — the
               late assets §7.2 places in every chain are taken, so V2a and V3
               separate.
  `escalate`   names nothing and says it cannot be done, so correct-refusal and
               over-refusal both have a numerator.
  `empty`      writes nothing, so the parse-failure path is exercised.

The mix is deterministic in the scenario id, never random, so two runs of the dry
pipeline produce byte-identical reports and a diff means a real change.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rcp.controls import gold_commitment                      # noqa: E402
from rcp import corpus                                         # noqa: E402
from rcp.generator import manifest                             # noqa: E402
from rcp.schema import Scenario                               # noqa: E402
from rcp.world import states                                  # noqa: E402

BEHAVIOURS = ("gold", "greedy", "escalate", "empty")


def behaviour(sc: Scenario) -> str:
    """Deterministic in the id, so the dry run is reproducible.

    `empty` is rare on purpose — one cell in twelve — because a parse-failure rate
    of 25 % would swamp the tables it is there to exercise.
    """
    h = sum(ord(c) for c in sc.id)
    if h % 12 == 0:
        return "empty"
    return BEHAVIOURS[h % 3]


def prose(sc: Scenario, kind: str) -> str:
    goal = states()[sc.casualty_state]["goal"]
    req = sc.requirement
    if kind == "empty":
        return ""
    if kind == "escalate":
        return (f"1. Hold position and keep the casualty under observation.\n"
                f"2. The assets on the ledger cannot deliver "
                f"{req.amount:g} {req.unit} within {req.deadline_h:g} hours.\n"
                f"3. Request additional capability before any attempt to "
                f"{goal} the vessel.\n"
                f"Assumption: no further assets arrive inside the window.")
    if kind == "greedy":
        ids = [a.id for a in sc.ledger if a.counts_toward(req)]
    else:
        ids = list(gold_commitment(sc) or
                   [a.id for a in sc.ledger if a.counts_toward(req)])
    lines = [f"{i}. Make {aid} fast to the casualty and take the strain."
             for i, aid in enumerate(ids, start=1)]
    lines.append(f"{len(lines) + 1}. Use the combined pull to {goal} the vessel.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="write mock generations.jsonl (no model)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=None, help="first N images")
    args = ap.parse_args(argv)

    rows = manifest()[:args.limit] if args.limit else manifest()
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        keep = {img for img, _, _ in rows}
        for sc in (s for s in corpus.load() if s.id in keep):
            kind = behaviour(sc)
            counts[kind] = counts.get(kind, 0) + 1
            fh.write(json.dumps({
                "scenario_id": sc.id, "arm": sc.arm,
                "casualty_state": sc.casualty_state,
                "prose": prose(sc, kind),
                "mock_behaviour": kind,
                "ledger_hash": corpus.ledger_hash(sc),
            }, sort_keys=True) + "\n")
    print(f"{out}: {sum(counts.values())} mock generations  {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
