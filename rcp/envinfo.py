"""What a run ran on. One record per job, written beside its output.

A generation is reproducible only against the exact weights, container and
library versions that produced it, and none of those are in the repo. So each
planning or extraction job records them once, and every row it writes carries
the job's `run_id` so a row can be traced to its record:

    python, torch, transformers, vllm, qwen_vl_utils versions
    GPU name and driver-visible CUDA version
    container path and sha256          (computed by the job script, passed in)
    weights directory and a content hash over every file in it

The weights hash is sha256 over `(relative path, sha256(file))` for every file,
so it changes if any shard, config or tokenizer file changes. Hashing ~16 GB of
shards per job would waste GPU allocation, so per-file digests are cached under
`$HF_HOME/../rcp_weights_<name>.json`, keyed on size and mtime.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import pathlib
import platform
import sys

PACKAGES = ("torch", "transformers", "vllm", "qwen_vl_utils", "qwen-vl-utils",
            "accelerate", "pillow")


def run_id() -> str:
    job = os.environ.get("SLURM_JOB_ID")
    return f"slurm-{job}" if job else "local-" + _dt.datetime.now().strftime("%Y%m%dT%H%M%S")


def _versions() -> dict[str, str | None]:
    from importlib import metadata

    out: dict[str, str | None] = {}
    for p in PACKAGES:
        try:
            out[p] = metadata.version(p)
        except metadata.PackageNotFoundError:
            continue
    return out


def _gpu() -> dict[str, str | None]:
    try:
        import torch
    except ImportError:
        return {"gpu": None, "cuda": None}
    if not torch.cuda.is_available():
        return {"gpu": None, "cuda": torch.version.cuda}
    return {"gpu": torch.cuda.get_device_name(0), "cuda": torch.version.cuda}


def _file_sha(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


def weights_hash(model_dir: str) -> str | None:
    root = pathlib.Path(os.path.expandvars(model_dir))
    if not root.is_dir():
        return None
    cache_dir = pathlib.Path(os.environ.get("HF_HOME", root.parent / ".cache")).parent
    cache = cache_dir / f"rcp_weights_{root.name}.json"
    try:
        known = json.loads(cache.read_text())
    except (OSError, ValueError):
        known = {}
    entries, fresh = [], {}
    for p in sorted(x for x in root.rglob("*") if x.is_file() and not x.name.startswith(".")):
        rel = str(p.relative_to(root))
        st = p.stat()
        hit = known.get(rel)
        if hit and hit["size"] == st.st_size and hit["mtime"] == st.st_mtime:
            digest = hit["sha256"]
        else:
            digest = _file_sha(p)
        fresh[rel] = {"size": st.st_size, "mtime": st.st_mtime, "sha256": digest}
        entries.append(f"{rel}\t{digest}")
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(fresh, indent=1))
    except OSError:
        pass  # a read-only cache costs time next job, not correctness
    return hashlib.sha256("\n".join(entries).encode()).hexdigest()


def record(model_dir: str, **extra) -> dict:
    return {
        "run_id": run_id(),
        "time_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "host": platform.node(),
        "python": sys.version.split()[0],
        "packages": _versions(),
        **_gpu(),
        "container": os.environ.get("RCP_CONTAINER"),
        "container_sha256": os.environ.get("RCP_CONTAINER_SHA256"),
        # read on the host by the job script: the container cannot see the
        # superproject's .git. "dirty" = uncommitted changes at submission.
        "git_commit": os.environ.get("RCP_GIT_COMMIT"),
        "git_dirty": os.environ.get("RCP_GIT_DIRTY"),
        "model_dir": os.path.expandvars(model_dir),
        "weights_sha256": weights_hash(model_dir),
        **extra,
    }


def append(path: pathlib.Path, rec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
