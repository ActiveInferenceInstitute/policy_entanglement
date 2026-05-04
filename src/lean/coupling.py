"""Coupling potentials and the lambda-entangled prior / posterior.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
from numpy.typing import NDArray

from joint_dist import mean_field_to_joint, normalize

ArrayF = NDArray[np.float64]


def trivial_coupling(shape: Sequence[int]) -> ArrayF:
    """Return the zero coupling potential of the given joint shape."""
    return np.zeros(tuple(shape), dtype=np.float64)


def entangled_prior_unnormalised(
    mf_prior: Sequence[ArrayF],
    coupling_J: ArrayF,
    lam: float,
) -> ArrayF:
    """`E_lam(pi) ∝ (∏_k E_k(pi^k)) · exp(lam · J(pi))` (unnormalised).

    Mirrors ``ActinfPolicyEntanglement.entangledPriorLogWeight`` (in
    log-space), exponentiated and multiplied through the mean-field
    base.  Returns the un-normalised mass tensor.
    """
    base = mean_field_to_joint(mf_prior)
    Ja = np.asarray(coupling_J, dtype=np.float64)
    if base.shape != Ja.shape:
        raise ValueError(
            f"coupling shape {Ja.shape} != mean-field shape {base.shape}"
        )
    return base * np.exp(lam * Ja)


def entangled_prior(
    mf_prior: Sequence[ArrayF],
    coupling_J: ArrayF,
    lam: float,
) -> ArrayF:
    """Normalised lambda-entangled prior, as a proper joint PMF tensor."""
    return normalize(entangled_prior_unnormalised(mf_prior, coupling_J, lam))


def entangled_posterior(
    mf_prior: Sequence[ArrayF],
    per_stream_G: Sequence[ArrayF],
    coupling_J: ArrayF,
    coupling_Kc: ArrayF,
    gamma: float,
    lam: float,
) -> ArrayF:
    """`q_lam(pi) ∝ E_lam(pi) · exp(-gamma · (∑_k G_k(pi^k) + lam · K_c(pi)))`.

    Returns the normalised joint posterior tensor.

    Mirrors ``ActinfPolicyEntanglement.entangledPosteriorLogWeight``.
    """
    prior_unn = entangled_prior_unnormalised(mf_prior, coupling_J, lam)
    G_total = mean_field_to_joint(
        [np.exp(-gamma * np.asarray(g, dtype=np.float64)) for g in per_stream_G]
    )
    Kc = np.asarray(coupling_Kc, dtype=np.float64)
    if Kc.shape != prior_unn.shape:
        raise ValueError(
            f"coupling K_c shape {Kc.shape} != joint shape {prior_unn.shape}"
        )
    return normalize(prior_unn * G_total * np.exp(-gamma * lam * Kc))


def expected_value(q: ArrayF, f: ArrayF) -> float:
    """`E_q[f] = ∑_pi q(pi) · f(pi)`."""
    qa = np.asarray(q, dtype=np.float64)
    fa = np.asarray(f, dtype=np.float64)
    if qa.shape != fa.shape:
        raise ValueError(
            f"expected_value shape mismatch: q={qa.shape}, f={fa.shape}"
        )
    return float(np.sum(qa * fa))


def entangled_log_weight_affine_in_lambda(
    coupling_J: ArrayF, coupling_Kc: ArrayF, gamma: float, pi_index: tuple[int, ...]
) -> tuple[float, float]:
    """Return ``(a, b)`` so that `log E_lam · exp(-gamma·lam·K_c) (pi_index) = a + b · lam`.

    `a` is the lam-independent coefficient (zero in the canonical form
    used in the Lean boundary), `b` is the slope ``J(pi) − gamma · K_c(pi)``.
    The structural lemma underlying Theorem 6.4 (e-geodesic).
    """
    Ja = np.asarray(coupling_J, dtype=np.float64)
    Kc = np.asarray(coupling_Kc, dtype=np.float64)
    a = 0.0
    b = float(Ja[pi_index] - gamma * Kc[pi_index])
    return a, b


def coupling_log_weight(
    coupling_J: ArrayF, coupling_Kc: ArrayF, gamma: float, lam: float
) -> ArrayF:
    """Pointwise log-weight: ``lam · J − gamma · lam · K_c`` (no MF base).

    Used by the geometry / decomposition modules to test the affine-in-λ
    property numerically.
    """
    Ja = np.asarray(coupling_J, dtype=np.float64)
    Kc = np.asarray(coupling_Kc, dtype=np.float64)
    if Ja.shape != Kc.shape:
        raise ValueError("J and K_c must have identical shapes")
    return lam * Ja - gamma * lam * Kc
