"""Tests for the configured long-horizon coupled rollout (T2).

No mocks: real pymdp.agent.Agent instances drive every step.
"""

from __future__ import annotations

import numpy as np
import pytest

from simulation.agents import pymdp_available

if not pymdp_available():
    pytestmark = pytest.mark.skip(reason="pymdp 1.0.1 not installed (uv sync --group sim)")
else:
    pytestmark = pytest.mark.requires_pymdp


from simulation import hyperparameters as H  # noqa: E402
from simulation.long_horizon import (  # noqa: E402
    LongHorizonResult,
    long_horizon_rollout,
    long_horizon_summary,
    tc_trajectory_recomputable,
    trajectory_marginals_are_pmfs,
    trajectory_tc_finite,
    trajectory_tc_nonneg,
)

# A short rollout for fast tests; the orchestrator script runs the full
# H.LONG_HORIZON_STEPS=100 horizon.  The short horizon is still long
# enough to exercise the tail-window steady-state mechanism (the
# default LONG_HORIZON_TAIL_WINDOW=20 is reduced via parameterization).
_SHORT_T = 25
_SHORT_WINDOW = 8


@pytest.fixture(scope="module")
def short_result() -> LongHorizonResult:
    return long_horizon_rollout(
        coupling_lambda_gen=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
        num_streams=int(H.PYMDP_ENSEMBLE_K),
        horizon=_SHORT_T,
        lam=float(H.LONG_HORIZON_LAMBDA),
        seed=int(H.LONG_HORIZON_SEED),
        tail_window=_SHORT_WINDOW,
        steady_state_tol=float(H.LONG_HORIZON_STEADY_STATE_TOL),
    )


def test_long_horizon_returns_record_with_correct_shape(
    short_result: LongHorizonResult,
) -> None:
    assert isinstance(short_result, LongHorizonResult)
    assert short_result.T == _SHORT_T
    assert short_result.lam == pytest.approx(float(H.LONG_HORIZON_LAMBDA))
    assert short_result.total_correlations.shape == (_SHORT_T,)
    assert len(short_result.marginal_trajectories) == int(H.PYMDP_ENSEMBLE_K)
    assert short_result.joint_trajectory.shape == (
        _SHORT_T,
        *(2 for _ in range(int(H.PYMDP_ENSEMBLE_K))),
    )
    assert short_result.tail_window == _SHORT_WINDOW
    for traj in short_result.marginal_trajectories:
        assert traj.shape == (_SHORT_T, 2)
    assert len(short_result.tail_marginal_means) == int(H.PYMDP_ENSEMBLE_K)
    assert len(short_result.tail_kl_per_stream) == int(H.PYMDP_ENSEMBLE_K)
    assert len(short_result.tail_kl_first_per_stream) == int(H.PYMDP_ENSEMBLE_K)
    assert len(short_result.tail_kl_mean_per_stream) == int(H.PYMDP_ENSEMBLE_K)
    assert len(short_result.tail_kl_max_per_stream) == int(H.PYMDP_ENSEMBLE_K)
    assert len(short_result.adjacent_kl_max_per_stream) == int(H.PYMDP_ENSEMBLE_K)


def test_long_horizon_tc_is_nonneg_and_finite(
    short_result: LongHorizonResult,
) -> None:
    assert trajectory_tc_nonneg(short_result)
    assert trajectory_tc_finite(short_result)


def test_long_horizon_marginals_are_pmfs(
    short_result: LongHorizonResult,
) -> None:
    assert trajectory_marginals_are_pmfs(short_result, atol=1e-6)


def test_long_horizon_tc_trajectory_recomputable(
    short_result: LongHorizonResult,
) -> None:
    assert tc_trajectory_recomputable(short_result)


def test_long_horizon_progress_callback_invoked() -> None:
    seen: list[tuple[int, int]] = []

    def cb(step: int, total: int) -> None:
        seen.append((step, total))

    long_horizon_rollout(
        coupling_lambda_gen=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
        num_streams=int(H.PYMDP_ENSEMBLE_K),
        horizon=5,
        lam=1.0,
        seed=0,
        tail_window=2,
        steady_state_tol=1e-1,
        progress_callback=cb,
    )
    assert seen == [(1, 5), (2, 5), (3, 5), (4, 5), (5, 5)]


def test_long_horizon_validates_horizon_minimum() -> None:
    with pytest.raises(ValueError, match="horizon"):
        long_horizon_rollout(
            coupling_lambda_gen=1.0,
            gamma=1.0,
            num_streams=2,
            horizon=1,
            lam=1.0,
            seed=0,
            tail_window=1,
            steady_state_tol=1e-2,
        )


def test_long_horizon_validates_tail_window_too_large() -> None:
    with pytest.raises(ValueError, match="tail_window"):
        long_horizon_rollout(
            coupling_lambda_gen=1.0,
            gamma=1.0,
            num_streams=2,
            horizon=4,
            lam=1.0,
            seed=0,
            tail_window=10,
            steady_state_tol=1e-2,
        )


def test_long_horizon_deterministic_under_fixed_seed() -> None:
    a = long_horizon_rollout(
        coupling_lambda_gen=1.0,
        gamma=1.0,
        num_streams=2,
        horizon=8,
        lam=1.5,
        seed=7,
        tail_window=3,
        steady_state_tol=1e-2,
    )
    b = long_horizon_rollout(
        coupling_lambda_gen=1.0,
        gamma=1.0,
        num_streams=2,
        horizon=8,
        lam=1.5,
        seed=7,
        tail_window=3,
        steady_state_tol=1e-2,
    )
    assert np.allclose(a.total_correlations, b.total_correlations)
    for ta, tb in zip(a.marginal_trajectories, b.marginal_trajectories, strict=True):
        assert np.allclose(ta, tb)


def test_long_horizon_summary_has_expected_keys(
    short_result: LongHorizonResult,
) -> None:
    summary = long_horizon_summary(short_result)
    expected = {
        "long_horizon_T",
        "long_horizon_lambda",
        "long_horizon_seed",
        "long_horizon_K",
        "long_horizon_tc_initial",
        "long_horizon_tc_final",
        "long_horizon_tc_max",
        "long_horizon_tc_mean",
        "long_horizon_tail_kl_max",
        "long_horizon_tail_kl_sum",
        "long_horizon_tail_kl_first_max",
        "long_horizon_tail_kl_mean_max",
        "long_horizon_tail_kl_window_max",
        "long_horizon_adjacent_kl_mean_max",
        "long_horizon_adjacent_kl_max",
        "long_horizon_tail_window",
        "long_horizon_habit_accumulation",
        "long_horizon_steady_state_tol",
        "long_horizon_tc_trajectory_floor",
        "long_horizon_steady_state_kl",
        "long_horizon_tc_recomputed_max_abs_diff",
    }
    assert expected.issubset(summary.keys())
    assert summary["long_horizon_T"] == float(_SHORT_T)
    assert summary["long_horizon_tail_kl_window_max"] >= summary["long_horizon_tail_kl_mean_max"]


def test_long_horizon_habit_accumulation_is_bool(
    short_result: LongHorizonResult,
) -> None:
    # The flag is well-defined (True or False) once tail_kl_per_stream
    # is set; we don't pin its value because short rollouts may not
    # converge — the orchestrator script runs T=100 to do so.
    assert isinstance(short_result.habit_accumulation, bool)


def test_long_horizon_negative_control_decoupled_does_not_accumulate_habit() -> None:
    """Compare max TC of the λ=0 rollout against max TC of the coupled rollout.

    This is not a tautology because it contrasts two distinct rollouts
    run under identical machinery but different coupling regimes:
    decoupled λ=0 versus the configured positive λ witness.
    """
    decoupled = long_horizon_rollout(
        coupling_lambda_gen=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
        num_streams=int(H.PYMDP_ENSEMBLE_K),
        horizon=_SHORT_T,
        lam=0.0,
        seed=int(H.LONG_HORIZON_SEED),
        tail_window=_SHORT_WINDOW,
        steady_state_tol=float(H.LONG_HORIZON_STEADY_STATE_TOL),
    )
    coupled = long_horizon_rollout(
        coupling_lambda_gen=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
        num_streams=int(H.PYMDP_ENSEMBLE_K),
        horizon=_SHORT_T,
        lam=float(H.LONG_HORIZON_LAMBDA),
        seed=int(H.LONG_HORIZON_SEED),
        tail_window=_SHORT_WINDOW,
        steady_state_tol=float(H.LONG_HORIZON_STEADY_STATE_TOL),
    )
    # 1e-12 is a pure round-off budget because the probed λ=0 rollout has exactly zero cross-stream correlation.
    assert decoupled.total_correlations.max() <= 1e-12
    # 1e-6 stays above float noise and encodes a genuine positive-coupling witness.
    assert coupled.total_correlations.max() > 1e-6
    assert decoupled.habit_accumulation is False


def test_long_horizon_validates_tail_window_too_small() -> None:
    """The ``window < 1`` branch in ``_validate_window`` raises ValueError."""
    with pytest.raises(ValueError, match="tail_window"):
        long_horizon_rollout(
            coupling_lambda_gen=1.0,
            gamma=1.0,
            num_streams=2,
            horizon=4,
            lam=1.0,
            seed=0,
            tail_window=0,
            steady_state_tol=1e-2,
        )


def _synthetic_result(
    *,
    marginals: tuple[np.ndarray, ...],
    tcs: np.ndarray | None = None,
) -> LongHorizonResult:
    """Build a synthetic ``LongHorizonResult`` for invariant tests.

    All fields are filled with deterministic numbers — no pymdp needed.
    """
    T = marginals[0].shape[0]
    K = len(marginals)
    if tcs is None:
        tcs = np.zeros(T, dtype=np.float64)
    tail_means = tuple(m.mean(axis=0) for m in marginals)
    tail_kl = tuple(0.0 for _ in range(K))
    joints = []
    for rows in zip(*marginals, strict=True):
        joint = rows[0]
        for row in rows[1:]:
            joint = np.multiply.outer(joint, row)
        joints.append(np.asarray(joint, dtype=np.float64))
    return LongHorizonResult(
        T=T,
        lam=1.0,
        seed=0,
        total_correlations=tcs.astype(np.float64),
        marginal_trajectories=tuple(m.astype(np.float64) for m in marginals),
        joint_trajectory=np.stack(joints, axis=0),
        tail_marginal_means=tail_means,
        tail_kl_per_stream=tail_kl,
        tail_kl_first_per_stream=tail_kl,
        tail_kl_mean_per_stream=tail_kl,
        tail_kl_max_per_stream=tail_kl,
        adjacent_kl_mean_per_stream=tail_kl,
        adjacent_kl_max_per_stream=tail_kl,
        habit_accumulation=True,
        steady_state_tol=1e-2,
        tail_window=max(1, min(2, T)),
    )


def test_trajectory_marginals_are_pmfs_rejects_negative_entry() -> None:
    """A marginal row containing a negative entry trips the early-exit branch."""
    bad = np.array([[0.5, 0.5], [-0.1, 1.1]])  # row 1 has a negative
    res = _synthetic_result(marginals=(bad,))
    assert trajectory_marginals_are_pmfs(res) is False


def test_trajectory_marginals_are_pmfs_rejects_non_normalized() -> None:
    """A row whose sum ≠ 1 trips the second early-exit branch."""
    bad = np.array([[0.5, 0.5], [0.4, 0.4]])  # row 1 sums to 0.8
    res = _synthetic_result(marginals=(bad,))
    assert trajectory_marginals_are_pmfs(res) is False


def test_tc_trajectory_recomputable_rejects_mismatched_recorded_tc() -> None:
    """A stored TC trajectory that disagrees with the retained joint is rejected."""
    good = np.array([[0.5, 0.5], [0.5, 0.5]])
    res = _synthetic_result(marginals=(good, good), tcs=np.array([0.0, 0.25]))
    assert tc_trajectory_recomputable(res) is False


# Note: the pure-numpy parameterized convergence tests for
# :func:`tail_window_kl` live in :mod:`tests.test_tail_window_kl`
# because they do not require pymdp and must run in the default
# ``uv sync`` environment (the module-level ``pytestmark`` above would
# otherwise skip them).  The pipeline regression guard that compares
# the standalone helper to a real ``LongHorizonResult`` *does* require
# pymdp, so it lives below alongside the rest of this file's tests.


def test_tail_window_kl_recoverable_via_full_pipeline(short_result: LongHorizonResult) -> None:
    """The standalone ``tail_window_kl`` helper agrees with the
    ``LongHorizonResult.tail_kl_per_stream`` field on a real rollout.
    Regression guard for the helper extraction (P1-3 round-5).
    """
    from simulation.long_horizon import tail_window_kl

    _, tail_kls_helper = tail_window_kl(
        short_result.marginal_trajectories,
        _SHORT_WINDOW,
    )
    for a, b in zip(tail_kls_helper, short_result.tail_kl_per_stream, strict=True):
        assert a == pytest.approx(b, abs=1e-12)


def test_divergent_tail_is_rejected_by_stationarity_criterion() -> None:
    """R6b (RedTeam 2026-05-19) — the DISCRIMINATING negative control.

    R6a reframed the long-horizon claim from "habit accumulation" to a
    *trajectory-stationarity* diagnostic; the pre-existing λ=0 control
    only covers the *no-coupling* ("nothing moves") case. RedTeam-H1's
    point is that a near-constant tail is exactly the static case — so a
    genuine discriminating control must show the criterion REJECTS a
    *non-stationary* trajectory at the same tolerance. This proves the
    `max_tail_kl ≤ steady_state_tol` flag is not vacuously always-True.
    """
    from simulation.long_horizon import tail_window_kl_statistics

    tol = float(H.LONG_HORIZON_STEADY_STATE_TOL)
    T, window = 40, 20

    # Divergent: the tail never settles — it oscillates between two
    # far-apart marginals every step, so each tail row's KL to the
    # tail-mean stays large.
    divergent = np.array(
        [([0.9, 0.1] if t % 2 == 0 else [0.1, 0.9]) for t in range(T)],
        dtype=np.float64,
    )
    # Stationary: constant in the tail → per-row KL to tail-mean ≈ 0.
    stationary = np.array([[0.7, 0.3] for _ in range(T)], dtype=np.float64)

    _, _, _, max_div, _, _ = tail_window_kl_statistics((divergent,), window)
    _, _, _, max_stat, _, _ = tail_window_kl_statistics((stationary,), window)

    # The criterion the habit_accumulation flag uses is
    # `all(max_tail_kl <= tol)`. It MUST reject the divergent tail...
    assert max_div[0] > tol, (
        f"divergent tail max-KL {max_div[0]:.4f} ≤ tol {tol} — the "
        "stationarity criterion does NOT discriminate a non-stationary "
        "trajectory (it would vacuously pass; R6b defect)."
    )
    # ...and accept the genuinely stationary one.
    assert max_stat[0] <= tol, (
        f"stationary tail max-KL {max_stat[0]:.6f} > tol {tol} — a genuinely stationary trajectory is wrongly rejected."
    )
