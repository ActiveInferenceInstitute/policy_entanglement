"""Theorem 4.1 — entanglement decomposition (numerical realisation).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from coupling import expected_value
from free_energy import (
    free_energy,
    marginal_free_energy,
    total_correlation,
)
from joint_dist import joint_marginal, mean_field_to_joint

ArrayF = NDArray[np.float64]


@dataclass(frozen=True)
class DecompositionTerms:
    """Components of the right-hand side of Theorem 4.1.

    Each field corresponds to a Lean definition under
    ``ActinfPolicyEntanglement.Decomposition``.
    """
    sum_marginal_free_energies: float
    coupling_cost_term: float
    coupling_prior_term: float
    total_correlation_gain: float

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
    return float(
        sum(
            marginal_free_energy(q, mf_prior, per_stream_G, gamma, k)
            for k in range(np.asarray(q).ndim)
        )
    )


def coupling_cost_term(
    q: ArrayF, coupling_Kc: ArrayF, gamma: float, lam: float
) -> float:
    """`gamma · lam · E_q[K_c]`.  Mirrors ``couplingCostTerm``."""
    return gamma * lam * expected_value(q, coupling_Kc)


def coupling_prior_term(
    q: ArrayF, coupling_J: ArrayF, mf_prior: Sequence[ArrayF], lam: float
) -> float:
    """`lam · E_q[J] − log Z_E(lam)` where
    ``Z_E(lam) = ∑_pi (∏_k E_k(pi^k)) · exp(lam · J(pi))``.

    Mirrors ``couplingPriorTerm``.
    """
    Ja = np.asarray(coupling_J, dtype=np.float64)
    base = mean_field_to_joint(mf_prior)
    log_Z = float(np.log(np.sum(base * np.exp(lam * Ja))))
    return lam * expected_value(q, Ja) - log_Z


def total_correlation_gain(q: ArrayF) -> float:
    """`−I(q)`.  Mirrors ``totalCorrelationGain``."""
    return float(-total_correlation(q))


def entanglement_decomposition_rhs(
    q: ArrayF,
    mf_prior: Sequence[ArrayF],
    per_stream_G: Sequence[ArrayF],
    coupling_J: ArrayF,
    coupling_Kc: ArrayF,
    gamma: float,
    lam: float,
) -> DecompositionTerms:
    """Bundle the four RHS components of Theorem 4.1 into a
    :class:`DecompositionTerms` record."""
    return DecompositionTerms(
        sum_marginal_free_energies=sum_marginal_free_energies(
            q, mf_prior, per_stream_G, gamma
        ),
        coupling_cost_term=coupling_cost_term(q, coupling_Kc, gamma, lam),
        coupling_prior_term=coupling_prior_term(q, coupling_J, mf_prior, lam),
        total_correlation_gain=total_correlation_gain(q),
    )


def free_energy_against_entangled_prior(
    q: ArrayF,
    mf_prior: Sequence[ArrayF],
    coupling_J: ArrayF,
    coupling_Kc: ArrayF,
    gamma: float,
    lam: float,
) -> float:
    """`F[q]` against the lambda-entangled prior, using
    `G_lam(pi) = gamma · lam · K_c(pi)` as the EFE component.  This is
    the LHS of Theorem 4.1 (matching the Lean statement).
    """
    base = mean_field_to_joint(mf_prior)
    Ja = np.asarray(coupling_J, dtype=np.float64)
    prior_unnorm = base * np.exp(lam * Ja)
    Z = float(np.sum(prior_unnorm))
    prior = prior_unnorm / Z
    G_lam = gamma * lam * np.asarray(coupling_Kc, dtype=np.float64)
    # The LHS of the manuscript identity uses gamma=1 inside free_energy
    # because gamma has already been absorbed into G_lam.
    return free_energy(q, prior, G_lam, gamma=1.0)


def decomposition_at_zero(
    q: ArrayF,
    mf_prior: Sequence[ArrayF],
    per_stream_G: Sequence[ArrayF],
    coupling_J: ArrayF,
    coupling_Kc: ArrayF,
    gamma: float,
) -> DecompositionTerms:
    """**Corollary 4.3** numerical realisation: at ``lambda = 0`` the
    decomposition collapses to the pure sum-of-marginals form
    ``F[q] = sum_k F[q^k] - I(q)``.  Mirrors
    ``ActinfPolicyEntanglement.Decomposition.decomposition_at_zero``.

    Returns the four bookkeeping terms at ``lambda = 0``; the
    ``coupling_cost_term`` is identically zero (factor ``lambda``) and
    the ``coupling_prior_term`` reduces to ``- log Z_E(0) = 0``.
    """
    return entanglement_decomposition_rhs(
        q, mf_prior, per_stream_G, coupling_J, coupling_Kc, gamma, lam=0.0
    )


def coupling_pays_for_itself(
    q_lam: ArrayF, q_zero: ArrayF, atol: float = 1e-12
) -> bool:
    """Coupling-pays-for-itself verdict: the lambda-entangled posterior
    has strictly higher total correlation than the lambda=0 baseline.

    Mirrors the ``CouplingVerdict.pays`` branch of the Lean
    ``couplingVerdict`` definition.
    """
    return total_correlation(q_lam) > total_correlation(q_zero) + atol
