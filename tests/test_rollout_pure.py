"""Tests for pure utility functions in rollout.py and sweep.py.

These tests work without pymdp by constructing synthetic dataclass
objects and calling the array-manipulation helpers directly.
"""

from __future__ import annotations

import numpy as np
import pytest

from lean.coupling import entangled_posterior
from lean.free_energy import total_correlation
from lean.joint_dist import mean_field_to_joint
from simulation.rollout import Rollout, RolloutStep, _sample_from_joint
from simulation.specs import CoupledEnsembleSpec, StreamSpec
from simulation.sweep import LambdaSweepResult, coupled_marginal_trajectories, marginal_trajectory

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _uniform_2x2() -> np.ndarray:
    return np.array([[0.25, 0.25], [0.25, 0.25]])


def _make_step(t: int, tc: float = 0.0) -> RolloutStep:
    q = _uniform_2x2()
    marg = (np.array([0.5, 0.5]), np.array([0.5, 0.5]))
    return RolloutStep(
        t=t,
        observations=(0, 0),
        mean_field_marginals=marg,
        coupled_joint=q,
        sampled_actions=(0, 0),
        total_correlation=tc,
    )


def _make_rollout(tcs: list[float]) -> Rollout:
    # We only need a spec object with num_streams() == 2 — build a minimal one.
    # 1 obs, 1 hidden state, 2 controls
    A = np.array([[1.0]])  # 1 obs x 1 state
    B = np.zeros((1, 1, 2))
    B[:, :, 0] = 1.0
    B[:, :, 1] = 1.0
    C = np.zeros(1)
    D = np.array([1.0])
    s = StreamSpec(A=A, B=B, C=C, D=D)
    spec = CoupledEnsembleSpec(
        streams=(s, s),
        coupling_j=np.zeros((2, 2)),
        coupling_kc=np.zeros((2, 2)),
        gamma=1.0,
    )
    steps = tuple(_make_step(t, tc) for t, tc in enumerate(tcs))
    return Rollout(steps=steps, spec=spec, lam=1.0, seed=0)


# ---------------------------------------------------------------------------
# Rollout dataclass methods
# ---------------------------------------------------------------------------


def test_rollout_total_correlations_shape() -> None:
    tcs = [0.0, 0.1, 0.3, 0.6, 1.0]
    rollout = _make_rollout(tcs)
    arr = rollout.total_correlations()
    assert arr.shape == (len(tcs),)
    np.testing.assert_allclose(arr, tcs)


def test_rollout_joint_trajectory_shape() -> None:
    tcs = [0.0, 0.2, 0.5]
    rollout = _make_rollout(tcs)
    traj = rollout.joint_trajectory()
    assert traj.shape == (3, 2, 2)  # T=3, K=2 binary each


# ---------------------------------------------------------------------------
# _sample_from_joint
# ---------------------------------------------------------------------------


def test_sample_from_joint_returns_valid_index() -> None:
    q = np.array([[0.5, 0.0], [0.0, 0.5]])  # mass on (0,0) and (1,1)
    rng = np.random.default_rng(42)
    for _ in range(20):
        idx = _sample_from_joint(q, rng)
        assert len(idx) == 2
        # Only (0,0) and (1,1) have mass
        assert idx in ((0, 0), (1, 1))


def test_sample_from_joint_uniform_distribution() -> None:
    q = _uniform_2x2()
    rng = np.random.default_rng(0)
    counts = {(0, 0): 0, (0, 1): 0, (1, 0): 0, (1, 1): 0}
    N = 400
    for _ in range(N):
        idx = _sample_from_joint(q, rng)
        counts[idx] += 1
    for v in counts.values():
        assert v > N // 8, "expected roughly uniform sampling"


# ---------------------------------------------------------------------------
# LambdaSweepResult
# ---------------------------------------------------------------------------


def test_lambda_sweep_result_num_streams() -> None:
    q = _uniform_2x2()
    margs = (np.array([0.5, 0.5]), np.array([0.5, 0.5]))
    result = LambdaSweepResult(
        lam=1.0,
        joint=q,
        marginals=margs,
        total_correlation=0.0,
        is_pmf=True,
    )
    assert result.num_streams == 2


def test_lambda_sweep_result_single_stream() -> None:
    q = np.array([0.5, 0.5])
    result = LambdaSweepResult(
        lam=0.0,
        joint=q,
        marginals=(q,),
        total_correlation=0.0,
        is_pmf=True,
    )
    assert result.num_streams == 1


# ---------------------------------------------------------------------------
# marginal_trajectory
# ---------------------------------------------------------------------------


def test_marginal_trajectory_shape() -> None:
    tcs = [0.0, 0.5, 1.0]
    rollout = _make_rollout(tcs)
    traj = marginal_trajectory(rollout, k=0)
    # T=3 steps, 2 controls per stream
    assert traj.shape == (3, 2)


def test_marginal_trajectory_values() -> None:
    tcs = [0.0, 0.5]
    rollout = _make_rollout(tcs)
    for k in range(2):
        traj = marginal_trajectory(rollout, k=k)
        np.testing.assert_allclose(traj, 0.5)  # uniform throughout


def test_marginal_trajectory_out_of_range_raises() -> None:
    rollout = _make_rollout([0.0, 0.5])
    with pytest.raises(IndexError, match="stream"):
        marginal_trajectory(rollout, k=99)


@pytest.mark.parametrize("k", [2, 3, 4, 6])
def test_coupled_trajectories_reduce_actual_nonexchangeable_joints(k: int) -> None:
    """Uncoupled input posteriors and coupled output marginals are distinct channels."""
    priors = [np.array([0.8, 0.2]), np.array([0.4, 0.6])]
    priors.extend(np.array([0.2 + 0.1 * (axis % 3), 0.8 - 0.1 * (axis % 3)]) for axis in range(2, k))
    target = np.array([[0.55, 0.05], [0.15, 0.25]])
    for prior in priors[2:]:
        target = np.multiply.outer(target, prior)
    interaction = np.log(target / mean_field_to_joint(priors))
    joint = entangled_posterior(
        priors,
        [np.zeros(2) for _ in range(k)],
        interaction,
        np.zeros_like(interaction),
        lam=1.0,
        gamma=1.0,
    )
    np.testing.assert_allclose(joint, target, atol=1e-12)
    transitions = np.array([[[1.0, 0.0], [1.0, 0.0]], [[0.0, 1.0], [0.0, 1.0]]])
    streams = tuple(StreamSpec(A=np.eye(2), B=transitions, C=np.log(prior), D=np.full(2, 0.5)) for prior in priors)
    spec = CoupledEnsembleSpec(
        streams=streams, coupling_j=interaction, coupling_kc=np.zeros_like(interaction), gamma=1.0
    )
    steps = tuple(
        RolloutStep(
            t=t,
            observations=(0,) * k,
            mean_field_marginals=tuple(priors),
            coupled_joint=joint,
            sampled_actions=(0,) * k,
            total_correlation=total_correlation(joint),
        )
        for t in range(3)
    )
    rollout = Rollout(steps=steps, spec=spec, lam=1.0, seed=7)
    trajectories = coupled_marginal_trajectories(rollout)
    expected = [np.array([0.6, 0.4]), np.array([0.7, 0.3]), *priors[2:]]
    for axis, marginal in enumerate(expected):
        np.testing.assert_allclose(trajectories[axis], np.tile(marginal, (3, 1)), atol=1e-12)
        np.testing.assert_allclose(marginal_trajectory(rollout, axis), np.tile(priors[axis], (3, 1)), atol=1e-12)
    assert not np.allclose(trajectories[0], marginal_trajectory(rollout, 0))
    assert not np.allclose(trajectories[1], marginal_trajectory(rollout, 1))
