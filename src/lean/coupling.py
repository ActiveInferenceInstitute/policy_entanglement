"""Coupling potentials and the lambda-entangled prior / posterior.

The central object of the framework lives here: ``entangled_posterior``
takes a per-stream mean-field prior, per-stream EFE, two coupling
potentials (habit ``J`` and preference ``K_c``), the EFE precision
``gamma``, and the coupling strength ``lam``, and returns the joint
policy posterior.  At ``lam = 0`` the result is the outer product of
the marginals (mean-field manifold); for large ``lam`` it concentrates
on the maximizers of ``J - gamma * K_c`` (archetypal joints).

Example::

    >>> import numpy as np
    >>> from lean.coupling import entangled_posterior
    >>> from lean.free_energy import total_correlation
    >>> mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    >>> G  = [np.zeros(2), np.zeros(2)]
    >>> J  = np.array([[1.0, -1.0], [-1.0, 1.0]])
    >>> Kc = np.zeros((2, 2))
    >>> q0 = entangled_posterior(mf, G, J, Kc, gamma=1.0, lam=0.0)
    >>> bool(np.allclose(q0, np.outer(mf[0], mf[1])))  # mean field at λ=0
    True
    >>> q4 = entangled_posterior(mf, G, J, Kc, gamma=1.0, lam=4.0)
    >>> round(total_correlation(q4), 3)  # near log 2 ≈ 0.693
    0.69

Lean companion: ``ActinfPolicyEntanglement.Coupling`` (boundary form).
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray
from scipy.special import logsumexp

ArrayF = NDArray[np.float64]


def trivial_coupling(shape: Sequence[int]) -> ArrayF:
    """Return the zero coupling potential of the given joint shape."""
    return np.zeros(tuple(shape), dtype=np.float64)


def _entangled_prior_log_weights(
    mf_prior: Sequence[ArrayF], coupling_j: ArrayF, lam: float
) -> ArrayF:
    """Combine the mean-field log mass and habit potential before exponentiation."""
    if not mf_prior:
        raise ValueError("mean_field_to_joint requires at least one stream")
    with np.errstate(divide="ignore"):
        log_base = np.log(np.asarray(mf_prior[0], dtype=np.float64))
        for marginal in mf_prior[1:]:
            log_base = np.add.outer(log_base, np.log(np.asarray(marginal, dtype=np.float64)))
    Ja = np.asarray(coupling_j, dtype=np.float64)
    if log_base.shape != Ja.shape:
        raise ValueError(f"coupling shape {Ja.shape} != mean-field shape {log_base.shape}")
    return log_base + lam * Ja


def _normalize_log_weights(log_weights: ArrayF) -> ArrayF:
    log_z = float(logsumexp(log_weights))
    if log_z == -np.inf:
        raise ValueError("cannot normalize a non-positive mass: total=0.0")
    return np.asarray(np.exp(log_weights - log_z), dtype=np.float64)


def entangled_prior_unnormalised(
    mf_prior: Sequence[ArrayF],
    coupling_j: ArrayF,
    lam: float,
) -> ArrayF:
    """`E_lam(pi) ∝ (∏_k E_k(pi^k)) · exp(lam · J(pi))` (unnormalized).

    The unnormalized mass can overflow when its true value is outside
    float64 range. Normalized prior/posterior callers stay in log space.
    """
    return np.exp(_entangled_prior_log_weights(mf_prior, coupling_j, lam))


def entangled_prior(
    mf_prior: Sequence[ArrayF],
    coupling_j: ArrayF,
    lam: float,
) -> ArrayF:
    """Normalized lambda-entangled prior, as a proper joint PMF tensor."""
    return _normalize_log_weights(_entangled_prior_log_weights(mf_prior, coupling_j, lam))


def entangled_posterior(
    mf_prior: Sequence[ArrayF],
    per_stream_G: Sequence[ArrayF],
    coupling_j: ArrayF,
    coupling_kc: ArrayF,
    gamma: float,
    lam: float,
    *,
    strict_positive_marginals: bool = False,
) -> ArrayF:
    """`q_lam(pi) ∝ E_lam(pi) · exp(-gamma · (∑_k G_k(pi^k) + lam · K_c(pi)))`.

    Returns the normalized joint posterior tensor.

    Mirrors ``ActinfPolicyEntanglement.entangledPosteriorLogWeight``.

    **Positivity precondition (RedTeam Methods H5 / B3, 2026-05-20).**
    The MathlibProofs ℝ keystone `free_energy_decomposition_full`
    requires *strict positivity* of every per-stream marginal
    (`hEkpos : ∀ k a, 0 < Ek k a`).  Production simulations use full-
    rank `D, C` preferences so this is satisfied trivially; degenerate
    edge cases (one-hot preferences, near-zero D entries) silently
    slip through because downstream `total_correlation` masks zeros.
    Pass ``strict_positive_marginals=True`` to assert the precondition
    explicitly and raise ``ValueError`` on violation — recommended for
    research code that might explore degenerate boundaries.  Default
    is ``False`` for backward compatibility with the production
    pipeline which never sees degenerate inputs.
    """
    if strict_positive_marginals:
        for k, m in enumerate(mf_prior):
            ma = np.asarray(m, dtype=np.float64)
            mn = float(ma.min())
            if mn <= 0.0:
                raise ValueError(
                    f"entangled_posterior: per-stream marginal {k} has min "
                    f"entry {mn} ≤ 0 but strict_positive_marginals=True. "
                    f"The MathlibProofs ℝ keystone requires `0 < Ek k a` "
                    f"for every per-stream marginal entry; degenerate "
                    f"boundaries fall outside the discharged ℝ theorem."
                )
    Ja = np.asarray(coupling_j, dtype=np.float64)
    Kc = np.asarray(coupling_kc, dtype=np.float64)
    if Kc.shape != Ja.shape:
        raise ValueError(f"coupling K_c shape {Kc.shape} != joint shape {Ja.shape}")
    log_weights = _entangled_prior_log_weights(mf_prior, Ja - gamma * Kc, lam)
    if len(per_stream_G) != log_weights.ndim:
        raise ValueError("per_stream_G must contain one vector per stream")
    for k, G_k in enumerate(per_stream_G):
        Ga = np.asarray(G_k, dtype=np.float64)
        if Ga.shape != (log_weights.shape[k],):
            raise ValueError(f"stream {k}: EFE shape {Ga.shape} != {(log_weights.shape[k],)}")
        shape = tuple(log_weights.shape[k] if axis == k else 1 for axis in range(log_weights.ndim))
        log_weights -= gamma * Ga.reshape(shape)
    return _normalize_log_weights(log_weights)


def expected_value(q: ArrayF, f: ArrayF) -> float:
    """`E_q[f] = ∑_pi q(pi) · f(pi)`."""
    qa = np.asarray(q, dtype=np.float64)
    fa = np.asarray(f, dtype=np.float64)
    if qa.shape != fa.shape:
        raise ValueError(f"expected_value shape mismatch: q={qa.shape}, f={fa.shape}")
    return float(np.sum(qa * fa))


def entangled_log_weight_affine_in_lambda(
    coupling_j: ArrayF, coupling_kc: ArrayF, gamma: float, pi_index: tuple[int, ...]
) -> tuple[float, float]:
    """Return ``(a, b)`` so that `log E_lam · exp(-gamma·lam·K_c) (pi_index) = a + b · lam`.

    `a` is the lam-independent coefficient (zero in the canonical form
    used in the Lean boundary), `b` is the slope ``J(pi) − gamma · K_c(pi)``.
    The structural lemma underlying Theorem 7.4 (e-geodesic).
    """
    Ja = np.asarray(coupling_j, dtype=np.float64)
    Kc = np.asarray(coupling_kc, dtype=np.float64)
    a = 0.0
    b = float(Ja[pi_index] - gamma * Kc[pi_index])
    return a, b


def coupling_log_weight(coupling_j: ArrayF, coupling_kc: ArrayF, gamma: float, lam: float) -> ArrayF:
    r"""Pointwise unnormalized log-weight: ``lam · J − gamma · lam · K_c``.

    This is the *bare* coupling contribution without the mean-field base or
    the normalization constant ``log Z_E(λ)``.  The full log-weight of the
    λ-entangled prior for a given joint policy π is::

        log E_λ(π) = Σ_k log E_k(π^k) + lam · J(π) − γ · lam · K_c(π) − log Z_E(λ)

    This function returns only the ``lam · J − γ · lam · K_c`` piece,
    which is used by the geometry and decomposition modules to test the
    affine-in-λ property numerically.
    """
    Ja = np.asarray(coupling_j, dtype=np.float64)
    Kc = np.asarray(coupling_kc, dtype=np.float64)
    if Ja.shape != Kc.shape:
        raise ValueError("J and K_c must have identical shapes")
    return lam * (Ja - gamma * Kc)
