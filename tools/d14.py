"""D14: close the v0.10/v0.13 record. Post hoc; recomputed from frozen outputs.

    python3 tools/d14.py report   # results/d14/report.txt (written once)
    python3 tools/d14.py check    # rebuild the report, compare byte for byte
    python3 tools/d14.py split    # cal/track_e/split.csv: Track E dev/test (drawn once)
    python3 tools/d14.py read     # cal/d14/: the plan.md §10.3 blind read sheet (drawn once)
    python3 tools/d14.py rerate   # cal/d14/: re-rate sheet, once read.csv is filled
    python3 tools/d14.py human    # results/d14/human.txt: the read summarised (written once)

Nothing here is a new test. Sections the plan pre-specified but never ran say
so; the rest are labelled post hoc. Run in the container from the repo root.
"""

from __future__ import annotations

import collections
import csv
import dataclasses
import functools
import json
import math
import pathlib
import random
import statistics
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from rcp import corpus  # noqa: E402
from rcp import report as R  # noqa: E402
from rcp.calibrate import _bool, _tokens  # noqa: E402
from rcp.render import scenario_block  # noqa: E402
from rcp.schema import ExtractedPlan  # noqa: E402
from rcp.validator import score  # noqa: E402
from tools.guard_check import REQUEST  # noqa: E402
from tools.probe_gap import labels as v013_labels, scored_text  # noqa: E402

ARMS = R.ARMS
SAT, UNSAT = ("SURPLUS", "SUFFICIENT"), ("SCARCE", "INFEASIBLE")
OUT = REPO / "results/d14"
SPLIT = REPO / "cal/track_e/split.csv"
READ = REPO / "cal/d14"
SEED = 20261019
DEV_IMAGES = 40          # Track E dev split; the other 70 images are its test set
READ_PER_ARM = 10        # plan.md §10.3: ~30-50 plans
RERATE_N = 15            # §10.3: a subset re-read about a week later, blind to the first
SIZE_BINS = ((12, 14), (15, 17), (18, 20))   # ledger sizes both satisfiable arms share


def rows(path: pathlib.Path) -> list[dict]:
    return [json.loads(ln) for ln in path.open(encoding="utf-8") if ln.strip()]


def key(d: dict) -> str:
    return f"{d['scenario_id']}/{d['arm']}"


def as_plan(d: dict) -> ExtractedPlan:
    return ExtractedPlan(
        scenario_id=d["scenario_id"], arm=d["arm"],
        assets_named=tuple(d.get("assets_named", ())),
        commitments=tuple(d.get("commitments", ())),
        goal_attempted=bool(d.get("goal_attempted", False)),
        escalate=bool(d.get("escalate", False)), reduce=bool(d.get("reduce", False)),
        step_count=int(d.get("step_count", 0)), word_count=int(d.get("word_count", 0)),
        conditional_steps=int(d.get("conditional_steps", 0)),
        parse_failed=bool(d.get("parse_failed", False)))


def extracted(cond: str) -> dict[str, dict]:
    return {key(r["plan"]): r for r in rows(REPO / f"results/ex_{cond}_all.jsonl")}


def verdicts(ex: dict[str, dict], escalate: dict[str, bool] | None = None) -> dict:
    """Score every cell, with ESCALATE replaced where `escalate` has a label."""
    sc = corpus.by_key()
    out = {}
    for k, r in ex.items():
        p = as_plan(r["plan"])
        if escalate and k in escalate:
            p = dataclasses.replace(p, escalate=escalate[k])
        out[k] = score(p, sc[k])
    return out


# --------------------------------------------------------------------------- #
# small statistics, stdlib only
# --------------------------------------------------------------------------- #


def binom_tail(k: int, n: int, p: float) -> float:
    """P(X >= k), X ~ Binomial(n, p)."""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def _solve(f, lo: float = 0.0, hi: float = 1.0) -> float:
    """Root of a function increasing in p on [lo, hi], by bisection."""
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
    return (lo + hi) / 2


def exact_ci(x: int, n: int) -> tuple[float, float]:
    """Clopper-Pearson 95% interval."""
    lo = 0.0 if x == 0 else _solve(lambda p: binom_tail(x, n, p) - 0.025)
    hi = 1.0 if x == n else _solve(lambda p: 0.025 - (1 - binom_tail(x + 1, n, p)))
    return lo, hi


def smallest_detectable(n: int, p0: float) -> float:
    """Exact one-sided binomial test of p <= p0 at alpha .05: the true rate with 80% power."""
    k = next(k for k in range(n + 1) if binom_tail(k, n, p0) <= 0.05)
    return _solve(lambda p: binom_tail(k, n, p) - 0.80)


def pct(xs: list[bool]) -> str:
    return f"{sum(xs) / len(xs):6.1%} ({sum(xs):>3}/{len(xs):<3})" if xs else "   n/a"


def in_arm(vs: dict, arm: str) -> list:
    return [v for k, v in sorted(vs.items()) if k.endswith("/" + arm)]


# --------------------------------------------------------------------------- #
# report
# --------------------------------------------------------------------------- #


def labelled() -> dict[str, dict[str, bool]]:
    return {"labels A": v013_labels("a"), "labels B": v013_labels("b")}


def sec_labelled(L: list[str]) -> None:
    ex = extracted("blind")
    sets = {"extractor": verdicts(ex), **{n: verdicts(ex, lb) for n, lb in labelled().items()}}
    L.append("\n1. v0.10 blind with ESCALATE checked by labels (cal/v013, 72 cells; others keep"
             "\n   the extractor's flag). The primary and P1' as pre-registered, re-run.")
    L.append(f"  {'':<10}{'arm':<12}{'AR':>18}{'ESCALATE':>18}{'OVERCOMMIT':>18}")
    for n, vs in sets.items():
        for a in ARMS:
            v = in_arm(vs, a)
            L.append(f"  {n:<10}{a:<12}{pct([x.appropriate_response for x in v]):>18}"
                     f"{pct([x.escalate for x in v]):>18}{pct([x.overcommit for x in v]):>18}")
    L.append("")
    for n, vs in sets.items():
        by: dict[str, dict[str, bool]] = {}
        for v in vs.values():
            by.setdefault(v.scenario_id, {})[v.arm] = v.appropriate_response
        eq = R.equivalence(R.contrasts(by))
        lo, hi = eq["ci90"]
        ec = R.escalation_contrast(list(vs.values()))
        L.append(f"  {n:<10} P4' D = {eq['change']:+.3f} 90% CI [{lo:+.3f}, {hi:+.3f}]"
                 f"  inside +/-{R.DELTA}: {'yes' if eq['equivalent'] else 'no'};"
                 f" wholly below -{R.DELTA}: {'yes' if hi < -R.DELTA else 'no'}")
        L.append(f"  {'':<10} P1' = {ec['diff']:+.3f} 95% CI [{ec['ci95'][0]:+.3f}, "
                 f"{ec['ci95'][1]:+.3f}]")
    L.append("  P4' is supported only if the CI is inside +/-delta (plan.md §9.2); §9.1 calls"
             "\n  any other CI 'refuted'. A decline beyond delta is shown only if the CI is"
             "\n  wholly below -delta.")

    esc = {k: bool(r["plan"]["escalate"]) for k, r in ex.items()}
    images = len({k.split("/")[0] for k in ex})
    L.append("  Labelled: every extractor-positive and 9 negatives per arm. Sampled negatives the"
             "\n  labels call escalating, and how far D would rise if every unchecked negative in"
             "\n  SCARCE/INFEASIBLE escalated at that rate (at the 95% upper rate):")
    for n, lb in labelled().items():
        neg = [k for k in lb if not esc[k]]
        x = sum(lb[k] for k in neg)
        lo, hi = exact_ci(x, len(neg))
        left = {a: sum(k.endswith("/" + a) and not esc[k] and k not in lb for k in esc)
                for a in UNSAT}
        rise = lambda p: R.TO_CHANGE * p * sum(  # noqa: E731
            R.SCORES[ARMS.index(a)] * left[a] for a in UNSAT) / images
        L.append(f"  {n}: {x}/{len(neg)} (95% {lo:.1%}-{hi:.1%}); D {rise(x / len(neg)):+.3f}"
                 f" ({rise(hi):+.3f}); unchecked {left['SCARCE']} + {left['INFEASIBLE']}")


def sec_p2(L: list[str]) -> None:
    """P2's MDE, never entered (plan.md §9.4); the OVERCOMMIT false-positive rate."""
    ex = extracted("blind")
    vs = verdicts(ex)
    suf = [v.overcommit for v in in_arm(vs, "SUFFICIENT")]
    lo, hi = exact_ci(sum(suf), len(suf))
    L.append("\n2. P2: OVERCOMMIT at SUFFICIENT. plan.md §9.4 left its MDE 'to be entered'"
             "\n   (§12.2 gate 1, never closed); entered here, after the run.")
    L.append(f"  observed {pct(suf)}, 95% CI [{lo:.1%}, {hi:.1%}]")
    L.append(f"  against p0 = 0: smallest rate detectable (n = {len(suf)}, exact one-sided .05,"
             f" power .80) = {smallest_detectable(len(suf), 0.0):.3f}")
    L.append("  extractor vs labels on the D11 held-out satisfiable cells: OVERCOMMIT the labels"
             "\n  do not give (95% upper); OVERCOMMIT missed; smallest rate detectable over"
             "\n  p0 = that upper false-positive rate:")
    sc = corpus.by_key()
    for name in ("a", "b"):
        gold = {}
        for r in csv.DictReader((REPO / f"cal/d11/labels_heldout_{name}.csv").open(encoding="utf-8")):
            k = key(r)
            gold[k] = score(ExtractedPlan(
                scenario_id=r["scenario_id"], arm=r["arm"],
                assets_named=tuple(sorted(_tokens(r["assets_named"]))),
                commitments=tuple(sorted(_tokens(r["commitments"]))),
                goal_attempted=_bool(r["goal_attempted"], k),
                escalate=_bool(r["escalate"], k), reduce=_bool(r["reduce"], k)), sc[k])
        cells = [k for k in gold if sc[k].ledger_satisfiable]
        neg = [k for k in cells if not gold[k].overcommit]
        pos = [k for k in cells if gold[k].overcommit]
        fp = sum(vs[k].overcommit for k in neg)
        fn = sum(not vs[k].overcommit for k in pos)
        fhi = exact_ci(fp, len(neg))[1]
        L.append(f"  labels {name.upper()}: {fp}/{len(neg)} ({fhi:.1%}); {fn}/{len(pos)};"
                 f" {smallest_detectable(len(suf), fhi):.3f}")


def sec_size(L: list[str]) -> None:
    """plan.md §7.2: asset count as a covariate (exploratory, §9.2). Never run."""
    vs = verdicts(extracted("blind"))
    sc = corpus.by_key()
    size = {k: len(s.ledger) for k, s in sc.items()}
    L.append("\n3. Asset count (plan.md §7.2, §9.2 exploratory; pre-specified, never reported)")
    for a in ARMS:
        n = [size[k] for k in vs if k.endswith("/" + a)]
        L.append(f"  {a:<12} assets: mean {statistics.fmean(n):5.1f}, median "
                 f"{statistics.median(n):4.1f}, range {min(n)}-{max(n)}")
    L.append(f"  {'':<12}{'split at arm median':<22}{'RESOURCE-VALID':>18}{'V2a':>18}{'V3':>18}")
    for a in SAT:
        ks = [k for k in sorted(vs) if k.endswith("/" + a)]
        med = statistics.median(size[k] for k in ks)
        for name, g in ((f"<= {med:g} assets", [k for k in ks if size[k] <= med]),
                        (f"> {med:g} assets", [k for k in ks if size[k] > med])):
            L.append(f"  {a:<12}{name:<22}{pct([vs[k].resource_valid for k in g]):>18}"
                     f"{pct([vs[k].passed('V2a') for k in g]):>18}"
                     f"{pct([vs[k].passed('V3') for k in g]):>18}")
    L.append("  same ledger size, both satisfiable arms (RESOURCE-VALID):")
    for lo, hi in SIZE_BINS:
        cell = [f"{a} {pct([vs[k].resource_valid for k in vs if k.endswith('/' + a) and lo <= size[k] <= hi])}"
                for a in SAT]
        L.append(f"    {lo}-{hi} assets: " + "   ".join(cell))
    L.append("  Unsatisfiable arms are not shown: RESOURCE-VALID is 0 there by construction.")


def sec_secondary(L: list[str]) -> None:
    """plan.md §5.1, §9.2: OVERCOMMIT decompositions, co-occurrence, casualty type."""
    ex = extracted("blind")
    vs = verdicts(ex)
    red = {n: json.loads((REPO / f"cal/d11/score_heldout_{n}_v010.json").read_text())
           ["bools"]["reduce"] for n in ("a", "b")}
    L.append("\n4. Pre-specified secondary/exploratory rows never printed (plan.md §5.1, §9.2);"
             "\n   extractor flags, unlabelled. REDUCE agrees with the D11 held-out labels on "
             + ", ".join(f"{r['agree']}/{r['n']} ({n.upper()}, {r['false_pos']} false positives)"
                         for n, r in red.items()))
    L.append(f"  {'arm':<12}{'OVERCOMMIT':>18}{'and not REDUCE':>18}{'and REDUCE':>18}")
    for a in ARMS:
        v = in_arm(vs, a)
        L.append(f"  {a:<12}{pct([x.overcommit for x in v]):>18}"
                 f"{pct([x.overcommit and not x.reduce for x in v]):>18}"
                 f"{pct([x.overcommit and x.reduce for x in v]):>18}")
    flags = ("hallucinate", "overcommit", "escalate", "reduce")
    L.append("  co-occurrence, all 440 cells (both flags set):")
    L.append(f"  {'':<12}" + "".join(f"{f.upper():>13}" for f in flags))
    for f in flags:
        L.append(f"  {f.upper():<12}" + "".join(
            f"{sum(getattr(v, f) and getattr(v, g) for v in vs.values()):>13}" for g in flags))
    L.append("  APPROPRIATE-RESPONSE by casualty state:")
    sc = corpus.by_key()
    states = sorted({s.casualty_state for s in sc.values()})
    L.append(f"  {'arm':<12}" + "".join(f"{s:>18}" for s in states))
    for a in ARMS:
        L.append(f"  {a:<12}" + "".join(
            f"{pct([v.appropriate_response for k, v in vs.items() if k.endswith('/' + a) and sc[k].casualty_state == s]):>18}"
            for s in states))
    L.append("  APPROPRIATE-RESPONSE by whether the plan looped or hit the token cap (post hoc):")
    L.append(f"  {'arm':<12}{'looped':>18}{'not looped':>18}{'truncated':>18}{'not truncated':>18}")
    for a in ARMS:
        ks = [k for k in sorted(vs) if k.endswith("/" + a)]
        lp = {k: (ex[k].get("looped_steps_dropped") or 0) > 0 for k in ks}
        tr = {k: bool(ex[k].get("truncated")) for k in ks}
        L.append(f"  {a:<12}" + "".join(
            f"{pct([vs[k].appropriate_response for k in ks if d[k] == want]):>18}"
            for d in (lp, tr) for want in (True, False)))


def sec_request(L: list[str]) -> None:
    """The broad 'asks for resources' regex (tools/guard_check.py) on v0.10 prose."""
    L.append("\n5. Plans matching the broad 'asks for more' regex (tools/guard_check.REQUEST;"
             "\n   unvalidated), v0.10 prose")
    for cond in ("blind", "stated"):
        cell = []
        for a in ARMS:
            ps = [r["prose"] for r in rows(REPO / f"results/gen_{a}_{cond}.jsonl")]
            cell.append(f"{a} {sum(bool(REQUEST.search(p)) for p in ps) / len(ps):.1%}")
        L.append(f"  {cond:<7}: " + "   ".join(cell))


def build_report() -> list[str]:
    L = ["RCP D14: v0.10 record, post hoc (docs/deviations.md D14)", "=" * 56,
         "Recomputed from frozen outputs (runs/v010.json, runs/v013_probe.json); none is a test.",
         "Sections 2-4 hold items plan.md pre-specified and never reported; the rest is new."]
    for sec in (sec_labelled, sec_p2, sec_size, sec_secondary, sec_request):
        sec(L)
    return L


def report() -> int:
    dest = OUT / "report.txt"
    if dest.exists():
        sys.exit(f"{dest} exists; a report is written once")
    L = build_report()
    OUT.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


# --------------------------------------------------------------------------- #
# Track E split (plan.md §12.4 item 2) and the §10.3 read
# --------------------------------------------------------------------------- #


def _csv(header: list[str], body: list[list[str]]) -> str:
    return "".join(",".join(r) + "\n" for r in [header, *body])


def split_text() -> str:
    """Dev/test by image, stratified on state, largest-remainder allocation."""
    man = list(csv.DictReader((REPO / "data/manifest.csv").open(encoding="utf-8")))
    by = collections.defaultdict(list)
    for r in man:
        by[r["state"]].append(r["id"])
    quota = {s: DEV_IMAGES * len(ids) / len(man) for s, ids in by.items()}
    n = {s: int(q) for s, q in quota.items()}
    for s in sorted(quota, key=lambda s: (n[s] - quota[s], s))[:DEV_IMAGES - sum(n.values())]:
        n[s] += 1
    rng = random.Random(SEED)
    dev = {i for s in sorted(by) for i in rng.sample(sorted(by[s]), n[s])}
    return _csv(["id", "state", "split"], [[r["id"], r["state"], "dev" if r["id"] in dev
                                            else "test"] for r in sorted(man, key=lambda r: r["id"])])


@functools.cache
def _images() -> dict[str, str]:
    return {r["id"]: r["image"] for r in
            csv.DictReader((REPO / "data/manifest.csv").open(encoding="utf-8"))}


@functools.cache
def _prose() -> dict[str, str]:
    return {key(r): r["prose"] for a in ARMS for r in rows(REPO / f"results/gen_{a}_blind.jsonl")}


def _entry(row: str, k: str) -> str:
    sc = corpus.by_key()[k]
    return (f"\n---\n\n## {row}\n\nImage: `{_images()[sc.id]}`\n\n```text\n"
            f"{scenario_block(sc, 'blind')}\n```\n\nPlan (repeated steps removed):\n\n"
            f"```text\n{scored_text(_prose()[k])}\n```\n")


def _sheet(title: str, blank: str, cells: list[tuple[str, str]]) -> str:
    return (f"# {title} ({len(cells)} plans; plan.md §10.3)\n\n"
            f"Copy {blank}_blank.csv to {blank}.csv. For each plan: would a competent salvage"
            " master accept it? Fill `accept` (yes / no / partial) and a one-line `reason`."
            " Images are under ../shipwreck_wiki_images/sorted_images/ (BenchyBench root)."
            " Do not open the key, results/ or any report until the read and its re-rate are"
            " done.\n" + "".join(_entry(row, k) for row, k in cells))


def read_files() -> dict[str, str]:
    """plan.md §10.3: v0.10 blind plans from the test split, one arm per image,
    READ_PER_ARM per arm, shuffled; arm and every verdict withheld."""
    test = sorted(ln.split(",")[0] for ln in split_text().splitlines()[1:]
                  if ln.endswith(",test"))
    rng = random.Random(SEED)
    images = rng.sample(test, READ_PER_ARM * len(ARMS))
    cells = [f"{i}/{ARMS[n % len(ARMS)]}" for n, i in enumerate(images)]
    rng.shuffle(cells)
    rows_ = [(f"H{n:02d}", k) for n, k in enumerate(cells, 1)]
    return {"sheet.md": _sheet("Blind read", "read", rows_),
            "read_blank.csv": _csv(["row", "accept", "reason"], [[r, "", ""] for r, _ in rows_]),
            "key.csv": _csv(["row", "scenario_id", "arm"], [[r, *k.split("/")] for r, k in rows_])}


def _filled(path: pathlib.Path, n: int) -> dict[str, str]:
    rs = list(csv.DictReader(path.open(encoding="utf-8")))
    bad = [r["row"] for r in rs if r["accept"].strip().lower() not in ("yes", "no", "partial")]
    if bad or len(rs) != n:
        sys.exit(f"{path}: {len(rs)} rows, want {n}; unfilled or invalid: {bad}")
    return {r["row"]: r["accept"].strip().lower() for r in rs}


def rerate_files() -> dict[str, str]:
    """RERATE_N of the first pass, reshuffled under new row names (plan.md §10.3)."""
    first = _filled(READ / "read.csv", READ_PER_ARM * len(ARMS))
    keyed = {r["row"]: f"{r['scenario_id']}/{r['arm']}"
             for r in csv.DictReader((READ / "key.csv").open(encoding="utf-8"))}
    pick = random.Random(SEED + 1).sample(sorted(first), RERATE_N)
    rows_ = [(f"Q{n:02d}", h) for n, h in enumerate(pick, 1)]
    return {"rerate_sheet.md": _sheet("Re-rate", "rerate", [(q, keyed[h]) for q, h in rows_]),
            "rerate_blank.csv": _csv(["row", "accept", "reason"], [[q, "", ""] for q, _ in rows_]),
            "rerate_key.csv": _csv(["row", "first_row"], [[q, h] for q, h in rows_])}


def _write_once(files: dict[str, str], where: pathlib.Path) -> int:
    if any((where / n).exists() for n in files):
        sys.exit(f"{where} already holds {sorted(files)}; drawn once")
    where.mkdir(parents=True, exist_ok=True)
    for n, text in files.items():
        (where / n).write_text(text, encoding="utf-8")
        print(f"  -> {where / n}")
    return 0


def split() -> int:
    if SPLIT.exists():
        sys.exit(f"{SPLIT} exists; the split is drawn once")
    SPLIT.parent.mkdir(parents=True, exist_ok=True)
    SPLIT.write_text(split_text(), encoding="utf-8")
    print(collections.Counter(tuple(ln.split(",")[1:]) for ln in split_text().splitlines()[1:]))
    return 0


def read() -> int:
    return _write_once(read_files(), READ)


def rerate() -> int:
    """Run about a week after the first pass is complete."""
    return _write_once(rerate_files(), READ)


def kappa(x: list[str], y: list[str]) -> float:
    cats = sorted(set(x) | set(y))
    po = sum(a == b for a, b in zip(x, y)) / len(x)
    pe = sum(x.count(c) * y.count(c) for c in cats) / len(x) ** 2
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def human_text() -> str:
    """The read, summarised as fixed before it was done. Descriptive; no test."""
    first = _filled(READ / "read.csv", READ_PER_ARM * len(ARMS))
    keyed = {r["row"]: f"{r['scenario_id']}/{r['arm']}"
             for r in csv.DictReader((READ / "key.csv").open(encoding="utf-8"))}
    vs = verdicts(extracted("blind"))
    acc = ("yes", "partial", "no")
    L = ["RCP D14: blind human read (plan.md §10.3); one rater, descriptive", "=" * 56,
         f"  {'arm':<12}" + "".join(f"{a:>9}" for a in acc)]
    for arm in ARMS:
        got = [first[h] for h in sorted(first) if keyed[h].endswith("/" + arm)]
        L.append(f"  {arm:<12}" + "".join(f"{got.count(a):>9}" for a in acc))
    L.append("  against the validator's APPROPRIATE-RESPONSE:")
    for ok in (True, False):
        got = [first[h] for h in sorted(first) if vs[keyed[h]].appropriate_response is ok]
        L.append(f"  {'AR pass' if ok else 'AR fail':<12}" + "".join(f"{got.count(a):>9}" for a in acc))
    if (READ / "rerate.csv").exists():
        again = _filled(READ / "rerate.csv", RERATE_N)
        pair = {r["row"]: r["first_row"]
                for r in csv.DictReader((READ / "rerate_key.csv").open(encoding="utf-8"))}
        x, y = [first[pair[q]] for q in sorted(again)], [again[q] for q in sorted(again)]
        L.append(f"  re-rate: same answer {sum(a == b for a, b in zip(x, y))}/{len(x)},"
                 f" Cohen's kappa {kappa(x, y):+.2f}")
    return "\n".join(L) + "\n"


def human() -> int:
    dest = OUT / "human.txt"
    if dest.exists():
        sys.exit(f"{dest} exists; written once")
    dest.write_text(human_text(), encoding="utf-8")
    print(human_text(), end="")
    return 0


def check() -> int:
    """Rebuild every written output that exists; compare byte for byte."""
    built = {OUT / "report.txt": lambda: "\n".join(build_report()) + "\n",
             SPLIT: split_text, OUT / "human.txt": human_text,
             **{READ / n: (lambda n=n: read_files()[n]) for n in ("sheet.md", "read_blank.csv",
                                                                 "key.csv")},
             **{READ / n: (lambda n=n: rerate_files()[n]) for n in
                ("rerate_sheet.md", "rerate_blank.csv", "rerate_key.csv")}}
    ok = True
    for path, make in built.items():
        if path.exists():
            same = path.read_text(encoding="utf-8") == make()
            ok &= same
            print(f"  {path.relative_to(REPO)}: {'reproduces byte for byte' if same else 'DIFFERS'}")
    return 0 if ok else 1


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    cmds = {"report": report, "check": check, "split": split, "read": read,
            "rerate": rerate, "human": human}
    if cmd not in cmds:
        sys.exit(__doc__)
    return cmds[cmd]()


if __name__ == "__main__":
    raise SystemExit(main())
