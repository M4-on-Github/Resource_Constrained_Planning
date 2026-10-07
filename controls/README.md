# `controls/` — the hand-written material

Everything in this directory exists because the pipeline cannot check itself. Two
files here are generated; the plans are not, and that is the point.

## What is here

| path | written by | purpose |
|---|---|---|
| `gold_stimuli.txt` | generated — `rcp.render.planner_prompt` over 10 selected cells | the verbatim briefing the gold-plan author worked from |
| `gold_plans/*.txt` | **a human-equivalent author, working blind** | §8.4's coverage-gate input |
| `gold_plans/NOTES.md` | the same author | the judgement calls, for review |

## The 10 cells, and why these 10

All four casualty states, all three size categories, eight satisfiable ledgers and
two that cannot be met inside the deadline:

| cell | state | size | ratio_fleet | ratio_deadline | satisfiable |
|---|---|---|---|---|---|
| `AGR-00017/SUFFICIENT` | aground | large | 1.85 | 1.24 | yes |
| `AGR-00018/SURPLUS` | aground | medium | 3.72 | 3.01 | yes |
| `CAP-00019/SUFFICIENT` | capsized | medium | 1.81 | 1.21 | yes |
| `CAP-00076/SURPLUS` | capsized | large | 3.20 | 2.46 | yes |
| `ON_-00135/SUFFICIENT` | on_fire | medium | 1.64 | 1.21 | yes |
| `ON_-00142/SURPLUS` | on_fire | large | 3.62 | 3.05 | yes |
| `SUN-00064/SUFFICIENT` | sunken | medium | 1.88 | 1.21 | yes |
| `SUN-00073/SURPLUS` | sunken | medium | 3.79 | 3.00 | yes |
| `AGR-00045/INFEASIBLE` | aground | medium | 0.63 | 0.25 | no |
| `SUN-00027/INFEASIBLE` | sunken | large | 0.82 | 0.27 | no |

Every casualty state appears at least twice, because the V5 vocabulary is
per-casualty and a state covered by one plan is a vocabulary tested by one sentence.

The two unsatisfiable cells are deliberate. A gold set made only of solvable
scenarios would never show whether the instrument can recognise a correct refusal,
which is half of §5.2.

**No §7.2 trap cell is included, because none exist.** `TRAP_FRACTION = 0.0` in v1,
so no scenario has `ratio_fleet > 1 ≥ ratio_deadline`. When the trap arm is enabled,
this set needs at least one, and the gold plan for it is the one that decides whether
a correct "the tide cannot be made" reads as a refusal or as a failure.

## Why the author was kept blind, and what that buys

The author read `gold_stimuli.txt` and nothing else. They were instructed not to open
`rcp/world.py`, `rcp/validator.py`, `rcp/flags.py`, the extractor, `plan.md`, or
`tests/`.

This is not ceremony. §8.4's gate measures *the fraction of steps a competent salvage
master wrote that the domain cannot name*. A plan written with `goal_vocabulary()` in
view would score 0 % `NO_MATCH` by construction, and the gate would be measuring its
own prompt. The blindness is what makes the number mean anything, and it is the same
reason the validator is not allowed to be an oracle for the planner.

**Known limitation: the author had no photograph.** The planner sees the casualty
image; the author saw only the ledger, plus the casualty state inferred from the
cell ID's prefix (`AGR-`, `CAP-`, `ON_-`, `SUN-`). The prompt itself does not state
the casualty state in the `blind` condition -- the domain block offers all four as
"may be" -- so the author had slightly *more* than a blind planner and slightly less
than a `stated`-condition one. So these
plans are sound-against-the-ledger but not grounded in the specific vessel, and they
are therefore valid input for the *vocabulary* gate — which reads action verbs — and
**not** a reference standard for visual grounding. Nothing in v1 scores visual
grounding, so this costs the gate nothing; it would matter the moment a check reads
the image.

## Running the gate

```bash
python -m rcp.coverage --out results/coverage.json
```

The rate is printed whatever it is, and `rcp.report` prints the line unconditionally.
A gate that is only mentioned when it passes is not a gate.

**If the rate is non-zero, the vocabulary is too narrow — not the plan wrong.** Widen
`goal_vocabulary` in `data/requirements.json`, or narrow what the prompt invites, and
re-run. Editing a gold plan to make the gate pass destroys the only independent
measurement in the repo.
