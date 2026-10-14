"""plan_v013.md's probe: the answer rule, the prompt, and the gap statistics."""

from __future__ import annotations

import pytest

from rcp import corpus
from rcp.probe import answer, knows, says_short
from rcp.render import TASKS, domain_block, domain_digest, planner_prompt, scenario_block, task_block
from tools.probe_gap import contrasts, verdict

#: v0.10's recorded digest (results/ex_blind_all.jsonl). The probe must not move it.
V010_BLIND = "22e9bbd8233453c71516fc07c7a901dc2df6968103a1676208b443189f063a2e"


@pytest.mark.parametrize("text,want", [
    ("YES\nThe on-scene total exceeds the requirement.", "yes"),
    ("no. Only 376 t is on scene.", "no"),
    ("**No**, the ledger falls short.", "no"),
    ("\n\n  Yes - two cranes suffice.", "yes"),
    ("Yes, but only if CRN-051 arrives.", "yes"),
    ("1. Deploy TUG-002 ...", None),
    ("The requirement cannot be met.\nNO", None),   # the first line decides
    ("Yesterday's survey ...", None),
    ("", None),
])
def test_answer_reads_only_the_first_non_empty_line(text, want):
    assert answer(text) == want


def test_the_two_wordings_have_opposite_short_answers():
    assert says_short("NO", "probe_can") is True
    assert says_short("YES", "probe_can") is False
    assert says_short("YES", "probe_short") is True
    assert says_short("NO", "probe_short") is False
    assert says_short("Unclear.", "probe_short") is None


def test_knows_averages_parsed_readings_only():
    assert knows([True, False]) == 0.5
    assert knows([True, None]) == 1.0
    assert knows([None, None]) is None


def test_the_study_digest_is_unchanged():
    assert domain_digest() == domain_digest("blind", "plan") == V010_BLIND


def test_probe_digests_differ_from_the_plan_and_each_other():
    ds = {domain_digest("blind", t) for t in TASKS}
    assert len(ds) == len(TASKS)


@pytest.mark.parametrize("task", ["probe_can", "probe_short"])
def test_a_probe_changes_only_the_task_block(task):
    """The manipulation is the task block: domain and scenario stay byte-identical."""
    for sc in list(corpus.by_key().values())[:40]:
        plan, probe = planner_prompt(sc), planner_prompt(sc, "blind", task)
        head = "\n\n".join([domain_block(), scenario_block(sc, "blind")])
        assert plan == head + "\n\n" + task_block()
        assert probe == head + "\n\n" + task_block(task)


def test_unknown_task_is_refused():
    with pytest.raises(ValueError):
        domain_digest("blind", "probe")


def test_contrast_is_unsatisfiable_mean_minus_satisfiable_mean():
    s = {"I/SURPLUS": 0.0, "I/SUFFICIENT": 1.0, "I/SCARCE": 1.0, "I/INFEASIBLE": 1.0}
    assert contrasts(s, {"I"}) == {"I": 0.5}


@pytest.mark.parametrize("lo,hi,start", [
    (0.21, 0.5, "GAP"), (-0.1, 0.19, "NO GAP"), (0.1, 0.3, "INCONCLUSIVE")])
def test_verdict_follows_the_ci_against_the_margin(lo, hi, start):
    assert verdict(lo, hi).startswith(start)
