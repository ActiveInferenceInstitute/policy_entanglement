"""Robustness, ablation, and long-horizon replicate sidecar pipeline.

Business logic for ``scripts/simulate_robustness.py``. The script remains
a thin orchestrator that calls :func:`run_robustness_pipeline`; this
module owns pipeline glue around numerical helpers in
:mod:`simulation.robustness`, CSV/JSON emission in
:mod:`simulation.robustness_emit`, and plotting helpers in
:mod:`visualizations.robustness_plots`.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

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
from .robustness_emit import (
    figure_metadata_dict,
    write_ablation_csv,
    write_interaction_csv,
    write_long_horizon_replicate_csv,
    write_long_horizon_seed_diagnostics_csv,
    write_long_horizon_threshold_sensitivity_csv,
    write_marginal_null_control_csv,
    write_robustness_csv,
)


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
    robustness_csv = write_robustness_csv(robustness_rows, sim_dir)
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
    ablation_csv = write_ablation_csv(ablation_rows, sim_dir)
    ablation_json = data_dir / "coupling_ablation_summary.json"
    ablation_json.write_text(json.dumps(ablation_flat, indent=2, sort_keys=True) + "\n")

    null_control_rows = run_marginal_null_control()
    null_control_flat = summarize_marginal_null_control_rows(null_control_rows)
    null_control_csv = write_marginal_null_control_csv(null_control_rows, sim_dir)
    null_control_json = data_dir / "marginal_null_control_summary.json"
    null_control_json.write_text(json.dumps(null_control_flat, indent=2, sort_keys=True) + "\n")

    def _interaction_progress(idx: int, total: int, scenario) -> None:
        print(f"[interaction-robustness] scenario {idx}/{total}: {scenario.scenario_id}", flush=True)

    interaction_rows = run_interaction_robustness_suite(progress_callback=_interaction_progress)
    interaction_summaries, interaction_flat = summarize_interaction_robustness_rows(interaction_rows)
    interaction_csv = write_interaction_csv(interaction_rows, sim_dir)
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
    replicate_csv = write_long_horizon_replicate_csv(replicate_results, replicate_records, sim_dir)
    seed_diagnostics_csv = write_long_horizon_seed_diagnostics_csv(seed_diagnostics, sim_dir)
    threshold_sensitivity_csv = write_long_horizon_threshold_sensitivity_csv(seed_diagnostics, sim_dir)
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

    def md(fn: str, stats: dict[str, float]) -> dict[str, str]:
        return figure_metadata_dict(fn, statistics=stats, project_root=project_root)

    tc_png = plot_robustness_tc_envelopes(
        robustness_rows,
        out_path=fig_dir / "robustness_tc_envelopes.png",
        metadata=md("plot_robustness_tc_envelopes", robustness_flat),
    )
    half_png = plot_robustness_half_saturation(
        robustness_summaries,
        out_path=fig_dir / "robustness_half_saturation.png",
        metadata=md("plot_robustness_half_saturation", robustness_flat),
    )
    residual_png = plot_robustness_decomposition_residuals(
        robustness_summaries,
        out_path=fig_dir / "robustness_decomposition_residuals.png",
        metadata=md("plot_robustness_decomposition_residuals", robustness_flat),
    )
    ablation_png = plot_coupling_ablation_summary(
        ablation_rows,
        out_path=fig_dir / "coupling_ablation_summary.png",
        metadata=md("plot_coupling_ablation_summary", ablation_flat),
    )
    null_control_png = plot_marginal_null_control_summary(
        null_control_rows,
        out_path=fig_dir / "marginal_null_control_summary.png",
        metadata=md("plot_marginal_null_control_summary", null_control_flat),
    )
    interaction_png = plot_interaction_robustness_summary(
        interaction_summaries,
        out_path=fig_dir / "interaction_robustness_summary.png",
        metadata=md("plot_interaction_robustness_summary", interaction_flat),
    )
    replicate_png = plot_long_horizon_replicate_envelope(
        replicate_results,
        out_path=fig_dir / "long_horizon_replicate_envelope.png",
        metadata=md("plot_long_horizon_replicate_envelope", replicate_flat),
    )
    seed_diag_png = plot_long_horizon_seed_diagnostics(
        seed_diagnostics,
        tolerance=float(H.LONG_HORIZON_STEADY_STATE_TOL),
        out_path=fig_dir / "long_horizon_seed_diagnostics.png",
        metadata=md("plot_long_horizon_seed_diagnostics", replicate_flat),
    )
    threshold_png = plot_long_horizon_threshold_sensitivity(
        seed_diagnostics,
        thresholds=H.LONG_HORIZON_DIAGNOSTIC_THRESHOLDS,
        canonical_tolerance=float(H.LONG_HORIZON_STEADY_STATE_TOL),
        out_path=fig_dir / "long_horizon_threshold_sensitivity.png",
        metadata=md("plot_long_horizon_threshold_sensitivity", replicate_flat),
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
