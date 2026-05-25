"""Targeted coverage for refactored library modules still below the 90% gate."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gates import regression_gate as rg
from lean.build_gate import main as build_gate_main
from manuscript.validation import ManuscriptValidationReport
from manuscript.validation_cli import _report_issues, _report_rendered_leaks, _report_status
from orchestration.build_pdf import (
    _as_mapping,
    _as_sequence,
    _extract_latex_preamble,
    _load_config,
    _metadata_args,
    _write_preamble_tex,
    regenerate_injected_manuscript,
)
from orchestration.build_pdf import (
    main as build_pdf_main,
)
from orchestration.run_all import StageResult, _run_parallel_batch, _run_serial, _spawn

PROJECT = Path(__file__).resolve().parent.parent.parent


def test_validation_cli_report_issues_prints_every_branch(capsys) -> None:
    report = ManuscriptValidationReport(
        section_files=["01_a.md"],
        missing_headings=["02_b.md"],
        empty_captions=["fig:empty"],
        undefined_tokens={"01_a.md": [("FIG", "missing")]},
        broken_links={"01_a.md": ["../nope.md"]},
        missing_figure_files={"01_a.md": ["../figures/x.png"]},
        out_of_range_variables={"k": "too high"},
        bad_section_refs={"01_a.md": ["§99"]},
        hardcoded_refs={"01_a.md": ["§5"]},
        hardcoded_numeric_literals={"01_a.md": ["42"]},
        hardcoded_rendered_source_fields={"01_a.md": ["labels.yaml"]},
        tokens_in_code_fences={"01_a.md": ["[[FIG:x]]"]},
        broken_lean_wiring={"thm_x": "missing lean decl"},
    )
    count = _report_issues(report)
    assert count == 12
    captured = capsys.readouterr().out
    assert "missing leading heading" in captured
    assert "four-track wiring" in captured


def test_validation_cli_rendered_leaks_and_status(tmp_path: Path, capsys) -> None:
    rendered = tmp_path / "output" / "manuscript"
    rendered.mkdir(parents=True)
    (rendered / "01_a.md").write_text("clean prose\n", encoding="utf-8")
    assert _report_rendered_leaks(rendered, project_root=tmp_path) == 0

    missing = tmp_path / "nope" / "manuscript"
    assert _report_rendered_leaks(missing, project_root=tmp_path) == 0
    assert "skipped" in capsys.readouterr().out

    assert _report_status(PROJECT) >= 0


def test_build_pdf_config_and_preamble_helpers(tmp_path: Path) -> None:
    ms = tmp_path / "manuscript"
    ms.mkdir()
    (ms / "config.yaml").write_text(
        "paper:\n  title: Title\n  subtitle: Sub\n  date: 2026-01-01\nauthors:\n  - name: Author\n",
        encoding="utf-8",
    )
    (ms / "preamble.md").write_text("% custom\n\\usepackage{x}\n", encoding="utf-8")
    assert _as_mapping({"a": 1})["a"] == 1
    assert _as_mapping("x") == {}
    assert list(_as_sequence([1, 2])) == [1, 2]
    assert _as_sequence("bad") == ()
    cfg = _load_config(ms)
    assert cfg["paper"]["title"] == "Title"
    args = _metadata_args(source_manuscript=ms, project_root=tmp_path)
    assert any("Title" in a for a in args)
    tex = _extract_latex_preamble("% line\n\\foo\n")
    assert "\\foo" in tex
    pre = tmp_path / "preamble.tex"
    _write_preamble_tex(source_manuscript=ms, preamble_tex=pre)
    assert "custom" in pre.read_text(encoding="utf-8")


def test_build_pdf_main_missing_manuscript(tmp_path: Path) -> None:
    assert build_pdf_main(project_root=tmp_path) != 0


def test_regenerate_injected_manuscript_fails_on_bad_script(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "manuscript_variables.py").write_text("raise SystemExit(3)\n", encoding="utf-8")
    code = regenerate_injected_manuscript(project_root=tmp_path)
    assert code == 3


def test_build_gate_main_missing_lean_dir(tmp_path: Path) -> None:
    assert build_gate_main(project_root=tmp_path) == 2


def test_run_all_spawn_serial_and_parallel(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    ok = scripts / "ok.py"
    ok.write_text("print('ok')\n", encoding="utf-8")
    res = _spawn("ok.py", capture=True, scripts_dir=scripts, project_root=tmp_path)
    assert isinstance(res, StageResult)
    assert res.returncode == 0
    assert "ok" in res.stdout
    assert _run_serial("ok.py", scripts_dir=scripts, project_root=tmp_path) == 0
    batch = _run_parallel_batch(["ok.py"], max_workers=1, scripts_dir=scripts, project_root=tmp_path)
    assert batch[0].returncode == 0


def test_regression_gate_parse_pytest_counts_errors_alias() -> None:
    counts = rg._parse_pytest_counts("==== 1 passed, 2 error in 0.1s ====")
    assert counts["errors"] == 2


def test_regression_gate_update_baseline_on_pass(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    reports = tmp_path / "output" / "reports"
    reports.mkdir(parents=True)
    baseline_path = tmp_path / "baseline.json"
    baseline_path.write_text(
        json.dumps(
            {
                "test_count_min": 5,
                "test_failed_max": 0,
                "coverage_percent_min": 85.0,
                "invariant_count_min": 2,
                "lean_lake_jobs_min": 0,
                "lean_sorry_max": 0,
                "lean_axiom_max": 0,
                "lean_unsafe_max": 0,
                "tolerance": {"test_count_drop_max": 0, "coverage_drop_pct_max": 2.0},
            }
        ),
        encoding="utf-8",
    )
    (reports / "test_results.json").write_text(
        json.dumps(
            {
                "pytest_returncode": 0,
                "summary": {"total_tests": 10, "total_failed": 0, "project_coverage": 92.0},
                "project": {"total": 10, "failed": 0, "coverage_percent": 92.0},
            }
        ),
        encoding="utf-8",
    )
    (reports / "dashboard_invariants.txt").write_text("summary:      3/3 passed, 0 failed\n", encoding="utf-8")
    (reports / "coverage.json").write_text(
        json.dumps(
            {
                "totals": {"percent_covered": 92.0},
                "files": {
                    "src/manuscript/status.py": {"summary": {"percent_covered": 96.0}},
                    "src/manuscript/pdf_validation.py": {"summary": {"percent_covered": 96.0}},
                    "src/visualizations/metadata.py": {"summary": {"percent_covered": 96.0}},
                    "src/simulation/parameter_sweep.py": {"summary": {"percent_covered": 96.0}},
                    "src/visualizations/btai_plots.py": {"summary": {"percent_covered": 96.0}},
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("REGRESSION_GATE_USE_EXISTING_TEST_REPORT", "1")
    monkeypatch.setattr(rg, "_lean_budget_snapshot", lambda **_: None)
    assert rg.gate(project_root=tmp_path, scripts_dir=tmp_path, baseline_path=baseline_path, update_baseline=True) == 0
    refreshed = json.loads(baseline_path.read_text(encoding="utf-8"))
    assert refreshed["test_count_min"] >= 10
    assert refreshed["coverage_percent_min"] >= 85.0
