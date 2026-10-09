"""The v0.11 guard test (docs/deviations.md D10): does the commitment header hold?

Reads generation rows only. No extractor, no validator, no endpoint: every number
here is a property of the prose (a header present, a branch written, a loop, a
truncation), which is what keeps a test on the study's own images from selecting
the prompt on the result (plan.md §6.4's reason for going off-corpus).

    python tools/guard_check.py --new results/v011_guard/gen_blind.jsonl \
        --baseline results/gen_SURPLUS_blind.jsonl results/gen_SCARCE_blind.jsonl

`--baseline` is restricted to the scenario keys in `--new`, so the two columns are
the same cells under the v0.10 and v0.11 prompts.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys

from rcp import extract_det

#: The acceptance criteria, fixed in D10 before any v0.11 generation existed.
MIN_HEADER = 0.95       # share with one declared state and a "Salvage Plan:" label
MAX_BRANCHED = 0.30     # share of plans with >= 1 conditional step
MAX_MEAN_BRANCHES = 1.0

#: Report-only (added with D10's revision 2, before its generation): hedges that
#: escape `conditional_steps`. Revision 2 bans the words the branch count looks for,
#: so a paraphrase ("on standby", "where necessary") could pass the criterion
#: without the plan committing; this column shows whether that happened.
HEDGE = re.compile(r"\b(?:as needed|as required|where (?:necessary|required)|"
                   r"when (?:necessary|required)|upon failure|on failure|"
                   r"contingenc\w*|back-?up|stand-?by|fallback|alternatively)\b",
                   re.IGNORECASE)


def load(paths: list[str]) -> list[dict]:
    rows = []
    for p in paths:
        with open(p, encoding="utf-8") as fh:
            rows += [json.loads(ln) for ln in fh if ln.strip()]
    return rows


def measure(rows: list[dict]) -> dict:
    n = len(rows)
    if not n:
        return {"n": 0}
    header = committed = correct = branched = looped = truncated = 0
    branches, tokens, ambiguous, hedged, steps = [], [], 0, 0, []
    for r in rows:
        declared, plan = extract_det.split_header(r["prose"])
        has_label = plan != r["prose"]
        committed += declared not in (None, "ambiguous")
        ambiguous += declared == "ambiguous"
        header += has_label and declared not in (None, "ambiguous")
        correct += declared == r.get("casualty_state")
        plan, dropped = extract_det.trim_repeated_steps(plan)
        looped += dropped > 0
        segs = extract_det.segment_steps(plan)
        k = extract_det.conditional_steps(segs)
        hedged += any(HEDGE.search(s) and not extract_det.conditional_steps([s])
                      for s in segs)
        steps.append(len(segs))
        branches.append(k)
        branched += k > 0
        truncated += bool(r.get("truncated"))
        tokens.append(r.get("n_tokens") or 0)
    return {"n": n, "header": header / n, "committed": committed / n,
            "ambiguous": ambiguous / n, "correct": correct / n,
            "branched": branched / n, "mean_branches": sum(branches) / n,
            "hedged": hedged / n, "median_steps": statistics.median(steps),
            "looped": looped / n, "truncated": truncated / n,
            "median_tokens": statistics.median(tokens)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="v0.11 guard test (D10)")
    ap.add_argument("--new", nargs="+", required=True)
    ap.add_argument("--baseline", nargs="*", default=[])
    args = ap.parse_args(argv)

    new = load(args.new)
    keys = {(r["scenario_id"], r["arm"]) for r in new}
    base = [r for r in load(args.baseline) if (r["scenario_id"], r["arm"]) in keys]
    arms = sorted({r["arm"] for r in new})

    cols = [("header ok", "header"), ("committed", "committed"),
            ("ambiguous", "ambiguous"), ("state correct", "correct"),
            ("w/ branch", "branched"), ("branches/plan", "mean_branches"),
            ("hedge, no if", "hedged"), ("median steps", "median_steps"),
            ("looped", "looped"), ("truncated", "truncated"),
            ("median tokens", "median_tokens")]
    print(f"{'':12} {'prompt':8} {'n':>4}  " + "  ".join(f"{c:>13}" for c, _ in cols))
    for arm in arms + ["ALL"]:
        for label, rows in (("v0.10", base), ("v0.11", new)):
            sel = [r for r in rows if arm == "ALL" or r["arm"] == arm]
            if not sel:
                continue
            m = measure(sel)
            cells = []
            for _, k in cols:
                v = m[k]
                cells.append(f"{v:>13.2f}" if k == "mean_branches" else
                             f"{v:>13.0f}" if k in ("median_tokens", "median_steps") else f"{v:>12.1%} ")
            print(f"{arm:12} {label:8} {m['n']:>4}  " + "  ".join(cells))

    m, b = measure(new), measure(base) if base else None
    checks = [
        ("header present and committed", m["header"] >= MIN_HEADER,
         f"{m['header']:.1%} >= {MIN_HEADER:.0%}"),
        ("plans with a branch", m["branched"] <= MAX_BRANCHED,
         f"{m['branched']:.1%} <= {MAX_BRANCHED:.0%}"),
        ("branches per plan", m["mean_branches"] <= MAX_MEAN_BRANCHES,
         f"{m['mean_branches']:.2f} <= {MAX_MEAN_BRANCHES:.1f}"),
    ]
    if b:
        checks += [
            ("loops no worse than v0.10", m["looped"] <= b["looped"],
             f"{m['looped']:.1%} vs {b['looped']:.1%}"),
            ("truncation no worse than v0.10", m["truncated"] <= b["truncated"],
             f"{m['truncated']:.1%} vs {b['truncated']:.1%}"),
        ]
    print("\nacceptance (D10):")
    for name, ok, detail in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:32} {detail}")
    print("  (state correct is reported, never a criterion: it is the planner's"
          " vision, not the prompt's format)")
    print("  ('hedge, no if' and median steps are reported, never criteria)")
    return 0 if all(ok for _, ok, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
