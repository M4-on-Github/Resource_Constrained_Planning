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
from .render import CONDITIONS, domain_digest, planner_prompt
from .schema import Scenario

#: §7.1's planner. Vision-language, 8B, runs in one RTX6000Ada at bf16.
DEFAULT_MODEL_DIR = "/data/$USER/qwen3vl-8b"

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


def corpus(limit: int | None = None,
           arms: tuple[str, ...] = ARMS) -> list[Scenario]:
    """The corpus, ordered image-major then by §7.2's arm order.

    Image-major matters for a partial run: `--limit 40` is then 10 complete images
    across all four arms rather than 40 cells of one arm, so an interrupted run still
    supports the paired trend test (§9.2) on a complete-case subset.

    `arms` narrows to a single arm for the disclosure experiment, which is run at
    `SUFFICIENT` only. `--limit` divides by the number of arms actually requested,
    so the "keeps arms complete" property holds for one arm as well as four.
    """
    bad = [a for a in arms if a not in ARMS]
    if bad:
        raise ValueError(f"unknown arm(s) {bad}; expected from {ARMS}")
    rows = manifest()
    if limit:
        rows = rows[:max(1, limit // len(arms))]
    by_key = {key(s): s for s in build_corpus(rows)}
    out = []
    for img, _, _ in rows:
        for arm in arms:
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
        max_tokens: int = DEFAULT_MAX_TOKENS, condition: str = "blind"):
    """Yield `(scenario, prose)` one cell at a time. Cluster-only.

    **Transformers, not vLLM.** The planner runs in `castor_qwen.sif`, which is the
    container QWEN-Maritime already validated against these exact weights on this
    cluster, and it carries no vLLM -- `castor_judge.sif` has vLLM but its 0.8.5
    registry has no `qwen3_vl`, so neither container can do both. The call shape
    below is copied from `QWEN-Maritime/CASTOR/run_inference.py` rather than
    invented, including `dtype=torch.float16`, because that is the version-matched
    spelling on the installed transformers there.

    **This is a generator so the caller can write as it goes.** vLLM returned the
    whole batch at once and losing it to a walltime kill cost nothing, because a
    rerun was minutes. HF `generate` is one forward pass per cell over ~1-1.5 h, so
    buffering would mean a timeout at 99 % wrote nothing and `--resume` had nothing
    to resume from.
    """
    import os

    import torch
    from transformers import AutoProcessor, Qwen3VLForConditionalGeneration

    try:
        from qwen_vl_utils import process_vision_info
    except ImportError:  # pragma: no cover - container-only dependency
        process_vision_info = None

    resolved = os.path.expandvars(model_dir)
    print(f"  [transformers] loading {resolved}", flush=True)
    processor = AutoProcessor.from_pretrained(resolved)
    model = Qwen3VLForConditionalGeneration.from_pretrained(
        resolved, dtype=torch.float16, device_map="cuda")
    model.eval()

    images = manifest_images()
    for i, sc in enumerate(scenarios, 1):
        path = image_path(sc, root, images)
        messages = [{"role": "user", "content": [
            {"type": "image", "image": str(path)},
            {"type": "text", "text": planner_prompt(sc, condition)},
        ]}]
        # apply_chat_template inserts the model's own image placeholder tokens;
        # hand-writing them is the thing that silently breaks across versions.
        text = processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True)
        if process_vision_info is not None:
            img_in, _ = process_vision_info(messages)
        else:
            from PIL import Image
            img_in = [Image.open(path).convert("RGB")]
        inputs = processor(text=[text], images=img_in,
                           return_tensors="pt", padding=True).to(model.device)

        # Greedy, k=1 (sec. 7.1). do_sample=False is the decisive flag; temperature
        # is left unset because passing one alongside do_sample=False only earns a
        # warning and cannot take effect.
        with torch.inference_mode():
            ids = model.generate(**inputs, max_new_tokens=max_tokens,
                                 do_sample=False)
        trimmed = ids[0][inputs["input_ids"].shape[1]:]
        prose = processor.decode(trimmed, skip_special_tokens=True)
        print(f"  [{i}/{len(scenarios)}] {key(sc)}  {len(prose.split())} words",
              flush=True)
        yield sc, prose


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="RCP planner: image + ledger -> salvage plan prose (plan.md §7.1)")
    ap.add_argument("--images", required=True,
                    help="sorted_images root, i.e. the directory holding "
                         "aground/ capsized/ on_fire/ sunken/")
    ap.add_argument("--out", required=True, help="output JSONL")
    ap.add_argument("--model-dir", default=DEFAULT_MODEL_DIR)
    ap.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    ap.add_argument("--arm", action="append", choices=list(ARMS), default=None,
                    help="restrict to one arm; repeatable. Default: all four")
    ap.add_argument("--condition", choices=list(CONDITIONS), default="blind",
                    help="casualty-state disclosure. 'blind' (default) is the "
                         "pre-existing prompt; 'stated' adds one line naming the "
                         "state. Recorded in domain_digest so the two cannot pool")
    ap.add_argument("--limit", type=int, default=None,
                    help="first N cells, image-major (keeps arms complete)")
    ap.add_argument("--resume", action="store_true",
                    help="append, skipping scenario keys already in --out")
    ap.add_argument("--dry-run", action="store_true",
                    help="write the prompts and exit; no model, no GPU")
    args = ap.parse_args(argv)
    arms = tuple(args.arm) if args.arm else ARMS

    root = pathlib.Path(args.images)
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    cells = corpus(args.limit, arms)
    images = manifest_images()
    missing = [sc.id for sc in cells if not image_path(sc, root, images).exists()]
    if missing:
        print(f"ERROR: {len(set(missing))} images not found under {root}, "
              f"first: {sorted(set(missing))[:3]}", file=sys.stderr)
        return 1

    digest = domain_digest(args.condition)
    if args.resume:
        already = done_keys(out)
        cells = [sc for sc in cells if key(sc) not in already]
        print(f"  resuming: {len(already)} done, {len(cells)} to go")
    print(f"  arms         : {', '.join(arms)}")
    print(f"  condition    : {args.condition}")
    print(f"  cells        : {len(cells)}")
    print(f"  domain digest: {digest}   (Rule 2 - must match across pooled runs)")

    if args.dry_run:
        dest = out.with_suffix(".prompts.jsonl")
        with dest.open("w", encoding="utf-8", newline="\n") as fh:
            for sc in cells:
                fh.write(json.dumps({
                    "scenario_id": sc.id, "arm": sc.arm,
                    "condition": args.condition,
                    "image": str(image_path(sc, root, images)),
                    "prompt": planner_prompt(sc, args.condition),
                }, sort_keys=True) + "\n")
        print(f"  dry run -> {dest}")
        return 0

    if not cells:
        print("  nothing to do")
        return 0

    # Flushed per cell. A walltime kill then leaves a file `--resume` can read, and
    # a half-written final line is tolerated by `done_keys`, which skips rows it
    # cannot parse rather than aborting.
    mode = "a" if args.resume and out.exists() else "w"
    n = empty = 0
    with out.open(mode, encoding="utf-8", newline="\n") as fh:
        for sc, prose in run(cells, root, args.model_dir, args.max_tokens,
                             args.condition):
            fh.write(json.dumps({
                "scenario_id": sc.id,
                "arm": sc.arm,
                "casualty_state": sc.casualty_state,
                "condition": args.condition,
                "prose": prose.strip(),
                "domain_digest": digest,
                "model_dir": args.model_dir,
            }, sort_keys=True) + "\n")
            fh.flush()
            n += 1
            empty += 0 if prose.strip() else 1

    print(f"  {n} generations -> {out}")
    print(f"  empty          : {empty}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
