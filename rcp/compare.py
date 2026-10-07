"""Paired two-condition comparison. plan.md §9.2, run at one arm.

`rcp.report` is the four-arm instrument: its primary test is a linear contrast
across `SURPLUS → INFEASIBLE`, and with one arm every image is an incomplete case,
so that test correctly declines to run and the report has no headline. This module
is the headline for the other shape of run — **one arm, two prompt conditions** —
which is what the casualty-state disclosure experiment is:

    sbatch jobs/plan_job.sh "$IMAGES" gen_blind.jsonl  --arm SUFFICIENT
    sbatch jobs/plan_job.sh "$IMAGES" gen_stated.jsonl --arm SUFFICIENT --condition stated

**One headline variable: disclosure.** Everything else is held fixed by
construction — same arm, same 110 images, same ledgers, same greedy decode, and
both prompts' two constant halves byte-identical (Rule 2). The one number this
module exists to produce is the paired difference in `APPROPRIATE-RESPONSE`.

**Why a separate module rather than a `condition` field on `Verdict`.** Threading
disclosure through `schema.Verdict`, `extract.py` and `report.py`'s frozen arm
machinery would put a second experimental axis inside the instrument that §9.2
froze against the first one. Here the two runs stay two files, scored by the one
`validator.score` implementation via `report._load_verdicts`, and the only new code
is the pairing and the test. Nothing in the four-arm path changes.

**This module refuses to pair runs that are not the experiment.** Different arms,
a file containing two conditions, or two files whose `domain_digest` agree all halt
rather than produce a table — the last because an agreeing digest means the
manipulation did not reach the prompt, and a null result from a prompt that never
varied is the one finding that would be purely an artifact.
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys

from .report import invariant_check
from .schema import Verdict

#: Two-sided α, as §9.2. Fixed here, not a flag: a chooseable α in a headline is a
#: garden of forking paths.
ALPHA = 0.05

#: The headline endpoint, then the decomposition. `appropriate_response` is first
#: because it is the one §5 names; the rest are recorded and demoted, which is the
#: same discipline `rcp.report` applies to its own secondary columns.
ENDPOINTS = ("appropriate_response", "plan_succeeds", "resource_valid",
             "escalate", "hallucinate", "overcommit", "over_refusal")


# --------------------------------------------------------------------------- #
# loading
# --------------------------------------------------------------------------- #


def _resolve(path: pathlib.Path) -> pathlib.Path:
    """Accept either `rcp.extract`'s output directory or the JSONL inside it."""
    return path / "extracted.jsonl" if path.is_dir() else path


def load(path: pathlib.Path) -> tuple[list[Verdict], str | None, str | None]:
    """Score one extraction and read back its condition and digest.

    Verdicts come from `report._load_verdicts`, so every endpoint in this module is
    computed by the same `validator.score` that produces the four-arm tables — there
    is no second implementation of `APPROPRIATE-RESPONSE` to drift.

    The condition and digest are read separately because `Verdict` does not carry
    them. They are provenance for the refusals below, not data.
    """
    from .report import _load_verdicts

    f = _resolve(path)
    verdicts, _ = _load_verdicts(f)

    conds, digests = set(), set()
    for line in f.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        conds.add(row.get("condition"))
        digests.add(row.get("domain_digest"))
    if len(conds) > 1:
        raise SystemExit(f"ERROR: {f} mixes conditions {sorted(map(str, conds))}; "
                         "one file per condition")
    if len(digests) > 1:
        raise SystemExit(f"ERROR: {f} mixes {len(digests)} domain digests; "
                         "its rows are not one run and must not be pooled")
    return verdicts, conds.pop() if conds else None, digests.pop() if digests else None


def single_arm(verdicts: list[Verdict], label: str) -> str:
    arms = sorted({v.arm for v in verdicts})
    if len(arms) != 1:
        raise SystemExit(f"ERROR: {label} spans arms {arms}. This is the "
                         "one-arm two-condition test; for four arms use rcp.report")
    return arms[0]


# --------------------------------------------------------------------------- #
# pairing and the test
# --------------------------------------------------------------------------- #


def pairs(a: list[Verdict], b: list[Verdict],
          endpoint: str) -> list[tuple[bool, bool]]:
    """Complete-case pairs on `scenario_id`, in the first run's order.

    Complete-case, not imputed, for §9.2's reason: an image the planner was shown
    in one condition and not the other carries no information about the difference,
    and filling it in would put a guess inside the headline.

    An endpoint that is `None` for either member drops the pair. `over_refusal` is
    `None` wherever it is undefined — that is the field's meaning, not a gap.
    """
    left = {v.scenario_id: getattr(v, endpoint) for v in a}
    right = {v.scenario_id: getattr(v, endpoint) for v in b}
    out = []
    for sid, x in left.items():
        y = right.get(sid)
        if x is None or y is None or sid not in right:
            continue
        out.append((bool(x), bool(y)))
    return out


def discordance(ps: list[tuple[bool, bool]]) -> tuple[int, int, int, int]:
    """`(both, only_first, only_second, neither)` — the 2x2 of a paired design."""
    both = sum(1 for x, y in ps if x and y)
    only_a = sum(1 for x, y in ps if x and not y)
    only_b = sum(1 for x, y in ps if y and not x)
    neither = sum(1 for x, y in ps if not x and not y)
    return both, only_a, only_b, neither


def exact_paired_test(ps: list[tuple[bool, bool]]) -> dict:
    """Exact two-sided paired test on the discordant pairs (McNemar, exact form).

    **Why the exact form and not the sign-flip permutation test `rcp.report` uses.**
    They are the same test. With two paired conditions the contrast scores are
    `(-1, +1)`, so a concordant pair contributes 0 under every sign flip and each
    discordant pair contributes ±1 with probability ½ — which is exactly
    `Binomial(n_discordant, ½)`. The permutation loop would *estimate* this p-value
    with Monte-Carlo error; `math.comb` returns it. So this is the four-arm test
    specialised to two conditions, computed in closed form rather than approximated.

    Two-sided by doubling the smaller tail and capping at 1. No add-one correction
    is needed or wanted here: unlike the Monte-Carlo path there is no sampling, so
    a small p-value is the true one and inflating it would understate the evidence.

    With zero discordant pairs the data carry no information about a difference,
    and `p = 1.0` is the correct statement of that, not a missing value.
    """
    _, only_a, only_b, _ = discordance(ps)
    n = only_a + only_b
    if n == 0:
        return {"n_pairs": len(ps), "n_discordant": 0, "p_value": 1.0,
                "diff": 0.0, "test": "exact binomial (no discordant pairs)"}
    k = min(only_a, only_b)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2.0 ** n)
    return {"n_pairs": len(ps), "n_discordant": n,
            "p_value": min(1.0, 2.0 * tail),
            "diff": (only_b - only_a) / len(ps),
            "test": "exact binomial on discordant pairs (two-sided)"}


def min_detectable_split(n_discordant: int, alpha: float = ALPHA) -> int | None:
    """Smallest `|b - c|` reaching `p < alpha` given this many discordant pairs.

    **This is the MDE stated without an assumption.** A conventional power
    calculation needs a guess at the discordance rate, which nobody has before the
    run; this instead says, for each number of discordant pairs the run might
    actually produce, how lopsided they must be. Reading the row matching the
    observed `n_discordant` turns the table into a post-hoc sensitivity statement
    that costs no extra assumption.

    `None` means no split is detectable at that `n` — with 5 or fewer discordant
    pairs even a unanimous split cannot reach two-sided .05, because `2 / 2**5`
    is .0625. That is a fact about the design, and worth knowing before the run
    rather than after.
    """
    n = n_discordant
    if n == 0:
        return None
    for k in range(n // 2, -1, -1):
        tail = sum(math.comb(n, i) for i in range(k + 1)) / (2.0 ** n)
        if min(1.0, 2.0 * tail) < alpha:
            return n - 2 * k
    return None


# --------------------------------------------------------------------------- #
# assembly
# --------------------------------------------------------------------------- #


def _rate(verdicts: list[Verdict], endpoint: str) -> tuple[float | None, int, int]:
    vals = [getattr(v, endpoint) for v in verdicts]
    defined = [bool(v) for v in vals if v is not None]
    if not defined:
        return None, 0, 0
    return sum(defined) / len(defined), sum(defined), len(defined)


def build(blind: list[Verdict], stated: list[Verdict],
          provenance: dict) -> dict:
    """The comparison. Halts the tables on an invariant violation, as §9.2 requires.

    `invariant_check` is `rcp.report`'s, not a copy: `¬LEDGER-SATISFIABLE ⟹
    ¬PLAN-SUCCEEDS` has exactly one implementation, and a violation here means a
    hand-edited or corrupted extraction, which is a bug and not a result.
    """
    violations = invariant_check(blind) + invariant_check(stated)
    if violations:
        return {"provenance": provenance, "invariant_violations": violations,
                "suppressed": True}

    rows = {}
    for ep in ENDPOINTS:
        ps = pairs(blind, stated, ep)
        rows[ep] = {
            "blind": _rate(blind, ep),
            "stated": _rate(stated, ep),
            "cells": discordance(ps),
            "test": exact_paired_test(ps),
        }
    headline = rows[ENDPOINTS[0]]
    n = headline["test"]["n_pairs"]
    # The observed count is forced into the grid so the instruction to "read the
    # row matching the observed count" is always satisfiable. Without it the table
    # is a generic reference and the reader has to interpolate.
    grid = sorted({d for d in (4, 6, 8, 10, 15, 20, 30, 40) if d <= max(n, 1)}
                  | {headline["test"]["n_discordant"]} - {0})
    return {
        "provenance": provenance,
        "invariant_violations": [],
        "suppressed": False,
        "headline": ENDPOINTS[0],
        "endpoints": rows,
        "observed_discordant": headline["test"]["n_discordant"],
        "mde": [(d, min_detectable_split(d)) for d in grid],
    }


def _pct(r: float | None) -> str:
    return "  n/a" if r is None else f"{100.0 * r:5.1f}%"


def render(rep: dict) -> str:
    p = rep["provenance"]
    out = ["=" * 72,
           " RCP disclosure comparison (plan.md sec. 9.2, one arm, two conditions)",
           "=" * 72,
           f" arm            : {p['arm']}",
           f" blind          : {p['blind_file']}  ({p['blind_n']} cells)",
           f" stated         : {p['stated_file']}  ({p['stated_n']} cells)",
           f" blind digest   : {p['blind_digest']}",
           f" stated digest  : {p['stated_digest']}",
           ""]

    if rep["suppressed"]:
        out += ["INVARIANT VIOLATED - all tables suppressed.",
                "  not(LEDGER-SATISFIABLE) implies not(PLAN-SUCCEEDS) fails at:"]
        out += [f"    {k}" for k in rep["invariant_violations"][:20]]
        out += ["", "This is a bug in the extraction or a hand-edited file, not a",
                "result. Fix it and rerun; do not report anything above."]
        return "\n".join(out)

    head = rep["endpoints"][rep["headline"]]
    t = head["test"]
    out += ["--- HEADLINE " + "-" * 59,
            f"  {rep['headline'].upper().replace('_', '-')}",
            f"    blind  : {_pct(head['blind'][0])}  ({head['blind'][1]}/{head['blind'][2]})",
            f"    stated : {_pct(head['stated'][0])}  ({head['stated'][1]}/{head['stated'][2]})",
            f"    paired difference (stated - blind) : {100.0 * t['diff']:+.1f} pp",
            f"    pairs {t['n_pairs']}, discordant {t['n_discordant']}, "
            f"p = {t['p_value']:.4f}  ({'significant' if t['p_value'] < ALPHA else 'not significant'} at alpha = {ALPHA})",
            f"    {t['test']}",
            ""]

    out += ["--- ALL ENDPOINTS (secondary; recorded, not the headline) " + "-" * 14,
            "  endpoint              blind   stated    diff   b    c    p",
            "  " + "-" * 60]
    for ep in ENDPOINTS:
        r = rep["endpoints"][ep]
        _, only_b, only_c, _ = r["cells"]
        tt = r["test"]
        out.append(f"  {ep:<20} {_pct(r['blind'][0])}  {_pct(r['stated'][0])}  "
                   f"{100.0 * tt['diff']:+6.1f}  {only_b:<4} {only_c:<4} "
                   f"{tt['p_value']:.4f}")
    out += ["",
            "  b = blind only, c = stated only. Concordant pairs carry no",
            "  information about a difference and are not in the test.",
            ""]

    out += ["--- SENSITIVITY " + "-" * 56,
            "  minimum |b - c| reaching p < .05, by discordant-pair count:",
            "  discordant   min |b - c|"]
    for d, m in rep["mde"]:
        mark = "   <- observed" if d == rep["observed_discordant"] else ""
        out.append(f"  {d:<12} "
                   f"{'not detectable at any split' if m is None else m}{mark}")
    out += ["",
            "  Assumption-free: no discordance rate is assumed. The marked row is",
            "  this run's; it says how lopsided the discordant pairs had to be.",
            "=" * 72]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="RCP paired comparison of two prompt conditions at one arm")
    ap.add_argument("--blind", required=True,
                    help="rcp.extract output (directory or extracted.jsonl) "
                         "for the 'blind' condition")
    ap.add_argument("--stated", required=True,
                    help="same, for the 'stated' condition")
    ap.add_argument("--out", default=None,
                    help="write the report to this FILE as well as stdout")
    ap.add_argument("--allow-equal-digest", action="store_true",
                    help="proceed when both runs share a domain_digest. Only for "
                         "re-analysing generations written before --condition "
                         "existed; never for a result")
    args = ap.parse_args(argv)

    bv, bc, bd = load(pathlib.Path(args.blind))
    sv, sc, sd = load(pathlib.Path(args.stated))

    arm = single_arm(bv, "--blind")
    if single_arm(sv, "--stated") != arm:
        raise SystemExit(f"ERROR: --blind is arm {arm}, --stated is "
                         f"{single_arm(sv, '--stated')}. Disclosure is the only "
                         "variable this module may compare")

    # The labels are advisory - the files say what they are. A swap would silently
    # flip the sign of every difference, so it is worth one check.
    for want, got, flag in (("blind", bc, "--blind"), ("stated", sc, "--stated")):
        if got is not None and got != want:
            raise SystemExit(f"ERROR: {flag} holds condition {got!r}, not {want!r}")
    for got, flag in ((bc, "--blind"), (sc, "--stated")):
        if got is None:
            print(f"  WARNING: {flag} has no 'condition' field - generations "
                  "predate the flag; trusting the argument", file=sys.stderr)

    if bd is not None and bd == sd and not args.allow_equal_digest:
        raise SystemExit(
            "ERROR: both runs carry domain_digest " + str(bd) + ".\n"
            "       The two prompts were identical, so there was no manipulation "
            "to measure\n"
            "       and a null result here would be an artifact. Regenerate with "
            "--condition,\n"
            "       or pass --allow-equal-digest if you know why and are not "
            "reporting it.")
    if bc is not None and bc == sc:
        raise SystemExit(f"ERROR: both runs are condition {bc!r}")

    rep = build(bv, sv, provenance={
        "arm": arm,
        "blind_file": str(_resolve(pathlib.Path(args.blind))),
        "stated_file": str(_resolve(pathlib.Path(args.stated))),
        "blind_n": len(bv), "stated_n": len(sv),
        "blind_digest": bd, "stated_digest": sd,
    })
    text = render(rep)
    print(text)
    if args.out:
        dest = pathlib.Path(args.out)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text + "\n", encoding="utf-8")
        print(f"\n  written -> {dest}")
    return 1 if rep["suppressed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
