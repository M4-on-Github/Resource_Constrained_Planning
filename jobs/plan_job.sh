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
#   sbatch jobs/plan_job.sh OUT_JSONL [EXTRA_ARGS_FOR_rcp.infer...]
#
# The image root is resolved, not passed — see the probe below. Override it with
# RCP_IMAGES=/path/to/sorted_images if you ever need to.
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

OUT="${1:?Usage: sbatch jobs/plan_job.sh OUT_JSONL [EXTRA_ARGS...]}"
shift 1 || true
# Everything after OUT_JSONL goes to rcp.infer verbatim: --arm SUFFICIENT,
# --condition stated, --limit N. Kept as pass-through rather than named flags
# so this script never has to track rcp.infer's CLI.
# Left in "$@" rather than copied to an array: "${arr[@]}" on an empty array
# errors under `set -u` on bash < 4.4, which the cluster may still have.

REPO="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"

# ── Resolve the image set ─────────────────────────────────────────────────────
# The images are not an argument because they are not a choice: there is one
# corpus, data/manifest.csv pins all 110 of its members by relative path, and a
# run against a different directory is not this experiment. Passing the path on
# every submit only created a way to get it wrong.
#
# Candidates are **probed, never guessed** — the rule from
# QWEN-Maritime/CASTOR/benchybench_paths.sh. If none holds the image set the job
# stops and prints what it tried, because a silent fallback to the wrong corpus
# is far worse than a failed submission.
#
# manifest.csv stores `aground/00017.jpg`, so the root is the directory that
# *directly* holds the four state directories. RCP sits at
# <BenchyBench>/Resource_Constrained_Planning, which makes $REPO/.. the normal hit.
IMAGES_SUBPATH="shipwreck_wiki_images/sorted_images"

have_images() {
    # Two of the four, not one: a stray empty `aground/` somewhere would
    # otherwise be enough to accept a wrong root.
    [ -n "${1:-}" ] && [ -d "$1/aground" ] && [ -d "$1/sunken" ]
}

IMAGES=""
TRIED=""
for cand in "${RCP_IMAGES:-}" \
            "${BENCHYBENCH_ROOT:+$BENCHYBENCH_ROOT/$IMAGES_SUBPATH}" \
            "$REPO/../$IMAGES_SUBPATH" \
            "$REPO/$IMAGES_SUBPATH" \
            "/data/$USER/BenchyBench/$IMAGES_SUBPATH"; do
    [ -n "$cand" ] || continue
    TRIED="$TRIED
       $cand"
    if have_images "$cand"; then IMAGES="$(cd "$cand" && pwd)"; break; fi
done

if [ -z "$IMAGES" ]; then
    echo "ERROR: cannot locate '$IMAGES_SUBPATH'." >&2
    echo "       Tried, in order:$TRIED" >&2
    echo "       Set RCP_IMAGES=/path/to/sorted_images to override, e.g." >&2
    echo "         RCP_IMAGES=/data/\$USER/images sbatch jobs/plan_job.sh $OUT" >&2
    exit 1
fi
# Every user-writable path lives under /data/$USER; /data/shared is read-only.
DATA_DIR="/data/$USER"
MODEL_DIR="$DATA_DIR/qwen3vl-8b"
# castor_qwen.sif, not castor_judge.sif. The judge SIF is vLLM 0.8.5, whose
# model registry has no qwen3_vl. castor_qwen.sif is QWEN-Maritime's container,
# already validated against these weights on this cluster -- it runs Qwen3-VL
# through transformers, which is why rcp.infer uses model.generate and not vLLM.
# jobs/extract_job.sh stays on castor_judge.sif, unchanged from P9.
SIF="$DATA_DIR/castor_qwen.sif"

[ -d "$MODEL_DIR" ] || { echo "ERROR: planner weights not found: $MODEL_DIR" >&2; exit 1; }
[ -f "$SIF" ]       || { echo "ERROR: $SIF not found."                  >&2
                         echo "       This is QWEN-Maritime's container; build it from that repo." >&2
                         exit 1; }

mkdir -p "$(dirname "$OUT")" logs

# ── Container digest, for the run's environment record (rcp/envinfo.py) ──────
# Hashed on the host because the container cannot see its own image file.
# Cached beside the SIF and reused while the SIF is older than the cache, so a
# multi-GB image is hashed once per rebuild rather than once per job.
SIF_SHA_CACHE="$DATA_DIR/.cache/$(basename "$SIF").sha256"
mkdir -p "$(dirname "$SIF_SHA_CACHE")"
if [ ! -s "$SIF_SHA_CACHE" ] || [ "$SIF" -nt "$SIF_SHA_CACHE" ]; then
    sha256sum "$SIF" | cut -d' ' -f1 > "$SIF_SHA_CACHE"
fi
SIF_SHA="$(cat "$SIF_SHA_CACHE")"

# ── Code version, for the same record ─────────────────────────────────────────
# SLURM snapshots this script at submission but the Python is read when the job
# starts, so this is the commit the job actually runs.
GIT_COMMIT="$(git -C "$REPO" rev-parse HEAD 2>/dev/null || echo unknown)"
GIT_DIRTY="$(git -C "$REPO" status --porcelain 2>/dev/null | grep -q . && echo yes || echo no)"

echo "==========================================="
echo " RCP planning (plan.md sec. 7.1)"
echo " Planner   : $MODEL_DIR"
echo " Images    : $IMAGES"
echo " Output    : $OUT"
echo " Container : $SIF ($SIF_SHA)"
echo " Commit    : $GIT_COMMIT (dirty: $GIT_DIRTY)"
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
    --bind "$IMAGES:$IMAGES" \
    --env USER="$USER" \
    --env HOME="$HOME" \
    --env PYTHONUNBUFFERED=1 \
    --env PYTHONPATH="$REPO" \
    --env HF_HOME="$DATA_DIR/.cache/huggingface" \
    --env HF_HUB_DISABLE_PROGRESS_BARS=1 \
    --env RCP_CONTAINER="$SIF" \
    --env RCP_CONTAINER_SHA256="$SIF_SHA" \
    --env RCP_GIT_COMMIT="$GIT_COMMIT" \
    --env RCP_GIT_DIRTY="$GIT_DIRTY" \
    --env SLURM_JOB_ID="${SLURM_JOB_ID:-}" \
    --env CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}" \
    "$SIF" \
    python3 -m rcp.infer \
        --images    "$IMAGES" \
        --out       "$OUT" \
        --model-dir "$MODEL_DIR" \
        --resume \
        "$@"

EXIT_CODE=$?
echo "==========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo " RCP planning complete : $(date)"
else
    echo " RCP planning FAILED (exit $EXIT_CODE) : $(date)" >&2
fi
echo "==========================================="
exit $EXIT_CODE
