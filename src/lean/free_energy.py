"""Free energies, entropies, and total correlation.

Information-theoretic primitives for joint and per-stream distributions
over policy spaces.  All quantities are in *nats* (natural log).

The total-correlation identity ``I(q) = Σ_k H(q^k) - H(q)`` is the
multi-information cost in the decomposition theorem (Theorem 5.1);
``total_correlation_via_kl`` exposes the equivalent
``D_KL(q ‖ ∏_k q^k)`` form (proved equivalent in Proposition 7.3).

Example::

    >>> import numpy as np
    >>> from lean.free_energy import total_correlation
    >>> q_mf = np.array([[0.25, 0.25], [0.25, 0.25]])    # uniform on 2×2
    >>> float(total_correlation(q_mf))                    # zero on MF manifold
    0.0
    >>> q_align = np.array([[0.5, 0.0], [0.0, 0.5]])      # perfect alignment
    >>> round(float(total_correlation(q_align)), 3)       # → log 2 ≈ 0.693
    0.693
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

from .joint_dist import joint_marginal, joint_marginals, m_projection

ArrayF = NDArray[np.float64]

_LOG_FLOOR = 1e-300  # avoid log(0); finite-mass entries dominate.


def _safe_log(p: ArrayF) -> ArrayF:
    """Elementwise ``log(p)`` with a numerical floor; zero entries map to
    ``log(_LOG_FLOOR)``.  Used inside ``∑ p · log(...)`` where the
    sentinel is multiplied by zero anyway."""
    pa = np.asarray(p, dtype=np.float64)
    return np.log(np.where(pa > 0.0, pa, _LOG_FLOOR))


def shannon_entropy(p: ArrayF) -> float:
    """`H(p) = −∑ p · log p` (natural log).  Boundary: nonneg; equal to 0
    iff `p` is a delta."""
    pa = np.asarray(p, dtype=np.float64)
    mask = pa > 0.0
    return float(-(pa[mask] * np.log(pa[mask])).sum())


def kl_divergence(q: ArrayF, p: ArrayF) -> float:
    """`KL(q ‖ p) = ∑ q · log(q/p)`.

    Returns ``+inf`` if `p` has zero mass on a point where `q` does not
    (absolute-continuity violation).
    """
    qa = np.asarray(q, dtype=np.float64).ravel()
    pa = np.asarray(p, dtype=np.float64).ravel()
    if qa.shape != pa.shape:
        q_shape = getattr(q, "shape", qa.shape)
        p_shape = getattr(p, "shape", pa.shape)
        raise ValueError(f"kl_divergence shape mismatch: q={q_shape}, p={p_shape}")
    mask_q = qa > 0.0
    # Absolute-continuity check: p=0 where q>0 → +inf.
    if np.any(pa[mask_q] <= 0.0):
        return float("inf")
    return float(np.sum(qa[mask_q] * (np.log(qa[mask_q]) - np.log(pa[mask_q]))))


def joint_entropy(q: ArrayF) -> float:
    """`H(q)` of the joint distribution."""
    return shannon_entropy(q)


def marginal_entropy(q: ArrayF, k: int) -> float:
    """`H(q^k)` — entropy of the kth marginal."""
    return shannon_entropy(joint_marginal(q, k))


def total_correlation(q: ArrayF) -> float:
    """`I(q) = ∑_k H(q^k) − H(q)`.

    The Python companion computes the per-stream marginals from `q`
    directly and returns the multi-information.

    Lean parity: this implements the same mathematical quantity as
    ``ActinfPolicyEntanglement.totalCorrelation q s sumStreamEntropies``
    when ``sumStreamEntropies = sum(shannon_entropy(m) for m in joint_marginals(q))``
    and ``s`` enumerates the joint policy support.  See
    :func:`total_correlation_lean_companion` for the Lean-shaped variant
    that exposes ``sumStreamEntropies`` as an explicit argument.

    Always ``>= 0``, equal to 0 iff `q` is mean-field.
    """
    qa = np.asarray(q, dtype=np.float64)
    margs = joint_marginals(qa)
    return float(sum(shannon_entropy(m) for m in margs) - joint_entropy(qa))


def total_correlation_lean_companion(q: ArrayF, sum_stream_entropies: float) -> float:
    """`I(q) = sum_stream_entropies − H(q)` — Lean-boundary-shaped form.

    Byte-for-byte parity with the boundary-fragment Lean definition
    ``ActinfPolicyEntanglement.totalCorrelation q s sumStreamEntropies``,
    which takes the per-stream entropy sum as an explicit Float
    parameter and subtracts the joint Shannon entropy.

    For any joint `q`, the identity
    ``total_correlation_lean_companion(q, sum(shannon_entropy(m) for m in joint_marginals(q)))
        == total_correlation(q)``
    holds to floating tolerance — this is the numerical witness that
    the boundary fragment's two-argument formula is the real multi-
    information rather than a placeholder.
    """
    qa = np.asarray(q, dtype=np.float64)
    return float(sum_stream_entropies - joint_entropy(qa))


def total_correlation_via_kl(q: ArrayF) -> float:
    """Total correlation computed as ``KL(q ‖ ∏_k q^k)``.

    Numerically equivalent to :func:`total_correlation` (Prop 7.3 in the
    manuscript) — exposed here so tests can verify the equivalence.
    """
    return kl_divergence(q, m_projection(q))


def free_energy(q: ArrayF, prior: ArrayF, G: ArrayF, gamma: float) -> float:
    """`F[q] = gamma · E_q[G] − E_q[log prior] − H(q)` (variational FE).

    Mirrors ``ActinfPolicyEntanglement.freeEnergy``.
    """
    qa = np.asarray(q, dtype=np.float64)
    pa = np.asarray(prior, dtype=np.float64)
    Ga = np.asarray(G, dtype=np.float64)
    if qa.shape != pa.shape or qa.shape != Ga.shape:
        raise ValueError("q, prior, G must share a common shape")
    expG = float(np.sum(qa * Ga))
    explogp = float(np.sum(qa * _safe_log(pa)))
    return gamma * expG - explogp - shannon_entropy(qa)


def marginal_free_energy(
    q: ArrayF,
    mf_prior: Sequence[ArrayF],
    per_stream_G: Sequence[ArrayF],
    gamma: float,
    k: int,
) -> float:
    """Per-stream marginal free energy.

    `F[q^k] = gamma · E_{q^k}[G_k] − E_{q^k}[log E_k] − H(q^k)`.
    """
    qa = np.asarray(q, dtype=np.float64)
    qk = joint_marginal(qa, k)
    Ek = np.asarray(mf_prior[k], dtype=np.float64)
    Gk = np.asarray(per_stream_G[k], dtype=np.float64)
    if qk.shape != Ek.shape or qk.shape != Gk.shape:
        raise ValueError(f"stream {k}: marginal shape {qk.shape}, prior {Ek.shape}, G {Gk.shape}")
    expGk = float(np.sum(qk * Gk))
    explogEk = float(np.sum(qk * _safe_log(Ek)))
    return gamma * expGk - explogEk - shannon_entropy(qk)
