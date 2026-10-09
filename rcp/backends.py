"""The model call, isolated. GLM-4-32B under vLLM guided decoding, cluster-only.

Same arrangement as P9's `plan_adequacy/extract.py`, and for the same two reasons:

  * **vLLM is imported inside the function.** Every other module in `rcp/` then
    imports on a machine with no vLLM and no GPU, so the deterministic pass, the
    prompt builders, the parser and the whole test suite run on a laptop. Only
    this one function needs the cluster.
  * **Prompt building and parsing live elsewhere** (`extract_llm`), so calibration
    exercises byte-identical code to the run. A calibration pass that used a
    different prompt path would prove nothing about what ships.

Greedy decoding, temperature 0.0, one model, one pass. plan.md §7.1 fixes the
planner at k=1 and the extractor has no reason to differ: a sampled extractor
would put variance in the measuring instrument.
"""

from __future__ import annotations

from typing import Callable

#: Default weights path on the AART cluster. `$USER` is expanded at call time —
#: never hardcode a username (repo-wide rule). Same GPTQ checkpoint P9 used, so
#: no new download and no new container.
DEFAULT_MODEL_DIR = "/data/$USER/glm-4-32b-0414-gptq"

#: GLM-4-32B's own limit; a plan plus the system prompt is far inside it.
DEFAULT_MAX_MODEL_LEN = 8192

#: The response is four short fields, but `not_assigned_work` echoes asset tokens
#: and a long plan can name twenty. At 256 the exploratory run lost 24 of 220
#: replies to parse failure (7 blind, 17 stated), uncorrelated with plan length
#: and undiagnosable because the raw text was discarded. 768 leaves room; the
#: retry below catches what still truncates.
DEFAULT_MAX_TOKENS = 768

#: A reply that fails to parse is re-asked once with this cap. Decoding is greedy,
#: so re-asking with the same cap would return the same bytes: the only failure a
#: retry can fix is truncation, and a larger cap is what fixes it.
RETRY_MAX_TOKENS = 2048


def run_vllm_batch(prompts: list[tuple[str, str]], model_dir: str, schema: dict,
                   max_model_len: int = DEFAULT_MAX_MODEL_LEN,
                   max_tokens: int = DEFAULT_MAX_TOKENS,
                   retry_if: Callable[[str], bool] | None = None,
                   retry_max_tokens: int = RETRY_MAX_TOKENS) -> list[dict]:
    """Run (system, user) pairs through one vLLM instance.

    Returns a list aligned with `prompts` of {"text", "finish_reason", "attempts"}.
    The text is kept verbatim; `extract_llm.parse_response` decides what it means.
    `retry_if(text)` marks replies to re-ask once at `retry_max_tokens`; the
    retried reply replaces the first, and `attempts` records that it happened.
    """
    import os

    from vllm import LLM, SamplingParams

    try:  # vLLM <= 0.11
        from vllm.sampling_params import GuidedDecodingParams
        guided = {"guided_decoding": GuidedDecodingParams(json=schema)}
    except ImportError:  # vLLM 0.12 renamed it
        from vllm.sampling_params import StructuredOutputsParams
        guided = {"structured_outputs": StructuredOutputsParams(json=schema)}

    resolved = os.path.expandvars(model_dir)
    print(f"  [vLLM] loading {resolved}")
    llm = LLM(
        model=resolved,
        dtype="auto",
        max_model_len=max_model_len,
        trust_remote_code=True,
        gpu_memory_utilization=0.90,
        # The system prompt is byte-identical across every call in the batch.
        enable_prefix_caching=True,
    )

    def run(batch: list[tuple[str, str]], cap: int) -> list[dict]:
        params = SamplingParams(temperature=0.0, max_tokens=cap, **guided)
        conversations = [[{"role": "system", "content": s},
                          {"role": "user", "content": u}] for s, u in batch]
        out = []
        for o in llm.chat(conversations, params):
            first = o.outputs[0] if o.outputs else None
            out.append({"text": first.text if first else "",
                        "finish_reason": getattr(first, "finish_reason", None),
                        "attempts": 1})
        return out

    results = run(prompts, max_tokens)
    if retry_if is not None:
        redo = [i for i, r in enumerate(results) if retry_if(r["text"])]
        if redo:
            print(f"  [vLLM] {len(redo)} replies failed to parse; retrying at "
                  f"max_tokens={retry_max_tokens}")
            for i, r in zip(redo, run([prompts[i] for i in redo], retry_max_tokens)):
                results[i] = {**r, "attempts": 2}
    return results
