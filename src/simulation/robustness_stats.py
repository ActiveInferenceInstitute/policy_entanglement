"""Wilson interval helpers for robustness replicate summaries."""

from __future__ import annotations

import numpy as np

_Z_95_TWO_SIDED: float | None = None


def _z_95_two_sided() -> float:
    """Cached two-sided 95% normal critical value derived from scipy.

    RedTeam Methods C5 (2026-05-20): the prior hardcoded constant
    ``1.959963984540054`` was a magic number a future copy-edit could
    silently round to ``1.96`` (narrows the interval by ~5%).  We now
    derive it from ``scipy.stats.norm.ppf(0.975)`` and cache it.
    """
    global _Z_95_TWO_SIDED
    if _Z_95_TWO_SIDED is None:
        from scipy.stats import norm

        _Z_95_TWO_SIDED = float(norm.ppf(0.975))
    return _Z_95_TWO_SIDED


def wilson_score_interval(
    successes: int,
    total: int,
    *,
    z: float | None = None,
) -> tuple[float, float]:
    """Wilson score interval for a binomial pass rate.

    The default ``z`` is the two-sided 95% normal critical value
    derived live from ``scipy.stats.norm.ppf(0.975)`` (RedTeam Methods
    C5, 2026-05-20).  It is used for long-horizon replicate pass rates
    so the manuscript reports uncertainty around the observed
    sensitivity result rather than treating a small seed count as a
    tuned point estimate.
    """
    if z is None:
        z = _z_95_two_sided()

    n = int(total)
    k = int(successes)
    if n < 1:
        raise ValueError("total must be positive")
    if k < 0 or k > n:
        raise ValueError("successes must satisfy 0 <= successes <= total")
    phat = k / n
    z2 = float(z) ** 2
    denom = 1.0 + z2 / n
    center = (phat + z2 / (2.0 * n)) / denom
    radius = (float(z) / denom) * np.sqrt((phat * (1.0 - phat) / n) + (z2 / (4.0 * n * n)))
    return float(max(0.0, center - radius)), float(min(1.0, center + radius))
