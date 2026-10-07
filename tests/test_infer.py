"""The planner's batching and resume. plan.md sec. 7.1.

Nothing here touches a model. What is worth pinning is the two decisions that
decide whether an *interrupted* run is still analysable: the cell ordering and
what `--resume` counts as done.
"""

from __future__ import annotations

import json

from rcp.infer import ARMS, corpus, done_keys, image_path, key
from rcp.generator import manifest_images


def test_the_corpus_is_the_full_440_cells():
    assert len(corpus()) == 440


def test_cells_are_ordered_image_major():
    """So `--limit` yields complete images. A partial run ordered arm-major would
    have no complete-case images at all, and sec. 9.2's paired test would have
    nothing to pair."""
    cells = corpus()
    assert [c.arm for c in cells[:4]] == list(ARMS)
    assert cells[0].id == cells[3].id
    assert cells[4].id != cells[0].id


def test_limit_keeps_arms_complete():
    cells = corpus(limit=40)
    assert len(cells) == 40
    by_image: dict[str, set[str]] = {}
    for c in cells:
        by_image.setdefault(c.id, set()).add(c.arm)
    assert all(a == set(ARMS) for a in by_image.values())


def test_every_cell_has_an_image_on_the_manifest():
    images = manifest_images()
    assert {c.id for c in corpus()} <= set(images)


def test_image_path_joins_the_manifests_relative_path(tmp_path):
    sc = corpus(limit=4)[0]
    rel = manifest_images()[sc.id]
    assert image_path(sc, tmp_path, manifest_images()) == tmp_path / rel


def test_resume_counts_a_written_plan_as_done(tmp_path):
    out = tmp_path / "g.jsonl"
    out.write_text(json.dumps(
        {"scenario_id": "AGR-00017", "arm": "SURPLUS", "prose": "1. Do it."}) + "\n",
        encoding="utf-8")
    assert done_keys(out) == {"AGR-00017/SURPLUS"}


def test_resume_does_not_count_an_empty_generation_as_done(tmp_path):
    """An empty row is a failed cell, not a finished one. Treating it as done
    would bake a parse failure into the run that a rerun could have fixed."""
    out = tmp_path / "g.jsonl"
    out.write_text(json.dumps(
        {"scenario_id": "AGR-00017", "arm": "SURPLUS", "prose": "   "}) + "\n",
        encoding="utf-8")
    assert done_keys(out) == set()


def test_resume_survives_a_truncated_last_line(tmp_path):
    """A job killed mid-write leaves one. Dying on it would make the kill
    unrecoverable, which is the one thing resume exists to prevent."""
    out = tmp_path / "g.jsonl"
    out.write_text(
        json.dumps({"scenario_id": "A", "arm": "SURPLUS", "prose": "x"}) + "\n"
        + '{"scenario_id": "B", "ar',
        encoding="utf-8")
    assert done_keys(out) == {"A/SURPLUS"}


def test_resume_on_a_missing_file_is_empty(tmp_path):
    assert done_keys(tmp_path / "nope.jsonl") == set()


def test_key_is_the_join_key_used_everywhere_downstream():
    sc = corpus(limit=4)[0]
    assert key(sc) == f"{sc.id}/{sc.arm}"
