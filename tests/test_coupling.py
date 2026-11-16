"""Tests for src/lean/coupling.py."""

from __future__ import annotations

import numpy as np
import pytest

from lean.coupling import (
    coupling_log_weight,
    entangled_log_weight_affine_in_lambda,
    entangled_posterior,
    entangled_prior,
    entangled_prior_unnormalised,
    expected_value,
    trivial_coupling,
)
from lean.joint_dist import is_pmf, mean_field_to_joint


def _symmetric_priors_2x2():
    return [np.array([0.5, 0.5]), np.array([0.5, 0.5])]


def _ising_J():
    return np.array([[0.5, -0.5], [-0.5, 0.5]])


def test_trivial_coupling_zero_everywhere():
    J = trivial_coupling((2, 3))
    assert J.shape == (2, 3)
    assert np.all(J == 0.0)


def test_entangled_prior_at_zero_is_mean_field():
    mf = _symmetric_priors_2x2()
    out = entangled_prior(mf, _ising_J(), lam=0.0)
    assert is_pmf(out)
    assert np.allclose(out, mean_field_to_joint(mf), atol=1e-12)


def test_entangled_prior_unnormalised_shape_mismatch_raises():
    mf = _symmetric_priors_2x2()
    bad_J = np.zeros((3, 3))  # wrong shape
    with pytest.raises(ValueError, match="coupling shape"):
        entangled_prior_unnormalised(mf, bad_J, lam=1.0)


def test_entangled_prior_concentrates_with_lambda():
    """As lambda grows, the Ising prior concentrates on aligned outcomes."""
    mf = _symmetric_priors_2x2()
    J = _ising_J()
    p_low = entangled_prior(mf, J, lam=0.5)
    p_high = entangled_prior(mf, J, lam=5.0)
    # Aligned mass = q(0,0) + q(1,1)
    aligned_low = p_low[0, 0] + p_low[1, 1]
    aligned_high = p_high[0, 0] + p_high[1, 1]
    assert aligned_high > aligned_low
    assert aligned_high > 0.95


def test_entangled_posterior_shape_mismatch_raises():
    mf = _symmetric_priors_2x2()
    G = [np.zeros(2), np.zeros(2)]
    with pytest.raises(ValueError, match="K_c shape"):
        entangled_posterior(mf, G, _ising_J(), np.zeros((3, 3)), gamma=1.0, lam=0.0)


def test_entangled_posterior_normalises():
    mf = _symmetric_priors_2x2()
    G = [np.array([0.0, 0.5]), np.array([0.0, 0.5])]
    Kc = np.zeros((2, 2))
    q = entangled_posterior(mf, G, _ising_J(), Kc, gamma=2.0, lam=0.7)
    assert is_pmf(q)


def test_entangled_posterior_strict_positive_marginals_rejects_degenerate():
    mf = [np.array([1.0, 0.0]), np.array([0.5, 0.5])]
    G = [np.zeros(2), np.zeros(2)]
    Kc = np.zeros((2, 2))
    with pytest.raises(ValueError, match="strict_positive_marginals"):
        entangled_posterior(
            mf,
            G,
            _ising_J(),
            Kc,
            gamma=1.0,
            lam=0.5,
            strict_positive_marginals=True,
        )


def test_expected_value_uniform_on_indicator():
    q = np.full((2, 2), 0.25)
    f = np.array([[1.0, 0.0], [1.0, 0.0]])  # indicator of pi^2 = 0
    assert abs(expected_value(q, f) - 0.5) < 1e-12


def test_expected_value_shape_mismatch_raises():
    with pytest.raises(ValueError, match="shape mismatch"):
        expected_value(np.zeros((2, 2)), np.zeros(2))


def test_log_weight_affine_in_lambda_recovers_slope():
    J = _ising_J()
    Kc = np.array([[0.1, 0.2], [0.3, 0.4]])
    a, b = entangled_log_weight_affine_in_lambda(J, Kc, gamma=2.0, pi_index=(0, 0))
    assert a == 0.0
    assert abs(b - (J[0, 0] - 2.0 * Kc[0, 0])) < 1e-12


def test_coupling_log_weight_is_affine_in_lambda():
    J = _ising_J()
    Kc = np.array([[0.1, 0.2], [0.3, 0.4]])
    w0 = coupling_log_weight(J, Kc, gamma=1.5, lam=0.0)
    w1 = coupling_log_weight(J, Kc, gamma=1.5, lam=1.0)
    w2 = coupling_log_weight(J, Kc, gamma=1.5, lam=2.0)
    # Affine: w(2) - w(1) == w(1) - w(0)
    assert np.allclose(w2 - w1, w1 - w0, atol=1e-12)


def test_coupling_log_weight_shape_mismatch_raises():
    J = np.zeros((2, 2))
    Kc = np.zeros((2, 3))
    with pytest.raises(ValueError, match="identical shapes"):
        coupling_log_weight(J, Kc, gamma=1.0, lam=1.0)


def test_entangled_posterior_strict_positive_marginals_raises() -> None:
    mf = [np.array([0.0, 1.0]), np.array([0.5, 0.5])]
    G = [np.array([0.0, 0.5]), np.array([0.0, 0.5])]
    with pytest.raises(ValueError, match="strict_positive_marginals"):
        entangled_posterior(mf, G, _ising_J(), np.zeros((2, 2)), gamma=1.0, lam=0.5, strict_positive_marginals=True)


def test_entangled_prior_3_stream_normalises():
    mf = [np.array([0.5, 0.5])] * 3
    J = np.zeros((2, 2, 2))
    out = entangled_prior(mf, J, lam=2.0)
    assert is_pmf(out)
    assert out.shape == (2, 2, 2)


def test_large_cancelling_couplings_keep_the_uniform_posterior() -> None:
    mf = _symmetric_priors_2x2()
    J = np.array([[1.0, -1.0], [-1.0, 1.0]])
    with np.errstate(over="raise", invalid="raise"):
        q = entangled_posterior(mf, [np.zeros(2), np.zeros(2)], J, J, gamma=1.0, lam=1000.0)
    np.testing.assert_allclose(q, np.full((2, 2), 0.25), atol=1e-12, rtol=0.0)


def test_large_prior_normalizes_without_materializing_unnormalized_mass() -> None:
    J = np.array([[1.0, -1.0], [-1.0, 1.0]])
    with np.errstate(over="raise", invalid="raise"):
        q = entangled_prior(_symmetric_priors_2x2(), J, lam=1000.0)
    np.testing.assert_allclose(q, [[0.5, 0.0], [0.0, 0.5]], atol=1e-12, rtol=0.0)


def test_log_space_posterior_preserves_moderate_gibbs_weights() -> None:
    mf = [np.array([0.3, 0.7]), np.array([0.6, 0.4])]
    G = [np.array([0.2, 0.8]), np.array([-0.3, 0.5])]
    J = _ising_J()
    Kc = np.array([[0.1, 0.4], [-0.2, 0.3]])
    gamma, lam = 1.3, 0.7
    expected = np.outer(mf[0], mf[1]) * np.exp(
        lam * J - gamma * (G[0][:, None] + G[1][None, :] + lam * Kc)
    )
    expected /= expected.sum()
    q = entangled_posterior(mf, G, J, Kc, gamma, lam)
    np.testing.assert_allclose(q, expected, atol=1e-12, rtol=0.0)


def test_log_space_posterior_preserves_zero_prior_support() -> None:
    mf = [np.array([1.0, 0.0]), np.array([0.3, 0.7])]
    J = np.zeros((2, 2))
    q = entangled_posterior(mf, [np.zeros(2), np.zeros(2)], J, J, gamma=1.0, lam=1.0)
    np.testing.assert_allclose(q, [[0.3, 0.7], [0.0, 0.0]], atol=1e-12, rtol=0.0)


def test_tiny_product_prior_retains_support_after_log_weighting() -> None:
    """A product below float64's range can become representable after coupling."""
    from lean.coupling import entangled_prior

    tiny = 1e-200
    priors = [np.array([tiny, 1.0]), np.array([tiny, 1.0])]
    for boost in (600.0, 1000.0):
        interaction = np.array([[boost, 0.0], [0.0, 0.0]])
        log_weights = np.array([2.0 * np.log(tiny) + boost, np.log(tiny), np.log(tiny), 0.0])
        expected_log = log_weights[0] - np.logaddexp.reduce(log_weights)
        with np.errstate(over="raise", invalid="raise"):
            joint = entangled_prior(priors, interaction, lam=1.0)
        assert np.isfinite(joint).all()
        assert joint[0, 0] > 0.0
        np.testing.assert_allclose(np.log(joint[0, 0]), expected_log, atol=1e-12)
        np.testing.assert_allclose(joint.sum(), 1.0, atol=1e-12)
