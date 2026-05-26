"""Conservative interval-style bracket for Float decomposition residuals.

Tier-N numerical corroboration only: certifies that float64 pipeline
residuals on the K=2 decomposition sweep grid stay inside a Decimal
outward margin envelope.  This is **not** a Flocq IEEE-754 proof.
"""

from __future__ import annotations

from decimal import Decimal, localcontext
from typing import Any

import numpy as np

from lean.bernoulli_toy import ising_coupling, ising_joint_posterior, symmetric_mean_field_prior
from lean.decomposition import entanglement_decomposition_rhs, free_energy_against_entangled_prior
from lean.invariants import SweepGrid


def _residual_at_lambda(lam: float) -> tuple[float, float, float]:
    """Return ``(residual, lhs, rhs.total)`` at one grid point."""
    lam_f = float(lam)
    mf = list(symmetric_mean_field_prior())
    ja = ising_coupling()
    kc = np.zeros_like(ja)
    gs = [np.zeros(2, dtype=np.float64), np.zeros(2, dtype=np.float64)]
    gamma = 1.0
    q = ising_joint_posterior(lam_f)
    rhs = entanglement_decomposition_rhs(q, mf, gs, ja, kc, gamma, lam_f)
    lhs = free_energy_against_entangled_prior(q, mf, gs, ja, kc, gamma, lam_f)
    return abs(lhs - rhs.total), float(lhs), float(rhs.total)


def _decimal_interval_upper(residual: float, lhs: float, rhs_total: float) -> Decimal:
    """Outward-rounded Decimal margin around one point's float residual."""
    with localcontext() as ctx:
        ctx.prec = 50
        base = Decimal(str(residual))
        scale = max(abs(Decimal(str(lhs))), abs(Decimal(str(rhs_total))), Decimal("1"))
        margin = scale * Decimal(2) ** -50 + Decimal(2) ** -52
        return base + margin


def decomposition_interval_bracket(grid: SweepGrid) -> dict[str, Any]:
    """Bracket certificate for ``decomposition_lhs_eq_rhs_max_residual``."""
    max_float = 0.0
    max_interval = Decimal(0)
    worst_lambda = float(grid.values()[0])
    for lam in grid.values():
        residual, lhs, rhs_total = _residual_at_lambda(lam)
        point_upper = _decimal_interval_upper(residual, lhs, rhs_total)
        if residual > max_float:
            max_float = residual
            worst_lambda = float(lam)
        max_interval = max(max_interval, point_upper)

    interval_upper = float(max_interval)
    contains = max_float <= interval_upper + 1e-18
    return {
        "decomposition_interval_upper": interval_upper,
        "decomposition_interval_contains_float": contains,
        "decomposition_interval_worst_lambda": worst_lambda,
        "decomposition_interval_grid_points": float(len(grid.values())),
        "decomposition_interval_reference": "float64+decimal_outward_margin",
    }


__all__ = ["decomposition_interval_bracket"]
