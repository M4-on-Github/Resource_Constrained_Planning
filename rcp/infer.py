"""The planner. Image + prompt -> prose, one row per (image, arm). plan.md §7.1.

This is the only stage that sees an image and the only stage whose output is not
determined by the repo: everything downstream of `generations.jsonl` is arithmetic
on a frozen corpus. It is therefore also the only stage worth resuming rather than
rerunning, which `--resume` does by scenario key.

**Decoding is greedy, k=1, temperature 0.0** (§7.1). A sampled planner would put
variance in the stimulus as well as the instrument, and §9.4's MDE is derived
against one generation per cell.

**The prompt is assembled by `rcp.render`, not here.** This module's whole job is
batching, image loading and I/O, so Rule 2's byte-identity property is a property of
one module with one test, not of the inference path. `domain_digest` is written into
every row: two runs with different digests are not comparable and must not be pooled.

**Why `llm.generate` with explicit `multi_modal_data` rather than `llm.chat`.** The
chat path builds the multimodal template itself, and which placeholder it inserts has
changed across vLLM versions. Applying the processor's chat template here makes the
exact string the model sees a thing this repo can print and diff — the same reason
the extractor's prompt building lives in a pure function.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from .generator import build_corpus, manifest, manifest_images
from .render import domain_digest, planner_prompt
from .schema import Scenario

#: §7.1's planner. Vision-language, 8B, runs in one RTX6000Ada at bf16.
DEFAULT_MODEL_DIR = "/data/$USER/qwen3-vl-8b-instruct"

#: A salvage plan in numbered steps. Generous enough that a long plan is not
#: truncated into a parse failure, and §9.2 reports word count per arm, so a cap
#: that bit would be a ceiling artifact in the headline's own control column.
DEFAULT_MAX_TOKENS = 1024

#: Arms in §7.2's order. Written out rather than derived so the output file's row
#: order is stable across runs.
ARMS = ("SURPLUS", "SUFFICIENT", "SCARCE", "INFEASIBLE")


def key(sc: Scenario) -> str:
    return f"{sc.id}/{sc.arm}"


def image_path(sc: Scenario, root: pathlib.Path, images: dict[str, str]) -> pathlib.Path:
    rel = images.get(sc.id)
    if rel is None:
        raise KeyError(f"{sc.id} is not in data/manifest.csv — rerun tools/build_manifest.py")
    return root / rel


def corpus(limit: int | None = None) -> list[Scenario]:
    """The 440 cells, ordered image-major then by §7.2's arm order.

    Image-major matters for a partial run: `--limit 40` is then 10 complete images
    across all four arms rather than 40 cells of one arm, so an interrupted run still
    supports the paired trend test (§9.2) on a complete-case subset.
    """
    rows = manifest()
    if limit:
        rows = rows[:max(1, limit // len(ARMS))]
    by_key = {key(s): s for s in build_corpus(rows)}
    out = []
    for img, _, _ in rows:
        for arm in ARMS:
            sc = by_key.get(f"{img}/{arm}")
            if sc is not None:
                out.append(sc)
    return out


def done_keys(path: pathlib.Path) -> set[str]:
    """Scenario keys already present in an output file, for `--resume`."""
    if not path.exists():
        return set()
    seen = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("prose", "").strip():
            seen.add(f"{r['scenario_id']}/{r['arm']}")
    return seen


def run(scenarios: list[Scenario], root: pathlib.Path, model_dir: str,
        max_tokens: int = DEFAULT_MAX_TOKENS) -> list[str]:
    """Generate one plan per scenario. Cluster-only; vLLM is imported here.

    Returns prose aligned with `scenarios`. One vLLM load for the whole batch: the
    prompt's constant halves are byte-identical across all 440 cells, so prefix
    caching pays for itself, and the image is the only per-row payload.
    """
    import os

    from PIL import Image
    from transformers import AutoProcessor
    from vllm import LLM, SamplingParams

    resolved = os.path.expandvars(model_dir)
    print(f"  [vLLM] loading {resolved}", flush=True)
    processor = AutoProcessor.from_pretrained(resolved, trust_remote_code=True)
    llm = LLM(
        model=resolved,
        dtype="auto",
        trust_remote_code=True,
        max_model_len=8192,
        gpu_memory_utilization=0.90,
        enable_prefix_caching=True,
        limit_mm_per_prompt={"image": 1},
    )
    params = SamplingParams(temperature=0.0, top_p=1.0, max_tokens=max_tokens)

    requests = []
    for sc in scenarios:
        img = Image.open(image_path(sc, root, manifest_images())).convert("RGB")
        messages = [{"role": "user", "content": [
            {"type": "image"},
            {"type": "text", "text": planner_prompt(sc)},
        ]}]
        text = processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True)
        requests.append({"prompt": text, "multi_modal_data": {"image": img}})

    outputs = llm.generate(requests, params)
    return [(o.outputs[0].text if o.outputs else "") for o in outputs]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="RCP planner: image + ledger -> salvage plan prose (plan.md §7.1)")
    ap.add_argument("--images", required=True,
                    help="sorted_images root, e.g. "
                         "../DeGF/CASTOR/shipwreck_wiki_images/sorted_images")
    ap.add_argument("--out", required=True, help="output JSONL")
    ap.add_argument("--model-dir", default=DEFAULT_MODEL_DIR)
    ap.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    ap.add_argument("--limit", type=int, default=None,
                    help="first N cells, image-major (keeps arms complete)")
    ap.add_argument("--resume", action="store_true",
                    help="append, skipping scenario keys already in --out")
    ap.add_argument("--dry-run", action="store_true",
                    help="write the prompts and exit; no model, no GPU")
    args = ap.parse_args(argv)

    root = pathlib.Path(args.images)
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    cells = corpus(args.limit)
    images = manifest_images()
    missing = [sc.id for sc in cells if not image_path(sc, root, images).exists()]
    if missing:
        print(f"ERROR: {len(set(missing))} images not found under {root}, "
              f"first: {sorted(set(missing))[:3]}", file=sys.stderr)
        return 1

    digest = domain_digest()
    if args.resume:
        already = done_keys(out)
        cells = [sc for sc in cells if key(sc) not in already]
        print(f"  resuming: {len(already)} done, {len(cells)} to go")
    print(f"  cells        : {len(cells)}")
    print(f"  domain digest: {digest}   (Rule 2 - must match across pooled runs)")

    if args.dry_run:
        dest = out.with_suffix(".prompts.jsonl")
        with dest.open("w", encoding="utf-8", newline="\n") as fh:
            for sc in cells:
                fh.write(json.dumps({
                    "scenario_id": sc.id, "arm": sc.arm,
                    "image": str(image_path(sc, root, images)),
                    "prompt": planner_prompt(sc),
                }, sort_keys=True) + "\n")
        print(f"  dry run -> {dest}")
        return 0

    if not cells:
        print("  nothing to do")
        return 0

    proses = run(cells, root, args.model_dir, args.max_tokens)
    mode = "a" if args.resume and out.exists() else "w"
    with out.open(mode, encoding="utf-8", newline="\n") as fh:
        for sc, prose in zip(cells, proses):
            fh.write(json.dumps({
                "scenario_id": sc.id,
                "arm": sc.arm,
                "casualty_state": sc.casualty_state,
                "prose": prose.strip(),
                "domain_digest": digest,
                "model_dir": args.model_dir,
            }, sort_keys=True) + "\n")

    empty = sum(1 for p in proses if not p.strip())
    print(f"  {len(proses)} generations -> {out}")
    print(f"  empty          : {empty}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
