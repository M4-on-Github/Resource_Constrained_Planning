"""plan_v013b.md: the told line, the no-totals block, the new wordings, the dev ids."""

from __future__ import annotations

import pytest

from rcp import corpus
from rcp.probe import says_short, verdict_word
from rcp.render import (CONDITIONS, TASKS, domain_block, domain_digest, on_scene,
                        planner_prompt, scenario_block, task_block, told_line, totals_line)
from tools.v013b import CAL, REPRO_IMAGES, dev_images, no_totals_verdict, verdict

#: Digests the runs recorded (results/gen_*_{blind,stated}.jsonl, results/v013_probe/).
#: Adding conditions and wordings must not move any of them.
RECORDED = {
    ("blind", "plan"): "22e9bbd8233453c71516fc07c7a901dc2df6968103a1676208b443189f063a2e",
    ("stated", "plan"): "bb5bebf4732ddedd9a15128513131fcd70695fa8cca108294aab7b21518b0eb7",
    ("blind", "probe_can"): "11493b333d2e1f34c7bd23512b5be142cd59671eea9407ca31ea07336bab10fc",
    ("blind", "probe_short"): "77dfbd63a109e7a94cec5ccc8ee1bc31dcd7555c9b90bef2712b6ee427f17d30",
}


@pytest.fixture(scope="module")
def cells():
    return list(corpus.by_key().values())


def test_recorded_digests_are_unchanged():
    for (cond, task), d in RECORDED.items():
        assert domain_digest(cond, task) == d, (cond, task)


def test_every_condition_and_task_has_its_own_digest():
    ds = {domain_digest(c, t) for c in CONDITIONS for t in TASKS}
    assert len(ds) == len(CONDITIONS) * len(TASKS)


def test_the_told_line_agrees_with_ledger_satisfiable_on_every_cell(cells):
    for sc in cells:
        line = told_line(sc)
        assert ("cannot be met" in line) == (not sc.ledger_satisfiable), f"{sc.id}/{sc.arm}"
        assert ("can be met" in line) == sc.ledger_satisfiable


def test_the_told_line_figures_are_the_totals_lines(cells):
    for sc in cells[:40]:
        have = f"{on_scene(sc):g} {sc.requirement.unit}"
        assert f"On scene within {sc.requirement.deadline_h:.1f} h: {have}" in totals_line(sc)
        assert f", {have} against {sc.requirement.amount:g} {sc.requirement.unit}" in told_line(sc)
        gap = f"{abs(on_scene(sc) - sc.requirement.amount):g} {sc.requirement.unit}"
        assert f"short by {gap}." in told_line(sc) or f"{gap} to spare." in told_line(sc)


def test_told_adds_one_line_under_the_totals_and_nothing_else(cells):
    for sc in cells[:40]:
        blind, told = scenario_block(sc, "blind"), scenario_block(sc, "told")
        assert told == blind + "\n" + told_line(sc)


def test_no_totals_drops_the_totals_line_and_its_blank(cells):
    for sc in cells[:40]:
        blind, bare = scenario_block(sc, "blind"), scenario_block(sc, "no_totals")
        assert blind == bare + "\n\n" + totals_line(sc)
        assert "On scene within" not in bare and "Full fleet" not in bare


@pytest.mark.parametrize("cond", ["told", "no_totals"])
def test_the_new_conditions_keep_the_constant_halves(cells, cond):
    for sc in cells[:40]:
        for task in TASKS:
            assert planner_prompt(sc, cond, task) == "\n\n".join(
                [domain_block(), scenario_block(sc, cond), task_block(task)])


@pytest.mark.parametrize("text,want", [
    ("On scene 170 t; required 340 t.\nINFEASIBLE", "infeasible"),
    ("418 t against 340 t.\n**FEASIBLE**", "feasible"),
    ("x\n  Feasible.  \n\n", "feasible"),
    ("INFEASIBLE\nbecause 170 t < 340 t", None),      # the last line decides
    ("x\nVerdict: INFEASIBLE", None),
    ("x\nNOT FEASIBLE", None),
    ("On scene 170 t; required", None),                # cut off at the token cap
    ("", None),
])
def test_feasible_reads_only_the_last_non_empty_line(text, want):
    assert verdict_word(text) == want


def test_each_new_wording_knows_which_answer_says_short():
    assert says_short("NO\nx", "probe_enough") is True
    assert says_short("YES\nx", "probe_enough") is False
    assert says_short("YES\nx", "probe_request") is True
    assert says_short("NO\nx", "probe_request") is False
    assert says_short("x\nINFEASIBLE", "probe_feasible") is True
    assert says_short("x\nFEASIBLE", "probe_feasible") is False
    assert says_short("YES", "probe_feasible") is None


def test_dev_ids_are_the_track_e_dev_split():
    ids = (CAL / "dev_ids.txt").read_text(encoding="utf-8").split()
    assert ids == dev_images() and len(ids) == 40
    repro = (CAL / "repro_ids.txt").read_text(encoding="utf-8").split()
    assert len(repro) == REPRO_IMAGES and set(repro) <= set(ids)


@pytest.mark.parametrize("lo,hi,want", [
    (0.51, 0.8, "ACTS WHEN TOLD"), (-0.05, 0.19, "DOES NOT ACT WHEN TOLD"),
    (0.3, 0.6, "IN BETWEEN"), (0.1, 0.3, "IN BETWEEN")])
def test_told_verdict_follows_the_ci_against_the_two_bars(lo, hi, want):
    assert verdict(lo, hi) == want


@pytest.mark.parametrize("lo,hi,want", [
    (-0.6, -0.21, "COLLAPSES"), (-0.19, 0.1, "HOLDS"), (-0.3, -0.1, "UNCLEAR")])
def test_no_totals_verdict_against_the_margin(lo, hi, want):
    assert no_totals_verdict(lo, hi) == want
