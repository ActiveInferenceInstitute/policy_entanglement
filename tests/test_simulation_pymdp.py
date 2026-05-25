"""End-to-end tests for the pymdp 1.0.1 simulation harness.

Marked ``requires_pymdp`` — the suite skips entirely when the ``sim``
group is not installed, keeping the lean infra runner green.
"""

from __future__ import annotations

import numpy as np
import pytest

from simulation.agents import pymdp_available

if not pymdp_available():
    pytestmark = pytest.mark.skip(reason="pymdp 1.0.1 not installed (uv sync --group sim)")
else:
    pytestmark = pytest.mark.requires_pymdp


from lean.joint_dist import is_pmf, joint_marginals
from simulation.agents import build_pymdp_agent, build_pymdp_agents
from simulation.builders import make_bernoulli_stream, make_ising_ensemble
from simulation.inference import (
    coupled_policy_posterior,
    per_stream_efe,
    per_stream_policy_posterior,
)
from simulation.rollout import simulate_coupled_rollout
from simulation.sweep import (
    LambdaSweepResult,
    lambda_sweep,
    marginal_trajectory,
    total_correlation_curve,
)


def test_pymdp_available_returns_true_when_imported() -> None:
    assert pymdp_available() is True


def test_build_pymdp_agent_smoke() -> None:
    spec = make_bernoulli_stream("s")
    agent = build_pymdp_agent(spec, policy_len=1)
    assert agent is not None
    assert hasattr(agent, "infer_states")
    assert hasattr(agent, "infer_policies")


def test_build_pymdp_agents_count_matches_spec() -> None:
    spec = make_ising_ensemble(num_streams=3)
    agents = build_pymdp_agents(spec)
    assert len(agents) == 3


def test_per_stream_policy_posterior_returns_pmfs() -> None:
    spec = make_ising_ensemble(num_streams=2)
    posteriors = per_stream_policy_posterior(spec, observations=[0, 0])
    assert len(posteriors) == 2
    for p in posteriors:
        assert p.ndim == 1
        assert p.shape[0] == 2
        assert np.isclose(p.sum(), 1.0, atol=1e-6)
        assert (p >= -1e-7).all()


def test_per_stream_efe_returns_finite_vectors() -> None:
    spec = make_ising_ensemble(num_streams=2)
    efes = per_stream_efe(spec, observations=[0, 0])
    assert len(efes) == 2
    for G in efes:
        assert G.ndim == 1
        assert G.shape[0] == 2
        assert np.isfinite(G).all()


def test_per_stream_observations_length_validation() -> None:
    spec = make_ising_ensemble(num_streams=2)
    with pytest.raises(ValueError, match="observations length"):
        per_stream_policy_posterior(spec, observations=[0, 0, 0])
    with pytest.raises(ValueError, match="observations length"):
        per_stream_efe(spec, observations=[0])


def test_coupled_policy_posterior_lambda_zero_is_outer_product() -> None:
    spec = make_ising_ensemble(num_streams=2)
    obs = [0, 0]
    q = coupled_policy_posterior(spec, obs, lam=0.0)
    mf = per_stream_policy_posterior(spec, obs)
    # At λ=0 the analytical layer collapses to the outer product of the
    # mean-field marginals, *up to* pymdp's sign/utility-info-gain weighting
    # which gets folded into G; the joint marginals must equal mf.
    margs = joint_marginals(q)
    for k in range(spec.num_streams()):
        # Allow a small relative tolerance because pymdp computes EFE with
        # `use_utility=True, use_states_info_gain=True`.
        assert np.allclose(margs[k] / margs[k].sum(), mf[k] / mf[k].sum(), atol=1e-6)


def test_coupled_policy_posterior_returns_valid_pmf() -> None:
    spec = make_ising_ensemble(num_streams=2)
    for lam in [0.0, 0.5, 1.0, 2.0, 4.0]:
        q = coupled_policy_posterior(spec, [0, 0], lam=lam)
        assert q.shape == (2, 2)
        assert is_pmf(q, atol=1e-7)


def test_coupled_policy_posterior_total_correlation_increases_with_lambda() -> None:
    """Total correlation should grow monotonically with |λ| (Prop 7.3)."""
    from lean.free_energy import total_correlation

    spec = make_ising_ensemble(num_streams=2)
    obs = [0, 0]
    lams = [0.0, 1.0, 2.0, 4.0]
    tcs = [total_correlation(coupled_policy_posterior(spec, obs, lam=l)) for l in lams]
    for i in range(len(tcs) - 1):
        assert tcs[i + 1] >= tcs[i] - 1e-9, f"non-monotone at λ={lams[i + 1]}: {tcs}"


def test_lambda_sweep_returns_one_result_per_lambda() -> None:
    spec = make_ising_ensemble(num_streams=2)
    lams = [0.0, 0.5, 1.0, 2.0]
    results = lambda_sweep(spec, [0, 0], lams)
    assert len(results) == len(lams)
    for r, l in zip(results, lams, strict=False):
        assert isinstance(r, LambdaSweepResult)
        assert r.lam == l
        assert r.num_streams == 2
        assert r.is_pmf
        assert r.total_correlation >= -1e-9


def test_total_correlation_curve_matches_lambda_sweep() -> None:
    spec = make_ising_ensemble(num_streams=2)
    lams = [0.0, 0.5, 1.5, 3.0]
    sweep = lambda_sweep(spec, [0, 0], lams)
    curve = total_correlation_curve(spec, [0, 0], lams)
    assert curve.shape == (len(lams),)
    for i, r in enumerate(sweep):
        assert np.isclose(curve[i], r.total_correlation)


def test_simulate_coupled_rollout_deterministic_under_fixed_seed() -> None:
    spec = make_ising_ensemble(num_streams=2)
    r1 = simulate_coupled_rollout(spec, horizon=5, lam=1.5, seed=7)
    r2 = simulate_coupled_rollout(spec, horizon=5, lam=1.5, seed=7)
    assert len(r1.steps) == 5 == len(r2.steps)
    for s1, s2 in zip(r1.steps, r2.steps, strict=False):
        assert s1.observations == s2.observations
        assert s1.sampled_actions == s2.sampled_actions
        assert np.allclose(s1.coupled_joint, s2.coupled_joint)


def test_simulate_coupled_rollout_initial_observations_validation() -> None:
    spec = make_ising_ensemble(num_streams=2)
    with pytest.raises(ValueError, match="initial_observations"):
        simulate_coupled_rollout(spec, horizon=2, lam=0.5, initial_observations=[0])


def test_simulate_coupled_rollout_on_step_callback_invoked() -> None:
    spec = make_ising_ensemble(num_streams=2)
    seen: list[int] = []
    simulate_coupled_rollout(
        spec,
        horizon=4,
        lam=0.0,
        seed=1,
        on_step=lambda step: seen.append(step.t),
    )
    assert seen == [0, 1, 2, 3]


def test_marginal_trajectory_shape() -> None:
    spec = make_ising_ensemble(num_streams=2)
    rollout = simulate_coupled_rollout(spec, horizon=6, lam=1.0, seed=2)
    M = marginal_trajectory(rollout, k=0)
    assert M.shape == (6, 2)
    for row in M:
        assert np.isclose(row.sum(), 1.0, atol=1e-6)


def test_marginal_trajectory_index_validation() -> None:
    spec = make_ising_ensemble(num_streams=2)
    rollout = simulate_coupled_rollout(spec, horizon=2, lam=0.0, seed=0)
    with pytest.raises(IndexError):
        marginal_trajectory(rollout, k=5)


def test_rollout_total_correlations_and_joint_trajectory() -> None:
    spec = make_ising_ensemble(num_streams=2)
    rollout = simulate_coupled_rollout(spec, horizon=3, lam=1.0, seed=4)
    tcs = rollout.total_correlations()
    assert tcs.shape == (3,)
    assert (tcs >= -1e-9).all()
    traj = rollout.joint_trajectory()
    assert traj.shape == (3, 2, 2)
    for q in traj:
        assert is_pmf(q, atol=1e-7)
