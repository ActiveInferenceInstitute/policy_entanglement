"""Additional library-import tests targeting the 95% src/ coverage gate."""

from __future__ import annotations

import json
import os
import shutil
import stat
from pathlib import Path

import pytest

from gates import regression_gate as rg
from lean.build_gate import main as build_gate_main
from manuscript import readiness as readiness_mod
from orchestration import build_pdf as bp
from orchestration.run_all import main as run_all_main

PROJECT = Path(__file__).resolve().parent.parent.parent


def _seed_labels_yaml(project_root: Path) -> None:
    refs = project_root / "manuscript" / "refs"
    refs.mkdir(parents=True, exist_ok=True)
    shutil.copy(PROJECT / "manuscript" / "refs" / "labels.yaml", refs / "labels.yaml")


def _install_fake_lake(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bindir = tmp_path / "bin"
    bindir.mkdir()
    lake = bindir / "lake"
    lake.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    lake.chmod(lake.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{bindir}{os.pathsep}{os.environ.get('PATH', '')}")


def _seed_boundary_lean(tmp_path: Path, *, body: str) -> None:
    lean = tmp_path / "lean"
    pkg = lean / "ActinfPolicyEntanglement"
    pkg.mkdir(parents=True)
    (pkg / "Demo.lean").write_text(body, encoding="utf-8")
    (lean / "ActinfPolicyEntanglement.lean").write_text("import ActinfPolicyEntanglement.Demo\n", encoding="utf-8")


def test_build_gate_main_detects_disallowed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_lake(tmp_path, monkeypatch)
    _seed_boundary_lean(tmp_path, body="unsafe def bad : Nat := 0\n")
    assert build_gate_main(project_root=tmp_path) == 1


def test_build_gate_main_detects_sorry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_lake(tmp_path, monkeypatch)
    _seed_boundary_lean(tmp_path, body="theorem t : True := by sorry\n")
    assert build_gate_main(project_root=tmp_path) == 1


def test_build_gate_main_detects_axiom(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_lake(tmp_path, monkeypatch)
    _seed_boundary_lean(tmp_path, body="axiom cheat : True\n")
    assert build_gate_main(project_root=tmp_path) == 1


def test_build_gate_main_detects_mathlib_import(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_lake(tmp_path, monkeypatch)
    _seed_boundary_lean(tmp_path, body="import Mathlib.Data.Nat.Basic\n")
    assert build_gate_main(project_root=tmp_path) == 1


def test_build_gate_main_success_summary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _install_fake_lake(tmp_path, monkeypatch)
    _seed_boundary_lean(tmp_path, body="theorem t : True := trivial\n")
    assert build_gate_main(project_root=tmp_path) == 0
    out = capsys.readouterr().out
    assert "OK  lake build succeeded" in out


def test_regression_gate_lean_budget_snapshot_parses_script(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "build_lean.py").write_text(
        "#!/usr/bin/env python3\nprint('OK  lake build succeeded · 21 lake jobs · 0 sorries · 0 axioms · 0 unsafe')\n",
        encoding="utf-8",
    )
    snap = rg._lean_budget_snapshot(project_root=tmp_path, scripts_dir=scripts)
    assert snap == {"lake_jobs": 21, "sorries": 0, "axioms": 0, "unsafe": 0}


def test_regression_gate_lean_budget_snapshot_returns_none_on_failure(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "build_lean.py").write_text("import sys\nsys.exit(1)\n", encoding="utf-8")
    assert rg._lean_budget_snapshot(project_root=tmp_path, scripts_dir=scripts) is None


def test_regression_gate_gate_with_lean_snapshot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    reports = tmp_path / "output" / "reports"
    reports.mkdir(parents=True)
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    baseline = scripts / "regression_baseline.json"
    baseline.write_text(
        json.dumps(
            {
                "test_count_min": 1,
                "test_failed_max": 0,
                "coverage_percent_min": 80.0,
                "invariant_count_min": 1,
                "lean_lake_jobs_min": 10,
                "lean_sorry_max": 0,
                "lean_axiom_max": 0,
                "lean_unsafe_max": 0,
                "tolerance": {"test_count_drop_max": 0, "coverage_drop_pct_max": 1.0},
            }
        ),
        encoding="utf-8",
    )
    (scripts / "build_lean.py").write_text(
        "print('OK  lake build succeeded · 15 lake jobs · 0 sorries · 0 axioms · 0 unsafe')\n",
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
    (reports / "dashboard_invariants.txt").write_text("summary:      2/2 passed, 0 failed\n", encoding="utf-8")
    (reports / "coverage.json").write_text(
        json.dumps(
            {
                "totals": {"percent_covered": 95.0},
                "files": {
                    f"src/manuscript/{name}.py": {"summary": {"percent_covered": 96.0}}
                    for name in ("status", "pdf_validation")
                }
                | {"src/visualizations/metadata.py": {"summary": {"percent_covered": 96.0}}}
                | {"src/simulation/parameter_sweep.py": {"summary": {"percent_covered": 96.0}}}
                | {"src/visualizations/btai_plots.py": {"summary": {"percent_covered": 96.0}}},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("REGRESSION_GATE_USE_EXISTING_TEST_REPORT", "1")
    assert rg.gate(project_root=tmp_path, scripts_dir=scripts, baseline_path=baseline) == 0


def test_readiness_write_release_readiness_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    class _Status:
        tests_total = 10
        tests_passed = 10
        tests_skipped = 0
        tests_failed = 0
        test_summary = "10 collected; 10 passed + 0 skipped"
        coverage_percent = 95.0
        pdf_pages = 8
        pdf_size_bytes = 1000
        pdf_size_mb = 0.001
        pdf_summary = "8 pages, 0.00 MB"

    monkeypatch.setattr("manuscript.readiness.load_project_status", lambda _root: _Status())
    (tmp_path / "output" / "reports").mkdir(parents=True)
    (tmp_path / "manuscript").mkdir(parents=True)
    (tmp_path / "output" / "reports" / "test_results.json").write_text(
        json.dumps(
            {
                "project": {
                    "total": 10,
                    "passed": 10,
                    "skipped": 0,
                    "failed": 0,
                    "coverage_percent": 95.0,
                }
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "manuscript" / "config.yaml").write_text("paper:\n  title: t\n", encoding="utf-8")
    _seed_labels_yaml(tmp_path)
    path = readiness_mod.write_release_readiness(tmp_path)
    assert path.exists()
    assert "Release Readiness Report" in path.read_text(encoding="utf-8")


def test_build_pdf_main_success_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    for name in ("manuscript_variables.py", "inject_manuscript_variables.py"):
        (scripts / name).write_text("print('ok')\n", encoding="utf-8")

    ms = tmp_path / "manuscript"
    injected = tmp_path / "output" / "manuscript"
    for d in (ms, injected):
        d.mkdir(parents=True, exist_ok=True)
        (d / "preamble.md").write_text("```latex\n\\usepackage{x}\n```\n", encoding="utf-8")
        (d / "config.yaml").write_text("paper:\n  title: T\n", encoding="utf-8")
    (injected / "01_intro.md").write_text("# Intro\n", encoding="utf-8")

    def _fake_render(**kwargs: object) -> Path:
        root = kwargs["project_root"]
        assert isinstance(root, Path)
        pdf = root / "output" / "pdf" / "actinf_policy_entanglement_lean_combined.pdf"
        pdf.parent.mkdir(parents=True, exist_ok=True)
        pdf.write_bytes(b"%PDF")
        return pdf

    monkeypatch.setattr(bp, "regenerate_injected_manuscript", lambda **_: 0)
    monkeypatch.setattr(bp, "render_combined_pdf", _fake_render)
    assert bp.main(project_root=tmp_path) == 0


def test_run_all_inserts_pdf_and_mathlib_stages(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "build_lean.py").write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
    (scripts / "build_mathlib_proofs.py").write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
    (scripts / "build_pdf.py").write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
    (scripts / "validate_pdf.py").write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
    (scripts / "readiness_report.py").write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
    (scripts / "regression_gate.py").write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
    monkeypatch.setattr(
        "orchestration.run_all.SCRIPTS",
        [
            ("build_lean.py", "lean"),
            ("regression_gate.py", "gate"),
        ],
    )
    code = run_all_main(
        ["--with-pdf", "--with-mathlib", "--no-manifest"],
        project_root=tmp_path,
        scripts_dir=scripts,
    )
    assert code == 0


def test_run_all_validator_failure_stops_early(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "validate_manuscript.py").write_text("import sys\nsys.exit(3)\n", encoding="utf-8")
    monkeypatch.setattr(
        "orchestration.run_all.SCRIPTS",
        [("validate_manuscript.py", "validate")],
    )
    code = run_all_main(["--no-manifest"], project_root=tmp_path, scripts_dir=scripts)
    assert code == 1
