#!/bin/bash
# -----------------------------------------------------------------------------
# RCP v0.13b dev-split diagnostic (plan_v013b.md). One job, one node: first the
# reproduction cells (plan_v013b.md's halt rule), then the probes, then the
# told-verdict plans. Each stage is jobs/plan_job.sh, so the container, image
# probe and environment records are the study's. Dev images only.
#
#   sbatch --exclude=pleiades-1-3 jobs/v013b_job.sh
#
#SBATCH -p pleiades
#SBATCH --constraint=RTX6000ADA
#SBATCH --gpus=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=6:00:00
#SBATCH -J rcp_v013b
#SBATCH --output=logs/rcp_v013b_%j.out
#SBATCH --error=logs/rcp_v013b_%j.err
# -----------------------------------------------------------------------------

set -euo pipefail
REPO="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
PLAN="$REPO/jobs/plan_job.sh"
OUT=results/v013b
DEV=cal/v013b/dev_ids.txt
REPRO=cal/v013b/repro_ids.txt

# 1. Reproduction: v0.10 plans and v0.13 probe answers, byte for byte
bash "$PLAN" "$OUT/repro_plan.jsonl" --ids-file "$REPRO"
for TASK in probe_can probe_short; do
    bash "$PLAN" "$OUT/repro_$TASK.jsonl" --ids-file "$REPRO" --task "$TASK" --max-tokens 64
done

# 2. Probes: v0.13's wordings without the totals line, then three new wordings
for TASK in probe_can probe_short; do
    bash "$PLAN" "$OUT/no_totals_$TASK.jsonl" --ids-file "$DEV" --condition no_totals \
        --task "$TASK" --max-tokens 64
done
for TASK in probe_enough probe_request; do
    bash "$PLAN" "$OUT/$TASK.jsonl" --ids-file "$DEV" --task "$TASK" --max-tokens 64
done
# States the totals before its verdict, so it gets room to finish
bash "$PLAN" "$OUT/probe_feasible.jsonl" --ids-file "$DEV" --task probe_feasible --max-tokens 256

# 3. Told-verdict plans (the primary); extraction is a separate job afterwards
bash "$PLAN" "$OUT/told_plan.jsonl" --ids-file "$DEV" --condition told
