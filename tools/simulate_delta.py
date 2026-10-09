"""The equivalence margin δ for §9.2's primary. plan.md §9.4.

P4 predicts APPROPRIATE-RESPONSE is flat across the four arms, so the primary is
an equivalence test, not a trend test: the fitted SURPLUS -> INFEASIBLE change D
must have its 90% CI inside (-δ, +δ) (two one-sided tests at α = .05). A null on
the old trend test said nothing; this says "no decline larger than δ".

δ is then the smallest margin this design can establish with 80% power when the
truth is exactly flat. It depends on the per-image variance of the contrast, i.e.
on the (unknown) flat rate p and the within-image correlation ρ across arms:

    contrast c_i = Σ_k s_k·y_ik,  s = (-3, -1, +1, +3)
    D = 0.3 · mean(c)           (a linear decline of d per arm step gives c = -10d,
                                 and a SURPLUS -> INFEASIBLE change of -3d)
    Var(c_i) = p(1-p)·20·(1-ρ)  (Σs² = 20, Σ_{j≠k} s_j s_k = -20)

so ρ = 0, p = .5 is the worst case and any positive correlation only helps.
(The analytic column takes ρ as the binary correlation; the simulation draws a
latent ρ, whose binary correlation is lower, so its power for ρ > 0 sits a little
under .80. The margin is set at ρ = 0, where the two agree.)
The script reports the analytic margin and checks it by simulation (correlated
binaries via a Gaussian copula, the same normal-theory interval report.py uses).

    python tools/simulate_delta.py            # table + the margin to enter
"""

from __future__ import annotations

import argparse
import random
import statistics
from statistics import NormalDist

SCORES = (-3.0, -1.0, 1.0, 3.0)
TO_DROP = 0.3            # D = TO_DROP * mean contrast, sign: positive = rises
                         # (rcp.report.TO_CHANGE; the margin is symmetric)
Z90 = NormalDist().inv_cdf(0.95)    # 90% two-sided CI = TOST at α = .05
# Power at a true D of 0 needs both one-sided tests to reject: |D̂| < δ - Z90·se
# with probability .80, i.e. δ - Z90·se = z_{.90}·se, not z_{.80}.
Z_POW = NormalDist().inv_cdf(0.90)


def analytic_delta(n: int, p: float, rho: float) -> float:
    se = TO_DROP * (20.0 * p * (1 - p) * (1 - rho) / n) ** 0.5
    return (Z90 + Z_POW) * se


def _image(rng: random.Random, p: float, rho: float) -> list[int]:
    # Gaussian copula: a shared image effect plus arm noise, thresholded at p.
    # ρ here is the latent correlation; the binary correlation is somewhat lower,
    # which makes the simulated margin conservative relative to the label.
    cut = NormalDist().inv_cdf(p)
    u = rng.gauss(0, 1)
    return [int(rho ** 0.5 * u + (1 - rho) ** 0.5 * rng.gauss(0, 1) < cut)
            for _ in SCORES]


def equivalent(cs: list[float], delta: float) -> bool:
    n = len(cs)
    d = TO_DROP * statistics.fmean(cs)
    se = TO_DROP * statistics.stdev(cs) / n ** 0.5
    return -delta < d - Z90 * se and d + Z90 * se < delta


def power(n: int, p: float, rho: float, delta: float, reps: int, seed: int) -> float:
    rng = random.Random(seed)
    hit = 0
    for _ in range(reps):
        cs = [sum(s * y for s, y in zip(SCORES, _image(rng, p, rho))) for _ in range(n)]
        hit += equivalent(cs, delta)
    return hit / reps


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--n", type=int, default=110)
    ap.add_argument("--reps", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20261009)
    args = ap.parse_args(argv)

    print(f"n = {args.n}, 90% CI (TOST α=.05), power 0.80, truth exactly flat\n")
    print(f"{'p':>5} {'rho':>5} {'δ analytic':>11} {'sim power at δ':>15}")
    worst = 0.0
    for p in (0.1, 0.2, 0.3, 0.5):
        for rho in (0.0, 0.3, 0.6):
            d = analytic_delta(args.n, p, rho)
            worst = max(worst, d)
            pw = power(args.n, p, rho, d, args.reps, args.seed)
            print(f"{p:>5.1f} {rho:>5.1f} {d:>11.3f} {pw:>15.3f}")
    margin = -(-worst * 100 // 5) * 5 / 100     # round up to the next 0.05
    pw = power(args.n, 0.5, 0.0, margin, args.reps, args.seed)
    print(f"\nworst case (p=.5, rho=0): δ = {worst:.3f}")
    print(f"pre-registered margin    : δ = {margin:.2f}  "
          f"(simulated power {pw:.3f} at the worst case)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
