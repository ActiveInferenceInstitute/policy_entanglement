"""Conservative interval-style bracket for Float decomposition residuals.

Tier-N numerical corroboration only: certifies that float64 pipeline
residuals on the K=2 decomposition sweep grid stay inside a Decimal
outward margin envelope.  This is **not** a Flocq IEEE-754 proof.
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal, localcontext
from typing import Any

from lean.invariants import DecompositionSweepPoint


def _decimal_interval_upper(residual: float, lhs: float, rhs_total: float) -> Decimal:
    """Outward-rounded Decimal margin around one point's float residual."""
    with localcontext() as ctx:
        ctx.prec = 50
        base = Decimal(str(residual))
        scale = max(abs(Decimal(str(lhs))), abs(Decimal(str(rhs_total))), Decimal("1"))
        margin = scale * Decimal(2) ** -50 + Decimal(2) ** -52
        return base + margin


def decomposition_interval_bracket(
    points: Sequence[DecompositionSweepPoint],
    *,
    invariant_max_residual: float,
) -> dict[str, Any]:
    """Bracket certificate for ``decomposition_lhs_eq_rhs_max_residual``.

    ``invariant_max_residual`` must come from the invariants path (e.g.
    :func:`lean.invariants.decomposition_invariants_from_points`) so
    ``decomposition_invariant_within_interval`` is a genuine two-source check.

    ``decomposition_interval_worst_lambda`` is the λ at the peak of the
    margin-widened Decimal upper bound, not necessarily the peak float residual.
    """
    if not points:
        raise ValueError("decomposition_interval_bracket requires at least one sweep point")

    max_interval = Decimal(0)
    worst_lambda = points[0].lam
    for point in points:
        point_upper = _decimal_interval_upper(point.residual, point.lhs, point.rhs_total)
        if point_upper > max_interval:
            max_interval = point_upper
            worst_lambda = point.lam

    interval_upper = float(max_interval)
    within = float(invariant_max_residual) <= interval_upper + 1e-18
    return {
        "decomposition_interval_upper": interval_upper,
        "decomposition_invariant_within_interval": within,
        "decomposition_interval_worst_lambda": worst_lambda,
        "decomposition_interval_grid_points": float(len(points)),
        "decomposition_interval_reference": "float64+decimal_outward_margin",
    }


__all__ = ["decomposition_interval_bracket"]
