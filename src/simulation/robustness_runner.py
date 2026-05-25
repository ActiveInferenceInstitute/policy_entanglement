"""Robustness, ablation, and long-horizon replicate sidecar pipeline.

Business logic for ``scripts/simulate_robustness.py``. The script remains
a thin orchestrator that calls :func:`run_robustness_pipeline`; this
module owns CSV serialisation, JSON summary writing, figure metadata,
and the figure-emission glue around the numerical helpers in
:mod:`simulation.robustness` and the plotting helpers in
:mod:`visualizations.robustness_plots`.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from visualizations.metadata import figure_metadata
from visualizations.robustness_plots import (
    plot_coupling_ablation_summary,
    plot_interaction_robustness_summary,
    plot_long_horizon_replicate_envelope,
    plot_long_horizon_seed_diagnostics,
    plot_long_horizon_threshold_sensitivity,
    plot_marginal_null_control_summary,
    plot_robustness_decomposition_residuals,
    plot_robustness_half_saturation,
    plot_robustness_tc_envelopes,
)
from visualizations.setup import deterministic_setup, ensure_outdir

from . import hyperparameters as H  # noqa: N812 — H = hyperparameters (manuscript convention).
from .agents import pymdp_available
from .robustness import (
    long_horizon_seed_diagnostics,
    long_horizon_tc_envelope,
    long_horizon_threshold_sensitivity,
    run_coupling_ablation,
    run_interaction_robustness_suite,
    run_long_horizon_replicates,
    run_marginal_null_control,
    run_robustness_suite,
    summarize_coupling_ablation_rows,
    summarize_interaction_robustness_rows,
    summarize_long_horizon_replicates,
    summarize_marginal_null_control_rows,
    summarize_robustness_rows,
)


def _snapshot() -> dict[str, Any]:
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


def _md(
    source_function: str,
    *,
    statistics: dict[str, Any] | None = None,
    project_root: Path | None = None,
) -> dict[str, str]:
    """Standardised PNG metadata for every robustness figure."""

    return figure_metadata(
        source_script="scripts/simulate_robustness.py",
        source_function=source_function,
        hyperparameters=_snapshot(),
        statistics=statistics,
        project_root=project_root,
    )


def _write_robustness_csv(rows, sim_dir: Path) -> Path:
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


def _write_ablation_csv(rows, sim_dir: Path) -> Path:
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


def _write_interaction_csv(rows, sim_dir: Path) -> Path:
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


def _write_long_horizon_replicate_csv(results, records, sim_dir: Path) -> Path:
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


def _write_long_horizon_seed_diagnostics_csv(diagnostics, sim_dir: Path) -> Path:
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


def _write_long_horizon_threshold_sensitivity_csv(diagnostics, sim_dir: Path) -> Path:
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


def _write_marginal_null_control_csv(rows, sim_dir: Path) -> Path:
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


def run_robustness_pipeline(
    *,
    fig_dir: Path,
    sim_dir: Path,
    data_dir: Path,
    project_root: Path | None = None,
) -> list[Path]:
    """Run the robustness, ablation, and replicate sidecar pipeline.

    Returns the ordered list of artifact paths (CSVs, JSON summaries,
    PNG figures) suitable for stdout emission by the orchestrator.
    Returns an empty list when pymdp is unavailable (the caller should
    treat that as a successful no-op).
    """

    if not pymdp_available():  # pragma: no cover
        return []
    ensure_outdir(fig_dir)
    ensure_outdir(sim_dir)
    ensure_outdir(data_dir)
    deterministic_setup(seed=int(H.FIGURE_GLOBAL_SEED))

    def _robust_progress(idx: int, total: int, scenario) -> None:
        print(f"[robustness] scenario {idx}/{total}: {scenario.scenario_id}", flush=True)

    robustness_rows = run_robustness_suite(progress_callback=_robust_progress)
    robustness_summaries, robustness_flat = summarize_robustness_rows(robustness_rows)
    robustness_csv = _write_robustness_csv(robustness_rows, sim_dir)
    robustness_json = data_dir / "robustness_summary.json"
    robustness_json.write_text(
        json.dumps(
            {
                **robustness_flat,
                "scenarios": [asdict(s) for s in robustness_summaries],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    ablation_rows = run_coupling_ablation()
    ablation_flat = summarize_coupling_ablation_rows(ablation_rows)
    ablation_csv = _write_ablation_csv(ablation_rows, sim_dir)
    ablation_json = data_dir / "coupling_ablation_summary.json"
    ablation_json.write_text(json.dumps(ablation_flat, indent=2, sort_keys=True) + "\n")

    null_control_rows = run_marginal_null_control()
    null_control_flat = summarize_marginal_null_control_rows(null_control_rows)
    null_control_csv = _write_marginal_null_control_csv(null_control_rows, sim_dir)
    null_control_json = data_dir / "marginal_null_control_summary.json"
    null_control_json.write_text(json.dumps(null_control_flat, indent=2, sort_keys=True) + "\n")

    def _interaction_progress(idx: int, total: int, scenario) -> None:
        print(f"[interaction-robustness] scenario {idx}/{total}: {scenario.scenario_id}", flush=True)

    interaction_rows = run_interaction_robustness_suite(progress_callback=_interaction_progress)
    interaction_summaries, interaction_flat = summarize_interaction_robustness_rows(interaction_rows)
    interaction_csv = _write_interaction_csv(interaction_rows, sim_dir)
    interaction_json = data_dir / "interaction_robustness_summary.json"
    interaction_json.write_text(
        json.dumps(
            {
                **interaction_flat,
                "scenarios": [asdict(s) for s in interaction_summaries],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    def _rep_progress(idx: int, total: int, seed: int) -> None:
        print(f"[long-horizon-replicates] seed {idx}/{total}: {seed}", flush=True)

    replicate_results = run_long_horizon_replicates(progress_callback=_rep_progress)
    replicate_records, replicate_flat = summarize_long_horizon_replicates(replicate_results)
    seed_diagnostics = long_horizon_seed_diagnostics(replicate_results)
    replicate_csv = _write_long_horizon_replicate_csv(replicate_results, replicate_records, sim_dir)
    seed_diagnostics_csv = _write_long_horizon_seed_diagnostics_csv(seed_diagnostics, sim_dir)
    threshold_sensitivity_csv = _write_long_horizon_threshold_sensitivity_csv(seed_diagnostics, sim_dir)
    replicate_json = data_dir / "long_horizon_replicates_summary.json"
    replicate_json.write_text(
        json.dumps(
            {
                **replicate_flat,
                "records": [asdict(r) for r in replicate_records],
                "diagnostics": [asdict(r) for r in seed_diagnostics],
                "threshold_sensitivity": [asdict(r) for r in long_horizon_threshold_sensitivity(seed_diagnostics)],
                "tc_envelope": long_horizon_tc_envelope(replicate_results),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    tc_png = plot_robustness_tc_envelopes(
        robustness_rows,
        out_path=fig_dir / "robustness_tc_envelopes.png",
        metadata=_md("plot_robustness_tc_envelopes", statistics=robustness_flat, project_root=project_root),
    )
    half_png = plot_robustness_half_saturation(
        robustness_summaries,
        out_path=fig_dir / "robustness_half_saturation.png",
        metadata=_md("plot_robustness_half_saturation", statistics=robustness_flat, project_root=project_root),
    )
    residual_png = plot_robustness_decomposition_residuals(
        robustness_summaries,
        out_path=fig_dir / "robustness_decomposition_residuals.png",
        metadata=_md("plot_robustness_decomposition_residuals", statistics=robustness_flat, project_root=project_root),
    )
    ablation_png = plot_coupling_ablation_summary(
        ablation_rows,
        out_path=fig_dir / "coupling_ablation_summary.png",
        metadata=_md("plot_coupling_ablation_summary", statistics=ablation_flat, project_root=project_root),
    )
    null_control_png = plot_marginal_null_control_summary(
        null_control_rows,
        out_path=fig_dir / "marginal_null_control_summary.png",
        metadata=_md("plot_marginal_null_control_summary", statistics=null_control_flat, project_root=project_root),
    )
    interaction_png = plot_interaction_robustness_summary(
        interaction_summaries,
        out_path=fig_dir / "interaction_robustness_summary.png",
        metadata=_md("plot_interaction_robustness_summary", statistics=interaction_flat, project_root=project_root),
    )
    replicate_png = plot_long_horizon_replicate_envelope(
        replicate_results,
        out_path=fig_dir / "long_horizon_replicate_envelope.png",
        metadata=_md("plot_long_horizon_replicate_envelope", statistics=replicate_flat, project_root=project_root),
    )
    seed_diag_png = plot_long_horizon_seed_diagnostics(
        seed_diagnostics,
        tolerance=float(H.LONG_HORIZON_STEADY_STATE_TOL),
        out_path=fig_dir / "long_horizon_seed_diagnostics.png",
        metadata=_md("plot_long_horizon_seed_diagnostics", statistics=replicate_flat, project_root=project_root),
    )
    threshold_png = plot_long_horizon_threshold_sensitivity(
        seed_diagnostics,
        thresholds=H.LONG_HORIZON_DIAGNOSTIC_THRESHOLDS,
        canonical_tolerance=float(H.LONG_HORIZON_STEADY_STATE_TOL),
        out_path=fig_dir / "long_horizon_threshold_sensitivity.png",
        metadata=_md("plot_long_horizon_threshold_sensitivity", statistics=replicate_flat, project_root=project_root),
    )

    return [
        robustness_csv,
        robustness_json,
        ablation_csv,
        ablation_json,
        null_control_csv,
        null_control_json,
        interaction_csv,
        interaction_json,
        replicate_csv,
        seed_diagnostics_csv,
        threshold_sensitivity_csv,
        replicate_json,
        tc_png,
        half_png,
        residual_png,
        ablation_png,
        null_control_png,
        interaction_png,
        replicate_png,
        seed_diag_png,
        threshold_png,
    ]


__all__ = [
    "run_robustness_pipeline",
]
