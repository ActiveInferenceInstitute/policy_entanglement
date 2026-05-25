#!/usr/bin/env python3
"""Thin CLI wrapper for the analytical-core manuscript figures.

Computation, plot assembly, and PNG emission live in
:mod:`visualizations.analytical_figures` (under ``src/``). This script
bootstraps the project's ``src/`` subpackages onto :data:`sys.path` and
forwards control to the src-side :func:`main`, which prints one absolute
path per emitted figure (manifest-collectable).

Each ``figure_*`` function is re-exported into this module's namespace so
historical test entry points that do
``importlib.import_module("generate_figures")`` and read ``OUTPUT_DIR``
continue to work without modification.

Usage::

    uv run --active python scripts/generate_figures.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
sys.path.insert(0, str(THIS_DIR))
from _bootstrap import ensure_project_paths  # noqa: E402

ensure_project_paths(project_root=PROJECT_ROOT)

from visualizations.analytical_figures import (  # noqa: E402,F401
    OUTPUT_DIR,
    emit_all_figures,
    figure_archetype_dendrogram,
    figure_coupling_graph,
    figure_coupling_tax_quadratic,
    figure_free_energy_curve,
    figure_ising_mi_curve,
    figure_joint_heatmap_with_marginals,
    figure_kl_geodesic_in_simplex,
    figure_lambda_star_locus,
    figure_log_weight_flow,
    figure_optimal_lambda,
    figure_phase_diagram,
    figure_phase_landscape,
    figure_schmidt_entropy_surface,
    figure_schmidt_rank_vs_lambda,
    figure_tensor_train_ranks,
    main,
)

__all__ = [
    "OUTPUT_DIR",
    "PROJECT_ROOT",
    "emit_all_figures",
    "figure_archetype_dendrogram",
    "figure_coupling_graph",
    "figure_coupling_tax_quadratic",
    "figure_free_energy_curve",
    "figure_ising_mi_curve",
    "figure_joint_heatmap_with_marginals",
    "figure_kl_geodesic_in_simplex",
    "figure_lambda_star_locus",
    "figure_log_weight_flow",
    "figure_optimal_lambda",
    "figure_phase_diagram",
    "figure_phase_landscape",
    "figure_schmidt_entropy_surface",
    "figure_schmidt_rank_vs_lambda",
    "figure_tensor_train_ranks",
    "main",
]


if __name__ == "__main__":
    main()
