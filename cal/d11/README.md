# D11 calibration set: dev and held-out labels

160 v0.10 **blind** plans for measuring extraction error and for choosing between
the study's extractor (`v010`) and D11's per-asset-role candidate (`d11`). The
rules are in `docs/deviations.md` D11. Drawn by `python tools/d11_sample.py --out
cal/d11` (seed 20261012), which refuses to overwrite.

**Split by image.** Within each casualty state, 40% of images form the dev pool
and 60% the held-out pool, and no image has plans on both sides. Each arm × state
stratum then draws 4 dev plans and 6 held-out plans:

| split | plans | images |
|---|---|---|
| dev | 64 | 35 |
| held-out | 96 | 53 |

**Labels.** The rules are in `LABELLING.md`.
- **Dev** (`labels_dev.csv`): drafted by a model from the rules and marked as
  such. The PI spot-checks them. Dev is where the d11 prompt may be revised.
- **Held-out** (`labels_heldout.csv`): labelled by the PI blind to every
  extractor's output, and scored once, after the d11 prompt is frozen.

| file | sha256 (as drawn) |
|---|---|
| `gen_sample.jsonl`: the 160 rows, byte-copied from `results/gen_*_blind.jsonl` | `710aca7d…` |
| `labels_dev_blank.csv` | `d9c52b16…` |
| `labels_heldout_blank.csv` | `1ed741cd…` |
| `dev_view.md`, `heldout_view.md`: the same plans, readable | `e118c3d4…`, `541fc195…` |

**Extraction.** `v010` is already frozen in `results/ex_blind_all.jsonl`. `d11`
runs once over the whole sample (one GPU job). Its output is registered with
`tools/runs.py freeze` and never overwritten. A dev revision gets a new directory.

```bash
sbatch --exclude=pleiades-0-17 jobs/extract_job.sh cal/d11/gen_sample.jsonl cal/d11/ex_d11 glm4_32b d11
python -m rcp.calibrate score --labels cal/d11/labels_heldout.csv --extracted results/ex_blind_all.jsonl --out cal/d11/score_heldout_v010.json
python -m rcp.calibrate score --labels cal/d11/labels_heldout.csv --extracted cal/d11/ex_d11/extracted.jsonl --out cal/d11/score_heldout_d11.json
```
