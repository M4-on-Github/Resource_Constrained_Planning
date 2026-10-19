# Run registry

`results/` is gitignored: model output is large and lives on the cluster disk. This
directory is what git keeps instead. Each finished run has one `runs/<name>.json`
holding the sha256, size and line count of every file it produced, the jobs that
wrote them (node, GPU, commit, prompt digest, weights and container hashes, from
the environment records each stage writes), and the repo commit when it was frozen.
`docs/deviations.md` says *why* a run exists; this says *what it produced*.

## Rules

1. **A new run writes to a new path.** Never into a registered run's files. The
   stages enforce it: `rcp.infer` refuses an existing `--out` without `--resume`
   (and `--resume` refuses a file written under another prompt), `rcp.extract`
   refuses an existing `extracted.jsonl` and `rcp.report` an existing
   `report.txt`, unless `--overwrite` is passed.
2. **Freeze a stage as soon as it finishes**, before anything reads it:

       python3 tools/runs.py freeze <name> --purpose "<one line>" <files or dirs>

   This writes `runs/<name>.json`, appends a row below, makes the files read-only
   (a stage that points at them fails instead of writing), and copies them to a
   read-only archive at `/data/$USER/rcp_archive/<name>/` on a separate volume.
   Commit the JSON and this README in the same commit as the deviations entry
   that records the run.
3. **Check before using a run's numbers:** `python3 tools/runs.py verify` rechecks
   every registered file and its archive copy (missing, changed or writable fails).
4. A run that is wrong is superseded, never edited: register the replacement
   under a new name and say so in `docs/deviations.md`.

## Layout

| path | what |
|---|---|
| `results/gen_<ARM>_<cond>.jsonl`, `ex_gen_*`, `ex_*_all.jsonl`, `rep_*`, `cmp_*`, `sens_*` | v0.10, the study; flat, as run |
| `results/dtype_check/` | D10's float16 vs bfloat16 check |
| `results/v011_guard/` | D10's structural tests of the v0.11 prompt |
| `results/v011/gen_<ARM>_<cond>.jsonl` | v0.11 revision 2 plans (failed, not analysed) |
| `results/v012_guard/` | D12's guard test of the v0.12 prompt (failed) |
| `cal/d11/ex_d11*/` | D11's extractor rounds r1–r3 on the calibration sample |

Names: `<version>_<stage>` for study runs (`v011_gen`, `v011_extract`,
`v011_reports`), `<version>_<test>` for checks (`v011_guard_r2`).

## Code for a run

`main` runs the study, v0.10: its planner prompt regenerates v0.10's prompt
digests (`tests/test_render.py`), and replaying v0.10's stored extractor replies
through it reproduces `rep_blind` and `rep_stated` byte for byte
(`python3 tools/check_v010.py`, in the container). The code a later
run used is at its job's `git_commit`, also tagged `run/<name>`:

    git checkout run/v012_guard

v0.10 itself ran at `4e348e6` (tag `study-2026-10-09`) and `2a86040` (the resumes).

## Index

| run | frozen | files | purpose |
|---|---|---|---|
| `v010` | 2026-10-09 | 56 | v0.10 study run: 880 plans (4 arms x blind/stated, float16, greedy), GLM extraction, reports, comparisons, loop sensitivity, smoke and resume-verify files |
| `v011_guard_r1` | 2026-10-09 | 2 | D10 test 1: v0.11 commitment header, 30 images x SURPLUS/SCARCE blind, job 50449; FAILED the branch criteria |
| `dtype_check_bf16` | 2026-10-09 | 2 | D10 dtype check: v0.10 prompt in bfloat16, 30 SURPLUS/blind cells, job 50450, branch dtype-check 60b2fdd |
| `v011_gen` | 2026-10-09 | 16 | v0.11 revision 2 full run, FAILED D10 test 2 (branch criteria), never extracted or analysed: 880 plans (4 arms x blind/stated, float16, greedy), jobs 50538-50545, commit 8ccb922 |
| `d11_cal_r1` | 2026-10-12 | 2 | D11: d11 extractor (prompt d875565b) over the 160-plan calibration sample, job 51565; dev-revision round 1 |
| `v012_guard` | 2026-10-12 | 2 | D12 guard test: v0.12 contingencies section, fresh 30 images x SURPLUS/SCARCE blind, job 51566; FAILED the branch criteria |
| `d11_cal_r2` | 2026-10-12 | 2 | D11: d11 extractor r2 (prompt 6830361f, per-plan closed asset_roles object) over the 160-plan calibration sample, job 51580; dev-revision round 2 |
| `d11_cal_r3` | 2026-10-12 | 2 | D11: d11 extractor r3 (prompt ca15ff28, {asset, role} list fixed by prefixItems) over the 160-plan calibration sample, job 51619; dev-revision round 3 |
| `v013_probe` | 2026-10-14 | 6 | plan_v013.md probe (SLURM 51908) |
| `v013b` | 2026-10-19 | 20 | plan_v013b.md: repro cells, probes, told plans (SLURM 52970), told extraction (SLURM 52971) |
