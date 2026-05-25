"""Shared λ-loop for robustness, ablation, and interaction sweeps."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

from lean.coupling import entangled_posterior
from lean.decomposition import (
    entanglement_decomposition_rhs,
    free_energy_against_entangled_prior,
)
from lean.free_energy import shannon_entropy, total_correlation
from lean.joint_dist import joint_marginals

from .inference import per_stream_policy_posterior
from .specs import CoupledEnsembleSpec

ArrayF = NDArray[np.float64]


def rows_for_spec(
    spec: CoupledEnsembleSpec,
    observations: Sequence[int],
    lams: Sequence[float],
) -> list[tuple[float, ArrayF, float, float, float, float, float, float, float]]:
    """Shared λ-loop for robustness and ablation rows.

    Returns tuples of ``(λ, q, TC, H(q), sum H(q^k), λ<J>, lhs, rhs,
    residual)``.  The per-stream pymdp posterior is computed once per
    spec/observation pair; the decomposition uses zero per-stream G
    because pymdp has already baked EFE into that posterior.
    """

    spec.validate()
    mf = per_stream_policy_posterior(spec, observations)
    zero_g = [np.zeros_like(m, dtype=np.float64) for m in mf]
    out: list[tuple[float, ArrayF, float, float, float, float, float, float, float]] = []
    for lam_value in lams:
        lam = float(lam_value)
        q = entangled_posterior(
            mf_prior=mf,
            per_stream_G=zero_g,
            coupling_j=spec.coupling_j,
            coupling_kc=spec.coupling_kc,
            gamma=spec.gamma,
            lam=lam,
        )
        margs = joint_marginals(q)
        joint_entropy = shannon_entropy(q.reshape(-1))
        marginal_entropy_sum = float(sum(shannon_entropy(m) for m in margs))
        coupling_term = float(lam) * float(np.sum(q * spec.coupling_j))
        lhs = free_energy_against_entangled_prior(
            q,
            mf,
            zero_g,
            spec.coupling_j,
            spec.coupling_kc,
            spec.gamma,
            lam,
        )
        rhs = entanglement_decomposition_rhs(
            q,
            mf,
            zero_g,
            spec.coupling_j,
            spec.coupling_kc,
            spec.gamma,
            lam,
        ).total
        out.append(
            (
                lam,
                np.asarray(q, dtype=np.float64),
                float(total_correlation(q)),
                float(joint_entropy),
                float(marginal_entropy_sum),
                float(coupling_term),
                float(lhs),
                float(rhs),
                float(abs(lhs - rhs)),
            )
        )
    return out
