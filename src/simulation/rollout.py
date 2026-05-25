"""Coupled-ensemble rollouts: time-series of POMDP inference + coupling."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from lean.free_energy import total_correlation

from .agents import _require_pymdp
from .inference import coupled_policy_posterior, per_stream_policy_posterior
from .specs import CoupledEnsembleSpec

ArrayF = NDArray[np.float64]


@dataclass(frozen=True)
class RolloutStep:
    """One time step of a coupled ensemble rollout."""

    t: int
    observations: tuple[int, ...]
    mean_field_marginals: tuple[ArrayF, ...]
    coupled_joint: ArrayF
    sampled_actions: tuple[int, ...]
    total_correlation: float


@dataclass(frozen=True)
class Rollout:
    """A deterministic coupled-ensemble rollout."""

    steps: tuple[RolloutStep, ...]
    spec: CoupledEnsembleSpec
    lam: float
    seed: int

    def total_correlations(self) -> ArrayF:
        return np.array([s.total_correlation for s in self.steps], dtype=np.float64)

    def joint_trajectory(self) -> ArrayF:
        """``(T, *policy_shape)`` array of coupled joint posteriors."""
        return np.stack([s.coupled_joint for s in self.steps], axis=0)


def _sample_from_joint(q: ArrayF, rng: np.random.Generator) -> tuple[int, ...]:
    flat = q.reshape(-1)
    idx = int(rng.choice(flat.size, p=flat / flat.sum()))
    idx_coords = np.unravel_index(idx, q.shape)
    return tuple(int(i) for i in idx_coords)


def simulate_coupled_rollout(
    spec: CoupledEnsembleSpec,
    *,
    horizon: int = 8,
    lam: float = 1.0,
    seed: int = 0,
    initial_observations: Sequence[int] | None = None,
    on_step: Callable[[RolloutStep], None] | None = None,
) -> Rollout:
    """Drive `spec` for `horizon` steps under coupling `lam`, deterministically
    sampling actions at each step.

    The rollout protocol per step:

      1. Each stream sees its own observation.
      2. We compute the λ-coupled joint policy posterior via
         :func:`coupled_policy_posterior`.
      3. We sample one joint action from that posterior with `rng`.
      4. The next observation per stream is determined by simulating
         each stream's `B` matrix one step under its sampled action,
         then sampling from the resulting `A·s` likelihood.
    """
    _require_pymdp()
    spec.validate()
    rng = np.random.default_rng(int(seed))
    n_streams = spec.num_streams()
    if initial_observations is None:
        initial_observations = tuple(0 for _ in range(n_streams))
    if len(initial_observations) != n_streams:
        raise ValueError(f"initial_observations length {len(initial_observations)} != num_streams={n_streams}")
    obs = list(initial_observations)
    states: list[ArrayF] = [s.D.copy() for s in spec.streams]

    steps: list[RolloutStep] = []
    for t in range(horizon):
        mf = per_stream_policy_posterior(spec, obs)
        # RedTeam Methods C6 (2026-05-20): pass the precomputed `mf` to
        # avoid pymdp re-inference inside `coupled_policy_posterior`
        # (used to be 2× pymdp calls per rollout step; now 1×).
        q_joint = coupled_policy_posterior(spec, obs, lam=lam, precomputed_mf=mf)
        action = _sample_from_joint(q_joint, rng)
        new_states: list[ArrayF] = []
        new_obs: list[int] = []
        for k in range(n_streams):
            s_kernel = spec.streams[k]
            s_next = s_kernel.B[:, :, int(action[k])] @ states[k]
            s_next = s_next / s_next.sum()
            new_states.append(s_next)
            obs_dist = s_kernel.A @ s_next
            obs_dist = obs_dist / obs_dist.sum()
            new_obs.append(int(rng.choice(obs_dist.size, p=obs_dist)))
        step = RolloutStep(
            t=t,
            observations=tuple(obs),
            mean_field_marginals=tuple(mf),
            coupled_joint=q_joint,
            sampled_actions=tuple(int(a) for a in action),
            total_correlation=total_correlation(q_joint),
        )
        steps.append(step)
        if on_step is not None:
            on_step(step)
        obs = new_obs
        states = new_states

    return Rollout(steps=tuple(steps), spec=spec, lam=float(lam), seed=int(seed))
