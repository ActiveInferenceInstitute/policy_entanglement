"""Publication plots for robustness, ablation, and replicate sidecars."""

from __future__ import annotations

from .robustness_plots_one_axis import (
    plot_robustness_decomposition_residuals,
    plot_robustness_half_saturation,
    plot_robustness_tc_envelopes,
)
from .robustness_plots_sidecars import (
    plot_coupling_ablation_summary,
    plot_interaction_robustness_summary,
    plot_long_horizon_replicate_envelope,
    plot_long_horizon_seed_diagnostics,
    plot_long_horizon_threshold_sensitivity,
    plot_marginal_null_control_summary,
)

__all__ = [
    "plot_coupling_ablation_summary",
    "plot_interaction_robustness_summary",
    "plot_long_horizon_replicate_envelope",
    "plot_long_horizon_seed_diagnostics",
    "plot_long_horizon_threshold_sensitivity",
    "plot_marginal_null_control_summary",
    "plot_robustness_decomposition_residuals",
    "plot_robustness_half_saturation",
    "plot_robustness_tc_envelopes",
]
