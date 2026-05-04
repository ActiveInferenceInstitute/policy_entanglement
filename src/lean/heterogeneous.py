"""Heterogeneous VFE/EFE ensembles and the O(lambda^2) coupling tax.
"""

from __future__ import annotations

from collections.abc import Sequence
from enum import Enum

import numpy as np
from numpy.typing import NDArray

from coupling import entangled_posterior
from free_energy import free_energy, kl_divergence
from joint_dist import joint_marginal, joint_marginals, mean_field_to_joint

ArrayF = NDArray[np.float64]


class InferenceMode(Enum):
    """Mirror of the Lean ``InferenceMode`` inductive."""
    VFE = "vfe"
    EFE = "efe"
    SOPHISTICATED = "sophisticated"


def is_planning_stream(mode: InferenceMode) -> bool:
    return mode in (InferenceMode.EFE, InferenceMode.SOPHISTICATED)


def is_reflexive_stream(mode: InferenceMode) -> bool:
    return mode is InferenceMode.VFE


def is_purely_reflexive(modes: Sequence[InferenceMode]) -> bool:
    return all(is_reflexive_stream(m) for m in modes)


def is_purely_planning(modes: Sequence[InferenceMode]) -> bool:
    return all(is_planning_stream(m) for m in modes)


def is_heterogeneous(modes: Sequence[InferenceMode]) -> bool:
    return any(is_reflexive_stream(m) for m in modes) and any(
        is_planning_stream(m) for m in modes
    )


def coupling_norm_sq(coupling_Kc: ArrayF) -> float:
    """`‖K_c‖² = ∑_pi K_c(pi)²`.  Mirrors ``couplingNormSq``."""
    Kc = np.asarray(coupling_Kc, dtype=np.float64)
    return float(np.sum(Kc * Kc))


def fixed_reflexive_posterior(
    mf_prior: Sequence[ArrayF],
    per_stream_G: Sequence[ArrayF],
    coupling_J: ArrayF,
    coupling_Kc: ArrayF,
    gamma: float,
    lam: float,
    modes: Sequence[InferenceMode],
) -> ArrayF:
    """Construct the joint that holds VFE streams at their lam=0
    marginals while EFE streams adapt to the lambda-entangled posterior.

    For each VFE stream we use the lam=0 marginal; for each EFE stream
    we use the marginal of the entangled posterior at the supplied
    `lam`.  The returned joint is the outer product (independent across
    streams) of these per-stream marginals.
    """
    K = len(modes)
    if K == 0:
        raise ValueError("modes must be non-empty")
    q_zero = entangled_posterior(
        mf_prior, per_stream_G, coupling_J, coupling_Kc, gamma, 0.0
    )
    q_lam = entangled_posterior(
        mf_prior, per_stream_G, coupling_J, coupling_Kc, gamma, lam
    )
    used_marginals: list[ArrayF] = []
    for k, mode in enumerate(modes):
        if is_reflexive_stream(mode):
            used_marginals.append(joint_marginal(q_zero, k))
        else:
            used_marginals.append(joint_marginal(q_lam, k))
    return mean_field_to_joint(used_marginals)


def coupling_tax(
    mf_prior: Sequence[ArrayF],
    per_stream_G: Sequence[ArrayF],
    coupling_J: ArrayF,
    coupling_Kc: ArrayF,
    gamma: float,
    lam: float,
    modes: Sequence[InferenceMode],
) -> float:
    """Numerical coupling tax: ``KL(q_full ‖ q_pinned)`` where
    ``q_full = q_lam`` is the fully-adaptive entangled posterior and
    ``q_pinned`` holds VFE streams at their lam=0 marginals.

    Mirrors ``ActinfPolicyEntanglement.couplingTax``.  Always
    non-negative; equal to 0 for purely reflexive or purely planning
    ensembles.
    """
    if is_purely_reflexive(modes) or is_purely_planning(modes):
        return 0.0
    q_full = entangled_posterior(
        mf_prior, per_stream_G, coupling_J, coupling_Kc, gamma, lam
    )
    q_pinned = fixed_reflexive_posterior(
        mf_prior, per_stream_G, coupling_J, coupling_Kc, gamma, lam, modes
    )
    return kl_divergence(q_full, q_pinned)


def quadratic_bound_curvature(
    mf_prior: Sequence[ArrayF],
    per_stream_G: Sequence[ArrayF],
    coupling_J: ArrayF,
    coupling_Kc: ArrayF,
    gamma: float,
    modes: Sequence[InferenceMode],
    lam_probe: float = 1e-2,
) -> float:
    """Estimate the structural curvature constant ``C`` such that

        couplingTax(lam) ≤ C · lam² · ‖K_c‖²

    by running the coupling tax at a small probe `lam_probe` and
    dividing by ``lam_probe² · ‖K_c‖²``.  Returns 0.0 when the coupling
    norm is 0 or the ensemble is non-heterogeneous.

    The estimate is then used by :func:`coupling_tax_within_quadratic_bound`.
    """
    if not is_heterogeneous(modes):
        return 0.0
    norm_sq = coupling_norm_sq(coupling_Kc)
    if norm_sq <= 0.0:
        return 0.0
    if abs(lam_probe) <= 0.0:
        raise ValueError("lam_probe must be non-zero")
    tax = coupling_tax(
        mf_prior, per_stream_G, coupling_J, coupling_Kc, gamma, lam_probe, modes
    )
    return float(tax / (lam_probe * lam_probe * norm_sq))


def coupling_tax_within_quadratic_bound(
    mf_prior: Sequence[ArrayF],
    per_stream_G: Sequence[ArrayF],
    coupling_J: ArrayF,
    coupling_Kc: ArrayF,
    gamma: float,
    lam: float,
    modes: Sequence[InferenceMode],
    safety_factor: float = 4.0,
    lam_probe: float = 1e-2,
) -> bool:
    """Verify Theorem 8.1 numerically at the given `lam`: the coupling tax
    is within ``safety_factor · C · lam² · ‖K_c‖²`` for the curvature `C`
    estimated at `lam_probe`.  The factor relaxes the bound to absorb
    higher-order corrections at non-tiny `lam`.
    """
    norm_sq = coupling_norm_sq(coupling_Kc)
    C = quadratic_bound_curvature(
        mf_prior, per_stream_G, coupling_J, coupling_Kc, gamma, modes, lam_probe
    )
    actual = coupling_tax(
        mf_prior, per_stream_G, coupling_J, coupling_Kc, gamma, lam, modes
    )
    bound = safety_factor * C * lam * lam * norm_sq
    return bool(actual <= bound + 1e-12)
