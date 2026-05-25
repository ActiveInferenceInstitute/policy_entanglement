"""Coupling ablation and fixed-marginal null-control suites."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

from lean.free_energy import total_correlation
from lean.joint_dist import joint_marginals

from . import hyperparameters as H  # noqa: N812
from .metrics import aligned_hypercube_mass as _aligned_mass
from .robustness_core import rows_for_spec
from .robustness_scenarios import (
    CouplingAblationRow,
    MarginalNullControlRow,
    _product_of_marginals,
    coupling_ablation_spec,
)

FloatGrid = Sequence[float] | NDArray[np.float64]


def run_coupling_ablation(lams: FloatGrid | None = None) -> list[CouplingAblationRow]:
    """Run the four configured coupling-ablation variants."""

    grid = [float(x) for x in (H.ROBUSTNESS_SWEEP_LAMBDAS.values() if lams is None else lams)]
    rows: list[CouplingAblationRow] = []
    observations = tuple(int(x) for x in H.PYMDP_SWEEP_OBSERVATIONS)
    for variant in H.COUPLING_ABLATION_VARIANTS:
        spec = coupling_ablation_spec(variant)
        for lam, q, tc, joint_h, marg_h, coupling_term, lhs, rhs, residual in rows_for_spec(
            spec,
            observations,
            grid,
        ):
            rows.append(
                CouplingAblationRow(
                    variant=variant,
                    lam=lam,
                    total_correlation=tc,
                    joint_entropy=joint_h,
                    marginal_entropy_sum=marg_h,
                    coupling_term=coupling_term,
                    aligned_mass=_aligned_mass(q),
                    decomposition_lhs=lhs,
                    decomposition_rhs=rhs,
                    decomposition_residual=residual,
                )
            )
    return rows


def run_marginal_null_control(lams: FloatGrid | None = None) -> list[MarginalNullControlRow]:
    """Run a fixed-marginal independence control for the canonical sweep."""

    grid = [float(x) for x in (H.ROBUSTNESS_SWEEP_LAMBDAS.values() if lams is None else lams)]
    spec = coupling_ablation_spec("aligned")
    observations = tuple(int(x) for x in H.PYMDP_SWEEP_OBSERVATIONS)
    rows: list[MarginalNullControlRow] = []
    for lam, q, tc, _joint_h, _marg_h, _coupling_term, _lhs, _rhs, _residual in rows_for_spec(
        spec,
        observations,
        grid,
    ):
        null_q = _product_of_marginals(joint_marginals(q))
        null_tc = float(total_correlation(null_q))
        original_mass = _aligned_mass(q)
        null_mass = _aligned_mass(null_q)
        rows.append(
            MarginalNullControlRow(
                lam=float(lam),
                original_total_correlation=float(tc),
                null_total_correlation=null_tc,
                original_aligned_mass=original_mass,
                null_aligned_mass=null_mass,
                tc_removed=float(tc - null_tc),
                aligned_mass_shift=float(original_mass - null_mass),
            )
        )
    return rows


def summarize_coupling_ablation_rows(rows: Sequence[CouplingAblationRow]) -> dict[str, float]:
    """Flat manuscript-variable summary for the ablation suite."""

    if not rows:
        raise ValueError("rows must be non-empty")
    variants = sorted({r.variant for r in rows})
    lambda_zero_rows = [r for r in rows if abs(r.lam) <= 1e-12]
    final_rows = [max((r for r in rows if r.variant == variant), key=lambda r: r.lam) for variant in variants]
    flat: dict[str, float] = {
        "coupling_ablation_variant_count": float(len(variants)),
        "coupling_ablation_row_count": float(len(rows)),
        "coupling_ablation_decomposition_residual_max": float(max(r.decomposition_residual for r in rows)),
        "coupling_ablation_lambda_zero_tc_max": float(
            max((r.total_correlation for r in lambda_zero_rows), default=0.0)
        ),
        "coupling_ablation_aligned_mass_shift": float(
            max(r.aligned_mass for r in final_rows) - min(r.aligned_mass for r in final_rows)
        ),
    }
    for variant in variants:
        group = [r for r in rows if r.variant == variant]
        key = variant.replace("-", "_")
        flat[f"coupling_ablation_{key}_tc_max"] = float(max(r.total_correlation for r in group))
        flat[f"coupling_ablation_{key}_aligned_mass_at_lambda_max"] = float(
            max(group, key=lambda r: r.lam).aligned_mass
        )
    return flat


def summarize_marginal_null_control_rows(rows: Sequence[MarginalNullControlRow]) -> dict[str, float]:
    """Flat manuscript-variable summary for the fixed-marginal null control."""

    if not rows:
        raise ValueError("rows must be non-empty")
    return {
        "robustness_null_control_row_count": float(len(rows)),
        "robustness_null_control_max_tc": float(max(r.null_total_correlation for r in rows)),
        "robustness_null_control_tc_removed_max": float(max(r.tc_removed for r in rows)),
        "robustness_null_control_aligned_mass_shift_max": float(max(abs(r.aligned_mass_shift) for r in rows)),
        "robustness_null_control_original_tc_max": float(max(r.original_total_correlation for r in rows)),
        # RedTeam 2026-05-19 C3 — the DISCRIMINATING metric. Over rows
        # that actually carry coupling (original_tc > 1e-6), the fraction
        # of multi-information the null control removes must be ≈ 1; the
        # min across them is gated to [1−1e-6, 1+1e-6]. A control that
        # leaves coupling (mis-marginalised) yields a fraction < 1; if no
        # row carries coupling the metric is 0.0 → also fails (the
        # control never exercised what it claims to neutralise). This is
        # the quantity `tc_removed_max (0,inf)` failed to constrain.
        "robustness_null_control_tc_removed_fraction_min": float(
            min(
                (r.tc_removed / r.original_total_correlation for r in rows if r.original_total_correlation > 1e-6),
                default=0.0,
            )
        ),
    }
