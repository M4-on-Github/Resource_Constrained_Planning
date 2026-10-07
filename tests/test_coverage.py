"""The V5 coverage gate. plan.md sec. 8.4.

The gate's whole value is that it can come out non-zero. So the tests that matter
are the ones proving it *reports a miss* rather than absorbing it: a vocabulary that
cannot name a competent plan's goal step has to show up as a number, and an
uncovered casualty has to show up as uncovered rather than as a pass.

These tests build their own gold directories in `tmp_path` and never read
`controls/gold_plans/`, so the real gate's rate stays a measurement rather than
something a test suite has pinned.
"""

from __future__ import annotations

import pathlib

import pytest

from rcp.coverage import cell_of, gold_files, render, run, score_plan
from rcp.extract_det import goal_vocabulary


def write(d: pathlib.Path, name: str, text: str) -> pathlib.Path:
    d.mkdir(parents=True, exist_ok=True)
    p = d / name
    p.write_text(text, encoding="utf-8", newline="\n")
    return p


REAL_CELL = "AGR-00017_SUFFICIENT.txt"     # aground, in the frozen corpus


# --------------------------------------------------------------------------- #
# file naming
# --------------------------------------------------------------------------- #


def test_cell_of_splits_the_filename_into_scenario_and_arm():
    assert cell_of(pathlib.Path(REAL_CELL)) == ("AGR-00017", "SUFFICIENT")


def test_an_underscored_state_prefix_still_parses():
    """`ON_-00142` is a real scenario id. A naive split on `_` loses the arm."""
    assert cell_of(pathlib.Path("ON_-00142_SURPLUS.txt")) == ("ON_-00142", "SURPLUS")


def test_a_misnamed_file_is_rejected_rather_than_guessed():
    with pytest.raises(ValueError):
        cell_of(pathlib.Path("my_notes.txt"))


def test_notes_and_other_stray_files_are_not_treated_as_plans(tmp_path):
    write(tmp_path, "NOTES.md", "# notes")
    write(tmp_path, "scratch.txt", "nope")
    write(tmp_path, REAL_CELL, "1. Refloat her.")
    assert [p.name for p in gold_files(tmp_path)] == [REAL_CELL]


# --------------------------------------------------------------------------- #
# the measurement
# --------------------------------------------------------------------------- #


def test_a_plan_using_the_vocabulary_is_a_hit():
    phrase = goal_vocabulary("aground")[0]
    r = score_plan(f"1. Rig the gear.\n2. {phrase.capitalize()} on the tide.", "aground")
    assert r["goal_hit"] and r["matched"]


def test_a_plan_the_vocabulary_cannot_name_is_a_miss_not_a_failure():
    """This is the case the gate exists for. A competent plan that says the thing
    in words the domain does not hold is a defect in the domain, and the gate's job
    is to make that countable instead of letting it read as a planning failure."""
    r = score_plan("1. Rig the purchase and heave her seaward on the flood.", "aground")
    assert r["goal_hit"] is False
    assert r["steps"] == 1


def test_steps_are_counted_so_the_denominator_is_steps_not_plans():
    r = score_plan("1. One.\n2. Two.\n3. Three.", "aground")
    assert r["steps"] == 3


def test_the_vocabulary_under_test_is_reported_with_every_cell():
    """A miss is only actionable if the report says what the domain *did* hold."""
    assert score_plan("1. x", "aground")["vocabulary"] == list(goal_vocabulary("aground"))


# --------------------------------------------------------------------------- #
# the run
# --------------------------------------------------------------------------- #


def test_an_empty_gold_directory_reports_not_run_rather_than_zero(tmp_path):
    """A 0.0 % rate on no plans is the single most misleading number the gate
    could print: it looks like the best possible result."""
    rep = run(tmp_path)
    assert rep["n_plans"] == 0
    assert rep["no_match_rate"] is None
    assert "not run" in render(rep)


def test_the_rate_counts_misses_over_plans(tmp_path):
    write(tmp_path, REAL_CELL, "1. Heave her seaward on the flood.")
    write(tmp_path, "AGR-00018_SURPLUS.txt",
          f"1. {goal_vocabulary('aground')[0]} the vessel.")
    rep = run(tmp_path)
    assert (rep["n_plans"], rep["no_match"]) == (2, 1)
    assert rep["no_match_rate"] == 0.5


def test_a_miss_is_named_in_the_rendered_output(tmp_path):
    write(tmp_path, REAL_CELL, "1. Heave her seaward on the flood.")
    text = render(run(tmp_path))
    assert "AGR-00017/SUFFICIENT" in text
    assert "MISSES" in text
    assert "too narrow" in text        # the remedy, stated where the miss is


def test_uncovered_casualty_states_are_reported_as_untested(tmp_path):
    """A state no gold plan touches has an untested vocabulary. Silence there
    would read as four states passing when only one was measured."""
    write(tmp_path, REAL_CELL, "1. x")
    rep = run(tmp_path)
    assert set(rep["states_uncovered"]) == {"capsized", "on_fire", "sunken"}
    assert "NOT COVERED" in render(rep)


def test_a_gold_file_naming_a_cell_outside_the_corpus_is_flagged(tmp_path):
    write(tmp_path, "AGR-99999_SURPLUS.txt", "1. x")
    rep = run(tmp_path)
    assert rep["unknown_cells"] == ["AGR-99999/SURPLUS"]
    assert rep["n_plans"] == 0
    assert "WARNING" in render(rep)


def test_the_gate_never_fails_the_run(tmp_path):
    """sec. 8.4 pre-registers no threshold. Enforcing one here would invent a gate
    the plan did not declare, and would create the incentive to edit a gold plan."""
    from rcp.coverage import main
    write(tmp_path, REAL_CELL, "1. Heave her seaward on the flood.")
    assert main(["--gold", str(tmp_path)]) == 0


def test_render_is_ascii(tmp_path):
    write(tmp_path, REAL_CELL, "1. Heave her seaward on the flood.")
    assert [c for c in render(run(tmp_path)) if ord(c) > 127] == []
