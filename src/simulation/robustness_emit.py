"""CSV/JSON emission and figure metadata for the robustness pipeline."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from visualizations.metadata import figure_metadata

from . import hyperparameters as H  # noqa: N812
from .robustness_replicates import long_horizon_threshold_sensitivity


def snapshot() -> dict[str, Any]:
    """Hyperparameter snapshot attached to robustness PNG metadata."""

    return {
        "K": int(H.PYMDP_ENSEMBLE_K),
        "gamma_baseline": float(H.PYMDP_ENSEMBLE_GAMMA),
        "observations_baseline": list(H.PYMDP_SWEEP_OBSERVATIONS),
        "robustness_observation_contexts": [list(obs) for obs in H.ROBUSTNESS_OBSERVATION_CONTEXTS],
        "robustness_gammas": list(float(x) for x in H.ROBUSTNESS_GAMMAS),
        "robustness_preference_strengths": list(float(x) for x in H.ROBUSTNESS_PREFERENCE_STRENGTHS),
        "robustness_coupling_scales": list(float(x) for x in H.ROBUSTNESS_COUPLING_SCALES),
        "robustness_interaction_families": list(H.ROBUSTNESS_INTERACTION_FAMILIES),
        "sweep_grid_points": int(H.ROBUSTNESS_SWEEP_LAMBDAS.num),
        "sweep_lambda_max": float(H.ROBUSTNESS_SWEEP_LAMBDAS.stop),
        "replicate_seeds": list(int(s) for s in H.LONG_HORIZON_REPLICATE_SEEDS),
        "seed": "replicate sidecar",
        "horizon": int(H.LONG_HORIZON_STEPS),
        "tail_window": int(H.LONG_HORIZON_TAIL_WINDOW),
        "steady_state_tol": float(H.LONG_HORIZON_STEADY_STATE_TOL),
        "diagnostic_thresholds": list(float(x) for x in H.LONG_HORIZON_DIAGNOSTIC_THRESHOLDS),
        "variants": list(H.COUPLING_ABLATION_VARIANTS),
    }


def figure_metadata_dict(
    source_function: str,
    *,
    statistics: dict[str, Any] | None = None,
    project_root: Path | None = None,
) -> dict[str, str]:
    """Standardised PNG metadata for every robustness figure."""

    return figure_metadata(
        source_script="scripts/simulate_robustness.py",
        source_function=source_function,
        hyperparameters=snapshot(),
        statistics=statistics,
        project_root=project_root,
    )


def write_robustness_csv(rows, sim_dir: Path) -> Path:
    path = sim_dir / "pymdp_robustness.csv"
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
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
            ]
        )
        for r in rows:
            writer.writerow(
                [
                    r.scenario_id,
                    r.axis,
                    r.level,
                    "|".join(str(int(x)) for x in r.observations),
                    f"{r.gamma:.10g}",
                    f"{r.preference_strength:.10g}",
                    f"{r.coupling_scale:.10g}",
                    f"{r.lam:.6f}",
                    f"{r.total_correlation:.10g}",
                    f"{r.joint_entropy:.10g}",
                    f"{r.marginal_entropy_sum:.10g}",
                    f"{r.coupling_term:.10g}",
                    f"{r.aligned_mass:.10g}",
                    f"{r.decomposition_lhs:.10g}",
                    f"{r.decomposition_rhs:.10g}",
                    f"{r.decomposition_residual:.10g}",
                ]
            )
    return path


def write_ablation_csv(rows, sim_dir: Path) -> Path:
    path = sim_dir / "pymdp_coupling_ablation.csv"
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
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
            ]
        )
        for r in rows:
            writer.writerow(
                [
                    r.variant,
                    f"{r.lam:.6f}",
                    f"{r.total_correlation:.10g}",
                    f"{r.joint_entropy:.10g}",
                    f"{r.marginal_entropy_sum:.10g}",
                    f"{r.coupling_term:.10g}",
                    f"{r.aligned_mass:.10g}",
                    f"{r.decomposition_lhs:.10g}",
                    f"{r.decomposition_rhs:.10g}",
                    f"{r.decomposition_residual:.10g}",
                ]
            )
    return path


def write_interaction_csv(rows, sim_dir: Path) -> Path:
    path = sim_dir / "pymdp_interaction_robustness.csv"
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "family",
                "scenario_id",
                "level_a",
                "level_b",
                "observations",
                "gamma",
                "preference_strength",
                "coupling_scale",
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
            ]
        )
        for r in rows:
            writer.writerow(
                [
                    r.family,
                    r.scenario_id,
                    r.level_a,
                    r.level_b,
                    "|".join(str(int(x)) for x in r.observations),
                    f"{r.gamma:.10g}",
                    f"{r.preference_strength:.10g}",
                    f"{r.coupling_scale:.10g}",
                    r.variant,
                    f"{r.lam:.6f}",
                    f"{r.total_correlation:.10g}",
                    f"{r.joint_entropy:.10g}",
                    f"{r.marginal_entropy_sum:.10g}",
                    f"{r.coupling_term:.10g}",
                    f"{r.aligned_mass:.10g}",
                    f"{r.decomposition_lhs:.10g}",
                    f"{r.decomposition_rhs:.10g}",
                    f"{r.decomposition_residual:.10g}",
                ]
            )
    return path


def write_long_horizon_replicate_csv(results, records, sim_dir: Path) -> Path:
    path = sim_dir / "pymdp_long_horizon_replicates.csv"
    record_by_seed = {int(r.seed): r for r in records}
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "seed",
                "t",
                "total_correlation",
                "habit_accumulation",
                "tail_kl_window_max",
                "adjacent_kl_max",
            ]
        )
        for result in results:
            rec = record_by_seed[int(result.seed)]
            for t, tc in enumerate(result.total_correlations):
                writer.writerow(
                    [
                        int(result.seed),
                        int(t),
                        f"{float(tc):.10g}",
                        int(rec.habit_accumulation),
                        f"{rec.tail_kl_window_max:.10g}",
                        f"{rec.adjacent_kl_max:.10g}",
                    ]
                )
    return path


def write_long_horizon_seed_diagnostics_csv(diagnostics, sim_dir: Path) -> Path:
    path = sim_dir / "pymdp_long_horizon_seed_diagnostics.csv"
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "seed",
                "habit_accumulation",
                "tc_final",
                "tc_max",
                "tail_kl_window_max",
                "adjacent_kl_max",
                "margin_to_tolerance",
                "failure_mode",
            ]
        )
        for r in diagnostics:
            writer.writerow(
                [
                    int(r.seed),
                    int(r.habit_accumulation),
                    f"{r.tc_final:.10g}",
                    f"{r.tc_max:.10g}",
                    f"{r.tail_kl_window_max:.10g}",
                    f"{r.adjacent_kl_max:.10g}",
                    f"{r.margin_to_tolerance:.10g}",
                    r.failure_mode,
                ]
            )
    return path


def write_long_horizon_threshold_sensitivity_csv(diagnostics, sim_dir: Path) -> Path:
    path = sim_dir / "pymdp_long_horizon_threshold_sensitivity.csv"
    rows = long_horizon_threshold_sensitivity(diagnostics)
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["threshold", "pass_rate", "pass_count", "fail_count", "ci_low", "ci_high"])
        for r in rows:
            writer.writerow(
                [
                    f"{r.threshold:.10g}",
                    f"{r.pass_rate:.10g}",
                    int(r.pass_count),
                    int(r.fail_count),
                    f"{r.ci_low:.10g}",
                    f"{r.ci_high:.10g}",
                ]
            )
    return path


def write_marginal_null_control_csv(rows, sim_dir: Path) -> Path:
    path = sim_dir / "pymdp_marginal_null_control.csv"
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "lambda",
                "original_total_correlation",
                "null_total_correlation",
                "original_aligned_mass",
                "null_aligned_mass",
                "tc_removed",
                "aligned_mass_shift",
            ]
        )
        for r in rows:
            writer.writerow(
                [
                    f"{r.lam:.6f}",
                    f"{r.original_total_correlation:.10g}",
                    f"{r.null_total_correlation:.10g}",
                    f"{r.original_aligned_mass:.10g}",
                    f"{r.null_aligned_mass:.10g}",
                    f"{r.tc_removed:.10g}",
                    f"{r.aligned_mass_shift:.10g}",
                ]
            )
    return path
