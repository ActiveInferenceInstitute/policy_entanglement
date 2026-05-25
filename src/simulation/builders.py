"""Deterministic constructors for streams and Ising K-stream ensembles."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .specs import CoupledEnsembleSpec, StreamSpec

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
    n_streams = len(shape)
    if n_streams < 2:
        raise ValueError("Ising coupling requires K ≥ 2")
    k_p = np.zeros(shape, dtype=np.float64)
    for idx in np.ndindex(*shape):
        same = sum(1 for i in range(n_streams) for j in range(i + 1, n_streams) if idx[i] == idx[j])
        diff = (n_streams * (n_streams - 1)) // 2 - same
        k_p[idx] = float(same - diff)
    k_p -= float(k_p.mean())
    if scale == 0.0:
        return np.zeros_like(k_p)
    peak = np.abs(k_p).max()
    if peak > 0.0:
        k_p *= scale / peak
    return k_p


def make_ising_ensemble(
    *,
    coupling_amplitude: float | None = None,
    coupling_lambda: float | None = None,
    preference_strength: float = 1.0,
    num_streams: int = 2,
    gamma: float = 1.0,
) -> CoupledEnsembleSpec:
    """A K-stream Ising ensemble whose coupling potential extends the
    K=2 Ising toy in :mod:`bernoulli_toy`.  See
    :func:`ising_coupling_tensor` for the K>2 generalization.

    **API note (RedTeam Methods B1, 2026-05-20).**  This builder's
    coupling parameter was previously named ``coupling_lambda``, which
    is semantically misleading: callers downstream apply
    ``exp(lam·J)`` for a *probe-grid* ``lam``, so the value baked into
    ``J`` here is a *peak amplitude*, not a ``λ`` value.  The
    parameter has been renamed to ``coupling_amplitude``; the legacy
    ``coupling_lambda`` kwarg is still accepted (one-release
    deprecation alias) and emits a ``DeprecationWarning`` when used.
    Passing both arguments simultaneously raises ``ValueError``.
    """
    if coupling_amplitude is not None and coupling_lambda is not None:
        raise ValueError(
            "make_ising_ensemble: pass either `coupling_amplitude` "
            "(preferred) or `coupling_lambda` (deprecated alias), not both."
        )
    if coupling_lambda is not None:
        import warnings

        warnings.warn(
            "make_ising_ensemble(coupling_lambda=...) is deprecated and "
            "will be removed in a future release; use "
            "make_ising_ensemble(coupling_amplitude=...) instead. The "
            "rename clarifies that this value scales the *peak* of `J`, "
            "not the downstream probe-grid `λ` (which multiplies `J` "
            "downstream via `exp(lam·J)`).",
            DeprecationWarning,
            stacklevel=2,
        )
        coupling_amplitude = coupling_lambda
    if coupling_amplitude is None:
        coupling_amplitude = 1.0

    streams = tuple(
        make_bernoulli_stream(
            name=f"stream_{k}",
            preference_strength=preference_strength,
            prior_bias=0.5,
        )
        for k in range(num_streams)
    )
    shape = tuple(2 for _ in range(num_streams))
    j_mat = ising_coupling_tensor(shape, scale=coupling_amplitude)
    kc_mat = np.zeros(shape, dtype=np.float64)
    spec = CoupledEnsembleSpec(streams=streams, coupling_j=j_mat, coupling_kc=kc_mat, gamma=gamma)
    spec.validate()
    return spec
