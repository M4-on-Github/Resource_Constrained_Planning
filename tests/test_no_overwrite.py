"""No stage silently replaces a finished output (runs/README.md).

Each check runs before any input is read or any model loads, so these tests pass
dummy inputs: reaching the input would itself be the failure.
"""

from rcp import extract, infer, report


def test_extraction_refuses_an_existing_output(tmp_path):
    (tmp_path / "extracted.jsonl").write_text("kept\n")
    rc = extract.main(["--input", str(tmp_path / "missing.jsonl"),
                       "--out", str(tmp_path), "--no-llm"])
    assert rc == 1
    assert (tmp_path / "extracted.jsonl").read_text() == "kept\n"


def test_a_report_refuses_an_existing_output(tmp_path):
    (tmp_path / "report.txt").write_text("kept\n")
    rc = report.main(["--input", str(tmp_path / "missing.jsonl"), "--out", str(tmp_path)])
    assert rc == 1
    assert (tmp_path / "report.txt").read_text() == "kept\n"


def test_the_planner_refuses_an_existing_output_without_resume(tmp_path):
    out = tmp_path / "gen.jsonl"
    out.write_text("kept\n")
    rc = infer.main(["--images", str(tmp_path), "--out", str(out)])
    assert rc == 1
    assert out.read_text() == "kept\n"
