# RCP v0.13: the knowing-doing probe (pre-registration)

Written 2026-10-14 and frozen at tag `v0.13-prereg`, before any probe output or
ESCALATE-check label exists. It builds on `plan.md` (v0.10, frozen). Unless said
here, the corpus, images, planner, decoding, container and conventions are the
study's. v0.10 is not changed. Every number below is printed by
`tools/probe_gap.py`.

## 1. Question

In v0.10 the planner escalated on 9.1 % (SCARCE) and 12.7 % (INFEASIBLE) of
unsatisfiable ledgers and 5.5 % of satisfiable ones (`results/rep_blind/report.txt`,
§5), although the prompt prints the total assemblable by the deadline
(`rcp/render.py`, `totals_line`). When it does not escalate, is that because it
does not see the shortfall (**knowing**), or because it sees it and the plan does
not say so (**doing**)? A plan alone cannot tell these apart.

## 2. Design

- **Cells.** The 440 v0.10 blind cells (110 images × 4 arms). Same image, same
  domain block, same scenario block (ledger and totals line).
- **Manipulation.** Only the task block changes, from the plan request to one
  question. It is asked twice per cell, once in each polarity:
  - `prompts/probe_task_can.txt` (sha256 `8b9702f8…`): "Can the requirement be met
    by the deadline using only the assets in the ledger?"
  - `prompts/probe_task_short.txt` (sha256 `b4db6dae…`): "Will the assets in the
    ledger fall short of the requirement by the deadline?"
  - Both ask for YES or NO on the first line, then a one-sentence reason.
  - `tests/test_probe.py` asserts that the domain and scenario blocks are
    byte-identical to v0.10's, and that v0.10's digest is unchanged.
- **Decoding.** As v0.10: Qwen3-VL-8B-Instruct, float16, greedy, one draw
  per cell, but `max_new_tokens` is 64.
- **Not run.** The stated condition, sampling, and a no-totals variant.

## 3. Measures

- **Truth.** `ledger_satisfiable`, which the generator computes for each cell. No
  model is involved.
- **Reading** (`rcp/probe.py`). Take the first non-empty line and strip leading
  punctuation and markdown. If it starts with the word YES or NO (any case), that
  is the answer; otherwise the reading is unparsed. "Says short" is NO for the
  `can` wording and YES for the `short` wording.
- **Knows, k.** Per cell, the mean of its parsed readings (0, 0.5 or 1). The cell
  is missing if neither reading parses.
- **Acts, e.** Per cell, v0.10's ESCALATE flag (`results/ex_blind_all.jsonl`),
  checked by labels:
  - **Why.** On D11's 96 held-out plans, the extractor flags escalation on 6 of 48
    unsatisfiable cells where the labels find 2 (A) and 3 (B). It finds 1 of 48 on
    satisfiable cells, where the labels find 0. Unchecked, that would understate
    the gap.
  - **Sample** (`cal/v013/`, drawn by `probe_gap.py prepare`, seed 20261014). All
    36 extractor-positive blind cells, plus 9 extractor-negative cells per arm.
    The 72 rows are shuffled, and the sheet shows only the plan text as extraction
    scored it: no arm, ledger, flag or key.
  - **Labellers.** Two model labellers, A and B (two fresh instances of one
    language model). Each gets only `cal/d11/LABELLING.md` (its escalate rule)
    and `cal/v013/sheet.md`, and is blind to the extractor, the key, the probe and
    the other's labels. Labels are committed before any probe output is read.
  - **e under labels A or B.** A sampled cell takes that labeller's value; every
    other cell keeps the extractor's (all extractor-negative).

## 4. Primary test (one)

- **Contrasts.** For each image, knows K = mean k over SCARCE and INFEASIBLE
  minus mean k over SURPLUS and SUFFICIENT. Acts E is the same contrast for e.
- **Gap.** G = K − E, one value per complete-case image (k present in all four
  arms). Report the mean with a paired 95 % CI, normal approximation.
- **Verdict**, margin 0.20 (the study's δ, not re-tuned):
  - CI lower bound > 0.20: **GAP**. The model knows more than it acts on.
  - CI upper bound < 0.20: **NO GAP**.
  - Otherwise: **INCONCLUSIVE**.
- **Labellers.** The verdict is computed with e from labels A and from labels B.
  It stands only if both agree; otherwise it is **LABELLER-DEPENDENT**. G with the
  unchecked extractor flag is printed beside it and is not the primary.

## 5. Controls and halt rules

1. **Reproduction (halt).** In the same job and before the probe, regenerate
   v0.10's plans for the images in `cal/v013/repro_ids.txt` (3 images × 4 arms,
   seeded). All 12 must be byte-identical to v0.10's. If any differ, nothing is
   analysed and a deviation is recorded.
2. **Digest.** Every probe row must carry its wording's digest.
3. **Always printed.**
   - Per arm and wording: the parse rate, the share saying "short", and polarity
     agreement. "Short" on SURPLUS or SUFFICIENT is the false-alarm rate.
   - The complete-case n.
   - The extractor's ESCALATE against each label set, on positives and on
     negatives.

## 6. Power (`probe_gap.py power`)

- **Assumptions.** Worst case for the probe (k is 0 or 1 at p = .5 in every arm,
  SD of K 0.50), v0.10's acts SD (0.305), and the two terms independent.
- **Precision.** SE of G is 0.056, so the 95 % CI half-width is 0.109.
- **Power.**
  - 0.77 to find GAP if the true G is 0.35; 80 % at G = 0.357.
  - 0.77 to find NO GAP if the true G is 0.05.
- **Inconclusive band.** A true G between about 0.09 and 0.31 will usually be
  inconclusive.
- Positively correlated K and E, or a consistent probe, would narrow the CI.

## 7. Secondary (descriptive, no tests)

- K separately for each wording.
- On unsatisfiable cells, how often the plan escalates when the probe says
  "short" (k = 1) and when it says "enough" (k = 0).
- The one-sentence reasons: read only to describe failures, never scored.

## 8. What each outcome means

- **GAP.** The planner sees the shortfall but does not act on it in the plan.
  The next lever is task structure (e.g. assess feasibility, then plan), which
  is Track E (plan.md §1, §12.4), not more plan wording (D10, D12).
- **NO GAP, with K low.** It does not see the shortfall even with the total
  printed. Prompting this model is unlikely to help; use another model or a
  computed feasibility check.
- **NO GAP, with K high.** It knows and mostly acts, but E is small, so this
  would contradict v0.10. Check the reading rule and the labels before
  interpreting it.
- **"Short" high on SURPLUS/SUFFICIENT too.** This is pessimism, not knowing; K
  stays low and G does not count as a gap.
- **INCONCLUSIVE or LABELLER-DEPENDENT.** Report it as such. Settling it needs
  replicates or hand labels, not a re-analysis.

## 9. Limits, stated before the run

- **Asking is a cue.** "Knows" means "recognises the shortfall when asked
  directly". The question also names the deadline, which the plan prompt leaves
  to the planner (plan.md §7.2's trap), so K is an upper bound on what the
  planner sees while planning.
- **The totals line is printed.** The probe tests reading it, not adding up a
  ledger.
- **One draw.** A single greedy float16 draw per cell, as in v0.10 (the dtype
  question, D10, stays open).
- **The acts term is model-labelled**, not hand-labelled, on 72 of 440 cells.
  Missed escalations elsewhere are not corrected; on held-out they were 0–1 in 96.
- **The wording is fixed here.** There is no pilot on the 110 images and no
  revision. A changed wording would be a new version.

## 10. Run

```bash
python3 -m pytest -q                                     # must pass before submitting
sbatch --exclude=pleiades-1-3 jobs/probe_job.sh          # repro cells, then both wordings
python3 tools/runs.py freeze v013_probe --purpose "plan_v013.md probe" results/v013_probe
python3 tools/probe_gap.py report                        # -> results/v013_probe/report.txt
```

The run is registered as `v013_probe` and its code is tagged `run/v013_probe`.
The labels go in `cal/v013/labels_a.csv` and `labels_b.csv`.

## 11. Deviations

Append-only and dated. Anything changed after the tag goes here, with what
motivated it.

*None yet.*
