"""Tests for the BTAI baseline harness in `src.simulation.btai_baseline`.

No mocks — every test exercises real numpy arithmetic and the project's
own determinism conventions.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from simulation.btai_baseline import (
    BTAIScenario,
    BTAITreeNode,
    _enumerate_joint_actions,
    default_btai_scenarios,
    default_mcts_budgets,
    joint_marginals,
    kl_against_reference,
    run_btai_scenario,
    sample_complexity_exponent,
    total_correlation,
    ucb_score,
)


def test_default_mcts_budgets_are_log_spaced() -> None:
    """The configured MCTS budget grid is {10^2, 10^3, 10^4}."""
    budgets = default_mcts_budgets()
    assert budgets == [100, 1000, 10000]


def test_default_scenarios_cross_budgets_and_horizons() -> None:
    """Default scenarios cross every budget with every standard horizon."""
    scenarios = default_btai_scenarios(lambda_value=1.0)
    budgets = {scenario.mcts_budget for scenario in scenarios}
    horizons = {scenario.horizon for scenario in scenarios}
    assert budgets == set(default_mcts_budgets())
    assert len(horizons) >= 1


def test_enumerate_joint_actions_k2() -> None:
    """Enumerating actions for K=2 Ising gives 4 joint actions."""
    actions = list(_enumerate_joint_actions((2, 2)))
    assert actions == [(0, 0), (0, 1), (1, 0), (1, 1)]


def test_enumerate_joint_actions_k3() -> None:
    """Enumerating actions for K=3 with sizes (2, 2, 2) gives 8 joint actions."""
    actions = list(_enumerate_joint_actions((2, 2, 2)))
    assert len(actions) == 8


def test_joint_marginals_match_axis_sums() -> None:
    """Marginals are axis-sums of the joint."""
    joint = np.array([[0.1, 0.2], [0.3, 0.4]])
    m1, m2 = joint_marginals(joint)
    np.testing.assert_allclose(m1, [0.3, 0.7])
    np.testing.assert_allclose(m2, [0.4, 0.6])


def test_joint_marginals_rejects_non_2d() -> None:
    """K != 2 inputs must raise."""
    with pytest.raises(ValueError):
        joint_marginals(np.array([0.5, 0.5]))


def test_total_correlation_zero_when_independent() -> None:
    """I(q) = 0 iff q factorises as outer product of marginals."""
    marginals = np.array([0.4, 0.6])
    joint = np.outer(marginals, marginals)
    assert total_correlation(joint) == pytest.approx(0.0, abs=1e-12)


def test_total_correlation_positive_when_coupled() -> None:
    """I(q) > 0 for a non-mean-field joint."""
    joint = np.array([[0.45, 0.05], [0.05, 0.45]])
    assert total_correlation(joint) > 0.0


def test_ucb_score_unvisited_is_infinite() -> None:
    """Unvisited children get infinite UCB to force exploration."""
    parent_visits = 10
    child = BTAITreeNode(visits=0)
    assert math.isinf(ucb_score(parent_visits, child, exploration=1.0))


def test_ucb_score_finite_for_visited() -> None:
    """Visited children get finite UCB."""
    parent_visits = 10
    child = BTAITreeNode(visits=4, expected_free_energy=0.5)
    score = ucb_score(parent_visits, child, exploration=1.0)
    assert math.isfinite(score)
    assert score == pytest.approx(-0.5 + math.sqrt(math.log(10) / 4))


def test_run_btai_scenario_returns_per_step() -> None:
    """A small BTAI run emits one observable per horizon step."""
    scenario = BTAIScenario(horizon=3, mcts_budget=16, seed=42, lambda_value=1.0)

    def constant_efe(_action: tuple[int, ...]) -> float:
        return 0.0

    result = run_btai_scenario(
        scenario=scenario,
        joint_action_space=(2, 2),
        expected_free_energy_fn=constant_efe,
    )
    assert len(result.per_step) == 3
    assert result.final_posterior is not None
    assert result.final_posterior.shape == (2, 2)
    np.testing.assert_allclose(result.final_posterior.sum(), 1.0, atol=1e-12)


def test_run_btai_scenario_efe_biases_posterior() -> None:
    """A BTAI run with biased EFE concentrates mass on the lower-EFE actions."""
    scenario = BTAIScenario(horizon=1, mcts_budget=200, seed=7, lambda_value=1.0)

    def biased_efe(action: tuple[int, ...]) -> float:
        return 0.0 if action == (0, 0) else 5.0

    result = run_btai_scenario(
        scenario=scenario,
        joint_action_space=(2, 2),
        expected_free_energy_fn=biased_efe,
    )
    posterior = result.final_posterior
    assert posterior is not None
    assert posterior[0, 0] > 0.5


def test_kl_against_reference_zero_on_identical() -> None:
    """KL(p || p) = 0."""
    posterior = np.array([0.25, 0.25, 0.25, 0.25]).reshape(2, 2)
    assert kl_against_reference(posterior, posterior) == pytest.approx(0.0, abs=1e-12)


def test_kl_against_reference_positive_for_distinct() -> None:
    """KL(p || q) > 0 when p != q."""
    measured = np.array([[0.4, 0.1], [0.1, 0.4]])
    reference = np.array([[0.25, 0.25], [0.25, 0.25]])
    assert kl_against_reference(measured, reference) > 0.0


def test_kl_against_reference_rejects_shape_mismatch() -> None:
    with pytest.raises(ValueError):
        kl_against_reference(np.array([0.5, 0.5]), np.array([[0.5], [0.5]]))


def test_sample_complexity_exponent_perfect_power_law() -> None:
    """A clean B^{-1} curve yields exponent exactly 1."""
    budgets = [100, 1000, 10000]
    kl_curve = [0.1, 0.01, 0.001]
    assert sample_complexity_exponent(budgets, kl_curve) == pytest.approx(1.0, abs=1e-12)


def test_sample_complexity_exponent_rejects_short_inputs() -> None:
    """Fitting needs at least 2 points."""
    with pytest.raises(ValueError):
        sample_complexity_exponent([100], [0.1])


def test_btai_run_deterministic_under_same_seed() -> None:
    """Same seed -> same posterior down to numpy float64 precision."""
    scenario = BTAIScenario(horizon=2, mcts_budget=32, seed=99, lambda_value=1.0)

    def efe(action: tuple[int, ...]) -> float:
        return float(action[0] - action[1])

    result_one = run_btai_scenario(scenario, (2, 2), efe)
    result_two = run_btai_scenario(scenario, (2, 2), efe)
    np.testing.assert_array_equal(result_one.final_posterior, result_two.final_posterior)


def test_total_correlation_rejects_non_2d() -> None:
    with pytest.raises(ValueError):
        total_correlation(np.array([0.5, 0.5]))


def test_run_btai_scenario_with_reference_posterior_populates_kl() -> None:
    """When a reference posterior is supplied, per-step observables carry KL."""
    scenario = BTAIScenario(horizon=2, mcts_budget=32, seed=3, lambda_value=1.0)

    def efe(_action: tuple[int, ...]) -> float:
        return 0.0

    reference = np.array([[0.5, 0.0], [0.0, 0.5]])
    result = run_btai_scenario(scenario, (2, 2), efe, reference_posterior=reference)
    assert all(obs.kl_against_reference is not None for obs in result.per_step)
    for obs in result.per_step:
        assert obs.kl_against_reference >= 0.0  # KL is non-negative


def test_run_btai_scenario_no_reference_keeps_kl_field_none() -> None:
    """When no reference is supplied, the kl_against_reference field stays None."""
    scenario = BTAIScenario(horizon=1, mcts_budget=8, seed=5, lambda_value=1.0)

    def efe(_action: tuple[int, ...]) -> float:
        return 0.0

    result = run_btai_scenario(scenario, (2, 2), efe)
    assert all(obs.kl_against_reference is None for obs in result.per_step)


def test_run_btai_scenario_rejects_shape_mismatch_reference() -> None:
    """A reference posterior with mismatched shape raises a clean ValueError."""
    scenario = BTAIScenario(horizon=1, mcts_budget=8, seed=5, lambda_value=1.0)

    def efe(_action: tuple[int, ...]) -> float:
        return 0.0

    bad_reference = np.array([0.5, 0.5])  # wrong shape
    with pytest.raises(ValueError):
        run_btai_scenario(scenario, (2, 2), efe, reference_posterior=bad_reference)


def test_pymdp_grounded_efe_fn_uses_real_pymdp_agent() -> None:
    """End-to-end: BTAI baseline driven by real `pymdp.agent.Agent` EFE.

    Requires real pymdp 1.0.1 to be installed (the project's standard
    dev environment); if absent, skips honestly via the
    `requires_pymdp` marker pattern used elsewhere in the suite.

    The test wires the real-pymdp EFE function through `pymdp_grounded_efe_fn`,
    runs a small BTAI scenario, and asserts (a) every per-step posterior is
    a valid PMF, (b) the per-step EFEs are finite (real pymdp returned
    numbers, not NaN), and (c) two runs at the same seed are bit-identical.
    """
    pytest.importorskip("pymdp")
    from simulation.btai_baseline import pymdp_grounded_efe_fn
    from simulation.builders import make_ising_ensemble

    spec = make_ising_ensemble(coupling_amplitude=1.0, preference_strength=1.0, num_streams=2, gamma=1.0)
    observations = (0, 0)
    efe_fn = pymdp_grounded_efe_fn(spec, observations)

    # Real pymdp returns finite EFE for every joint action.
    joint_action_space = spec.policy_shape()
    actions = list(_enumerate_joint_actions(joint_action_space))
    for action in actions:
        value = efe_fn(action)
        assert np.isfinite(value), (
            f"pymdp returned non-finite EFE for joint_action={action}; "
            "real pymdp.agent.Agent should always emit a finite EFE."
        )

    # Run a small BTAI scenario through the real-pymdp EFE.
    scenario = BTAIScenario(horizon=2, mcts_budget=16, seed=42, lambda_value=1.0)
    result = run_btai_scenario(scenario, joint_action_space, efe_fn)
    assert len(result.per_step) == 2
    for observable in result.per_step:
        assert observable.joint_posterior.shape == joint_action_space
        np.testing.assert_allclose(observable.joint_posterior.sum(), 1.0, atol=1e-12)

    # Determinism: same seed → bit-identical posterior.
    result_again = run_btai_scenario(scenario, joint_action_space, efe_fn)
    np.testing.assert_array_equal(result.final_posterior, result_again.final_posterior)


def test_pymdp_grounded_efe_fn_rejects_wrong_action_length() -> None:
    """The pymdp-grounded EFE rejects joint actions of mismatched length."""
    pytest.importorskip("pymdp")
    from simulation.btai_baseline import pymdp_grounded_efe_fn
    from simulation.builders import make_ising_ensemble

    spec = make_ising_ensemble(num_streams=2)
    efe_fn = pymdp_grounded_efe_fn(spec, (0, 0))
    with pytest.raises(ValueError):
        efe_fn((0,))  # length 1, expected length 2
