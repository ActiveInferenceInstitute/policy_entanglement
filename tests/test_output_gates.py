"""Tests for release output validation gates."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from manuscript import output_gates
from manuscript.output_gates import artifact_validators, csv_helpers, png_validation, pymdp_validators
from tests.output_gates_helpers import patch_output_dir as _patch_output_dir
from manuscript.output_gates.constants import REQUIRED_VARIABLES
from simulation import hyperparameters as H

PROJECT = Path(__file__).resolve().parent.parent
FIG_DIR = PROJECT / "output" / "figures"
SIM_DIR = PROJECT / "output" / "simulations"
DATA_DIR = PROJECT / "output" / "data"


VALIDATOR_FUNCS = (
    artifact_validators.validate_figures,
    artifact_validators.validate_variables,
    pymdp_validators.validate_sweep,
    pymdp_validators.validate_free_energy_bundle,
    pymdp_validators.validate_multi_k_sweep,
    pymdp_validators.validate_long_horizon,
    pymdp_validators.validate_revertibility,
    pymdp_validators.validate_robustness_suite,
    pymdp_validators.validate_coupling_ablation,
    pymdp_validators.validate_marginal_null_control,
    pymdp_validators.validate_interaction_robustness,
    pymdp_validators.validate_long_horizon_replicates,
    pymdp_validators.validate_long_horizon_seed_diagnostics,
    pymdp_validators.validate_long_horizon_threshold_sensitivity,
    pymdp_validators.validate_run_log,
)


def _write_fake_png(path: Path, *, header: bytes | None = None, body: bytes = b"\x00") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((header or output_gates.PNG_HEADER) + body)


def _minimal_variables_payload() -> dict[str, object]:
    payload: dict[str, object] = {}
    for key, (lo, hi) in REQUIRED_VARIABLES.items():
        payload[key] = (lo + hi) / 2.0
    for k in (2, 3, 4, 5):
        payload[f"tt_ranks_K{k}"] = [2] * (k - 1)
    return payload


def test_output_gate_constants_exposed() -> None:
    assert output_gates.PNG_HEADER == b"\x89PNG\r\n\x1a\n"
    assert output_gates.MIN_TICK_FONT_SIZE >= 12.0
    assert "ising_mi_curve.png" in output_gates.REQUIRED_FIGURES


def test_registry_structural_count_gates_delegate() -> None:
    gates = output_gates._registry_structural_count_gates()
    assert "theorem_registry_count" in gates
    low, high = gates["theorem_registry_count"]
    assert low == high


def test_check_png_missing_and_blank_and_bad_header(tmp_path: Path) -> None:
    missing = tmp_path / "missing.png"
    assert png_validation.check_png(missing) == 1
    assert png_validation.check_png(missing, optional=True) == 0

    blank = tmp_path / "blank.png"
    _write_fake_png(blank, body=b"")
    assert png_validation.check_png(blank) == 1

    not_png = tmp_path / "not_png.png"
    _write_fake_png(not_png, header=b"NOTPNG!!")
    assert png_validation.check_png(not_png) == 1


def test_check_png_semantic_metadata_rejects_stale_theorem(tmp_path: Path) -> None:
    path = tmp_path / "meta.png"
    stale_label = f"Theorem {6}.{4}"
    info = {
        "project.uncertainty_semantics": "deterministic_grid",
        "project.figure_statistics": json.dumps(
            {
                "schema_version": 2,
                "axes_count": 1,
                "axes": [{"title": stale_label}],
                "figure_size_inches": [6.0, 4.0],
                "figure_texts": [],
            }
        ),
        "project.hyperparameters": json.dumps({}),
    }
    failures = png_validation.check_png_semantic_metadata(path, info)
    assert failures >= 1


def test_validate_variables_missing_and_out_of_range(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "output" / "data"
    out.mkdir(parents=True)
    _patch_output_dir(monkeypatch, tmp_path)

    assert artifact_validators.validate_variables() == 1

    bad = out / "manuscript_variables.json"
    payload = _minimal_variables_payload()
    first_key = next(iter(REQUIRED_VARIABLES))
    lo, hi = REQUIRED_VARIABLES[first_key]
    payload[first_key] = hi + 1.0
    bad.write_text(json.dumps(payload), encoding="utf-8")
    rc = artifact_validators.validate_variables()
    assert rc >= 1


def test_optional_validators_absent_artifacts_return_zero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_output_dir(monkeypatch, tmp_path)
    assert pymdp_validators.validate_sweep() == 0
    assert pymdp_validators.validate_free_energy_bundle() == 0
    assert pymdp_validators.validate_run_log() == 0


def test_validate_run_log_malformed_jsonl(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    logs = tmp_path / "output" / "logs"
    logs.mkdir(parents=True)
    (logs / "pymdp_runs.jsonl").write_text("{not json}\n", encoding="utf-8")
    _patch_output_dir(monkeypatch, tmp_path)
    rc = pymdp_validators.validate_run_log()
    captured = capsys.readouterr()
    assert rc >= 1
    assert "malformed JSONL" in captured.err


def test_csv_helpers_grid_and_read_paths(tmp_path: Path) -> None:
    grid = H.PYMDP_SWEEP_LAMBDAS
    rows = [{"lambda": str(v)} for v in grid.values()]
    assert csv_helpers.grid_values(grid) == [float(v) for v in grid.values()]
    assert csv_helpers.rows_match_grid(rows, grid, label="test-grid") == 0

    bad_rows = [{"lambda": "999.0"}]
    assert csv_helpers.rows_match_grid(bad_rows, grid, label="bad-grid") >= 1

    missing_cols = tmp_path / "bad.csv"
    missing_cols.write_text("lambda\n0.0\n", encoding="utf-8")
    _, fail = csv_helpers.read_csv_rows(missing_cols, {"lambda", "total_correlation"})
    assert fail == 1

    absent = tmp_path / "absent.csv"
    rows_out, fail = csv_helpers.read_csv_rows(absent, {"lambda"})
    assert rows_out == []
    assert fail == 0


def test_validate_variables_passes_minimal_sidecar(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "output" / "data"
    out.mkdir(parents=True)
    (out / "manuscript_variables.json").write_text(
        json.dumps(_minimal_variables_payload()),
        encoding="utf-8",
    )
    _patch_output_dir(monkeypatch, tmp_path)
    assert artifact_validators.validate_variables() == 0


def test_validate_variables_rejects_invalid_json_and_tt_ranks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _patch_output_dir(monkeypatch, tmp_path)
    data = out / "data"
    data.mkdir(parents=True)
    (data / "manuscript_variables.json").write_text("{not json", encoding="utf-8")
    assert artifact_validators.validate_variables() == 1

    payload = _minimal_variables_payload()
    payload["ising_mi_at_lam_05"] = "not-run"
    (data / "manuscript_variables.json").write_text(json.dumps(payload), encoding="utf-8")
    assert artifact_validators.validate_variables() >= 1

    payload = _minimal_variables_payload()
    del payload[next(iter(REQUIRED_VARIABLES))]
    (data / "manuscript_variables.json").write_text(json.dumps(payload), encoding="utf-8")
    assert artifact_validators.validate_variables() >= 1

    payload = _minimal_variables_payload()
    payload["tt_ranks_K3"] = [1, 2, 3]
    (data / "manuscript_variables.json").write_text(json.dumps(payload), encoding="utf-8")
    assert artifact_validators.validate_variables() >= 1


def test_validate_sweep_rejects_bad_csv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    data = tmp_path / "output" / "data"
    data.mkdir(parents=True)
    (data / "parameter_sweep.csv").write_text("lambda\n0.0\n", encoding="utf-8")
    _patch_output_dir(monkeypatch, tmp_path)
    assert pymdp_validators.validate_sweep() == 1


def test_validate_sweep_passes_synthetic_grid(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    data = tmp_path / "output" / "data"
    data.mkdir(parents=True)
    header = (
        "lambda,mi_closed_form,mi_empirical,mi_residual,free_energy_u0,"
        "free_energy_u1,free_energy_u2,schmidt_rank,entanglement_entropy,phase\n"
    )
    rows = []
    for lam in H.PARAMETER_SWEEP_LAMBDAS.values():
        rows.append(
            f"{lam},0.1,0.1,0.0,0.0,0.0,0.0,2,0.5,phase1\n",
        )
    (data / "parameter_sweep.csv").write_text(header + "".join(rows), encoding="utf-8")
    _patch_output_dir(monkeypatch, tmp_path)
    assert pymdp_validators.validate_sweep() == 0


def test_robustness_validator_flags_missing_summary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    if not (SIM_DIR / "pymdp_robustness.csv").exists():
        pytest.skip("robustness CSV not generated")
    sim = tmp_path / "output" / "simulations"
    sim.mkdir(parents=True)
    shutil.copy(SIM_DIR / "pymdp_robustness.csv", sim / "pymdp_robustness.csv")
    _patch_output_dir(monkeypatch, tmp_path)
    assert pymdp_validators.validate_robustness_suite() >= 1


@pytest.mark.skipif(not FIG_DIR.exists(), reason="output/figures not generated")
def test_check_png_semantic_metadata_uses_real_figure_metadata() -> None:
    from PIL import Image

    path = FIG_DIR / "pymdp_robustness_tc_envelopes.png"
    if not path.exists():
        path = FIG_DIR / "ising_mi_curve.png"
    info = {str(k): str(v) for k, v in Image.open(path).info.items()}
    assert png_validation.check_png_semantic_metadata(path, info) == 0
    bad = dict(info)
    bad["project.uncertainty_semantics"] = "invalid_semantics"
    assert png_validation.check_png_semantic_metadata(path, bad) >= 1


def test_validate_run_log_accepts_minimal_valid_jsonl(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    logs = tmp_path / "output" / "logs"
    logs.mkdir(parents=True)
    records = [
        {"timestamp": "t0", "event": "main_start", "status": "ok"},
        {"timestamp": "t1", "section": "figure_pymdp_lambda_sweep", "status": "ok"},
        {"timestamp": "t2", "section": "figure_pymdp_rollout", "status": "ok"},
        {"timestamp": "t3", "section": "figure_pymdp_free_energies", "status": "ok"},
        {"timestamp": "t4", "event": "main_end", "status": "ok"},
    ]
    (logs / "pymdp_runs.jsonl").write_text(
        "\n".join(json.dumps(r) for r in records) + "\n",
        encoding="utf-8",
    )
    _patch_output_dir(monkeypatch, tmp_path)
    assert pymdp_validators.validate_run_log() == 0


@pytest.mark.skipif(not SIM_DIR.exists(), reason="output/simulations not generated")
def test_simulation_validators_pass_on_project_output(monkeypatch: pytest.MonkeyPatch) -> None:
    """Exercise pymdp CSV validators against the canonical generated tree."""
    _patch_output_dir(monkeypatch, PROJECT)
    for fn in VALIDATOR_FUNCS[2:]:
        assert fn() == 0, fn.__name__


@pytest.mark.skipif(not DATA_DIR.exists(), reason="output/data not generated")
def test_validate_variables_passes_on_project_output(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_output_dir(monkeypatch, PROJECT)
    assert artifact_validators.validate_variables() == 0


@pytest.mark.skipif(not FIG_DIR.exists(), reason="output/figures not generated")
def test_check_png_on_generated_figure() -> None:
    path = FIG_DIR / "ising_mi_curve.png"
    assert png_validation.check_png(path) == 0


@pytest.mark.skipif(not FIG_DIR.exists(), reason="output/figures not generated")
def test_validate_figures_passes_on_project_output(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_output_dir(monkeypatch, PROJECT)
    assert artifact_validators.validate_figures() == 0


@pytest.mark.skipif(not SIM_DIR.exists(), reason="output/simulations not generated")
def test_free_energy_bundle_copied_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Minimal copy of the real bundle should satisfy the validator."""
    src = PROJECT / "output" / "simulations" / "pymdp_free_energy_bundle.csv"
    dst_dir = tmp_path / "output" / "simulations"
    dst_dir.mkdir(parents=True)
    shutil.copy(src, dst_dir / src.name)
    _patch_output_dir(monkeypatch, tmp_path)
    assert pymdp_validators.validate_free_energy_bundle() == 0


@pytest.mark.skipif(not FIG_DIR.exists(), reason="output/figures not generated")
def test_output_gates_main_passes_on_generated_artifacts(capsys) -> None:
    rc = output_gates.main()
    captured = capsys.readouterr()
    assert rc == 0, captured.err
    assert "All output validations passed." in captured.out


def test_validate_outputs_script_is_thin_cli() -> None:
    script = PROJECT / "scripts" / "validate_outputs.py"
    text = script.read_text(encoding="utf-8")
    assert "output_gates" in text
    assert len(text.splitlines()) < 40


@pytest.mark.skipif(not FIG_DIR.exists(), reason="output/figures not generated")
def test_validate_outputs_subprocess() -> None:
    result = subprocess.run(
        [sys.executable, str(PROJECT / "scripts" / "validate_outputs.py")],
        cwd=PROJECT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
