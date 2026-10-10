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
(`conditional_steps`) and the truncation rate at 2048. Its outputs are discarded.
Guard: 7 of 10 plans ran 400–770 tokens with a median of 1 conditional step
(exploratory: ~8). Truncation: 3 of 10 hit 2048, every one a loop — see D9.

## D9. Greedy loops cut at the first repeated step (found by D8)

*Found:* AGR-00017, -00041, -00045 reprint an earlier step verbatim (renumbered)
until the token cap — greedy decoding's self-reinforcing repeat. Not new: the same
rule finds 10 blind and 15 stated exploratory plans looping, all inside D3's 1024-cap
truncations, so a share of D3's "truncated" was loops, not long plans, and raising
the cap could not fix them. *Considered and rejected:* a no-repeat-n-gram ban at
decoding. Clean plans legitimately repeat token runs of 12–22 (exploratory up to
~60), while the loops repeat only ~30 because the step number changes, so no n
separates them and the ban would alter clean plans. *Changed:*
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

## D10. v0.11 commitment header in the planner prompt (§6.2) — proposed, under test

*Found, after the four-arm run (so this is a post-data change and the v0.10 run
becomes a pilot if it is adopted):* the single-course guard (D1) did not hold.
Blind plans with ≥ 1 conditional step: 78–90 % per arm (3.9–5.9 per plan); stated
67–81 %. Two sources. (i) Branching on the casualty type ("if the vessel is found
to be aground…"): 66 / 440 blind plans, 5 / 440 stated — the blind planner hedges
over what the photo shows instead of deciding. (ii) Contingency branches ("if the
pull is insufficient, add TUG-006"), in both conditions. The branches matter
because the extractor under-excludes their assets: a hand read of 20 random
`SURPLUS`/blind V2a failures found 9 where the late asset appears only in a
backup, "if it fails", other-casualty or explicitly "do not commit" step, against
D2's rule; the extractor excluded 4.6 % of named assets overall. (The extractor
fix is separate and needed regardless; it is not part of D10.)

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

*Dtype check (job 50450, branch `dtype-check` at `60b2fdd`; not merged).* v0.10
loads the planner in float16, copied from QWEN-Maritime's `run_inference.py`;
the checkpoint is bfloat16. 30 `SURPLUS` / blind cells under the v0.10 prompt
(same domain digest) were rerun in bfloat16 (`cal/dtype_check/ids.txt` on that
branch): 20 whose float16 plan looped, 10 clean. Looped 6 / 20 and 2 / 10 (float16:
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
- **Where test 1's state errors fall.** All 18 wrong cells are sunken images
  (9 images: 5 read as capsized, 4 as aground). Every aground, capsized and on-fire
  image was right. `prompt_procedural_v3.txt` adds a checklist of features to
  look for, image-based reasons for ruling out each other technique, and "Do not
  guess". On the same 30 images it does no better: 21 / 30, sunken 1 / 9. Over
  all 110 it gets 70 / 110 (sunken 7 / 33). So this is the planner's vision, not
  the prompt. No observation wording is added: tuning it toward the sunken label
  on the study's own images is what §6.4 rules out. The image goes to the model
  in both conditions (`rcp/infer.py`), and "stated" adds only the disclosure line.

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

## D12. v0.12: contingencies in their own section, not banned (§6.2) — proposed, under test

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

*What follows.*
- **If it passes**, the 8 v0.12 jobs run in full to `results/v012/`, extraction
  uses the extractor D11 settles on, and the analysis plan is unchanged, with D10's
  four V5 additions (a)–(d). v0.12 becomes the main run, and v0.10 the pilot.
  v0.10, re-scored under D11, is still reported beside it.
- **If it fails**, there is no further revision. The test output is registered as
  a failed attempt, and v0.10 with D11 is the study.

## Provenance: run registry and no-overwrite guards (2026-10-09)

`results/` is gitignored, so until now the 880 v0.10 plans and every report
existed on one disk with nothing in git describing them, and extraction and
reports overwrote an existing output silently. Now: `runs/<name>.json` (tracked)
records each finished run's files with sha256, size and line count, the jobs that
wrote them, and the repo commit at freeze; `tools/runs.py freeze` makes the files
read-only and copies them to `/data/$USER/rcp_archive/<name>/`, a separate volume;
`tools/runs.py verify` rechecks both copies. `rcp.infer` refuses an existing
`--out` without `--resume`, `rcp.extract` an existing `extracted.jsonl` and
`rcp.report` an existing `report.txt`, unless `--overwrite`. Registered so far:
`v010` (56 files, jobs 50412–50435), `v011_guard_r1` (job 50449) and
`dtype_check_bf16` (job 50450, outputs copied from the `dtype-check` worktree), and `v011_gen` (jobs 50538–50545, the failed revision 2 run, D10).
Rules and layout: `runs/README.md`.
