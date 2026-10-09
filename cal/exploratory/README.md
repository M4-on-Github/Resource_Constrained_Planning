# Exploratory run — calibration set, not results

The 220 plans from the v0.9 exploratory run (`docs/deviations.md` D0): Qwen3-VL-8B,
`SUFFICIENT` only, blind and stated, `max_new_tokens` 1024, written against the
**v0.9** ledgers. They are kept as the extraction calibration pool (plan.md §6.4),
never scored as study results and never pooled with the v0.10 run.

| file | what |
|---|---|
| `gen_SUFFICIENT_blind.jsonl`, `gen_SUFFICIENT_stated.jsonl` | the generations (no `ledger_hash`: they predate it) |
| `corpus_v09_sufficient.jsonl` + `.sha256` | the 110 v0.9 `SUFFICIENT` scenarios they were written against |

Extract them against their own ledgers, never the frozen v0.10 corpus (extraction
refuses that anyway):

```bash
python -m rcp.extract --input cal/exploratory/gen_SUFFICIENT_blind.jsonl \
    --out cal/exploratory/ex_blind \
    --corpus cal/exploratory/corpus_v09_sufficient.jsonl --allow-unhashed
```
