#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# RCP extraction — one SLURM job, one vLLM load, the whole run.
#
# Takes a JSONL of planner generations ({scenario_id, arm, prose}) and writes
# extracted.jsonl: one ExtractedPlan plus its trace per generation (plan.md
# §6.3). The validator is then a laptop job — it never sees prose.
#
# Deliberately NOT a SLURM array, unlike P9's stage 1. P9 arrayed over runs
# because each task was a separate plan folder; here the whole corpus is 440
# generations against one model, and loading a 32B GPTQ checkpoint costs more
# than scoring every prompt in it. One load, one batch, prefix caching on.
#
# Reuses P9's container and GLM-4-32B weights, so there is nothing to build and
# nothing to download — see plan_adequacy_calibrate_job.sh's header.
#
#   sbatch jobs/extract_job.sh generations.jsonl results/extract_v1
#
#SBATCH -p pleiades
#SBATCH --constraint=RTX6000ADA
#SBATCH --gpus=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=2:00:00
#SBATCH -J rcp_extract
#SBATCH --output=logs/rcp_extract_%j.out
#SBATCH --error=logs/rcp_extract_%j.err
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

INPUT="${1:?Usage: sbatch jobs/extract_job.sh INPUT_JSONL OUT_DIR [MODEL_KEY]}"
OUT_DIR="${2:?Usage: sbatch jobs/extract_job.sh INPUT_JSONL OUT_DIR [MODEL_KEY]}"
MODEL="${3:-glm4_32b}"

REPO="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
# Every user-writable path lives under /data/$USER; /data/shared is read-only.
DATA_DIR="/data/$USER"

# ── Resolve model directory — same keys as P9, same checkpoints ──────────────
case "$MODEL" in
    glm4_32b)       MODEL_DIR="$DATA_DIR/glm-4-32b-0414-gptq" ;;
    llama_3_3_70b)  MODEL_DIR="$DATA_DIR/llama-3.3-70b-instruct-w4a16" ;;
    phi4_14b)       MODEL_DIR="$DATA_DIR/phi-4-w4a16" ;;
    *) echo "ERROR: unknown model key '$MODEL' (expected glm4_32b, llama_3_3_70b, or phi4_14b)" >&2; exit 1 ;;
esac

SIF="$DATA_DIR/castor_judge.sif"
for required in "$MODEL_DIR" "$REPO/rcp" "$REPO/prompts"; do
    [ -d "$required" ] || { echo "ERROR: missing directory: $required" >&2; exit 1; }
done
[ -f "$SIF" ] || { echo "ERROR: $SIF not found — build it from Eval_CASTOR/containers/build_judge_container.sh" >&2; exit 1; }
[ -f "$INPUT" ] || { echo "ERROR: input generations not found: $INPUT" >&2; exit 1; }

mkdir -p "$OUT_DIR"

echo "==========================================="
echo " RCP extraction (plan.md sec. 6.3)"
echo " Model     : $MODEL"
echo " Model dir : $MODEL_DIR"
echo " Input     : $INPUT"
echo " Output    : $OUT_DIR/extracted.jsonl"
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
    --env USER="$USER" \
    --env HOME="$HOME" \
    --env PYTHONUNBUFFERED=1 \
    --env PYTHONPATH="$REPO" \
    --env HF_HOME="$DATA_DIR/.cache/huggingface" \
    --env HF_HUB_DISABLE_PROGRESS_BARS=1 \
    --env CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}" \
    "$SIF" \
    python3 -m rcp.extract \
        --model-dir "$MODEL_DIR" \
        --input     "$INPUT" \
        --out       "$OUT_DIR"

EXIT_CODE=$?
echo "==========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo " RCP extraction complete : $(date)"
else
    echo " RCP extraction FAILED (exit $EXIT_CODE) : $(date)" >&2
fi
echo "==========================================="
exit $EXIT_CODE
