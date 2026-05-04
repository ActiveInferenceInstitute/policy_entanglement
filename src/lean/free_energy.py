"""Free energies, entropies, and total correlation.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

from joint_dist import joint_marginal, joint_marginals, m_projection

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
    qa = np.asarray(q, dtype=np.float64)
    pa = np.asarray(p, dtype=np.float64)
    if qa.shape != pa.shape:
        raise ValueError(
            f"kl_divergence shape mismatch: q={qa.shape}, p={pa.shape}"
        )
    out = 0.0
    for q_i, p_i in zip(qa.ravel(), pa.ravel()):
        if q_i <= 0.0:
            continue
        if p_i <= 0.0:
            return float("inf")
        out += float(q_i * (np.log(q_i) - np.log(p_i)))
    return out


def joint_entropy(q: ArrayF) -> float:
    """`H(q)` of the joint distribution."""
    return shannon_entropy(q)


def marginal_entropy(q: ArrayF, k: int) -> float:
    """`H(q^k)` — entropy of the kth marginal."""
    return shannon_entropy(joint_marginal(q, k))


def total_correlation(q: ArrayF) -> float:
    """`I(q) = ∑_k H(q^k) − H(q)`.

    Mirrors ``ActinfPolicyEntanglement.totalCorrelation``.  Always
    ``>= 0``, equal to 0 iff `q` is mean-field.
    """
    qa = np.asarray(q, dtype=np.float64)
    margs = joint_marginals(qa)
    return float(sum(shannon_entropy(m) for m in margs) - joint_entropy(qa))


def total_correlation_via_kl(q: ArrayF) -> float:
    """Total correlation computed as ``KL(q ‖ ∏_k q^k)``.

    Numerically equivalent to :func:`total_correlation` (Prop 6.3 in the
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
        raise ValueError(
            f"stream {k}: marginal shape {qk.shape}, prior {Ek.shape},"
            f" G {Gk.shape}"
        )
    expGk = float(np.sum(qk * Gk))
    explogEk = float(np.sum(qk * _safe_log(Ek)))
    return gamma * expGk - explogEk - shannon_entropy(qk)
