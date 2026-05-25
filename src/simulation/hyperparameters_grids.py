"""Analytical figure grids and global seed constants."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

ArrayF = NDArray[np.float64]


@dataclass(frozen=True)
class FigureGrid:
    """A 1-D ``(start, stop, num)`` linspace plus a label."""

    start: float
    stop: float
    num: int
    label: str = ""

    def values(self) -> ArrayF:
        return np.linspace(self.start, self.stop, self.num)


#: 121-point grid on $[0, 6]$: closed-form Ising mutual information
#: validation against the empirical total correlation; also the
#: row count of `output/data/parameter_sweep.csv`.
PARAMETER_SWEEP_LAMBDAS = FigureGrid(0.0, 6.0, 121, label="parameter_sweep")

#: 31-point grid on $[0, 1.5]$: heterogeneous-coupling-tax envelope.
COUPLING_TAX_LAMBDAS = FigureGrid(0.0, 1.5, 31, label="coupling_tax_quadratic")

#: 401-point grid on $[0, 4]$: phase diagram fill bands.
PHASE_DIAGRAM_LAMBDAS = FigureGrid(0.0, 4.0, 401, label="phase_diagram")

#: 191-point grid on $\Delta \in [-0.95, 0.95]$: optimal coupling locus.
OPTIMAL_LAMBDA_DELTAS = FigureGrid(-0.95, 0.95, 191, label="optimal_lambda")

#: 81-point grid on $[0, 4]$: Schmidt rank vs $\lambda$.
SCHMIDT_RANK_LAMBDAS = FigureGrid(0.0, 4.0, 81, label="schmidt_rank")

#: 41-point grid on $[0, 4]$ × 21-point grid on utilities $[0, 2]$:
#: free-energy phase landscape and Schmidt entropy surface.
PHASE_LANDSCAPE_LAMBDAS = FigureGrid(0.0, 4.0, 41, label="phase_landscape_lams")
PHASE_LANDSCAPE_UTILITIES = FigureGrid(0.0, 2.0, 21, label="phase_landscape_utilities")

#: 31-point grid on $[0, 3]$: log-weight e-geodesic flow.
LOG_WEIGHT_FLOW_LAMBDAS = FigureGrid(0.0, 3.0, 31, label="log_weight_flow")

#: 21-point grid on $[0, 4]$: KL geodesic in the simplex summary plane.
KL_GEODESIC_LAMBDAS = FigureGrid(0.0, 4.0, 21, label="kl_geodesic")

#: 20-point grid on utilities $[0, 0.95]$ × 16-point grid on
#: precisions $\gamma \in [0.5, 2.0]$: $\lambda^\star$ locus.
LAMBDA_STAR_UTILITIES = FigureGrid(0.0, 0.95, 20, label="lambda_star_utility")
LAMBDA_STAR_GAMMAS = FigureGrid(0.5, 2.0, 16, label="lambda_star_gamma")

#: Deterministic seed used by `deterministic_setup` at the top of
#: the figure scripts.  Pinned so every figure is bit-reproducible.
FIGURE_GLOBAL_SEED: int = 42
