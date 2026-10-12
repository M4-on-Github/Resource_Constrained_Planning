"""Does this checkout still reproduce v0.10? No model is called.

  1. Replays every frozen v0.10 extraction (`results/ex_<cond>_all.jsonl`) through
     the current code: the same prose preprocessing as `rcp.extract`'s CLI, then
     `compose` on the stored GLM reply. `plan` and `trace` must match exactly.
  2. Re-runs `rcp.report` on the replayed rows; `report.json` and `report.txt`
     must match the frozen `results/rep_<cond>/`.

Run in the container from the repo root, after `tools/runs.py verify`:

    python3 tools/check_v010.py

The planner side is checked by `tests/test_render.py`, which pins v0.10's prompt
digests. Exit 0 if everything matches.
"""

from __future__ import annotations

import contextlib
import glob
import io
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rcp import extract, extract_det, report  # noqa: E402


def replay(cond: str, dest: pathlib.Path, scenarios: dict) -> int:
    gen = {}
    for p in glob.glob(f"results/gen_*_{cond}.jsonl"):
        for ln in open(p, encoding="utf-8"):
            r = json.loads(ln)
            gen[f"{r['scenario_id']}/{r['arm']}"] = r
    bad = 0
    with dest.open("w", encoding="utf-8", newline="\n") as fh:
        for ln in open(f"results/ex_{cond}_all.jsonl", encoding="utf-8"):
            row = json.loads(ln)
            t = row["trace"]
            key = f"{t['scenario_id']}/{t['arm']}"
            _, prose = extract_det.split_header(gen[key]["prose"])
            prose, _ = extract_det.split_contingencies(prose)
            prose, looped = extract_det.trim_repeated_steps(prose)
            meta = {"text": t["llm_raw"], "finish_reason": t["llm_finish_reason"],
                    "attempts": t["llm_attempts"]}
            plan, trace = extract.compose(prose, scenarios[key], t["llm_raw"], meta)
            plan, trace = extract._plan_dict(plan), json.loads(json.dumps(trace))
            if (plan, trace, looped) != (row["plan"], t, row.get("looped_steps_dropped")):
                bad += 1
                print(f"  DIFF {cond} {key}")
            fh.write(json.dumps({**row, "plan": plan, "trace": trace}, sort_keys=True) + "\n")
    return bad


def main() -> int:
    scenarios = extract._load_scenarios()
    failed = False
    with tempfile.TemporaryDirectory() as tmp:
        for cond in ("blind", "stated"):
            rows = pathlib.Path(tmp) / f"ex_{cond}_all.jsonl"
            bad = replay(cond, rows, scenarios)
            out = pathlib.Path(tmp) / f"rep_{cond}"
            with contextlib.redirect_stdout(io.StringIO()):
                report.main(["--input", str(rows), "--controls", "results/controls.json",
                             "--out", str(out)])
            frozen = pathlib.Path(f"results/rep_{cond}")
            same_json = ((out / "report.json").read_bytes()
                         == (frozen / "report.json").read_bytes())
            same_txt = (out / "report.txt").read_bytes() == (frozen / "report.txt").read_bytes()
            ok = bad == 0 and same_json and same_txt
            failed |= not ok
            print(f"{'OK  ' if ok else 'FAIL'} {cond}: extraction diffs {bad}, "
                  f"report.json {'same' if same_json else 'DIFFERS'}, "
                  f"report.txt {'same' if same_txt else 'DIFFERS'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
