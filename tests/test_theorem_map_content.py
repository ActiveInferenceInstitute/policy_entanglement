"""Audit theorem-map rows by asserting the real mathematical content.

This closes the gap between "a theorem-map row exists" and "the mapped
test exercises the intended invariant" for `cor_4_4`, `thm_4_2`,
`thm_6_4`, and the K=2 numerical witness of
`entanglement_decomposition_generalK`.
"""

from __future__ import annotations

import numpy as np

from lean.bernoulli_toy import ising_coupling, ising_joint_posterior
from lean.coupling import coupling_log_weight
from lean.decomposition import (
    entanglement_decomposition_rhs,
    free_energy_against_entangled_prior,
)
from lean.free_energy import kl_divergence, total_correlation
from lean.joint_dist import joint_marginals, m_projection, mean_field_to_joint


def _sum_q_log_m_over_p(q: np.ndarray, m: np.ndarray, p: np.ndarray) -> float:
    mask = q > 0.0
    return float(np.sum(q[mask] * np.log(m[mask] / p[mask])))


def test_cor_4_4_strict_gain_iff_non_mean_field() -> None:
    """Compare TC of an entangled joint against TC of the mean-field λ=0 joint.

    This is not a tautology because it contrasts two distinct
    distributions, one genuinely entangled and one exactly mean-field.
    """
    q_non_mean_field = ising_joint_posterior(1.5)
    q_mean_field = ising_joint_posterior(0.0)
    # 1e-6 is safely above float noise here and encodes "strictly positive" rather than numerical fuzz.
    assert total_correlation(q_non_mean_field) > 1e-6
    # 1e-12 is a round-off budget because λ=0 gives the exact product baseline analytically.
    assert abs(total_correlation(q_mean_field)) < 1e-12


def test_thm_4_2_closed_form_free_energy_identity() -> None:
    """Compare the closed-form free-energy LHS against the decomposition RHS total.

    This is not a tautology because the two sides come from distinct
    implementations of the theorem's closed log-partition identity.
    """
    mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    J = ising_coupling()
    Kc = np.zeros((2, 2), dtype=np.float64)
    for utility, lam in ((0.5, 1.0), (1.0, 2.0), (0.0, 0.5)):
        G = [np.array([0.0, utility]), np.array([0.0, utility])]
        q = ising_joint_posterior(lam) if utility == 0.0 else None
        if q is None:
            from lean.coupling import entangled_posterior

            q = entangled_posterior(mf, G, J, Kc, gamma=1.0, lam=lam)
        lhs = free_energy_against_entangled_prior(q, mf, G, J, Kc, gamma=1.0, lam=lam)
        rhs = entanglement_decomposition_rhs(q, mf, G, J, Kc, gamma=1.0, lam=lam).total
        # 1e-9 is a sum-of-logs floating budget; both sides are algebraically equal but numerically independent.
        assert abs(lhs - rhs) < 1e-9


def test_thm_6_4_e_geodesic_affine_in_lambda() -> None:
    """Compare a difference of coupling log-weights against its affine λ prediction.

    This is not a tautology because it contrasts two distinct tensors:
    the finite difference of log-weights and the theorem's affine form.
    """
    J = ising_coupling()
    Kc = np.zeros((2, 2), dtype=np.float64)
    for lam1, lam2 in ((0.5, 1.0), (2.0, 0.3), (1.0, 4.0)):
        lhs = coupling_log_weight(J, Kc, 0.0, lam1) - coupling_log_weight(J, Kc, 0.0, lam2)
        rhs = (lam1 - lam2) * (J - 0.0 * Kc)
        # 1e-9 is a tight float budget because the affine identity is exact in real arithmetic.
        assert np.allclose(lhs, rhs, atol=1e-9)


def test_capstone_generalK_K2_numerical_witness() -> None:
    """Compare KL identities for product and entangled K=2 joints.

    This is not a tautology because each conjunct compares distinct
    quantities: `D(q||p)` versus `D(q||m)+Σq log(m/p)`, and `D(q||m)`
    versus `D(q||p)`, for two different choices of `q`.
    """
    product_factors = [np.array([0.7, 0.3]), np.array([0.4, 0.6])]
    comparison_factors = [np.array([0.55, 0.45]), np.array([0.35, 0.65])]
    p = mean_field_to_joint(comparison_factors)
    q_cases = [
        ("product", mean_field_to_joint(product_factors)),
        ("entangled", ising_joint_posterior(1.5)),
    ]
    for label, q in q_cases:
        m = m_projection(q)
        d_q_m = kl_divergence(q, m)
        d_q_p = kl_divergence(q, p)
        bridge = _sum_q_log_m_over_p(q, m, p)
        # 1e-9 is a floating summation budget for KL identities over only four atoms.
        assert d_q_m >= -1e-9, label
        # 1e-9 is appropriate here because both sides are direct finite sums over the same 2x2 support.
        assert abs(d_q_p - (d_q_m + bridge)) < 1e-9, label
        # 1e-9 encodes the monotonicity inequality with round-off slack only.
        assert d_q_m <= d_q_p + 1e-9, label
    # 1e-9 is a round-off budget because a product joint is exactly its own m-projection analytically.
    assert kl_divergence(q_cases[0][1], m_projection(q_cases[0][1])) < 1e-9
    entangled_q = q_cases[1][1]
    entangled_m = m_projection(entangled_q)
    # 1e-9 is a cross-path equality budget for KL(q||m(q)) = total correlation(q).
    assert abs(kl_divergence(entangled_q, entangled_m) - total_correlation(entangled_q)) < 1e-9
    # 1e-6 stays well above float noise and encodes the intended "strictly entangled" witness.
    assert total_correlation(entangled_q) > 1e-6
    rebuilt_m = mean_field_to_joint(joint_marginals(entangled_q))
    # 1e-12 is an exact remarginalize-and-rebuild budget on a 2x2 joint.
    assert np.allclose(entangled_m, rebuilt_m, atol=1e-12)
