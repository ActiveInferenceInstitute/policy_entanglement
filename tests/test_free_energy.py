"""Tests for src/lean/free_energy.py."""

from __future__ import annotations

import numpy as np
import pytest

from lean.free_energy import (
    free_energy,
    joint_entropy,
    kl_divergence,
    marginal_entropy,
    marginal_free_energy,
    shannon_entropy,
    total_correlation,
    total_correlation_lean_companion,
    total_correlation_via_kl,
)
from lean.joint_dist import joint_marginals, mean_field_to_joint


def test_shannon_entropy_uniform_2():
    p = np.array([0.5, 0.5])
    assert abs(shannon_entropy(p) - np.log(2.0)) < 1e-12


def test_shannon_entropy_delta_is_zero():
    p = np.array([1.0, 0.0])
    assert abs(shannon_entropy(p)) < 1e-12


def test_shannon_entropy_uniform_4_log_4():
    p = np.full(4, 0.25)
    assert abs(shannon_entropy(p) - np.log(4.0)) < 1e-12


def test_kl_divergence_self_is_zero():
    p = np.array([0.3, 0.7])
    assert abs(kl_divergence(p, p)) < 1e-12


def test_kl_divergence_shape_mismatch_raises():
    with pytest.raises(ValueError, match="shape mismatch"):
        kl_divergence(np.array([0.5, 0.5]), np.array([0.3, 0.3, 0.4]))


def test_kl_divergence_absolute_continuity_violation_returns_inf():
    """KL(q ‖ p) = ∞ when p has zero mass on a point where q is positive."""
    q = np.array([0.5, 0.5])
    p = np.array([1.0, 0.0])
    assert kl_divergence(q, p) == float("inf")


def test_kl_divergence_known_value_bernoulli():
    # KL(Bernoulli(0.5) ‖ Bernoulli(0.25)) = 0.5·log(2) + 0.5·log(2/3)/log(2)·log(2)
    # Easier: compute manually
    q = np.array([0.5, 0.5])
    p = np.array([0.25, 0.75])
    expected = 0.5 * np.log(0.5 / 0.25) + 0.5 * np.log(0.5 / 0.75)
    assert abs(kl_divergence(q, p) - expected) < 1e-12


def test_kl_divergence_skips_zero_q_entries():
    q = np.array([1.0, 0.0])
    p = np.array([0.5, 0.5])
    expected = 1.0 * np.log(1.0 / 0.5)
    assert abs(kl_divergence(q, p) - expected) < 1e-12


def test_total_correlation_zero_for_mean_field():
    m = (np.array([0.6, 0.4]), np.array([0.3, 0.7]))
    q = mean_field_to_joint(m)
    assert abs(total_correlation(q)) < 1e-12


def test_total_correlation_positive_for_correlated():
    # Perfectly correlated joint
    q = np.array([[0.5, 0.0], [0.0, 0.5]])
    I = total_correlation(q)
    assert I > 0.0
    # For this joint, marginals are uniform on {0,1}; H(q^k) = log 2 = 0.693...
    # H(q) = log 2 (only two non-zero outcomes with mass 0.5 each)
    # I = 2 · log 2 − log 2 = log 2
    assert abs(I - np.log(2.0)) < 1e-12


def test_total_correlation_via_kl_matches_direct():
    """Prop 7.3: I(q) == KL(q ‖ ∏ q^k) numerically."""
    rng = np.random.default_rng(seed=42)
    q = rng.dirichlet(np.ones(6)).reshape(2, 3)
    direct = total_correlation(q)
    via_kl = total_correlation_via_kl(q)
    assert abs(direct - via_kl) < 1e-9


def test_total_correlation_lean_companion_matches_python_for_K2():
    """Numerical witness: the boundary-fragment Lean signature
    ``totalCorrelation q s sumStreamEntropies`` returns the multi-
    information when the caller passes ``Σ_k H(q^k)``.

    This is the parity invariant that distinguishes the new
    boundary-fragment definition (``sumStreamEntropies − H(q)``) from
    the prior placeholder (``kl q q s ≡ 0``).
    """
    rng = np.random.default_rng(seed=2026)
    for _ in range(10):
        q = rng.dirichlet(np.ones(4)).reshape(2, 2)
        margs = joint_marginals(q)
        sum_stream_entropies = float(sum(shannon_entropy(m) for m in margs))
        lean_form = total_correlation_lean_companion(q, sum_stream_entropies)
        python_form = total_correlation(q)
        assert abs(lean_form - python_form) < 1e-12, (lean_form, python_form)


def test_total_correlation_lean_companion_vanishes_at_mean_field():
    """Mean-field anchor: ``totalCorrelation_vanishes_at_meanField``
    in Lean asserts the formula collapses to 0 when the per-stream
    entropies sum to the joint entropy.  The Python companion
    reproduces this numerically."""
    q_mf = np.full((2, 2), 0.25)  # uniform K=2 joint, exactly mean-field
    margs = joint_marginals(q_mf)
    sum_stream_entropies = float(sum(shannon_entropy(m) for m in margs))
    H_joint = joint_entropy(q_mf)
    # The two scalars are equal by hand: 2 * log 2 = log 4.
    assert abs(sum_stream_entropies - H_joint) < 1e-12
    lean_form = total_correlation_lean_companion(q_mf, sum_stream_entropies)
    assert abs(lean_form) < 1e-12


def test_total_correlation_lean_companion_strictly_positive_off_mean_field():
    """Off-mean-field invariant: when sumStreamEntropies > H(q), the
    Lean form is strictly positive — confirming the boundary fragment
    is **not** identically zero (the prior bug)."""
    q_corr = np.array([[0.5, 0.0], [0.0, 0.5]])  # maximally correlated bipartite
    margs = joint_marginals(q_corr)
    sum_stream_entropies = float(sum(shannon_entropy(m) for m in margs))
    lean_form = total_correlation_lean_companion(q_corr, sum_stream_entropies)
    # I = log 2 - 0 = log 2 for the antidiagonal joint.
    assert lean_form > 0.0
    assert abs(lean_form - float(np.log(2.0))) < 1e-9


def test_joint_entropy_3_stream():
    q = np.full((2, 2, 2), 0.125)
    assert abs(joint_entropy(q) - np.log(8.0)) < 1e-12


def test_marginal_entropy_recovers_log2():
    q = np.full((2, 4), 0.125)  # uniform, marginal on stream 0 is uniform Bernoulli
    assert abs(marginal_entropy(q, 0) - np.log(2.0)) < 1e-12
    assert abs(marginal_entropy(q, 1) - np.log(4.0)) < 1e-12


def test_free_energy_shape_validation():
    with pytest.raises(ValueError, match="common shape"):
        free_energy(
            np.zeros((2, 2)),
            np.zeros((2, 3)),
            np.zeros((2, 2)),
            gamma=1.0,
        )


def test_free_energy_uniform_q_zero_g_yields_kl_to_uniform():
    """With G=0 and gamma=0, F[q] = -E_q[log p] - H(q) = KL(q ‖ p)."""
    q = np.array([[0.3, 0.2], [0.1, 0.4]])
    p = np.full((2, 2), 0.25)
    G = np.zeros((2, 2))
    F = free_energy(q, p, G, gamma=0.0)
    expected = kl_divergence(q, p)
    assert abs(F - expected) < 1e-12


def test_marginal_free_energy_uniform():
    q = np.full((2, 2), 0.25)
    mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    G = [np.zeros(2), np.zeros(2)]
    Fk = marginal_free_energy(q, mf, G, gamma=1.0, k=0)
    # uniform q^k vs uniform mf prior: KL = 0; H(q^k) = log 2; F = -log 2 - 0 = ?
    # F = gamma · E[G_k] − E[log E_k] − H(q^k)
    # = 0 − 0.5·log(0.5)·2 − log 2
    # = -log(0.5) - log(0.5) ... wait,
    # E[log E_k] for uniform q and uniform E_k = log(0.5)
    # H(q^k) = log 2
    # F = 0 − log(0.5) − log 2 = log 2 - log 2 = 0
    assert abs(Fk) < 1e-12


def test_marginal_free_energy_shape_validation():
    q = np.zeros((2, 2))
    bad_prior = [np.array([0.5, 0.5, 0.5]), np.array([0.5, 0.5])]
    G = [np.zeros(2), np.zeros(2)]
    with pytest.raises(ValueError, match="stream 0"):
        marginal_free_energy(q, bad_prior, G, gamma=1.0, k=0)
