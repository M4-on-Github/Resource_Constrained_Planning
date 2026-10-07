"""Extraction calibration. plan.md sec. 6.4.

Calibration is the only place a human's judgement enters the pipeline, so the
properties worth pinning are the ones that protect the labels: the sample must be
reproducible (a half-filled sheet has to keep lining up), a blank must never be
read as a "no", and a label that breaks the pipeline's own subset invariant must
stop the run rather than be scored.
"""

from __future__ import annotations

import csv

import pytest

from rcp.calibrate import _bool, _prf, _tokens, compare, render, stratify, write_sheet


def row(sid: str, arm: str, state: str = "aground", prose: str = "1. Pull.") -> dict:
    return {"scenario_id": sid, "arm": arm, "casualty_state": state, "prose": prose}


ROWS = [row(f"AGR-{i:05d}", arm, st)
        for i in range(12)
        for arm in ("SURPLUS", "SUFFICIENT", "SCARCE", "INFEASIBLE")
        for st in ("aground",)]


# --------------------------------------------------------------------------- #
# sampling
# --------------------------------------------------------------------------- #


def test_the_sample_is_deterministic():
    """The sheet is a physical artifact. If the sample moved between runs, the
    labels on a half-finished sheet would stop lining up with the plans."""
    assert stratify(ROWS) == stratify(ROWS)


def test_the_sample_is_balanced_across_arms():
    s = stratify(ROWS, per_stratum=3)
    counts: dict[str, int] = {}
    for r in s:
        counts[r["arm"]] = counts.get(r["arm"], 0) + 1
    assert set(counts.values()) == {3}


def test_a_thin_stratum_is_taken_whole_rather_than_padded():
    thin = ROWS + [row("CAP-00001", "SURPLUS", "capsized")]
    s = stratify(thin, per_stratum=4)
    assert sum(1 for r in s if r["casualty_state"] == "capsized") == 1


def test_the_sheet_carries_the_prose_beside_the_blank_columns(tmp_path):
    """Joining two files by hand is the commonest way a label set gets
    misaligned, so the labeller is never asked to."""
    dest = tmp_path / "labels_blank.csv"
    write_sheet(stratify(ROWS, per_stratum=2), dest)
    got = list(csv.DictReader(dest.open(encoding="utf-8")))
    assert got[0]["prose"] == "1. Pull."
    assert all(got[0][f] == "" for f in
               ("assets_named", "commitments", "goal_attempted", "escalate", "reduce"))


# --------------------------------------------------------------------------- #
# reading a sheet
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("cell", ["y", "Yes", "1", "TRUE", " true "])
def test_truthy_spellings_a_human_actually_writes(cell):
    assert _bool(cell, "x") is True


@pytest.mark.parametrize("cell", ["n", "No", "0", "false"])
def test_falsy_spellings(cell):
    assert _bool(cell, "x") is False


@pytest.mark.parametrize("cell", ["", "   ", "?", "maybe"])
def test_a_blank_is_not_a_label(cell):
    """An unlabelled row scored as False would silently turn a human's omission
    into a judgement, and it would bias every rate in the same direction."""
    with pytest.raises(ValueError):
        _bool(cell, "AGR-00001/SURPLUS goal_attempted")


def test_tokens_are_normalised_so_tug_001_matches_TUG001():
    assert _tokens("TUG-001; tug 001") == {"tug001"}


def test_tokens_of_a_blank_cell_is_the_empty_set():
    assert _tokens("") == set()


# --------------------------------------------------------------------------- #
# the metrics
# --------------------------------------------------------------------------- #


def test_empty_against_empty_is_agreement_not_zero():
    """A plan that named nothing, extracted as naming nothing, is the sec. 3.6
    vacuous case. Scoring it 0 would make the negative control look like an
    extraction failure."""
    assert _prf(set(), set())["f1"] == 1.0


def test_a_missed_asset_costs_recall_not_precision():
    r = _prf({"a", "b"}, {"a"})
    assert r["p"] == 1.0 and r["r"] == 0.5 and r["fn"] == 1


def test_an_invented_asset_costs_precision():
    r = _prf({"a"}, {"a", "b"})
    assert r["r"] == 1.0 and r["p"] == 0.5 and r["fp"] == 1


# --------------------------------------------------------------------------- #
# compare
# --------------------------------------------------------------------------- #


def label(sid="AGR-00017", arm="SURPLUS", named="", commits="",
          goal="yes", esc="no", red="no") -> dict:
    return {"scenario_id": sid, "arm": arm, "assets_named": named,
            "commitments": commits, "goal_attempted": goal,
            "escalate": esc, "reduce": red}


def extracted(sid="AGR-00017", arm="SURPLUS", named=(), commits=(),
              goal=True, esc=False, red=False) -> dict:
    return {"scenario_id": sid, "arm": arm, "assets_named": list(named),
            "commitments": list(commits), "goal_attempted": goal,
            "escalate": esc, "reduce": red}


def test_perfect_agreement_scores_one_everywhere():
    rep = compare([label(named="TUG-001", commits="TUG-001")],
                  {"AGR-00017/SURPLUS": extracted(named=["TUG-001"],
                                                  commits=["TUG-001"])})
    assert rep["sets"]["assets_named"]["f1"] == 1.0
    assert rep["bools"]["goal_attempted"]["agreement"] == 1.0


def test_a_disagreement_is_recorded_with_its_direction():
    rep = compare([label(goal="no")],
                  {"AGR-00017/SURPLUS": extracted(goal=True)})
    assert rep["bools"]["goal_attempted"]["false_pos"] == 1
    assert rep["bools"]["goal_attempted"]["false_neg"] == 0


def test_a_label_breaking_the_subset_invariant_halts_rather_than_scoring():
    """The pipeline enforces commitments subset assets_named in code, so a label
    that breaks it is a labelling error, not a finding about the extractor."""
    with pytest.raises(ValueError, match="labelling error"):
        compare([label(named="TUG-001", commits="TUG-002")],
                {"AGR-00017/SURPLUS": extracted()})


def test_a_labelled_row_with_no_extraction_is_reported_not_silently_dropped():
    rep = compare([label(sid="NOPE-00001")], {})
    assert rep["missing_from_extraction"] == ["NOPE-00001/SURPLUS"]
    assert rep["n_compared"] == 0


def test_render_is_ascii():
    rep = compare([label(named="TUG-001", commits="TUG-001")],
                  {"AGR-00017/SURPLUS": extracted(named=["TUG-001"],
                                                  commits=["TUG-001"])})
    assert [c for c in render(rep) if ord(c) > 127] == []
