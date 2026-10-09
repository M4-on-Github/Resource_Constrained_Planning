# Corpus realism: findings from the hand-authored check

**Date:** 2026-10-07 · **Corpus:** 110 images x 4 arms = 440 cells ·
**Status (2026-10-09, plan.md v0.10):** acted on before the freeze, in the
corpus rebuild logged as `docs/deviations.md` D5. Per finding:

1. `location` — **fixed.** Invented ports per chain; ETA = mobilisation +
   distance ÷ type speed, or underway at a drawn range; consistency asserted in
   `tests/test_generator.py`.
2. Enabling kit — **fixed.** Present, on time and inert in every arm wherever the
   casualty state has one (dive team for capsized/sunken, pump for on_fire).
3. Boundary fragility — **partly.** No asset now arrives within max(0.3 h, 5 %)
   of the deadline. Single-asset fragility at `SUFFICIENT` remains: a 1.2 × arm
   built from whole assets is close to the line by design.
4. Identical ratings — **partly.** 25 % of asset draws now come from any
   placeable type rather than the nearest capability band.

The findings below are kept as they were recorded, against the v0.9 corpus.

§7.2 provides for ~10 ledgers authored by hand "to catch a generator that is
internally consistent but maritime-implausible (a 200 m tanker offered three small
harbor tugs), which would make the planner's 'failures' reasonable responses to an
unreasonable scenario."

That check has now been run. A salvage-plan author worked through 10 rendered cells
blind — no access to `rcp/world.py`, `rcp/validator.py`, `rcp/flags.py`, the
extractor, `plan.md`, or `tests/`, for the reasons in `controls/README.md` — and
reported what looked wrong about the ledgers. Three of its observations were then
verified against all 440 cells. All three reproduce; two are worse at corpus scale
than in the sample.

The gate itself passed: **0.0% `NO_MATCH`**, all four casualty vocabularies
exercised. These findings are about the *stimulus*, not the instrument.

---

## 1. `location` is noise

**Claim:** ETA appears drawn independently of `location`. "Singapore anchorage" sits
beside Valletta and Gibraltar as though interchangeable, and two assets at the *same*
named location can differ wildly in ETA.

**Verified, and stronger than claimed.** Median ETA across all 440 cells, by location:

| location | n | eta range (h) | median |
|---|---|---|---|
| Gibraltar | 349 | 0.4 – 119.7 | 5.1 |
| at sea | 337 | 0.4 – 118.4 | 6.0 |
| Valletta | 335 | 0.4 – 109.1 | 5.6 |
| depot | 333 | 0.3 – 97.3 | 5.4 |
| regional base | 331 | 0.4 – 117.1 | 6.1 |
| Singapore anchorage | 330 | 0.4 – 115.1 | 5.9 |
| Algeciras | 330 | 0.3 – 85.6 | 5.6 |
| Port Mahon | 320 | 0.3 – 112.4 | 5.5 |
| Las Palmas | 319 | 0.3 – 99.2 | 5.0 |
| Rotterdam | 314 | 0.5 – 111.8 | 5.4 |
| Piraeus | 313 | 0.5 – 107.0 | 5.9 |

The eleven distributions are indistinguishable. `location` carries no information
about arrival time.

**Scoring impact: none.** No check reads `location`; V2a reads `eta_hours` alone. So
this cannot move any endpoint and is not a correctness defect.

**Why it still matters.** `location` is rendered into the ledger table the planner
reads, as *realism* — permitted unlimited by Rule 1, scored by nothing. But incoherent
realism is not neutral: a planner that reasons about geography is being handed noise
and may distrust the ledger, and a reader auditing a plan's reasoning cannot tell a
sound inference from a lucky one. It also weakens §7.2's stated purpose, since a
maritime reviewer notices this immediately.

**Options, if fixed.** Either (a) derive `eta_hours` from a distance per location so
the column means something, or (b) drop `location` from the rendered table entirely.
(b) is ~2 lines in `render.py` and costs nothing the experiment measures; (a) is a
generator change that moves every ETA and therefore every `ratio_deadline`, so it
cannot be done after freeze.

---

## 2. Enabling kit is missing on submerged and inverted casualties

**Claim:** you cannot rig a submerged or inverted hull without divers or an ROV, and
several such cells have neither.

**Verified and systematic:**

| casualty state | cells with a dive team or ROV |
|---|---|
| aground | 53 / 168 |
| capsized | **24 / 76** |
| on_fire | 22 / 64 |
| sunken | **35 / 132** |

So roughly **70% of `capsized` and `sunken` cells offer no way to get rigging onto the
hull.** Separately, 47/64 `on_fire` cells carry a dewatering pump, although the
domain block the planner reads warns that a fire-damaged vessel is then exposed to
sinking, and no cell carries foam concentrate although the same block raises
alcohol-resistant foam.

**Scoring impact: none in v1, by design.** The checks score the *rated scalar* —
bollard pull, t·m, m³/h. A plan that commits enough lift and no divers is
resource-sound as v1 defines it. This is exactly the limitation §10.4 already concedes
and Q14 already decided: v1 establishes that a plan is resource-sound and attempts the
right goal, **not** that it could be executed.

So the author's sharpest version of this — *"a planner who only matches the rated
scalar scores full marks on an unexecutable plan"* — is **true and in scope**, not a
defect. It is worth re-reading §10.4 now that there is a concrete instance behind it.

**Why it still matters.** It is a ledger-plausibility defect regardless of scoring. A
competent planner asked to raise a wreck with three cranes and no divers may correctly
escalate — and that escalation would be scored as `over_refusal` on a satisfiable
ledger, because `ledger_satisfiable` only consults the rated scalar. **That is a path
by which a correct plan is marked wrong**, and it is the one item here with a
plausible route to the endpoint. Worth checking against §5.2's over-refusal rate once
real generations exist: if `over_refusal` is non-trivial and concentrated in
`capsized`/`sunken` cells lacking divers, this is the explanation.

**Options.** Add an enabling-kit rule to the generator — every `capsized`/`sunken`
ledger carries a dive team or ROV; every `on_fire` ledger carries a dewatering pump —
as a *precondition on ledger construction*, not a new check. It changes the asset
counts but not the rated-scalar sums, so `ratio_fleet` and `ratio_deadline` are
untouched and arm fidelity is preserved. That makes it the cheapest of the three
fixes and the one I would do first.

---

## 3. Boundary fragility

**Claim:** `SUN-00027`'s only in-window crane lands at 31.7 h against a 31.8 h
deadline — six minutes of margin. `AGR-00018`'s `TUG-006` arrives at *exactly* the
3.3 h deadline.

**Verified, and broader than the two cells spotted:**

- **40 counting assets sit within 2% of their cell's deadline, across 32 of 440 cells.**
- **33 of 440 cells lose satisfiability if any single in-window asset is removed** —
  the surplus over the requirement is smaller than the smallest contributing asset.

**Scoring impact: none today.** `arrives_by` is a deterministic comparison and the
corpus is frozen, so these cells score consistently every run. Arm fidelity is
currently exact: SURPLUS/SUFFICIENT 100% satisfiable, SCARCE/INFEASIBLE 0%.

**Why it matters.** These are the cells that would flip if the requirement magnitude
bands, the asset catalogue, or the ETA draw changed — and **all three of those tables
are still `"frozen": false`.** Any edit to `data/requirements.json` or
`data/assets.json` risks moving 33 cells across the satisfiability line, which would
break §7.3's arm-fidelity invariant and be caught by the manipulation check as a
corpus rejection rather than a result. It is an argument for freezing those tables
before generation, and for re-running `python -m rcp` after any edit to them.

A separate, smaller point: an asset arriving at *exactly* the deadline counts as
in-window (`arrives_by` is `<=`). That is a defensible convention and it is tested,
but it should be stated in §7.2 rather than left to the code.

---

## 4. `CAP-00076` is not a selection problem

Thirteen crane barges of **identical** 60,000 t·m rating, ten of them inside 12 h,
780,000 t·m in total against a 243,800 t·m requirement.

Two objections, both the author's. Real heavy-lift availability is nothing like this.
And more importantly for the experiment: with identical ratings there is no *choice* to
get right — the cell reduces to a division rather than a selection, so it discriminates
much less than a cell with varied capabilities would. Identical-rating ledgers are
worth auditing corpus-wide for the same reason.

---

## 5. One judgement call flagged for review

`CAP-00019` is **arithmetically sufficient but operationally marginal.** The three
sponson sets alone give 7,600 t·m against 9,200 required, so `RGT-002` is mandatory —
and it lands at 5.5 h, leaving 1.1 h to rig a parbuckling jack set.

The author wrote it as sufficient-with-a-no-roll-contingency rather than calling it
infeasible, and flagged the call itself. That is the right disposition for the gold
set — `ledger_satisfiable` is computed from the scalar and is `True`, so a gold plan
that refused would contradict the positive control — but the case shows the gap
between *satisfiable* and *achievable* at its narrowest, and it is the single best
example to cite when stating §10.4's limitation.

---

## Summary

| # | finding | scoring impact | route to the endpoint | cost to fix |
|---|---|---|---|---|
| 1 | `location` is noise | none | none | low (drop the column) or high (re-derive ETA) |
| 2 | no divers/ROV on ~70% of submerged cells | none in v1 (§10.4) | **plausible** — may inflate `over_refusal` | low (ledger precondition; scalars unchanged) |
| 3 | 33 cells one asset from flipping | none while frozen | only via editing the unfrozen tables | none — freeze first |
| 4 | identical-rating ledgers | none | weakens discrimination | medium (vary the catalogue) |

**Nothing here blocks the first run.** Findings 1, 3 and 4 do not touch an endpoint.
Finding 2 has a route to `over_refusal` and is the one to watch in the first real
report; it is also the cheapest to fix, because an enabling-kit precondition leaves
every rated-scalar sum — and therefore arm fidelity — exactly as it is.
