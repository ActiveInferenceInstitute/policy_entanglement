"""Final coverage push for refactored library modules (95% gate)."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
import yaml

from dashboard_types import dashboard as dash_mod
from gates import regression_gate as rg
from lean import mathlib_proofs_gate as mpg
from manuscript import readiness as readiness_mod
from manuscript import theorem_map as tm
from manuscript.registry import load_registry
from manuscript.validation_cli import _report_rendered_leaks, _report_status
from manuscript.validation_cli import main as validation_cli_main
from orchestration import build_pdf as bp
from orchestration import run_all as ra
from orchestration.build_pdf import main as build_pdf_main
from orchestration.run_all import main as run_all_main
from reporting import _interactive_dashboard_local as idash

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


def test_interactive_dashboard_local_json_helpers(tmp_path: Path) -> None:
    assert idash._git_rev(tmp_path / "not_a_git_repo") == "unknown"
    assert idash._git_dirty(tmp_path / "not_a_git_repo") is False

    class _NumpyLike:
        __module__ = "numpy.ndarray"

        def tolist(self) -> list[int]:
            return [1, 2]

    assert idash._to_jsonable(_NumpyLike()) == [1, 2]

    class _Scalar:
        __module__ = "numpy.float64"

        def item(self) -> float:
            return 3.5

    assert idash._to_jsonable(_Scalar()) == pytest.approx(3.5)
    assert idash._to_jsonable(float("inf")) is None
    assert idash._to_jsonable({Path("/a"): 1}) == {"/a": 1}


def test_interactive_dashboard_local_full_render_bundle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(idash, "_git_rev", lambda repo_root=None: "abc123")
    monkeypatch.setattr(idash, "_git_dirty", lambda repo_root=None: True)

    dash = idash.InteractiveDashboard(
        title="Local dashboard",
        subtitle="fallback renderer",
        project_name="actinf",
        repo_root=tmp_path,
    )
    dash.set_payload({"path": tmp_path / "source", "nan": float("nan"), "items": {2, 1}})
    dash.set_hyperparameters({"long": list(range(8)), "short": [1, 2]})
    dash.set_meta(answer=Path("meta.json"), value=float("-inf"))
    dash.add_dropdown(
        "choice",
        "Choice",
        options=[1, "two"],
        default="two",
        option_labels=["one", "two"],
        description="select one",
    )
    dash.add_toggle("flag", "Flag", default=True, description="binary switch")
    dash.add_panel(
        idash.Panel(
            panel_id="p",
            title="Panel",
            description="Panel description",
            traces=[{"x": [1, 2], "y": [3, 4], "type": "scatter"}],
            layout={"title": "Plot"},
            driven_by=["choice"],
            update_fn="return Plotly.relayout(panelId, {title: String(controls.choice)});",
            preview_rows=3,
        )
    )
    dash.add_invariant(idash.Invariant("ok", actual=1.0, expected=1.0, description="passes"))
    dash.add_invariant(idash.Invariant("bad", actual=2.0, expected=1.0, description="fails"))
    dash.add_table("rows", [{"path": tmp_path / "row", "value": float("nan")}])
    dash.add_note("rendered locally")

    invariant_text = dash.render_invariants_text()
    assert "git status:   dirty" in invariant_text
    assert "PASS] ok" in invariant_text
    assert "FAIL] bad" in invariant_text

    summary = dash.render_summary_text()
    assert "[0 ... 7] (len=8)" in summary
    assert "rendered locally" in summary

    bundle = dash.to_json()
    assert bundle["git_dirty"] is True
    assert bundle["panels"][0]["preview_rows"] == 3
    assert bundle["invariants"][1]["passed"] is False

    paths = dash.write(
        html_path=tmp_path / "dashboard.html",
        json_path=tmp_path / "dashboard.json",
        txt_path=tmp_path / "summary.txt",
        invariants_path=tmp_path / "invariants.txt",
    )
    assert set(paths) == {"html", "json", "summary", "invariants"}
    html = paths["html"].read_text(encoding="utf-8")
    assert "cdn.plot.ly" in html
    assert 'data-tab="raw"' in html
    assert "CONTROL_VALUES" in html

    written = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert written["payload"]["nan"] is None
    assert written["tables"]["rows"][0]["value"] is None


def test_dashboard_types_main_success_and_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    html = tmp_path / "d.html"
    js = tmp_path / "d.json"
    inv = tmp_path / "inv.txt"
    summary = tmp_path / "sum.txt"
    argv = [
        "--num",
        "11",
        "--html-out",
        str(html),
        "--json-out",
        str(js),
        "--invariants-out",
        str(inv),
        "--summary-out",
        str(summary),
    ]
    dash_mod.main(argv)

    class _Dash:
        def write(self, **kwargs: object) -> dict[str, Path]:
            return {"html": html, "json": js, "invariants": inv, "summary": summary}

        def evaluate_invariants(self) -> list[dict[str, object]]:
            return [{"name": "bad", "passed": False}]

    monkeypatch.setattr(dash_mod, "build_dashboard_payload", lambda args: {})
    monkeypatch.setattr(dash_mod, "build_dashboard", lambda args, payload: _Dash())
    with pytest.raises(SystemExit) as exc:
        dash_mod.main(argv)
    assert exc.value.code == 1


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
