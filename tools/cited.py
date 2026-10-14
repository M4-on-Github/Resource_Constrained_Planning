"""Numbers cited in docs/deviations.md (D8-D11) that no other tool prints.

Each line names its entry and recomputes the number with the pattern or
definition it was first reported with. Numbers other tools print are not
repeated: `rcp.report` (`results/rep_*/report.txt`: loops, branches and
truncation per arm; D9's sensitivity), `tools/guard_check.py` (the D10 and D12
test tables), `tools/branch_diag.py` (D12), `tools/audit.py` (D10's hand reads),
`tools/flip_direction.py` and `rcp.calibrate` (D11).

    python3 tools/cited.py           # from results/ and cal/
    python3 tools/cited.py images    # D9: image sizes; needs ../shipwreck_wiki_images
    python3 tools/cited.py tokens    # D9: repeated token runs; needs the planner's tokenizer
    python3 tools/cited.py p9        # D10: P9's procedural_v3 plans; needs ../Eval_CASTOR

P9's answers file is untracked in Eval_CASTOR; the one read had sha256 `84f88c5d…`.

Run in the container from the repo root. `images` and `p9` need the BenchyBench
root bound; `tokens` needs /data/$USER bound and transformers (castor_qwen.sif).
Not re-derived: D0-D5 (measured with
the code of the time), job ids and crash details (SLURM logs), and D10's "same
result as before for all 940" (a comparison with parser code since replaced).
"""

from __future__ import annotations

import collections
import csv
import getpass
import json
import pathlib
import re
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rcp import extract_det as ed  # noqa: E402
from rcp.calibrate import _bool, _tokens  # noqa: E402
from rcp.generator import manifest_images  # noqa: E402
from rcp.normalize import normalize  # noqa: E402
from tools.guard_check import measure  # noqa: E402

ARMS = ("SURPLUS", "SUFFICIENT", "SCARCE", "INFEASIBLE")
IMAGES = "../shipwreck_wiki_images/sorted_images"
TOKENIZER = f"/data/{getpass.getuser()}/qwen3vl-8b"
P9 = ("../Eval_CASTOR/pipelines/plan_coherence/improved/results/"
      "answers_qwen3vl8b_baseline_procedural_v3_improved.jsonl")

#: D10 (i), counted over the whole prose. tools/branch_diag.py's "state" trigger
#: is a later, broader pattern and gives other counts.
STATE_IF = re.compile(r"if the vessel (is|has been)? ?(found to be |confirmed (to be )?)?"
                      r"(aground|capsized|sunken|on fire)", re.I)
#: D10 test 1, counted over conditional steps only.
TYPE_IF = re.compile(r"if (the )?(vessel|ship|wreck|hull|casualty) is (found |determined |"
                     r"confirmed )?(to be )?(aground|grounded|capsized|sunk|sunken|on fire|"
                     r"burning)", re.I)
ASKS = re.compile(r"request|call for|mobili[sz]e additional", re.I)
#: D10 test 2: the wording that opens a conditional step's condition.
LEAD = re.compile(r"\b(if|unless|should|in case|once|when|otherwise)\b[^,.;]{0,40}", re.I)


def rows(path: str) -> list[dict]:
    return [json.loads(ln) for ln in open(path, encoding="utf-8") if ln.strip()]


def ids(path: str) -> set[str]:
    return {ln.strip() for ln in open(path) if ln.strip() and not ln.startswith("#")}


def gen(cond: str = "blind") -> list[dict]:
    return [r for a in ARMS for r in rows(f"results/gen_{a}_{cond}.jsonl")]


def plan(prose: str) -> tuple[list[str], int]:
    """Steps as extraction scores them (header off, loops cut), and steps dropped."""
    body, dropped = ed.trim_repeated_steps(ed.split_header(prose)[1])
    return ed.segment_steps(body), dropped


def looped(r: dict) -> bool:
    return ed.trim_repeated_steps(r["prose"])[1] > 0


def d8_d9() -> None:
    smoke = rows("results/smoke_SUFFICIENT_blind.jsonl")
    capped = [r for r in smoke if r["truncated"]]
    rest = [r for r in smoke if not r["truncated"]]

    def branches(rs):
        return statistics.median(ed.conditional_steps(ed.segment_steps(r["prose"])) for r in rs)

    explo = rows("cal/exploratory/gen_SUFFICIENT_blind.jsonl")
    print(f"D8   smoke: {len(capped)}/{len(smoke)} hit the cap; the other {len(rest)} ran "
          f"{min(r['n_tokens'] for r in rest)}-{max(r['n_tokens'] for r in rest)} tokens, "
          f"median conditional steps {branches(rest):g} (exploratory blind {branches(explo):g})")
    cut = {r["scenario_id"]: plan(r["prose"]) for r in smoke if looped(r)}
    print(f"D9   smoke loops cut to {', '.join(f'{s} {len(p)}' for s, (p, _) in cut.items())} "
          f"steps; the looped plans are the capped ones: "
          f"{sorted(cut) == sorted(r['scenario_id'] for r in capped)}")
    for cond in ("blind", "stated"):
        ex = rows(f"cal/exploratory/gen_SUFFICIENT_{cond}.jsonl")
        print(f"D9   exploratory {cond}: {sum(map(looped, ex))}/{len(ex)} looped")
    v010 = {r["scenario_id"]: r for r in rows("results/gen_SUFFICIENT_blind.jsonl")}
    same = [r["prose"] == v010[r["scenario_id"]]["prose"] for r in smoke]
    runs = sorted({v010[r["scenario_id"]]["run_id"] for r in smoke})
    print(f"D9   smoke vs the v0.10 rows ({', '.join(runs)}): identical {sum(same)}/{len(same)}")
    redo = [r for r in rows("results/diag/verify_SUFFICIENT_blind.jsonl")
            if r["run_id"] == "slurm-50435"]
    print(f"D9   rerun (slurm-50435) vs saved rows: identical "
          f"{sum(r['prose'] == v010[r['scenario_id']]['prose'] for r in redo)}/{len(redo)}")


def d10() -> None:
    blind, stated = gen("blind"), gen("stated")
    for cond, g in (("blind", blind), ("stated", stated)):
        print(f"D10  v0.10 {cond}, plans branching on the casualty state: "
              f"{sum(bool(STATE_IF.search(r['prose'])) for r in g)}/{len(g)}")
    for a in ARMS:
        t = [r["trace"] for r in rows(f"results/ex_gen_{a}_blind/extracted.jsonl")]
        x, n = sum(len(r["not_assigned_work"]) for r in t), sum(len(r["assets_named"]) for r in t)
        print(f"D10  v010 extractor, {a}/blind: excluded {x} of {n} named assets ({x / n:.1%}); "
              f"plans excluding any {sum(bool(r['not_assigned_work']) for r in t)}/{len(t)}")
    g = blind + stated
    print(f"D10  split_header changes v0.10 plans: "
          f"{sum(ed.split_header(r['prose']) != (None, r['prose']) for r in g)}/{len(g)}")

    t1 = rows("results/v011_guard/gen_blind.jsonl")
    keys = {(r["scenario_id"], r["arm"]) for r in t1}
    base = [r for r in blind if (r["scenario_id"], r["arm"]) in keys]
    for name, rs in (("v0.10", base), ("v0.11 test 1", t1)):
        cs = {r["arm"]: [] for r in rs}
        for r in rs:
            cs[r["arm"]].append([s for s in plan(r["prose"])[0] if ed.conditional_steps([s])])
        print(f"D10  {name}, same 60 cells: plans branching on the casualty type "
              f"{sum(any(TYPE_IF.search(s) for s in c) for v in cs.values() for c in v)}/60; "
              + "; ".join(f"{a} branch steps {sum(map(len, v))}, asking for more "
                          f"{sum(bool(ASKS.search(s)) for c in v for s in c)}"
                          for a, v in sorted(cs.items())))

    clean = collections.defaultdict(list)
    for r in blind:
        steps, dropped = plan(r["prose"])
        if not dropped and not r["truncated"]:
            clean[r["arm"]].append(len(steps))
    kept = [len(plan(r["prose"])[0]) for r in g if looped(r)]
    print("D10  v0.10 blind, median steps of plans neither looped nor truncated: "
          + ", ".join(f"{a} {statistics.median(clean[a]):g}" for a in ARMS)
          + f"; looped plans (both conditions, {len(kept)}) start repeating after "
          f"a median of {statistics.median(kept)}")
    print("D10  v0.10 blind, plans asking for resources (guard_check REQUEST): "
          + ", ".join(f"{a} {measure([r for r in blind if r['arm'] == a])['requests']:.1%}"
                      for a in ARMS))

    wrong = [(r["scenario_id"], r["casualty_state"], ed.split_header(r["prose"])[0])
             for r in t1 if ed.split_header(r["prose"])[0] != r["casualty_state"]]
    per_image = collections.defaultdict(list)
    for sid, _, d in wrong:
        per_image[sid].append(d)
    print(f"D10  test 1 declared-state errors: {len(wrong)}/{len(t1)} cells, true state "
          f"{dict(collections.Counter(w[1] for w in wrong))}, declared "
          f"{dict(collections.Counter(w[2] for w in wrong))}; {len(per_image)} images, read as "
          f"{dict(collections.Counter('/'.join(sorted(v)) for v in per_image.values()))}")

    f16 = {r["scenario_id"]: r for r in rows("results/gen_SURPLUS_blind.jsonl")}
    bf16 = rows("results/dtype_check/gen_bf16.jsonl")
    rate = {}
    for group in (True, False):
        g16 = [r for r in bf16 if looped(f16[r["scenario_id"]]) is group]
        rate[group] = sum(map(looped, g16)) / len(g16)
        print(f"D10  dtype, cells {'looped' if group else 'clean'} in float16: bfloat16 looped "
              f"{sum(map(looped, g16))}/{len(g16)}, prose identical "
              f"{sum(r['prose'] == f16[r['scenario_id']]['prose'] for r in g16)}/{len(g16)}")
    p = sum(map(looped, f16.values())) / len(f16)
    print(f"D10  dtype, SURPLUS/blind loop rate weighted by stratum: bfloat16 "
          f"{p * rate[True] + (1 - p) * rate[False]:.1%}, float16 {p:.1%}")

    keep = ids("cal/v011_guard/ids.txt")
    t2 = [r for a in ("SURPLUS", "SCARCE") for r in rows(f"results/v011/gen_{a}_blind.jsonl")
          if r["scenario_id"] in keep]
    lead = collections.Counter()
    for r in t2:
        for s in plan(r["prose"])[0]:
            if ed.conditional_steps([s]):
                m = LEAD.search(s)
                lead[m.group(0)[:30].lower() if m else s[:40]] += 1
    print(f"D10  test 2, {sum(lead.values())} branch steps; commonest openings: "
          + ", ".join(f"'{k}' {v}" for k, v in lead.most_common(6)))


def d11() -> None:
    def load(name):
        return {(t["scenario_id"], t["arm"]): t for t in
                (json.loads(ln)["trace"] for ln in open(f"cal/d11/{name}/extracted.jsonl"))}

    def labels(name):
        return {(r["scenario_id"], r["arm"]): r for r in
                csv.DictReader(open(f"cal/d11/{name}.csv", encoding="utf-8"))}

    r1, r2, r3 = load("ex_d11"), load("ex_d11_r2"), load("ex_d11_r3")
    print(f"D11  r1 replies that hit the token cap: "
          f"{sum(t['llm_finish_reason'] == 'length' for t in r1.values())}/{len(r1)}")
    dev = labels("labels_dev")
    gold = {k: _tokens(v["commitments"]) for k, v in dev.items()}
    parsed = [k for k in dev if not r1[k]["llm_parse_failed"]]
    for name, t in (("r1", r1), ("r2", r2)):
        miss = sum(len(gold[k] - {normalize(a) for a in t[k]["commitments"]}) for k in parsed)
        esc = sum(t[k]["escalate"] != _bool(dev[k]["escalate"], k) for k in parsed)
        print(f"D11  {name} on the {len(parsed)} dev plans r1 parsed: misses {miss} "
              f"committed assets, escalate wrong on {esc}")
    placed = [(k, a) for k in dev for a in r1[k]["assets_named"]
              if normalize(a) in gold[k] and a not in (r1[k]["roles_missing"] or [])]
    print(f"D11  of the {len(placed)} gold-committed assets r1 placed, not committed: "
          f"r1 {sum(r1[k]['asset_roles'][a] != 'committed' for k, a in placed)}, "
          f"r3 {sum(r3[k]['asset_roles'].get(a) != 'committed' for k, a in placed)}")
    q = collections.defaultdict(lambda: [0, 0])
    for k in dev:
        t = r3[k]
        names = t["assets_named"]
        for i, a in enumerate(names):
            if normalize(a) in gold[k] and a not in (t["roles_missing"] or []):
                q[min(3, 4 * i // len(names))][0] += t["asset_roles"][a] != "committed"
                q[min(3, 4 * i // len(names))][1] += 1
    print("D11  r3, gold-committed assets called not committed, by quarter of the list: "
          + ", ".join(f"{q[i][0]}/{q[i][1]}" for i in range(4)))
    a, b = labels("labels_heldout_a"), labels("labels_heldout_b")
    same = {f: sum(_bool(a[k][f], k) == _bool(b[k][f], k) for k in a)
            for f in ("goal_attempted", "escalate", "reduce")}
    print(f"D11  A-B agreement on {len(a)} held-out plans: commitments identical "
          f"{sum(_tokens(a[k]['commitments']) == _tokens(b[k]['commitments']) for k in a)}, "
          + ", ".join(f"{f} {v}" for f, v in same.items()))


def images(root: str = IMAGES) -> None:
    from PIL import Image
    mp = {s: Image.open(f"{root}/{p}").size for s, p in manifest_images().items()}
    big = sorted(s for s, (w, h) in mp.items() if w * h >= 5_000_000)
    print(f"D9   images of 5 MP or more: {len(big)}/{len(mp)}")


def longest_repeat(seq: list[int]) -> int:
    """Longest n such that some n-gram occurs twice."""
    def has(n):
        seen = set()
        for i in range(len(seq) - n + 1):
            if tuple(seq[i:i + n]) in seen:
                return True
            seen.add(tuple(seq[i:i + n]))
        return False
    lo, hi = 0, len(seq)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        lo, hi = (mid, hi) if has(mid) else (lo, mid - 1)
    return lo


def tokens(model_dir: str = TOKENIZER) -> None:
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_dir)
    for path in ("results/smoke_SUFFICIENT_blind.jsonl",
                 "cal/exploratory/gen_SUFFICIENT_blind.jsonl",
                 "cal/exploratory/gen_SUFFICIENT_stated.jsonl"):
        loop, other = [], []
        for r in rows(path):
            t = tok(r["prose"], add_special_tokens=False)["input_ids"]
            (loop if looped(r) else other).append((longest_repeat(t), len(t), r["scenario_id"]))
        print(f"D9   {path}: looped {len(loop)}, longest repeat "
              f"{min(loop)[0]}-{max(loop)[0]} tokens, length {min(x[1] for x in loop)}-"
              f"{max(x[1] for x in loop)}; not looped {len(other)}, longest repeat median "
              f"{statistics.median(x[0] for x in other):g}, top "
              + ", ".join(f"{s} {n} ({m} tokens)" for n, m, s in sorted(other)[-3:][::-1]))


def p9(path: str = P9) -> None:
    truth = {v: v.split("/")[0] for v in manifest_images().values()}
    sid = {v: k for k, v in manifest_images().items()}
    keep = ids("cal/v011_guard/ids.txt")
    rs = rows(path)
    dec = [(truth[r["image"]], ed.split_header(r["text"])[0], sid[r["image"]] in keep, r)
           for r in rs]
    print(f"D10  P9 procedural_v3: one declared state "
          f"{sum(d not in (None, 'ambiguous') for _, d, _, _ in dec)}/{len(rs)}")
    for name, sel in (("all", dec), ("test-1 images", [x for x in dec if x[2]])):
        ok = sum(t == d for t, d, _, _ in sel)
        sunk = [t == d for t, d, _, _ in sel if t == "sunken"]
        print(f"D10  P9 procedural_v3, {name}: state correct {ok}/{len(sel)}, "
              f"sunken {sum(sunk)}/{len(sunk)}")
    branched = sum(bool(ed.conditional_steps(plan(r["text"])[0])) for r in rs)
    print(f"D10  P9 procedural_v3, plans with a conditional step: {branched}/{len(rs)}")


if __name__ == "__main__":
    cmd = sys.argv[1:2]
    if not cmd:
        d8_d9(), d10(), d11()
    elif cmd[0] in ("images", "tokens", "p9"):
        globals()[cmd[0]](*sys.argv[2:])
    else:
        sys.exit(__doc__)
