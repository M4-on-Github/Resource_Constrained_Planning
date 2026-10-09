"""tools/runs.py: a frozen run is checksummed, read-only, archived and verifiable."""

import importlib.util
import json
import os
import pathlib

import pytest

_spec = importlib.util.spec_from_file_location(
    "runs_tool", pathlib.Path(__file__).resolve().parent.parent / "tools" / "runs.py")
runs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(runs)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    (root / "runs").mkdir(parents=True)
    (root / "runs" / "README.md").write_text("| run |\n")
    (root / "results").mkdir()
    monkeypatch.setattr(runs, "REPO", root)
    monkeypatch.setattr(runs, "RUNS", root / "runs")
    monkeypatch.setattr(runs, "ARCHIVE", tmp_path / "archive")
    return root


def _gen(root):
    f = root / "results" / "gen.jsonl"
    f.write_text('{"prose": "1. Tow."}\n')
    (root / "results" / "gen.env.jsonl").write_text(
        json.dumps({"run_id": "slurm-1", "host": "n1", "packages": {"x": "1"}}) + "\n")
    return f


def test_freeze_records_checksums_and_jobs_and_makes_the_files_read_only(repo):
    f = _gen(repo)
    assert runs.main(["freeze", "r1", "--purpose", "test", str(repo / "results")]) == 0
    rec = json.loads((repo / "runs" / "r1.json").read_text())
    assert {x["path"] for x in rec["files"]} == {"results/gen.jsonl", "results/gen.env.jsonl"}
    assert rec["jobs"][0]["run_id"] == "slurm-1" and "packages" not in rec["jobs"][0]
    assert not os.access(str(f), os.W_OK)
    assert (runs.ARCHIVE / "r1" / "results" / "gen.jsonl").read_text() == f.read_text()
    assert "| `r1` |" in (repo / "runs" / "README.md").read_text()
    assert runs.main(["verify", "r1"]) == 0


def test_verify_fails_on_a_changed_file(repo):
    f = _gen(repo)
    runs.main(["freeze", "r1", "--purpose", "test", str(f)])
    os.chmod(str(f), 0o644)
    f.write_text("edited\n")
    assert runs.main(["verify", "r1"]) == 1


def test_a_name_and_a_file_are_registered_once(repo):
    f = _gen(repo)
    runs.main(["freeze", "r1", "--purpose", "test", str(f)])
    with pytest.raises(SystemExit):
        runs.main(["freeze", "r1", "--purpose", "again", str(repo / "results" / "gen.env.jsonl")])
    with pytest.raises(SystemExit):
        runs.main(["freeze", "r2", "--purpose", "again", str(f)])
