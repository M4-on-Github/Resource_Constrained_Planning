"""Case studies for rcp_v010.tex, drawn by fixed rules rather than chosen by reading.

All cases are v0.10 blind plans scored as in the frozen run. For each kind, the
eligible cells are sorted and one is drawn with random.Random(SEED); the rules
and the seed were fixed (2026-10-14) before any case was read.
- ledgers:  one image, all four arms.
- late:     satisfiable ledger, V3 passes, V2a fails, no ESCALATE.
- hedge:    unsatisfiable ledger, no ESCALATE, a conditional step that asks for
            resources (guard_check REQUEST).
- escalate: unsatisfiable ledger, ESCALATE by the extractor and by both
            held-out label sets.
- state:    the plan branches on the casualty state (cited.STATE_IF).
- loop:     the plan looped (D9).
- flip:     a held-out cell where v010 and label set A disagree on AR (D11).

    python3 tools/cases.py              # every kind: ledger, verdict, evidence steps
    python3 tools/cases.py hedge full   # one kind, with the whole scored plan

Run in the container from the repo root.
"""

from __future__ import annotations

import csv
import json
import pathlib
import random
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rcp import extract_det as ed  # noqa: E402
from rcp.calibrate import _bool, _tokens  # noqa: E402
from rcp.extract import _load_scenarios  # noqa: E402
from rcp.schema import ExtractedPlan  # noqa: E402
from rcp.validator import score  # noqa: E402
from tools.cited import ARMS, STATE_IF, looped, plan, rows  # noqa: E402
from tools.guard_check import REQUEST  # noqa: E402

SEED = 20261014
KINDS = ("ledgers", "late", "hedge", "escalate", "state", "loop", "flip")
SC = _load_scenarios()


def as_plan(d: dict) -> ExtractedPlan:
    keys = ("assets_named", "commitments")
    return ExtractedPlan(**{k: tuple(v) if k in keys else v for k, v in d.items()})


CELLS = {}
for _a in ARMS:
    _gen = {r["scenario_id"]: r for r in rows(f"results/gen_{_a}_blind.jsonl")}
    for _r in rows(f"results/ex_gen_{_a}_blind/extracted.jsonl"):
        _p = as_plan(_r["plan"])
        _key = f"{_p.scenario_id}/{_a}"
        CELLS[_key] = dict(plan=_p, sc=SC[_key], v=score(_p, SC[_key]),
                           gen=_gen[_p.scenario_id])


def steps(c: dict) -> list[str]:
    return plan(c["gen"]["prose"])[0]


def labels(name: str) -> dict:
    return {f"{r['scenario_id']}/{r['arm']}": r
            for r in csv.DictReader(open(f"cal/d11/{name}.csv", encoding="utf-8"))}


def eligible(kind: str) -> list[str]:
    out = []
    for key, c in sorted(CELLS.items()):
        sat, v, p = c["sc"].ledger_satisfiable, c["v"], c["plan"]
        if kind == "late":
            ok = sat and v.checks["V3"].passed and not v.checks["V2a"].passed and not p.escalate
        elif kind == "hedge":
            ok = not sat and not p.escalate and any(
                REQUEST.search(s) for s in steps(c) if ed.conditional_steps([s]))
        elif kind == "state":
            ok = bool(STATE_IF.search(c["gen"]["prose"]))
        elif kind == "loop":
            ok = looped(c["gen"])
        else:
            ok = False
        if ok:
            out.append(key)
    if kind == "escalate":
        a, b = labels("labels_heldout_a"), labels("labels_heldout_b")
        out = sorted(k for k in a if not CELLS[k]["sc"].ledger_satisfiable
                     and CELLS[k]["plan"].escalate
                     and _bool(a[k]["escalate"], k) and _bool(b[k]["escalate"], k))
    if kind == "flip":
        a = labels("labels_heldout_a")
        for k in sorted(a):
            r = a[k]
            gold = ExtractedPlan(scenario_id=r["scenario_id"], arm=r["arm"],
                                 assets_named=tuple(sorted(_tokens(r["assets_named"]))),
                                 commitments=tuple(sorted(_tokens(r["commitments"]))),
                                 goal_attempted=_bool(r["goal_attempted"], k),
                                 escalate=_bool(r["escalate"], k), reduce=_bool(r["reduce"], k))
            if score(gold, SC[k]).appropriate_response != CELLS[k]["v"].appropriate_response:
                out.append(k)
    return out


def show(key: str, kind: str, full: bool) -> None:
    c = CELLS[key]
    sc, v, p = c["sc"], c["v"], c["plan"]
    q = sc.requirement
    on_time = [a for a in sc.ledger if a.eta_hours <= q.deadline_h]
    print(f"## {kind}: {key} ({sc.casualty_state}; ledger "
          f"{'satisfiable' if sc.ledger_satisfiable else 'unsatisfiable'})")
    print(f"need {q.amount:g} {q.unit} ({q.goal}) by {q.deadline_h:g} h; {len(sc.ledger)} assets, "
          f"{len(on_time)} on time; on-time ratio {sc.ratio_deadline:.2f}, "
          f"whole ledger {sc.ratio_fleet:.2f}")
    print("verdict: " + ", ".join(f"{k} {'pass' if r.passed else 'FAIL'}"
                                  for k, r in v.checks.items())
          + f"; ESCALATE {p.escalate}; AR {v.appropriate_response}")
    print(f"committed: {', '.join(p.commitments) or '-'}")
    for k, r in v.checks.items():
        if not r.passed and r.detail:
            print(f"  {k}: {r.detail[:300]}")
    s = steps(c)
    late = set(re.findall(r"([A-Z]{2,4}-\d+) eta", v.checks["V2a"].detail))
    pick = {
        "late": lambda t: any(re.search(rf"\b{re.escape(x)}\b", t) for x in late),
        "flip": lambda t: any(re.search(rf"\b{re.escape(x)}\b", t) for x in late),
        "hedge": lambda t: ed.conditional_steps([t]) and REQUEST.search(t),
        "escalate": lambda t: REQUEST.search(t) and not ed.conditional_steps([t]),
        "state": lambda t: STATE_IF.search(t),
    }.get(kind)
    if kind == "loop":
        body = ed.split_header(c["gen"]["prose"])[1]
        cut = body[len(ed.trim_repeated_steps(body)[0]):].strip().splitlines()
        print(f"steps kept {len(s)}, dropped {plan(c['gen']['prose'])[1]}, "
              f"truncated {c['gen']['truncated']}; first repeated step: {cut[0][:300]}")
    if kind == "flip":
        r = labels("labels_heldout_a")[key]
        print(f"labels A: commitments {r['commitments']}; escalate {r['escalate']}; "
              f"note: {r['notes']}")
    for i, t in enumerate(s, 1):
        if full or (pick and pick(t)):
            print(f"  {i:>2}. {t.strip()[:400]}")
    print()


def main(kind: str | None, full: bool) -> None:
    for k in [kind] if kind else KINDS:
        if k == "ledgers":
            img = random.Random(SEED).choice(sorted({key.split("/")[0] for key in CELLS}))
            print(f"# ledgers: image {img}\n")
            for a in ARMS:
                show(f"{img}/{a}", "ledgers", full)
            continue
        keys = eligible(k)
        key = random.Random(SEED).choice(keys)
        print(f"# {k}: {len(keys)} eligible, drew {key}\n")
        show(key, k, full)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] not in KINDS:
        sys.exit(__doc__)
    main(args[0] if args else None, "full" in args[1:])
