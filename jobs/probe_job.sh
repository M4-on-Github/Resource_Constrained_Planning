#!/bin/bash
# -----------------------------------------------------------------------------
# RCP v0.13 knowing-doing probe (plan_v013.md). One job, one node: first the
# reproduction cells (v0.10's plan prompt; plan_v013.md's halt rule), then the
# probe in both wordings. Each stage is jobs/plan_job.sh, so the container,
# image probe and environment records are the study's.
#
#   sbatch --exclude=pleiades-1-3 jobs/probe_job.sh
#
#SBATCH -p pleiades
#SBATCH --constraint=RTX6000ADA
#SBATCH --gpus=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=4:00:00
#SBATCH -J rcp_probe
#SBATCH --output=logs/rcp_probe_%j.out
#SBATCH --error=logs/rcp_probe_%j.err
# -----------------------------------------------------------------------------

set -euo pipefail
REPO="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
OUT=results/v013_probe

bash "$REPO/jobs/plan_job.sh" "$OUT/repro_plan.jsonl" --ids-file cal/v013/repro_ids.txt
for TASK in probe_can probe_short; do
    bash "$REPO/jobs/plan_job.sh" "$OUT/$TASK.jsonl" --task "$TASK" --max-tokens 64
done
