"""Plans beside their extraction trace and verdict, for reading by hand (D10).

    python3 tools/audit.py v2a SURPLUS blind 20 7   # 20 random V2a failures, seed 7
    python3 tools/audit.py loop SCARCE blind        # every looped plan

`v2a` prints, per failure, the deadline and requirement, the late committed assets
with their ledger rows, what the extractor excluded, and every line of the kept
prose naming a late asset. `loop` prints each looped plan's kept prose, the
extractor's raw reply and the first repeated line. The two commands above are the
D10 audits; output is deterministic, so it is not stored.

Run in the container from the repo root. Reads `results/gen_<ARM>_<COND>.jsonl`
and `results/ex_gen_<ARM>_<COND>/extracted.jsonl`.
"""

from __future__ import annotations

import json
import pathlib
import random
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rcp import extract_det  # noqa: E402
from rcp.extract import _load_scenarios  # noqa: E402
from rcp.schema import ExtractedPlan  # noqa: E402
from rcp.validator import score  # noqa: E402

mode, arm, cond = sys.argv[1], sys.argv[2], sys.argv[3]
sc_all = _load_scenarios()
gen = {json.loads(l)["scenario_id"]: json.loads(l)
       for l in open(f"results/gen_{arm}_{cond}.jsonl") if l.strip()}
rows = [json.loads(l) for l in open(f"results/ex_gen_{arm}_{cond}/extracted.jsonl") if l.strip()]


def verdict(row):
    d = row["plan"]
    sc = sc_all[f"{d['scenario_id']}/{d['arm']}"]
    p = ExtractedPlan(scenario_id=d["scenario_id"], arm=d["arm"],
                      assets_named=tuple(d["assets_named"]),
                      commitments=tuple(d["commitments"]),
                      goal_attempted=d["goal_attempted"], escalate=d["escalate"],
                      reduce=d["reduce"], step_count=d["step_count"],
                      word_count=d["word_count"],
                      conditional_steps=d["conditional_steps"],
                      parse_failed=d["parse_failed"])
    return sc, score(p, sc)


if mode == "v2a":
    n, seed = int(sys.argv[4]), int(sys.argv[5])
    fails = []
    for r in rows:
        sc, v = verdict(r)
        chk = v.checks
        if not chk["V2a"].passed:
            fails.append((r, sc, v, chk))
    print(f"# {arm}/{cond}: {len(fails)} V2a failures of {len(rows)}; showing {n} (seed {seed})\n")
    random.Random(seed).shuffle(fails)
    for r, sc, v, chk in fails[:n]:
        sid = r["plan"]["scenario_id"]
        prose, _ = extract_det.trim_repeated_steps(gen[sid]["prose"])
        late_ids = re.findall(r"([A-Z]{2,4}-\d+) eta", chk["V2a"].detail)
        print(f"## {sid}  deadline {sc.requirement.deadline_h}h  need {sc.requirement.amount:g} {sc.requirement.unit}"
              f"  | V3 {'pass' if chk['V3'].passed else 'FAIL'} ({chk['V3'].detail})"
              f"  | looped {r['looped_steps_dropped']}  escalate {r['plan']['escalate']}")
        print(f"late committed: {chk['V2a'].detail}")
        print(f"not_assigned_work (LLM): {r['trace']['not_assigned_work']}")
        for aid in sorted(set(late_ids)):
            a = sc.asset(aid)
            print(f"  ledger {aid}: eta {a.eta_hours}h cap {a.capability:g} {a.quantity or ''}")
        print("lines naming a late asset:")
        for ln in prose.splitlines():
            if any(re.search(rf"\b{re.escape(x)}\b", ln, re.I) for x in late_ids):
                print("   > " + ln.strip()[:400])
        print()
else:
    looped = [r for r in rows if r["looped_steps_dropped"] > 0]
    print(f"# {arm}/{cond}: {len(looped)} looped plans\n")
    for r in looped:
        sc, v = verdict(r)
        sid = r["plan"]["scenario_id"]
        prose, dropped = extract_det.trim_repeated_steps(gen[sid]["prose"])
        full = gen[sid]["prose"]
        rest = full[len(prose):].strip().splitlines()
        print(f"## {sid}  AR {v.appropriate_response}  escalate {r['plan']['escalate']}"
              f"  reduce {r['plan']['reduce']}  steps kept {r['plan']['step_count']}  dropped {dropped}")
        print(f"LLM raw: {r['trace']['llm_raw']}")
        print("--- kept plan ---")
        print(prose)
        print(f"--- first repeated line (cut here) ---\n   {rest[0][:300] if rest else ''}")
        print()
