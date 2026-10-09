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
| `results/gen_<ARM>_<cond>.jsonl`, `ex_gen_*`, `rep_*`, `cmp_*`, `sens_*` | v0.10 (the pilot, if v0.11 is adopted); flat, as run |
| `results/v011_guard/` | D10's structural tests of the v0.11 prompt |
| `results/dtype_check/` | D10's float16 vs bfloat16 check |
| `results/v011/gen_<ARM>_<cond>.jsonl` | v0.11 plans, one file per arm × condition |
| `results/v011/ex_gen_<ARM>_<cond>/` | v0.11 extraction (`extract_job.sh`'s default beside its input) |
| `results/v011/rep_<cond>/`, `cmp_<ARM>/`, `sens_*` | v0.11 reports |

Names: `<version>_<stage>` for study runs (`v011_gen`, `v011_extract`,
`v011_reports`), `<version>_<test>` for checks (`v011_guard_r2`).

## Index

| run | frozen | files | purpose |
|---|---|---|---|
| `v010` | 2026-10-09 | 56 | v0.10 study run: 880 plans (4 arms x blind/stated, float16, greedy), GLM extraction, reports, comparisons, loop sensitivity, smoke and resume-verify files |
| `v011_guard_r1` | 2026-10-09 | 2 | D10 test 1: v0.11 commitment header, 30 images x SURPLUS/SCARCE blind, job 50449; FAILED the branch criteria |
| `dtype_check_bf16` | 2026-10-09 | 2 | D10 dtype check: v0.10 prompt in bfloat16, 30 SURPLUS/blind cells, job 50450, branch dtype-check 60b2fdd |
| `v011_gen` | 2026-10-09 | 16 | v0.11 revision 2 full run, FAILED D10 test 2 (branch criteria), never extracted or analysed: 880 plans (4 arms x blind/stated, float16, greedy), jobs 50538-50545, commit 8ccb922 |
