"""λ-sweep utilities: aggregate the coupled posterior across a grid of"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from lean.free_energy import total_correlation
from lean.joint_dist import is_pmf, joint_marginal

from .inference import coupled_policy_posterior
from .rollout import Rollout
from .specs import CoupledEnsembleSpec

ArrayF = NDArray[np.float64]
# Callers pass either Python lists or numpy float arrays as 1-D grids.
FloatGrid = Sequence[float] | NDArray[np.float64]


@dataclass(frozen=True)
class LambdaSweepResult:
    """Bundle of every quantity collected at one λ value."""

    lam: float
    joint: ArrayF
    marginals: tuple[ArrayF, ...]
    total_correlation: float
    is_pmf: bool

    @property
    def num_streams(self) -> int:
        return len(self.marginals)


def lambda_sweep(
    spec: CoupledEnsembleSpec,
    observations: Sequence[int],
    lams: FloatGrid,
) -> list[LambdaSweepResult]:
    """Run :func:`coupled_policy_posterior` for every `lam` in `lams`,
    bundling the joint, marginals, total correlation, and PMF check.

    Determinism: the same `spec` and `observations` always produce the
    same trajectory because pymdp runs deterministic FPI by default.
    """
    out: list[LambdaSweepResult] = []
    for lam in lams:
        q = coupled_policy_posterior(spec, observations, float(lam))
        margs = tuple(joint_marginal(q, k) for k in range(q.ndim))
        out.append(
            LambdaSweepResult(
                lam=float(lam),
                joint=q,
                marginals=margs,
                total_correlation=total_correlation(q),
                is_pmf=is_pmf(q, atol=1e-7),
            )
        )
    return out


def total_correlation_curve(
    spec: CoupledEnsembleSpec,
    observations: Sequence[int],
    lams: Sequence[float],
) -> ArrayF:
    """1-D ``(len(lams),)`` array of total-correlation values across `lams`."""
    sweep = lambda_sweep(spec, observations, lams)
    return np.array([r.total_correlation for r in sweep], dtype=np.float64)


def marginal_trajectory(rollout: Rollout, k: int) -> ArrayF:
    """``(T, num_controls_k)`` time-series of stream `k`'s mean-field
    marginal across a coupled rollout.
    """
    if not 0 <= k < rollout.spec.num_streams():
        raise IndexError(f"stream {k} out of range")
    return np.stack([s.mean_field_marginals[k] for s in rollout.steps], axis=0)
