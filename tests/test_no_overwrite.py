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


def test_the_d11_sampler_refuses_an_existing_sample(tmp_path):
    import importlib.util
    import pathlib

    path = pathlib.Path(__file__).resolve().parent.parent / "tools" / "d11_sample.py"
    spec = importlib.util.spec_from_file_location("d11_sample", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    (tmp_path / "gen_sample.jsonl").write_text("kept\n")
    assert mod.main(["--out", str(tmp_path)]) == 1
    assert (tmp_path / "gen_sample.jsonl").read_text() == "kept\n"


def test_a_calibration_score_refuses_an_existing_output(tmp_path):
    from rcp import calibrate

    out = tmp_path / "score.json"
    out.write_text("kept\n")
    rc = calibrate.main(["score", "--labels", str(tmp_path / "missing.csv"),
                         "--extracted", str(tmp_path / "missing.jsonl"), "--out", str(out)])
    assert rc == 1
    assert out.read_text() == "kept\n"
