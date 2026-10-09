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
- the guard line now lists the words a step may not contain — "if", "unless",
  "in case", "in the event", "otherwise", "as needed", "as required" — and asks
  for each step as a plain statement of what is done. It names no shortfall and no
  remedy; "adequate / sufficient" are not banned (P9's ban would suppress
  `ESCALATE`), so a conditional request can become an unconditional one.
Same 60 cells, same criteria, same baseline; output
`results/v011_guard/gen_blind_r2.jsonl`; domain digest `1043f79d…`. Banning the
words the branch count looks for makes that count easier to pass by paraphrase,
so `tools/guard_check.py` gains a report-only column, "hedge, no if": plans with a
step that hedges ("as needed", "on standby", "backup", "where necessary", …)
without a word `conditional_steps` counts. On test 1 it is 33.3 % for both v0.10
and v0.11. It is read alongside the branch criteria, never as one. If revision 2
fails, prompt work stops here: v0.10 stands as the study and the branching is
handled in extraction (D11).
