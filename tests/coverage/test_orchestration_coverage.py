"""Domain-scoped coverage meta-tests: orchestration, gates, readiness, cross-refs."""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest
import yaml

from gates import regression_gate as rg
from lean import mathlib_proofs_gate as mpg
from lean.build_gate import main as build_gate_main
from manuscript import readiness as readiness_mod
from manuscript import theorem_map as tm
from manuscript.registry import load_registry
from manuscript.validation import ManuscriptValidationReport
from manuscript.validation_cli import _report_issues, _report_rendered_leaks, _report_status
from manuscript.validation_cli import main as validation_cli_main
from orchestration import build_pdf as bp
from orchestration import run_all as ra
from orchestration.build_pdf import (
    _as_mapping,
    _as_sequence,
    _extract_latex_preamble,
    _load_config,
    _metadata_args,
    _write_preamble_tex,
    regenerate_injected_manuscript,
)
from orchestration.build_pdf import main as build_pdf_main
from orchestration.run_all import StageResult, _run_parallel_batch, _run_serial, _spawn
from orchestration.run_all import main as run_all_main

PROJECT = Path(__file__).resolve().parent.parent.parent

KEYSTONE_BODY = "\n".join(f"theorem {name} : True := trivial" for name in mpg.KEYSTONE_THEOREMS)


def _write_fake_lake_script(bin_dir: Path, *, build_rc: int = 0, build_out: str = "OK\n") -> None:
    bin_dir.mkdir(parents=True, exist_ok=True)
    script = bin_dir / "lake"
    escaped_out = build_out.replace("'", "'\"'\"'")
    script.write_text(
        """#!/bin/sh
if [ "$1" = "build" ]; then
  printf '%s' '"""
        + escaped_out
        + """'
  exit """
        + str(build_rc)
        + """
fi
if [ "$1" = "env" ] && [ "$2" = "lean" ]; then
  printf '%s\\n' \\
    "'MathlibProofs.streamMarginal_productDist' depends on axioms: [propext, Classical.choice, Quot.sound]" \\
    "'MathlibProofs.logDiv_prod_separates' depends on axioms: [propext, Classical.choice, Quot.sound]" \\
    "'MathlibProofs.klReal_nonneg' depends on axioms: [propext, Classical.choice, Quot.sound]" \\
    "'MathlibProofs.klReal_split_via_intermediate' depends on axioms: [propext, Classical.choice, Quot.sound]" \\
    "'MathlibProofs.klReal_minimises_generalK' depends on axioms: [propext, Classical.choice, Quot.sound]" \\
    "'MathlibProofs.entanglement_decomposition_generalK' depends on axioms: [propext, Classical.choice, Quot.sound]" \\
    "'MathlibProofs.free_energy_decomposition_full' depends on axioms: [propext, Classical.choice, Quot.sound]" \\
    "'MathlibProofs.streamMarginal_pos' depends on axioms: [propext, Classical.choice, Quot.sound]" \\
    "'MathlibProofs.multiInformation_nonneg_at_joint' depends on axioms: [propext, Classical.choice, Quot.sound]"
  exit 0
fi
exit 1
""",
        encoding="utf-8",
    )
    script.chmod(0o755)


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


PROJECT = Path(__file__).resolve().parent.parent.parent


def test_regression_gate_write_fresh_test_results_stub(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cov_path = tmp_path / "output" / "reports" / "coverage.json"
    test_path = tmp_path / "output" / "reports" / "test_results.json"
    log_path = tmp_path / "output" / "reports" / "pytest_regression_gate.log"
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_ok.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "__pycache__").mkdir()
    (tmp_path / "src" / "__pycache__" / "stale.pyc").write_bytes(b"x")

    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        cov_path.parent.mkdir(parents=True, exist_ok=True)
        cov_path.write_text(json.dumps({"totals": {"percent_covered": 96.0}, "files": {}}), encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0, stdout="1 passed in 0.01s\n", stderr="")

    monkeypatch.setattr(rg.subprocess, "run", fake_run)
    report = rg._write_fresh_test_results(
        project_root=tmp_path,
        test_results_path=test_path,
        pytest_log_path=log_path,
        coverage_json_path=cov_path,
    )
    assert report is not None
    assert report["project"]["coverage_percent"] == pytest.approx(96.0)
    assert test_path.exists()
    assert log_path.exists()


def test_regression_gate_write_fresh_test_results_pytest_fail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cov_path = tmp_path / "output" / "reports" / "coverage.json"
    test_path = tmp_path / "output" / "reports" / "test_results.json"
    log_path = tmp_path / "output" / "reports" / "pytest_regression_gate.log"
    (tmp_path / "tests").mkdir()

    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        cov_path.parent.mkdir(parents=True, exist_ok=True)
        cov_path.write_text(json.dumps({"totals": {"percent_covered": 50.0}}), encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 1, stdout="1 failed in 0.01s\n", stderr="boom\n")

    monkeypatch.setattr(rg.subprocess, "run", fake_run)
    report = rg._write_fresh_test_results(
        project_root=tmp_path,
        test_results_path=test_path,
        pytest_log_path=log_path,
        coverage_json_path=cov_path,
    )
    assert report is not None
    assert report["pytest_returncode"] == 1


def test_regression_gate_critical_coverage_and_invariants(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert rg._critical_module_coverage_issues(tmp_path / "missing.json") == [
        f"coverage JSON missing: {tmp_path / 'missing.json'}"
    ]
    bad = tmp_path / "bad.json"
    bad.write_text('{"files": "nope"}', encoding="utf-8")
    assert rg._critical_module_coverage_issues(bad) == ["coverage JSON has no files object"]

    inv = tmp_path / "output" / "reports" / "dashboard_invariants.txt"
    inv.parent.mkdir(parents=True, exist_ok=True)
    inv.write_text("summary:      2/5 passed, 3 failed\n", encoding="utf-8")
    assert rg._count_invariants(inv) == (2, 5)

    scripts = tmp_path / "scripts"
    scripts.mkdir()
    baseline = scripts / "regression_baseline.json"
    baseline.write_text(
        json.dumps(
            {
                "test_count_min": 1,
                "test_failed_max": 0,
                "coverage_percent_min": 80.0,
                "invariant_count_min": 10,
                "lean_lake_jobs_min": 0,
                "lean_sorry_max": 0,
                "lean_axiom_max": 0,
                "lean_unsafe_max": 0,
                "tolerance": {"test_count_drop_max": 0, "coverage_drop_pct_max": 1.0},
            }
        ),
        encoding="utf-8",
    )
    reports = inv.parent
    (reports / "test_results.json").write_text(
        json.dumps(
            {
                "pytest_returncode": 0,
                "summary": {"total_tests": 5, "total_failed": 0, "project_coverage": 95.0},
                "project": {"total": 5, "failed": 0, "coverage_percent": 95.0},
            }
        ),
        encoding="utf-8",
    )
    (reports / "coverage.json").write_text(
        json.dumps({"totals": {"percent_covered": 95.0}, "files": {}}), encoding="utf-8"
    )
    inv.write_text("summary:      2/5 passed, 3 failed\n", encoding="utf-8")
    monkeypatch.setenv("REGRESSION_GATE_USE_EXISTING_TEST_REPORT", "1")
    monkeypatch.setattr(
        rg, "_lean_budget_snapshot", lambda **_: {"lake_jobs": 5, "sorries": 0, "axioms": 0, "unsafe": 0}
    )
    assert rg.gate(project_root=tmp_path, scripts_dir=scripts, baseline_path=baseline) == 1


def test_regression_gate_unparseable_lake_jobs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    scripts = tmp_path / "scripts"
    reports = tmp_path / "output" / "reports"
    scripts.mkdir()
    reports.mkdir(parents=True)
    baseline = scripts / "regression_baseline.json"
    baseline.write_text(
        json.dumps(
            {
                "test_count_min": 1,
                "test_failed_max": 0,
                "coverage_percent_min": 80.0,
                "invariant_count_min": 0,
                "lean_lake_jobs_min": 5,
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
                "summary": {"total_tests": 5, "total_failed": 0, "project_coverage": 95.0},
                "project": {"total": 5, "failed": 0, "coverage_percent": 95.0},
            }
        ),
        encoding="utf-8",
    )
    (reports / "coverage.json").write_text(
        json.dumps({"totals": {"percent_covered": 95.0}, "files": {}}), encoding="utf-8"
    )
    (reports / "dashboard_invariants.txt").write_text("summary:      1/1 passed, 0 failed\n", encoding="utf-8")

    def _bad_jobs(**_kwargs: object) -> dict[str, int]:
        return {"lake_jobs": -1, "sorries": 0, "axioms": 0, "unsafe": 0}

    monkeypatch.setenv("REGRESSION_GATE_USE_EXISTING_TEST_REPORT", "1")
    monkeypatch.setattr(rg, "_lean_budget_snapshot", _bad_jobs)
    assert rg.gate(project_root=tmp_path, scripts_dir=scripts, baseline_path=baseline) == 1


def test_theorem_map_helpers_and_write() -> None:
    refs = PROJECT / "manuscript" / "refs"
    registry = load_registry(refs)
    thm = registry.labels.theorems["thm_4_1"]
    assert "THMREF" in tm._theorem_token(thm)
    assert "decomposition" in tm._python_link("thm_4_1")
    assert "test_decomposition" in tm._test_link("thm_4_1")
    assert "typed contract" in tm._python_link("thm_11_1")
    assert tm._test_link("missing_label_xyz") == "—"

    with_lean = registry.labels.theorems["thm_4_1"]
    assert "LEAN" in tm._theorem_token(with_lean)
    assert "ActinfPolicyEntanglement" in tm._lean_link(with_lean)

    md = tm.render(refs)
    assert "Per-theorem four-track" in md
    out = tm.write(PROJECT)
    assert out.exists()


def test_build_pdf_mirror_run_and_main_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bp._mirror_render_auxiliary_files(source_manuscript=tmp_path / "nope", injected_manuscript=tmp_path / "also_nope")
    assert bp._load_config(tmp_path / "empty") == {}

    log = tmp_path / "run.log"
    bp._run(["echo", "hi"], cwd=tmp_path, stdout_path=log)
    assert "hi" in log.read_text(encoding="utf-8")

    scripts = tmp_path / "scripts"
    scripts.mkdir()
    for name in ("manuscript_variables.py", "inject_manuscript_variables.py"):
        (scripts / name).write_text("import sys\nsys.exit(0)\n", encoding="utf-8")

    pdf_path = tmp_path / "output" / "pdf" / "actinf_policy_entanglement_lean_combined.pdf"

    def _good_render(**kwargs: object) -> Path:
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        pdf_path.write_bytes(b"%PDF")
        return pdf_path

    monkeypatch.setattr(bp, "render_combined_pdf", _good_render)
    assert build_pdf_main(project_root=tmp_path) == 0

    def _wrong_render(**kwargs: object) -> Path:
        other = tmp_path / "other.pdf"
        other.write_bytes(b"%PDF")
        return other

    monkeypatch.setattr(bp, "render_combined_pdf", _wrong_render)
    assert build_pdf_main(project_root=tmp_path) == 1

    def _boom(**kwargs: object) -> Path:
        raise RuntimeError("render failed")

    monkeypatch.setattr(bp, "render_combined_pdf", _boom)
    assert build_pdf_main(project_root=tmp_path) == 1


def test_run_all_manifest_large_file_and_parallel_stderr(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "a.py").write_text(
        "import sys\nprint('out', flush=True)\nprint('err', file=sys.stderr, flush=True)\n", encoding="utf-8"
    )
    out_dir = tmp_path / "output"
    out_dir.mkdir()
    (out_dir / "big.bin").write_bytes(b"x" * (ra._SHA256_MAX_BYTES + 1))

    manifest = ra._write_manifest(
        project_root=tmp_path,
        run_summary={"stages": [{"script": "a.py", "duration_s": 1.0, "returncode": 0}], "total_wall_s": 1.0},
    )
    text = manifest.read_text(encoding="utf-8")
    assert "(skipped: >8 MB)" in text

    monkeypatch.setattr(ra, "SCRIPTS", [("a.py", "a")])
    monkeypatch.setattr(ra, "PARALLEL_STAGE_STEMS", frozenset({"a"}))
    code = run_all_main(["--no-manifest"], project_root=tmp_path, scripts_dir=scripts)
    assert code == 0


def test_run_all_validator_break(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "validate_outputs.py").write_text("import sys\nsys.exit(2)\n", encoding="utf-8")
    monkeypatch.setattr(ra, "SCRIPTS", [("validate_outputs.py", "validate")])
    monkeypatch.setattr(ra, "PARALLEL_STAGE_STEMS", frozenset())
    assert (
        run_all_main(["--only", "validate_outputs", "--no-manifest"], project_root=tmp_path, scripts_dir=scripts) == 1
    )


def test_run_all_build_parser_pdf_mathlib_flags() -> None:
    args = ra.build_parser().parse_args(["--with-pdf", "--with-mathlib", "--only", "build_lean"])
    assert args.with_pdf is True
    assert args.with_mathlib is True


def test_readiness_figure_pdf_git_helpers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    counts = readiness_mod._status_counts([" R file", "?? x"])
    assert counts["other"] == 1

    _seed = tmp_path / "manuscript" / "refs"
    _seed.mkdir(parents=True)
    import shutil

    shutil.copy(PROJECT / "manuscript" / "refs" / "labels.yaml", _seed / "labels.yaml")

    fig = tmp_path / "output" / "figures" / "tiny.png"
    fig.parent.mkdir(parents=True)
    fig.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
        b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x01\x01\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    audit = readiness_mod._figure_audit(tmp_path, [fig])
    assert audit["pil_available"] is True
    assert audit["min_width_px"] == 1

    class _Status:
        tests_total = 1
        tests_passed = 1
        tests_skipped = 0
        tests_failed = 0
        test_summary = "ok"
        coverage_percent = 90.0
        pdf_pages = 1
        pdf_size_bytes = 10
        pdf_size_mb = 0.0
        pdf_summary = "1 page"

    pdf_audit = readiness_mod._pdf_artifact_audit(tmp_path, _Status())
    assert pdf_audit["exists"] is False

    def _bad_git(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(["git"], 1, stdout="", stderr="no repo")

    monkeypatch.setattr(readiness_mod.subprocess, "run", _bad_git)
    assert readiness_mod._git_status_lines(tmp_path) == ["(git status failed: no repo)"]


def test_validation_cli_rendered_leaks_and_status(tmp_path: Path) -> None:
    rendered = tmp_path / "output" / "manuscript"
    rendered.mkdir(parents=True)
    (rendered / "01_a.md").write_text("Unresolved [[FIG:missing]] token\n", encoding="utf-8")
    assert _report_rendered_leaks(rendered, project_root=tmp_path) >= 1

    outside = tmp_path / "elsewhere" / "manuscript"
    assert _report_rendered_leaks(outside, project_root=tmp_path) == 0

    assert _report_status(PROJECT) >= 0


def test_validation_cli_main_on_live_manuscript() -> None:
    assert validation_cli_main([], project_root=PROJECT) in (0, 1)


def test_pymdp_pipeline_main_stubbed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import visualizations.pymdp_figures as pf
    from simulation import pymdp_pipeline as pp
    from simulation.agents import pymdp_available

    if not pymdp_available():
        pytest.skip("pymdp not installed")

    def _path(name: str) -> Path:
        p = tmp_path / name
        p.write_text("x", encoding="utf-8")
        return p

    class _Logger:
        def fresh(self) -> None:
            return None

        def emit(self, _payload: object) -> None:
            return None

    monkeypatch.setattr(pf, "LOGGER", _Logger())
    monkeypatch.setattr(pf, "figure_pymdp_lambda_sweep", lambda: (_path("s.csv"), _path("c.png")))
    monkeypatch.setattr(pf, "figure_pymdp_rollout", lambda: _path("r.png"))
    monkeypatch.setattr(pf, "figure_pymdp_free_energies", lambda: (_path("f1.png"), _path("f2.png")))
    pp.main([])


def test_mathlib_proofs_gate_branches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mathlib_dir = tmp_path / "lean" / "MathlibProofs"
    mathlib_dir.mkdir(parents=True)
    (mathlib_dir / "lakefile.lean").write_text("-- lake\n", encoding="utf-8")
    (mathlib_dir / "MathlibProofs.lean").write_text(KEYSTONE_BODY + "\n", encoding="utf-8")

    bin_dir = tmp_path / "bin"
    _write_fake_lake_script(bin_dir, build_rc=2, build_out="fail\n")
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")
    assert mpg.run_mathlib_proofs_gate(tmp_path) == 2

    _write_fake_lake_script(bin_dir, build_out="warning: MathlibProofs.lean:1:1: unused\n")
    assert mpg.run_mathlib_proofs_gate(tmp_path) == 1

    _write_fake_lake_script(bin_dir, build_out="OK\n")
    assert mpg.run_mathlib_proofs_gate(tmp_path) == 0

    src = mathlib_dir / "MathlibProofs.lean"
    src.write_text("theorem streamMarginal_productDist : True := trivial\n", encoding="utf-8")
    assert any("expected keystone" in issue for issue in mpg.axiom_audit(mathlib_dir, src))


def test_axiom_audit_subprocess_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mathlib_dir = tmp_path / "lean" / "MathlibProofs"
    mathlib_dir.mkdir(parents=True)
    src = mathlib_dir / "MathlibProofs.lean"
    src.write_text(KEYSTONE_BODY + "\n", encoding="utf-8")

    def _bad_lean(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="lean broke")

    monkeypatch.setattr(mpg.subprocess, "run", _bad_lean)
    assert any("failed to run" in issue for issue in mpg.axiom_audit(mathlib_dir, src))


def test_theorem_map_no_lean_companion_branch() -> None:
    class _Thm:
        label = "demo"
        name = "Demo"
        kind = "theorem"
        number = "0.0"
        status = "witness"
        has_lean_companion = False
        lean_module = ""
        lean_name = ""

    assert tm._theorem_token(_Thm()) == "`[[THMREF:demo]]`"
    assert tm._lean_link(_Thm()) == "—"


def test_build_pdf_mirror_copies_bib_and_config(tmp_path: Path) -> None:
    src_ms = tmp_path / "manuscript"
    inj_ms = tmp_path / "output" / "manuscript"
    src_ms.mkdir(parents=True)
    inj_ms.mkdir(parents=True)
    (src_ms / "config.yaml").write_text("paper:\n  title: T\n", encoding="utf-8")
    (src_ms / "preamble.md").write_text("```latex\n\\foo\n```\n", encoding="utf-8")
    (src_ms / "refs.bib").write_text("@article{a}\n", encoding="utf-8")
    bp._mirror_render_auxiliary_files(source_manuscript=src_ms, injected_manuscript=inj_ms)
    assert (inj_ms / "config.yaml").exists()
    assert (inj_ms / "refs.bib").exists()


def test_metrics_half_saturation_branches() -> None:
    from simulation.metrics import half_saturation_interpolated

    assert half_saturation_interpolated([0.0, 1.0, 2.0], [0.5, 0.6, 0.6]) == pytest.approx((0.0, 0.5))
    assert half_saturation_interpolated([0.0, 1.0, 2.0], [0.0, 0.5, 0.5]) == pytest.approx((0.5, 0.25))
    assert half_saturation_interpolated([0.0, 1.0, 2.0], [0.0, 0.4, 0.8]) == pytest.approx((1.0, 0.4))


def test_trajectory_plot_rejects_empty_total_correlations(tmp_path: Path) -> None:
    import numpy as np

    from visualizations.trajectory_plots import plot_rollout_marginals

    with pytest.raises(ValueError, match="total_correlations"):
        plot_rollout_marginals(
            marginals_per_stream=[np.ones((2, 2))],
            titles=["A"],
            total_correlations=np.array([]),
            out_path=tmp_path / "out.png",
        )


def test_registry_facts_skips_non_dict_theorem_rows(tmp_path: Path) -> None:
    import shutil

    from manuscript.registry_facts import registry_structural_facts

    ms = tmp_path / "manuscript"
    refs = ms / "refs"
    refs.mkdir(parents=True)
    shutil.copy(PROJECT / "manuscript" / "refs" / "labels.yaml", refs / "labels.yaml")
    shutil.copy(PROJECT / "manuscript" / "refs" / "citations.yaml", refs / "citations.yaml")
    labels = yaml.safe_load((refs / "labels.yaml").read_text(encoding="utf-8"))
    labels["theorems"]["bad_row"] = "not-a-dict"
    (refs / "labels.yaml").write_text(yaml.dump(labels), encoding="utf-8")
    facts = registry_structural_facts(tmp_path)
    assert facts["theorem_registry_count"] >= 1


def test_regression_gate_coverage_fail_under_reads_pyproject() -> None:
    assert rg._coverage_fail_under(PROJECT) == pytest.approx(95.0)


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


def test_validation_cli_rendered_leaks_clean_and_skipped(tmp_path: Path, capsys) -> None:
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
    assert not any("normalsize" in a for a in args)
    assert not any("Sub" in a for a in args)
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
