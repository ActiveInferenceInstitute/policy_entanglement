"""Information geometry of the entanglement manifold.

Dually-flat (e/m) structure on the policy simplex.  The mean-field
submanifold ``M_MF ⊂ M`` is e-flat (Proposition 7.1); the
``λ``-family ``{q_λ}`` is the *e-geodesic* departing it (Theorem 7.4);
marginalization is the m-projection (Proposition 7.2); and total
correlation equals the KL of ``q`` to its m-projection
(Proposition 7.3).

The Pythagorean residual gives an *exact* decomposition of KL to any
reference point through the m-projection:

    D_KL(q ‖ q_ref) = I(q) + D_KL(m_projection(q) ‖ q_ref) + residual

The residual is zero up to floating tolerance when ``q_ref`` lies on
``M_MF`` (Proposition 7.5).  ``pythagorean_residual`` returns it for
numerical witness.

Example::

    >>> import numpy as np
    >>> from lean.coupling import entangled_posterior
    >>> from lean.geometry import m_projection, is_mean_field
    >>> mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    >>> G  = [np.zeros(2), np.zeros(2)]
    >>> J  = np.array([[1.0, -1.0], [-1.0, 1.0]])
    >>> Kc = np.zeros((2, 2))
    >>> q  = entangled_posterior(mf, G, J, Kc, gamma=1.0, lam=2.0)
    >>> bool(is_mean_field(q, atol=1e-9))            # coupled ⇒ not MF
    False
    >>> bool(is_mean_field(m_projection(q), atol=1e-9))  # projection lands on MF
    True

Lean companion: ``ActinfPolicyEntanglement.Geometry``.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

from .coupling import (
    coupling_log_weight,
    entangled_log_weight_affine_in_lambda,
    entangled_posterior,
)
from .free_energy import kl_divergence, total_correlation, total_correlation_via_kl
from .joint_dist import is_mean_field, m_projection, mean_field_to_joint

ArrayF = NDArray[np.float64]


def is_in_mean_field_submanifold(q: ArrayF, atol: float = 1e-9) -> bool:
    """Predicate: `q` lies on M_MF (the mean-field submanifold)."""
    return is_mean_field(q, atol=atol)


def m_projection_minimises_kl(
    q: ArrayF,
    candidate_marginals: Sequence[ArrayF],
    atol: float = 1e-12,
) -> bool:
    """Verify Prop 7.2 numerically: `KL(q ‖ ∏ q^k) ≤ KL(q ‖ ∏ p^k)` for any
    candidate mean-field `p`.
    """
    proj = m_projection(q)
    cand = mean_field_to_joint(candidate_marginals)
    return kl_divergence(q, proj) <= kl_divergence(q, cand) + atol


def pythagorean_residual(q: ArrayF, mf_reference: Sequence[ArrayF]) -> float:
    """`KL(q ‖ ref) − [I(q) + KL(∏ q^k ‖ ref)]`.

    Should be 0 (up to floating tolerance) for any joint `q` and any
    mean-field reference, by Prop 7.5 of the manuscript.
    """
    ref = mean_field_to_joint(mf_reference)
    lhs = kl_divergence(q, ref)
    rhs = total_correlation_via_kl(q) + kl_divergence(m_projection(q), ref)
    return float(lhs - rhs)


def is_e_geodesic(
    coupling_j: ArrayF,
    coupling_kc: ArrayF,
    gamma: float,
    pi_index: tuple[int, ...],
    lams: Sequence[float],
    atol: float = 1e-9,
) -> bool:
    """Consistency witness for Theorem 7.4's affine-in-λ structure.

    The unnormalized pointwise coupling log-weight is affine in ``lam`` *by
    construction*: ``coupling_log_weight`` computes ``lam·J − gamma·lam·K_c``.
    This check confirms the affine *decomposition* ``(a, b)`` returned by
    ``entangled_log_weight_affine_in_lambda`` agrees with that canonical
    weight at each ``lam`` — i.e. it guards against the two presentations
    of the same closed form drifting apart (a typo in one of them).

    **Honest scope (do not over-read):** this is NOT an independent
    validation of the e-geodesic property. Both ``actual`` and ``predicted``
    reduce to the same ``lam·(J − gamma·K_c)`` formula, so the comparison is
    an algebraic identity and cannot detect an error in that formula itself.
    A genuinely independent probe must route through a different code path —
    differencing the *normalized* log-posterior of ``entangled_posterior``
    across ``lam`` (exp → normalize → log); see
    ``tests/test_geometry.py::test_e_geodesic_slope_via_normalized_posterior``.
    """
    a, b = entangled_log_weight_affine_in_lambda(coupling_j, coupling_kc, gamma, pi_index)
    for lam in lams:
        actual = float(coupling_log_weight(coupling_j, coupling_kc, gamma, lam)[pi_index])
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
    coupling_j: ArrayF,
    coupling_kc: ArrayF,
    gamma: float,
    lam: float,
    atol: float = 1e-12,
) -> bool:
    """Numerical version of the coupling-pays-for-itself verdict.

    Computes the lambda-entangled posterior and the lambda=0
    (mean-field) posterior, and returns ``True`` iff the entangled
    posterior has **strictly higher total correlation** than the
    lambda=0 baseline (i.e. coupling strictly increases the agentic
    gain ``I(q_lambda)``).  This is the operational total-correlation
    verdict, matching ``decomposition.coupling_pays_for_itself`` and
    the Lean ``couplingVerdict`` semantics (``tax < gain`` with
    ``gain = I(q_lambda)``); it is **not** a free-energy comparison.
    The free-energy "coupling pays for itself" motivation (Sec. 2J)
    reduces to this total-correlation test through the decomposition
    theorem's accounting of the ``I(q_lambda)`` gain term.
    """
    if lam <= 0.0:
        return False
    q_entangled = entangled_posterior(mf_prior, per_stream_G, coupling_j, coupling_kc, gamma, lam)
    q_mf = entangled_posterior(mf_prior, per_stream_G, coupling_j, coupling_kc, gamma, 0.0)
    # The verdict is purely about the total-correlation gain at this lam:
    return bool(total_correlation(q_entangled) > total_correlation(q_mf) + atol)


def coupling_log_weight_affine_check(
    coupling_j: ArrayF,
    coupling_kc: ArrayF,
    gamma: float,
    lams: Sequence[float],
    atol: float = 1e-9,
) -> bool:
    """Verify ``coupling_log_weight`` is affine in `lam` for every entry."""
    if len(lams) < 2:
        raise ValueError("need at least 2 lams to check affineness")
    base = coupling_log_weight(coupling_j, coupling_kc, gamma, lams[0])
    for lam in lams[1:]:
        diff = coupling_log_weight(coupling_j, coupling_kc, gamma, lam) - base
        # diff should be (lam - lams[0]) · (J − gamma · K_c)
        slope = (lam - lams[0]) * (
            np.asarray(coupling_j, dtype=np.float64) - gamma * np.asarray(coupling_kc, dtype=np.float64)
        )
        if not np.allclose(diff, slope, atol=atol):
            return False
    return True
