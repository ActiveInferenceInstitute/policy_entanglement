"""Coupled-ensemble rollouts: time-series of POMDP inference + coupling.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Callable

import numpy as np
from numpy.typing import NDArray

from free_energy import total_correlation

from agents import _require_pymdp
from inference import coupled_policy_posterior, per_stream_policy_posterior
from specs import CoupledEnsembleSpec

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
    return np.unravel_index(idx, q.shape)


def simulate_coupled_rollout(
    spec: CoupledEnsembleSpec,
    *,
    T: int = 8,
    lam: float = 1.0,
    seed: int = 0,
    initial_observations: Sequence[int] | None = None,
    on_step: Callable[[RolloutStep], None] | None = None,
) -> Rollout:
    """Drive `spec` for `T` steps under coupling `lam`, deterministically
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
    K = spec.K()
    if initial_observations is None:
        initial_observations = tuple(0 for _ in range(K))
    if len(initial_observations) != K:
        raise ValueError(
            f"initial_observations length {len(initial_observations)} != K={K}"
        )
    obs = list(initial_observations)
    states: list[ArrayF] = [s.D.copy() for s in spec.streams]

    steps: list[RolloutStep] = []
    for t in range(T):
        mf = per_stream_policy_posterior(spec, obs)
        q_joint = coupled_policy_posterior(spec, obs, lam=lam)
        action = _sample_from_joint(q_joint, rng)
        new_states: list[ArrayF] = []
        new_obs: list[int] = []
        for k in range(K):
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
