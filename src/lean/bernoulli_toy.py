"""Closed-form K=2 Bernoulli / Ising worked example (manuscript §6.1).

The simplest non-trivial instance of the framework: two binary policy
streams with a symmetric Ising habit coupling
``J(π) = (2π¹-1)(2π²-1)``.  Every framework theorem has a closed-form
witness here that can be checked algebraically *and* numerically.

Key closed forms:

* ``ising_mutual_information(λ) = log 2 - H_b(σ(λ))`` — analytical MI
  of the K=2 joint, where ``σ`` is the logistic and ``H_b`` the binary
  entropy.  Saturates at ``log 2`` as ``|λ| → ∞``.
* ``optimal_lambda(Δ) = 2 · arctanh(Δ/Δ_max)`` — the coupling that
  realizes a target alignment surplus ``Δ`` ([[THMREF:thm_4_2]]).
* ``ising_free_energy_curve(λ, u) = -u·tanh(λ/2) - I(λ)`` — closed-form
  free-energy curve for the symmetric toy at utility surplus ``u``.

Example::

    >>> import numpy as np
    >>> from lean.bernoulli_toy import (
    ...     ising_mutual_information, optimal_lambda, ising_joint_posterior,
    ... )
    >>> round(ising_mutual_information(0.0), 6)
    0.0
    >>> round(ising_mutual_information(10.0), 4)  # near saturation log 2
    0.6926
    >>> round(optimal_lambda(0.5), 4)             # 2·arctanh(0.5)
    1.0986
    >>> q = ising_joint_posterior(2.0)
    >>> bool(np.allclose(q.sum(), 1.0))           # PMF
    True

Lean companion: ``ActinfPolicyEntanglement.BernoulliToy``.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .coupling import entangled_posterior
from .free_energy import total_correlation
from .joint_dist import is_mean_field
from .phase_constants import PHASE_LAMBDA_C1, PHASE_LAMBDA_C2

ArrayF = NDArray[np.float64]


def ising_coupling(shape: tuple[int, int] = (2, 2)) -> ArrayF:
    """Ising-style symmetric coupling: prefers aligned `(0,0)` or `(1,1)`,
    penalises misaligned.  Returns a (2, 2) ndarray with mean zero.

    Mirrors ``ActinfPolicyEntanglement.BernoulliToy.isingCoupling``.
    """
    if shape != (2, 2):
        raise ValueError("ising_coupling is only defined for shape (2, 2)")
    return np.array([[0.5, -0.5], [-0.5, 0.5]], dtype=np.float64)


def symmetric_mean_field_prior() -> tuple[ArrayF, ArrayF]:
    """Symmetric Bernoulli(1/2) marginals on each of the two streams."""
    return (np.array([0.5, 0.5]), np.array([0.5, 0.5]))


def ising_mutual_information(lam: float) -> float:
    """Closed-form mutual information of the K=2 symmetric Ising joint at
    coupling `lam` with the swing-1 coupling
    ``J(pi) = aligned_indicator(pi) - 1/2``:

        I(lam) = log 2 − H_b(sigma(lam))

    where ``sigma(lam) = 1/(1+exp(-lam))`` is the logistic function and
    ``H_b(p) = −p log p − (1-p) log(1-p)`` is the binary entropy.

    The function is even in `lam`, monotonically increasing in `|lam|`,
    saturates at ``log 2`` as ``|lam| → ∞``, and is zero at ``lam = 0``.

    Mirrors ``BernoulliToy.isingMutualInformation``.
    """
    lam = float(lam)
    # Numerically stable logistic.
    if lam >= 0:
        pa = 1.0 / (1.0 + np.exp(-lam))
    else:
        e = np.exp(lam)
        pa = e / (1.0 + e)
    # Binary entropy with safe logs.
    H_b = 0.0 if pa <= 0.0 or pa >= 1.0 else -pa * np.log(pa) - (1.0 - pa) * np.log(1.0 - pa)
    return float(np.log(2.0) - H_b)


def ising_joint_posterior(lam: float) -> ArrayF:
    """The (un-utility) lambda-entangled joint over the K=2 Ising toy with
    symmetric Bernoulli(1/2) priors and zero per-stream EFE.
    """
    mf = list(symmetric_mean_field_prior())
    Kc = np.zeros((2, 2), dtype=np.float64)
    return entangled_posterior(
        mf_prior=mf,
        per_stream_G=[np.zeros(2, dtype=np.float64), np.zeros(2, dtype=np.float64)],
        coupling_j=ising_coupling(),
        coupling_kc=Kc,
        gamma=0.0,
        lam=lam,
    )


def empirical_mutual_information(lam: float) -> float:
    """Numeric total correlation of the *closed-form* K=2 Ising joint.

    **This is NOT a Monte-Carlo sampler.** It evaluates the audited
    :func:`~lean.free_energy.total_correlation` on the exact analytic
    joint :func:`ising_joint_posterior`, so agreement with
    :func:`ising_mutual_information` (to ``BERNOULLI_VERIFICATION_TOLERANCE``)
    is an *internal analytic-consistency* check: two algebraically
    independent closed forms for the same quantity must coincide to
    numerical precision.  For the genuine finite-sample empirical witness
    (a seeded multinomial estimator with a sampling-error bound) see
    :func:`empirical_mutual_information_montecarlo`.
    """
    return total_correlation(ising_joint_posterior(lam))


def empirical_mutual_information_montecarlo(lam: float, n_samples: int, seed: int) -> float:
    """Genuine finite-N Monte-Carlo estimate of the K=2 Ising total
    correlation.

    Draws ``n_samples`` i.i.d. categorical samples from the four-atom
    distribution ``ising_joint_posterior(lam)`` using a seeded
    ``numpy.random.default_rng`` generator, forms the empirical 2x2 joint
    (counts / N), and returns the audited
    :func:`~lean.free_energy.total_correlation` of that *empirical*
    joint.  Unlike :func:`empirical_mutual_information` this is a real
    stochastic estimator: the estimate is a random variable whose bias is
    ``O(1/N)`` (plug-in entropy bias) and whose standard deviation is
    ``O(1/sqrt(N))``, so it converges to
    :func:`ising_mutual_information` only in the finite-sample sense, not
    to floating-point tolerance.  Deterministic given ``(lam, n_samples,
    seed)``.

    The empirical-agreement claim in the manuscript is witnessed by this
    function (and ``tests/test_bernoulli_toy.py``'s convergence /
    concentration tests), not by :func:`empirical_mutual_information`.
    """
    if n_samples <= 0:
        raise ValueError("n_samples must be positive")
    joint = np.asarray(ising_joint_posterior(lam), dtype=np.float64)
    flat = joint.reshape(-1)
    flat = flat / flat.sum()
    rng = np.random.default_rng(seed)
    draws = rng.choice(flat.size, size=int(n_samples), p=flat)
    counts = np.bincount(draws, minlength=flat.size).astype(np.float64)
    empirical_joint = (counts / float(n_samples)).reshape(joint.shape)
    return total_correlation(empirical_joint)


def optimal_lambda(delta: float, delta_max: float = 1.0) -> float:
    """`lam* = 2 · arctanh(delta / delta_max)` — the coupling that
    *realizes* a target expected alignment ``delta``.

    Concretely: under the symmetric K=2 Ising joint, the expected
    alignment is ``alpha(lam) = tanh(lam/2)``; inverting gives
    ``lam* = 2 · arctanh(alpha)``.  ``delta`` here is interpreted as the
    target alignment value, not a utility.  Saturates at ``inf`` when
    ``delta -> delta_max`` and at 0 when ``delta = 0``.

    See the appendix on the K=2 Bernoulli derivation in the manuscript
    for the full alignment–coupling correspondence.  Mirrors
    ``BernoulliToy.optimalLambda``.
    """
    if delta_max <= 0.0:
        raise ValueError("delta_max must be positive")
    ratio = float(delta) / float(delta_max)
    if abs(ratio) >= 1.0:
        return float("inf") if ratio > 0 else float("-inf")
    return float(2.0 * np.arctanh(ratio))


def ising_free_energy_curve(lam: float, utility: float) -> float:
    """`F(lam) = -utility · alignment(lam) − I(lam)`.

    The closed-form free-energy curve for the K=2 Ising toy with a
    single utility scalar — *utility* is the surplus an aligned outcome
    delivers, and ``alignment(lam) = 2σ(lam) − 1 = tanh(lam/2)`` is the
    signed expected alignment under the lambda-entangled posterior.

    * For ``lam > 0``: alignment is positive; F decreases (coupling pays).
    * For ``lam < 0``: alignment is negative (coupling *penalises*
      alignment); F increases, reflecting anti-alignment coupling.
    * For ``utility ≥ 0`` and ``lam ≥ 0``: F is monotonically decreasing
      in lam (both summands non-positive).

    Mirrors ``BernoulliToy.isingFreeEnergyCurve``.
    """
    lam_f = float(lam)
    # Numerically stable logistic for the signed alignment tanh(lam/2).
    if lam_f >= 0.0:
        sigma = 1.0 / (1.0 + np.exp(-lam_f))
    else:
        e = np.exp(lam_f)
        sigma = e / (1.0 + e)
    alignment = 2.0 * sigma - 1.0
    return float(-float(utility) * alignment - ising_mutual_information(lam_f))


def coupling_phase_at(
    lam: float,
    lam_c1: float | None = None,
    lam_c2: float | None = None,
) -> str:
    """Determine the coupling phase from `lam` and two critical couplings.

    Returns one of ``"disordered"``, ``"mixed"``, ``"frozen"`` —
    matches the Lean ``CouplingPhase`` inductive.

    The critical couplings default to the centralized hyperparameter
    constants ``PHASE_LAMBDA_C1`` and ``PHASE_LAMBDA_C2`` (in
    :mod:`lean.phase_constants`) rather than to inline magic
    numbers (RedTeam Methods C2 / M3, 2026-05-20).  Both constants are
    illustrative (they make the K=2 phase boundaries non-degenerate);
    real values are model-dependent.  Callers that need the inline
    defaults preserved should pass them explicitly.
    """
    if lam_c1 is None:
        lam_c1 = float(PHASE_LAMBDA_C1)
    if lam_c2 is None:
        lam_c2 = float(PHASE_LAMBDA_C2)
    if lam < lam_c1:
        return "disordered"
    if lam <= lam_c2:
        return "mixed"
    return "frozen"


def is_mean_field_at_zero(atol: float = 1e-9) -> bool:
    """Sanity check: the lambda=0 Ising joint is mean-field."""
    return is_mean_field(ising_joint_posterior(0.0), atol=atol)
