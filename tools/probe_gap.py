"""plan_v013.md: the knowing-doing probe. Prepare, power, report.

    python3 tools/probe_gap.py prepare   # cal/v013/: ESCALATE check sheet, repro ids
    python3 tools/probe_gap.py power     # plan_v013.md §6's power figures
    python3 tools/probe_gap.py report    # results/v013_probe/report.txt
    python3 tools/probe_gap.py check     # rebuild the report, compare byte for byte
    python3 tools/probe_gap.py posthoc   # results/v013_probe/posthoc.txt (D13)

`prepare`, `report` and `posthoc` refuse to overwrite. Run in the container from
the repo root. Every number in plan_v013.md, its report and D13 is printed here.
`posthoc` is not pre-registered and says so.
"""

from __future__ import annotations

import csv
import json
import pathlib
import random
import statistics
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from rcp import corpus, extract_det as ed  # noqa: E402
from rcp.calibrate import _bool  # noqa: E402
from rcp.probe import knows, says_short  # noqa: E402
from rcp.render import domain_digest  # noqa: E402
from rcp.report import ARMS, Z95  # noqa: E402

SEED = 20261014
MARGIN = 0.20
NEG_PER_ARM = 9
REPRO_IMAGES = 3
UNSAT, SAT = ("SCARCE", "INFEASIBLE"), ("SURPLUS", "SUFFICIENT")
WORDINGS = ("probe_can", "probe_short")
CAL = REPO / "cal/v013"
OUT = REPO / "results/v013_probe"
EXTRACTED = REPO / "results/ex_blind_all.jsonl"


def rows(path: pathlib.Path) -> list[dict]:
    return [json.loads(ln) for ln in path.open(encoding="utf-8") if ln.strip()]


def key(r: dict) -> str:
    return f"{r['scenario_id']}/{r['arm']}"


def v010_escalate() -> dict[str, bool]:
    """The study's ESCALATE flag per blind cell, from its frozen extraction."""
    return {key(r["plan"]): bool(r["plan"]["escalate"]) for r in rows(EXTRACTED)}


def v010_plans() -> dict[str, dict]:
    return {key(r): r for a in ARMS for r in rows(REPO / f"results/gen_{a}_blind.jsonl")}


def scored_text(prose: str) -> str:
    """The plan as extraction scores it (header, contingencies, loops removed)."""
    plan = ed.split_header(prose)[1]
    plan = ed.split_contingencies(plan)[0]
    return ed.trim_repeated_steps(plan)[0]


# --------------------------------------------------------------------------- #
# prepare
# --------------------------------------------------------------------------- #


def sample() -> list[str]:
    """Every extractor-positive cell plus NEG_PER_ARM negatives per arm, shuffled."""
    esc = v010_escalate()
    rng = random.Random(SEED)
    picked = sorted(k for k, e in esc.items() if e)
    for arm in ARMS:
        neg = sorted(k for k, e in esc.items() if not e and k.endswith("/" + arm))
        picked += rng.sample(neg, NEG_PER_ARM)
    rng.shuffle(picked)
    return picked


def repro_images() -> list[str]:
    ids = sorted({k.split("/")[0] for k in v010_escalate()})
    return sorted(random.Random(SEED).sample(ids, REPRO_IMAGES))


def prepare() -> int:
    names = ("sheet.md", "labels_blank.csv", "key.csv", "repro_ids.txt")
    if any((CAL / n).exists() for n in names):
        sys.exit(f"{CAL} already holds the sheet; it is drawn once")
    CAL.mkdir(parents=True, exist_ok=True)
    plans, cells = v010_plans(), sample()
    with (CAL / "sheet.md").open("w", encoding="utf-8", newline="\n") as md, \
         (CAL / "labels_blank.csv").open("w", encoding="utf-8", newline="") as lb, \
         (CAL / "key.csv").open("w", encoding="utf-8", newline="") as kf:
        blank, keyw = csv.writer(lb, lineterminator="\n"), csv.writer(kf, lineterminator="\n")
        blank.writerow(["row", "escalate", "notes"])
        keyw.writerow(["row", "scenario_id", "arm"])
        md.write(f"# v0.13 ESCALATE check ({len(cells)} plans)\n\n"
                 "Label `escalate` in labels_blank.csv by the escalate rule in "
                 "cal/d11/LABELLING.md.\n")
        for n, k in enumerate(cells, 1):
            row = f"R{n:02d}"
            blank.writerow([row, "", ""])
            keyw.writerow([row, *k.split("/")])
            md.write(f"\n---\n\n## {row}\n\n```text\n{scored_text(plans[k]['prose'])}\n```\n")
    (CAL / "repro_ids.txt").write_text("\n".join(repro_images()) + "\n", encoding="utf-8")
    print(f"  {len(cells)} plans ({sum(v010_escalate()[k] for k in cells)} extractor-positive)"
          f", repro images {repro_images()} -> {CAL}")
    return 0


# --------------------------------------------------------------------------- #
# statistics
# --------------------------------------------------------------------------- #


def contrasts(score: dict[str, float], images: set[str]) -> dict[str, float]:
    """Per image: mean over the unsatisfiable arms minus mean over the satisfiable."""
    return {i: (sum(score[f"{i}/{a}"] for a in UNSAT)
                - sum(score[f"{i}/{a}"] for a in SAT)) / 2 for i in sorted(images)}


def ci95(xs: list[float]) -> tuple[float, float, float]:
    m, se = statistics.fmean(xs), statistics.stdev(xs) / len(xs) ** 0.5
    return m, m - Z95 * se, m + Z95 * se


def verdict(lo: float, hi: float) -> str:
    if lo > MARGIN:
        return f"GAP: knows exceeds acts by more than {MARGIN}"
    if hi < MARGIN:
        return f"NO GAP: any gap is below {MARGIN}"
    return "INCONCLUSIVE"


def power() -> int:
    """Worst-case probe variance; the acts term's SD from v0.10's own flags."""
    esc = {k: float(v) for k, v in v010_escalate().items()}
    images = {k.split("/")[0] for k in esc}
    sd_e = statistics.stdev(contrasts(esc, images).values())
    var_k = 0.25   # k in {0, 1} with p = .5 in every arm, arms independent
    n = len(images)
    se = ((var_k + sd_e ** 2) / n) ** 0.5
    nd = statistics.NormalDist()

    def p_gap(g):
        return nd.cdf((g - MARGIN) / se - Z95)

    def p_none(g):
        return nd.cdf((MARGIN - g) / se - Z95)

    g80 = MARGIN + (Z95 + nd.inv_cdf(0.80)) * se
    print(f"  n images                         : {n}")
    print(f"  SD of v0.10 acts contrast        : {sd_e:.3f}")
    print(f"  worst-case SD of knows contrast  : {var_k ** 0.5:.3f}")
    print(f"  SE of the gap (independent terms): {se:.4f}; 95% half-width {Z95 * se:.3f}")
    print(f"  power to find GAP at G = 0.35    : {p_gap(0.35):.2f}")
    print(f"  G with 80% power for GAP         : {g80:.3f}")
    print(f"  power to find NO GAP at G = 0.05 : {p_none(0.05):.2f}")
    print(f"  inconclusive band (true G)       : about {MARGIN - Z95 * se:.2f} to "
          f"{MARGIN + Z95 * se:.2f}")
    return 0


# --------------------------------------------------------------------------- #
# report
# --------------------------------------------------------------------------- #


def labels(name: str) -> dict[str, bool]:
    rowkey = {r["row"]: f"{r['scenario_id']}/{r['arm']}"
              for r in csv.DictReader((CAL / "key.csv").open(encoding="utf-8"))}
    return {rowkey[r["row"]]: _bool(r["escalate"], f"{name} {r['row']}")
            for r in csv.DictReader((CAL / f"labels_{name}.csv").open(encoding="utf-8"))}


def probe_reads() -> dict[str, dict[str, bool | None]]:
    """Per cell, per wording: does the answer say the ledger falls short."""
    read: dict[str, dict[str, bool | None]] = {}
    for w in WORDINGS:
        rs = rows(OUT / f"{w}.jsonl")
        bad = {r["domain_digest"] for r in rs} - {domain_digest("blind", w)}
        if bad:
            sys.exit(f"{w}.jsonl carries another prompt's digest: {sorted(bad)}")
        for r in rs:
            read.setdefault(key(r), {})[w] = says_short(r["prose"], w)
    return read


def labelled_acts() -> dict[str, dict[str, float]]:
    """The acts score per cell: the extractor's flag, and with labels A or B."""
    esc = v010_escalate()
    acts = {"extractor": {c: float(v) for c, v in esc.items()}}
    for n in ("a", "b"):
        lb = labels(n)
        acts[f"labels {n.upper()}"] = {c: float(lb.get(c, v)) for c, v in esc.items()}
    return acts


def repro(L: list[str]) -> bool:
    """Halt rule: the regenerated v0.10 cells must be byte-identical."""
    plans = v010_plans()
    got = rows(OUT / "repro_plan.jsonl")
    want = {f"{i}/{a}" for i in (CAL / "repro_ids.txt").read_text().split() for a in ARMS}
    same = [key(r) for r in got if r["prose"] == plans[key(r)]["prose"]]
    ok = {key(r) for r in got} == want and len(same) == len(want)
    L.append(f"  reproduction: {len(same)}/{len(want)} v0.10 cells byte-identical"
             f" -> {'PASS' if ok else 'FAIL: HALT, nothing below is analysed'}")
    return ok


def build_report() -> tuple[list[str], int]:
    L = ["RCP v0.13 knowing-doing probe (plan_v013.md)", "=" * 44]
    if not repro(L):
        return L, 2

    sat = {k: sc.ledger_satisfiable for k, sc in corpus.by_key().items()}
    read = probe_reads()
    k = {c: knows(list(v.values())) for c, v in read.items()}
    images = {c.split("/")[0] for c in k
              if all(k.get(f"{c.split('/')[0]}/{a}") is not None for a in ARMS)}

    L.append("\n1. Parse rate and 'falls short' rate, per arm and wording")
    L.append(f"  {'arm':<12}{'parsed can':>12}{'parsed short':>14}{'short (can)':>13}"
             f"{'short (short)':>15}{'polarity agree':>16}")
    for a in ARMS:
        cs = [c for c in read if c.endswith("/" + a)]
        cell = []
        for w in WORDINGS:
            v = [read[c].get(w) for c in cs]
            p = [x for x in v if x is not None]
            cell += [f"{len(p)}/{len(v)}", f"{sum(p) / len(p):.1%}" if p else "n/a"]
        both = [c for c in cs if None not in (read[c].get(WORDINGS[0]), read[c].get(WORDINGS[1]))]
        agree = sum(read[c][WORDINGS[0]] == read[c][WORDINGS[1]] for c in both)
        L.append(f"  {a:<12}{cell[0]:>12}{cell[2]:>14}{cell[1]:>13}{cell[3]:>15}"
                 f"{f'{agree}/{len(both)}':>16}")
    L.append(f"  complete-case images: {len(images)}")

    esc = v010_escalate()
    acts = labelled_acts()
    lab = {n: labels(n) for n in ("a", "b")}
    K = contrasts(k, images)

    L.append("\n2. Contrasts (unsatisfiable minus satisfiable arms), paired 95% CI")
    m, lo, hi = ci95(list(K.values()))
    L.append(f"  knows (probe)            : {m:+.3f} [{lo:+.3f}, {hi:+.3f}]")
    for w in WORDINGS:
        kw = {c: float(v[w]) for c, v in read.items() if v.get(w) is not None}
        im = {i for i in images if all(f"{i}/{a}" in kw for a in ARMS)}
        m, lo, hi = ci95(list(contrasts(kw, im).values()))
        L.append(f"    {w:<22} : {m:+.3f} [{lo:+.3f}, {hi:+.3f}]  (n = {len(im)})")
    E = {}
    for n, s in acts.items():
        E[n] = contrasts(s, images)
        m, lo, hi = ci95(list(E[n].values()))
        L.append(f"  acts (v0.10 ESCALATE, {n:<10}): {m:+.3f} [{lo:+.3f}, {hi:+.3f}]")

    L.append(f"\n3. PRIMARY: gap G = knows - acts, margin {MARGIN} (n = {len(images)})")
    verdicts = []
    for n in ("labels A", "labels B", "extractor"):
        g = [K[i] - E[n][i] for i in sorted(images)]
        m, lo, hi = ci95(g)
        v = verdict(lo, hi)
        if n != "extractor":
            verdicts.append(v)
        L.append(f"  acts from {n:<10}: G = {m:+.3f} [{lo:+.3f}, {hi:+.3f}] -> {v}"
                 + ("   (printed, not the primary)" if n == "extractor" else ""))
    L.append("  -> " + (verdicts[0] if verdicts[0] == verdicts[1]
                        else "LABELLER-DEPENDENT: A and B disagree; no verdict"))

    L.append("\n4. ESCALATE check: extractor against labels on the sampled cells")
    for n, lb in lab.items():
        pos = [c for c in lb if esc[c]]
        neg = [c for c in lb if not esc[c]]
        L.append(f"  labels {n.upper()}: extractor-positive confirmed {sum(lb[c] for c in pos)}"
                 f"/{len(pos)}; extractor-negative found escalating {sum(lb[c] for c in neg)}"
                 f"/{len(neg)}")

    L.append("\n5. Cell level, unsatisfiable cells; k = 1 or 0 (descriptive)")
    for n in ("labels A", "labels B"):
        for val, name in ((1.0, "probe says short"), (0.0, "probe says enough")):
            cs = [c for c in k if k[c] == val and not sat[c] and c.split("/")[0] in images]
            e = sum(acts[n][c] for c in cs)
            L.append(f"  {name:<26}: {len(cs):>3} cells, plan escalates ({n}) {int(e)}"
                     + (f" ({e / len(cs):.1%})" if cs else ""))
    return L, 0


def report() -> int:
    dest = OUT / "report.txt"
    if dest.exists():
        sys.exit(f"{dest} exists; a report is written once")
    L, code = build_report()
    dest.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return code


def check() -> int:
    """Rebuild the report from the frozen outputs and labels; it must match."""
    L, _ = build_report()
    same = (OUT / "report.txt").read_text(encoding="utf-8") == "\n".join(L) + "\n"
    print(f"  report.txt {'reproduces byte for byte' if same else 'DIFFERS'}")
    return 0 if same else 1


def posthoc() -> int:
    """D13's numbers that plan_v013.md did not pre-register. Not tests."""
    dest = OUT / "posthoc.txt"
    if dest.exists():
        sys.exit(f"{dest} exists; it is written once")
    read, acts = probe_reads(), labelled_acts()
    images = {c.split("/")[0] for c in read}
    L = ["RCP v0.13 probe: post hoc, NOT pre-registered (docs/deviations.md D13)",
         "=" * 70, "\n1. Gap per wording (plan_v013.md pre-registers only the pooled gap)"]
    for n in ("labels A", "labels B"):
        E = contrasts(acts[n], images)
        for w in WORDINGS:
            K = contrasts({c: float(v[w]) for c, v in read.items()}, images)
            m, lo, hi = ci95([K[i] - E[i] for i in sorted(images)])
            L.append(f"  {n}, {w:<12}: G = {m:+.3f} [{lo:+.3f}, {hi:+.3f}]")
    L.append("\n2. Plan escalates, per arm (v0.10 blind; the extractor and the two label sets)")
    L.append(f"  {'arm':<12}" + "".join(f"{n:>12}" for n in acts))
    for a in ARMS:
        cs = [c for c in acts["extractor"] if c.endswith("/" + a)]
        L.append(f"  {a:<12}" + "".join(f"{sum(s[c] for c in cs) / len(cs):>12.1%}"
                                        for s in acts.values()))
    sat = [c for c in read if c.split("/")[1] in SAT]
    both = [c for c in sat if read[c]["probe_can"] and not read[c]["probe_short"]]
    L.append(f"\n3. Satisfiable cells answering NO to both wordings: {len(both)}/{len(sat)}")
    prose = {w: {key(r): r["prose"] for r in rows(OUT / f"{w}.jsonl")} for w in WORDINGS}
    L.append("\n4. Five of those, drawn with seed {} (plan_v013.md §7: read to describe)"
             .format(SEED))
    for c in sorted(random.Random(SEED).sample(both, 5)):
        L.append(f"  {c}")
        for w in WORDINGS:
            L.append(f"    {w:<12}: " + prose[w][c][:300].replace("\n", " | "))
    dest.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    cmds = {"prepare": prepare, "power": power, "report": report, "check": check,
            "posthoc": posthoc}
    if cmd not in cmds:
        sys.exit(__doc__)
    return cmds[cmd]()


if __name__ == "__main__":
    raise SystemExit(main())
