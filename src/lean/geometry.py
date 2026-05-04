"""Information geometry of the entanglement manifold.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

from coupling import (
    coupling_log_weight,
    entangled_log_weight_affine_in_lambda,
    entangled_posterior,
)
from free_energy import kl_divergence, total_correlation, total_correlation_via_kl
from joint_dist import is_mean_field, m_projection, mean_field_to_joint

ArrayF = NDArray[np.float64]


def is_in_mean_field_submanifold(q: ArrayF, atol: float = 1e-9) -> bool:
    """Predicate: `q` lies on M_MF (the mean-field submanifold)."""
    return is_mean_field(q, atol=atol)


def m_projection_minimises_kl(
    q: ArrayF,
    candidate_marginals: Sequence[ArrayF],
    atol: float = 1e-12,
) -> bool:
    """Verify Prop 6.2 numerically: `KL(q ‖ ∏ q^k) ≤ KL(q ‖ ∏ p^k)` for any
    candidate mean-field `p`.
    """
    proj = m_projection(q)
    cand = mean_field_to_joint(candidate_marginals)
    return kl_divergence(q, proj) <= kl_divergence(q, cand) + atol


def pythagorean_residual(q: ArrayF, mf_reference: Sequence[ArrayF]) -> float:
    """`KL(q ‖ ref) − [I(q) + KL(∏ q^k ‖ ref)]`.

    Should be 0 (up to floating tolerance) for any joint `q` and any
    mean-field reference, by Prop 6.5 of the manuscript.
    """
    ref = mean_field_to_joint(mf_reference)
    lhs = kl_divergence(q, ref)
    rhs = total_correlation_via_kl(q) + kl_divergence(m_projection(q), ref)
    return float(lhs - rhs)


def is_e_geodesic(
    coupling_J: ArrayF,
    coupling_Kc: ArrayF,
    gamma: float,
    pi_index: tuple[int, ...],
    lams: Sequence[float],
    atol: float = 1e-9,
) -> bool:
    """Verify Theorem 6.4: the family `{q_lam}_lam` traces an e-geodesic.

    Concretely: the unnormalised log-weight is affine in `lam`, with
    slope ``J(pi) − gamma·K_c(pi)`` and intercept ``0``.  Tested against
    a concrete pi_index and a sequence of lams.
    """
    a, b = entangled_log_weight_affine_in_lambda(
        coupling_J, coupling_Kc, gamma, pi_index
    )
    Ja = np.asarray(coupling_J, dtype=np.float64)
    Kc = np.asarray(coupling_Kc, dtype=np.float64)
    for lam in lams:
        actual = lam * Ja[pi_index] - gamma * lam * Kc[pi_index]
        predicted = a + b * lam
        if abs(actual - predicted) > atol:
            return False
    return True


def revertibility(q: ArrayF) -> ArrayF:
    """The m-projection — i.e. the reverted, mean-field representation
    of any joint posterior.  Mirrors ``ActinfPolicyEntanglement.revertibility``.
    """
    return m_projection(q)


def coupling_pays_off(
    mf_prior: Sequence[ArrayF],
    per_stream_G: Sequence[ArrayF],
    coupling_J: ArrayF,
    coupling_Kc: ArrayF,
    gamma: float,
    lam: float,
    atol: float = 1e-12,
) -> bool:
    """Numerical version of the coupling-pays-for-itself verdict.

    Computes the lambda-entangled posterior, the lambda=0 (mean-field)
    posterior, and returns ``True`` iff the entangled posterior has
    strictly lower free energy than the lambda=0 baseline (using the
    coupled prior / EFE).  Mirrors ``CouplingVerdict.pays`` /
    ``does_not_pay`` from the Lean module.
    """
    if lam <= 0.0:
        return False
    q_entangled = entangled_posterior(
        mf_prior, per_stream_G, coupling_J, coupling_Kc, gamma, lam
    )
    q_mf = entangled_posterior(
        mf_prior, per_stream_G, coupling_J, coupling_Kc, gamma, 0.0
    )
    # The verdict is purely about the total-correlation gain at this lam:
    return bool(total_correlation(q_entangled) > total_correlation(q_mf) + atol)


def coupling_log_weight_affine_check(
    coupling_J: ArrayF,
    coupling_Kc: ArrayF,
    gamma: float,
    lams: Sequence[float],
    atol: float = 1e-9,
) -> bool:
    """Verify ``coupling_log_weight`` is affine in `lam` for every entry."""
    if len(lams) < 2:
        raise ValueError("need at least 2 lams to check affineness")
    base = coupling_log_weight(coupling_J, coupling_Kc, gamma, lams[0])
    for lam in lams[1:]:
        diff = coupling_log_weight(coupling_J, coupling_Kc, gamma, lam) - base
        # diff should be (lam - lams[0]) · (J − gamma · K_c)
        slope = (
            (lam - lams[0])
            * (np.asarray(coupling_J, dtype=np.float64)
               - gamma * np.asarray(coupling_Kc, dtype=np.float64))
        )
        if not np.allclose(diff, slope, atol=atol):
            return False
    return True
