"""Shared simulation metrics with explicit semantics.

Centralises aligned-mass and half-saturation helpers that previously
lived under duplicate private names in :mod:`simulation.robustness` and
:mod:`simulation.statistics`.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

ArrayF = NDArray[np.float64]


def aligned_hypercube_mass(q: ArrayF) -> float:
    """Mass on the two fully aligned hypercube corners of a joint PMF."""

    qa = np.asarray(q, dtype=np.float64)
    lo = tuple(0 for _ in range(qa.ndim))
    hi = tuple(s - 1 for s in qa.shape)
    return float(qa[lo] + qa[hi])


def aligned_policy_mass(action_distribution: ArrayF) -> float:
    """Mass on fully aligned joint policies in lex order (size ``2^K``).

    Returns NaN when the flattened size is not a power of two.
    """

    flat = np.asarray(action_distribution, dtype=np.float64).reshape(-1)
    k = int(round(np.log2(flat.size))) if flat.size > 0 else 0
    if flat.size != 2**k:
        return float("nan")
    return float(flat[0] + flat[-1])


def half_saturation_lambda(
    lams: Sequence[float] | NDArray[np.floating],
    tcs: Sequence[float] | NDArray[np.floating],
) -> float | None:
    """First λ whose total correlation reaches half of the scenario maximum."""

    if not lams or not tcs:
        return None
    max_tc = max(float(v) for v in tcs)
    if max_tc <= 1e-12:
        return None
    target = 0.5 * max_tc
    for lam, tc in zip(lams, tcs, strict=True):
        if float(tc) >= target:
            return float(lam)
    return float(lams[-1])


def half_saturation_interpolated(
    lams: Sequence[float] | NDArray[np.floating],
    tcs: Sequence[float] | NDArray[np.floating],
) -> tuple[float, float]:
    """Half-saturation (λ, TC) by linear interpolation on the sweep grid."""

    lams_a = np.asarray(lams, dtype=np.float64)
    tcs_a = np.asarray(tcs, dtype=np.float64)
    tc_max = float(tcs_a.max())
    if tc_max <= 0.0:
        return 0.0, 0.0
    target = 0.5 * tc_max
    above = np.where(tcs_a >= target)[0]
    if above.size == 0:
        return float(lams_a[-1]), float(tcs_a[-1])
    j = int(above[0])
    if j == 0:
        return float(lams_a[0]), float(tcs_a[0])
    t0, t1 = tcs_a[j - 1], tcs_a[j]
    l0, l1 = lams_a[j - 1], lams_a[j]
    if t1 == t0:
        return float(l1), float(t1)
    frac = float((target - t0) / (t1 - t0))
    return float(l0 + frac * (l1 - l0)), float(target)


__all__ = [
    "aligned_hypercube_mass",
    "aligned_policy_mass",
    "half_saturation_interpolated",
    "half_saturation_lambda",
]
