"""Where do the planner's conditional steps come from? Exploratory (D12 note).

Post hoc, on plans already read: descriptive only, no test. Conditional steps are
`extract_det._CONDITIONAL` matches; triggers are classified by the first matching
pattern below, so the categories are rough.

    python3 tools/branch_diag.py triggers   # v0.10, all 880 plans
    python3 tools/branch_diag.py assets     # v0.10 blind: assets named only in branches
    python3 tools/branch_diag.py versions   # v0.10/v0.11/v0.12 on the v0.12 guard images
    python3 tools/branch_diag.py held       # same images: capability assets held back

Run in the container from the repo root. A late asset is one with eta_hours past
the deadline; a capability asset is one whose quantity is the requirement's.
"""

from __future__ import annotations

import collections
import glob
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rcp import extract_det as ed  # noqa: E402

ARMS = ("SURPLUS", "SUFFICIENT", "SCARCE", "INFEASIBLE")
GUARD_IDS = "cal/v012_guard/ids.txt"
VERSIONS = (("v0.10", "results/gen_*_blind.jsonl"),
            ("v0.11", "results/v011/gen_*_blind.jsonl"),
            ("v0.12", "results/v012_guard/gen_blind.jsonl"))

#: first match wins, most specific first
TRIGGERS = [(n, re.compile(p, re.I)) for n, p in [
    ("state", r"\bif (?:the )?(?:vessel|casualty|ship|she|it) (?:is|was)? ?(?:found to be |"
              r"confirmed (?:to be |as )?|determined to be )?(?:on fire|capsized|sunk|sunken|"
              r"aground|grounded|inverted|afloat|submerged)\b|\bif (?:it|this) is (?:a |an )?"
              r"(?:fire|capsiz|sink|ground)"),
    ("failure", r"\bif (?:the )?(?:vessel |casualty |she |it )?(?:is |remains )?(?:still|not) "
                r"(?:aground|refloat|afloat|righted|moving|free)|\bif (?:the )?\w+(?: \w+)? "
                r"(?:fails|stalls|parts|does not|doesn't|is unsuccessful|is insufficient)|"
                r"should (?:\w+\s+){0,6}?fail|\bif (?:resistance|load|strain|tension)|"
                r"if unsuccessful|failing that|otherwise"),
    ("finding", r"\bif (?:any )?(?:hazardous|trapped|cargo|fuel|oil|pollut|leak|breach|damage|"
                r"hull|structural|the hull|there is|there are|present|confirmed|found|"
                r"identified|detected|required by|necessary based)|\bif (?:\w+ ){0,3}(?:is|are) "
                r"(?:present|found|detected|identified|confirmed|suspected)"),
    ("topup", r"\b(?:if|as|where|when) (?:needed|required|necessary)\b|\bif (?:additional|more|"
              r"further|extra) |\bas (?:a )?(?:backup|fallback|contingency|reserve)\b|"
              r"\bin case\b|\bin the event\b"),
    ("time", r"\bif (?:\w+ ){0,4}(?:arrives?|is late|delayed|not on scene|on scene|in time|"
             r"before|after|window|tide|high water|weather)"),
    ("success", r"\bif (?:the )?(?:fire|suppression|refloat|righting|lift|operation)\w* "
                r"(?:is |are )?(?:contained|successful|suppressed|extinguished|out|complete)"),
]]
NAMES = [n for n, _ in TRIGGERS] + ["other"]


def trigger(step: str) -> str:
    return next((n for n, p in TRIGGERS if p.search(step)), "other")


def is_cond(step: str) -> bool:
    return bool(ed._CONDITIONAL.search(step))


def corpus() -> dict[str, dict]:
    return {f"{c['id']}/{c['arm']}": c
            for c in map(json.loads, open("data/corpus.jsonl", encoding="utf-8"))}


def plans(pattern: str, blind_only: bool = False, guard: bool = False):
    """(row, corpus cell, scored steps, contingencies section) as rcp.extract reads
    them: header off, contingencies set aside, loops cut."""
    keep = ({ln.strip() for ln in open(GUARD_IDS) if ln.strip() and not ln.startswith("#")}
            if guard else None)
    cells = corpus()
    for f in sorted(glob.glob(pattern)):
        if f.endswith(".env.jsonl"):
            continue
        for r in map(json.loads, open(f, encoding="utf-8")):
            if blind_only and r["condition"] != "blind":
                continue
            if keep is not None and (r["arm"] not in ("SURPLUS", "SCARCE")
                                     or r["scenario_id"] not in keep):
                continue
            _, body = ed.split_header(r["prose"])
            body, cont = ed.split_contingencies(body)
            body, _ = ed.trim_repeated_steps(body)
            yield r, cells[f"{r['scenario_id']}/{r['arm']}"], ed.segment_steps(body), cont


def mentions(asset_id: str, steps: list[str]) -> list[str]:
    pat = re.compile(r"\b" + re.escape(asset_id) + r"\b", re.I)
    return [s for s in steps if pat.search(s)]


def cmd_triggers() -> None:
    tab, n = collections.defaultdict(collections.Counter), collections.Counter()
    for r, _, steps, _ in plans("results/gen_*_*.jsonl"):
        key = (r["arm"], r["condition"])
        n[key] += 1
        tab[key].update(trigger(s) for s in steps if is_cond(s))
    print("v0.10: conditional steps per plan, by trigger")
    print(f"{'arm/condition':22}" + "".join(f"{k:>9}" for k in NAMES) + f"{'total':>8}")
    for arm in ARMS:
        for cond in ("blind", "stated"):
            t, m = tab[(arm, cond)], n[(arm, cond)]
            print(f"{arm + '/' + cond:22}" + "".join(f"{t[k] / m:9.2f}" for k in NAMES)
                  + f"{sum(t.values()) / m:8.2f}")
    tot = sum(tab.values(), collections.Counter())
    print(f"share of {sum(tot.values())} steps: "
          + ", ".join(f"{k} {tot[k] / sum(tot.values()):.0%}" for k in NAMES))


def cmd_assets() -> None:
    T = collections.defaultdict(lambda: [0, 0])
    for r, c, steps, _ in plans("results/gen_*_blind.jsonl", blind_only=True):
        req = c["requirement"]
        for a in c["ledger"]:
            hits = mentions(a["id"], steps)
            if hits:
                key = (a["quantity"] == req["quantity"], a["eta_hours"] > req["deadline_h"])
                T[key][0] += all(is_cond(s) for s in hits)
                T[key][1] += 1
    print("v0.10 blind: named assets mentioned only in conditional steps")
    for cap in (True, False):
        for late in (False, True):
            o, m = T[(cap, late)]
            if m:
                print(f"  {'capability' if cap else 'support':10} {'late' if late else 'on time':8}"
                      f" {o / m:6.1%} ({o}/{m})")


def cmd_versions() -> None:
    print("blind SURPLUS+SCARCE, v0.12 guard images: conditional steps per plan, by trigger")
    print(f"{'':8}{'plans':>6}{'any':>8}" + "".join(f"{k:>9}" for k in NAMES))
    for name, pattern in VERSIONS:
        P = [[s for s in steps if is_cond(s)]
             for *_, steps, _ in plans(pattern, blind_only=True, guard=True)]
        per = collections.Counter(trigger(s) for p in P for s in p)
        print(f"{name:8}{len(P):>6}{sum(map(bool, P)) / len(P):>8.1%}"
              + "".join(f"{per[k] / len(P):9.2f}" for k in NAMES))


def cmd_held() -> None:
    """Held back: a capability asset named only in conditional steps or only in
    v0.12's Contingencies section."""
    print("blind SURPLUS+SCARCE, v0.12 guard images: capability assets held back")
    for name, pattern in VERSIONS:
        T, any_on_time = {False: [0, 0], True: [0, 0]}, [0, 0]
        for _, c, steps, cont in plans(pattern, blind_only=True, guard=True):
            req, held_on_time = c["requirement"], False
            for a in c["ledger"]:
                if a["quantity"] != req["quantity"]:
                    continue
                hits = mentions(a["id"], steps)
                if not hits and not mentions(a["id"], [cont or ""]):
                    continue
                held, late = all(is_cond(s) for s in hits), a["eta_hours"] > req["deadline_h"]
                T[late][0] += held
                T[late][1] += 1
                held_on_time |= held and not late
            any_on_time[0] += held_on_time
            any_on_time[1] += 1
        f = lambda x: f"{x[0] / x[1]:.1%} ({x[0]}/{x[1]})"
        print(f"  {name}: on time {f(T[False])}, late {f(T[True])}, "
              f"plans holding back an on-time asset {f(any_on_time)}")


if __name__ == "__main__":
    cmds = {"triggers": cmd_triggers, "assets": cmd_assets,
            "versions": cmd_versions, "held": cmd_held}
    if len(sys.argv) != 2 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    cmds[sys.argv[1]]()
