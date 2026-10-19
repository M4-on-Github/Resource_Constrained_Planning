# Deviations log

Every change to the design, the corpus, the prompts or the instrument made after
plan.md v0.9 (2026-10-07), with what motivated it. plan.md §12.2 requires this:
a change made after seeing data is admissible only if it is recorded, and a
reader has to be able to tell which results it could have been tuned against.

## D0. The exploratory run (2026-10-07/08) — not part of the study

`SUFFICIENT` only, 110 images × {blind, stated}, Qwen3-VL-8B greedy,
`max_new_tokens` 1024; extraction GLM-4-32B GPTQ, `max_tokens` 256.
SLURM jobs `rcp_plan_49799/49800/50128/50129`, `rcp_extract_50130/50131`.

| | blind | stated |
|---|---|---|
| `APPROPRIATE-RESPONSE` | 19.1 % | 11.8 % |
| V2a-only failures | 71 / 110 | — |
| plans hitting the 1024-token cap | 37 | 31 |
| extractor replies failing to parse | 7 | 17 |
| plans with ≥ 1 conditional step | 108 | 109 |

This run was used to find instrument faults, so **every fix below was motivated by
on-corpus data** — the same 110 images the study uses, at one of its four arms.
That is the deviation: plan.md §6.4 asks for tuning off-corpus. It is accepted
because (i) none of the fixes reads the planner's resource behaviour, only how it is
measured, and (ii) the exploratory plans are kept, unscored, as the extraction
calibration set (`cal/exploratory/`), not reused as results. Its numbers are never
pooled with the study's.

## D1. Single-course guard in the planner prompt (§6.2)

*Found:* ~8 conditional steps per plan; V2a and V3 were scoring the union of
every branch, so backup assets counted as committed (most of the 71 V2a-only
failures). *Changed:* one line in `prompts/planner_task.txt` telling the planner
to commit to a single course of action with no "if … then" branches. Structural;
names no resource or shortfall (`tests/test_render.py`). The `ESCALATE`
affordance line is unchanged. *Measured, not assumed:* `conditional_steps` per
plan (`rcp/extract_det.py`), reported per arm.

## D2. Extractor scope and escalation rules (§6.3)

*Found:* the extractor counted backup / contingency / post-goal assets as assigned,
and read "if the refloat fails, request more tugs" as escalation — overcounting
`ESCALATE`. *Changed* (`prompts/extract_system.txt`): assigned means toward the
goal at or before the goal step; backup, post-goal and other-branch assets are not
assigned; escalation is true only when the plan says resources fall short or asks
for more *before* attempting. Extraction error is **not yet measured** against hand
labels — first results are reported as preliminary on that account.

## D3. Token caps and retry

*Found:* 68 truncated plans; 24 unparseable extractor replies, undiagnosable because
the raw reply was discarded. *Changed:* planner `max_new_tokens` 1024 → 2048 with
`n_tokens` and `truncated` recorded per row; extractor 256 → 768, one retry at 2048
for a reply that fails to parse, raw reply / finish reason / attempt count kept in
the trace.

## D4. V1 made non-vacuous (§4)

*Found:* `assets_named` held only resolvable tokens, so V1 could not fail.
*Changed:* unresolved ID-shaped tokens are collected and fail V1, with zero-padding
and end-of-text truncation exemptions. *Rescanned:* the exploratory plans contained
no invented IDs under the new rule, so their `HALLUCINATE ≈ 0` stands.

## D5. Corpus rebuilt (§7.2) — `docs/corpus_realism.md` findings fixed

Nested arms with stable random type-prefixed IDs; invented ports and
distance-consistent ETAs; deadline margin max(0.3 h, 5 %); enabling kit in every
arm; `SURPLUS` realised ≥ 2.0 ×. Two tuning choices made while building it, both
for realism rather than for any outcome:

* **Lift-bag transit speed 20 → 10 kn** — bags travel as deck cargo on a workboat,
  not under their own power.
* **Type exploration** (25 % of draws from any placeable type, not just the nearest
  capability band) — without it `CAP-00019` (9 200 t·m by 6.6 h) could only be met
  by one asset class and the chain never closed.

Realised per arm (mean on-time ratio / ledger size): `SURPLUS` 2.86 / 18.6,
`SUFFICIENT` 1.22 / 13.0, `SCARCE` 0.51 / 7.9, `INFEASIBLE` 0.27 / 6.0;
satisfiable 110 / 110 / 0 / 0. Frozen to `data/corpus.jsonl`, sha256
`1154d352fd3306c520e2f6d4a47f9f83c67e7ed79b24acc950b8676f2a21e364`.

## D6. Predictions and primary analysis (§9)

P1 → P1′ (unsatisfiable-vs-satisfiable `ESCALATE` contrast, paired CI); P4 → P4′
and the primary from a trend test to an **equivalence test**, δ = 0.20 from
`tools/simulate_delta.py`; blind primary, stated a descriptive factor. Entered
2026-10-09, **before any four-arm generation exists**. The exploratory run informed
that the endpoint is far from ceiling (19 %) but not the margin, which depends
only on n and the worst-case variance.

## D7. Reproducibility

Frozen corpus + sha; `ledger_hash` on every generation row, checked at extraction;
one environment record per job (`*.env.jsonl` / `env.jsonl`: packages, GPU,
container sha256, weights hash, `run_id`). Output files are per arm and condition,
`results/gen_<ARM>_<cond>.jsonl`, because `--resume` keys on `scenario_id/arm`.

## D8. Smoke run (SLURM 50412, 2026-10-09)

10 images, `SUFFICIENT`, blind, before the full run, to check guard compliance
(`conditional_steps`) and the truncation rate at 2048. Its outputs are kept (run
`v010`) but are not results. Guard: 7 of 10 plans ran 401–766 tokens with a median
of 1 conditional step (exploratory blind: 6.5). Truncation: 3 of 10 hit 2048, every
one a loop — see D9.

## D9. Greedy loops cut at the first repeated step (found by D8)

*Found:* AGR-00017, -00041, -00045 reprint an earlier step verbatim (renumbered)
until the token cap — greedy decoding's self-reinforcing repeat. Not new: the same
rule finds 10 blind and 15 stated exploratory plans looping, all inside D3's 1024-cap
truncations, so a share of D3's "truncated" was loops, not long plans, and raising
the cap could not fix them. *Considered and rejected:* a no-repeat-n-gram ban at
decoding. A loop's longest repeated token run is 24–71 tokens (the step number
changes between copies), while plans that do not loop repeat runs of up to 22 (D8)
and, in the exploratory plans, up to 64 below the cap (AGR-00086) and 73 at it; no
n separates them, and the ban would alter clean plans. *Changed:*
`extract_det.trim_repeated_steps` cuts a plan at its first marker-led step whose
text (number, case and spacing ignored) repeats an earlier step; both the
deterministic pass and the extractor see the cut plan. Under greedy decoding this
is exactly what a stop-on-repeat rule during generation would produce, so nothing
is regenerated and the planner's output is unchanged. On D8 it cut the three loops
(to 7, 19 and 4 steps) and no other plan; in the exploratory plans it fires only on
cap-length plans. Recorded per row as `looped_steps_dropped`, reported per arm as
`looped` beside `truncated` (§9.2). Decided after seeing D8, before any four-arm
generation exists.

*Provenance of the study run (2026-10-09).* Planning jobs 50413–50427 (odd) started
from commit a399b95, whose planning path D9 does not touch; extraction jobs
50414–50428 (even) start after them and run the D9 commit. Their environment
records predate the `git_commit` field (SLURM snapshots job scripts at
submission), so this paragraph is the record of which commit each stage ran.

*Job 50417 (`SUFFICIENT`, blind) crashed* at cell 44 of 110 (CAP-00006) with a
CUDA device-side assert inside `generate` (`modeling_qwen3_vl.py`, the
`cache_position` check); the 43 rows before it were flushed and kept, and its
extraction 50418 was cancelled before it ran. Resumed as job 50430 on the same node
(pleiades-0-17, `--resume`, same commit): it wrote CAP-00006 normally (412 tokens)
and crashed the same way at its cell 47 (SUN-00094); extraction 50431 was
cancelled before it ran. Resumed again as job 50433 with `--exclude=pleiades-0-17`
and `CUDA_LAUNCH_BLOCKING=1` (pleiades-0-23): it completed the remaining rows,
SUN-00094 included, with no error. Extraction 50434 ran on all 110 rows (25 looped,
0 parse failures). Rows from the three planning jobs are told apart by `run_id`.

*Are the rows written by the crashed jobs sound?* Generation is deterministic: the
smoke run (D8) and 50417 agree byte for byte on their 10 shared cells, the three
2048-token loops included. Job 50435 (pleiades-0-23) regenerated five rows the
crashed jobs saved — AGR-00224 and CAP-00002 from 50417, CAP-00006, SUN-00073 and
SUN-00091 from 50430 — and all five are identical to the saved rows. Its output
(`results/diag/verify_SUFFICIENT_blind.jsonl`) is a check, not a study result.
Image size is not the trigger (29 images of 5 MP or more ran cleanly elsewhere),
and both crashes hit different inputs that run cleanly on another node, so the
likeliest cause is a faulty GPU on pleiades-0-17. Not proven: the planning jobs
did not yet log the GPU's UUID, so it cannot be shown both crashes used the same
card. The job scripts now log it.

*Sensitivity to D9 (preliminary).* Dropping every looped plan and re-running the
report on the complete-case images that remain (blind 45, stated 62) leaves the
primary NOT ESTABLISHED, with a larger fitted decline (blind −0.287, 90 % CI
[−0.443, −0.130]; stated −0.203 [−0.334, −0.072]). Looping is concentrated in
`SURPLUS`, so this subset is not a random one; it is reported beside the primary,
not instead of it.

## D10. v0.11 commitment header in the planner prompt (§6.2) — FAILED its test

*Found, after the four-arm run (so this is a post-data change and the v0.10 run
becomes a pilot if it is adopted):* the single-course guard (D1) did not hold.
Blind plans with ≥ 1 conditional step: 78–90 % per arm (3.9–5.9 per plan); stated
67–81 %. Two sources. (i) Branching on the casualty type ("if the vessel is found
to be aground…"): 66 / 440 blind plans, 5 / 440 stated — the blind planner hedges
over what the photo shows instead of deciding. (ii) Contingency branches ("if the
pull is insufficient, add TUG-006"), in both conditions. The branches matter
because the extractor under-excludes their assets. A hand read of 20 random
`SURPLUS`/blind V2a failures (`tools/audit.py v2a SURPLUS blind 20 7`) found 9
where the late asset appears only in a backup, "if it fails", other-casualty or
explicitly "do not commit" step, against D2's rule; 9 used it in the main
operation and 2 were unclear (the per-plan reading was not kept). The extractor
excluded 4.6 % of named assets in `SURPLUS`/blind (1.1–4.4 % in the other blind
arms). Of the 16 looped `SCARCE`/blind plans, 5 are scored as escalating
(`tools/audit.py loop SCARCE blind`): 2 clearly, 1 calls its capacity
insufficient and then says it meets the need, and 2 only say "if still grounded,
deploy more", which D2's rule does not count. (The extractor fix is separate and
needed regardless; it is not part of D10.)

*Changed:* `prompts/planner_task.txt` asks for three lines before the plan —
`Casualty type:` (choose one), `Observed conditions:` ("cannot tell from the
image" allowed), `Course of action:` — then `Salvage Plan:` and the steps. The
mechanism is P9's `prompt_procedural_v3.txt`, where the same planner on the same
images committed to a casualty type in 110 / 110 and wrote a conditional step in
28 / 110 plans, almost all "if recovered, tow", which that prompt itself asks for.
Not carried over from P9 v3: its ban on "adequate / sufficient / as required" and
on deferring to another person (both would suppress `ESCALATE`), its technique
catalogue and order lists (domain content, not format), and "if recovered, tow".
The guard line now reads "every step is an action that will be carried out";
the `ESCALATE` affordance line is unchanged, and no new line names a resource,
a shortfall or a request (`tests/test_render.py`). Extraction reads off the header
(`extract_det.split_header`), scores only the text after `Salvage Plan:` so an ID
in "Course of action:" is not a named asset, and records `declared_casualty` per
row. On the 880 v0.10 plans `split_header` changes nothing (0 / 880).

*Test, fixed before any v0.11 generation.* §6.4 asks for format tuning on CASTOR
images outside the 110; none exist (`sorted_images` holds exactly the 110). The
test therefore runs on the study's images and is confined to properties of the
prose, never an endpoint: no extraction, no validator, no `ESCALATE`. 30 images,
stratified 11 / 9 / 5 / 5 by state (`cal/v011_guard/ids.txt`, seed recorded
there), × {`SURPLUS`, `SCARCE`}, blind, greedy, 2048 tokens. `tools/guard_check.py`
compares against the same 60 cells under v0.10. Accept if all hold:

| criterion | threshold | v0.10, same 60 cells |
|---|---|---|
| header present with one declared state, and a `Salvage Plan:` label | ≥ 95 % | 0 % |
| plans with ≥ 1 conditional step (plan section only) | ≤ 30 % | 73.3 % |
| conditional steps per plan | ≤ 1.0 | 5.53 |
| looped plans | ≤ v0.10 | 31.7 % |
| truncated plans | ≤ v0.10 | 35.0 % |

Declared-state accuracy against `casualty_state` is reported, never a criterion:
it measures the planner's vision, not the prompt's format. If a criterion fails,
one further wording revision is allowed under the same rules and recorded here.

*Test 1 (job 50449, pleiades-0-23, 60 / 60 cells): FAIL.* Header 100 % (state
correct 70 %, reported only); plans with a branch 76.7 % (v0.10 73.3 %); branches
per plan 2.68 (5.53); looped 31.7 % (31.7 %; `SURPLUS` 53.3 % vs 43.3 %, `SCARCE`
10.0 % vs 20.0 %); truncated 33.3 % (35.0 %). The header did what it was for:
plans branching on the casualty type fell from 12 / 60 to 1 / 60. What remains is
contingency branches ("if the vessel does not refloat by T+3.1 h, lighter with
BRG-048"; "use HLB-012 … if needed"), which the v0.10 guard line already forbade
in words. In `SCARCE`, 28 of the 80 branch steps ask for more resources ("request
additional resources if the 300 t lift capacity proves insufficient"): that is
`ESCALATE` phrased as a condition, so a revision must remove the condition without
discouraging the request.

*Revision 2 (the one further revision allowed above), fixed before its generation.*
Three changes to `prompts/planner_task.txt`; the `ESCALATE` affordance line and
every Rule 1 / Rule 2 check are unchanged (`tests/test_render.py`):
- the plan is "a numbered sequence of at most 15 steps": v0.10's clean plans have
  a median of 10–14 steps and its looped plans start repeating after a median of
  17, so the cap sits above most real plans and below where loops begin;
- "Name only the assets the plan uses.", against backup and "will not be used"
  assets appearing in the steps (the D10 extractor audit);
- the guard line says what a committed plan is instead of only forbidding the
  form: "write the one plan you will carry out, not a set of options to choose
  from later. Every step is an action that will happen, and no step depends on
  how an earlier step turns out. So do not write conditional steps, backup or
  reserve steps, steps that wait to see whether an earlier step worked, or
  alternatives." It names no shortfall and no remedy, and bans no word:
  "adequate / sufficient" stay allowed (P9's ban would suppress `ESCALATE`), so a
  conditional request can become an unconditional one.
As first committed (`e113a84`), revision 2's guard was a list of banned words
("if", "unless", "in case", "in the event", "otherwise", "as needed", "as
required"). It was replaced before any generation, because banning the words the
branch count looks for lets a plan pass the count by paraphrase without
committing; a description of the goal leaves the count an honest measure.
Same 60 cells, same criteria, same baseline; output
`results/v011_guard/gen_blind_r2.jsonl`; domain digest `c46a8667…`.
`tools/guard_check.py` gains a report-only column, "hedge, no if": plans with a
step that hedges ("as needed", "on standby", "backup", "where necessary", …)
without a word `conditional_steps` counts. On test 1 it is 33.3 % for both v0.10
and v0.11. It is read alongside the branch criteria, never as one. If revision 2
fails, prompt work stops here: v0.10 stands as the study and the branching is
handled in extraction (D11).

*Dtype check (job 50450, commit `60b2fdd`, tag `run/dtype_check_bf16`; not merged).* v0.10
loads the planner in float16, copied from QWEN-Maritime's `run_inference.py`;
the checkpoint is bfloat16. 30 `SURPLUS` / blind cells under the v0.10 prompt
(same domain digest) were rerun in bfloat16 (`cal/dtype_check/ids.txt` at that
tag): 20 whose float16 plan looped, 10 clean. Looped 6 / 20 and 2 / 10 (float16:
20 / 20 and 0 / 10); prose identical in 0 / 30. The groups were selected on the
float16 outcome, so most of the drop is that selection: any numerical change moves
a greedy path off its repeat, and it moved two clean plans onto one. Weighted by
stratum, bfloat16's `SURPLUS` / blind loop rate is roughly 23 % against float16's
33 %, uncertain at n = 30. Dtype is not the loop's cause; greedy decoding on long,
branching plans is. **Decision: dtype stays float16 for v0.11**, so the revision 2
test and any v0.11 run differ from v0.10 in the prompt alone. bfloat16 is left as
a named open item, to be settled before a later version, never mid-run.

*Review before revision 2's generation (no new generation read; fixed before it).*
- **Parser.** `split_header` missed three plan labels a model could plausibly
  write: a heading with no colon ("### Salvage Plan"), a qualifier ("Salvage Plan
  (refloat):") and a number ("4. Salvage Plan:"). In each the whole prose, header
  included, would have been scored. It also read "Casualty type: fire" as no
  declared state, so "header ok" would fail a committed plan. Fixed: the looser
  label forms are tried only after a "Casualty type:" line and only when the
  exact label is missing, and the label must stand alone on its line, so a step
  that mentions "the salvage plan" is never taken for one. Bare "fire" now counts
  as `on_fire` unless "no" or "not" precedes it. On the 880 v0.10 plans and test
  1's 60, `split_header` returns the same result as before for all 940; the
  cases are in `tests/test_extract.py`.
- **No-harm flag for `ESCALATE` (report-only).** `tools/guard_check.py` gains
  "asks/escalate": the share of plans whose plan section asks for resources or
  escalates (a fixed regex, `REQUEST`). P1′ is the `ESCALATE` contrast, so a guard
  that talked the planner out of asking would remove the outcome being measured.
  Test 1 did not (`SURPLUS` 53.3 % → 66.7 %, `SCARCE` 36.7 % → 70.0 %, same
  cells; v0.10 over all 110 blind images: 52–61 % per arm). The flag is not a
  criterion. If it falls well below v0.10 on revision 2, the run is reported and
  the drop is read before anything is adopted. Also reported only: the share of
  plans over the 15-step cap.
- **What committing does to V5, pre-specified before any v0.11 endpoint.** V5
  credits a plan that attempts the goal for the *true* casualty state. A v0.10
  blind plan that hedged over the casualty type could earn that credit from one
  of its branches. A v0.11 plan names one state, and on test 1 that state was
  wrong in 30 % of cells. Those plans fail V5 in every arm alike. That lowers
  APPROPRIATE-RESPONSE levels, so blind SURPLUS and INFEASIBLE can both sit near
  a floor, which makes equivalence easier to show for a reason unrelated to
  resource reasoning. It also widens stated − blind. So, if v0.11 is run, its
  reports add the following beside the pre-registered primary (which is
  unchanged):
  (a) the AR level in each arm, next to every difference;
  (b) declared-state accuracy by arm and condition, and how often the four arms
  of one image declare the same state;
  (c) a sensitivity analysis: the blind primary restricted to images whose
  declared state is correct in all four arms;
  (d) the stated condition, which discloses the state, is the vision-free
  comparison.
  If (c) and the primary disagree on ESTABLISHED / NOT ESTABLISHED, the report
  says so and leads with neither.
- **Where test 1's state errors fall.** All 18 wrong cells are the 9 sunken
  images, wrong in both arms (13 cells read as capsized, 5 as aground). Every
  aground, capsized and on-fire image was right. `prompt_procedural_v3.txt` adds
  a checklist of features to look for, image-based reasons for ruling out each
  other technique, and "Do not guess". On the same 30 images it does no better:
  21 / 30, sunken 1 / 9. Over all 110 it gets 70 / 110 (sunken 7 / 33). So this
  is the planner's vision, not the prompt. No observation wording is added: tuning
  it toward the sunken label on the study's own images is what §6.4 rules out. The
  image goes to the model in both conditions (`rcp/infer.py`), and "stated" adds
  only the disclosure line.

*Revision 2 is run as the full study, and the test is read from it (decided for
time, before any revision 2 output exists).* The 8 v0.11 jobs (4 arms × 2
conditions, `results/v011/gen_<ARM>_<cond>.jsonl`) are submitted together.
Decoding is greedy and the prompt is the same, so the 60 test cells inside the
full run are the cells a separate test job would have written. The acceptance
rule is unchanged:
1. Freeze the generation.
2. Run `tools/guard_check.py --new results/v011/gen_SURPLUS_blind.jsonl
   results/v011/gen_SCARCE_blind.jsonl` restricted to `cal/v011_guard/ids.txt`
   (its `--ids-file`), against the same v0.10 cells.
3. Record the result here.

Nothing is extracted or validated until step 3 is done. If the criteria fail,
the run is kept as a registered failed attempt and is never analysed. v0.10
stands, with D11.

*Test 2 (revision 2, read from jobs 50538 and 50542, pleiades-0-23, commit
`8ccb922`, 60 / 60 cells): FAIL.* Header 100 % (state correct 70 %, reported
only); plans with a branch 86.7 % (v0.10 73.3 %, test 1 76.7 %); branches per
plan 4.87 (5.53; test 1 2.68); looped 13.3 % (31.7 %); truncated 5.0 % (35.0 %).
Report-only: hedge with no "if" 25.0 % (33.3 %); asks/escalate 78.3 % (45.0 %),
so no drop; over 15 steps 0 % (35.0 %). The step cap held and cut loops and
truncation sharply, but the branches are still there. They are contingencies,
not casualty-type hedges. The most common wordings in the 292 branch steps are
"if needed" (41), "if refloat fails" or "still fails" (26) and "if the vessel
is still not refloated" (16). Often a backup asset is attached ("Deploy TUG-017
and TUG-045 as backup tugs to assist if primary tugs lose traction").
Step 1 was done out of order. The test read the two files as soon as their
jobs completed (110 rows each, no errors in the logs), while 50539
(`SURPLUS`/stated) and 50545 (`INFEASIBLE`/stated) were still running. The
files' sha256 at the time of the read was `13635a1c…` (`gen_SURPLUS_blind.jsonl`)
and `5fa8ffe2…` (`gen_SCARCE_blind.jsonl`). The full run is frozen as
`v011_gen` when the last job ends, and its record must show these hashes.
Done: all 8 jobs completed (110 rows each, no errors) and `runs/v011_gen.json`
(16 files) records both hashes unchanged.
**Decision, as fixed above:** the v0.11 run is a registered failed attempt and
is not extracted or analysed. Prompt work stops. v0.10 is the study, and
contingency branches are handled in extraction (D11): an asset named only in a
conditional, backup or "if needed" step is not committed.

## D11. Extractor: a role per asset, adopted only on held-out labels (§6.3, §6.4) — not adopted; v010 measured on held-out

*Found.* In 9 of 20 hand-read `SURPLUS` V2a failures, the failure came from an
asset named only in a backup step (D10). The v010 question lists exclusions and
defaults to "assigned" when unsure. Extraction error has never been measured
against hand labels (D2).

*Candidate* `d11` (`rcp.extract --extractor d11`; `prompts/extract_system_d11.txt`,
sha256 `d875565b…`). Section 1 asks for one role per listed asset (`committed`,
`held_back`, `not_used`), with no default. `commitments` are the `committed`
assets. Sections 2–4 and the user prompt are byte-identical to v010's. An asset
given no role stays committed and is counted in `roles_missing`. v010 remains
the default. Its 440 frozen v0.10 blind extractions replay byte-identical
through the new code.

*Labels* (`cal/d11/`, drawn 2026-10-12, before any d11 output exists). 160 v0.10
blind plans, split by image:
- dev: 64 plans, 35 images;
- held-out: 96 plans, 53 images;
- 4 dev and 6 held-out plans per arm × state.

Labelling:
- The rules are the study's definitions, in `cal/d11/LABELLING.md`.
- `assets_named` is pre-filled by the resolver. Nothing else is pre-filled.
- The dev labels are drafted by the same model that wrote the d11 prompt, so they
  may share its reading. The PI spot-checks them.
- ~~The held-out set is labelled by the PI~~ (amended below).
- The dev labels (`labels_dev.csv`, sha256 `726a1286…`) were drafted before any
  extractor output on the sample was read. Drafting turned up cases the rules
  did not settle. Conventions for them were added to `LABELLING.md` (sha256
  `981c1cce…`) before any held-out label was written.

*Procedure.*
1. d11 runs once over the whole sample.
2. While the prompt may change, only dev scores (both extractors) are read. Each
   revision gets a new output directory and is listed here with its prompt hash.
3. The prompt is frozen and its hash recorded here.
4. The held-out set is then scored once, against both extractors.

*Dev revisions* (dev scores only; `cal/d11/score_dev_*.json`):
- **r1** (`ex_d11/`, prompt `d875565b…`, job 51565, run `d11_cal_r1`). 44 of 160
  replies hit the token cap: GLM repeated `asset_roles` entries, and the open
  array allowed it. Those plans fell back to all committed, goal not attempted.
  Dev, v010 → r1: verdict flips 6 → 4 of 64, `commitments` F1 0.906 → 0.956.
- **r2** (`ex_d11_r2/`, prompt `6830361f…`). `asset_roles` becomes an object with
  one required key per listed asset, in order, built per plan (`schema_for`);
  the prompt's format line says so. No question wording changed. Job 51580, run
  `d11_cal_r2`: 0 parse failures. Dev, v010 → r2: verdict flips 6 → 11 of 64,
  `commitments` F1 0.906 → 0.917 (false negatives 6 → 80, mostly `not_used`),
  `escalate` agreement 0.984 → 0.844. On the 43 dev plans r1 parsed, r2 misses
  63 committed assets to r1's 8 and gets `escalate` wrong on 7 to r1's 3, though
  that question's text is unchanged: the closed object changed GLM's answers, not
  only their form. r2 is not frozen.
- **r3** (`ex_d11_r3/`, prompt `ca15ff28…`). Round 1's list of {asset, role},
  fixed to one entry per listed asset, in order (`prefixItems`, each asset a
  `const`); the format line says so. No question wording changed. If r3 does not
  have fewer dev flips than v010, no d11 prompt is frozen and v010 stays.
  Job 51619, run `d11_cal_r3`: 0 parse failures. Dev, v010 → r3: verdict flips
  6 → 14 of 64, `commitments` F1 0.906 → 0.906 (false negatives 6 → 81),
  `escalate` agreement 0.984 → 0.812. On the 307 gold-committed assets r1 placed,
  r3 calls 54 not committed to r1's 8. r3's misses grow along the list (none in
  its first quarter, 25 of 79 in its last). **Stop rule met: no d11 prompt is
  frozen, v010 stays.** Why a forced, complete list changes GLM's answers is not
  known.

*Amendment (2026-10-12, while the d11 job ran and before any of its output was
read).* The PI has no time to label, so neither the held-out set nor the dev
spot-check is hand-labelled. Two model labellers label held-out instead, each blind
to all extractor output and to the other's labels:
- **A** (`labels_heldout_a.csv`): the model that wrote the d11 prompt and the dev
  labels. It may share the d11 prompt's reading.
- **B** (`labels_heldout_b.csv`): a fresh instance of the same model, given only
  `LABELLING.md` and the held-out sheet. It has seen no prompt, dev label or
  extractor output.

A and B are the same model, so they are not independent in the way a human
labeller would be. The adoption rule below must hold against A and against B
separately. The extraction error is reported against each, with A–B agreement,
and is called agreement with model labels, not measured error.

Both written before any d11 output was read: A `7ac0be92…`, B `ccfe2e55…`. A–B
agreement: commitments identical on 95/96 plans, `goal_attempted` 96/96,
`escalate` 95/96, `reduce` 93/96.

`rcp.calibrate score` now keeps every flipped cell, for pairing, and refuses to
overwrite its output.

*Adoption rule, fixed now.* d11 is adopted only if, on held-out, all of these
hold (against both label sets, per the amendment):
- (a) it has fewer verdict flips than v010 (a tie means not adopted);
- (b) its `commitments` F1 is at least v010's;
- (c) its `goal_attempted` and `escalate` agreement are each no more than 2 pp
  below v010's.

The paired counts (cells flipped by v010 only, and by d11 only) are reported in
either case. With 96 plans this is a decision rule, not a significance test.

*What follows.* Either way, the held-out verdict-flip rate of the extractor used
is reported as the measured extraction error. It replaces "unvalidated".
- **If d11 is adopted**, all 880 v0.10 plans are re-extracted to
  `results/v010_d11/` and reported beside the frozen v0.10 reports, which stay.
- **If not**, v010 stays.

*Held-out result (2026-10-12).* No d11 prompt was frozen (r3 above), so only v010
was scored, once, against each label set (`cal/d11/score_heldout_{a,b}_v010.json`).
d11 was never run against held-out.

| v010 on held-out (96 plans) | vs A | vs B |
|---|---|---|
| verdict flips | 8 (8.3%) | 9 (9.4%) |
| `commitments` F1 (fp / fn) | 0.922 (99 / 12) | 0.922 (98 / 12) |
| `goal_attempted` agreement | 0.938 | 0.938 |
| `escalate` agreement (false positives) | 0.948 (5) | 0.938 (5) |
| `reduce` agreement | 0.667 | 0.677 |

The flips are not random in direction (`tools/flip_direction.py`). Against A,
all 8 flatten the AR decline.
On SURPLUS and SUFFICIENT the extractor fails a plan the labels pass (4): a
backup asset counted as committed fails V2a. On SCARCE and INFEASIBLE it passes a
plan the labels fail (4): an escalation the labels do not see. Against B, 8 of 9
do; the ninth is a SCARCE plan the extractor fails. All 6 dev flips go the same
way. AR on held-out by the labels (A), against v010: SURPLUS 10/24 vs 7/24,
INFEASIBLE 1/24 vs 3/24. So v010's error, if anything, makes AR look flatter than
the labels do, and the primary's "not established" does not depend on it. This is
descriptive: 24 plans per arm, against model labels.

## D12. v0.12: contingencies in their own section, not banned (§6.2) — FAILED its test

*Why there is a third revision although D10 said prompt work stops after revision
2 (decided 2026-10-10, at the PI's request, before any v0.12 generation).* This
reopens D10's stop rule, and that is recorded here as a deviation from it.
Revisions 1 and 2 showed two things. The planner follows a section format exactly:
the header held in 60 / 60 plans both times. And it will not drop contingencies,
whatever the wording (test 2: 86.7 % of plans branch, mostly "if needed" and "if
refloat fails"). Contingency planning is also ordinary salvage practice, so the
prompt stops fighting it. Contingencies get their own section after the plan, and
only the plan is scored. Then a backup asset is set aside by the format, which a
parser reads exactly, instead of by an LLM judgment (D11).

*Changed:*
- `prompts/planner_task.txt`: the guard line ends "…or alternatives in the
  Salvage Plan". A new last line follows the affordance line: "After the last
  step, write "Contingencies:" and list, one per line, at most 5 things you would
  do if a step does not work or conditions change, naming any backup or reserve
  assets there and not in the Salvage Plan." It names no shortfall and no remedy
  for one, and it comes after the affordance so the affordance is not read as
  part of a condition (`tests/test_render.py`). Domain digest (blind)
  `d82e636c…`.
- `extract_det.split_contingencies` cuts the plan at a "Contingencies:" label
  that opens a line. `rcp.extract` scores only the text before it, and records
  the section (`contingencies`) and the ledger IDs named only there
  (`contingency_only_assets`) per row, never scored. On the 1,820 existing plans
  (v0.10, v0.11, test 1) the label never occurs, so their extraction is
  unchanged.
- `tools/guard_check.py` measures branches on the plan section only and reports
  the share of plans with the section ("contingencies").
- An "if" step left inside the Salvage Plan still counts as a branch. ESCALATE is
  read from the plan section, so a request written only under "Contingencies:" is
  a contingency, as D2's rule already says ("if the refloat fails, request more
  tugs" → false).

*Test, fixed before any v0.12 generation.* The test uses 30 fresh images:
`cal/v012_guard/ids.txt`, drawn from the 80 not in `cal/v011_guard/ids.txt`,
stratified 11 / 9 / 5 / 5, seed 20261010. The earlier 30 images have now been
looked at twice. As before, the cells are {`SURPLUS`, `SCARCE`} × blind, greedy,
2048 tokens, float16, one job, written to `results/v012_guard/gen_blind.jsonl`.
`guard_check.py --ids-file cal/v012_guard/ids.txt` is run twice: once against the
same cells under v0.10 (`results/gen_*_blind.jsonl`), and once against v0.11
(`results/v011/gen_*_blind.jsonl`, registered failed run, read for prose only).
The criteria are D10's, unchanged and measured on the plan section: header
≥ 95 %; plans with a branch ≤ 30 %; branches per plan ≤ 1.0; loops and truncation
no worse than v0.10 on these cells. Reported only: state correct; contingency
section present; asks/escalate in the plan section (a fall well below v0.10 is a
reason to look before adopting, as in D10); hedge with no "if"; over 15 steps.

*Pre-flight review, before any v0.12 generation (2026-10-12).* The criteria are
unchanged. Three fixes and one addition:
- **Parser: a numbered contingency step no longer cuts the plan.**
  `split_contingencies` took "2. Contingency: keep TUG-045 ready" for the section
  label, so steps 3 onward were dropped from scoring and from the branch count,
  which favours the guard test. A numbered label now counts only when it stands
  alone on its line ("16. Contingencies:").
- **Parser: more label forms.** It now takes one qualifier word, a parenthesis or
  a dash ("Contingency measures:", "Contingencies (if a step fails):",
  "Contingencies -"). "Backup plan:" and "Fallback:" are still not the label, and
  count as not following the format. On the 1,820 earlier plans (v0.10, v0.11,
  test 1) the label still never occurs, so their extraction is unchanged.
- **`guard_check.py`: "asks, cont. only"** (reported, not a criterion): the
  share of plans that ask for resources under "Contingencies:" but not in the
  plan. ESCALATE is read from the plan only, so this is the share whose ask the
  new section moved out of P1′.
- **`report.py`: D10's V5 additions (b) and (c)**, now implemented. For a run
  with the header it prints section 3b: declared-state accuracy per arm, the
  share of images declaring one state in all four arms, and the primary
  restricted to images declared correctly in all four arms, with each arm's AR
  on that subset (a). If that and the primary differ on ESTABLISHED, both the
  primary and 3b say so. (d) is `rcp.compare`, unchanged. All four v0.10 reports
  (`rep_*`, `sens_noloop_*`) regenerate byte-identical.

*What follows.*
- **If it passes**, the 8 v0.12 jobs run in full to `results/v012/`, extraction
  uses the extractor D11 settles on, and the analysis plan is unchanged, with D10's
  four V5 additions (a)–(d). v0.12 becomes the main run, and v0.10 the pilot.
  v0.10, re-scored under D11, is still reported beside it.
- **If it fails**, there is no further revision. The test output is registered as
  a failed attempt, and v0.10 with D11 is the study.

*Result (2026-10-12, job 51566, run `v012_guard`): FAILED.* All 60 plans wrote
the header and a "Contingencies:" section, but the plan section still branched:

| criterion | v0.12 | v0.10 | v0.11 | limit |
|---|---|---|---|---|
| header | 100 % | 0 % | 100 % | ≥ 95 % |
| plans with a branch | 83.3 % | 85.0 % | 76.7 % | ≤ 30 % |
| branches per plan | 4.28 | 3.97 | 3.35 | ≤ 1.0 |
| looped | 13.3 % | 20.0 % | 10.0 % | no worse than v0.10 |
| truncated | 0 % | 20.0 % | 13.3 % | no worse than v0.10 |

Reported only: asks/escalate in the plan 58.3 % (v0.10 55.0 %); asks only under
"Contingencies:" 15.0 %. The planner writes its failure branches ("if the
refloat stalls, …") in the plan and lists contingencies again below it; every
section label parsed. As fixed above, there is no further revision: v0.12 is
not run in full, and v0.10, re-scored under D11, is the study. (D11 was not
adopted, so v0.10 stands as scored, with v010's held-out error reported.)

*Exploratory: where the branches come from (2026-10-12, after the result; post
hoc, descriptive).* `tools/branch_diag.py` classifies each conditional step by its
trigger, by the first matching pattern, so the categories are rough.
- v0.10, all 3,217 conditional steps: "if needed" top-ups 24 %, casualty state
  20 %, findings (hazmat, trapped water) 17 %, failure 7 %, **time 5 %**, other
  25 % (mostly escalation ladders and operating feedback). State branches mostly
  vanish when the state is stated.
- v0.10 blind: a capability asset named only in branches is 8.0 % of on-time
  ones and 28.6 % of late ones. Holding a late asset back is consistent with the
  deadline; holding back an on-time one is the hedge that matters for AR.
- On the 30 v0.12 guard images (SURPLUS+SCARCE blind): v0.11's header removed
  state branches (1.03 → 0.00 per plan), and failure branches rose (0.13 → 0.60;
  v0.12 1.18). Plans holding back an on-time capability asset: v0.10 20.0 %,
  v0.11 33.3 %, v0.12 63.3 %. v0.12's request to name "backup or reserve
  assets" there went with more hedging, not less.

Reading: the planner's branching is not driven by time, so relaxing deadlines
would not address it, and the prompt revisions moved it rather than removed it.
Any later planner work should target on-time assets held back, which needs a
per-asset role measure (D11's question) calibrated on that study's own plans.

## D13. v0.13 knowing-doing probe (`plan_v013.md`) — GAP

Pre-registered at `v0.13-prereg`; labels `cal/v013/labels_{a,b}.csv` committed
before the run; SLURM 51908, run `v013_probe`; `tools/probe_gap.py report` ->
`results/v013_probe/report.txt`.

- Reproduction 12/12 byte-identical. All 880 probe answers parsed.
- Says "short" on every SCARCE and INFEASIBLE cell, both wordings (220/220).
- Knows contrast +0.570 [+0.522, +0.619]; acts (labels A and B) +0.041
  [+0.010, +0.072] and [+0.012, +0.070].
- **Primary:** G = +0.530 [+0.473, +0.586] (A), [+0.474, +0.585] (B) -> **GAP**,
  both label sets. On unsatisfiable cells the plan escalates in 10 (A) / 9 (B)
  of 220 although the probe said "short" on all 220.
- The `can` wording answers NO on 68 % (SURPLUS) and 76 % (SUFFICIENT) of
  satisfiable cells; 128 of 220 satisfiable cells answer NO to both wordings.
  In a seeded read of 5 (§7), the `can` answer adds up a subset of assets and
  finds too little; the `short` answer quotes the totals line. Post hoc, per
  wording: G = +0.241 [+0.164, +0.318] (`can`), +0.818 [+0.759, +0.877]
  (`short`), labels A. The contrast removes a constant bias, so the `can`
  wording's NO lean lowers K and does not make the gap.
- **ESCALATE check:** of the 36 extractor-positive blind cells, A confirms 10 and
  B 8; of 36 sampled negatives, each finds 1. So most extractor ESCALATE flags
  are not escalations. With labels, the plan escalates on 0.0 / 0.9 / 2.7 /
  6.4 % (A) and 0.0 / 0.0 / 2.7 / 5.5 % (B) of SURPLUS / SUFFICIENT / SCARCE /
  INFEASIBLE, against the extractor's 5.5 / 5.5 / 9.1 / 12.7 %
  (`results/rep_blind/report.txt` §5). v0.10's ESCALATE rates, P6 and AR on the
  unsatisfiable arms (which is ESCALATE there) are overstated; v0.10's
  pre-registered numbers are not recomputed. Missed escalations among the 404
  unsampled negatives are not corrected (plan_v013.md §9).
- Post hoc numbers above: `tools/probe_gap.py posthoc` ->
  `results/v013_probe/posthoc.txt`. `probe_gap.py check` rebuilds `report.txt`
  byte for byte.

Reading: the planner sees the shortfall when asked and does not act on it in the
plan. Next lever is task structure (plan_v013.md §8), which is Track E.

## D14. Closing the v0.10 record (2026-10-19; post hoc, no GPU)

`tools/d14.py report` -> `results/d14/report.txt`, from frozen outputs only;
`d14.py check` rebuilds every D14 output byte for byte. Nothing here is a test.
It replaces the review's [new] numbers (`docs/review_2026-10-19.md`), whose
ledger-size split was tie-biased.

- **P4′ reading.** §9.2 supports P4′ only if the 90 % CI lies inside ±δ; §9.1's
  "refuted" and the report's NOT ESTABLISHED name the same outcome. A decline
  larger than δ is not shown either: no CI below is wholly under −δ.
- **Checked ESCALATE** (`cal/v013` labels on their 72 cells; other cells keep the
  extractor's flag). AR on SCARCE / INFEASIBLE 2.7 / 6.4 % (A), 2.7 / 5.5 % (B),
  against 9.1 / 12.7 %. P4′ D = −0.254 [−0.329, −0.178] (A), −0.262 [−0.336,
  −0.188] (B): not established. P1′ +0.041 [+0.010, +0.072] (A), [+0.012,
  +0.070] (B). P6 (ESCALATE on satisfiable ledgers) 0.0 / 0.9 % (A), 0 / 0 (B).
  Of 36 sampled negatives 1 escalates (95 % ≤ 14.5 %); if the 178 unchecked
  unsatisfiable negatives escalated at that rate D would rise by 0.027, at
  14.5 % by 0.139.
- **P2 MDE** (§9.4 "to be entered"; §12.2 gate 1 never closed). n = 110, exact
  one-sided .05, power .80: 0.015 against π = 0. The extractor flags OVERCOMMIT
  on 5 of 16 held-out satisfiable plans the D11 labels clear (95 % ≤ 58.7 %;
  misses 1 of 32); against that bound the MDE is 0.705, not §9.4's guessed
  0.07–0.11. Observed 76.4 % [67.3, 83.9] lies above 58.7 %, so OVERCOMMIT at
  SUFFICIENT is not all extractor error.
- **Asset count** (§7.2, §9.2; pre-specified, never run). Mean ledger 18.6 /
  13.0 / 7.9 / 6.0 assets by arm. RESOURCE-VALID falls with size within an arm
  (SURPLUS 41.4 % at ≤ 18 assets, 15.4 % above; SUFFICIENT 24.6 % at ≤ 12, 13.2 %
  above), and SURPLUS beats SUFFICIENT at equal size (12–14: 50.0 vs 12.5 %;
  15–17: 37.5 vs 7.7 %; 18–20: 26.5 vs 10.0 %). Size runs against the arm trend,
  so it does not explain the decline.
- **Other pre-specified rows** (§5.1, §9.2): OVERCOMMIT ∧ ¬REDUCE 40–45 % in every
  arm, ∧ REDUCE 22 / 36 / 46 / 45 %, but REDUCE agrees with held-out labels on
  only 64/96 (A) and 65/96 (B). Co-occurrence and casualty state are in the
  report; capsized has the lowest AR in three arms (0–5.3 %); in SUFFICIENT
  on_fire is lower (6.2 vs 10.5 %).
- **Post hoc.** Looped or truncated plans: AR 11 % vs 38 % in SURPLUS, 31 % vs
  5 % in SCARCE (n = 16). The D10 "asks for more" regex matches 52–61 % of plans
  in every arm and both conditions; it does not separate the arms and is not
  validated.
- **v0.13 by wording** (from D13's posthoc): G = +0.241 [+0.164, +0.318] for
  `can`, whose CI crosses the 0.2 margin, and +0.818 [+0.759, +0.877] for
  `short`. Only the pooled G was registered; it now carries both in its headline.
- **Track E split** (§12.4 item 2; Track M's rates are frozen in
  `runs/v010.json`). `d14.py split` -> `cal/track_e/split.csv`: 40 dev / 70 test
  images, stratified on state (dev 15 aground, 7 capsized, 6 on_fire, 12
  sunken), seed 20261019. Tune on dev only; report on test against Track M
  recomputed on test.
- **Human work, open.**
  - §10.3 read: `d14.py read` -> `cal/d14/sheet.md`. It holds 40 blind v0.10 plans
    on test images (10 per arm, shuffled; arm and verdicts withheld). Test images
    keep the read away from the material Track E tunes on. Fill `cal/d14/read.csv`.
    About a week later, `d14.py rerate` draws 15 for a blind re-read. `d14.py
    human` writes `results/d14/human.txt`; its summary was fixed in code before
    the read. The read is never used for tuning.
  - Hand ESCALATE labels on the 72 `cal/v013` cells: `cal/v013/labels_human.csv`,
    rule D2 in `cal/d11/LABELLING.md`. Do not open `labels_{a,b}.csv` or
    extractor output first.
- **Pre-registered, not done.** V2b, V4a, V4b and V6 (§4) are not in the
  validator; each needs a reading the extractor does not make. DEGRADE needs an
  open-vocabulary LLM read and was never built. P5's ablation was never run.
  Replicates and sampling: one greedy draw per cell (open items).

## D15. v0.13b: told verdict, no totals, more wordings (`plan_v013b.md`) — ACTS WHEN TOLD

Pre-registered at `v0.13b-prereg`; SLURM 52970 (plans, probes) and 52971
(extraction), run `v013b`, tag `run/v013b`; labels `cal/v013b/labels_{a,b}.csv`
committed before the report; `tools/v013b.py report` ->
`results/v013b/report.txt` (`check` rebuilds it byte for byte). Dev split only,
40 images × 4 arms.

- Reproduction 36/36 byte-identical; every file passes §5.
- **Primary:** E_told = +0.713 [+0.597, +0.828] (A), +0.675 [+0.556, +0.794]
  (B) -> **ACTS WHEN TOLD**, both label sets. v0.10 blind on the same images:
  +0.025 (A), +0.037 (B). Told plans escalate on 0 / 0 / 62.5 / 80.0 % (A) of
  SURPLUS / SUFFICIENT / SCARCE / INFEASIBLE. A and B agree on 157/160; the 3
  differ where a shortfall is stated only inside a failure branch (A yes, B no).
- **Says it; the plan changes little.** 58 % (A) / 59 % (B) of escalating
  unsatisfiable told plans still commit an asset arriving after the deadline.
  V2a passes go from 32.5 to 42.5 % (SCARCE) and 20.0 to 32.5 % (INFEASIBLE). On
  SUFFICIENT, V3 passes fall from 82.5 to 65.0 %. Descriptive, no test.
- **No totals: COLLAPSES.** Pooled ΔK = −0.438 [−0.536, −0.339]. Without the
  totals line, `can` answers NO on 97.5 % of satisfiable cells (K +0.025);
  `short` K = +0.375.
- **Verdict source: SELF-VERDICT in `probe_feasible`.** K = +0.987 [+0.961,
  +1.013], "short" on 1.3 % of satisfiable cells, 158/160 parsed (the 2 put
  FEASIBLE on the sentence's line). `enough` K = +0.762; `request` K = +0.138
  (YES on 86 % of satisfiable cells).

Reading (plan_v013b.md §8): the planner acts on a verdict it is given, and
reaches a reliable one when it states the numbers first, but only by reading the
printed totals line. v0.14: the `feasible` verdict first, totals printed, then
the plan; report V2a beside ESCALATE, since stating the verdict did not stop late
assets being committed.

## Provenance: run registry and no-overwrite guards (2026-10-09)

`results/` is gitignored, so until now the 880 v0.10 plans and every report
existed on one disk with nothing in git describing them, and extraction and
reports overwrote an existing output silently. Now: `runs/<name>.json` (tracked)
records each finished run's files with sha256, size and line count, the jobs that
wrote them, and the repo commit at freeze; `tools/runs.py freeze` makes the files
read-only and copies them to `/data/$USER/rcp_archive/<name>/`, a separate volume;
`tools/runs.py verify` rechecks both copies. `rcp.infer` refuses an existing
`--out` without `--resume`, `rcp.extract` an existing `extracted.jsonl` and
`rcp.report` an existing `report.txt`, unless `--overwrite`. Registered so far,
each with a tag `run/<name>` on the commit that froze it: `v010` (56 files, jobs
50412–50435, smoke and rerun included), `v011_guard_r1` (job 50449),
`dtype_check_bf16` (job 50450, outputs copied from the `dtype-check` worktree),
`v011_gen` (jobs 50538–50545, the failed revision 2 run, D10), `v012_guard` (job
51566) and `d11_cal_r1`–`r3` (jobs 51565, 51580, 51619). Rules and layout:
`runs/README.md`.

*Where the numbers come from.* Each number in D8–D14 is printed by a script in
the repo, run in the container from the repo root:
- `rcp.report` (`results/rep_*/report.txt`): per-arm loops, branches and
  truncation, D9's sensitivity;
- `tools/guard_check.py`: the D10 and D12 test tables;
- `tools/branch_diag.py`: D12's exploratory note;
- `rcp.calibrate`: D11's scores, and `tools/flip_direction.py` their direction;
- `tools/audit.py`: D10's hand reads (output only; the readings are above);
- `tools/cited.py`: everything else, each line labelled with its entry.
- `tools/probe_gap.py`: D13; `tools/d14.py`: D14.
`tools/cases.py` draws the tex's case studies (seeded, rules fixed before reading).
`tools/check_v010.py` replays the frozen v0.10 extraction byte for byte. Not
re-derivable: D0–D5 (measured with the code of the time), job ids and crash
details (SLURM logs), and D10's "the same result as before for all 940" (a
comparison with parser code since replaced).

## Open items (2026-10-14; order set 2026-10-19)

**Next, in order** (why: `docs/review_2026-10-19.md` §4):
1. **D14: close the record (no GPU).** Computed and entered (D14). Still open:
   the §10.3 blind human read and its re-rate, and hand labels on the 72
   `cal/v013` cells.
2. **v0.13b: done (D15).** Acts when told; the `feasible` wording's own
   verdict is reliable, but only with the totals line printed.
3. **v0.14 (Track E, test split).** Assess, then plan: the `feasible` verdict
   first (totals printed), then the plan (D15).
4. Then a second model and replicates.

Not done. Each would be a new version or a new study, never a change to v0.10.
- **Dtype** (D10): bfloat16 looped less than float16 (roughly 23 % against 33 %,
  n = 30). Settle it before a later version.
- **P5** (plan.md §9.1): the mechanism-block ablation was never run.
- **Hand labels** (D2, D11): extraction error is measured against model labels
  only.
- **d11** (D11): never run on held-out. Why a closed or complete output schema
  changed GLM's answers, not only their form, is not known.
- **Replicates**: one model, greedy decoding, one plan per cell. Nothing measures
  how much the results depend on the decoding.
- **Held-back assets** (D12): later planner work needs a per-asset role measure,
  calibrated on that study's own plans.

`plan.md` is the pre-registration and is not edited after the run; its §6.1
assertion audit is `prompts/assertions_audit.csv`.
