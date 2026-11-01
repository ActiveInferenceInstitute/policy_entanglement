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
from manuscript.output_gates.constants import REQUIRED_VARIABLES
from simulation import hyperparameters as H
from tests.output_gates_helpers import patch_output_dir as _patch_output_dir

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


def test_analytical_variable_ranges_match_required_variables() -> None:
    """Shared keys in ANALYTICAL_VARIABLE_RANGES must match REQUIRED_VARIABLES."""
    from manuscript.validation_cli import EXPECTED_RANGES
    from manuscript.variable_ranges import ANALYTICAL_VARIABLE_RANGES

    assert EXPECTED_RANGES is ANALYTICAL_VARIABLE_RANGES
    for key, expected in ANALYTICAL_VARIABLE_RANGES.items():
        assert key in REQUIRED_VARIABLES, f"missing gate range for analytical key: {key}"
        assert REQUIRED_VARIABLES[key] == expected, (
            f"drift on {key}: gate={REQUIRED_VARIABLES[key]!r} analytical={expected!r}"
        )
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


def test_check_png_git_revision_binds_figure_to_head(tmp_path: Path) -> None:
    """A figure's embedded project.git_revision is provenance to be enforced:
    a stale rev differing from HEAD must fail, a matching/absent/unknown rev
    must not (RedTeam C7, 2026-08-01)."""
    path = tmp_path / "fig.png"
    head = png_validation._current_short_head()
    assert head is not None  # this review's repo is a live git checkout

    # Matching HEAD -> OK.
    assert png_validation.check_png_git_revision({"project.git_revision": head}, path) == 0
    # Absent / unknown -> not bound (structural validation owns that path).
    assert png_validation.check_png_git_revision({}, path) == 0
    assert png_validation.check_png_git_revision({"project.git_revision": "unknown"}, path) == 0
    # Non-rev garbage -> fail (tampered/truncated provenance).
    assert png_validation.check_png_git_revision({"project.git_revision": "not-a-rev"}, path) == 1
    # Stale but plausible rev -> fail.
    stale = "deadbeef" if head != "deadbeef" else "c0ffee0"
    assert png_validation.check_png_git_revision({"project.git_revision": stale}, path) == 1


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


def _write_output_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    """Write a small CSV fixture under a redirected ``output/`` tree."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [",".join(header), *(",".join(row) for row in rows)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _long_horizon_table(steps: int, *, marginal: str = "0.5") -> list[list[str]]:
    return [[str(t), "0.25", marginal, marginal] for t in range(steps)]


_LONG_HORIZON_HEADER = ["t", "total_correlation", "q0_u0", "q0_u1"]
_REPLICATE_HEADER = [
    "seed",
    "t",
    "total_correlation",
    "habit_accumulation",
    "tail_kl_window_max",
    "adjacent_kl_max",
]
_DIAGNOSTIC_HEADER = [
    "seed",
    "habit_accumulation",
    "tc_final",
    "tc_max",
    "tail_kl_window_max",
    "adjacent_kl_max",
    "margin_to_tolerance",
    "failure_mode",
]
_THRESHOLD_HEADER = ["threshold", "pass_rate", "pass_count", "fail_count", "ci_low", "ci_high"]
_ROBUSTNESS_REQUIRED = {
    "scenario_id",
    "axis",
    "level",
    "observations",
    "gamma",
    "preference_strength",
    "coupling_scale",
    "lambda",
    "total_correlation",
    "joint_entropy",
    "marginal_entropy_sum",
    "coupling_term",
    "aligned_mass",
    "decomposition_lhs",
    "decomposition_rhs",
    "decomposition_residual",
}
_ABLATION_REQUIRED = {
    "variant",
    "lambda",
    "total_correlation",
    "joint_entropy",
    "marginal_entropy_sum",
    "coupling_term",
    "aligned_mass",
    "decomposition_lhs",
    "decomposition_rhs",
    "decomposition_residual",
}


def test_long_horizon_validator_flags_missing_columns_and_length(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = _patch_output_dir(monkeypatch, tmp_path)
    csv_path = out / "simulations" / "pymdp_long_horizon.csv"
    _write_output_csv(csv_path, ["t"], [["0"], ["1"]])
    assert pymdp_validators.validate_long_horizon() == 1

    _write_output_csv(csv_path, _LONG_HORIZON_HEADER, [["0", "0.1", "0.5", "0.5"]])
    assert pymdp_validators.validate_long_horizon() == 1


def test_long_horizon_validator_flags_non_normalized_marginals(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _patch_output_dir(monkeypatch, tmp_path)
    _write_output_csv(
        out / "simulations" / "pymdp_long_horizon.csv",
        _LONG_HORIZON_HEADER,
        _long_horizon_table(int(H.LONG_HORIZON_STEPS), marginal="0.25"),
    )
    assert pymdp_validators.validate_long_horizon() >= 1


def test_long_horizon_validator_flags_summary_drift(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _patch_output_dir(monkeypatch, tmp_path)
    _write_output_csv(
        out / "simulations" / "pymdp_long_horizon.csv",
        _LONG_HORIZON_HEADER,
        _long_horizon_table(int(H.LONG_HORIZON_STEPS)),
    )
    summary = {
        "long_horizon_tc_recomputed_max_abs_diff": 0.0,
        "long_horizon_tail_window": int(H.LONG_HORIZON_TAIL_WINDOW),
        "long_horizon_tail_kl_first_max": 0.0,
        "long_horizon_tail_kl_mean_max": 0.0,
        "long_horizon_tail_kl_window_max": 0.0,
        "long_horizon_adjacent_kl_mean_max": 0.0,
        "long_horizon_adjacent_kl_max": 0.0,
    }
    summary_path = out / "data" / "long_horizon_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    summary_path.write_text(json.dumps(summary | {"long_horizon_tail_window": 999}), encoding="utf-8")
    assert pymdp_validators.validate_long_horizon() >= 1

    steady_state_tol = float(H.LONG_HORIZON_STEADY_STATE_TOL)
    summary_path.write_text(
        json.dumps(summary | {"long_horizon_tail_kl_window_max": steady_state_tol * 2.0}),
        encoding="utf-8",
    )
    assert pymdp_validators.validate_long_horizon() >= 1

    summary_path.write_text(json.dumps(summary | {"long_horizon_adjacent_kl_max": -1.0}), encoding="utf-8")
    assert pymdp_validators.validate_long_horizon() >= 1


def test_long_horizon_replicates_validator_flags_row_drift(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _patch_output_dir(monkeypatch, tmp_path)
    seeds = [int(s) for s in H.LONG_HORIZON_REPLICATE_SEEDS]
    rows = [[str(seed), str(t), "0.1", "1", "0.0", "0.0"] for seed in seeds for t in range(5)]
    _write_output_csv(out / "simulations" / "pymdp_long_horizon_replicates.csv", _REPLICATE_HEADER, rows)
    assert pymdp_validators.validate_long_horizon_replicates() >= 1


def test_long_horizon_seed_diagnostics_flags_margin_and_mode_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = _patch_output_dir(monkeypatch, tmp_path)
    seeds = [int(s) for s in H.LONG_HORIZON_REPLICATE_SEEDS]
    tol = float(H.LONG_HORIZON_STEADY_STATE_TOL)
    path = out / "simulations" / "pymdp_long_horizon_seed_diagnostics.csv"

    def rows(*, habit: int, mode: str, margin: str) -> list[list[str]]:
        return [[str(s), str(habit), "0.1", "0.2", "0.0", "0.0", margin, mode] for s in seeds]

    _write_output_csv(path, _DIAGNOSTIC_HEADER, rows(habit=1, mode="passes", margin=f"{tol:.6f}"))
    assert pymdp_validators.validate_long_horizon_seed_diagnostics() == 0

    _write_output_csv(path, _DIAGNOSTIC_HEADER, rows(habit=1, mode="passes", margin="999.0"))
    assert pymdp_validators.validate_long_horizon_seed_diagnostics() >= 1

    _write_output_csv(path, _DIAGNOSTIC_HEADER, rows(habit=1, mode="tail_window_kl_above_tol", margin=f"{tol:.6f}"))
    assert pymdp_validators.validate_long_horizon_seed_diagnostics() >= 1

    _write_output_csv(path, _DIAGNOSTIC_HEADER, rows(habit=0, mode="passes", margin=f"{tol:.6f}"))
    assert pymdp_validators.validate_long_horizon_seed_diagnostics() >= 1

    _write_output_csv(path, _DIAGNOSTIC_HEADER, rows(habit=1, mode="passes", margin=f"{tol:.6f}")[:-2])
    assert pymdp_validators.validate_long_horizon_seed_diagnostics() >= 1

    _write_output_csv(path, _DIAGNOSTIC_HEADER, rows(habit=2, mode="passes", margin=f"{tol:.6f}"))
    assert pymdp_validators.validate_long_horizon_seed_diagnostics() >= 1


def test_long_horizon_threshold_sensitivity_flags_rate_and_ci_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = _patch_output_dir(monkeypatch, tmp_path)
    thresholds = [float(x) for x in H.LONG_HORIZON_DIAGNOSTIC_THRESHOLDS]
    rows = [[f"{th:.6f}", "0.6", "3", "2", "0.3", "0.9"] for th in thresholds]
    path = out / "simulations" / "pymdp_long_horizon_threshold_sensitivity.csv"

    _write_output_csv(path, _THRESHOLD_HEADER, rows)
    assert pymdp_validators.validate_long_horizon_threshold_sensitivity() == 0

    rows[2] = [f"{thresholds[2]:.6f}", "1.5", "3", "2", "0.3", "0.9"]
    _write_output_csv(path, _THRESHOLD_HEADER, rows)
    assert pymdp_validators.validate_long_horizon_threshold_sensitivity() >= 1

    rows[2] = [f"{thresholds[2]:.6f}", "0.6", "3", "2", "0.7", "0.9"]
    _write_output_csv(path, _THRESHOLD_HEADER, rows)
    assert pymdp_validators.validate_long_horizon_threshold_sensitivity() >= 1

    _write_output_csv(path, _THRESHOLD_HEADER, rows[:-2])
    assert pymdp_validators.validate_long_horizon_threshold_sensitivity() >= 1


def test_long_horizon_validators_accept_absent_artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_output_dir(monkeypatch, tmp_path)
    assert pymdp_validators.validate_long_horizon() == 0
    assert pymdp_validators.validate_long_horizon_replicates() == 0
    assert pymdp_validators.validate_long_horizon_seed_diagnostics() == 0
    assert pymdp_validators.validate_long_horizon_threshold_sensitivity() == 0


def test_long_horizon_validator_flags_row_sequence_and_negative_tc(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = _patch_output_dir(monkeypatch, tmp_path)
    steps = int(H.LONG_HORIZON_STEPS)
    rows = _long_horizon_table(steps)
    rows[3][0] = "7"
    rows[4][1] = "-1.0"
    _write_output_csv(out / "simulations" / "pymdp_long_horizon.csv", _LONG_HORIZON_HEADER, rows)
    assert pymdp_validators.validate_long_horizon() >= 1


def test_long_horizon_replicates_validator_flags_row_content(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _patch_output_dir(monkeypatch, tmp_path)
    seeds = [int(s) for s in H.LONG_HORIZON_REPLICATE_SEEDS]
    rows = [
        [str(seed), str(2 * t), "0.1", "1", "0.0", "0.0"]
        for seed in seeds
        for t in range(5)
        if not (seed == seeds[0] and t == 1)
    ]
    rows.append([str(seeds[0]), "1", "0.1", "2", "0.0", "0.0"])
    rows.append([str(seeds[0]), "1", "-0.5", "1", "0.0", "0.0"])
    _write_output_csv(out / "simulations" / "pymdp_long_horizon_replicates.csv", _REPLICATE_HEADER, rows)
    assert pymdp_validators.validate_long_horizon_replicates() >= 1


def test_long_horizon_replicates_validator_flags_summary_seed_count(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = _patch_output_dir(monkeypatch, tmp_path)
    seeds = [int(s) for s in H.LONG_HORIZON_REPLICATE_SEEDS]
    steps = int(H.LONG_HORIZON_STEPS)
    rows = [[str(seed), str(t), "0.1", "1", "0.0", "0.0"] for seed in seeds for t in range(steps)]
    _write_output_csv(out / "simulations" / "pymdp_long_horizon_replicates.csv", _REPLICATE_HEADER, rows)
    summary_path = out / "data" / "long_horizon_replicates_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(
            {
                "long_horizon_replicate_seed_count": 3,
                "long_horizon_replicate_habit_pass_rate": 0.5,
                "long_horizon_replicate_tc_final_mean": 0.1,
                "long_horizon_replicate_tail_kl_window_max": 0.05,
            }
        ),
        encoding="utf-8",
    )
    assert pymdp_validators.validate_long_horizon_replicates() >= 1


def test_robustness_validators_flag_absent_and_short_artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _patch_output_dir(monkeypatch, tmp_path)
    assert pymdp_validators.validate_robustness_suite() == 0
    assert pymdp_validators.validate_coupling_ablation() == 0

    _write_output_csv(
        out / "simulations" / "pymdp_robustness.csv",
        ["scenario_id", *sorted(_ROBUSTNESS_REQUIRED - {"scenario_id"})],
        [["coupling_0", *["0.0"] * len(_ROBUSTNESS_REQUIRED - {"scenario_id"})]],
    )
    assert pymdp_validators.validate_robustness_suite() >= 1

    _write_output_csv(
        out / "simulations" / "pymdp_coupling_ablation.csv",
        ["variant", *sorted(_ABLATION_REQUIRED - {"variant"})],
        [["null", *["0.0"] * len(_ABLATION_REQUIRED - {"variant"})]],
    )
    assert pymdp_validators.validate_coupling_ablation() >= 1
