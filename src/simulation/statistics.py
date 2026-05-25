"""Summary statistics derived from a sequence of pymdp-grounded
:class:`FreeEnergyBundle` records.

These quantities feed the manuscript's auto-injected variable table:
each summary scalar is mirrored into
``output/data/manuscript_variables.json`` and substituted into prose
via ``[[VAR:key]]`` — no value reaches the manuscript by hand.

Pure functions — given a list of bundles (and optional reference
distributions), they return a flat dict of numeric scalars.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from lean.free_energy import shannon_entropy as _shannon

from .inference import FreeEnergyBundle
from .metrics import aligned_policy_mass, half_saturation_interpolated

ArrayF = NDArray[np.float64]


@dataclass(frozen=True)
class BundleSummary:
    """A flat snapshot of every scalar we want to talk about.

    Field order is stable; field names map 1:1 to the JSON keys
    emitted by `pymdp_summary_statistics(...)`.
    """

    n_lambda_points: int
    lambda_min: float
    lambda_max: float

    tc_min: float
    tc_max: float
    tc_mean: float
    tc_at_half_saturation: float
    lambda_at_half_saturation: float

    vfe_total_min: float
    vfe_total_max: float
    vfe_total_mean: float

    coupling_term_min: float
    coupling_term_max: float

    joint_entropy_min: float
    joint_entropy_max: float

    aligned_mass_min: float
    aligned_mass_max: float
    aligned_mass_at_lambda_max: float

    kl_to_lambda_zero_min: float
    kl_to_lambda_zero_max: float
    kl_to_uniform_at_lambda_max: float

    action_entropy_min: float
    action_entropy_max: float
    action_mode_prob_at_lambda_max: float


def _kl(p: ArrayF, q: ArrayF) -> float:
    """Lenient KL: floor on zero entries in `q` is ``1e-300`` rather than
    raising to ``+inf`` (cf. :func:`lean.free_energy.kl_divergence`).
    Kept local because the absolute-continuity-tolerant variant is what
    the action-distribution / pymdp-summary statistics need.
    """
    pa = np.asarray(p, dtype=np.float64).reshape(-1)
    qa = np.asarray(q, dtype=np.float64).reshape(-1)
    mask = pa > 0.0
    return float((pa[mask] * (np.log(pa[mask]) - np.log(np.where(qa[mask] > 0.0, qa[mask], 1e-300)))).sum())


# Note: ``_shannon`` is imported at top from :mod:`lean.free_energy` to
# avoid a private-helper duplicate; same masking and floor semantics.


def _aligned_mass(action_distribution: ArrayF) -> float:
    return aligned_policy_mass(action_distribution)


def _half_saturation(
    lams: Sequence[float] | NDArray[np.floating],
    tcs: Sequence[float] | NDArray[np.floating],
) -> tuple[float, float]:
    return half_saturation_interpolated(lams, tcs)


def pymdp_summary_statistics(
    bundles: Sequence[FreeEnergyBundle],
) -> BundleSummary:
    """Reduce a list of `FreeEnergyBundle` records to a single
    summary record (one scalar per field).

    Every field is real numeric, derived directly from the bundle
    fields without any external state.  At least two bundles are
    required (so min / max / mean are well-defined).
    """
    if len(bundles) < 2:
        raise ValueError("need at least 2 bundles for summary statistics")

    lams = np.array([b.lam for b in bundles], dtype=np.float64)
    tcs = np.array([b.total_correlation for b in bundles], dtype=np.float64)
    vfe = np.array([b.vfe_total for b in bundles], dtype=np.float64)
    coup = np.array([b.coupling_term for b in bundles], dtype=np.float64)
    Hjoint = np.array([b.joint_entropy for b in bundles], dtype=np.float64)
    aligned = np.array(
        [_aligned_mass(b.action_distribution) for b in bundles],
        dtype=np.float64,
    )
    action_H = np.array(
        [_shannon(b.action_distribution) for b in bundles],
        dtype=np.float64,
    )
    action_mode = np.array(
        [float(np.asarray(b.action_distribution).reshape(-1).max()) for b in bundles],
        dtype=np.float64,
    )

    q0 = np.asarray(bundles[0].action_distribution, dtype=np.float64).reshape(-1)
    q0_norm = q0 / q0.sum() if q0.sum() > 0 else q0
    qN = np.asarray(bundles[-1].action_distribution, dtype=np.float64).reshape(-1)
    qN_norm = qN / qN.sum() if qN.sum() > 0 else qN
    uniform = np.full_like(qN_norm, 1.0 / qN_norm.size)
    kl_to_q0 = np.array(
        [
            _kl(
                np.asarray(b.action_distribution).reshape(-1)
                / max(float(np.asarray(b.action_distribution).sum()), 1e-300),
                q0_norm,
            )
            for b in bundles
        ],
        dtype=np.float64,
    )
    kl_uniform_at_max = _kl(qN_norm, uniform)

    lam_half, tc_half = _half_saturation(lams, tcs)

    return BundleSummary(
        n_lambda_points=int(lams.size),
        lambda_min=float(lams[0]),
        lambda_max=float(lams[-1]),
        tc_min=float(tcs.min()),
        tc_max=float(tcs.max()),
        tc_mean=float(tcs.mean()),
        tc_at_half_saturation=float(tc_half),
        lambda_at_half_saturation=float(lam_half),
        vfe_total_min=float(vfe.min()),
        vfe_total_max=float(vfe.max()),
        vfe_total_mean=float(vfe.mean()),
        coupling_term_min=float(coup.min()),
        coupling_term_max=float(coup.max()),
        joint_entropy_min=float(Hjoint.min()),
        joint_entropy_max=float(Hjoint.max()),
        aligned_mass_min=float(aligned.min()),
        aligned_mass_max=float(aligned.max()),
        aligned_mass_at_lambda_max=float(aligned[-1]),
        kl_to_lambda_zero_min=float(kl_to_q0.min()),
        kl_to_lambda_zero_max=float(kl_to_q0.max()),
        kl_to_uniform_at_lambda_max=float(kl_uniform_at_max),
        action_entropy_min=float(action_H.min()),
        action_entropy_max=float(action_H.max()),
        action_mode_prob_at_lambda_max=float(action_mode[-1]),
    )


def summary_to_var_dict(summary: BundleSummary, *, prefix: str = "pymdp") -> dict[str, float]:
    """Flatten a `BundleSummary` to a dict of `<prefix>_<field>` keys
    suitable for direct merge into ``manuscript_variables.json``.
    """
    out: dict[str, float] = {}
    for name in summary.__dataclass_fields__:
        out[f"{prefix}_summary_{name}"] = float(getattr(summary, name))
    return out


# ---------------------------------------------------------------------------
# Multi-seed / multi-sweep aggregation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class QuantileEnvelope:
    """Per-grid-point quantile statistics over a stack of sweeps.

    Each field is shape ``(n_lambda_points,)`` aligned with ``lams``.
    Used to summarize the variability of an observable (e.g. total
    correlation) across multiple seeds or perturbed runs of the same
    sweep grid.
    """

    lams: ArrayF
    median: ArrayF
    lower: ArrayF  # default 0.25 quantile
    upper: ArrayF  # default 0.75 quantile
    minimum: ArrayF
    maximum: ArrayF
    n_runs: int
    quantile_lower: float
    quantile_upper: float


def quantile_envelope_over_sweeps(
    sweeps: Sequence[Sequence[FreeEnergyBundle]],
    *,
    field: str = "total_correlation",
    quantile_lower: float = 0.25,
    quantile_upper: float = 0.75,
) -> QuantileEnvelope:
    """Aggregate a stack of bundle sweeps into a quantile envelope.

    Every sweep must share the same ``λ`` grid (length and values) so
    the quantiles are well-defined per grid point.

    Args:
        sweeps: One inner list per run; each inner list is a sweep
            of :class:`FreeEnergyBundle` records sharing the same
            ``λ`` grid.
        field: Bundle attribute to aggregate. Must name a scalar
            attribute on :class:`FreeEnergyBundle` (e.g. ``"vfe_total"``,
            ``"total_correlation"``, ``"joint_entropy"``).
        quantile_lower: Lower quantile (default ``0.25``).
        quantile_upper: Upper quantile (default ``0.75``).

    Returns:
        :class:`QuantileEnvelope` with ``median``/``lower``/``upper``/
        ``minimum``/``maximum`` arrays of length ``len(sweeps[0])``.

    Raises:
        ValueError: if ``sweeps`` is empty, ``λ`` grids disagree, or
            quantile bounds are out of order.
    """
    if not (0.0 <= quantile_lower < quantile_upper <= 1.0):
        raise ValueError(
            f"expected 0 <= quantile_lower < quantile_upper <= 1; got ({quantile_lower}, {quantile_upper})"
        )
    if len(sweeps) == 0:
        raise ValueError("need at least one sweep")
    n_grid = len(sweeps[0])
    if n_grid < 2:
        raise ValueError("each sweep must contain at least 2 grid points")
    lams_ref = np.array([b.lam for b in sweeps[0]], dtype=np.float64)
    stack = np.empty((len(sweeps), n_grid), dtype=np.float64)
    for i, sweep in enumerate(sweeps):
        if len(sweep) != n_grid:
            raise ValueError(f"sweep {i} has {len(sweep)} grid points; expected {n_grid}")
        lams_i = np.array([b.lam for b in sweep], dtype=np.float64)
        if not np.allclose(lams_i, lams_ref, atol=1e-12):
            raise ValueError(
                f"sweep {i} λ-grid disagrees with sweep 0 (max |Δλ| = {float(np.max(np.abs(lams_i - lams_ref))):.3e})"
            )
        for j, b in enumerate(sweep):
            try:
                value = getattr(b, field)
            except AttributeError as exc:  # pragma: no cover
                raise ValueError(f"FreeEnergyBundle has no field '{field}'") from exc
            stack[i, j] = float(value)

    return QuantileEnvelope(
        lams=lams_ref,
        median=np.median(stack, axis=0),
        lower=np.quantile(stack, quantile_lower, axis=0),
        upper=np.quantile(stack, quantile_upper, axis=0),
        minimum=stack.min(axis=0),
        maximum=stack.max(axis=0),
        n_runs=len(sweeps),
        quantile_lower=float(quantile_lower),
        quantile_upper=float(quantile_upper),
    )


def is_monotone_nondecreasing(
    values: Sequence[float] | NDArray[np.floating],
    *,
    atol: float = 1e-9,
) -> bool:
    """Return ``True`` iff ``values`` is non-decreasing within tolerance.

    A direct numerical witness for monotone-in-|λ| claims (Theorems 4.1,
    7.1, etc.). Tolerance ``atol`` defends against floating-point drift
    on near-flat segments.
    """
    arr = np.asarray(values, dtype=np.float64)
    if arr.size < 2:
        return True
    diffs = np.diff(arr)
    return bool(np.all(diffs >= -atol))


def total_correlation_saturation_index(
    bundles: Sequence[FreeEnergyBundle],
    *,
    saturation_fraction: float = 0.95,
) -> float:
    """Smallest λ on the sweep where TC reaches ``saturation_fraction × max(TC)``.

    Returns ``+inf`` if the sweep never reaches that level, e.g.
    when the maximum TC over the grid is already below
    ``saturation_fraction × max(TC)`` due to a degenerate sweep
    (saturation_fraction approaching 1 with a near-flat TC curve).

    Use:
        >>> idx = total_correlation_saturation_index(bundles, saturation_fraction=0.9)

    A finite return value is the natural quantitative answer to "by
    what λ has the coupling done most of its work?"
    """
    if not (0.0 < saturation_fraction <= 1.0):
        raise ValueError("saturation_fraction must be in (0, 1]")
    if len(bundles) < 2:
        raise ValueError("need at least 2 bundles")
    lams = np.array([b.lam for b in bundles], dtype=np.float64)
    tcs = np.array([b.total_correlation for b in bundles], dtype=np.float64)
    tc_max = float(tcs.max())
    if tc_max <= 0.0:
        return float("inf")
    target = saturation_fraction * tc_max
    above = np.where(tcs >= target)[0]
    if above.size == 0:  # pragma: no cover — unreachable: tcs.max() is always in above
        return float("inf")
    return float(lams[int(above[0])])
