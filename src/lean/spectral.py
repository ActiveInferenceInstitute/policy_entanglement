"""Spectral structure of the bipartite (K=2) joint policy posterior.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import cast

import numpy as np
from numpy.typing import NDArray

ArrayF = NDArray[np.float64]


@dataclass(frozen=True)
class Archetype:
    """A single archetypal mode `(weight, u, v)` from the SVD of a K=2
    joint policy posterior.  Mirrors the Lean ``Archetype`` structure.

    `weight = s_alpha` (singular value), `u`/`v` are unit-norm marginal
    patterns on the two streams.
    """
    weight: float
    u: ArrayF
    v: ArrayF


def schmidt_rank(q: ArrayF, atol: float = 1e-12) -> int:
    """Schmidt rank of a bipartite (K=2) joint policy posterior.

    Mirrors ``Bipartite.schmidtRank``.  Computes ``# {s : s > atol}``.
    """
    qa = np.asarray(q, dtype=np.float64)
    if qa.ndim != 2:
        raise ValueError(f"schmidt_rank requires K=2 (ndim=2), got ndim={qa.ndim}")
    s = np.linalg.svd(qa, compute_uv=False)
    return int(np.sum(s > atol))


def schmidt_decomposition(q: ArrayF, atol: float = 1e-12) -> list[Archetype]:
    """Full Schmidt decomposition of a K=2 joint as a list of
    :class:`Archetype` modes, in descending weight order.
    """
    qa = np.asarray(q, dtype=np.float64)
    if qa.ndim != 2:
        raise ValueError(f"schmidt_decomposition requires K=2, got ndim={qa.ndim}")
    U, s, Vh = np.linalg.svd(qa, full_matrices=False)
    out: list[Archetype] = []
    for alpha, sv in enumerate(s):
        if sv <= atol:
            break
        out.append(Archetype(weight=float(sv), u=U[:, alpha].copy(), v=Vh[alpha, :].copy()))
    return out


def entanglement_entropy(q: ArrayF, atol: float = 1e-12) -> float:
    """Policy entanglement entropy ``S_E = -∑ p_alpha · log p_alpha``
    where ``p_alpha = s_alpha² / ∑ s²``.

    Mirrors ``Bipartite.entanglementEntropy``.
    """
    qa = np.asarray(q, dtype=np.float64)
    if qa.ndim != 2:
        raise ValueError(f"entanglement_entropy requires K=2, got ndim={qa.ndim}")
    s = np.linalg.svd(qa, compute_uv=False)
    s2 = s * s
    total = s2.sum()
    if total <= atol:
        return 0.0
    p = s2 / total
    mask = p > atol
    return float(-(p[mask] * np.log(p[mask])).sum())


def schmidt_rank_one_iff_mean_field(q: ArrayF, atol: float = 1e-9) -> bool:
    """Verify Prop 7.1: rank-1 Schmidt iff `q` is mean-field.

    Numerical predicate that returns ``True`` iff the (boolean)
    equivalence holds for the given `q`.
    """
    from joint_dist import is_mean_field
    rank_one = schmidt_rank(q, atol=atol) == 1
    mf = is_mean_field(q, atol=atol)
    return rank_one == mf


def tensor_train_ranks(q: ArrayF, atol: float = 1e-12) -> list[int]:
    """Tensor-train (matrix-product-state) bond dimensions across each
    cut ``{1..k} | {k+1..K}`` of the joint tensor `q`.

    Mirrors ``ActinfPolicyEntanglement.tensorTrainRanks``.  Returns a
    list of length ``K-1``.
    """
    qa = np.asarray(q, dtype=np.float64)
    K = qa.ndim
    if K < 2:
        return []
    out: list[int] = []
    flat = qa.copy()
    left_dim = 1
    for k in range(K - 1):
        # Reshape to (left_dim · q.shape[k], rest)
        right_dim = int(np.prod(flat.shape[1:]))
        m = flat.reshape(flat.shape[0], right_dim)
        s = np.linalg.svd(m, compute_uv=False)
        rank = int(np.sum(s > atol))
        out.append(rank)
        # Carry forward the residual for the next cut
        if k + 1 < K - 1:
            flat = flat.reshape(flat.shape[0] * flat.shape[1], *flat.shape[2:])
        left_dim *= flat.shape[0]
    return out


def entanglement_spectrum(q: ArrayF) -> list[int]:
    """Multi-stream entanglement spectrum: the K-1 bond dimensions.

    Synonym for :func:`tensor_train_ranks`; mirrors the Lean name.
    """
    return tensor_train_ranks(q)


def archetype_marginal_pattern(arch: Archetype, atol: float = 1e-12) -> tuple[ArrayF, ArrayF]:
    """Return the unit-norm marginal pattern pair `(u, v)` of an archetype,
    re-normalised to be probability-like (non-negative, summing to 1) when
    that's possible without sign-flipping.
    """
    u = np.asarray(arch.u, dtype=np.float64)
    v = np.asarray(arch.v, dtype=np.float64)
    return u, v
