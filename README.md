# Resource-Constrained Planning (RCP)

Does a vision-language model's planning behaviour change when the resources it is
given change?

A VLM receives a maritime casualty image, domain knowledge, and a named, grounded
resource ledger. It writes a one-shot prose salvage plan. A validator then replays
that plan against the ledger and decides whether it was a resource-sound response to
the world it was actually given. The ledger is varied across four arms — `SURPLUS`,
`SUFFICIENT`, `SCARCE`, `INFEASIBLE` — over the same 110 images, so scarcity is the
manipulation and everything else is held fixed.

**`plan.md` is the specification and this file is the map.** Where they disagree,
`plan.md` wins. Section numbers below refer to it.

Successor to the P9 "plan adequacy" pipeline in `../Eval_CASTOR/pipelines/plan_adequacy/`.

---

## The one headline number

```
APPROPRIATE-RESPONSE  =  PLAN-SUCCEEDS      if LEDGER-SATISFIABLE
                         ESCALATE           otherwise
```

where `PLAN-SUCCEEDS = V5 ∧ V1 ∧ V2a ∧ V3` and `RESOURCE-VALID = V1 ∧ V2a ∧ V3`.

| check | question |
|---|---|
| `V5` | does a step attempt the casualty's terminal goal action? |
| `V1` | is every asset the plan names actually on the ledger? |
| `V2a` | does each committed asset arrive by the deadline, in the right scalar? |
| `V3` | does the committed capability meet the requirement? |

Everything else the pipeline computes — `ESCALATE`, `REDUCE`, `HALLUCINATE`,
`OVERCOMMIT`, the per-check rates — is **descriptive** and reported beside the
headline, never substituted for it. `REDUCE` is accepted, ignored, and descriptive
only.

**The invariant.** `¬LEDGER-SATISFIABLE ⟹ ¬PLAN-SUCCEEDS`. The validator raises
`AssertionError` on a violation per cell, and `report.invariant_check()` re-asserts it
over the whole run and suppresses every table if it ever fails. A violation is a bug,
not a result.

**P4 predicts the headline is flat across the four arms** — a competent planner
succeeds where it can and refuses soundly where it cannot. So **a null is the
substantive result**, which is why the analysis is one pre-registered test and why
§9.4's minimum detectable effect is a freeze gate rather than an afterthought.

---

## Pipeline

```
data/manifest.csv ─┐
                   ├─> generator.build_corpus()   110 images x 4 arms = 440 cells
data/*.json       ─┘        │
                            v
                     render.planner_prompt()      constant domain + varying ledger
                            │
                   image ───┤
                            v
                        rcp.infer                 Qwen3-VL-8B, greedy, k=1   [GPU]
                            │  generations.jsonl
                            v
                       rcp.extract                prose -> ExtractedPlan
                   ├─ extract_det   deterministic: IDs, steps, goal phrases
                   └─ extract_llm   4 binary fields via GLM-4-32B            [GPU]
                            │  extracted.jsonl
                            v
                      rcp.validator               pure arithmetic, never sees prose
                            │
                            v
                       rcp.report                 §9.2's five sections, in order
```

Supporting, off the main path: `rcp.controls` (§8.3 instrument controls),
`rcp.coverage` (§8.4 vocabulary gate), `rcp.calibrate` (§6.4 extraction loss),
`rcp.flags`, `rcp.normalize`, `rcp.schema`, `rcp.world`.

### Module map

| module | role |
|---|---|
| `schema.py` | `Asset`, `Requirement`, `Scenario`, `ExtractedPlan`, `Allocation`, `Verdict`. `Asset.quantity` is the **scalar dimension name** (`bollard_pull`), not a count. |
| `world.py` | loads the declared world from `data/`. Registries, not branches (§12.1). |
| `normalize.py` | ID normalisation, frozen with the check registry. |
| `generator.py` | builds the 440 cells; sizes each arm by `ratio_deadline`. |
| `render.py` | assembles the prompt; **where Rule 2 is enforced** (see below). |
| `infer.py` | the planner. The only stage that sees an image. |
| `extract_det.py` | deterministic extraction. No model, no network. |
| `extract_llm.py` | the four LLM fields, under vLLM guided decoding. |
| `extract.py` | composes both halves. |
| `validator.py` | the four checks. Pure, deterministic, prose-blind. |
| `flags.py` | the §5 flags as pure functions. |
| `controls.py` | positive/negative instrument controls (§8.3). |
| `coverage.py` | the V5 vocabulary gate (§8.4). |
| `calibrate.py` | per-field extraction loss against hand labels (§6.4). |
| `report.py` | the five printed sections; the print order **is** the analysis plan. |

---

## Three design decisions worth knowing before reading the code

**1. The validator is not an oracle for the planner.** It checks a plan; it does not
solve the problem. The alternative — per-casualty goal trees and a solver — is
designed and costed in `archive/casualty_tree.md` and rejected for v1 (Q14). The
accepted cost, stated plainly in §10.4: v1 does not establish that a plan reaches the
end goal, only that it is **resource-sound and attempts the right one**.

**2. V1 is immune to extraction error, structurally.** The LLM never produces a token.
`assets_named` is deterministic resolution against `ledger_ids`, and `commitments` is a
**subtraction** from that set, enforced in code. So the model can only ever remove an
ID, never invent one, and `HALLUCINATE` cannot be an extraction artifact. V2a, V3 and
`OVERCOMMIT` carry one LLM subtraction each, bounded above by `|assets_named|` — which
is measured, not asserted, by `rcp.calibrate`.

**3. Rule 2 is enforced by byte-identity, not by reading sentences.** Nothing in the
prompt may indicate which constraint binds. The enforceable form:

> the domain/assertion block is byte-identical across all 110 scenarios and all four
> arms; only the image and the ledger vary.

So the prompt is two constant files plus one varying middle, `domain_digest()` hashes
both constant halves, every generation row records that digest, and `test_render.py`
asserts the halves do not move. Two runs with different digests are not comparable and
must not be pooled. The ledger table sorts **by ID, not by ETA** — ETA order would put
the binding constraint at the top of the table.

Rule 1 (assertions may state facts about resources, never what to do when they fall
short) is audited line by line in `prompts/assertions_audit.csv`, with a written
reason per line.

### The §7.2 trap

`ratio_fleet > 1 ≥ ratio_deadline`: the fleet sum clears the requirement but the
by-deadline sum does not. A planner reading only totals passes; it fails because a
late asset cannot contribute to work due before the deadline. That is `OVERCOMMIT` as
a concrete, countable event. **`TRAP_FRACTION = 0.0` in v1** — no trap cells exist
yet; the arm is deferred to v2. Every chain still carries late assets of the
required class, so `OVERCOMMIT` stays countable.

### The frozen corpus (v0.10)

The arms are **nested**: one chain per image, `INFEASIBLE` ⊂ `SCARCE` ⊂
`SUFFICIENT` ⊂ `SURPLUS`, sharing requirement, geography and asset IDs. Ports are
invented per chain and ETAs follow from distance and type speed. The 440 cells are
generated once and frozen to `data/corpus.jsonl` + `data/corpus.sha256`; every
later stage reads that file, every generation row carries a `ledger_hash`, and
extraction refuses a row whose hash does not match. Phase A fails if `data/` no
longer regenerates the frozen file.

```bash
python -m rcp.corpus --check    # regenerate and compare; exit 1 on drift
python -m rcp.corpus --write    # (re)freeze — before inference only
```

All post-v0.9 changes and why: `docs/deviations.md`.

---

## Running it

### No GPU — everything short of generation

```bash
python -m rcp                              # Phase A gates: corpus + drift, controls, coverage, freeze
python -m pytest tests/ -q                 # 253 tests
python tools/simulate_delta.py             # the sec. 9.4 equivalence margin (delta = 0.20)
python -m rcp.coverage                     # the §8.4 vocabulary gate on controls/gold_plans/
python -m rcp.controls --out results/controls.json

# the whole pipeline, dry, no model:
python tools/mock_planner.py --out results/generations.jsonl
python -m rcp.extract  --input results/generations.jsonl --out results/ex --no-llm
python -m rcp.report   --input results/ex/extracted.jsonl \
                       --controls results/controls.json --out results/rep
```

`tools/mock_planner.py` writes prose by rule, deterministic in the scenario id, with
four behaviours (`gold`, `greedy`, `escalate`, `empty`) chosen so every branch of
§9.2's tables gets a numerator. It is a **smoke test for the plumbing**, not a
baseline. The dry run currently gives arm fidelity PASS and both non-negotiable
controls PASS over all 440 cells.

### On the cluster (AART `pleiades`, RTX6000Ada)

The host Python is 3.6, so everything runs in a container: `castor_qwen.sif`
(planning), `castor_judge.sif` (extraction, vLLM), `gemma4_judge.sif` (the only
one with pytest):

```bash
apptainer exec --containall --pwd "$PWD" --bind "$PWD:$PWD" --bind /tmp:/tmp \
    --env PYTHONPATH="$PWD" /data/$USER/gemma4_judge.sif \
    python3 -m pytest tests/ -q -p no:cacheprovider
```

The study run (v0.10): four arms × two conditions, **one output file per job**,
because `--resume` keys on `scenario_id/arm` and not on condition (it now refuses
a file whose rows carry another prompt's `domain_digest`):

```bash
for ARM in SURPLUS SUFFICIENT SCARCE INFEASIBLE; do
  for COND in blind stated; do
    sbatch jobs/plan_job.sh results/gen_${ARM}_${COND}.jsonl --arm $ARM --condition $COND
  done
done
# then, per file:                 (-> results/ex_gen_<ARM>_<cond>/)
sbatch jobs/extract_job.sh results/gen_SURPLUS_blind.jsonl
```

Each planning row records `n_tokens`, `truncated` (hit the 2048 cap),
`ledger_hash` and `run_id`; each job appends one environment record (packages, GPU,
container sha256, weights hash, git commit) to `<out>.env.jsonl`, and extraction to
`<out_dir>/env.jsonl`. Extraction cuts a greedy loop at its first verbatim-repeated
step before scoring (`looped_steps_dropped`, reported per arm as `looped`;
docs/deviations.md D9); the generation file keeps the full prose. The four-arm report concatenates the four blind
extractions; `rcp.compare` is run once per arm for blind vs stated.

**The image root is resolved, not passed.** There is one corpus, `data/manifest.csv`
pins all 110 of its members by relative path, and a run against some other directory
is not this experiment — so the path was only ever a way to get it wrong.
`plan_job.sh` probes `$RCP_IMAGES`, `$BENCHYBENCH_ROOT`, `$REPO/..` (the normal hit,
since RCP is a submodule of BenchyBench and `shipwreck_wiki_images/` sits at its
root), `$REPO`, then `/data/$USER/BenchyBench`. Candidates are **probed, never
guessed**, the rule from `QWEN-Maritime/CASTOR/benchybench_paths.sh`: if none holds
the image set the job stops and prints what it tried, because silently running the
wrong corpus is worse than a failed submission. Override with
`RCP_IMAGES=/path/to/sorted_images sbatch ...`.

`extract_job.sh`'s output directory is likewise derived from its input —
`results/gen_blind.jsonl` -> `results/ex_gen_blind/` — so two conditions cannot be
extracted into the same directory, where the second would silently overwrite the
first.

`plan_job.sh` passes everything after the output path to `rcp.infer` verbatim, so the
flags that scope a run live on the `sbatch` line, not in the script. It runs in
`castor_qwen.sif` — QWEN-Maritime's container, already validated against these weights
on this cluster. That container carries no vLLM, which is why `rcp.infer` generates
through `model.generate`; `castor_judge.sif` has vLLM but its 0.8.5 registry has no
`qwen3_vl`, so no single container can do both stages. Extraction stays on
`castor_judge.sif`, unchanged from P9.

### The disclosure run (one arm, two conditions) — the exploratory shape

The first experiment holds the arm fixed at `SUFFICIENT` and varies **one** thing:
whether the prompt names the casualty state, or the planner has to read it off the
image. 110 images x 2 conditions = 220 generations.

```bash
sbatch jobs/plan_job.sh results/gen_blind.jsonl  --arm SUFFICIENT
sbatch jobs/plan_job.sh results/gen_stated.jsonl --arm SUFFICIENT --condition stated

sbatch jobs/extract_job.sh results/gen_blind.jsonl    # -> results/ex_gen_blind/
sbatch jobs/extract_job.sh results/gen_stated.jsonl   # -> results/ex_gen_stated/

python -m rcp.compare --blind  results/ex_gen_blind \
                      --stated results/ex_gen_stated \
                      --out    results/disclosure.txt
```

`--arm SUFFICIENT` is what holds this to 110 cells rather than 440; without it the
4 h walltime is not enough. The two runs must go to different output files: `--resume`
keys on `scenario_id/arm` and not on condition, so pointing both at one file would
make the second job believe every cell was already done.

`stated` adds exactly one line — `Confirmed casualty state: <state>.` — to the
scenario block and changes nothing else. Deliberately not the natural-looking
version: pruning the other three states' guidance out of the domain block would vary
disclosure *and* prompt length together, so a difference could be attributed to
neither. The line goes in the scenario block, not the domain block, because the
domain block is the half Rule 2 holds byte-identical; `tests/test_render.py` asserts
that identity across both conditions now.

The condition is hashed into `domain_digest`, so the two runs carry different digests
even though neither constant file moved, and `rcp.compare` refuses to pair two files
whose digests agree — an agreeing digest means the manipulation never reached the
prompt, and a null result from a prompt that never varied is pure artifact.

**Use `rcp.compare`, not `rcp.report`, for this shape of run.** `rcp.report`'s primary
test is a four-arm linear contrast; at one arm every image is an incomplete case, so
it correctly declines to run and the report has no headline. `rcp.compare` supplies
the headline for the paired two-condition design: the difference in
`APPROPRIATE-RESPONSE` and an exact paired test on the discordant pairs. It is the
same test, specialised — with scores `(-1, +1)` the sign-flip permutation null *is*
`Binomial(n_discordant, ½)`, so the p-value is computed in closed form rather than
estimated. `tests/test_compare.py` checks that equivalence by enumeration.

Two things this run cannot measure, stated up front. **Correct refusal is untested**:
it needs an unsatisfiable ledger, and `SUFFICIENT` has none. And the requirement's
unit (`bollard pull` / `t·m` / `m³/h`) already correlates with the casualty, so even
`blind` is not a clean test of visual identification — it is a test of whether naming
the state changes the plan.

Cells are ordered **image-major**, so an interrupted run still yields complete images
for the paired test rather than complete arms. `--resume` skips finished keys and does
**not** count an empty generation as done.

Model paths use `/data/$USER/...`, expanded at runtime with `os.path.expandvars()`.
Never hardcode a username; `/data/shared/` is read-only.

### Calibration (§6.4)

```bash
python -m rcp.calibrate sample --input results/generations.jsonl --out cal/
#   ... a human fills cal/labels_blank.csv -> cal/labels.csv ...
python -m rcp.calibrate score --labels cal/labels.csv --extracted results/ex/extracted.jsonl
```

64 plans, balanced over arm x casualty state, deterministic (the sheet is a physical
artifact — a moving sample would stop lining up with a half-filled one). A blank cell
is **rejected**, never read as "no". **The figure to quote is `verdict_flip`**, not
per-field agreement: the endpoint is a conjunction and can move while every field
looks fine.

---

## What the report prints, in order

The order is the analysis plan — each gate precedes what it licenses.

| § | section | note |
|---|---|---|
| 0 | provenance | cells scored, extraction file, **the Rule 2 domain digest** |
| 1 | **manipulation check** | per-arm `LEDGER-SATISFIABLE` vs §7.3's required values, plus `ratio_fleet` / `ratio_deadline` quartiles. A corpus failing this is **rejected, not interpreted** — the endpoints below are suppressed |
| 2 | instrument controls | positive; negative **fails on V3** specifically; §8.4's `NO_MATCH` rate |
| 3 | **PRIMARY** | `APPROPRIATE-RESPONSE` per arm, with median steps/words beside it as the ceiling-artifact column, then the trend test |
| 4 | descriptive decomposition | `PLAN-SUCCEEDS`, `RESOURCE-VALID`, V5/V1/V2a/V3, §5.2's two refusal rates with `n/a` where the denominator does not apply |
| 5 | secondary flags | `ESCALATE`/`REDUCE`/`HALLUCINATE`/`OVERCOMMIT`, extraction loss stated adjacent. SURPLUS's `ESCALATE` rate **is** the affordance's false-positive rate |

**The test.** A paired sign-flip permutation test on one linear contrast per
complete-case image, scores `(-3, -1, +1, +3)` over the ordered arms. Paired, ordinal,
one comparison, stdlib only so a reviewer can read it, add-one p-value so it never
reports zero. Sign flips generate the null exactly. Complete-case: an image missing an
arm is **dropped, not imputed** — imputing would put a guess inside the headline.

---

## Status

**Built and tested end to end.** 253 tests pass. The dry pipeline runs
`mock_planner → extract → controls → coverage → report` with arm fidelity PASS and
both non-negotiable controls PASS over all 440 cells.

### Gates

| gate | state |
|---|---|
| §8.3 positive control | **PASS** — every gold plan scores `PLAN-SUCCEEDS` |
| §8.3 negative control | **PASS** — fails, and fails *on V3*, with V1 vacuously true |
| §8.3 cross-check | **PASS** — `satisfiable_without_gold` and `gold_without_satisfiable` both empty, in both directions |
| §8.4 coverage gate | **PASS — 0.0% `NO_MATCH`** over 10 blind-authored prose plans, all four casualty vocabularies exercised |
| §6.1 assertion audit | **DONE** — `prompts/assertions_audit.csv`, reason per line |
| §9.4 equivalence margin | **ENTERED** — δ = 0.20 (`tools/simulate_delta.py`; 80 % power at the worst-case variance) |
| §12.2 data freeze | **DONE** — all four data files `"frozen": true`; corpus sha256 `1154d352fd33…` |
| extraction calibration | **NOT YET** — first results are preliminary until hand labels exist |

### Known findings about the corpus

Recorded in `docs/corpus_realism.md` against the v0.9 corpus. 1 and 2 are **fixed**
in the v0.10 rebuild; 3 is partly fixed (deadline margin):

1. **`location` is noise.** Median ETA is 5.0–6.1 h at every one of the eleven named
   locations. Nothing scores it, so no check is affected; it is incoherent *realism*.
2. **Enabling kit is missing on submerged and inverted casualties.** Only 24/76
   `capsized` and 35/132 `sunken` cells carry a dive team or ROV.
3. **Boundary fragility.** 33/440 cells lose satisfiability if any single in-window
   asset is removed, and 40 counting assets sit within 2% of their deadline.

### Not doing, deliberately

Padding ledgers with distractors · resource state that advances per call (that is a
simulator) · `Asset.status` occupancy wiring (~15 lines, deferred) · a solver-based
validator (Q14).

---

## Layout

```
plan.md                    the specification
data/                      the declared world — manifest + four JSON registries
prompts/                   planner halves, extractor prompts, the assertion audit
rcp/                       the pipeline
controls/                  hand-written material: gold plans, stimuli, provenance
tests/                     206 tests
tools/                     manifest builder, mock planner
jobs/                      SLURM scripts
archive/                   earlier plan revisions, the rejected casualty-tree design
docs/                      findings
```
