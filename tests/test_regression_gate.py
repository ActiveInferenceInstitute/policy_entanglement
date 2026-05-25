"""Unit tests for regression-gate helper logic."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from gates import regression_gate as rg

PROJECT = Path(__file__).resolve().parent.parent
SCRIPT = PROJECT / "scripts" / "regression_gate.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("regression_gate", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_parse_pytest_counts_handles_all_summary_kinds() -> None:
    mod = _load_module()
    counts = mod._parse_pytest_counts(
        "noise\n==== 10 passed, 1 failed, 2 skipped, 1 xfailed, 1 xpassed in 1.23s ====\n"
    )
    assert counts["passed"] == 10
    assert counts["failed"] == 1
    assert counts["skipped"] == 2
    assert counts["xfailed"] == 1
    assert counts["xpassed"] == 1


def test_critical_module_coverage_issues_detect_missing_and_low_modules(tmp_path: Path) -> None:
    mod = _load_module()
    coverage = tmp_path / "coverage.json"
    coverage.write_text(
        json.dumps(
            {
                "files": {
                    "src/manuscript/status.py": {"summary": {"percent_covered": 96.0}},
                    "src/manuscript/pdf_validation.py": {"summary": {"percent_covered": 94.99}},
                }
            }
        ),
        encoding="utf-8",
    )

    issues = mod._critical_module_coverage_issues(
        coverage,
        {
            "src/manuscript/status.py": 95.0,
            "src/manuscript/pdf_validation.py": 95.0,
            "src/visualizations/metadata.py": 95.0,
        },
    )

    assert "src/manuscript/pdf_validation.py: coverage 94.99% < floor 95.00%" in issues
    assert "src/visualizations/metadata.py: missing from coverage JSON" in issues


def test_critical_module_coverage_issues_passes_when_all_floors_met(tmp_path: Path) -> None:
    mod = _load_module()
    coverage = tmp_path / "coverage.json"
    coverage.write_text(
        json.dumps(
            {
                "files": {
                    "a.py": {"summary": {"percent_covered": 95.0}},
                    "b.py": {"summary": {"percent_covered": 100.0}},
                }
            }
        ),
        encoding="utf-8",
    )
    assert mod._critical_module_coverage_issues(coverage, {"a.py": 95.0, "b.py": 95.0}) == []


def test_critical_module_coverage_issues_reports_malformed_json_shape(tmp_path: Path) -> None:
    mod = _load_module()
    missing = tmp_path / "missing.json"
    assert mod._critical_module_coverage_issues(missing, {"a.py": 95.0}) == [f"coverage JSON missing: {missing}"]

    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"files": []}), encoding="utf-8")
    assert mod._critical_module_coverage_issues(bad, {"a.py": 95.0}) == ["coverage JSON has no files object"]

    no_summary = tmp_path / "no_summary.json"
    no_summary.write_text(json.dumps({"files": {"a.py": {}}}), encoding="utf-8")
    assert mod._critical_module_coverage_issues(no_summary, {"a.py": 95.0}) == ["a.py: missing coverage summary"]


def test_regression_gate_library_helpers(tmp_path: Path) -> None:
    inv = tmp_path / "dashboard_invariants.txt"
    inv.write_text("summary:      3/3 passed, 0 failed\n", encoding="utf-8")
    assert rg._count_invariants(inv) == (3, 3)

    cov = tmp_path / "coverage.json"
    cov.write_text(json.dumps({"totals": {"percent_covered": 91.5}}), encoding="utf-8")
    assert rg._coverage_percent_from_json(cov) == pytest.approx(91.5)

    cache = tmp_path / "pkg"
    cache.mkdir()
    pycache = cache / "__pycache__"
    pycache.mkdir()
    (pycache / "mod.pyc").write_bytes(b"x")
    assert rg._clear_bytecode_cache(tmp_path) >= 1


def test_regression_gate_uses_existing_report_when_env_set(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    reports = tmp_path / "output" / "reports"
    reports.mkdir(parents=True)
    baseline = tmp_path / "baseline.json"
    baseline.write_text(
        json.dumps(
            {
                "test_count_min": 1,
                "test_failed_max": 0,
                "coverage_percent_min": 80.0,
                "invariant_count_min": 1,
                "lean_lake_jobs_min": 0,
                "lean_sorry_max": 0,
                "lean_axiom_max": 0,
                "lean_unsafe_max": 0,
                "tolerance": {"test_count_drop_max": 0, "coverage_drop_pct_max": 1.0},
            }
        ),
        encoding="utf-8",
    )
    (reports / "test_results.json").write_text(
        json.dumps(
            {
                "pytest_returncode": 0,
                "summary": {"total_tests": 10, "total_failed": 0, "project_coverage": 90.0},
                "project": {"total": 10, "failed": 0, "coverage_percent": 90.0},
            }
        ),
        encoding="utf-8",
    )
    (reports / "dashboard_invariants.txt").write_text("summary:      2/2 passed, 0 failed\n", encoding="utf-8")
    (reports / "coverage.json").write_text(
        json.dumps(
            {
                "totals": {"percent_covered": 90.0},
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
    code = rg.gate(project_root=tmp_path, scripts_dir=tmp_path, baseline_path=baseline)
    assert code == 0


def test_regression_gate_fails_on_test_regression(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    reports = tmp_path / "output" / "reports"
    reports.mkdir(parents=True)
    baseline = tmp_path / "baseline.json"
    baseline.write_text(
        json.dumps(
            {
                "test_count_min": 100,
                "test_failed_max": 0,
                "coverage_percent_min": 95.0,
                "invariant_count_min": 1,
                "lean_lake_jobs_min": 0,
                "lean_sorry_max": 0,
                "lean_axiom_max": 0,
                "lean_unsafe_max": 0,
                "tolerance": {"test_count_drop_max": 0, "coverage_drop_pct_max": 0.5},
            }
        ),
        encoding="utf-8",
    )
    (reports / "test_results.json").write_text(
        json.dumps(
            {
                "pytest_returncode": 0,
                "summary": {"total_tests": 50, "total_failed": 0, "project_coverage": 94.0},
                "project": {"total": 50, "failed": 0, "coverage_percent": 94.0},
            }
        ),
        encoding="utf-8",
    )
    (reports / "dashboard_invariants.txt").write_text("summary:      1/1 passed, 0 failed\n", encoding="utf-8")
    (reports / "coverage.json").write_text(
        json.dumps({"totals": {"percent_covered": 94.0}, "files": {}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("REGRESSION_GATE_USE_EXISTING_TEST_REPORT", "1")
    monkeypatch.setattr(rg, "_lean_budget_snapshot", lambda **_: None)
    assert rg.gate(project_root=tmp_path, scripts_dir=tmp_path, baseline_path=baseline) == 1


def test_count_invariants_returns_none_for_missing_file(tmp_path: Path) -> None:
    assert rg._count_invariants(tmp_path / "missing.txt") is None


def test_regression_gate_fails_closed_on_missing_invariant_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    reports = tmp_path / "output" / "reports"
    reports.mkdir(parents=True)
    baseline = tmp_path / "baseline.json"
    baseline.write_text(
        json.dumps(
            {
                "test_count_min": 1,
                "test_failed_max": 0,
                "coverage_percent_min": 80.0,
                "invariant_count_min": 1,
                "lean_lake_jobs_min": 0,
                "lean_sorry_max": 0,
                "lean_axiom_max": 0,
                "lean_unsafe_max": 0,
                "tolerance": {"test_count_drop_max": 0, "coverage_drop_pct_max": 1.0},
            }
        ),
        encoding="utf-8",
    )
    (reports / "test_results.json").write_text(
        json.dumps(
            {
                "pytest_returncode": 0,
                "summary": {"total_tests": 10, "total_failed": 0, "project_coverage": 90.0},
                "project": {"total": 10, "failed": 0, "coverage_percent": 90.0},
            }
        ),
        encoding="utf-8",
    )
    (reports / "coverage.json").write_text(
        json.dumps(
            {
                "totals": {"percent_covered": 90.0},
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
    monkeypatch.setattr(
        rg, "_lean_budget_snapshot", lambda **_: {"lake_jobs": 5, "sorries": 0, "axioms": 0, "unsafe": 0}
    )
    assert rg.gate(project_root=tmp_path, scripts_dir=tmp_path, baseline_path=baseline) == 1


def test_load_baseline_and_test_results(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.json"
    baseline.write_text('{"test_count_min": 1}\n', encoding="utf-8")
    loaded = rg._load_baseline(baseline)
    assert loaded["test_count_min"] == 1
    missing = rg._load_test_results(tmp_path / "nope.json")
    assert missing is None


def test_regression_gate_fails_on_lean_sorry_regression(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    reports = tmp_path / "output" / "reports"
    scripts = tmp_path / "scripts"
    reports.mkdir(parents=True)
    scripts.mkdir()
    baseline = scripts / "regression_baseline.json"
    baseline.write_text(
        json.dumps(
            {
                "test_count_min": 1,
                "test_failed_max": 0,
                "coverage_percent_min": 80.0,
                "invariant_count_min": 0,
                "lean_lake_jobs_min": 0,
                "lean_sorry_max": 0,
                "lean_axiom_max": 0,
                "lean_unsafe_max": 0,
                "tolerance": {"test_count_drop_max": 0, "coverage_drop_pct_max": 1.0},
            }
        ),
        encoding="utf-8",
    )
    (reports / "test_results.json").write_text(
        json.dumps(
            {
                "pytest_returncode": 0,
                "summary": {"total_tests": 10, "total_failed": 0, "project_coverage": 95.0},
                "project": {"total": 10, "failed": 0, "coverage_percent": 95.0},
            }
        ),
        encoding="utf-8",
    )
    (reports / "coverage.json").write_text(
        json.dumps({"totals": {"percent_covered": 95.0}, "files": {}}),
        encoding="utf-8",
    )
    (reports / "dashboard_invariants.txt").write_text("summary:      1/1 passed, 0 failed\n", encoding="utf-8")

    def _bad_lean(**_kwargs: object) -> dict[str, int]:
        return {"lake_jobs": 10, "sorries": 1, "axioms": 0, "unsafe": 0}

    monkeypatch.setenv("REGRESSION_GATE_USE_EXISTING_TEST_REPORT", "1")
    monkeypatch.setattr(rg, "_lean_budget_snapshot", _bad_lean)
    assert rg.gate(project_root=tmp_path, scripts_dir=scripts, baseline_path=baseline) == 1
