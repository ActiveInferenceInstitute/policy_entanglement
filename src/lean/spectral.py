"""Spectral structure of the bipartite (K=2) joint policy posterior.

Schmidt decomposition, archetypal eigenvectors, and tensor-train bond
dimensions for joint posteriors over multi-stream policy spaces.

The load-bearing identity ([[THMREF:prop_7_1]]) is: a bipartite joint
``q`` is mean-field iff its Schmidt rank is 1.  ``schmidt_rank`` is
the operational test; ``schmidt_decomposition`` returns the archetypal
``(weight, u, v)`` triples in descending weight order.

For ``K > 2`` streams, ``tensor_train_ranks`` returns the bond
dimensions ``(r_1, ..., r_{K-1})`` across the canonical left-to-right
cuts.  Low-rank coupling potentials produce low-rank posteriors
([[THMREF:thm_7_3]] sparsity-rank tradeoff).

Example::

    >>> import numpy as np
    >>> from lean.spectral import schmidt_rank, tensor_train_ranks
    >>> q_mf = np.outer([0.5, 0.5], [0.5, 0.5])
    >>> schmidt_rank(q_mf, atol=1e-9)
    1
    >>> q_anti = np.array([[0.5, 0.0], [0.0, 0.5]])
    >>> schmidt_rank(q_anti, atol=1e-9)
    2

Lean companion: ``ActinfPolicyEntanglement.Spectral.Bipartite`` for
the rank-1 ↔ mean-field equivalence.  The Python side computes
tensor-train ranks numerically now; a separate additive
``MathlibProofs`` layer is where SVD/rank-continuity witness payloads
are discharged without changing the boundary package.
"""

from __future__ import annotations

from dataclasses import dataclass

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
    from .joint_dist import is_mean_field

    rank_one = schmidt_rank(q, atol=atol) == 1
    mf = is_mean_field(q, atol=atol)
    return bool(rank_one == mf)


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
    for k in range(K - 1):
        right_dim = int(np.prod(flat.shape[1:]))
        m = flat.reshape(flat.shape[0], right_dim)
        s = np.linalg.svd(m, compute_uv=False)
        out.append(int(np.sum(s > atol)))
        if k + 1 < K - 1:
            flat = flat.reshape(flat.shape[0] * flat.shape[1], *flat.shape[2:])
    return out


def entanglement_spectrum(q: ArrayF) -> list[int]:
    """Multi-stream entanglement spectrum: the K-1 bond dimensions.

    Synonym for :func:`tensor_train_ranks`; mirrors the Lean name.
    """
    return tensor_train_ranks(q)


def archetype_marginal_pattern(arch: Archetype, atol: float = 1e-12) -> tuple[ArrayF, ArrayF]:
    """Return the unit-norm marginal pattern pair `(u, v)` of an archetype,
    re-normalized to be probability-like (non-negative, summing to 1) when
    that's possible without sign-flipping.
    """
    u = np.asarray(arch.u, dtype=np.float64)
    v = np.asarray(arch.v, dtype=np.float64)
    return u, v


def entanglement_entropy_per_cut(q: ArrayF, k: int, atol: float = 1e-12) -> float:
    """Per-cut bond entropy: entanglement entropy across the bipartition
    splitting streams ``{1..k+1}`` from ``{k+2..K}`` of the
    ``K``-dimensional joint tensor `q` (0-indexed cut ``k`` lies between
    axis ``k`` and axis ``k+1``).

    This is the composition of :func:`entanglement_entropy` with a
    per-cut bipartite reshape; for ``K = 2`` and ``k = 0`` it coincides
    exactly with :func:`entanglement_entropy`.  Implements the
    manuscript symbol ``S_k(q_lambda)`` (S06 "Spectral and
    tensor-network symbols").
    """
    qa = np.asarray(q, dtype=np.float64)
    K = qa.ndim
    if K < 2:
        raise ValueError(f"entanglement_entropy_per_cut requires ndim>=2, got {K}")
    if not 0 <= k < K - 1:
        raise ValueError(f"cut index k must be in [0, {K - 2}], got {k}")
    left = int(np.prod(qa.shape[: k + 1]))
    right = int(np.prod(qa.shape[k + 1 :]))
    return entanglement_entropy(qa.reshape(left, right), atol=atol)


def mps_decomposition(q: ArrayF, atol: float = 1e-12) -> list[ArrayF]:
    """Left-canonical matrix-product-state (tensor-train) decomposition
    of the joint tensor `q` into per-site factors ``A^{(k)}`` via
    successive SVDs.

    Returns ``K`` site tensors; site ``k`` has shape
    ``(r_{k}, d_k, r_{k+1})`` with ``r_0 = r_K = 1``.  The full
    left-to-right contraction of the returned factors reconstructs `q`
    to floating tolerance (the load-bearing invariant; verified in
    ``tests/test_spectral.py``).  Convention: **canonical
    left-orthogonal TT-SVD** — the same successive-SVD procedure that
    underlies :func:`tensor_train_ranks`.  Implements the manuscript
    symbol ``A^{(k)}`` (S06 "Spectral and tensor-network symbols").
    """
    qa = np.asarray(q, dtype=np.float64)
    K = qa.ndim
    if K < 1:
        raise ValueError("mps_decomposition requires ndim>=1")
    dims = qa.shape
    factors: list[ArrayF] = []
    rprev = 1
    remainder = qa.reshape(rprev, qa.size)
    for axis in range(K):
        dk = dims[axis]
        cols = remainder.size // (rprev * dk)
        mat = remainder.reshape(rprev * dk, cols)
        U, s, Vh = np.linalg.svd(mat, full_matrices=False)
        rank = int(np.sum(s > atol)) or 1
        U, s, Vh = U[:, :rank], s[:rank], Vh[:rank, :]
        factors.append(U.reshape(rprev, dk, rank))
        remainder = s[:, None] * Vh
        rprev = rank
    # remainder is now a (rprev, 1) residual gauge scalar; fold into the last site
    factors[-1] = factors[-1] * float(np.asarray(remainder).reshape(-1)[0])
    return factors
