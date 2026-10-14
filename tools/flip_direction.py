"""Which way do the extractor's verdict flips go? (D11 held-out note.)

`rcp.calibrate` counts the plans where APPROPRIATE-RESPONSE differs between the
labels and the extractor. This prints AR per arm under each, and each flip with
its direction. A flip *flattens* AR when the extractor fails a plan the labels
pass on a satisfiable ledger, or passes one they fail on an unsatisfiable ledger;
otherwise it *steepens*. Gold plans are built from the label sheet exactly as in
`rcp.calibrate.compare`.

    python3 tools/flip_direction.py            # dev, held-out A, held-out B
    python3 tools/flip_direction.py cal/d11/labels_heldout_a.csv

Run in the container from the repo root. Reads the frozen v0.10 blind
extraction, `results/ex_blind_all.jsonl`.
"""

from __future__ import annotations

import collections
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rcp.calibrate import _bool, _tokens  # noqa: E402
from rcp.extract import _load_scenarios  # noqa: E402
from rcp.schema import ExtractedPlan  # noqa: E402
from rcp.validator import score  # noqa: E402

ARMS = ("SURPLUS", "SUFFICIENT", "SCARCE", "INFEASIBLE")
EXTRACTED = "results/ex_blind_all.jsonl"
LABELS = ("cal/d11/labels_dev.csv", "cal/d11/labels_heldout_a.csv",
          "cal/d11/labels_heldout_b.csv")


def main(paths: list[str]) -> None:
    scenarios = _load_scenarios()
    got = {}
    for line in open(EXTRACTED):
        p = json.loads(line)["plan"]
        got[f"{p['scenario_id']}/{p['arm']}"] = p

    for path in paths:
        ar = collections.defaultdict(lambda: [0, 0, 0])   # n, labels, extractor
        flips = []
        for r in csv.DictReader(open(path)):
            key = f"{r['scenario_id']}/{r['arm']}"
            g, sc = got[key], scenarios[key]

            def plan(named, commits, goal, esc, red):
                return ExtractedPlan(scenario_id=r["scenario_id"], arm=r["arm"],
                                     assets_named=tuple(named), commitments=tuple(commits),
                                     goal_attempted=goal, escalate=esc, reduce=red)

            gold = plan(sorted(_tokens(r["assets_named"])), sorted(_tokens(r["commitments"])),
                        _bool(r["goal_attempted"], key), _bool(r["escalate"], key),
                        _bool(r["reduce"], key))
            ext = plan(g["assets_named"], g["commitments"], bool(g["goal_attempted"]),
                       bool(g["escalate"]), bool(g["reduce"]))
            a = score(gold, sc).appropriate_response
            b = score(ext, sc).appropriate_response
            n = ar[r["arm"]]
            n[0] += 1
            n[1] += a
            n[2] += b
            if a != b:
                flat = b != sc.ledger_satisfiable
                flips.append((key, "extractor passes, labels fail" if b
                              else "extractor fails, labels pass",
                              "flattens" if flat else "steepens"))

        print(f"{path}  ({sum(v[0] for v in ar.values())} plans)")
        print(f"  {'':12}{'AR labels':>11}{'AR extractor':>14}")
        for arm in ARMS:
            n, a, b = ar[arm]
            print(f"  {arm:12}{f'{a}/{n}':>11}{f'{b}/{n}':>14}")
        flat = sum(f[2] == "flattens" for f in flips)
        print(f"  {len(flips)} flips, {flat} flatten AR")
        for f in flips:
            print(f"    {f[0]:22}{f[1]:32}{f[2]}")
        print()


if __name__ == "__main__":
    main(sys.argv[1:] or list(LABELS))
