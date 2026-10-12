"""D11's calibration sample: v0.10 blind plans, split by image into dev and held-out.

    python tools/d11_sample.py --out cal/d11

Images are split first, within each casualty state, so no image has plans on both
sides: the dev set is where the extractor prompt may be revised, and a held-out
plan of the same image under another ledger would leak its wording. Then each
arm x state stratum draws DEV_PER plans from dev images and HELD_PER from held-out
images. Blind only: the primary is blind, the extractor never sees the condition,
and `rcp.calibrate` keys labels by scenario_id/arm.

Writes, refusing to overwrite:
  gen_sample.jsonl            the sampled generation rows, byte-identical to v0.10's
  labels_{dev,heldout}_blank.csv  one row per plan, label columns empty
  {dev,heldout}_view.md       the same plans, readable
The sheets show the text extraction scores (loops cut at the first repeat, D9),
and pre-fill `assets_named` from the deterministic resolver; the labeller corrects
it if wrong. Every other label column is blank.
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rcp import extract_det  # noqa: E402
from rcp.extract import _load_scenarios  # noqa: E402
from rcp.world import states  # noqa: E402

SEED = 20261012
ARMS = ("SURPLUS", "SUFFICIENT", "SCARCE", "INFEASIBLE")
DEV_SHARE = 0.4          # of each state's images
DEV_PER, HELD_PER = 4, 6  # plans per arm x state stratum: 64 dev, 96 held-out
INPUTS = [f"results/gen_{a}_blind.jsonl" for a in ARMS]
COLUMNS = ["scenario_id", "arm", "casualty_state", "goal", "assets_named",
           "commitments", "goal_attempted", "escalate", "reduce", "notes",
           "looped_steps_cut", "prose"]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    out = pathlib.Path(args.out)
    names = ["gen_sample.jsonl", "labels_dev_blank.csv", "labels_heldout_blank.csv",
             "dev_view.md", "heldout_view.md"]
    if any((out / n).exists() for n in names):
        print(f"ERROR: {out} already holds a sample; refusing to overwrite.",
              file=sys.stderr)
        return 1

    lines = {}
    for p in INPUTS:
        for ln in pathlib.Path(p).read_text(encoding="utf-8").splitlines():
            if ln.strip():
                r = json.loads(ln)
                lines[(r["scenario_id"], r["arm"])] = (ln, r)
    images: dict[str, list[str]] = {}
    for (sid, _), (_, r) in lines.items():
        images.setdefault(r["casualty_state"], [])
        if sid not in images[r["casualty_state"]]:
            images[r["casualty_state"]].append(sid)

    rng = random.Random(SEED)
    pool: dict[str, set[str]] = {"dev": set(), "heldout": set()}
    for state in sorted(images):
        ids = sorted(images[state])
        rng.shuffle(ids)
        k = round(DEV_SHARE * len(ids))
        pool["dev"] |= set(ids[:k])
        pool["heldout"] |= set(ids[k:])

    picked: dict[str, list[tuple[str, str]]] = {"dev": [], "heldout": []}
    for arm in ARMS:
        for state in sorted(images):
            for split, n in (("dev", DEV_PER), ("heldout", HELD_PER)):
                ids = sorted(i for i in images[state] if i in pool[split])
                rng.shuffle(ids)
                picked[split] += [(i, arm) for i in ids[:n]]

    scenarios = _load_scenarios()
    goals = {s: v["goal"] for s, v in states().items()}
    out.mkdir(parents=True, exist_ok=True)
    keys = sorted(picked["dev"] + picked["heldout"], key=lambda k: (k[1], k[0]))
    with (out / "gen_sample.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for k in keys:
            fh.write(lines[k][0] + "\n")
    for split in ("dev", "heldout"):
        rows = sorted(picked[split], key=lambda k: (k[0], ARMS.index(k[1])))
        with (out / f"labels_{split}_blank.csv").open(
                "w", encoding="utf-8", newline="") as fh, \
             (out / f"{split}_view.md").open("w", encoding="utf-8", newline="\n") as md:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(COLUMNS)
            md.write(f"# D11 {split} plans ({len(rows)})\n\nLabel in "
                     f"labels_{split}_blank.csv; rules in LABELLING.md.\n")
            for n, (sid, arm) in enumerate(rows, 1):
                r = lines[(sid, arm)][1]
                sc = scenarios[f"{sid}/{arm}"]
                _, plan = extract_det.split_header(r["prose"])
                plan, _ = extract_det.split_contingencies(plan)
                plan, cut = extract_det.trim_repeated_steps(plan)
                named = extract_det.deterministic_pass(plan, sc)["assets_named"]
                goal = goals[r["casualty_state"]]
                w.writerow([sid, arm, r["casualty_state"], goal, ";".join(named),
                            "", "", "", "", "", cut, plan])
                md.write(f"\n---\n\n## {n}. {sid} / {arm}\n\n"
                         f"state **{r['casualty_state']}**, goal **{goal}**"
                         + (f", loop cut ({cut} steps dropped)" if cut else "")
                         + f"\n\nassets named: {', '.join(named) or '(none)'}\n\n"
                         + "```text\n" + plan + "\n```\n")
    print(f"  dev images {len(pool['dev'])}, held-out images {len(pool['heldout'])}")
    print(f"  dev plans {len(picked['dev'])}, held-out plans {len(picked['heldout'])}"
          f" -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
