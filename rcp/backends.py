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

import json
from typing import Any

#: Default weights path on the AART cluster. `$USER` is expanded at call time —
#: never hardcode a username (repo-wide rule). Same GPTQ checkpoint P9 used, so
#: no new download and no new container.
DEFAULT_MODEL_DIR = "/data/$USER/glm-4-32b-0414-gptq"

#: GLM-4-32B's own limit; a plan plus the system prompt is far inside it.
DEFAULT_MAX_MODEL_LEN = 8192

#: The response is four short fields. A cap this low is also a guard: a model
#: that starts narrating has already failed the "no explanation" instruction, and
#: truncating it turns a runaway generation into one parse failure.
DEFAULT_MAX_TOKENS = 256


def run_vllm_batch(prompts: list[tuple[str, str]], model_dir: str, schema: dict,
                   max_model_len: int = DEFAULT_MAX_MODEL_LEN,
                   max_tokens: int = DEFAULT_MAX_TOKENS) -> list[Any]:
    """Run (system, user) pairs through one vLLM instance.

    Returns a list aligned with `prompts`, each entry a parsed dict or None.
    None is a parse failure and is handled by `extract_llm.parse_response`; this
    function does not decide what a failure means.
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
    params = SamplingParams(temperature=0.0, max_tokens=max_tokens, **guided)

    conversations = [[{"role": "system", "content": s},
                      {"role": "user", "content": u}] for s, u in prompts]
    outputs = llm.chat(conversations, params)

    parsed: list[Any] = []
    for out in outputs:
        text = out.outputs[0].text if out.outputs else ""
        try:
            parsed.append(json.loads(text))
        except (json.JSONDecodeError, TypeError):
            # Guided decoding should make this unreachable; keep the raw text so
            # extract_llm._loads gets a second chance and the failure is visible.
            parsed.append(text)
    return parsed
