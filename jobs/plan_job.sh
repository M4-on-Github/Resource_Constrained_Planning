#!/bin/bash
# -----------------------------------------------------------------------------
# RCP planning — Qwen3-VL-8B writes one salvage plan per (image, arm) cell.
#
# The only stage that sees an image, and the only one whose output the repo does
# not determine: everything after generations.jsonl is arithmetic on a frozen
# corpus. So this is the stage worth resuming, and --resume is on by default
# here — a requeued job picks up the cells it has not written yet.
#
# One job, one load, 440 cells. The prompt's constant halves are byte-identical
# across every cell (plan.md Rule 2), so prefix caching pays for itself and the
# image is the only per-row payload.
#
#   sbatch jobs/plan_job.sh IMAGES_ROOT OUT_JSONL
#
#SBATCH -p pleiades
#SBATCH --constraint=RTX6000ADA
#SBATCH --gpus=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=4:00:00
#SBATCH -J rcp_plan
#SBATCH --output=logs/rcp_plan_%j.out
#SBATCH --error=logs/rcp_plan_%j.err
# -----------------------------------------------------------------------------

set -euo pipefail

IMAGES="${1:?Usage: sbatch jobs/plan_job.sh IMAGES_ROOT OUT_JSONL}"
OUT="${2:?Usage: sbatch jobs/plan_job.sh IMAGES_ROOT OUT_JSONL}"

REPO="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
# Every user-writable path lives under /data/$USER; /data/shared is read-only.
DATA_DIR="/data/$USER"
MODEL_DIR="$DATA_DIR/qwen3-vl-8b-instruct"
SIF="$DATA_DIR/castor_judge.sif"

[ -d "$MODEL_DIR" ] || { echo "ERROR: planner weights not found: $MODEL_DIR" >&2; exit 1; }
[ -d "$IMAGES" ]    || { echo "ERROR: images root not found: $IMAGES" >&2; exit 1; }
[ -f "$SIF" ]       || { echo "ERROR: $SIF not found" >&2; exit 1; }

mkdir -p "$(dirname "$OUT")" logs

echo "==========================================="
echo " RCP planning (plan.md sec. 7.1)"
echo " Planner   : $MODEL_DIR"
echo " Images    : $IMAGES"
echo " Output    : $OUT"
echo " Job ID    : ${SLURM_JOB_ID:-none}"
echo " Node      : $(hostname)"
echo " Started   : $(date)"
echo "==========================================="

nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader || true

apptainer exec \
    --containall \
    --nv \
    --pwd "$REPO" \
    --bind /tmp:/tmp \
    --bind "$REPO:$REPO" \
    --bind "$DATA_DIR:$DATA_DIR" \
    --bind "$(cd "$IMAGES" && pwd):$(cd "$IMAGES" && pwd)" \
    --env USER="$USER" \
    --env HOME="$HOME" \
    --env PYTHONUNBUFFERED=1 \
    --env PYTHONPATH="$REPO" \
    --env HF_HOME="$DATA_DIR/.cache/huggingface" \
    --env HF_HUB_DISABLE_PROGRESS_BARS=1 \
    --env CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}" \
    "$SIF" \
    python3 -m rcp.infer \
        --images    "$IMAGES" \
        --out       "$OUT" \
        --model-dir "$MODEL_DIR" \
        --resume

EXIT_CODE=$?
echo "==========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo " RCP planning complete : $(date)"
else
    echo " RCP planning FAILED (exit $EXIT_CODE) : $(date)" >&2
fi
echo "==========================================="
exit $EXIT_CODE
