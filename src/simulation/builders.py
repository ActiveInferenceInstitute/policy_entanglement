"""Deterministic constructors for streams and Ising K-stream ensembles.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from specs import CoupledEnsembleSpec, StreamSpec

ArrayF = NDArray[np.float64]


def two_state_identity_likelihood(num_states: int = 2) -> ArrayF:
    """Identity observation likelihood: ``A = I``.  Each state emits its
    own discrete signal — fully observable in the limit.
    """
    return np.eye(num_states, dtype=np.float64)


def two_action_swap_transitions(num_states: int = 2) -> ArrayF:
    """Two-action transition tensor.

    * Action 0 ("hold") preserves the state.
    * Action 1 ("swap") cycles to the next state.

    Returns shape ``(num_states, num_states, 2)``.
    """
    if num_states < 2:
        raise ValueError("need at least 2 states")
    B = np.zeros((num_states, num_states, 2), dtype=np.float64)
    B[:, :, 0] = np.eye(num_states)
    B[:, :, 1] = np.roll(np.eye(num_states), 1, axis=0)
    return B


def make_bernoulli_stream(
    name: str,
    *,
    preference_strength: float = 1.0,
    prior_bias: float = 0.5,
) -> StreamSpec:
    """A 2-state, 2-action stream that mirrors one half of the K=2
    Ising toy in :mod:`bernoulli_toy`.
    """
    A = two_state_identity_likelihood(2)
    B = two_action_swap_transitions(2)
    C = np.array([0.0, preference_strength], dtype=np.float64)
    D = np.array([prior_bias, 1.0 - prior_bias], dtype=np.float64)
    spec = StreamSpec(A=A, B=B, C=C, D=D, name=name)
    spec.validate()
    return spec


def ising_coupling_tensor(shape: tuple[int, ...], scale: float = 1.0) -> ArrayF:
    """Pairwise-aligned Ising coupling on a `K`-dim hypercube.

    For K=2 this matches ``[[scale/2, -scale/2], [-scale/2, scale/2]]``
    after the scaling step (since the swing is 1 and the mean is 0); for
    K>2, every all-equal corner gets weight proportional to the number
    of aligned pairs and other corners are penalised proportionally.
    Mean is zero.
    """
    K = len(shape)
    if K < 2:
        raise ValueError("Ising coupling requires K ≥ 2")
    Kp = np.zeros(shape, dtype=np.float64)
    for idx in np.ndindex(*shape):
        same = sum(1 for i in range(K) for j in range(i + 1, K) if idx[i] == idx[j])
        diff = (K * (K - 1)) // 2 - same
        Kp[idx] = float(same - diff)
    Kp -= float(Kp.mean())
    if scale == 0.0:
        return np.zeros_like(Kp)
    peak = np.abs(Kp).max()
    if peak > 0.0:
        Kp *= scale / peak
    return Kp


def make_ising_ensemble(
    *,
    coupling_lambda: float = 1.0,
    preference_strength: float = 1.0,
    K: int = 2,
    gamma: float = 1.0,
) -> CoupledEnsembleSpec:
    """A K-stream Ising ensemble whose coupling potential extends the
    K=2 Ising toy in :mod:`bernoulli_toy`.  See
    :func:`ising_coupling_tensor` for the K>2 generalisation.
    """
    streams = tuple(
        make_bernoulli_stream(
            name=f"stream_{k}",
            preference_strength=preference_strength,
            prior_bias=0.5,
        )
        for k in range(K)
    )
    shape = tuple(2 for _ in range(K))
    J = ising_coupling_tensor(shape, scale=coupling_lambda)
    Kc = np.zeros(shape, dtype=np.float64)
    spec = CoupledEnsembleSpec(streams=streams, coupling_J=J, coupling_Kc=Kc, gamma=gamma)
    spec.validate()
    return spec
