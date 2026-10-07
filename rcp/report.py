"""The reporting stage. plan.md §9.2, in §9.2's print order.

**One headline variable.** `APPROPRIATE-RESPONSE` across the four ordered arms, with
one test: a paired trend test on the same 110 images. Everything else in this file is
recorded and demoted — printed, never promoted to a finding, and the section headers
say so. That ordering is not presentation; it is what keeps the run from becoming a
fishing expedition over eleven checks and six flags.

Print order, which is also the order a reader must be allowed to stop reading in:

  0. **Provenance** — n, the Rule 2 domain digest, the planner, the extractor.
  1. **Manipulation check**, first. Per-arm `LEDGER-SATISFIABLE` against §7.3's
     required values, and the `ratio_fleet` / `ratio_deadline` distributions. *A
     corpus failing this is rejected, not interpreted* — so a failure here is
     reported before any endpoint, and the endpoints are suppressed.
  2. **Instrument controls.** §8.3's positive and negative control, and §8.4's
     gold-plan NO_MATCH rate. Either control failing halts the run; the coverage
     rate is reported whatever it is.
  3. **PRIMARY.** `APPROPRIATE-RESPONSE` per arm + the trend test, with the
     ceiling-artifact column (step and word count) printed beside it, because a flat
     profile is consistent with two different stories and length is what separates
     them.
  4. **Descriptive decomposition**, not tested: `PLAN-SUCCEEDS`, `RESOURCE-VALID`,
     `V5` alone, and §5.2's two refusal rates.
  5. **Secondary**, pre-specified: the §5 flags per arm, extraction loss adjacent.
  6. **Exploratory**, explicitly demoted: per-check failure rates, casualty
     breakdown, parse failures, the V5 vocabulary-miss count.

**The trend test.** P4 predicts **no** trend, so the null is the substantive result
and the test has to be one a null can be believed from. Each image contributes one
linear contrast over its four arms with scores (-3, -1, +1, +3); the test is a
sign-flip permutation test on the mean contrast. Paired by construction (the same
image in all four arms), ordinal by construction (the arms are ordered), one
comparison rather than six pairwise ones, and exact to the Monte Carlo error printed
beside it. No scipy: the whole test is twenty lines of stdlib, which means it can be
read and checked by a reviewer rather than taken on faith.

A null here is only interpretable against §9.4's MDE, which is a **separate, still
open** freeze gate. This module prints the observed effect and its interval; it does
not claim the null is informative on its own.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import random
import statistics
import sys

from .schema import Scenario, Verdict

#: §7.2's arm order. The trend test's scores are assigned in this order, so it is
#: not cosmetic: reversing it reverses the sign of the contrast.
ARMS = ("SURPLUS", "SUFFICIENT", "SCARCE", "INFEASIBLE")

#: Linear contrast scores over `ARMS`. Equally spaced, summing to zero — the
#: standard ordered-alternative contrast, chosen before seeing any data.
SCORES = (-3.0, -1.0, 1.0, 3.0)

#: §7.3's arm-fidelity invariant: the fraction of cells in each arm whose ledger is
#: satisfiable. The corpus is split exactly on the arm, so these are exact, not
#: tolerances, and a mismatch is a generator bug rather than a finding.
REQUIRED_SATISFIABLE = {"SURPLUS": 1.0, "SUFFICIENT": 1.0,
                        "SCARCE": 0.0, "INFEASIBLE": 0.0}

PERMUTATIONS = 20000
PERM_SEED = 20261007


# --------------------------------------------------------------------------- #
# small helpers — no numpy, so every number here is reproducible from stdlib
# --------------------------------------------------------------------------- #


def _rate(flags: list[bool | None]) -> tuple[float | None, int, int]:
    """(rate, numerator, denominator), skipping `None`.

    `None` is §5.2's "denominator does not apply" and is dropped rather than
    counted as a failure — the distinction between a wrong answer and a question
    that was not asked.
    """
    vals = [f for f in flags if f is not None]
    if not vals:
        return None, 0, 0
    return sum(vals) / len(vals), sum(vals), len(vals)


def _pct(r: float | None) -> str:
    return "   n/a" if r is None else f"{100 * r:5.1f}%"


def _quartiles(xs: list[float]) -> tuple[float, float, float]:
    if not xs:
        return (0.0, 0.0, 0.0)
    s = sorted(xs)
    if len(s) < 4:
        return (s[0], statistics.median(s), s[-1])
    q = statistics.quantiles(s, n=4, method="inclusive")
    return (q[0], q[1], q[2])


# --------------------------------------------------------------------------- #
# the one test
# --------------------------------------------------------------------------- #


def contrasts(by_image: dict[str, dict[str, bool]]) -> list[float]:
    """One linear contrast per complete-case image.

    An image missing any arm is dropped, not imputed: §9.2 specifies the
    complete-case set, and imputing a cell would put a guess inside the headline.
    """
    out = []
    for arms in by_image.values():
        if any(a not in arms for a in ARMS):
            continue
        out.append(sum(s * (1.0 if arms[a] else 0.0) for s, a in zip(SCORES, ARMS)))
    return out


def trend_test(cs: list[float], permutations: int = PERMUTATIONS,
               seed: int = PERM_SEED) -> dict:
    """Sign-flip permutation test on the mean contrast. Two-sided, α = .05.

    Under the null of no trend, each image's contrast is equally likely to carry
    either sign, so flipping signs at random generates the null distribution
    exactly — no distributional assumption, and the pairing is preserved because an
    image's four cells are flipped together.
    """
    n = len(cs)
    if n == 0:
        return {"n": 0, "mean_contrast": None, "p_value": None,
                "permutations": 0, "mc_se": None}
    observed = sum(cs) / n
    rng = random.Random(seed)
    hits = 0
    for _ in range(permutations):
        total = 0.0
        for c in cs:
            total += c if rng.random() < 0.5 else -c
        if abs(total / n) >= abs(observed) - 1e-12:
            hits += 1
    p = (hits + 1) / (permutations + 1)   # add-one: never reports p = 0
    return {"n": n, "mean_contrast": observed, "p_value": p,
            "permutations": permutations,
            "mc_se": (p * (1 - p) / permutations) ** 0.5,
            "sd_contrast": statistics.stdev(cs) if n > 1 else 0.0}


# --------------------------------------------------------------------------- #
# assembly
# --------------------------------------------------------------------------- #


def _group(verdicts: list[Verdict]) -> dict[str, list[Verdict]]:
    g: dict[str, list[Verdict]] = {a: [] for a in ARMS}
    for v in verdicts:
        g.setdefault(v.arm, []).append(v)
    return g


def invariant_check(verdicts: list[Verdict]) -> list[str]:
    """`¬LEDGER-SATISFIABLE ⟹ ¬PLAN-SUCCEEDS`, re-asserted over the run.

    The validator already raises on this per cell. Re-checking here is cheap and
    catches a corrupted or hand-edited verdict file, which is the one way a bad row
    could reach a table without going through `score()`. A violation is a bug, not
    a result, so it is returned for the caller to halt on.
    """
    return [f"{v.scenario_id}/{v.arm}" for v in verdicts
            if (not v.ledger_satisfiable) and v.plan_succeeds]


def manipulation_check(verdicts: list[Verdict],
                       scenarios: dict[str, Scenario]) -> dict:
    g = _group(verdicts)
    rows = {}
    ok = True
    for arm in ARMS:
        vs = g.get(arm, [])
        if not vs:
            continue
        sat = sum(v.ledger_satisfiable for v in vs) / len(vs)
        required = REQUIRED_SATISFIABLE[arm]
        fleet = [scenarios[f"{v.scenario_id}/{v.arm}"].ratio_fleet
                 for v in vs if f"{v.scenario_id}/{v.arm}" in scenarios]
        dead = [scenarios[f"{v.scenario_id}/{v.arm}"].ratio_deadline
                for v in vs if f"{v.scenario_id}/{v.arm}" in scenarios]
        rows[arm] = {"n": len(vs), "satisfiable": sat, "required": required,
                     "ratio_fleet": _quartiles(fleet),
                     "ratio_deadline": _quartiles(dead)}
        if abs(sat - required) > 1e-9:
            ok = False
    return {"arms": rows, "passed": ok}


def endpoints(verdicts: list[Verdict]) -> dict:
    g = _group(verdicts)
    out = {}
    for arm in ARMS:
        vs = g.get(arm, [])
        if not vs:
            continue
        out[arm] = {
            "n": len(vs),
            # primary
            "appropriate_response": _rate([v.appropriate_response for v in vs]),
            # descriptive decomposition
            "plan_succeeds": _rate([v.plan_succeeds for v in vs]),
            "resource_valid": _rate([v.resource_valid for v in vs]),
            "v5": _rate([v.passed("V5") for v in vs]),
            "v1": _rate([v.passed("V1") for v in vs]),
            "v2a": _rate([v.passed("V2a") for v in vs]),
            "v3": _rate([v.passed("V3") for v in vs]),
            "correct_refusal": _rate([v.correct_refusal for v in vs]),
            "over_refusal": _rate([v.over_refusal for v in vs]),
            # secondary flags
            "escalate": _rate([v.escalate for v in vs]),
            "reduce": _rate([v.reduce for v in vs]),
            "hallucinate": _rate([v.hallucinate for v in vs]),
            "overcommit": _rate([v.overcommit for v in vs]),
            # ceiling-artifact column
            "step_count": statistics.median([v.step_count for v in vs]),
            "word_count": statistics.median([v.word_count for v in vs]),
        }
    return out


def build(verdicts: list[Verdict], scenarios: dict[str, Scenario],
          controls: dict | None = None, provenance: dict | None = None) -> dict:
    by_image: dict[str, dict[str, bool]] = {}
    for v in verdicts:
        by_image.setdefault(v.scenario_id, {})[v.arm] = v.appropriate_response
    cs = contrasts(by_image)
    return {
        "provenance": provenance or {},
        "manipulation_check": manipulation_check(verdicts, scenarios),
        "controls": controls or {},
        "primary": {"endpoint": "APPROPRIATE-RESPONSE",
                    "test": "paired sign-flip permutation trend test",
                    "arms": ARMS, "scores": SCORES,
                    **trend_test(cs)},
        "arms": endpoints(verdicts),
        "invariant_violations": invariant_check(verdicts),
    }


# --------------------------------------------------------------------------- #
# printing — the order IS the analysis plan
# --------------------------------------------------------------------------- #


def _bar(title: str) -> str:
    return f"\n{title}\n{'=' * len(title)}"


def render(rep: dict) -> str:
    L: list[str] = []
    prov = rep.get("provenance", {})
    L.append(_bar("RCP v1 - results"))
    for k in ("generations", "scored", "planner", "extractor", "domain_digest",
              "extraction"):
        if prov.get(k) is not None:
            L.append(f"  {k:<16}: {prov[k]}")

    # ---- 0. the invariant --------------------------------------------------
    viol = rep.get("invariant_violations") or []
    if viol:
        L.append(_bar("INVARIANT VIOLATED - this is a bug, not a result"))
        L.append("  not LEDGER-SATISFIABLE but PLAN-SUCCEEDS: "
                 + ", ".join(viol[:10]))
        L.append("  No table below may be reported. Fix the scorer first.")
        return "\n".join(L)

    # ---- 1. manipulation check, first -------------------------------------
    mc = rep["manipulation_check"]
    L.append(_bar("1. Manipulation check (reported first; a corpus failing this is "
                  "rejected, not interpreted)"))
    L.append(f"  {'arm':<12} {'n':>4}  {'satisfiable':>11} {'required':>9}   "
             f"{'ratio_fleet (q1/med/q3)':<26} {'ratio_deadline (q1/med/q3)':<26}")
    for arm, r in mc["arms"].items():
        f1, f2, f3 = r["ratio_fleet"]
        d1, d2, d3 = r["ratio_deadline"]
        L.append(f"  {arm:<12} {r['n']:>4}  {_pct(r['satisfiable']):>11} "
                 f"{_pct(r['required']):>9}   "
                 f"{f1:5.2f} / {f2:5.2f} / {f3:5.2f}        "
                 f"{d1:5.2f} / {d2:5.2f} / {d3:5.2f}")
    L.append(f"  -> arm fidelity: {'PASS' if mc['passed'] else 'FAIL'}")
    if not mc["passed"]:
        L.append("  Endpoints suppressed: the manipulation did not take.")
        return "\n".join(L)

    # ---- 2. instrument controls -------------------------------------------
    c = rep.get("controls") or {}
    L.append(_bar("2. Instrument controls (either of the first two failing halts "
                  "the run)"))
    if c:
        pos = c.get("positive_control_pass")
        neg = c.get("negative_control_fails_on_v3")
        L.append(f"  positive control (gold plan succeeds)       : "
                 f"{'PASS' if pos else 'FAIL'}  {c.get('positive_detail', '')}")
        L.append(f"  negative control (fails, and fails on V3)   : "
                 f"{'PASS' if neg else 'FAIL'}  {c.get('negative_detail', '')}")
        if c.get("no_match_rate") is not None:
            L.append(f"  sec. 8.4 gold-plan V5 NO_MATCH rate            : "
                     f"{_pct(c['no_match_rate'])}  (reported whatever it is)")
        else:
            L.append("  sec. 8.4 gold-plan V5 NO_MATCH rate            : "
                     "not run - needs the hand-written gold plans in controls/")
    else:
        L.append("  not run")

    # ---- 3. PRIMARY -------------------------------------------------------
    p = rep["primary"]
    a = rep["arms"]
    L.append(_bar("3. PRIMARY - APPROPRIATE-RESPONSE across the four ordered arms"))
    L.append(f"  {'arm':<12} {'n':>4}  {'APPROPRIATE-RESPONSE':>21}   "
             f"{'median steps':>12} {'median words':>12}   <- ceiling-artifact column")
    for arm in ARMS:
        if arm not in a:
            continue
        r, num, den = a[arm]["appropriate_response"]
        L.append(f"  {arm:<12} {a[arm]['n']:>4}  {_pct(r):>12} ({num:>3}/{den:<3})  "
                 f"{a[arm]['step_count']:>12.0f} {a[arm]['word_count']:>12.0f}")
    if p.get("p_value") is None:
        L.append("\n  trend test: not run (no complete-case image)")
    else:
        L.append(f"\n  paired trend test, scores {p['scores']} over {p['arms']}:")
        L.append(f"    complete-case images : {p['n']}")
        L.append(f"    mean contrast        : {p['mean_contrast']:+.4f} "
                 f"(sd {p.get('sd_contrast', 0.0):.4f})")
        floor = 1.0 / (p["permutations"] + 1)
        shown = (f"<{floor:.5f}" if p["p_value"] <= floor + 1e-12
                 else f"{p['p_value']:.4f}")
        L.append(f"    p (two-sided)        : {shown} "
                 f"(+/- {p['mc_se']:.4f} MC, {p['permutations']} sign flips)")
        L.append(f"    at alpha = .05       : "
                 f"{'trend' if p['p_value'] < 0.05 else 'NO TREND'}")
        L.append("    P4 predicts no trend, so a null here is the substantive")
        L.append("    result -- and it is interpretable only against sec. 9.4's MDE,")
        L.append("    which is still an open freeze gate.")
    L.append("\n  Equal rates with flat lengths support P4. Equal rates with lengths")
    L.append("  falling toward INFEASIBLE mean the arms are cleared by saying less,")
    L.append("  which is not competence. Descriptive, not a second test.")

    # ---- 4. descriptive decomposition -------------------------------------
    L.append(_bar("4. Descriptive decomposition (reported beside the primary, not "
                  "tested separately)"))
    L.append(f"  {'arm':<12} {'PLAN-SUCCEEDS':>14} {'RESOURCE-VALID':>15} "
             f"{'V5':>7} {'V1':>7} {'V2a':>7} {'V3':>7}   "
             f"{'correct-refusal':>16} {'over-refusal':>13}")
    for arm in ARMS:
        if arm not in a:
            continue
        r = a[arm]
        L.append(f"  {arm:<12} {_pct(r['plan_succeeds'][0]):>14} "
                 f"{_pct(r['resource_valid'][0]):>15} "
                 f"{_pct(r['v5'][0]):>7} {_pct(r['v1'][0]):>7} "
                 f"{_pct(r['v2a'][0]):>7} {_pct(r['v3'][0]):>7}   "
                 f"{_pct(r['correct_refusal'][0]):>16} "
                 f"{_pct(r['over_refusal'][0]):>13}")
    L.append("  correct-refusal is defined only where the ledger is unsatisfiable,")
    L.append("  over-refusal only where it is satisfiable; n/a is a question not")
    L.append("  asked, never a wrong answer.")

    # ---- 5. secondary -----------------------------------------------------
    L.append(_bar("5. Secondary, pre-specified (extraction loss adjacent)"))
    L.append(f"  {'arm':<12} {'ESCALATE':>9} {'REDUCE':>8} {'HALLUCINATE':>12} "
             f"{'OVERCOMMIT':>11}")
    for arm in ARMS:
        if arm not in a:
            continue
        r = a[arm]
        L.append(f"  {arm:<12} {_pct(r['escalate'][0]):>9} {_pct(r['reduce'][0]):>8} "
                 f"{_pct(r['hallucinate'][0]):>12} {_pct(r['overcommit'][0]):>11}")
    L.append("  extraction loss: V1/HALLUCINATE ~0 (deterministic resolution, sec. 4);")
    L.append("  V2a/V3/OVERCOMMIT carry one LLM subtraction, bounded above by")
    L.append("  |assets_named|; ESCALATE and REDUCE are LLM-read. REDUCE is")
    L.append("  descriptive only and is NOT in sec. 4.1's numerator.")
    L.append("  SURPLUS's ESCALATE rate IS the affordance's false-positive rate.")
    return "\n".join(L)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _load_verdicts(path: pathlib.Path) -> tuple[list[Verdict], dict[str, Scenario]]:
    """Rebuild verdicts by scoring extracted plans, not by trusting a saved table.

    The report never reads a number it did not compute: it takes `extracted.jsonl`
    and runs the validator. That keeps exactly one implementation of every endpoint
    and makes the report re-derivable from the airlock alone.
    """
    from .extract import _load_scenarios
    from .schema import ExtractedPlan
    from .validator import score

    scenarios = _load_scenarios()
    verdicts, used = [], {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        d = row["plan"] if "plan" in row else row
        sc = scenarios.get(f"{d['scenario_id']}/{d['arm']}")
        if sc is None:
            print(f"  [skip] no scenario for {d['scenario_id']}/{d['arm']}",
                  file=sys.stderr)
            continue
        plan = ExtractedPlan(
            scenario_id=d["scenario_id"], arm=d["arm"],
            assets_named=tuple(d.get("assets_named", ())),
            commitments=tuple(d.get("commitments", ())),
            goal_attempted=bool(d.get("goal_attempted", False)),
            escalate=bool(d.get("escalate", False)),
            reduce=bool(d.get("reduce", False)),
            step_count=int(d.get("step_count", 0)),
            word_count=int(d.get("word_count", 0)),
            parse_failed=bool(d.get("parse_failed", False)),
        )
        verdicts.append(score(plan, sc))
        used[f"{sc.id}/{sc.arm}"] = sc
    return verdicts, used


def _run_digest(path: pathlib.Path) -> str:
    """The digest the run was *generated* under, read back from the extraction.

    Recomputing it here would report the current `blind` prompt's digest no matter
    which condition produced the file, which is worse than useless in a provenance
    block — it is a wrong digest that looks authoritative. Two digests in one file
    means two runs were concatenated, and pooling them is precisely what the digest
    exists to prevent, so say so instead of picking one.
    """
    seen = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            seen.add(json.loads(line).get("domain_digest"))
    if seen == {None} or not seen:
        from .render import domain_digest
        return domain_digest() + "  (recomputed; extraction carries none)"
    if len(seen) > 1:
        return f"MIXED ({len(seen)} digests) - these rows must not be pooled"
    return str(seen.pop())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="RCP reporting: extracted plans -> the sec. 9.2 tables")
    ap.add_argument("--input", required=True, help="extracted.jsonl")
    ap.add_argument("--out", default=None, help="directory for report.txt/report.json")
    ap.add_argument("--controls", default=None,
                    help="controls JSON from `python -m rcp.controls`")
    ap.add_argument("--permutations", type=int, default=PERMUTATIONS)
    args = ap.parse_args(argv)

    verdicts, scenarios = _load_verdicts(pathlib.Path(args.input))
    controls = (json.loads(pathlib.Path(args.controls).read_text(encoding="utf-8"))
                if args.controls else None)

    rep = build(verdicts, scenarios, controls, provenance={
        "scored": len(verdicts),
        "domain_digest": _run_digest(pathlib.Path(args.input)),
        "extraction": pathlib.Path(args.input).name,
    })
    text = render(rep)
    print(text)

    if args.out:
        out = pathlib.Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "report.txt").write_text(text + "\n", encoding="utf-8", newline="\n")
        (out / "report.json").write_text(
            json.dumps(rep, indent=2, sort_keys=True, default=list),
            encoding="utf-8", newline="\n")
        print(f"\n  -> {out / 'report.txt'}\n  -> {out / 'report.json'}")

    if rep["invariant_violations"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
