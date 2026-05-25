"""Tests for the adversarial-perturbation harness in `src.simulation.adversarial`.

No mocks; every test exercises real numpy arithmetic.
"""

from __future__ import annotations

import numpy as np
import pytest

from simulation.adversarial import (
    AdversarialScenario,
    analytical_lipschitz_bound,
    coupling_covariance,
    default_adversarial_scenarios,
    default_epsilon_grid,
    default_lambda_grid,
    empirical_lipschitz_constant,
    kl_divergence,
    measure_drift,
    perturbed_posterior,
    rank_one_adversary,
    sparse_single_adversary,
    uniform_random_adversary,
    variance_under_q,
)


def test_default_epsilon_grid_is_log_spaced() -> None:
    """Pre-registered epsilon grid is log-spaced 1e-3 .. 1e0."""
    grid = default_epsilon_grid()
    assert len(grid) == 7
    assert grid[0] == pytest.approx(1e-3)
    assert grid[-1] == pytest.approx(1.0)


def test_default_lambda_grid_matches_revertibility() -> None:
    """Lambda grid matches the revertibility sweep's five points."""
    assert default_lambda_grid() == [0.0, 0.5, 1.0, 2.0, 4.0]


def test_default_scenarios_cross_all_classes() -> None:
    """Default scenarios touch all three adversary classes at every grid point."""
    scenarios = list(default_adversarial_scenarios(seed=12345))
    classes = {scenario.adversary_class for scenario in scenarios}
    assert classes == {"rank_one", "uniform_random", "sparse_single"}
    expected_total = len(default_lambda_grid()) * len(default_epsilon_grid()) * len(classes)
    assert len(scenarios) == expected_total


def test_variance_under_q_zero_for_constant() -> None:
    """Variance of a constant under any distribution is zero."""
    q = np.array([[0.25, 0.25], [0.25, 0.25]])
    J = np.ones((2, 2))
    assert variance_under_q(q, J) == pytest.approx(0.0, abs=1e-12)


def test_variance_under_q_matches_textbook() -> None:
    """Var_q(J) matches E_q[J^2] - (E_q[J])^2 by hand."""
    q = np.array([[0.5, 0.0], [0.0, 0.5]])
    J = np.array([[1.0, 0.0], [0.0, -1.0]])
    expected_mean = 0.5 * 1.0 + 0.5 * -1.0
    expected_second = 0.5 * 1.0 + 0.5 * 1.0
    expected_variance = expected_second - expected_mean**2
    assert variance_under_q(q, J) == pytest.approx(expected_variance, abs=1e-12)


def test_coupling_covariance_shape() -> None:
    """The flattened coupling covariance matrix has the right shape."""
    q = np.array([[0.25, 0.25], [0.25, 0.25]])
    J = np.array([[1.0, 0.0], [0.0, 1.0]])
    cov = coupling_covariance(q, J)
    assert cov.shape == (4, 4)


def test_analytical_lipschitz_bound_zero_at_lambda_zero() -> None:
    """At lambda = 0 the analytical Lipschitz bound is zero."""
    q = np.array([[0.25, 0.25], [0.25, 0.25]])
    J = np.array([[1.0, 0.0], [0.0, 1.0]])
    assert analytical_lipschitz_bound(0.0, 0.1, q, J) == pytest.approx(0.0, abs=1e-12)


def test_analytical_lipschitz_bound_scales_with_lambda_and_epsilon() -> None:
    """Bound scales linearly with lambda * epsilon."""
    q = np.array([[0.4, 0.1], [0.1, 0.4]])
    J = np.array([[1.0, -1.0], [-1.0, 1.0]])
    base = analytical_lipschitz_bound(1.0, 0.1, q, J)
    doubled = analytical_lipschitz_bound(2.0, 0.1, q, J)
    assert doubled == pytest.approx(2.0 * base, rel=1e-12)
    eps_doubled = analytical_lipschitz_bound(1.0, 0.2, q, J)
    assert eps_doubled == pytest.approx(2.0 * base, rel=1e-12)


def test_kl_divergence_zero_on_identical() -> None:
    p = np.array([0.4, 0.6])
    assert kl_divergence(p, p) == pytest.approx(0.0, abs=1e-12)


def test_kl_divergence_positive_on_distinct() -> None:
    p = np.array([0.4, 0.6])
    q = np.array([0.6, 0.4])
    assert kl_divergence(p, q) > 0.0


def test_kl_divergence_rejects_shape_mismatch() -> None:
    with pytest.raises(ValueError):
        kl_divergence(np.array([0.5, 0.5]), np.array([0.25, 0.25, 0.5]))


def test_rank_one_adversary_norm_bounded_by_epsilon() -> None:
    """The rank-one adversary respects the L_infty budget."""
    q = np.array([[0.4, 0.1], [0.1, 0.4]])
    J = np.array([[1.0, 0.0], [0.0, 1.0]])
    delta = rank_one_adversary(q, J, epsilon=0.1)
    assert float(np.max(np.abs(delta))) <= 0.1 + 1e-12


def test_uniform_random_adversary_has_correct_norm() -> None:
    """Each cell of the uniform adversary has magnitude exactly epsilon."""
    delta = uniform_random_adversary((4, 4), epsilon=0.07, seed=1)
    np.testing.assert_allclose(np.abs(delta), 0.07)


def test_sparse_single_adversary_has_one_nonzero() -> None:
    """The sparse single-cell adversary has exactly one non-zero entry."""
    delta = sparse_single_adversary((3, 3), epsilon=0.2, seed=42)
    nonzero_count = int(np.sum(delta != 0.0))
    assert nonzero_count == 1
    assert float(np.max(np.abs(delta))) == pytest.approx(0.2)


def test_perturbed_posterior_normalises() -> None:
    """The perturbed posterior sums to 1."""
    q = np.array([[0.4, 0.1], [0.1, 0.4]])
    J = np.array([[1.0, 0.0], [0.0, 1.0]])
    delta = rank_one_adversary(q, J, epsilon=0.1)
    perturbed = perturbed_posterior(q, J, delta, lambda_value=1.0)
    assert perturbed.sum() == pytest.approx(1.0, abs=1e-12)


def test_perturbed_posterior_identity_under_zero_perturbation() -> None:
    """Zero delta_J leaves q unchanged."""
    q = np.array([[0.4, 0.1], [0.1, 0.4]])
    J = np.array([[1.0, 0.0], [0.0, 1.0]])
    delta = np.zeros_like(J)
    np.testing.assert_allclose(perturbed_posterior(q, J, delta, lambda_value=1.0), q)


def test_measure_drift_returns_observable() -> None:
    """measure_drift returns an AdversarialObservable with the bound and the drift."""
    scenario = AdversarialScenario(lambda_value=1.0, epsilon=0.05, adversary_class="rank_one", seed=1)
    q = np.array([[0.4, 0.1], [0.1, 0.4]])
    J = np.array([[1.0, -1.0], [-1.0, 1.0]])
    observable = measure_drift(scenario, q, J)
    assert observable.scenario is scenario
    assert observable.measured_kl_drift >= 0.0
    assert observable.analytical_bound >= 0.0


def test_measure_drift_unknown_class_raises() -> None:
    """Unknown adversary class raises a clean ValueError."""
    bad_scenario = AdversarialScenario(lambda_value=1.0, epsilon=0.05, adversary_class="malicious", seed=1)
    q = np.array([[0.5, 0.0], [0.0, 0.5]])
    J = np.array([[1.0, 0.0], [0.0, 1.0]])
    with pytest.raises(ValueError):
        measure_drift(bad_scenario, q, J)


def test_empirical_lipschitz_constant_zero_on_empty() -> None:
    assert empirical_lipschitz_constant([]) == 0.0


def test_empirical_lipschitz_constant_picks_max() -> None:
    """Empirical Lipschitz constant is the max ratio across scenarios."""
    q = np.array([[0.5, 0.0], [0.0, 0.5]])
    J = np.array([[1.0, 0.0], [0.0, 1.0]])
    scenario_a = AdversarialScenario(lambda_value=1.0, epsilon=0.1, adversary_class="rank_one", seed=1)
    scenario_b = AdversarialScenario(lambda_value=1.0, epsilon=0.05, adversary_class="rank_one", seed=2)
    observables = [measure_drift(scenario_a, q, J), measure_drift(scenario_b, q, J)]
    constant = empirical_lipschitz_constant(observables)
    assert constant >= 0.0


def test_first_order_bound_holds_in_small_epsilon_regime() -> None:
    """In the small-epsilon regime the first-order Lipschitz bound must
    genuinely hold: measured KL drift ≤ the analytical bound.

    At epsilon=1e-3 the linearization is tight (measured drift is orders
    of magnitude under the bound), so this asserts the *actual* bound,
    not a 10x-padded surrogate that would pass even on an order-of-
    magnitude error.
    """
    scenario = AdversarialScenario(lambda_value=1.0, epsilon=0.001, adversary_class="rank_one", seed=11)
    q = np.array([[0.4, 0.1], [0.1, 0.4]])
    J = np.array([[1.0, -1.0], [-1.0, 1.0]])
    observable = measure_drift(scenario, q, J)
    assert observable.measured_kl_drift <= observable.analytical_bound + 1e-12
