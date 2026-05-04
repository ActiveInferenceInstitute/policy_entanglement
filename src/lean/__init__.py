"""Python mirrors of the Lean 4 boundary-fragment modules.
"""

from __future__ import annotations

from joint_dist import (  # noqa: F401
    is_mean_field,
    is_non_negative,
    is_pmf,
    joint_marginal,
    joint_marginals,
    m_projection,
    mean_field_to_joint,
    normalize,
)
from coupling import (  # noqa: F401
    coupling_log_weight,
    entangled_log_weight_affine_in_lambda,
    entangled_posterior,
    entangled_prior,
    entangled_prior_unnormalised,
    expected_value,
    trivial_coupling,
)
from free_energy import (  # noqa: F401
    free_energy,
    joint_entropy,
    kl_divergence,
    marginal_entropy,
    marginal_free_energy,
    shannon_entropy,
    total_correlation,
    total_correlation_via_kl,
)
from geometry import (  # noqa: F401
    coupling_log_weight_affine_check,
    coupling_pays_off,
    is_e_geodesic,
    is_in_mean_field_submanifold,
    m_projection_minimises_kl,
    pythagorean_residual,
    revertibility,
)
from spectral import (  # noqa: F401
    Archetype,
    archetype_marginal_pattern,
    entanglement_entropy,
    entanglement_spectrum,
    schmidt_decomposition,
    schmidt_rank,
    schmidt_rank_one_iff_mean_field,
    tensor_train_ranks,
)
from bernoulli_toy import (  # noqa: F401
    coupling_phase_at,
    empirical_mutual_information,
    is_mean_field_at_zero,
    ising_coupling,
    ising_free_energy_curve,
    ising_joint_posterior,
    ising_mutual_information,
    optimal_lambda,
    symmetric_mean_field_prior,
)
from heterogeneous import (  # noqa: F401
    InferenceMode,
    coupling_norm_sq,
    coupling_tax,
    coupling_tax_within_quadratic_bound,
    fixed_reflexive_posterior,
    is_heterogeneous,
    is_planning_stream,
    is_purely_planning,
    is_purely_reflexive,
    is_reflexive_stream,
    quadratic_bound_curvature,
)
from decomposition import (  # noqa: F401
    DecompositionTerms,
    coupling_cost_term,
    coupling_pays_for_itself,
    coupling_prior_term,
    decomposition_at_zero,
    entanglement_decomposition_rhs,
    free_energy_against_entangled_prior,
    sum_marginal_free_energies,
    total_correlation_gain,
)
