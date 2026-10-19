"""plan_v013b.md: the dev-split diagnostic. Prepare, power, label sheet, report.

    python3 tools/v013b.py prepare   # cal/v013b/: dev and reproduction ids (drawn once)
    python3 tools/v013b.py power     # plan_v013b.md §6's power figures
    python3 tools/v013b.py sheet     # cal/v013b/: ESCALATE sheet for the told plans (after the run)
    python3 tools/v013b.py report    # results/v013b/report.txt (written once)
    python3 tools/v013b.py check     # rebuild the report, compare byte for byte

Only Track E dev images (cal/track_e/split.csv) are run or read; the report halts
on a row from any other image. `prepare`, `sheet` and `report` refuse to
overwrite. Run in the container from the repo root.
"""

from __future__ import annotations

import csv
import pathlib
import random
import statistics
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from rcp.calibrate import _bool  # noqa: E402
from rcp.probe import knows, says_short  # noqa: E402
from rcp.render import domain_digest  # noqa: E402
from rcp.report import ARMS, Z95  # noqa: E402
from tools.d14 import extracted, in_arm, key, pct, rows, verdicts  # noqa: E402
from tools.probe_gap import ci95, contrasts, labelled_acts, scored_text  # noqa: E402

SEED = 20261019
HIGH, LOW = 0.50, 0.20     # told-verdict bars; LOW is the study's δ
RELIABLE = 0.80            # a self-verdict's K lower bound, for v0.14 to use it
PARSE_MIN = 0.95
REPRO_IMAGES = 3
SAT, UNSAT = ("SURPLUS", "SUFFICIENT"), ("SCARCE", "INFEASIBLE")
V013_WORDINGS = ("probe_can", "probe_short")
WITH_TOTALS = (*V013_WORDINGS, "probe_enough", "probe_request", "probe_feasible")
SPLIT = REPO / "cal/track_e/split.csv"
CAL = REPO / "cal/v013b"
OUT = REPO / "results/v013b"
V013 = REPO / "results/v013_probe"
TOLD = OUT / "told_plan.jsonl"
TOLD_EX = OUT / "ex_told_plan/extracted.jsonl"


def dev_images() -> list[str]:
    return sorted(r["id"] for r in csv.DictReader(SPLIT.open(encoding="utf-8"))
                  if r["split"] == "dev")


def cells(images) -> set[str]:
    return {f"{i}/{a}" for i in images for a in ARMS}


def probe_file(condition: str, task: str) -> pathlib.Path:
    """v0.13's two wordings with totals are read from v0.13's run, not rerun."""
    if condition == "no_totals":
        return OUT / f"no_totals_{task}.jsonl"
    return (V013 if task in V013_WORDINGS else OUT) / f"{task}.jsonl"


# --------------------------------------------------------------------------- #
# prepare, power, sheet
# --------------------------------------------------------------------------- #


def prepare() -> int:
    if any((CAL / n).exists() for n in ("dev_ids.txt", "repro_ids.txt")):
        sys.exit(f"{CAL} already holds the ids; they are drawn once")
    CAL.mkdir(parents=True, exist_ok=True)
    dev = dev_images()
    repro = sorted(random.Random(SEED).sample(dev, REPRO_IMAGES))
    (CAL / "dev_ids.txt").write_text("\n".join(dev) + "\n", encoding="utf-8")
    (CAL / "repro_ids.txt").write_text("\n".join(repro) + "\n", encoding="utf-8")
    print(f"  {len(dev)} dev images, reproduction images {repro} -> {CAL}")
    return 0


def _se(pu: float, ps: float, n: int) -> float:
    """SE of the told contrast when both cells of a pair always agree (worst case)."""
    return ((pu * (1 - pu) + ps * (1 - ps)) / n) ** 0.5


def _solve(f, lo: float, hi: float) -> float:
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
    return (lo + hi) / 2


def power() -> int:
    n, nd = len(dev_images()), statistics.NormalDist()
    ps = 0.05

    def acts(pu):
        return nd.cdf((pu - ps - HIGH) / _se(pu, ps, n) - Z95)

    def not_acts(pu):
        return nd.cdf((LOW - (pu - ps)) / _se(pu, ps, n) - Z95)

    print(f"  n images: {n}; escalation on satisfiable cells assumed {ps:.2f}")
    for pu in (0.80, 0.70):
        print(f"  P(ACTS WHEN TOLD) if unsatisfiable cells escalate at {pu:.2f}: {acts(pu):.2f}")
    print(f"  80% power for ACTS at unsatisfiable escalation "
          f"{_solve(lambda p: acts(p) - 0.80, HIGH, 1.0):.2f}")
    for pu in (0.05, 0.10):
        print(f"  P(DOES NOT ACT) if unsatisfiable cells escalate at {pu:.2f}: "
              f"{not_acts(pu):.2f}")

    # The reliability bar: a wording that never misses and false-alarms at rate f
    # has K = 1 - f and, worst case, SD sqrt(f(1 - f)).
    def lower(f):
        return (1 - f) - Z95 * (f * (1 - f) / n) ** 0.5
    f = _solve(lambda f: RELIABLE - lower(f), 0.0, 0.5)
    print(f"  a self-verdict clears K > {RELIABLE} if it misses nothing and "
          f"false-alarms on at most {f:.1%} of satisfiable cells")

    # No-totals: v0.13's pooled K on these images, against a worst-case K without
    dev = set(dev_images())
    k = {}
    for w in V013_WORDINGS:
        for r in rows(V013 / f"{w}.jsonl"):
            if r["scenario_id"] in dev:
                k.setdefault(key(r), []).append(says_short(r["prose"], w))
    sd_t = statistics.stdev(contrasts({c: knows(v) for c, v in k.items()}, dev).values())
    se = ((0.25 + sd_t ** 2) / n) ** 0.5
    print(f"  no totals: SD of v0.13 K on dev {sd_t:.3f}, worst-case SD without totals 0.500;"
          f" 95% half-width of the change {Z95 * se:.3f}")
    return 0


def sheet() -> int:
    names = ("sheet.md", "labels_blank.csv", "key.csv")
    if any((CAL / n).exists() for n in names):
        sys.exit(f"{CAL} already holds the label sheet; it is drawn once")
    plans = {key(r): r for r in rows(TOLD)}
    if set(plans) != cells(dev_images()):
        sys.exit(f"{TOLD} does not hold exactly the {4 * len(dev_images())} dev cells")
    order = sorted(plans)
    random.Random(SEED).shuffle(order)
    with (CAL / "sheet.md").open("w", encoding="utf-8", newline="\n") as md, \
         (CAL / "labels_blank.csv").open("w", encoding="utf-8", newline="") as lb, \
         (CAL / "key.csv").open("w", encoding="utf-8", newline="") as kf:
        blank, keyw = csv.writer(lb, lineterminator="\n"), csv.writer(kf, lineterminator="\n")
        blank.writerow(["row", "escalate", "notes"])
        keyw.writerow(["row", "scenario_id", "arm"])
        md.write(f"# v0.13b ESCALATE labels ({len(order)} plans)\n\n"
                 "Copy labels_blank.csv to labels_a.csv (or labels_b.csv) and label "
                 "`escalate` there by the escalate rule in cal/d11/LABELLING.md.\n")
        for n, c in enumerate(order, 1):
            row = f"T{n:03d}"
            blank.writerow([row, "", ""])
            keyw.writerow([row, *c.split("/")])
            md.write(f"\n---\n\n## {row}\n\n```text\n{scored_text(plans[c]['prose'])}\n```\n")
    print(f"  {len(order)} told plans -> {CAL}")
    return 0


# --------------------------------------------------------------------------- #
# report
# --------------------------------------------------------------------------- #


def told_labels(name: str) -> dict[str, bool]:
    rowkey = {r["row"]: f"{r['scenario_id']}/{r['arm']}"
              for r in csv.DictReader((CAL / "key.csv").open(encoding="utf-8"))}
    lab = {rowkey[r["row"]]: _bool(r["escalate"], f"{name} {r['row']}")
           for r in csv.DictReader((CAL / f"labels_{name}.csv").open(encoding="utf-8"))}
    if set(lab) != set(rowkey.values()):
        sys.exit(f"labels_{name}.csv does not label every told plan")
    return lab


def verdict(lo: float, hi: float) -> str:
    if lo > HIGH:
        return "ACTS WHEN TOLD"
    if hi < LOW:
        return "DOES NOT ACT WHEN TOLD"
    return "IN BETWEEN"


def no_totals_verdict(lo: float, hi: float) -> str:
    if hi < -LOW:
        return "COLLAPSES"
    if lo > -LOW:
        return "HOLDS"
    return "UNCLEAR"


def _problems(path: pathlib.Path, condition: str, task: str, want: set[str],
              only_dev: bool) -> list[str]:
    """Halt conditions for one output file: digest, image split, one row per cell."""
    if not path.exists():
        return [f"{path.relative_to(REPO)} missing"]
    rs = rows(path)
    dev = {c.split("/")[0] for c in want}
    if not only_dev:
        rs = [r for r in rs if r["scenario_id"] in dev]
    ks = [key(r) for r in rs]
    out = []
    if any(r["domain_digest"] != domain_digest(condition, task) for r in rs):
        out.append("another prompt's digest")
    if any(r["scenario_id"] not in dev for r in rs):
        out.append("a row from outside the dev split")
    if len(ks) != len(set(ks)) or set(ks) != want:
        out.append(f"{len(set(ks))} cells, want {len(want)}")
    return [f"{path.relative_to(REPO)}: {p}" for p in out]


def _repro(L: list[str], name: str, got: pathlib.Path, ref: dict[str, str],
           want: set[str]) -> bool:
    rs = rows(got) if got.exists() else []
    same = [key(r) for r in rs if r["prose"] == ref.get(key(r))]
    ok = {key(r) for r in rs} == want and len(same) == len(want)
    L.append(f"  reproduction, {name}: {len(same)}/{len(want)} byte-identical"
             f" -> {'PASS' if ok else 'FAIL'}")
    return ok


def halt_checks(L: list[str], dev: list[str]) -> bool:
    L.append("0. Halt checks")
    repro = (CAL / "repro_ids.txt").read_text(encoding="utf-8").split()
    want = cells(repro)
    ok = _repro(L, "v0.10 plans", OUT / "repro_plan.jsonl",
                {key(r): r["prose"] for a in ARMS
                 for r in rows(REPO / f"results/gen_{a}_blind.jsonl")}, want)
    for w in V013_WORDINGS:
        ok &= _repro(L, f"v0.13 {w}", OUT / f"repro_{w}.jsonl",
                     {key(r): r["prose"] for r in rows(V013 / f"{w}.jsonl")}, want)
    files = [(TOLD, "told", "plan", True)]
    files += [(probe_file("blind", w), "blind", w, w not in V013_WORDINGS) for w in WITH_TOTALS]
    files += [(probe_file("no_totals", w), "no_totals", w, True) for w in V013_WORDINGS]
    bad = [p for f in files for p in _problems(*f[:3], cells(dev), f[3])]
    told_ex = rows(TOLD_EX) if TOLD_EX.exists() else []
    if {key(r["plan"]) for r in told_ex} != cells(dev) or any(
            r.get("domain_digest") != domain_digest("told", "plan") for r in told_ex):
        bad.append(f"{TOLD_EX.relative_to(REPO)}: not the told plans' extraction")
    L += [f"  {b}" for b in bad]
    L.append(f"  every file: dev images only, one row per cell, its prompt's digest"
             f" -> {'PASS' if not bad else 'FAIL'}")
    ok &= not bad
    if not ok:
        L.append("  HALT: nothing below is analysed")
    return ok


def ci_text(xs: list[float]) -> str:
    if len(xs) < 2:
        return "n/a"
    m, lo, hi = ci95(xs)
    return f"{m:+.3f} [{lo:+.3f}, {hi:+.3f}]"


def rate(xs: list[float]) -> str:
    return f"{sum(xs) / len(xs):.1%}" if xs else "n/a"


def k_scores(read: dict[str, bool | None]) -> dict[str, float]:
    return {c: float(v) for c, v in read.items() if v is not None}


def complete(score: dict[str, float], dev: list[str]) -> set[str]:
    return {i for i in dev if all(f"{i}/{a}" in score for a in ARMS)}


def build_report() -> tuple[list[str], int]:
    L = ["RCP v0.13b dev-split diagnostic (plan_v013b.md)", "=" * 47]
    dev = dev_images()
    if not halt_checks(L, dev):
        return L, 2
    devset = set(dev)

    # ---- told-verdict plans ------------------------------------------------
    ex_told = {key(r["plan"]): r for r in rows(TOLD_EX)}
    ex_blind = {c: r for c, r in extracted("blind").items() if c.split("/")[0] in devset}
    lab = {"labels A": told_labels("a"), "labels B": told_labels("b")}
    blind_acts = {n: {c: v for c, v in s.items() if c.split("/")[0] in devset}
                  for n, s in labelled_acts().items()}
    told_acts = {**{n: {c: float(v) for c, v in lb.items()} for n, lb in lab.items()},
                 "extractor": {c: float(r["plan"]["escalate"]) for c, r in ex_told.items()}}

    L.append(f"\n1. PRIMARY: told-verdict plans, ESCALATE contrast (unsatisfiable minus "
             f"satisfiable), n = {len(dev)}")
    calls = []
    for n in ("labels A", "labels B", "extractor"):
        m, lo, hi = ci95(list(contrasts(told_acts[n], devset).values()))
        v = verdict(lo, hi)
        if n != "extractor":
            calls.append(v)
        L.append(f"  {n:<10}: E_told = {m:+.3f} [{lo:+.3f}, {hi:+.3f}] -> {v}"
                 + ("   (printed, not the primary)" if n == "extractor" else ""))
    L.append("  -> " + (calls[0] if calls[0] == calls[1]
                        else "LABELLER-DEPENDENT: A and B disagree; no verdict"))
    for n in ("labels A", "labels B"):
        m, lo, hi = ci95(list(contrasts(blind_acts[n], devset).values()))
        L.append(f"  for comparison, v0.10 blind on these images ({n}, cal/v013): "
                 f"{m:+.3f} [{lo:+.3f}, {hi:+.3f}]")

    L.append("\n2. ESCALATE per arm: told plans, and v0.10 blind on the same images")
    L.append(f"  {'arm':<12}" + "".join(f"{h:>18}" for h in (
        "told A", "told B", "told ext", "blind A", "blind B", "blind ext")))
    for a in ARMS:
        L.append(f"  {a:<12}" + "".join(
            f"{pct([bool(x) for x in in_arm(s, a)]):>18}"
            for s in (*told_acts.values(), *(blind_acts[n] for n in (
                "labels A", "labels B", "extractor")))))

    L.append("\n3. Beside ESCALATE (labels A): does the plan change, or only say so?")
    vt = verdicts(ex_told, lab["labels A"])
    vb = verdicts(ex_blind, {c: bool(v) for c, v in blind_acts["labels A"].items()})
    L.append(f"  {'arm':<12}{'':<7}" + "".join(f"{h:>18}" for h in (
        "AR", "OVERCOMMIT", "V2a pass", "V3 pass", "RESOURCE-VALID")))
    for a in ARMS:
        for name, vs in (("told", vt), ("blind", vb)):
            v = in_arm(vs, a)
            cols = ([r.appropriate_response for r in v], [r.overcommit for r in v],
                    [r.passed("V2a") for r in v], [r.passed("V3") for r in v],
                    [r.resource_valid for r in v])
            L.append(f"  {a if name == 'told' else '':<12}{name:<7}"
                     + "".join(f"{pct(c):>18}" for c in cols))
    for n, lb in lab.items():
        esc = [c for c in vt if lb[c] and c.split("/")[1] in UNSAT]
        L.append(f"  unsatisfiable told plans escalating ({n}) that still commit a late "
                 f"asset (fail V2a): {pct([not vt[c].passed('V2a') for c in esc])}")

    # ---- probes --------------------------------------------------------------
    L.append(f"\n4. Probes on the {len(dev)} dev images ('short' = says the ledger falls short)")
    L.append(f"  {'totals':<8}{'wording':<16}{'parsed':>10}{'short, unsat':>16}"
             f"{'short, sat':>14}   K [95% CI] (complete-case n)")
    read: dict[tuple[str, str], dict[str, bool | None]] = {}
    for cond, ws in (("blind", WITH_TOTALS), ("no_totals", V013_WORDINGS)):
        for w in ws:
            rd = {key(r): says_short(r["prose"], w) for r in rows(probe_file(cond, w))
                  if r["scenario_id"] in devset}
            read[cond, w] = rd
            ks = k_scores(rd)
            im = complete(ks, dev)
            un = [v for c, v in ks.items() if c.split("/")[1] in UNSAT]
            sa = [v for c, v in ks.items() if c.split("/")[1] in SAT]
            L.append(f"  {'yes' if cond == 'blind' else 'no':<8}{w:<16}"
                     f"{f'{len(ks)}/{len(rd)}':>10}{rate(un):>16}{rate(sa):>14}   "
                     f"{ci_text(list(contrasts(ks, im).values()))} ({len(im)})")

    L.append(f"\n5. Without the totals line: change in K (no totals minus totals), paired")
    pooled = {}
    for cond in ("blind", "no_totals"):
        pooled[cond] = {c: knows([read[cond, w].get(c) for w in V013_WORDINGS])
                        for c in cells(dev)}
        pooled[cond] = {c: v for c, v in pooled[cond].items() if v is not None}
    for name, sc in (("pooled (decides)", pooled),
                     *((w, {cond: k_scores(read[cond, w]) for cond in pooled})
                       for w in V013_WORDINGS)):
        im = complete(sc["blind"], dev) & complete(sc["no_totals"], dev)
        kt, kn = contrasts(sc["blind"], im), contrasts(sc["no_totals"], im)
        d = [kn[i] - kt[i] for i in sorted(im)]
        L.append(f"  {name:<18}: {ci_text(d)} (n = {len(im)})"
                 + (f" -> {no_totals_verdict(*ci95(d)[1:]) if len(d) > 1 else 'UNCLEAR'}"
                    if name.startswith("pooled") else ""))

    L.append(f"\n6. Verdict source for v0.14: the wording with totals with the highest K")
    best = None
    for w in WITH_TOTALS:
        ks = k_scores(read["blind", w])
        xs = list(contrasts(ks, complete(ks, dev)).values())
        if len(xs) < 2:
            continue
        m, lo, _ = ci95(xs)
        if best is None or m > best[1]:
            best = (w, m, lo, len(ks) / len(read["blind", w]))
    w, m, lo, parsed = best or ("no wording", 0.0, 0.0, 0.0)
    ok = lo > RELIABLE and parsed >= PARSE_MIN
    L.append(f"  {w}: K = {m:+.3f}, lower bound {lo:+.3f} (needs > {RELIABLE}), parsed "
             f"{parsed:.1%} (needs >= {PARSE_MIN:.0%})")
    L.append(f"  -> {'SELF-VERDICT in ' + w if ok else 'COMPUTED VERDICT: no wording is reliable'}")
    return L, 0


def report() -> int:
    dest = OUT / "report.txt"
    if dest.exists():
        sys.exit(f"{dest} exists; a report is written once")
    # A step not yet done is not a halt: write nothing until its output exists.
    todo = [p.relative_to(REPO) for p in (TOLD_EX, CAL / "labels_a.csv", CAL / "labels_b.csv")
            if not p.exists()]
    if todo:
        sys.exit(f"not yet there, nothing written: {', '.join(map(str, todo))}")
    L, code = build_report()
    dest.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return code


def check() -> int:
    L, _ = build_report()
    same = (OUT / "report.txt").read_text(encoding="utf-8") == "\n".join(L) + "\n"
    print(f"  report.txt {'reproduces byte for byte' if same else 'DIFFERS'}")
    return 0 if same else 1


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    cmds = {"prepare": prepare, "power": power, "sheet": sheet, "report": report,
            "check": check}
    if cmd not in cmds:
        sys.exit(__doc__)
    return cmds[cmd]()


if __name__ == "__main__":
    raise SystemExit(main())
