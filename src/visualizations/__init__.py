"""Reusable plotting helpers for the manuscript figures."""

from __future__ import annotations

from . import analytical_figures, pymdp_figures  # noqa: F401
from .annotations import (  # noqa: F401
    ENTROPY_LABEL,
    FREE_ENERGY_LABEL,
    GAMMA_LABEL,
    LAMBDA_LABEL,
    LAMBDA_MATH,
    MI_LABEL,
    TOTAL_CORRELATION_LABEL,
    UTILITY_LABEL,
    add_claim_strength_tag,
    add_mean_field_baseline,
    add_provenance_footer,
    add_saturation_marker,
    add_stats_box,
    add_tolerance_band,
    apply_lambda_axis,
    mark_critical_lambdas,
    pin_theorem,
)
from .free_energy_plots import (  # noqa: F401
    plot_action_distribution_evolution,
    plot_bundle_quantile_envelope,
    plot_efe_under_posterior,
    plot_entropy_decomposition,
    plot_free_energy_panel,
    plot_vfe_decomposition,
)
from .geodesic import plot_kl_geodesic_in_simplex, plot_lambda_star_locus  # noqa: F401
from .graphs import has_networkx, has_seaborn, plot_coupling_graph  # noqa: F401
from .heatmaps import (  # noqa: F401
    plot_lambda_utility_heatmap,
    plot_schmidt_entropy_surface,
)
from .joint_plots import plot_joint_heatmap_with_marginals  # noqa: F401
from .log_weight import plot_log_weight_flow  # noqa: F401
from .metadata import (  # noqa: F401
    figure_metadata,
    figure_statistics,
    has_project_metadata,
    read_figure_metadata,
    summarize_array,
)
from .multi_k_plots import (  # noqa: F401
    plot_long_horizon_marginals,
    plot_long_horizon_steady_state,
    plot_multi_k_aligned_mass,
    plot_multi_k_total_correlation,
    plot_multi_k_tt_rank_profile,
    plot_revertibility_witness,
)
from .pymdp_extras import (  # noqa: F401
    plot_action_entropy_curve,
    plot_kl_to_lambda_zero,
    plot_marginal_entropy_per_stream,
    plot_pymdp_summary_panel,
)
from .robustness_plots import (  # noqa: F401
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
from .setup import deterministic_setup, ensure_outdir  # noqa: F401
from .spectral_plots import (  # noqa: F401
    plot_archetype_dendrogram,
    plot_tensor_train_rank_surface,
)
from .trajectory_plots import plot_rollout_marginals  # noqa: F401

__all__ = [
    "plot_vfe_decomposition",
    "plot_efe_under_posterior",
    "plot_entropy_decomposition",
    "plot_action_distribution_evolution",
    "plot_free_energy_panel",
    "plot_bundle_quantile_envelope",
    "figure_metadata",
    "figure_statistics",
    "summarize_array",
    "read_figure_metadata",
    "has_project_metadata",
    "plot_action_entropy_curve",
    "plot_kl_to_lambda_zero",
    "plot_marginal_entropy_per_stream",
    "plot_pymdp_summary_panel",
    "plot_coupling_ablation_summary",
    "plot_interaction_robustness_summary",
    "plot_long_horizon_replicate_envelope",
    "plot_long_horizon_seed_diagnostics",
    "plot_long_horizon_threshold_sensitivity",
    "plot_marginal_null_control_summary",
    "plot_robustness_decomposition_residuals",
    "plot_robustness_half_saturation",
    "plot_robustness_tc_envelopes",
    "deterministic_setup",
    "ensure_outdir",
    "plot_lambda_utility_heatmap",
    "plot_schmidt_entropy_surface",
    "plot_joint_heatmap_with_marginals",
    "plot_archetype_dendrogram",
    "plot_tensor_train_rank_surface",
    "plot_rollout_marginals",
    "has_networkx",
    "has_seaborn",
    "plot_coupling_graph",
    "plot_log_weight_flow",
    "plot_kl_geodesic_in_simplex",
    "plot_lambda_star_locus",
    # Annotation helpers (apply consistent visual conventions)
    "apply_lambda_axis",
    "pin_theorem",
    "add_provenance_footer",
    "mark_critical_lambdas",
    "add_stats_box",
    "add_mean_field_baseline",
    "add_tolerance_band",
    "add_saturation_marker",
    "add_claim_strength_tag",
    "LAMBDA_LABEL",
    "LAMBDA_MATH",
    "UTILITY_LABEL",
    "GAMMA_LABEL",
    "FREE_ENERGY_LABEL",
    "MI_LABEL",
    "TOTAL_CORRELATION_LABEL",
    "ENTROPY_LABEL",
    # K>2 / long-horizon / revertibility figures
    "plot_long_horizon_marginals",
    "plot_long_horizon_steady_state",
    "plot_multi_k_aligned_mass",
    "plot_multi_k_total_correlation",
    "plot_multi_k_tt_rank_profile",
    "plot_revertibility_witness",
    # Manuscript figure suites (importable orchestrators)
    "analytical_figures",
    "pymdp_figures",
]
