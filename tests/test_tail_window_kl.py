"""Pure-numpy convergence tests for :func:`simulation.long_horizon.tail_window_kl`.

This file deliberately has **no pymdp dependency**: every test feeds
the convergence helper synthetic marginal trajectories built from
numpy alone, so the parameterized horizons ``T ∈ {25, 50, 100}`` run in
the default ``uv sync`` environment without the ``sim`` group.

The published numerical witness for **habit accumulation**
(Manuscript §9.4) is the steady-state KL bounded by
``H.LONG_HORIZON_STEADY_STATE_TOL`` at the full horizon
``H.LONG_HORIZON_STEPS = 100``.  Until the round-4 helper extraction,
the only test of this logic ran at the *short* horizon ``T = 25``;
this file (round-5, P1-3) closes that gap by exercising convergence
at the full horizon — and at intermediate horizons — without re-running
pymdp.
"""

from __future__ import annotations

import numpy as np
import pytest

from simulation.long_horizon import tail_window_kl, tail_window_kl_statistics


def _converged_trajectory(
    T: int,  # noqa: N803 — T = horizon (manuscript symbol).
    dim: int,
    tail_window: int,
    seed: int = 0,
) -> np.ndarray:
    """Build a synthetic ``(T, dim)`` marginal trajectory that drifts
    linearly from uniform to a converged value over the first
    ``T - tail_window`` steps, then sits at the converged value for
    the trailing window.  Tail-window KL must be exactly 0.
    """
    rng = np.random.default_rng(seed=seed)
    converged = rng.dirichlet(np.ones(dim))
    uniform = np.full(dim, 1.0 / dim)
    traj = np.zeros((T, dim), dtype=np.float64)
    drift_steps = T - tail_window
    for t in range(drift_steps):
        alpha = (t + 1) / max(drift_steps, 1)
        row = (1.0 - alpha) * uniform + alpha * converged
        traj[t] = row / row.sum()
    traj[drift_steps:] = converged
    return traj


@pytest.mark.parametrize(
    ("T", "tail_window"),  # noqa: PT006 — tuple form supported by pytest.
    [(25, 8), (50, 15), (100, 20)],
)
def test_tail_window_kl_perfect_convergence_at_multiple_horizons(
    T: int,  # noqa: N803
    tail_window: int,
) -> None:
    """Tail KL is exactly 0 across horizons ``T ∈ {25, 50, 100}`` when
    the trailing window is constant.

    This is the P1-3 round-5 test that exercises the full
    ``LONG_HORIZON_STEPS = 100`` convergence logic *without* running
    pymdp.  Prior to round 4 the helper was inline inside the
    rollout, so the published `T = 100` numerical witness was
    untested — only the short ``T = 25`` rollout ran in CI.
    """
    traj_k0 = _converged_trajectory(T, 2, tail_window, seed=0)
    traj_k1 = _converged_trajectory(T, 2, tail_window, seed=1)
    tail_means, tail_kls = tail_window_kl((traj_k0, traj_k1), tail_window)
    assert len(tail_means) == 2
    assert len(tail_kls) == 2
    for kl in tail_kls:
        assert kl == pytest.approx(0.0, abs=1e-12)
    for mean, traj in zip(tail_means, (traj_k0, traj_k1), strict=True):
        assert np.allclose(mean, traj[-1], atol=1e-12)


@pytest.mark.parametrize("T", [25, 50, 100])
def test_tail_window_kl_drifting_trajectory_detects_lack_of_convergence(
    T: int,  # noqa: N803
) -> None:
    """A marginal that keeps drifting through the trailing window
    produces a *non-zero* tail KL at every horizon.  Round-5 P1-3
    test: the convergence witness fires for non-converging
    trajectories at every published horizon.
    """
    tail_window = max(8, T // 5)
    rng = np.random.default_rng(seed=T)
    start = rng.dirichlet(np.ones(3))
    end = rng.dirichlet(np.ones(3))
    traj = np.zeros((T, 3), dtype=np.float64)
    for t in range(T):
        alpha = t / max(T - 1, 1)
        row = (1.0 - alpha) * start + alpha * end
        traj[t] = row / row.sum()
    _, tail_kls = tail_window_kl((traj,), tail_window)
    assert tail_kls[0] > 0.0, f"T={T}: a drifting trajectory must produce strictly positive tail KL, got {tail_kls[0]}"
    assert tail_kls[0] < 0.5, (
        f"T={T}: tail KL exploded ({tail_kls[0]}); the drift envelope is supposed to keep it bounded"
    )


def test_tail_window_kl_uniform_trajectory_yields_zero_kl() -> None:
    """A perfectly constant trajectory at every step trivially
    converges — tail KL is exactly 0 at every horizon.
    """
    for T in (25, 50, 100):  # noqa: N806 — T = horizon.
        traj = np.tile(np.array([0.3, 0.5, 0.2]), (T, 1))
        _, tail_kls = tail_window_kl((traj,), tail_window=8)
        assert tail_kls[0] == pytest.approx(0.0, abs=1e-15)


def test_tail_window_kl_empty_raises() -> None:
    """An empty marginal trajectory tuple must raise immediately."""
    with pytest.raises(ValueError, match="non-empty"):
        tail_window_kl((), tail_window=5)


def test_tail_window_kl_validates_window_too_small() -> None:
    """``tail_window < 1`` delegates to ``_validate_window`` and raises."""
    traj = np.full((10, 2), 0.5, dtype=np.float64)
    with pytest.raises(ValueError, match="tail_window"):
        tail_window_kl((traj,), tail_window=0)


def test_tail_window_kl_validates_window_too_large() -> None:
    """``tail_window > T`` delegates to ``_validate_window`` and raises."""
    traj = np.full((10, 2), 0.5, dtype=np.float64)
    with pytest.raises(ValueError, match="tail_window"):
        tail_window_kl((traj,), tail_window=11)


def test_tail_window_kl_returns_correct_per_stream_count() -> None:
    """K streams in → K tail means + K tail KLs out, regardless of horizon."""
    rng = np.random.default_rng(seed=999)
    for K in (1, 2, 3, 5):  # noqa: N806 — K = number of streams.
        trajectories = tuple(rng.dirichlet(np.ones(2), size=50) for _ in range(K))
        # Re-normalize (Dirichlet samples are PMFs already, but be defensive).
        trajectories = tuple(traj / traj.sum(axis=1, keepdims=True) for traj in trajectories)
        tail_means, tail_kls = tail_window_kl(trajectories, tail_window=10)
        assert len(tail_means) == K
        assert len(tail_kls) == K
        for mean in tail_means:
            assert mean.shape == (2,)
            assert mean.sum() == pytest.approx(1.0, abs=1e-12)


def test_tail_window_kl_statistics_names_first_mean_max_semantics() -> None:
    """The richer helper distinguishes first-tail, mean-tail, max-tail,
    and adjacent-step KL instead of overloading one "tail KL" scalar.
    """
    traj = np.array(
        [
            [0.70, 0.30],
            [0.65, 0.35],
            [0.60, 0.40],
            [0.55, 0.45],
            [0.52, 0.48],
        ],
        dtype=np.float64,
    )
    (
        tail_means,
        first_kls,
        mean_kls,
        max_kls,
        adjacent_mean_kls,
        adjacent_max_kls,
    ) = tail_window_kl_statistics((traj,), tail_window=3)

    assert np.allclose(tail_means[0], traj[-3:].mean(axis=0))
    assert first_kls[0] > 0.0
    assert max_kls[0] >= mean_kls[0] >= 0.0
    assert adjacent_max_kls[0] >= adjacent_mean_kls[0] > 0.0
