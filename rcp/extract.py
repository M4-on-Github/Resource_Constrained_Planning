"""Composition: prose in, `ExtractedPlan` out. plan.md §6.3.

`ExtractedPlan` is the airlock (§3.6 claim 1) — the validator never sees prose,
so everything the validator can be wrong about has to be wrong here first. The
division of labour is therefore the whole design:

| field           | decided by      | why |
|-----------------|-----------------|-----|
| `assets_named`  | deterministic   | §6.3 states the rule as a resolution test |
| `commitments`   | det. minus LLM  | a subtraction from a closed set, never an extraction |
| `goal_attempted`| det. OR LLM     | vocabulary match, model adjudicates only the misses |
| `escalate`      | LLM             | no deterministic surface |
| `reduce`        | LLM             | no deterministic surface |
| counts          | deterministic   | §9.2 covariates |

Two properties this buys, both enforced in code rather than asked of the model:

  * `commitments ⊆ assets_named`, so **V1 cannot fail because of the extractor**
    and the model cannot manufacture a `HALLUCINATE`.
  * The model can only *remove* capability from V3's pool, never add to it.

`goal_attempted` is a disjunction on purpose. The deterministic pass is the
vocabulary match §8.4's coverage gate measures; the model is asked the same
question regardless, and both answers are recorded in the trace. The gate's
NO_MATCH rate is then `goal_hit_det == False and attempts_goal == True` —
generations where the plan did attempt the goal in wording the frozen vocabulary
does not contain. That is the number that tells you whether V5 is too narrow,
and it falls out of the run instead of needing its own pass.

**The extraction loss of V2a and V3 is therefore not zero, and §4's registry must
not claim it is.** It is bounded — a subtraction from a deterministic set — and it
is measured on the calibration subset, per field, against hand labels. V1's ~0 is
real because nothing above touches it.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from . import backends, extract_det, extract_llm
from .schema import ExtractedPlan, Scenario
from .world import states


def deterministic_only(prose: str, scenario: Scenario) -> tuple[ExtractedPlan, dict]:
    """Extraction with no model, for tests and for a dry run over real prose.

    Commits every named asset and takes no stance. Not a substitute for the full
    pass: it cannot see a refusal, so `ESCALATE` is always false and §5.2's
    correct-refusal rate would read as zero. Useful for checking the resolver and
    the counts against real generations before spending GPU time.
    """
    det = extract_det.deterministic_pass(prose, scenario)
    plan = ExtractedPlan(
        scenario_id=scenario.id,
        arm=scenario.arm,
        assets_named=det["assets_named"],
        commitments=det["assets_named"],
        goal_attempted=det["goal_hit_det"],
        step_count=det["step_count"],
        word_count=det["word_count"],
        parse_failed=det["parse_failed"],
    )
    return plan, {**det, "llm": None}


def compose(prose: str, scenario: Scenario, llm_raw: object) -> tuple[ExtractedPlan, dict]:
    """The real extraction: deterministic pass, then the model's subtraction."""
    det = extract_det.deterministic_pass(prose, scenario)
    named = det["assets_named"]
    llm = extract_llm.parse_response(llm_raw, named)

    excluded = set(llm["not_assigned_work"])
    commitments = tuple(t for t in named if t not in excluded)

    plan = ExtractedPlan(
        scenario_id=scenario.id,
        arm=scenario.arm,
        assets_named=named,
        commitments=commitments,
        # The vocabulary match is authoritative when it fires; the model is only
        # ever asked to rescue a miss. A model saying "no" cannot overturn a
        # literal goal phrase in the prose.
        goal_attempted=det["goal_hit_det"] or llm["attempts_goal"],
        escalate=llm["escalates"],
        reduce=llm["reduces"],
        step_count=det["step_count"],
        word_count=det["word_count"],
        parse_failed=det["parse_failed"],
    )
    trace = {
        "scenario_id": scenario.id,
        "arm": scenario.arm,
        "assets_named": list(named),
        "not_assigned_work": list(llm["not_assigned_work"]),
        "commitments": list(commitments),
        "goal_hit_det": det["goal_hit_det"],
        "goal_matched": list(det["goal_matched"]),
        "attempts_goal_llm": llm["attempts_goal"],
        # §8.4's coverage gate: the plan reached the goal in wording the frozen
        # vocabulary does not contain.
        "v5_no_match": (not det["goal_hit_det"]) and llm["attempts_goal"],
        "escalate": llm["escalates"],
        "reduce": llm["reduces"],
        "step_count": det["step_count"],
        "word_count": det["word_count"],
        "parse_failed": det["parse_failed"],
        "llm_parse_failed": llm["llm_parse_failed"],
    }
    return plan, trace


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _load_scenarios() -> dict[str, Scenario]:
    """The corpus, keyed as the generation rows reference it.

    Rebuilt rather than read from disk: the generator is deterministic given
    data/, so this is the same 440 cells the planner was shown, and a drift in
    data/ shows up as a missing key instead of a silently different ledger.
    """
    from .generator import build_corpus, manifest

    return {f"{s.id}/{s.arm}": s for s in build_corpus(manifest())}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="RCP extraction: plan prose -> ExtractedPlan (plan.md §6.3)")
    ap.add_argument("--input", required=True,
                    help="JSONL of generations: {scenario_id, arm, prose}")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--model-dir", default=backends.DEFAULT_MODEL_DIR,
                    help="vLLM weights dir (GLM-4-32B GPTQ, as P9)")
    ap.add_argument("--no-llm", action="store_true",
                    help="deterministic pass only; no GPU, no model")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args(argv)

    scenarios = _load_scenarios()
    rows = [json.loads(ln) for ln in
            pathlib.Path(args.input).read_text(encoding="utf-8").splitlines() if ln.strip()]
    if args.limit:
        rows = rows[:args.limit]

    items = []
    for r in rows:
        key = f"{r['scenario_id']}/{r['arm']}"
        sc = scenarios.get(key)
        if sc is None:
            print(f"  [skip] no scenario for {key}", file=sys.stderr)
            continue
        det = extract_det.deterministic_pass(r["prose"], sc)
        items.append({"row": r, "scenario": sc, "prose": r["prose"],
                      "assets_named": det["assets_named"],
                      "goal": states()[sc.casualty_state]["goal"]})

    if args.no_llm:
        results = [deterministic_only(it["prose"], it["scenario"]) for it in items]
    else:
        prompts = extract_llm.build_prompts(items)
        raws = backends.run_vllm_batch(prompts, args.model_dir, extract_llm.SCHEMA)
        results = [compose(it["prose"], it["scenario"], raw)
                   for it, raw in zip(items, raws)]

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "extracted.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for plan, trace in results:
            fh.write(json.dumps({"plan": _plan_dict(plan), "trace": trace},
                                sort_keys=True) + "\n")

    failed = sum(1 for _, t in results if t.get("llm_parse_failed"))
    empty = sum(1 for _, t in results if t["parse_failed"])
    no_match = sum(1 for _, t in results if t.get("v5_no_match"))
    print(f"  {len(results)} extracted -> {out / 'extracted.jsonl'}")
    print(f"  empty generations      : {empty}")
    print(f"  llm parse failures     : {failed}")
    print(f"  V5 vocabulary misses   : {no_match}  (sec. 8.4 coverage gate)")
    return 0


def _plan_dict(plan: ExtractedPlan) -> dict:
    import dataclasses

    d = dataclasses.asdict(plan)
    for k, v in d.items():
        if isinstance(v, tuple):
            d[k] = list(v)
    return d


if __name__ == "__main__":
    raise SystemExit(main())
