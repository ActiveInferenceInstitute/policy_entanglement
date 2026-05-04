"""Closed-form K=2 Bernoulli / Ising worked example (manuscript §5.1).
"""

from __future__ import annotations

from typing import cast

import numpy as np
from numpy.typing import NDArray

from coupling import entangled_posterior, expected_value
from free_energy import free_energy, total_correlation
from joint_dist import is_mean_field, mean_field_to_joint

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
    if pa <= 0.0 or pa >= 1.0:
        H_b = 0.0
    else:
        H_b = -pa * np.log(pa) - (1.0 - pa) * np.log(1.0 - pa)
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
        coupling_J=ising_coupling(),
        coupling_Kc=Kc,
        gamma=0.0,
        lam=lam,
    )


def empirical_mutual_information(lam: float) -> float:
    """Total correlation of the K=2 Ising joint posterior — should match
    :func:`ising_mutual_information` to floating tolerance.
    """
    return total_correlation(ising_joint_posterior(lam))


def optimal_lambda(delta: float, delta_max: float = 1.0) -> float:
    """`lam* = 2 · arctanh(delta / delta_max)` — the coupling that
    *realises* a target expected alignment ``delta``.

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
    """`F(lam) = -utility · alignment_prob(lam) − I(lam)`.

    The closed-form free-energy curve for the K=2 Ising toy with a
    single utility scalar — *utility* is the surplus an aligned outcome
    delivers, and ``alignment_prob(lam) = 2 sigma(lam) − 1`` is the
    expected alignment under the lambda-entangled posterior.

    Both summands are non-positive (utility · alignment_prob ≥ 0; MI ≥
    0), so `F` is monotonically decreasing in `|lam|` whenever
    ``utility ≥ 0``.  Mirrors ``BernoulliToy.isingFreeEnergyCurve``.
    """
    alignment = 2.0 / (1.0 + np.exp(-abs(float(lam)))) - 1.0
    return float(-utility * alignment - ising_mutual_information(lam))


def coupling_phase_at(
    lam: float,
    lam_c1: float = 0.5,
    lam_c2: float = 2.5,
) -> str:
    """Determine the coupling phase from `lam` and two critical couplings.

    Returns one of ``"disordered"``, ``"mixed"``, ``"frozen"`` —
    matches the Lean ``CouplingPhase`` inductive.  The default critical
    couplings ``(0.5, 2.5)`` are illustrative (they make the K=2 phase
    boundaries non-degenerate); real values are model-dependent.
    """
    if lam < lam_c1:
        return "disordered"
    if lam <= lam_c2:
        return "mixed"
    return "frozen"


def is_mean_field_at_zero(atol: float = 1e-9) -> bool:
    """Sanity check: the lambda=0 Ising joint is mean-field."""
    return is_mean_field(ising_joint_posterior(0.0), atol=atol)
