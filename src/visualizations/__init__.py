"""Reusable plotting helpers for the manuscript figures.
"""

from __future__ import annotations

from setup import deterministic_setup, ensure_outdir  # noqa: F401
from heatmaps import (  # noqa: F401
    plot_lambda_utility_heatmap,
    plot_schmidt_entropy_surface,
)
from joint_plots import plot_joint_heatmap_with_marginals  # noqa: F401
from spectral_plots import (  # noqa: F401
    plot_archetype_dendrogram,
    plot_tensor_train_rank_surface,
)
from trajectory_plots import plot_rollout_marginals  # noqa: F401
from graphs import has_networkx, has_seaborn, plot_coupling_graph  # noqa: F401
from log_weight import plot_log_weight_flow  # noqa: F401
from geodesic import plot_kl_geodesic_in_simplex, plot_lambda_star_locus  # noqa: F401

__all__ = [
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
]
