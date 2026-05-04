"""Tests for src/bernoulli_toy.py — closed-form K=2 Ising worked example."""
from __future__ import annotations

import numpy as np
import pytest

from bernoulli_toy import (
    coupling_phase_at,
    empirical_mutual_information,
    is_mean_field_at_zero,
    ising_coupling,
    ising_free_energy_curve,
    ising_joint_posterior,
    ising_mutual_information,
    optimal_lambda,
    symmetric_mean_field_prior,
)


def test_ising_coupling_shape_and_zero_mean():
    K = ising_coupling()
    assert K.shape == (2, 2)
    assert abs(K.sum()) < 1e-12


def test_ising_coupling_other_shape_raises():
    with pytest.raises(ValueError, match="2, 2"):
        ising_coupling(shape=(3, 3))


def test_symmetric_prior_is_uniform():
    a, b = symmetric_mean_field_prior()
    assert np.allclose(a, np.array([0.5, 0.5]))
    assert np.allclose(b, np.array([0.5, 0.5]))


def test_ising_mutual_information_zero_at_zero():
    assert abs(ising_mutual_information(0.0)) < 1e-12


def test_ising_mutual_information_increases_with_lambda():
    Is = [ising_mutual_information(l) for l in [0.0, 0.5, 1.0, 2.0, 5.0]]
    for a, b in zip(Is, Is[1:]):
        assert b >= a - 1e-12


def test_ising_mutual_information_even_in_lambda():
    for lam in [0.5, 1.5, 3.0]:
        assert abs(ising_mutual_information(lam) - ising_mutual_information(-lam)) < 1e-12


def test_ising_mutual_information_saturates_to_log2():
    """As lam -> ∞, MI saturates at log 2 (perfect alignment)."""
    Iinf = ising_mutual_information(50.0)
    assert abs(Iinf - np.log(2.0)) < 1e-6


def test_ising_joint_posterior_at_zero_is_uniform():
    q = ising_joint_posterior(0.0)
    assert np.allclose(q, np.full((2, 2), 0.25), atol=1e-12)


def test_ising_joint_posterior_concentrates_at_high_lambda():
    q = ising_joint_posterior(5.0)
    aligned = q[0, 0] + q[1, 1]
    assert aligned > 0.99


def test_empirical_mi_matches_closed_form():
    """Numerical TC of the Ising joint matches the closed-form formula."""
    for lam in [0.0, 0.5, 1.0, 2.0, 4.0]:
        emp = empirical_mutual_information(lam)
        closed = ising_mutual_information(lam)
        assert abs(emp - closed) < 1e-9, f"lam={lam}: emp={emp}, closed={closed}"


def test_optimal_lambda_zero_for_zero_surplus():
    assert abs(optimal_lambda(0.0)) < 1e-12


def test_optimal_lambda_saturates():
    assert optimal_lambda(1.0) == float("inf")
    assert optimal_lambda(-1.0) == float("-inf")
    assert optimal_lambda(2.0, delta_max=1.0) == float("inf")


def test_optimal_lambda_invalid_max_raises():
    with pytest.raises(ValueError, match="positive"):
        optimal_lambda(0.5, delta_max=0.0)


def test_optimal_lambda_monotonic_in_delta():
    lams = [optimal_lambda(d) for d in [0.0, 0.2, 0.4, 0.6, 0.8]]
    for a, b in zip(lams, lams[1:]):
        assert b > a


def test_ising_free_energy_curve_decreasing_in_lambda_with_utility():
    """For positive utility, F decreases as lambda grows from 0."""
    F0 = ising_free_energy_curve(0.0, utility=1.0)
    F1 = ising_free_energy_curve(1.0, utility=1.0)
    F2 = ising_free_energy_curve(3.0, utility=1.0)
    assert F0 > F1
    assert F1 > F2


def test_coupling_phase_at_boundaries():
    assert coupling_phase_at(0.0) == "disordered"
    assert coupling_phase_at(1.0) == "mixed"
    assert coupling_phase_at(5.0) == "frozen"


def test_coupling_phase_at_with_custom_thresholds():
    assert coupling_phase_at(0.3, lam_c1=0.1, lam_c2=1.0) == "mixed"
    assert coupling_phase_at(0.05, lam_c1=0.1, lam_c2=1.0) == "disordered"
    assert coupling_phase_at(2.0, lam_c1=0.1, lam_c2=1.0) == "frozen"


def test_is_mean_field_at_zero_passes():
    assert is_mean_field_at_zero()
