"""The frozen corpus. rcp/corpus.py, plan.md §7.1, §12.2.

Every stage after the generator reads data/corpus.jsonl and nothing else, so
these pin the three things that make that safe: the file is what data/ still
generates, its bytes match the recorded sha, and the per-row ledger hash that
extraction checks is a stable function of what the planner was shown.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json

import pytest

from rcp import corpus
from rcp.extract import check_ledger_hashes


def test_frozen_corpus_matches_regeneration():
    """If this fails, data/ or the generator moved after the freeze. Before the
    run: re-freeze. After it: revert, because the plans were written against the
    frozen ledgers."""
    assert corpus.drift() == []


def test_recorded_sha_matches_the_file():
    blob = corpus.CORPUS_FILE.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == corpus.recorded_sha()


def test_load_refuses_an_edited_corpus(tmp_path):
    p, sp = tmp_path / "c.jsonl", tmp_path / "c.sha256"
    corpus.write(corpus.load()[:4], p, sp)
    assert len(corpus.load(p, sp)) == 4
    p.write_bytes(p.read_bytes().replace(b'"SURPLUS"', b'"SCARCE"', 1))
    corpus._load.cache_clear()
    with pytest.raises(ValueError, match="does not match"):
        corpus.load(p, sp)


def test_round_trip_is_exact():
    for sc in corpus.load()[:40]:
        assert corpus.from_dict(json.loads(json.dumps(corpus.to_dict(sc)))) == sc


def test_ledger_hash_is_stable_and_sensitive():
    sc = corpus.load()[0]
    assert corpus.ledger_hash(sc) == corpus.ledger_hash(corpus.from_dict(corpus.to_dict(sc)))
    a = sc.ledger[0]
    moved = dataclasses.replace(sc, ledger=(dataclasses.replace(a, eta_hours=a.eta_hours + 0.1),)
                                + sc.ledger[1:])
    assert corpus.ledger_hash(moved) != corpus.ledger_hash(sc)


def test_ledger_hash_ignores_fields_the_planner_never_saw():
    sc = corpus.load()[0]
    assert corpus.ledger_hash(dataclasses.replace(sc, seed=sc.seed + 1)) == corpus.ledger_hash(sc)


def test_extraction_refuses_a_row_written_against_another_ledger():
    sc = corpus.load()[0]
    scenarios = {f"{sc.id}/{sc.arm}": sc}
    good = {"scenario_id": sc.id, "arm": sc.arm, "ledger_hash": corpus.ledger_hash(sc)}
    stale = {**good, "ledger_hash": "0" * 64}
    unhashed = {"scenario_id": sc.id, "arm": sc.arm}
    assert check_ledger_hashes([good], scenarios) == []
    assert check_ledger_hashes([stale], scenarios) == [f"{sc.id}/{sc.arm}"]
    assert check_ledger_hashes([unhashed], scenarios) == [f"{sc.id}/{sc.arm}"]
    assert check_ledger_hashes([unhashed], scenarios, allow_unhashed=True) == []
    assert check_ledger_hashes([stale], scenarios, allow_unhashed=True) != []
