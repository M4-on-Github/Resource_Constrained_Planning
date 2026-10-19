# RCP v0.13b: told, no totals, more wordings (pre-registration)

Written 2026-10-19 and frozen at tag `v0.13b-prereg`, before any v0.13b output
exists. It builds on `plan.md` (v0.10) and `plan_v013.md` (v0.13), both frozen.
Unless said here, the corpus, planner, decoding, container, extractor and
conventions are theirs. Every number below is printed by `tools/v013b.py`. Only
the 40 Track E dev images are run; the 70 test images stay unseen for v0.14.

## 1. Question

v0.13 found a GAP (G = +0.530): asked directly, the planner says an unsatisfiable
ledger falls short, but its plans do not escalate. Before v0.14 builds on that:

1. **Told (primary).** If the prompt states the shortfall, does the plan act on it?
2. **No totals.** Does knowing survive when the totals line is not printed?
3. **Verdict source.** Is any wording reliable enough for v0.14 to use the
   model's own verdict, or must v0.14 compute it?

## 2. Design

- **Cells.** 40 dev images (`cal/v013b/dev_ids.txt`, from `cal/track_e/split.csv`
  by `v013b.py prepare`) × 4 arms = 160.
- **Told plans.** Condition `told` is v0.10's blind prompt plus one line under the
  totals line, computed from the ledger (`rcp/render.py`, `told_line`):
  - unsatisfiable: "Computed check: on scene within 5.4 h, 170 t against 340 t
    required, short by 170 t. The requirement cannot be met by the deadline."
  - satisfiable: "… N t to spare. The requirement can be met by the deadline."
  - The task block is v0.10's plan request; decoding is v0.10's (2048 tokens).
    The plans are extracted by GLM as in v0.10.
- **No totals.** Condition `no_totals` is the blind prompt without the totals line,
  asked in v0.13's two wordings (64 tokens). The comparison with totals uses v0.13's
  answers on the same images; they are not rerun.
- **Three new wordings**, with totals:
  - `probe_task_enough.txt` (sha256 `8be34e56…`): "Is the combined capability on
    scene by the deadline enough to meet the requirement?" YES/NO; NO is short.
  - `probe_task_request.txt` (`b202278b…`): "Should more resources be requested
    before the work begins?" YES/NO; YES is short.
  - `probe_task_feasible.txt` (`eed460d7…`): v0.13's `can` question; first state
    the on-scene capability and the required amount, then FEASIBLE or INFEASIBLE
    alone on the last line (256 tokens).
- `tests/test_v013b.py` asserts that `told` adds exactly one line and `no_totals`
  removes exactly the totals line, that the told line agrees with
  `ledger_satisfiable` on all 440 cells, and that no recorded digest moves.
- **Not run.** Sampling, the stated condition, the test split.

## 3. Measures

- **Acts when told.** ESCALATE on each told plan, labelled on all 160 by two model
  labellers, A and B, as in v0.13. They are two fresh instances of one language
  model. Each gets only `cal/d11/LABELLING.md` and `cal/v013b/sheet.md` (shuffled,
  seed 20261019, plan text as extraction scored it, no arm, ledger or key). The
  extractor's flag is printed.
- **Reading.** YES/NO wordings as v0.13 (`rcp/probe.py`). `feasible`: the last
  non-empty line, stripped of punctuation and markdown, must be FEASIBLE or
  INFEASIBLE; otherwise it is unparsed.
- **K** per wording, as v0.13: per image, the share saying "short" on the two
  unsatisfiable arms minus the two satisfiable arms, on complete-case images.

## 4. Primary test (one)

- **E_told.** Per image, labelled ESCALATE averaged over SCARCE and INFEASIBLE,
  minus the same over SURPLUS and SUFFICIENT. Report the mean with a paired 95 %
  CI, normal approximation, n = 40.
- **Verdict:**
  - Lower bound > 0.50: **ACTS WHEN TOLD**.
  - Upper bound < 0.20 (the study's δ): **DOES NOT ACT WHEN TOLD**.
  - Otherwise: **IN BETWEEN**.
- It stands only if labels A and B agree; otherwise it is **LABELLER-DEPENDENT**.
- v0.10's blind E on the same images is printed beside it. It is +0.025 under
  labels A and +0.037 under labels B (known before this plan).

## 5. Controls and halt rules

1. **Reproduction (halt).** In the same job, before anything else, regenerate
   v0.10's plans and v0.13's two probe answers for `cal/v013b/repro_ids.txt`
   (3 dev images × 4 arms, seed 20261019). All 36 must be byte-identical. If any
   differ, nothing is analysed and a deviation is recorded.
2. **Files (halt).** Every output has dev images only, one row per cell, and its
   prompt's digest. The told extraction must carry the told digest.
3. **Always printed.**
   - ESCALATE per arm, told and v0.10 blind, per labeller and extractor.
   - Told against blind: AR, OVERCOMMIT, V2a, V3, RESOURCE-VALID.
   - The share of escalating unsatisfiable told plans that still commit a late
     asset (fail V2a).
   - Per wording: the parse rate, "short" on unsatisfiable and on satisfiable
     cells (false alarms), and K.

## 6. Power (`v013b.py power`)

- **Told.** Assumes satisfiable escalation 0.05 and, as the worst case, that both
  cells of an arm pair always agree.
  - ACTS WHEN TOLD: power 0.93 if unsatisfiable cells escalate at 0.80, and 0.46
    at 0.70. Power reaches 80 % at 0.76.
  - DOES NOT ACT WHEN TOLD: 0.98 at 0.05 and 0.73 at 0.10.
- **No totals.** The CI half-width of ΔK is 0.173. This assumes v0.13's dev K
  SD (0.246), a worst-case SD of 0.50 without totals, and independence.
- **Self-verdict.** A wording that never misses clears the bar if it false-alarms
  on at most 10.5 % of satisfiable cells.

## 7. Secondary (by rule, not the primary)

- **No totals.** ΔK = K without totals minus K with totals. It is pooled over
  v0.13's two wordings (k as in v0.13) and paired by image. Per-wording values
  are printed.
  - Upper bound < −0.20: **COLLAPSES**.
  - Lower bound > −0.20: **HOLDS**.
  - Otherwise: **UNCLEAR**.
- **Verdict source for v0.14.** Take the wording with totals that has the highest
  K, out of five: v0.13's two and the three new ones. It is a **SELF-VERDICT** if
  K's lower bound is > 0.80 and its parse rate is ≥ 95 %. Otherwise it is a
  **COMPUTED VERDICT**.

## 8. What each outcome means

- **ACTS WHEN TOLD.** The gap is in drawing the conclusion, not in acting on it.
  v0.14 gives the verdict first (self or computed, per §7), then asks for the plan.
- **DOES NOT ACT WHEN TOLD.** Being told is not enough. v0.14 needs a structural
  lever (a mandatory feasibility field in the plan) or another model.
- **IN BETWEEN.** Report it as such. v0.14 then compares verdict-first against a
  mandatory feasibility field.
- **LABELLER-DEPENDENT.** Report it. Settling it needs hand labels.
- **ESCALATE rises but late assets are still committed.** The plan repeats the
  verdict without changing. This is printed beside the primary and does not
  change the verdict.
- **No totals COLLAPSES.** v0.13's "knows" narrows to "reads the printed total",
  and v0.14 must print totals or compute the verdict. **HOLDS**: the model adds up
  the ledger itself.

## 9. Limits, stated before the run

- **Told breaks plan.md §7.2's trap on purpose.** The line names the deadline and
  the verdict. E_told measures acting on a supplied conclusion, not reaching it.
- **Repeating counts.** Under the label rule, a plan that copies the verdict line
  and asks for more counts as escalating. V2a and OVERCOMMIT are printed beside it.
- **Some numbers are already known.** `probe_short`'s dev K, +0.887 [+0.813,
  +0.962], comes from v0.13 and on its own clears the self-verdict bar. A new
  wording replaces it only by scoring higher. The with-totals side of the
  no-totals comparison is v0.13's, also already seen.
- **The sample is small.** It is the dev split only (40 images), so the test split
  stays unseen for v0.14.
- **The labels are model labels**, not hand labels.
- **One draw.** A single greedy float16 draw per cell (D10 stays open).
- **The wordings are fixed here**, with no pilot.

## 10. Run

```bash
python3 -m pytest -q                                      # must pass before submitting
sbatch --exclude=pleiades-1-3 jobs/v013b_job.sh           # repro cells, probes, told plans
sbatch --exclude=pleiades-1-3 jobs/extract_job.sh results/v013b/told_plan.jsonl
python3 tools/runs.py freeze v013b --purpose "plan_v013b.md" results/v013b
python3 tools/v013b.py sheet                              # -> cal/v013b/sheet.md
python3 tools/v013b.py report                             # -> results/v013b/report.txt
```

The run is registered as `v013b` and its code is tagged `run/v013b`. The labels
go in `cal/v013b/labels_a.csv` and `labels_b.csv` and are committed before
`report` runs.

## 11. Deviations

Append-only and dated. Anything changed after the tag goes here, with what
motivated it.

*None yet.*
