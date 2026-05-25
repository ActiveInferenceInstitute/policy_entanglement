"""Robustness and coupling-ablation stress-test hyperparameters."""

from __future__ import annotations

from simulation.hyperparameters_grids import FigureGrid

#: One-axis-at-a-time observation-context perturbations for the
#: reviewer-facing robustness suite.  The canonical static pymdp sweep
#: uses :data:`PYMDP_SWEEP_OBSERVATIONS`; these contexts test whether
#: the total-correlation and decomposition witnesses survive all four
#: binary observation cases without expanding to a full Cartesian grid.
ROBUSTNESS_OBSERVATION_CONTEXTS: tuple[tuple[int, ...], ...] = (
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1),
)

#: One-axis-at-a-time EFE precision values for robustness sweeps.
ROBUSTNESS_GAMMAS: tuple[float, ...] = (0.5, 1.0, 2.0)

#: One-axis-at-a-time prior-preference strengths for robustness sweeps.
ROBUSTNESS_PREFERENCE_STRENGTHS: tuple[float, ...] = (0.5, 1.0, 2.0)

#: One-axis-at-a-time Ising coupling-scale values for robustness
#: sweeps; the ``0.0`` row is the null-coupling flatline sentinel.
ROBUSTNESS_COUPLING_SCALES: tuple[float, ...] = (0.0, 0.5, 1.0, 1.5)

#: Appendix-only targeted two-axis interaction families.  These avoid
#: the full Cartesian product while testing the three most review-
#: relevant interactions: observation context with coupling scale,
#: precision with preference strength, and coupling variant with
#: coupling scale.
ROBUSTNESS_INTERACTION_FAMILIES: tuple[str, ...] = (
    "observation_x_coupling_scale",
    "gamma_x_preference_strength",
    "coupling_variant_x_coupling_scale",
)

#: λ grid for the robustness and coupling-ablation experiments.  It is
#: intentionally identical in shape to the canonical pymdp sweep but
#: named separately so figure metadata can distinguish stress tests
#: from the main sweep.
ROBUSTNESS_SWEEP_LAMBDAS = FigureGrid(0.0, 4.0, 21, label="robustness_sweep")

#: Fixed coupling-ablation variants.  ``heterogeneous_kc`` uses the
#: small signed tax matrix below while keeping the aligned Ising prior.
COUPLING_ABLATION_VARIANTS: tuple[str, ...] = (
    "aligned",
    "null",
    "anti_aligned",
    "heterogeneous_kc",
)

#: Small cross-stream tax matrix used by the heterogeneous ablation.
COUPLING_ABLATION_KC_MATRIX: tuple[tuple[float, float], tuple[float, float]] = (
    (0.2, -0.1),
    (-0.1, 0.2),
)
