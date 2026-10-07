"""Build data/manifest.csv from Eval_CASTOR's human ground truth.

plan.md §7.1's corpus is 110 CASTOR images. Two fields are needed per image and
both are human-labelled, so neither is inferred here:

  state           -> the `state` column. Authoritative; q1-q5 are not casualty
                     labels (see the §7.1 note).
  size_category   -> the LEADING WORD of `size_estimate`. The column carries two
                     spellings of the same value ("medium (10-50m)" with a hyphen
                     and with an en-dash, the latter mojibake under UTF-8), so
                     matching the full string would silently split one category
                     into two. The leading word is stable under both.

Run from the repo root. Writes data/manifest.csv, which is committed: the corpus
must be reproducible from the manifest alone, with no path to Eval_CASTOR at
generation time.
"""

from __future__ import annotations

import csv
import pathlib
import sys

GT = pathlib.Path("../Eval_CASTOR/human_ground_truth_label/human_gt.csv")
OUT = pathlib.Path("data/manifest.csv")

#: plan.md §7.1. A mismatch means the GT file moved under us.
EXPECTED_N = {"aground": 42, "sunken": 33, "capsized": 19, "on_fire": 16}
SIZES = {"small", "medium", "large"}


def main() -> int:
    if not GT.exists():
        print(f"not found: {GT.resolve()}", file=sys.stderr)
        return 1

    rows: list[tuple[str, str, str]] = []
    with GT.open(encoding="utf-8", errors="replace", newline="") as fh:
        for r in csv.DictReader(fh):
            image = (r.get("image") or "").strip()
            state = (r.get("state") or "").strip()
            size = (r.get("size_estimate") or "").strip().split()[0].lower()
            if not image:
                continue
            if state not in EXPECTED_N:
                print(f"unknown state {state!r} for {image}", file=sys.stderr)
                return 1
            if size not in SIZES:
                print(f"unknown size {size!r} for {image}", file=sys.stderr)
                return 1
            # IMG id: the image path without directory or extension, prefixed by
            # state so ids stay distinct and human-readable in results tables.
            stem = pathlib.PurePosixPath(image).stem
            rows.append((f"{state.upper()[:3]}-{stem}", state, size))

    counts: dict[str, int] = {}
    for _, state, _ in rows:
        counts[state] = counts.get(state, 0) + 1
    if counts != EXPECTED_N:
        print(f"state counts {counts} != plan.md §7.1 {EXPECTED_N}", file=sys.stderr)
        return 1
    if len({r[0] for r in rows}) != len(rows):
        print("duplicate image ids", file=sys.stderr)
        return 1

    rows.sort()
    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["id", "state", "size_category"])
        w.writerows(rows)

    sizes: dict[str, int] = {}
    for _, _, s in rows:
        sizes[s] = sizes.get(s, 0) + 1
    print(f"{OUT}: {len(rows)} images  states {counts}  sizes {sizes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
