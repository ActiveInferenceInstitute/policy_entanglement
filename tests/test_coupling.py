"""Tests for src/coupling.py."""
from __future__ import annotations

import numpy as np
import pytest

from coupling import (
    coupling_log_weight,
    entangled_log_weight_affine_in_lambda,
    entangled_posterior,
    entangled_prior,
    entangled_prior_unnormalised,
    expected_value,
    trivial_coupling,
)
from joint_dist import is_pmf, mean_field_to_joint


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
        entangled_posterior(
            mf, G, _ising_J(), np.zeros((3, 3)), gamma=1.0, lam=0.0
        )


def test_entangled_posterior_normalises():
    mf = _symmetric_priors_2x2()
    G = [np.array([0.0, 0.5]), np.array([0.0, 0.5])]
    Kc = np.zeros((2, 2))
    q = entangled_posterior(mf, G, _ising_J(), Kc, gamma=2.0, lam=0.7)
    assert is_pmf(q)


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


def test_entangled_prior_3_stream_normalises():
    mf = [np.array([0.5, 0.5])] * 3
    J = np.zeros((2, 2, 2))
    out = entangled_prior(mf, J, lam=2.0)
    assert is_pmf(out)
    assert out.shape == (2, 2, 2)
