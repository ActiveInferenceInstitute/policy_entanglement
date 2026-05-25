"""Corruption fixtures for ``manuscript.output_gates`` error branches.

Copies canonical ``output/simulations`` and ``output/data`` sidecars into a
temp tree, perturbs one column or field, and asserts the matching validator
returns a non-zero failure count.
"""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

import pytest

from manuscript.output_gates import csv_helpers, png_validation, pymdp_validators
from manuscript.output_gates.constants import (
    MIN_FIGURE_HEIGHT,
    MIN_FIGURE_WIDTH,
    VALID_UNCERTAINTY_SEMANTICS,
)
from simulation import hyperparameters as H
from tests.output_gates_helpers import patch_output_dir as _patch_output_dir

PROJECT = Path(__file__).resolve().parent.parent
SIM_DIR = PROJECT / "output" / "simulations"
DATA_DIR = PROJECT / "output" / "data"
FIG_DIR = PROJECT / "output" / "figures"


def _stage_output_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    out = _patch_output_dir(monkeypatch, tmp_path)
    if SIM_DIR.is_dir():
        shutil.copytree(SIM_DIR, out / "simulations", dirs_exist_ok=True)
    if DATA_DIR.is_dir():
        shutil.copytree(DATA_DIR, out / "data", dirs_exist_ok=True)
    return out


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fields = list(reader.fieldnames or [])
        return fields, list(reader)


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


pytestmark = pytest.mark.skipif(
    not SIM_DIR.is_dir(),
    reason="output/simulations not generated — run pipeline first",
)


def test_staged_output_tree_passes_all_pymdp_validators(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stage_output_tree(tmp_path, monkeypatch)
    validators = (
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
    )
    for fn in validators:
        assert fn() == 0, fn.__name__


def test_sweep_missing_columns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _patch_output_dir(monkeypatch, tmp_path)
    data = out / "data"
    data.mkdir(parents=True)
    (data / "parameter_sweep.csv").write_text("lambda\n0.0\n", encoding="utf-8")
    assert pymdp_validators.validate_sweep() == 1


def test_sweep_mi_mismatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "data" / "parameter_sweep.csv"
    if not path.exists():
        header = (
            "lambda,mi_closed_form,mi_empirical,mi_residual,free_energy_u0,"
            "free_energy_u1,free_energy_u2,schmidt_rank,entanglement_entropy,phase\n"
        )
        rows = [
            f"{lam},0.1,0.1,0.0,0.0,0.0,0.0,2,0.5,p\n"
            for lam in H.PARAMETER_SWEEP_LAMBDAS.values()
        ]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(header + "".join(rows), encoding="utf-8")
    fields, rows = _read_csv(path)
    rows[0]["mi_empirical"] = str(float(rows[0]["mi_closed_form"]) + 1.0)
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_sweep() >= 1


def test_free_energy_bundle_lambda_zero_coupling(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Corrupt λ≈0 mean-field baseline (shared sweep_validation helper path)."""
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_free_energy_bundle.csv"
    fields, rows = _read_csv(path)
    zero_tol = float(H.PYMDP_COUPLING_ZERO_TOLERANCE)
    for row in rows:
        if abs(float(row["lambda"])) < zero_tol:
            row["coupling_term"] = "0.5"
            break
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_free_energy_bundle() >= 1


def test_robustness_h_gap_mismatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Corrupt H-gap vs TC invariant (shared validate_tc_decomposition_group path)."""
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_robustness.csv"
    fields, rows = _read_csv(path)
    rows[0]["marginal_entropy_sum"] = str(float(rows[0]["joint_entropy"]) + 99.0)
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_robustness_suite() >= 1


def test_free_energy_bundle_negative_tc(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_free_energy_bundle.csv"
    fields, rows = _read_csv(path)
    for row in rows:
        if abs(float(row["lambda"])) > 0.01:
            row["total_correlation"] = "-1.0"
            break
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_free_energy_bundle() >= 1


def test_free_energy_bundle_decomposition_residual(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_free_energy_bundle.csv"
    fields, rows = _read_csv(path)
    rows[1]["decomposition_residual"] = "1.0"
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_free_energy_bundle() >= 1


def test_multi_k_invalid_tt_ranks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_K3_sweep.csv"
    if not path.exists():
        pytest.skip("K3 sweep not generated")
    fields, rows = _read_csv(path)
    rows[0]["tt_ranks"] = "1|2|3"
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_multi_k_sweep() >= 1


def test_revertibility_flag_corruption(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_revertibility.csv"
    fields, rows = _read_csv(path)
    rows[0]["revertible"] = "0"
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_revertibility() >= 1


def test_long_horizon_nonsequential_t(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_long_horizon.csv"
    fields, rows = _read_csv(path)
    rows[1]["t"] = "99"
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_long_horizon() >= 1


def test_long_horizon_summary_drift(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    summary_path = out / "data" / "long_horizon_summary.json"
    if not summary_path.exists():
        pytest.skip("long_horizon_summary.json not generated")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["long_horizon_tc_recomputed_max_abs_diff"] = 1.0
    summary_path.write_text(json.dumps(summary), encoding="utf-8")
    assert pymdp_validators.validate_long_horizon() >= 1


def test_robustness_nonmonotone_tc(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_robustness.csv"
    fields, rows = _read_csv(path)
    scenario = rows[0]["scenario_id"]
    group = sorted((r for r in rows if r["scenario_id"] == scenario), key=lambda r: float(r["lambda"]))
    if len(group) >= 2:
        group[-1]["total_correlation"] = str(float(group[0]["total_correlation"]) - 0.5)
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_robustness_suite() >= 1


def test_coupling_ablation_null_variant_positive_tc(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_coupling_ablation.csv"
    fields, rows = _read_csv(path)
    for row in rows:
        if row["variant"] == "null":
            row["total_correlation"] = "0.5"
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_coupling_ablation() >= 1


def test_marginal_null_control_bad_null_tc(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_marginal_null_control.csv"
    fields, rows = _read_csv(path)
    rows[0]["null_total_correlation"] = "0.01"
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_marginal_null_control() >= 1


def test_long_horizon_replicates_bad_habit_flag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_long_horizon_replicates.csv"
    fields, rows = _read_csv(path)
    rows[0]["habit_accumulation"] = "2"
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_long_horizon_replicates() >= 1


def test_seed_diagnostics_wrong_failure_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_long_horizon_seed_diagnostics.csv"
    fields, rows = _read_csv(path)
    for row in rows:
        if row["habit_accumulation"] == "1":
            row["failure_mode"] = "tail_window_kl_above_tol"
            break
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_long_horizon_seed_diagnostics() >= 1


def test_threshold_sensitivity_nonmonotone_rates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_long_horizon_threshold_sensitivity.csv"
    fields, rows = _read_csv(path)
    if len(rows) >= 2:
        rows[-1]["pass_rate"] = "0.0"
        rows[0]["pass_rate"] = "1.0"
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_long_horizon_threshold_sensitivity() >= 1


def test_run_log_missing_timestamp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    logs = out / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    records = [
        {"event": "main_start", "status": "ok"},
        {"timestamp": "t1", "section": "figure_pymdp_lambda_sweep", "status": "ok"},
        {"timestamp": "t2", "section": "figure_pymdp_rollout", "status": "ok"},
        {"timestamp": "t3", "section": "figure_pymdp_free_energies", "status": "ok"},
        {"timestamp": "t4", "event": "main_end", "status": "ok"},
    ]
    (logs / "pymdp_runs.jsonl").write_text(
        "\n".join(json.dumps(r) for r in records) + "\n",
        encoding="utf-8",
    )
    assert pymdp_validators.validate_run_log() >= 1


def test_run_log_missing_required_section(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    logs = out / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    records = [
        {"timestamp": "t0", "event": "main_start", "status": "ok"},
        {"timestamp": "t1", "section": "figure_pymdp_lambda_sweep", "status": "ok"},
        {"timestamp": "t4", "event": "main_end", "status": "ok"},
    ]
    (logs / "pymdp_runs.jsonl").write_text(
        "\n".join(json.dumps(r) for r in records) + "\n",
        encoding="utf-8",
    )
    assert pymdp_validators.validate_run_log() >= 1


@pytest.mark.skipif(not FIG_DIR.is_dir(), reason="output/figures not generated")
def test_png_constructed_metadata_error_paths(tmp_path: Path) -> None:
    from PIL import Image, PngImagePlugin

    path = tmp_path / "synthetic.png"
    img = Image.new("RGB", (MIN_FIGURE_WIDTH, MIN_FIGURE_HEIGHT), color=(128, 64, 32))
    # Non-flat pixels.
    px = img.load()
    assert px is not None
    px[0, 0] = (0, 0, 0)
    px[-1, -1] = (255, 255, 255)

    stats = {
        "schema_version": 1,
        "axes_count": 1,
        "axes": [
            {
                "index": 0,
                "title": "Small",
                "font_sizes": {"title": 8.0, "xlabel": 8.0, "yticklabels": [8.0]},
                "text_count": 0,
            }
        ],
        "figure_size_inches": [6.0, 4.0],
        "figure_texts": [{"fontsize": 6.0, "text": "note"}],
    }
    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text("project.source_script", "tests/test_output_gates_corruption.py")
    pnginfo.add_text("project.source_function", "test_png_constructed_metadata_error_paths")
    pnginfo.add_text("project.uncertainty_semantics", next(iter(VALID_UNCERTAINTY_SEMANTICS)))
    pnginfo.add_text("project.figure_statistics", json.dumps(stats))
    pnginfo.add_text("project.hyperparameters", json.dumps({"K": 2}))
    img.save(path, pnginfo=pnginfo)

    assert png_validation.check_png(path) >= 1

    bad_stats_info = {
        "project.uncertainty_semantics": "deterministic_grid",
        "project.figure_statistics": "{bad json",
        "project.hyperparameters": "{}",
    }
    assert png_validation.check_png_semantic_metadata(path, bad_stats_info) >= 1

    tiny = tmp_path / "tiny.png"
    Image.new("RGB", (100, 100), color=(1, 2, 3)).save(tiny)
    assert png_validation.check_png(tiny) >= 1


def test_png_finite_and_decode_helpers() -> None:
    with pytest.raises(ValueError, match="not finite"):
        png_validation._finite("nan")
    path = Path("synthetic.png")
    obj, bad = png_validation._decode_json_metadata({}, path, "project.figure_statistics")
    assert obj is None and bad == 1
    obj, bad = png_validation._decode_json_metadata(
        {"project.figure_statistics": "{bad"}, path, "project.figure_statistics"
    )
    assert obj is None and bad == 1


def test_png_semantic_font_and_hyper_paths(tmp_path: Path) -> None:
    path = tmp_path / "pymdp_test_panel.png"
    info = {
        "project.uncertainty_semantics": "invalid",
        "project.figure_statistics": json.dumps({"schema_version": 0, "axes_count": 0}),
        "project.hyperparameters": json.dumps([]),
    }
    assert png_validation.check_png_semantic_metadata(path, info) >= 3

    stats = {
        "schema_version": 2,
        "axes_count": 1,
        "axes": [
            {
                "index": 0,
                "title": "Title",
                "xlabel": "X",
                "ylabel": "Y",
                "font_sizes": {
                    "title": 6.0,
                    "xlabel": 6.0,
                    "ylabel": 6.0,
                    "xticklabels": [6.0],
                    "yticklabels": [6.0],
                    "legend": [6.0],
                    "texts": [{"fontsize": 6.0}],
                },
                "text_count": 0,
                "legend_labels": [f"Theorem {6}.{4}"],
                "texts": ["Fig. 6.4"],
            }
        ],
        "figure_size_inches": [6.0, 4.0],
        "figure_texts": [{"fontsize": 6.0, "text": "note"}],
    }
    info2 = {
        "project.uncertainty_semantics": "deterministic_grid",
        "project.figure_statistics": json.dumps(stats),
        "project.hyperparameters": json.dumps({}),
    }
    assert png_validation.check_png_semantic_metadata(path, info2) >= 5

    stats["axes"][0]["font_sizes"] = {}
    stats["axes"][0]["text_count"] = 1
    info3 = {
        "project.uncertainty_semantics": "deterministic_grid",
        "project.figure_statistics": json.dumps(stats),
        "project.hyperparameters": json.dumps({"K": 2}),
    }
    multi_k = tmp_path / "multi_k_sweep_panel.png"
    assert png_validation.check_png_semantic_metadata(multi_k, info3) >= 1


def test_sweep_missing_columns_and_row_count(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _patch_output_dir(monkeypatch, tmp_path)
    path = out / "data" / "parameter_sweep.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("lambda\n0.0\n1.0\n", encoding="utf-8")
    assert pymdp_validators.validate_sweep() >= 1

    path.write_text("lambda,mi_closed_form\n0.0,0.1\n", encoding="utf-8")
    assert pymdp_validators.validate_sweep() >= 1


def test_free_energy_bundle_missing_columns_and_baseline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_free_energy_bundle.csv"
    canonical = path.read_text(encoding="utf-8")
    path.write_text("lambda\n0.0\n", encoding="utf-8")
    assert pymdp_validators.validate_free_energy_bundle() >= 1

    path.write_text(canonical, encoding="utf-8")
    fields, rows = _read_csv(path)
    for row in rows:
        if abs(float(row["lambda"])) < 0.01:
            row["total_correlation"] = "0.5"
            row["coupling_term"] = "0.5"
            break
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_free_energy_bundle() >= 1


def test_free_energy_h_gap_and_nonfinite(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_free_energy_bundle.csv"
    fields, rows = _read_csv(path)
    rows[2]["marginal_entropy_sum"] = str(float(rows[2]["joint_entropy"]) + 0.01)
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_free_energy_bundle() >= 1

    fields, rows = _read_csv(path)
    rows[3]["vfe_total"] = "nan"
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_free_energy_bundle() >= 1


def test_multi_k_sweep_error_branches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    for k in H.MULTI_K_VALUES:
        path = out / "simulations" / f"pymdp_K{k}_sweep.csv"
        if not path.exists():
            continue
        fields, rows = _read_csv(path)
        rows[1]["total_correlation"] = str(float(rows[0]["total_correlation"]) - 0.1)
        _write_csv(path, fields, rows)
        assert pymdp_validators.validate_multi_k_sweep() >= 1
        break


def test_multi_k_aligned_mass_and_zero_baseline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    k = H.MULTI_K_VALUES[0]
    path = out / "simulations" / f"pymdp_K{k}_sweep.csv"
    if not path.exists():
        pytest.skip("K sweep not generated")
    fields, rows = _read_csv(path)
    rows[0]["aligned_mass"] = "1.5"
    rows[0]["total_correlation"] = "0.5"
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_multi_k_sweep() >= 1


def test_long_horizon_wrong_length_and_negative_tc(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_long_horizon.csv"
    fields, rows = _read_csv(path)
    _write_csv(path, fields, rows[:5])
    assert pymdp_validators.validate_long_horizon() >= 1

    shutil.copy(SIM_DIR / "pymdp_long_horizon.csv", path)
    fields, rows = _read_csv(path)
    rows[5]["total_correlation"] = "-0.1"
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_long_horizon() >= 1


def test_long_horizon_summary_missing_keys(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    summary_path = out / "data" / "long_horizon_summary.json"
    if not summary_path.exists():
        pytest.skip("long_horizon_summary.json not generated")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary.pop("long_horizon_tail_kl_window_max", None)
    summary["long_horizon_adjacent_kl_max"] = -1.0
    summary_path.write_text(json.dumps(summary), encoding="utf-8")
    assert pymdp_validators.validate_long_horizon() >= 1


def test_revertibility_error_branches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_revertibility.csv"
    fields, rows = _read_csv(path)
    rows[0]["kl_identity_residual"] = "999"
    rows[0]["marginals_match"] = "0"
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_revertibility() >= 1


def test_robustness_scenario_and_decomposition_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_robustness.csv"
    fields, rows = _read_csv(path)
    rows[0]["scenario_id"] = "bogus_scenario"
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_robustness_suite() >= 1

    shutil.copy(SIM_DIR / "pymdp_robustness.csv", path)
    fields, rows = _read_csv(path)
    rows[10]["decomposition_residual"] = "1.0"
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_robustness_suite() >= 1


def test_coupling_ablation_variant_and_nonnull_tc(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_coupling_ablation.csv"
    fields, rows = _read_csv(path)
    rows[0]["variant"] = "bogus"
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_coupling_ablation() >= 1

    shutil.copy(SIM_DIR / "pymdp_coupling_ablation.csv", path)
    fields, rows = _read_csv(path)
    for row in rows:
        if row["variant"] != "null":
            row["total_correlation"] = "0.0"
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_coupling_ablation() >= 1


def test_marginal_null_tc_removed_and_summary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_marginal_null_control.csv"
    fields, rows = _read_csv(path)
    rows[0]["tc_removed"] = "999"
    rows[0]["original_aligned_mass"] = "2.0"
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_marginal_null_control() >= 1

    summary_path = out / "data" / "marginal_null_control_summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["robustness_null_control_max_tc"] = "0.5"
        summary_path.write_text(json.dumps(summary), encoding="utf-8")
        assert pymdp_validators.validate_marginal_null_control() >= 1


def test_interaction_robustness_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_interaction_robustness.csv"
    if not path.exists():
        pytest.skip("interaction robustness not generated")
    fields, rows = _read_csv(path)
    rows[0]["family"] = "bogus_family"
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_interaction_robustness() >= 1

    shutil.copy(SIM_DIR / "pymdp_interaction_robustness.csv", path)
    fields, rows = _read_csv(path)
    for row in rows:
        if row.get("variant") == "null":
            row["total_correlation"] = "0.5"
            break
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_interaction_robustness() >= 1


def test_long_horizon_replicates_seed_and_summary_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_long_horizon_replicates.csv"
    fields, rows = _read_csv(path)
    rows[0]["seed"] = "99999"
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_long_horizon_replicates() >= 1

    summary_path = out / "data" / "long_horizon_replicates_summary.json"
    if summary_path.exists():
        shutil.copy(SIM_DIR / "pymdp_long_horizon_replicates.csv", path)
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["long_horizon_replicate_habit_pass_rate"] = 2.0
        summary_path.write_text(json.dumps(summary), encoding="utf-8")
        assert pymdp_validators.validate_long_horizon_replicates() >= 1


def test_seed_diagnostics_margin_mismatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_long_horizon_seed_diagnostics.csv"
    fields, rows = _read_csv(path)
    rows[0]["margin_to_tolerance"] = "999"
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_long_horizon_seed_diagnostics() >= 1


def test_threshold_sensitivity_ci_and_counts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _stage_output_tree(tmp_path, monkeypatch)
    path = out / "simulations" / "pymdp_long_horizon_threshold_sensitivity.csv"
    fields, rows = _read_csv(path)
    rows[0]["threshold"] = "999"
    rows[0]["pass_rate"] = "2.0"
    rows[0]["ci_low"] = "0.9"
    rows[0]["ci_high"] = "0.8"
    rows[0]["pass_count"] = "0"
    rows[0]["fail_count"] = "0"
    _write_csv(path, fields, rows)
    assert pymdp_validators.validate_long_horizon_threshold_sensitivity() >= 1


def test_run_log_malformed_and_too_few_records(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = _patch_output_dir(monkeypatch, tmp_path)
    logs = out / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    (logs / "pymdp_runs.jsonl").write_text("{bad json}\n", encoding="utf-8")
    assert pymdp_validators.validate_run_log() >= 1

    (logs / "pymdp_runs.jsonl").write_text(
        '{"timestamp":"t0","event":"main_start","status":"ok"}\n',
        encoding="utf-8",
    )
    assert pymdp_validators.validate_run_log() >= 1


def test_csv_helpers_lambda_mismatch(tmp_path: Path) -> None:
    grid = H.PYMDP_SWEEP_LAMBDAS
    rows = [{"lambda": "999.0"} for _ in grid.values()]
    assert csv_helpers.rows_match_grid(rows, grid, label="mismatch") >= 1
