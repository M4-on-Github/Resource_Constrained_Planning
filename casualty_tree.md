# Casualty goal trees — all four, feasibility

**Status: designed, costed, and not adopted for v1.** Referenced appendix to
`plan.md` — the resolution is `plan.md` §13 Q14, the staged entry path is §12.3, and
this file is the argument behind both. Retained under §12.2's rule that superseded
design text is marked superseded, never deleted.

Question it was written to answer: does a solver-capable validator stay exhaustive,
and what does each casualty type cost over the current design?

## Summary

| | n | objective | terminal | new scalars | routes collapse? | blocker |
|---|---|---|---|---|---|---|
| `aground` | 42 | refloat, get under tow | `UNDER_TOW` | +1 transit pull | **yes** — all push on pull | tide waiting moves the IV |
| `capsized` | 19 | right, then refloat, then tow | `UNDER_TOW` | +1 pull, after a **unit change** t·m → t | **yes** — all push on moment | deepest chain, smallest-but-one n; 2nd deadline |
| `sunken` | 33 | raise and transport, **or** remove in place | **two terminals** | +1 transit pull | **no** — root OR, different asset classes | scarcity drives terminal-switch, not refusal |
| `on_fire` | 16 | extinguish, then tow | `UNDER_TOW` (+ a 2nd terminal) | — | **partly** | **the unit is a rate** — needs a clock |

**Routes collapse** means every way of achieving the node pushes on one inequality,
so the solver searches discrete modifiers rather than paths. That is what keeps
search exhaustive.

**Shared:** all four converge on `AFLOAT → TOW_RIGGED → TRANSIT_CAPABLE → UNDER_TOW`.
The tow sub-tree is written once.

---

## 1. `aground` — n = 42

**Objective:** break the vessel out of the ground and get it under tow to a yard.

```
UNDER_TOW ← AFLOAT ∧ TOW_RIGGED ∧ TRANSIT_CAPABLE
AFLOAT ⟺ Σ(pull committed) + beach_gear ≥ pull_req − lightening_δ − tide_δ − dredge_δ
```

Five routes — direct pull, lightening, beach gear, higher tide, dredging — all add
pull or reduce required pull. One inequality, discrete modifiers.

**Search:** 4⁶ roles × 3 lightening × 2 tide × 2 dredge ≈ **49 k**. Trivial.

| vs. existing | |
|---|---|
| **gain** | lightening moves from an LLM-read `REDUCE` flag to a **symbolic** score — off the lossy path |
| **cost** | +1 scalar, +2 nodes, ordering via F5 |
| **unchanged** | V1, V2a, the `IMG-042` ETA trap, the arms, §10 |

**Risk:** waiting for a higher tide reduces the requirement, so it is a
*planner-selectable change to the IV*. Bound the delta, or drop the option and keep
tide waiting as `REDUCE`. Recommend the latter.

## 2. `capsized` — n = 19

**Objective:** right the vessel, then refloat it, then tow.

```
UNDER_TOW ← AFLOAT ← RIGHTED
RIGHTED ⟺ Σ(moment committed) ≥ moment_req − dewatering_δ − buoyancy_δ
```

Parbuckling, compartment dewatering, high-side ballasting, pontoon buoyancy — all
push on righting moment. Collapses like aground.

| vs. existing | |
|---|---|
| **gain** | same — dewatering/buoyancy become symbolic routes |
| **cost** | **deepest chain**, and a **unit change mid-tree**: t·m to right, then t to refloat. Two requirement scalars in different units |
| **risk** | the progressive-flooding deadline governs righting; does it still bind during refloat? A second temporal phase, which the world has no clock for |

**n = 19 is the problem.** The deepest tree sits on the second-smallest cell.

## 3. `sunken` — n = 33

**Objective:** raise the vessel and transport it — **or**, if it cannot be raised,
remove it in place.

```
          ┌── DELIVERED ← UNDER_TOW ← AFLOAT ← RAISED
ROOT (OR) ┤
          └── REMOVED_IN_PLACE ← cut up / sever / clear
RAISED ⟺ Σ(lift capacity) ≥ lift_req − deballast_δ − cargo_δ − staged_lift_δ
```

**The routes do not collapse at the root.** Raising needs cranes and lift barges;
removal in place needs divers and cutting gear. Different asset classes, so it is a
genuine OR, not a modifier. Under each terminal it collapses again.

**Search:** two sub-trees, each aground-sized. Still exhaustive.

| vs. existing | |
|---|---|
| **gain** | the root OR gives `DEGRADE` the route vocabulary it lacks — **promotes it from exploratory to scoreable** |
| **cost** | two terminals; `LEDGER-SATISFIABLE` becomes "satisfiable under *either*" |
| **risk** | **scaling the ledger down no longer makes it infeasible — it makes the other terminal correct.** So `INFEASIBLE` produces terminal-switching, not refusal |

That last row is the real cost: P1 and P6 pool refusal across all 110 images, and for
sunken they would be measuring strategy change instead. Either declare every sunken
scenario liftable-in-principle, or state the refusal predictions per casualty type
and lose the pooled *n*.

## 4. `on_fire` — n = 16

**Objective:** extinguish, then tow to a yard. Secondary terminal: controlled
scuttling, which hands the problem to the `sunken` tree.

```
UNDER_TOW ← AFLOAT? ← EXTINGUISHED
EXTINGUISHED ⟺ Σ(water delivery m³/h) ≥ delivery_req − foam_δ − inerting_δ
```

| vs. existing | |
|---|---|
| **cost** | **the unit is a rate, not a quantity.** Today V3 compares a committed rate to a required rate and that is sound. "The fire is out" is an achieved state — rate × duration ≥ volume — which needs the clock §3.3 says the world does not have |
| **risk** | scuttling is a genuine measure and a second terminal; "let it burn out" is sometimes correct |
| **risk** | `AFLOAT?` is conditional — a burning vessel afloat needs only a tow; one aground needs refloating too. **Not observable from the image** |

**n = 16, and the hardest unit problem.** This is the type to leave at
stabilization.

---

## Cross-cutting

1. **Collapse is the viability test.** aground and capsized collapse; sunken and
   on_fire have root ORs to terminals with different asset classes. Only the first
   pair is cheap.
2. **Two types need a clock.** on_fire (rate × duration) and capsized (a second
   deadline phase). §3.3 rules one out as not constructible from prose.
3. **Depth is inverse to n.** The deepest trees land on n = 19 and n = 16.
4. **The tow sub-tree is shared** by all four. Written once, reused.
5. **Two types need an unobserved fact** — is the burning / capsized vessel *also*
   aground? Determines whether refloat is in the path. Not in the corpus, not in
   `human_gt`.
6. **Search stays exhaustive everywhere**, given the ≤ 8-asset ledger invariant.
   Computation was never the constraint; the measurement was.
7. **`hull_status` stays out** of all four. A holed vessel refloated sinks, which is
   a real precondition — but modelling it is the first step back to P9's
   precondition graph. State as a limitation.

## Staging

| stage | content | cost |
|---|---|---|
| **0** | lightening / dewatering **OR-branch only**, no tree. One scalar, 64 subsets, arms untouched | pre-freeze-able now; captures the main gain for `aground` + `capsized` |
| **1** | full trees for `aground` + `capsized`, shared tow sub-tree, no root ORs | the four-section rewrite; needs the unit-change and 2nd-deadline decisions |
| **2** | `sunken` + `on_fire` root ORs | needs a `DEGRADE` vocabulary, a clock, and a decision on pooled vs. per-type refusal predictions |

Stage 0 gets most of the symbolic-scoring gain for 61 of 110 images at near-zero
cost. Stage 2 is where the study changes character.

## Correction to the earlier draft

The first version of this file said the tree was "smaller than expected" on the
strength of `aground`. That was a selection error: `aground` was picked as the
*hardest* type for having the richest route space, but richest routes turned out to
mean *most routes that collapse into one inequality* — the best case, not the worst.
`sunken` and `on_fire` are where the architecture actually strains.
