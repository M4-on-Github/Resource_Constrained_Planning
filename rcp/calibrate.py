"""Extraction loss, measured per field against hand labels. plan.md §6.4.

Two commands, because calibration is two jobs separated by a human:

    python -m rcp.calibrate sample --input generations.jsonl --out cal/
        draws a stratified subset and writes `labels_blank.csv`, one row per
        generation, with the plan's prose beside empty label columns.

    python -m rcp.calibrate score --labels cal/labels.csv \\
                                  --extracted extract/extracted.jsonl
        compares the extractor's output to those labels, per field, and prints the
        loss figures §4's registry is required to carry.

**What is measured, and why each number exists.**

| field | metric | what a bad number means |
|---|---|---|
| `assets_named` | set P / R / F1 | §4's ~0 claim for V1 is false. This is the one number that can falsify a *structural* claim, so it is measured even though no model touches the field. |
| `commitments` | set P / R / F1 | the subtraction is lossy; V2a and V3 inherit it |
| `goal_attempted` | agreement, and the two error directions | V5 is in the headline; a false negative here reads as a planner that never tried |
| `escalate` | agreement | §5.2's two refusal rates are only as good as this |
| `reduce` | agreement | descriptive only — not in §4.1's numerator |

**And one number that is not a field: `verdict_flip`.** The fraction of calibration
cells where scoring the hand labels and scoring the extractor's output give a
different `APPROPRIATE-RESPONSE`. Per-field agreement can look good while the
endpoint moves, because the endpoint is a conjunction; this is the only figure that
answers "how wrong is the headline?" directly, and it is the one to quote.

**The labels are the ground truth and the extractor is the thing on trial.** Nothing
here feeds back into the extractor automatically. A disagreement is reported, and
whether it is fixed by changing the prompt is a decision made once, before the run,
and recorded — §6.4's "tuned off-corpus, at zero cost to *n*".
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import random
import sys

from .normalize import normalize
from .schema import ExtractedPlan

#: §6.4 asks for 60-80 hand-labelled plans. 16 strata (4 arms x 4 casualty states)
#: at 4 each is 64 — inside the band, and balanced on both axes that could plausibly
#: move extraction difficulty.
PER_STRATUM = 4
SAMPLE_SEED = 20261007

LABEL_FIELDS = ("assets_named", "commitments", "goal_attempted", "escalate", "reduce")

#: Boolean label spellings accepted from the sheet. A blank is NOT false — it is an
#: unlabelled row, and `score` refuses to count one rather than silently scoring a
#: human's omission as a judgement.
_TRUE = {"1", "y", "yes", "t", "true"}
_FALSE = {"0", "n", "no", "f", "false"}


def _bool(cell: str, where: str) -> bool:
    v = (cell or "").strip().lower()
    if v in _TRUE:
        return True
    if v in _FALSE:
        return False
    raise ValueError(f"{where}: {cell!r} is not yes/no — blank rows are not labels")


def _tokens(cell: str) -> set[str]:
    """A semicolon-separated ID list from the sheet, normalised for comparison."""
    return {normalize(t) for t in (cell or "").split(";") if t.strip()}


# --------------------------------------------------------------------------- #
# sample
# --------------------------------------------------------------------------- #


def stratify(rows: list[dict], per_stratum: int = PER_STRATUM,
             seed: int = SAMPLE_SEED) -> list[dict]:
    """Balanced on arm x casualty_state, deterministic in `seed`.

    Deterministic because the sheet is a physical artifact: if the sample moved
    between runs, the labels on a half-finished sheet would stop lining up.
    """
    buckets: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        buckets.setdefault((r["arm"], r.get("casualty_state", "?")), []).append(r)
    rng = random.Random(seed)
    out = []
    for k in sorted(buckets):
        b = sorted(buckets[k], key=lambda r: r["scenario_id"])
        rng.shuffle(b)
        out.extend(b[:per_stratum])
    return sorted(out, key=lambda r: (r["arm"], r["scenario_id"]))


def write_sheet(sample: list[dict], dest: pathlib.Path) -> None:
    """One row per plan, prose included, label columns empty.

    Prose goes in the sheet rather than in a sibling file so a labeller never has to
    join two things by hand — the single commonest way a label set gets misaligned.
    """
    with dest.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["scenario_id", "arm", "casualty_state",
                    "assets_named", "commitments",
                    "goal_attempted", "escalate", "reduce", "notes", "prose"])
        for r in sample:
            w.writerow([r["scenario_id"], r["arm"], r.get("casualty_state", ""),
                        "", "", "", "", "", "", r["prose"]])


# --------------------------------------------------------------------------- #
# score
# --------------------------------------------------------------------------- #


def _prf(gold: set[str], got: set[str]) -> dict:
    """Set precision/recall/F1, with the empty-vs-empty case counted as agreement.

    Both empty is the §3.6 vacuous case — a plan that named nothing, extracted as
    naming nothing — and scoring it 0 would make the negative control look like an
    extraction failure.
    """
    if not gold and not got:
        return {"p": 1.0, "r": 1.0, "f1": 1.0, "tp": 0, "fp": 0, "fn": 0}
    tp = len(gold & got)
    fp = len(got - gold)
    fn = len(gold - got)
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return {"p": p, "r": r, "f1": f1, "tp": tp, "fp": fp, "fn": fn}


def _mean(xs: list[float]) -> float | None:
    return sum(xs) / len(xs) if xs else None


def compare(labels: list[dict], extracted: dict[str, dict]) -> dict:
    """Per-field loss plus `verdict_flip`. Raises on an unlabelled row."""
    from .extract import _load_scenarios
    from .validator import score

    scenarios = _load_scenarios()
    sets: dict[str, list[dict]] = {"assets_named": [], "commitments": []}
    bools: dict[str, dict[str, int]] = {
        f: {"agree": 0, "n": 0, "false_pos": 0, "false_neg": 0}
        for f in ("goal_attempted", "escalate", "reduce")}
    flips, scored, missing = [], 0, []

    for row in labels:
        key = f"{row['scenario_id']}/{row['arm']}"
        got = extracted.get(key)
        if got is None:
            missing.append(key)
            continue
        where = f"{key} "
        gold_named = _tokens(row["assets_named"])
        gold_commits = _tokens(row["commitments"])
        if not gold_commits <= gold_named:
            raise ValueError(
                f"{where}: hand labels have commitments outside assets_named "
                f"({sorted(gold_commits - gold_named)}) — the pipeline enforces "
                "the subset, so a label breaking it is a labelling error")
        sets["assets_named"].append(_prf(gold_named, {normalize(t) for t in got["assets_named"]}))
        sets["commitments"].append(_prf(gold_commits, {normalize(t) for t in got["commitments"]}))

        for f in bools:
            g = _bool(row[f], where + f)
            x = bool(got[f])
            bools[f]["n"] += 1
            bools[f]["agree"] += int(g == x)
            if x and not g:
                bools[f]["false_pos"] += 1
            if g and not x:
                bools[f]["false_neg"] += 1

        sc = scenarios.get(key)
        if sc is not None:
            gold_plan = ExtractedPlan(
                scenario_id=row["scenario_id"], arm=row["arm"],
                assets_named=tuple(sorted(gold_named)),
                commitments=tuple(sorted(gold_commits)),
                goal_attempted=_bool(row["goal_attempted"], where),
                escalate=_bool(row["escalate"], where),
                reduce=_bool(row["reduce"], where))
            got_plan = ExtractedPlan(
                scenario_id=row["scenario_id"], arm=row["arm"],
                assets_named=tuple(got["assets_named"]),
                commitments=tuple(got["commitments"]),
                goal_attempted=bool(got["goal_attempted"]),
                escalate=bool(got["escalate"]),
                reduce=bool(got["reduce"]))
            a = score(gold_plan, sc).appropriate_response
            b = score(got_plan, sc).appropriate_response
            scored += 1
            if a != b:
                flips.append(key)

    return {
        "n_labelled": len(labels),
        "n_compared": sum(1 for _ in sets["assets_named"]),
        "missing_from_extraction": missing,
        "sets": {f: {"precision": _mean([x["p"] for x in v]),
                     "recall": _mean([x["r"] for x in v]),
                     "f1": _mean([x["f1"] for x in v]),
                     "fp": sum(x["fp"] for x in v),
                     "fn": sum(x["fn"] for x in v)}
                 for f, v in sets.items()},
        "bools": {f: {**v, "agreement": (v["agree"] / v["n"]) if v["n"] else None}
                  for f, v in bools.items()},
        "verdict_flip": {"n": scored, "flips": len(flips),
                         "rate": (len(flips) / scored) if scored else None,
                         "cells": flips[:20]},
    }


def render(rep: dict) -> str:
    L = ["", "Extraction calibration (plan.md sec. 6.4)",
         "=" * 42,
         f"  labelled rows   : {rep['n_labelled']}",
         f"  compared        : {rep['n_compared']}"]
    if rep["missing_from_extraction"]:
        L.append(f"  MISSING from extraction: {len(rep['missing_from_extraction'])} "
                 f"{rep['missing_from_extraction'][:5]}")
    L += ["", "  set fields (precision / recall / F1, false pos, false neg)"]
    for f, v in rep["sets"].items():
        if v["precision"] is None:
            continue
        L.append(f"    {f:<14} {v['precision']:.3f} / {v['recall']:.3f} / "
                 f"{v['f1']:.3f}   fp={v['fp']:<3} fn={v['fn']}")
    L += ["", "  binary fields (agreement, false pos, false neg)"]
    for f, v in rep["bools"].items():
        if v["agreement"] is None:
            continue
        L.append(f"    {f:<14} {v['agreement']:.3f}  "
                 f"fp={v['false_pos']:<3} fn={v['false_neg']:<3} (n={v['n']})")
    vf = rep["verdict_flip"]
    L += ["", "  THE NUMBER TO QUOTE"]
    if vf["rate"] is None:
        L.append("    verdict_flip   : not computed")
    else:
        L.append(f"    verdict_flip   : {100 * vf['rate']:.1f}%  "
                 f"({vf['flips']}/{vf['n']} cells where APPROPRIATE-RESPONSE moves)")
        L.append("    Per-field agreement can look good while the endpoint moves,")
        L.append("    because the endpoint is a conjunction. This is the figure")
        L.append("    sec. 4's registry carries for V2a and V3.")
        if vf["cells"]:
            L.append(f"    cells          : {', '.join(vf['cells'])}")
    L.append("")
    L.append("  assets_named F1 below 1.000 falsifies sec. 4's ~0 claim for V1 and")
    L.append("  is a resolver bug, not a model error -- no model touches that field.")
    return "\n".join(L)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _read_jsonl(path: pathlib.Path) -> list[dict]:
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines()
            if ln.strip()]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="RCP extraction calibration (sec. 6.4)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("sample", help="draw a stratified subset and write a label sheet")
    s.add_argument("--input", required=True, help="generations.jsonl")
    s.add_argument("--out", required=True, help="directory for labels_blank.csv")
    s.add_argument("--per-stratum", type=int, default=PER_STRATUM)

    c = sub.add_parser("score", help="compare hand labels to the extractor")
    c.add_argument("--labels", required=True, help="the filled-in label sheet")
    c.add_argument("--extracted", required=True, help="extracted.jsonl")
    c.add_argument("--out", default=None, help="also write calibration.json here")

    args = ap.parse_args(argv)

    if args.cmd == "sample":
        rows = _read_jsonl(pathlib.Path(args.input))
        sample = stratify(rows, args.per_stratum)
        out = pathlib.Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        dest = out / "labels_blank.csv"
        write_sheet(sample, dest)
        strata = {}
        for r in sample:
            k = f"{r['arm']}/{r.get('casualty_state', '?')}"
            strata[k] = strata.get(k, 0) + 1
        print(f"  {len(sample)} plans -> {dest}")
        print(f"  strata: {len(strata)} cells, {min(strata.values())}-"
              f"{max(strata.values())} each")
        print("  Fill assets_named and commitments as semicolon-separated ledger IDs,")
        print("  and goal_attempted / escalate / reduce as yes or no. A blank is not")
        print("  a label and will be rejected.")
        return 0

    labels = list(csv.DictReader(
        pathlib.Path(args.labels).open(encoding="utf-8-sig", newline="")))
    got = {}
    for row in _read_jsonl(pathlib.Path(args.extracted)):
        d = row["plan"] if "plan" in row else row
        got[f"{d['scenario_id']}/{d['arm']}"] = d
    try:
        rep = compare(labels, got)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    text = render(rep)
    print(text)
    if args.out:
        p = pathlib.Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rep, indent=2, sort_keys=True),
                     encoding="utf-8", newline="\n")
        print(f"\n  -> {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
