"""Joint and mean-field policy distributions over finite policy spaces."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
from numpy.typing import NDArray

ArrayF = NDArray[np.float64]


def _as_float64(a: Any) -> ArrayF:
    """Cast to float64 ndarray without copy when possible."""
    return np.asarray(a, dtype=np.float64)


def is_non_negative(q: ArrayF, atol: float = 0.0) -> bool:
    """Return True iff every entry of `q` is at least `-atol`."""
    return bool(np.all(_as_float64(q) >= -atol))


def is_pmf(q: ArrayF, atol: float = 1e-9) -> bool:
    """Predicate: `q` is a (joint or per-stream) probability mass function.

    Mirrors ``ActinfPolicyEntanglement.IsPMF`` from the Lean module.
    """
    qa = _as_float64(q)
    return bool(np.all(qa >= -atol)) and bool(abs(qa.sum() - 1.0) <= atol)


def normalize(q: ArrayF) -> ArrayF:
    """Divide by the total mass; raises if `q` sums to zero."""
    qa = _as_float64(q)
    s = qa.sum()
    if s <= 0.0:
        raise ValueError(f"cannot normalize a non-positive mass: total={s}")
    return np.asarray(qa / s, dtype=np.float64)


def mean_field_to_joint(marginals: Sequence[ArrayF]) -> ArrayF:
    """Embed a mean-field tuple of marginals as a joint via outer product.

    Equivalent to ``ActinfPolicyEntanglement.MFDist.toJoint`` from the
    Lean boundary, but with the actual outer product computed.
    """
    if not marginals:
        raise ValueError("mean_field_to_joint requires at least one stream")
    out = _as_float64(marginals[0])
    for m in marginals[1:]:
        out = np.multiply.outer(out, _as_float64(m))
    return out


def joint_marginal(q: ArrayF, k: int) -> ArrayF:
    """Marginal of `q` on stream `k`.

    Sums over all other streams, returning a 1-D ndarray of length
    ``q.shape[k]``.  Mirrors ``JointDist.marginal``.
    """
    qa = _as_float64(q)
    if not 0 <= k < qa.ndim:
        raise IndexError(f"stream index {k} out of range for ndim={qa.ndim}")
    other_axes = tuple(i for i in range(qa.ndim) if i != k)
    return np.asarray(qa.sum(axis=other_axes) if other_axes else qa.copy(), dtype=np.float64)


def joint_marginals(q: ArrayF) -> list[ArrayF]:
    """All per-stream marginals of `q` as a list of 1-D arrays.

    Mirrors ``JointDist.marginals`` (the m-projection bundle).
    """
    qa = _as_float64(q)
    return [joint_marginal(qa, k) for k in range(qa.ndim)]


def is_mean_field(q: ArrayF, atol: float = 1e-9) -> bool:
    """Predicate: `q` factorizes as the outer product of its marginals.

    Mirrors ``ActinfPolicyEntanglement.IsMeanField``.  Numerically: a
    joint is mean-field iff the L1 distance from the m-projection product
    is zero.
    """
    qa = _as_float64(q)
    proj = mean_field_to_joint(joint_marginals(qa))
    return bool(np.max(np.abs(qa - proj)) <= atol)


def m_projection(q: ArrayF) -> ArrayF:
    """Marginalize and re-multiply: `q -> ∏_k q^k`.

    The dual-flat m-projection onto the mean-field submanifold; see
    ``ActinfPolicyEntanglement.mProjection`` in the Lean module.  This is
    the closest mean-field to `q` in KL distance.
    """
    return mean_field_to_joint(joint_marginals(q))
