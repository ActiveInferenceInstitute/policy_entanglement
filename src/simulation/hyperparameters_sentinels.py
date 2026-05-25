"""Sentinel λ values, Monte Carlo witness knobs, and pymdp tolerances."""

from __future__ import annotations

#: λ values at which closed-form Ising MI is reported in §6.1 / §13.
ISING_MI_SENTINEL_LAMBDAS: tuple[float, ...] = (0.5, 1.0, 2.0)

#: Saturating λ used to print the asymptote (≈ log 2).
ISING_MI_SATURATION_LAMBDA: float = 50.0

#: $\Delta_{\mathrm{util}}$ values at which $\lambda^\star$ is reported.
OPTIMAL_LAMBDA_SENTINEL_DELTAS: tuple[float, ...] = (0.5, 0.9)

#: λ values at which Schmidt entropy / rank are reported.
SPECTRAL_SENTINEL_LAMBDAS: tuple[float, ...] = (0.0, 1.0, 3.0)

#: λ values at which the Ising alignment $\tanh(\lambda/2)$ is reported.
ISING_ALIGNMENT_SENTINEL_LAMBDAS: tuple[float, ...] = (0.5, 1.0, 2.0, 3.0)

#: λ values at which the motor+attention aligned-probability is reported.
MOTOR_ATTENTION_SENTINEL_LAMBDAS: tuple[float, ...] = (0.0, 1.0, 2.0)

#: K values across which the TT rank profile is enumerated.
TT_RANK_STREAM_COUNTS: tuple[int, ...] = (2, 3, 4, 5)

#: λ at which the tensor-train rank profile is reported.
TT_RANK_PROFILE_LAMBDA: float = 2.0

#: Absolute tolerance used for Schmidt / tensor-train numerical ranks.
SPECTRAL_RANK_ATOL: float = 1e-9

#: λ used for the standalone K=2 joint heatmap with marginals.
JOINT_HEATMAP_LAMBDA: float = 2.0

#: λ used for the Schmidt-archetype dendrogram.
ARCHETYPE_DENDROGRAM_LAMBDA: float = 3.0

#: λ at which the genuine finite-N Monte-Carlo mutual-information
#: witness targets the closed-form Ising value.
MONTECARLO_MI_LAMBDA: float = 1.0

#: Sample count for each seeded Monte-Carlo mutual-information witness.
#: Large enough to make the sample mean concentrate while remaining fast.
MONTECARLO_MI_N: int = 120_000

#: Number of independent seeded Monte-Carlo replicates used for the
#: concentration witness.
MONTECARLO_MI_SEEDS: int = 12

#: Additive slack on top of the empirical 4σ confidence radius for the
#: plug-in mutual-information estimator's finite-N entropy bias.
MONTECARLO_MI_BIAS_TOL: float = 5e-3

#: Number of streams in the standalone coupling-graph visualization.
COUPLING_GRAPH_STREAM_COUNT: int = 4

#: pymdp λ values at which total correlation is sampled into the JSON.
PYMDP_TOTAL_CORRELATION_SENTINEL_LAMBDAS: tuple[float, ...] = (0.0, 1.0, 2.0, 4.0)

#: λ values at which the Bernoulli appendix (§S03) cross-checks the
#: closed-form mutual information against the empirical total
#: correlation. Five values: zero baseline, two interior anchors,
#: and a saturating high-coupling probe.
BERNOULLI_VERIFICATION_LAMBDAS: tuple[float, ...] = (0.0, 0.5, 1.0, 2.0, 4.0)

#: Strict closed-form-vs-empirical tolerance for the Bernoulli sentinel
#: cross-check. This is tighter than the full parameter-sweep CI gate.
BERNOULLI_VERIFICATION_TOLERANCE: float = 1e-9

#: Numerical agreement tolerance between closed-form and empirical MI
#: enforced in the §6.1 / §13 prose.
PARAMETER_SWEEP_AGREEMENT_TOLERANCE: float = 1e-6

# Canonical utility surplus levels for ``scripts/parameter_sweep.py`` defaults
# and ``validate_sweep`` column schema (three-point FE curve).
PARAMETER_SWEEP_DEFAULT_UTILITIES: tuple[float, ...] = (0.0, 1.0, 2.0)

#: λ=0 marginal-agreement tolerance for the pymdp coupled posterior.
PYMDP_MARGINAL_AGREEMENT_TOLERANCE: float = 1e-6

#: λ=0 free-energy-bundle total-correlation tolerance.
PYMDP_TC_ZERO_TOLERANCE: float = 1e-7

#: λ=0 coupling-term tolerance and non-negativity round-off floor.
PYMDP_COUPLING_ZERO_TOLERANCE: float = 1e-9

#: λ=0 entropy additivity tolerance.
PYMDP_ENTROPY_ADD_TOLERANCE: float = 1e-7

#: Positive-λ pymdp decomposition residual tolerance.  This checks the
#: ``free_energy_against_entangled_prior`` LHS against
#: ``entanglement_decomposition_rhs(...).total`` after zeroing the
#: per-stream G vectors already absorbed by pymdp's policy posterior.
PYMDP_DECOMPOSITION_RESIDUAL_TOLERANCE: float = 1e-9

#: Cross-platform JAX/pymdp single-stream floating tolerance.
PYMDP_SINGLE_STREAM_FLOAT_TOLERANCE: float = 1e-6

#: Coupling-tax probe λ used to extract the $O(\lambda^2)$ curvature
#: constant $C$ printed in figure ``coupling_tax_quadratic``.
COUPLING_TAX_PROBE_LAMBDA: float = 0.05
