"""Long-horizon coupled-ensemble rollouts.

The default :func:`simulate_coupled_rollout` runs for
:data:`hyperparameters.PYMDP_ROLLOUT_STEPS` steps — enough to
demonstrate the per-step coupling mechanism. To witness "habit
accumulation" (Manuscript §9.4) we need a horizon long enough for
the marginal MF posterior $q^k_t$ to approach a steady-state.

This module wraps :func:`simulation.rollout.simulate_coupled_rollout`
with a richer post-processing layer:

* Time-series of per-stream marginal entropy and joint total
  correlation.
* Tail-window KL divergence against the trailing-window marginal mean
  as a quantitative steady-state convergence witness.
* A boolean ``habit_accumulation`` flag asserting the tail KL falls
  below :data:`hyperparameters.LONG_HORIZON_STEADY_STATE_TOL`.

The module is fully deterministic for a fixed seed; no mocks.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from lean.free_energy import kl_divergence, total_correlation
from lean.joint_dist import joint_marginals

from .agents import _require_pymdp
from .builders import make_ising_ensemble
from .rollout import Rollout, simulate_coupled_rollout

ArrayF = NDArray[np.float64]


@dataclass(frozen=True)
class LongHorizonResult:
    r"""Aggregated outcome of a long-horizon coupled rollout.

    * ``T``                            — number of steps actually executed.
    * ``lam``                          — coupling strength used.
    * ``seed``                         — deterministic seed used.
    * ``total_correlations``           — ``(T,)`` per-step
      $I(q_t)$.
    * ``marginal_trajectories``        — list of ``(T, |Π^k|)``
      arrays, one per stream.
    * ``joint_trajectory``             — ``(T, *policy_shape)`` array
      of full coupled joint posteriors; retained so total correlation
      is exactly recomputable from the stored rollout.
    * ``tail_marginal_means``          — ``(K, |Π^k|)`` mean
      per-stream marginal over the trailing ``tail_window`` steps.
    * ``tail_kl_per_stream``           — legacy alias for
      ``tail_kl_first_per_stream``.
    * ``tail_kl_first_per_stream``     — ``(K,)`` KL divergence of
      the first marginal in the trailing window against the
      trailing-window mean.
    * ``tail_kl_mean_per_stream``      — ``(K,)`` mean KL over all
      rows in the trailing window against the trailing-window mean.
    * ``tail_kl_max_per_stream``       — ``(K,)`` maximum KL over
      the trailing window against the trailing-window mean; used as
      the strict convergence witness.
    * ``adjacent_kl_mean_per_stream``  — ``(K,)`` mean
      $D_{\mathrm{KL}}(q_t^k\|q_{t-1}^k)$ over the whole trajectory.
    * ``adjacent_kl_max_per_stream``   — ``(K,)`` max adjacent-step
      KL over the whole trajectory.
    * ``habit_accumulation``           — True iff every per-stream tail
      KL is below the configured tolerance, i.e. the marginal has
      stopped moving.
    * ``steady_state_tol``             — Tolerance used for the
      convergence test.
    * ``tail_window``                  — trailing-window width used
      to compute ``tail_marginal_means`` and ``tail_kl_per_stream``.
    """

    T: int
    lam: float
    seed: int
    total_correlations: ArrayF
    marginal_trajectories: tuple[ArrayF, ...]
    joint_trajectory: ArrayF
    tail_marginal_means: tuple[ArrayF, ...]
    tail_kl_per_stream: tuple[float, ...]
    tail_kl_first_per_stream: tuple[float, ...]
    tail_kl_mean_per_stream: tuple[float, ...]
    tail_kl_max_per_stream: tuple[float, ...]
    adjacent_kl_mean_per_stream: tuple[float, ...]
    adjacent_kl_max_per_stream: tuple[float, ...]
    habit_accumulation: bool
    steady_state_tol: float
    tail_window: int


def _validate_window(T: int, window: int) -> None:  # noqa: N803 — T = horizon (manuscript symbol).
    """Validate the trailing-window length against the rollout horizon.

    Raises ``ValueError`` if ``window < 1`` (degenerate window) or if
    ``window > T`` (window cannot span more steps than the rollout
    actually has).
    """
    if window < 1:
        raise ValueError(f"tail_window must be ≥ 1, got {window}")
    if window > T:
        raise ValueError(f"tail_window ({window}) > T ({T})")


def tail_window_kl(
    marginal_trajectories: tuple[ArrayF, ...],
    tail_window: int,
) -> tuple[tuple[ArrayF, ...], tuple[float, ...]]:
    """Per-stream tail-window mean + tail-vs-trailing-step KL.

    Convergence witness for *habit accumulation* (§9.4): for each
    stream `k`, take the trailing ``tail_window``-long slice of the
    marginal trajectory, average it to get the trailing-window mean,
    and compute the KL divergence of the *first* marginal in the
    trailing window against the trailing-window mean.  Low KL means
    the marginal has stopped moving — i.e., a steady state has been
    reached.

    Args:
        marginal_trajectories: Tuple of ``(T, |Π^k|)`` arrays, one per
            stream.  All arrays must share the same leading axis ``T``.
        tail_window: Number of trailing steps used for the
            convergence test.  Must satisfy ``1 ≤ tail_window ≤ T``.

    Returns:
        ``(tail_means, tail_kl_per_stream)`` where ``tail_means`` is a
        tuple of ``(|Π^k|,)`` arrays (normalized so each sums to 1)
        and ``tail_kl_per_stream`` is a tuple of floats — one KL per
        stream.

    Raises:
        ValueError: If ``tail_window < 1`` or ``tail_window > T``, via
            :func:`_validate_window`.
    """
    if not marginal_trajectories:
        raise ValueError("marginal_trajectories must be non-empty")
    T = int(marginal_trajectories[0].shape[0])  # noqa: N806 — T = horizon (manuscript symbol).
    _validate_window(T, tail_window)
    start = T - int(tail_window)
    tail_means: list[ArrayF] = []
    tail_kls: list[float] = []
    for traj in marginal_trajectories:
        window = traj[start:]
        mean = window.mean(axis=0)
        mean = mean / mean.sum()
        tail_means.append(mean.astype(np.float64))
        first_in_tail = traj[start]
        kl_v = kl_divergence(first_in_tail, mean)
        tail_kls.append(float(kl_v))
    return tuple(tail_means), tuple(tail_kls)


def tail_window_kl_statistics(
    marginal_trajectories: tuple[ArrayF, ...],
    tail_window: int,
) -> tuple[
    tuple[ArrayF, ...],
    tuple[float, ...],
    tuple[float, ...],
    tuple[float, ...],
    tuple[float, ...],
    tuple[float, ...],
]:
    """Return first/mean/max tail-window KL plus adjacent-step KL summaries.

    For each stream, the tail-window KL family is
    ``D_KL(q_t^k || mean_tail(q^k))`` for
    ``t ∈ {T-tail_window, ..., T-1}``.  Adjacent-step KL is reported
    separately as ``D_KL(q_t^k || q_{t-1}^k)`` over the whole
    trajectory; it is not used as the habit-accumulation criterion.
    """
    if not marginal_trajectories:
        raise ValueError("marginal_trajectories must be non-empty")
    T = int(marginal_trajectories[0].shape[0])  # noqa: N806 — T = horizon (manuscript symbol).
    _validate_window(T, tail_window)
    start = T - int(tail_window)
    tail_means: list[ArrayF] = []
    first_tail_kls: list[float] = []
    mean_tail_kls: list[float] = []
    max_tail_kls: list[float] = []
    adjacent_mean_kls: list[float] = []
    adjacent_max_kls: list[float] = []
    for traj in marginal_trajectories:
        window = traj[start:]
        mean = window.mean(axis=0)
        mean = mean / mean.sum()
        tail_means.append(mean.astype(np.float64))
        tail_kls = np.array(
            [kl_divergence(row, mean) for row in window],
            dtype=np.float64,
        )
        adjacent_kls = np.array(
            [kl_divergence(traj[t], traj[t - 1]) for t in range(1, T)],
            dtype=np.float64,
        )
        first_tail_kls.append(float(tail_kls[0]))
        mean_tail_kls.append(float(tail_kls.mean()))
        max_tail_kls.append(float(tail_kls.max()))
        adjacent_mean_kls.append(float(adjacent_kls.mean()) if adjacent_kls.size else 0.0)
        adjacent_max_kls.append(float(adjacent_kls.max()) if adjacent_kls.size else 0.0)
    return (
        tuple(tail_means),
        tuple(first_tail_kls),
        tuple(mean_tail_kls),
        tuple(max_tail_kls),
        tuple(adjacent_mean_kls),
        tuple(adjacent_max_kls),
    )


def long_horizon_rollout(
    *,
    coupling_lambda_gen: float,
    gamma: float,
    num_streams: int,
    horizon: int,
    lam: float,
    seed: int,
    tail_window: int,
    steady_state_tol: float,
    progress_callback=None,
) -> LongHorizonResult:
    """Run a deterministic coupled rollout of ``horizon`` steps.

    Args:
        coupling_lambda_gen: scale of the underlying Ising J tensor.
        gamma: EFE precision used by the K agents.
        num_streams: K, the number of POMDP streams.
        horizon: rollout length T (steps).
        lam: coupling strength applied to the policy posterior.
        seed: deterministic seed (drives both action sampling and
            observation sampling inside the rollout).
        tail_window: number of trailing steps used for the steady-
            state convergence test.
        steady_state_tol: tolerance under which the tail-vs-trailing
            KL must fall for ``habit_accumulation`` to be True.
        progress_callback: optional ``Callable[[int, int], None]``
            invoked at every step with ``(t, horizon)`` so the
            orchestrator script can emit progress logs for the
            configured long rollout.
    """
    if horizon < 2:
        raise ValueError(f"horizon must be ≥ 2 for habit-accumulation; got {horizon}")
    _require_pymdp()
    _validate_window(horizon, tail_window)

    spec = make_ising_ensemble(
        coupling_amplitude=float(coupling_lambda_gen),
        num_streams=int(num_streams),
        gamma=float(gamma),
    )

    def _on_step(step) -> None:
        """Per-step bridge from :class:`RolloutStep` to the user callback."""
        if progress_callback is not None:
            progress_callback(step.t + 1, int(horizon))

    rollout: Rollout = simulate_coupled_rollout(
        spec,
        horizon=int(horizon),
        lam=float(lam),
        seed=int(seed),
        on_step=_on_step,
    )

    # Per-step total correlation.
    tcs = rollout.total_correlations()
    joints = rollout.joint_trajectory()

    # Marginal time-series per stream: ``(T, |Π^k|)``.
    marg_trajs: list[ArrayF] = []
    for k in range(spec.num_streams()):
        marg_trajs.append(np.stack([s.mean_field_marginals[k] for s in rollout.steps], axis=0))

    # Tail-window mean per stream plus explicit first/mean/max KL
    # semantics — extracted so convergence witnesses can be exercised
    # at any horizon without re-running pymdp.
    (
        tail_means,
        first_tail_kls,
        mean_tail_kls,
        max_tail_kls,
        adjacent_mean_kls,
        adjacent_max_kls,
    ) = tail_window_kl_statistics(tuple(marg_trajs), int(tail_window))

    habit = all(kl <= float(steady_state_tol) for kl in max_tail_kls)

    return LongHorizonResult(
        T=int(horizon),
        lam=float(lam),
        seed=int(seed),
        total_correlations=tcs,
        marginal_trajectories=tuple(marg_trajs),
        joint_trajectory=joints.astype(np.float64),
        tail_marginal_means=tuple(tail_means),
        tail_kl_per_stream=tuple(first_tail_kls),
        tail_kl_first_per_stream=tuple(first_tail_kls),
        tail_kl_mean_per_stream=tuple(mean_tail_kls),
        tail_kl_max_per_stream=tuple(max_tail_kls),
        adjacent_kl_mean_per_stream=tuple(adjacent_mean_kls),
        adjacent_kl_max_per_stream=tuple(adjacent_max_kls),
        habit_accumulation=bool(habit),
        steady_state_tol=float(steady_state_tol),
        tail_window=int(tail_window),
    )


def long_horizon_summary(result: LongHorizonResult) -> dict[str, float]:
    """Manuscript-variable-ready scalars derived from a long-horizon run.

    Stable keys; values are JSON-friendly floats.
    """
    K = len(result.tail_kl_per_stream)  # noqa: N806 — K = number of streams (manuscript symbol).
    out: dict[str, float] = {
        "long_horizon_T": float(result.T),
        "long_horizon_lambda": float(result.lam),
        "long_horizon_seed": float(result.seed),
        "long_horizon_K": float(K),
        "long_horizon_tc_initial": float(result.total_correlations[0]),
        "long_horizon_tc_final": float(result.total_correlations[-1]),
        "long_horizon_tc_max": float(result.total_correlations.max()),
        "long_horizon_tc_mean": float(result.total_correlations.mean()),
        "long_horizon_tail_kl_max": float(max(result.tail_kl_per_stream)),
        "long_horizon_tail_kl_sum": float(sum(result.tail_kl_per_stream)),
        "long_horizon_tail_kl_first_max": float(max(result.tail_kl_first_per_stream)),
        "long_horizon_tail_kl_mean_max": float(max(result.tail_kl_mean_per_stream)),
        "long_horizon_tail_kl_window_max": float(max(result.tail_kl_max_per_stream)),
        "long_horizon_adjacent_kl_mean_max": float(max(result.adjacent_kl_mean_per_stream)),
        "long_horizon_adjacent_kl_max": float(max(result.adjacent_kl_max_per_stream)),
        "long_horizon_tail_window": float(result.tail_window),
        "long_horizon_habit_accumulation": 1.0 if result.habit_accumulation else 0.0,
        "long_horizon_steady_state_tol": float(result.steady_state_tol),
        # Joint total correlation across the *trajectory* (Theorem 5.1
        # ground truth: the coupled joint is the same TC channel as the
        # short-horizon rollout, just measured many times).
        "long_horizon_tc_trajectory_floor": float(result.total_correlations.min()),
    }
    recomputed = recompute_total_correlations(result)
    out["long_horizon_tc_recomputed_max_abs_diff"] = float(np.max(np.abs(recomputed - result.total_correlations)))
    # Backward-compatible headline: the strict max KL over the whole
    # trailing window against its mean.
    out["long_horizon_steady_state_kl"] = float(max(result.tail_kl_max_per_stream))
    return out


# ---------------------------------------------------------------------------
# Lightweight invariants checkable without re-running the rollout
# ---------------------------------------------------------------------------


def trajectory_tc_nonneg(result: LongHorizonResult, atol: float = 1e-9) -> bool:
    """Total correlation is non-negative at every step of the rollout."""
    return bool(np.all(result.total_correlations >= -atol))


def trajectory_tc_finite(result: LongHorizonResult) -> bool:
    """Total correlation is finite at every step (no NaN/Inf)."""
    return bool(np.all(np.isfinite(result.total_correlations)))


def recompute_total_correlations(result: LongHorizonResult) -> ArrayF:
    """Recompute ``I(q_t)`` directly from the stored joint trajectory."""
    return np.array(
        [total_correlation(np.asarray(joint, dtype=np.float64)) for joint in result.joint_trajectory],
        dtype=np.float64,
    )


def trajectory_marginals_are_pmfs(result: LongHorizonResult, atol: float = 1e-7) -> bool:
    """Every per-stream marginal across the trajectory is a proper PMF."""
    for traj in result.marginal_trajectories:
        if not np.all(traj >= -atol):
            return False
        sums = traj.sum(axis=1)
        if not np.allclose(sums, 1.0, atol=atol):
            return False
    return True


def tc_trajectory_recomputable(result: LongHorizonResult, atol: float = 1e-9) -> bool:
    """Sanity check: every recorded step TC equals the
    :func:`lean.free_energy.total_correlation` of the corresponding joint.

    Returns True iff the recomputed values agree with the recorded ones
    to ``atol``.
    """
    recomputed = recompute_total_correlations(result)
    return bool(np.all(np.isfinite(recomputed)) and np.allclose(recomputed, result.total_correlations, atol=atol))


__all__ = [
    "LongHorizonResult",
    "long_horizon_rollout",
    "long_horizon_summary",
    "recompute_total_correlations",
    "tail_window_kl",
    "tail_window_kl_statistics",
    "tc_trajectory_recomputable",
    "trajectory_marginals_are_pmfs",
    "trajectory_tc_finite",
    "trajectory_tc_nonneg",
]


# (joint_marginals imported above for downstream consumers that might
# want to recover full per-step marginal bundles from a Rollout.)
_ = joint_marginals
