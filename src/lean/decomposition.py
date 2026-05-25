"""Theorem 5.1 — entanglement decomposition (numerical realization).

The load-bearing identity of the framework:

    F[q_λ] = Σ_k F[q^k_λ]  +  γλ⟨K_c⟩_{q_λ}  +  log Z_E(λ) - λ⟨J⟩_{q_λ}
            +  I(q_λ)

where ``I(q_λ) ≥ 0`` is total correlation.  ``entanglement_decomposition_rhs``
bundles the four RHS terms into a frozen ``DecompositionTerms`` record;
``free_energy_against_entangled_prior`` returns the LHS in the same
Gibbs form, so the identity is *numerically witnessable* at every
``(q, J, K_c, γ, λ)``.

Example::

    >>> import numpy as np
    >>> from lean.coupling import entangled_posterior
    >>> from lean.decomposition import (
    ...     entanglement_decomposition_rhs,
    ...     free_energy_against_entangled_prior,
    ... )
    >>> mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    >>> G  = [np.zeros(2), np.zeros(2)]
    >>> J  = np.array([[0.5, -0.5], [-0.5, 0.5]])
    >>> Kc = np.zeros((2, 2))
    >>> lam = 1.5
    >>> q   = entangled_posterior(mf, G, J, Kc, gamma=1.0, lam=lam)
    >>> lhs = free_energy_against_entangled_prior(q, mf, G, J, Kc, 1.0, lam)
    >>> rhs = entanglement_decomposition_rhs(q, mf, G, J, Kc, 1.0, lam).total
    >>> bool(np.isclose(lhs, rhs, atol=1e-10))
    True

Lean companion: ``ActinfPolicyEntanglement.Decomposition.entanglement_decomposition``
(boundary form with witness-consuming analytic content).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.special import logsumexp

from .coupling import expected_value
from .free_energy import (
    free_energy,
    marginal_free_energy,
    total_correlation,
)
from .joint_dist import mean_field_to_joint

ArrayF = NDArray[np.float64]


@dataclass(frozen=True)
class DecompositionTerms:
    """Components of the right-hand side of Theorem 5.1.

    Each field corresponds to a Lean definition under
    ``ActinfPolicyEntanglement.Decomposition``.
    """

    sum_marginal_free_energies: float
    coupling_cost_term: float
    coupling_prior_term: float
    total_correlation_gain: float

    @property
    def multi_information_term(self) -> float:
        """The multi-information :math:`I(q)` fourth term (**plus** sign in Gibbs form)."""

        return self.total_correlation_gain

    @property
    def total(self) -> float:
        return (
            self.sum_marginal_free_energies
            + self.coupling_cost_term
            + self.coupling_prior_term
            + self.total_correlation_gain
        )


def sum_marginal_free_energies(
    q: ArrayF,
    mf_prior: Sequence[ArrayF],
    per_stream_G: Sequence[ArrayF],
    gamma: float,
) -> float:
    """`∑_k F[q^k]`.  Mirrors ``sumMarginalFreeEnergies``."""
    qa = np.asarray(q, dtype=np.float64)
    return float(sum(marginal_free_energy(qa, mf_prior, per_stream_G, gamma, k) for k in range(qa.ndim)))


def coupling_cost_term(q: ArrayF, coupling_kc: ArrayF, gamma: float, lam: float) -> float:
    """`gamma · lam · E_q[K_c]`.  Mirrors ``couplingCostTerm``."""
    return gamma * lam * expected_value(q, coupling_kc)


def coupling_prior_term(q: ArrayF, coupling_j: ArrayF, mf_prior: Sequence[ArrayF], lam: float) -> float:
    """`log Z_E(λ) − λ · E_q[J]` where
    ``Z_E(λ) = ∑_pi (∏_k E_k(pi^k)) · exp(λ · J(π))``.

    This is the contribution of ``−E_q[log E_λ]`` *after* separating out
    ∑_k E_q^k[log E_k] into :func:`marginal_free_energy`, i.e. the
    ``+ log Z − λ E_q[J]`` piece of
    ``−E_q[∑ log E_k + λ J − log Z_E]``.

    Mirrors ``couplingPriorTerm``.
    """
    Ja = np.asarray(coupling_j, dtype=np.float64)
    base = mean_field_to_joint(mf_prior)
    # Numerically stable log-sum-exp avoids overflow at large |lam|.
    # `logsumexp(x, b=w)` computes log(sum(w * exp(x))) without ever
    # materialising exp on the hot path. The base weights are
    # non-negative (a PMF), so the `b=` weighting is well-defined.
    log_Z = float(logsumexp(lam * Ja, b=base))
    return log_Z - lam * expected_value(q, Ja)


def _marginals_efes_broadcast_to_joint(
    per_stream_G: Sequence[ArrayF],
    joint_shape: tuple[int, ...],
) -> ArrayF:
    """Pointwise \\(\\sum_k G_k(\\pi^k)\\) reshaped like the coupling tensor."""
    acc = np.zeros(joint_shape, dtype=np.float64)
    nd = len(joint_shape)
    for k, Gk in enumerate(per_stream_G):
        Ga = np.asarray(Gk, dtype=np.float64)
        if Ga.shape != (joint_shape[k],):
            raise ValueError(
                f"stream {k}: per_stream_G has shape {Ga.shape}; expected {(joint_shape[k],)} to match coupling tensor"
            )
        expand_shape = tuple(joint_shape[k] if axis == k else 1 for axis in range(nd))
        acc += Ga.reshape(expand_shape)
    return acc


def multi_information_term(q: ArrayF) -> float:
    """`I(q) = ∑_k H(q^k) − H(q)` (Theorem 5.1 fourth term).

    Preferred name when reading the Gibbs expansion; Lean still exposes the
    parallel ``totalCorrelationGain``.
    """

    return float(total_correlation(q))


def total_correlation_gain(q: ArrayF) -> float:
    """`I(q) = ∑_k H(q^k) − H(q)`.

    Mirrors ``totalCorrelationGain`` — synonym of :func:`multi_information_term`.

    Interpretive remarks in the manuscript still describe coupling benefits
    via paired inequalities involving ``−I`` in dual coordinates while the
    Gibbs bookkeeping writes ``+ I`` explicitly.
    """
    return multi_information_term(q)


def entanglement_decomposition_rhs(
    q: ArrayF,
    mf_prior: Sequence[ArrayF],
    per_stream_G: Sequence[ArrayF],
    coupling_j: ArrayF,
    coupling_kc: ArrayF,
    gamma: float,
    lam: float,
) -> DecompositionTerms:
    """Bundle the four RHS components of Theorem 5.1 into a
    :class:`DecompositionTerms` record."""
    return DecompositionTerms(
        sum_marginal_free_energies=sum_marginal_free_energies(q, mf_prior, per_stream_G, gamma),
        coupling_cost_term=coupling_cost_term(q, coupling_kc, gamma, lam),
        coupling_prior_term=coupling_prior_term(q, coupling_j, mf_prior, lam),
        total_correlation_gain=multi_information_term(q),
    )


def free_energy_against_entangled_prior(
    q: ArrayF,
    mf_prior: Sequence[ArrayF],
    per_stream_G: Sequence[ArrayF],
    coupling_j: ArrayF,
    coupling_kc: ArrayF,
    gamma: float,
    lam: float,
) -> float:
    r"""LHS :math:`F[q_\lambda]` in Theorem 5.1 (Gibbs form).

    Uses the manuscript convention
    :math:`G_\lambda(\pi)=\sum_k G_k(\pi^k)+\lambda K_c(\pi)` and the
    normalized entangled prior
    :math:`E_\lambda \propto (\prod_k E_k)\,\exp(\lambda J)`.

    :func:`~lean.free_energy.free_energy` computes
    ``gamma * E[G] − E[log prior] − H`` with this full :math:`G_\lambda`;
    splitting into stream / coupling-prior / :math:`I` parts is handled by
    :func:`entanglement_decomposition_rhs`.
    """
    base = mean_field_to_joint(mf_prior)
    Ja = np.asarray(coupling_j, dtype=np.float64)
    Kc_a = np.asarray(coupling_kc, dtype=np.float64)
    if Ja.shape != Kc_a.shape:
        raise ValueError("coupling_j and coupling_kc must share the joint shape")

    prior_unnorm = base * np.exp(lam * Ja)
    prior = prior_unnorm / float(np.sum(prior_unnorm))

    stream_part = _marginals_efes_broadcast_to_joint(per_stream_G, Ja.shape)
    g_lambda_joint = stream_part + lam * Kc_a

    return free_energy(q, prior, g_lambda_joint, gamma)


def decomposition_at_zero(
    q: ArrayF,
    mf_prior: Sequence[ArrayF],
    per_stream_G: Sequence[ArrayF],
    coupling_j: ArrayF,
    coupling_kc: ArrayF,
    gamma: float,
) -> DecompositionTerms:
    """**Corollary 5.3** numerical realization: at ``lambda = 0`` the
    coupling terms vanish and
    ``F[q] = sum_k F[q^k] + I(q)`` for the same bookkeeping split.
    Mirrors
    ``ActinfPolicyEntanglement.Decomposition.decomposition_at_zero``.

    Returns the four bookkeeping terms at ``lambda = 0``; the
    ``coupling_cost_term`` is identically zero (factor ``lambda``) and
    the ``coupling_prior_term`` reduces to ``log Z_E(0) = 0``.
    """
    return entanglement_decomposition_rhs(q, mf_prior, per_stream_G, coupling_j, coupling_kc, gamma, lam=0.0)


def coupling_pays_for_itself(q_lam: ArrayF, q_zero: ArrayF, atol: float = 1e-12) -> bool:
    """Coupling-pays-for-itself verdict: the lambda-entangled posterior
    has strictly higher total correlation than the lambda=0 baseline.

    Mirrors the ``CouplingVerdict.pays`` branch of the Lean
    ``couplingVerdict`` definition.
    """
    return total_correlation(q_lam) > total_correlation(q_zero) + atol
