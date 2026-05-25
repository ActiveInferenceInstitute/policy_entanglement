"""Single-source-of-truth hyperparameters for every figure / sweep
script that injects numbers into the manuscript.

Centralising these here is the manuscript's no-hardcode rule made
mechanical: scripts (`scripts/generate_figures.py`,
`scripts/parameter_sweep.py`, `scripts/simulate_pymdp.py`) read the
constants below, and `scripts/manuscript_variables.py` mirrors the
same constants into `output/data/manuscript_variables.json` so the
manuscript can `[[VAR:...]]` substitute them with no risk of drift.

All constants are immutable at import time.  Any change here
re-flows through every figure caption, prose value, and the
range-validation layer in `validate_manuscript.py`.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from lean.phase_constants import PHASE_LAMBDA_C1, PHASE_LAMBDA_C2  # noqa: F401 - re-export for sidecars/scripts

ArrayF = NDArray[np.float64]


@dataclass(frozen=True)
class FigureGrid:
    """A 1-D ``(start, stop, num)`` linspace plus a label."""

    start: float
    stop: float
    num: int
    label: str = ""

    def values(self) -> ArrayF:
        return np.linspace(self.start, self.stop, self.num)


# ---------------------------------------------------------------------------
# λ-sweep grids (closed-form Bernoulli + analytical figures)
# ---------------------------------------------------------------------------

#: 121-point grid on $[0, 6]$: closed-form Ising mutual information
#: validation against the empirical total correlation; also the
#: row count of `output/data/parameter_sweep.csv`.
PARAMETER_SWEEP_LAMBDAS = FigureGrid(0.0, 6.0, 121, label="parameter_sweep")

#: 31-point grid on $[0, 1.5]$: heterogeneous-coupling-tax envelope.
COUPLING_TAX_LAMBDAS = FigureGrid(0.0, 1.5, 31, label="coupling_tax_quadratic")

#: 401-point grid on $[0, 4]$: phase diagram fill bands.
PHASE_DIAGRAM_LAMBDAS = FigureGrid(0.0, 4.0, 401, label="phase_diagram")

#: 191-point grid on $\Delta \in [-0.95, 0.95]$: optimal coupling locus.
OPTIMAL_LAMBDA_DELTAS = FigureGrid(-0.95, 0.95, 191, label="optimal_lambda")

#: 81-point grid on $[0, 4]$: Schmidt rank vs $\lambda$.
SCHMIDT_RANK_LAMBDAS = FigureGrid(0.0, 4.0, 81, label="schmidt_rank")

#: 41-point grid on $[0, 4]$ × 21-point grid on utilities $[0, 2]$:
#: free-energy phase landscape and Schmidt entropy surface.
PHASE_LANDSCAPE_LAMBDAS = FigureGrid(0.0, 4.0, 41, label="phase_landscape_lams")
PHASE_LANDSCAPE_UTILITIES = FigureGrid(0.0, 2.0, 21, label="phase_landscape_utilities")

#: 31-point grid on $[0, 3]$: log-weight e-geodesic flow.
LOG_WEIGHT_FLOW_LAMBDAS = FigureGrid(0.0, 3.0, 31, label="log_weight_flow")

#: 21-point grid on $[0, 4]$: KL geodesic in the simplex summary plane.
KL_GEODESIC_LAMBDAS = FigureGrid(0.0, 4.0, 21, label="kl_geodesic")

#: 20-point grid on utilities $[0, 0.95]$ × 16-point grid on
#: precisions $\gamma \in [0.5, 2.0]$: $\lambda^\star$ locus.
LAMBDA_STAR_UTILITIES = FigureGrid(0.0, 0.95, 20, label="lambda_star_utility")
LAMBDA_STAR_GAMMAS = FigureGrid(0.5, 2.0, 16, label="lambda_star_gamma")


# ---------------------------------------------------------------------------
# pymdp simulation harness
# ---------------------------------------------------------------------------

#: 21-point λ-sweep on $[0, 4]$ that drives `simulate_pymdp.py`'s
#: total-correlation curve and the four sentinel-λ heatmaps.
PYMDP_SWEEP_LAMBDAS = FigureGrid(0.0, 4.0, 21, label="pymdp_sweep")

#: Deterministic rollout horizon (steps) and seed used by
#: `simulate_coupled_rollout` in the figure pipeline.
PYMDP_ROLLOUT_STEPS: int = 10
PYMDP_ROLLOUT_SEED: int = 0
PYMDP_ROLLOUT_LAMBDA: float = 2.0

#: Observations driving the static λ-sweep (both streams see "0").
PYMDP_SWEEP_OBSERVATIONS: tuple[int, ...] = (0, 0)

#: Deterministic seed used by `deterministic_setup` at the top of
#: the figure scripts.  Pinned so every figure is bit-reproducible.
FIGURE_GLOBAL_SEED: int = 42

#: Coupling strength baked into the K=2 ensemble shipped to pymdp.
PYMDP_ENSEMBLE_COUPLING_LAMBDA: float = 1.0
PYMDP_ENSEMBLE_GAMMA: float = 1.0
PYMDP_ENSEMBLE_K: int = 2


# ---------------------------------------------------------------------------
# K>2 ensemble experiments (T1: multi-K sweep)
# ---------------------------------------------------------------------------

#: Stream counts at which the K>2 multi-K experiment runs the full
#: ``free_energy_curve`` sweep. ``K=2`` is already covered by
#: :data:`PYMDP_ENSEMBLE_K`; this tuple drives the additional CSV / figure
#: outputs in :mod:`simulation.multi_k_experiments`.
MULTI_K_VALUES: tuple[int, ...] = (3, 4, 5)

#: 9-point λ-sweep on $[0, 4]$ used by the multi-K experiment. Sparser
#: than :data:`PYMDP_SWEEP_LAMBDAS` because the K=5 ensemble has a
#: 2^5 = 32-cell joint and a larger Agent construction cost; 9 grid
#: points is sufficient to resolve the monotone TC growth in λ.
MULTI_K_SWEEP_LAMBDAS = FigureGrid(0.0, 4.0, 9, label="multi_k_sweep")

#: Sentinel λ at which each multi-K experiment emits a single joint
#: heatmap snapshot for the manuscript figure.
MULTI_K_SENTINEL_LAMBDA: float = 2.0


# ---------------------------------------------------------------------------
# Long-horizon rollout (T2: T=100 steps)
# ---------------------------------------------------------------------------

#: Horizon (steps) of the long-horizon rollout used to verify habit
#: accumulation under the coupled dynamics.
LONG_HORIZON_STEPS: int = 100

#: Coupling strength of the long-horizon rollout. We pick a moderate
#: value so the marginals are non-trivially deformed by coupling
#: without being saturated.
LONG_HORIZON_LAMBDA: float = 2.0

#: Deterministic seed for the long-horizon rollout.
LONG_HORIZON_SEED: int = 0

#: Optional replicate seeds for robustness summaries. The canonical
#: manuscript figure uses :data:`LONG_HORIZON_SEED`; these additional
#: seeds let future scripts build quantile envelopes without changing
#: the main deterministic artifact.
LONG_HORIZON_REPLICATE_SEEDS: tuple[int, ...] = (0, 7, 13, 29, 41)

#: How many trailing steps to average over when computing the marginal
#: steady-state. The marginal at horizon - LONG_HORIZON_TAIL_WINDOW
#: should be close (within :data:`LONG_HORIZON_STEADY_STATE_TOL`) to
#: the time-averaged marginal across the trailing window.
LONG_HORIZON_TAIL_WINDOW: int = 20

#: Tolerance on the trailing-vs-tail KL divergence used to mark the
#: marginal as ``converged``. Set loosely because the long-horizon
#: rollout includes stochastic sampling of actions and observations:
#: the realized per-step marginal fluctuates around the steady-state
#: by a finite-sample KL of ~0.1 even after habit accumulation.
LONG_HORIZON_STEADY_STATE_TOL: float = 1.5e-1


# ---------------------------------------------------------------------------
# Robustness / ablation stress tests
# ---------------------------------------------------------------------------

#: One-axis-at-a-time observation-context perturbations for the
#: reviewer-facing robustness suite.  The canonical static pymdp sweep
#: uses :data:`PYMDP_SWEEP_OBSERVATIONS`; these contexts test whether
#: the total-correlation and decomposition witnesses survive all four
#: binary observation cases without expanding to a full Cartesian grid.
ROBUSTNESS_OBSERVATION_CONTEXTS: tuple[tuple[int, ...], ...] = (
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1),
)

#: One-axis-at-a-time EFE precision values for robustness sweeps.
ROBUSTNESS_GAMMAS: tuple[float, ...] = (0.5, 1.0, 2.0)

#: One-axis-at-a-time prior-preference strengths for robustness sweeps.
ROBUSTNESS_PREFERENCE_STRENGTHS: tuple[float, ...] = (0.5, 1.0, 2.0)

#: One-axis-at-a-time Ising coupling-scale values for robustness
#: sweeps; the ``0.0`` row is the null-coupling flatline sentinel.
ROBUSTNESS_COUPLING_SCALES: tuple[float, ...] = (0.0, 0.5, 1.0, 1.5)

#: Appendix-only targeted two-axis interaction families.  These avoid
#: the full Cartesian product while testing the three most review-
#: relevant interactions: observation context with coupling scale,
#: precision with preference strength, and coupling variant with
#: coupling scale.
ROBUSTNESS_INTERACTION_FAMILIES: tuple[str, ...] = (
    "observation_x_coupling_scale",
    "gamma_x_preference_strength",
    "coupling_variant_x_coupling_scale",
)

#: λ grid for the robustness and coupling-ablation experiments.  It is
#: intentionally identical in shape to the canonical pymdp sweep but
#: named separately so figure metadata can distinguish stress tests
#: from the main sweep.
ROBUSTNESS_SWEEP_LAMBDAS = FigureGrid(0.0, 4.0, 21, label="robustness_sweep")

#: Fixed coupling-ablation variants.  ``heterogeneous_kc`` uses the
#: small signed tax matrix below while keeping the aligned Ising prior.
COUPLING_ABLATION_VARIANTS: tuple[str, ...] = (
    "aligned",
    "null",
    "anti_aligned",
    "heterogeneous_kc",
)

#: Small cross-stream tax matrix used by the heterogeneous ablation.
COUPLING_ABLATION_KC_MATRIX: tuple[tuple[float, float], tuple[float, float]] = (
    (0.2, -0.1),
    (-0.1, 0.2),
)

#: Threshold probes for long-horizon replicate diagnostics.  The
#: canonical habit flag continues to use
#: :data:`LONG_HORIZON_STEADY_STATE_TOL`; these probes expose how
#: sensitive the pass rate is to stricter or looser tail-window KL
#: criteria.
LONG_HORIZON_DIAGNOSTIC_THRESHOLDS: tuple[float, ...] = (0.05, 0.10, 0.15, 0.20, 0.25)


# ---------------------------------------------------------------------------
# Revertibility / m-projection (T3)
# ---------------------------------------------------------------------------

#: λ grid on which :mod:`simulation.revertibility` evaluates the
#: m-projection witness. Five sentinel values: zero baseline, three
#: interior probes, and a saturating high-coupling probe.
REVERTIBILITY_LAMBDAS: tuple[float, ...] = (0.0, 0.5, 1.0, 2.0, 4.0)

#: Floating-point tolerance for the "m-projection marginals match the
#: original posterior's marginals" identity. This is an exact algebraic
#: equality (marginals are linear in the joint), so the tolerance is
#: a floating-point round-off budget rather than a modeling slack.
REVERTIBILITY_TOLERANCE: float = 1e-12

#: Tolerance for the ``KL(q_λ ‖ m(q_λ)) == I(q_λ)`` identity. Slightly
#: looser than :data:`REVERTIBILITY_TOLERANCE` because both sides of
#: the equation involve sums of safe-log terms.
REVERTIBILITY_KL_IDENTITY_TOLERANCE: float = 1e-9


# ---------------------------------------------------------------------------
# pymdp 1.0.1 Agent construction knobs
# ---------------------------------------------------------------------------
# Centralising these means a single edit propagates to every Agent built by
# `simulation.agents.build_pymdp_agent` and every downstream sweep / rollout.
# The previous behaviour hardcoded defaults inside the builder; that left
# the inference algorithm, FPI iteration count, and the precision-of-action
# settings opaque to the manuscript's reproducibility contract.

#: Default policy lookahead horizon passed to ``pymdp.agent.Agent``. A
#: value of 1 corresponds to the single-step posterior on which the
#: manuscript's coupled-policy derivation is anchored (§4); larger values
#: extend pymdp's own internal lookahead — orthogonal to the framework's
#: λ-coupling layer.
PYMDP_AGENT_POLICY_LEN: int = 1

#: Inference algorithm. ``"fpi"`` (fixed-point iteration) is pymdp's
#: deterministic default and the only algorithm currently exercised by
#: this harness; ``"vmp"`` (variational message passing) is available for
#: alternative experimentation but not validated against the §13 numeric
#: witnesses.
PYMDP_AGENT_INFERENCE_ALGO: str = "fpi"

#: FPI iteration count. pymdp's default is 16; we lift to 32 so the
#: per-stream posterior is converged to a tighter tolerance, matching
#: the analytical layer's ``1e-12`` agreement floor on
#: ``PYMDP_MARGINAL_AGREEMENT_TOLERANCE``.
PYMDP_AGENT_NUM_ITER: int = 32

#: Action-selection mode for ``Agent.sample_action``. ``"deterministic"``
#: pins the rollout to the argmax-policy at every step (the manuscript's
#: §14 long-horizon trace claims deterministic seeding; the alternative
#: ``"stochastic"`` is documented but not currently exercised).
PYMDP_AGENT_ACTION_SELECTION: str = "deterministic"

#: Inverse-temperature on the action-selection policy. Higher values
#: sharpen toward the argmax; the default 16 matches pymdp's library
#: default and keeps the argmax-policy effectively deterministic.
PYMDP_AGENT_ALPHA: float = 16.0

#: Whether to include the *states* info-gain term in EFE. Disabled by
#: default in the K=2 Ising setting because the observation likelihood
#: is identity (no state information to gain).
PYMDP_AGENT_USE_STATES_INFO_GAIN: bool = False

#: Whether to include the *parameter* info-gain term in EFE. Off by
#: default because the K=2 Ising A/B/D matrices are fixed (no parameter
#: learning).
PYMDP_AGENT_USE_PARAM_INFO_GAIN: bool = False


# ---------------------------------------------------------------------------
# BTAI baseline (shipped §13 empirical harness) — central knobs


# ---------------------------------------------------------------------------
# BTAI baseline (shipped §13 empirical harness) — central knobs
# ---------------------------------------------------------------------------

#: Pre-registered MCTS budgets used by the BTAI head-to-head baseline.
#: Log-spaced over three orders of magnitude (10², 10³, 10⁴) — the same
#: schedule embedded in the §13 shipped worked-run design.
BTAI_DEFAULT_BUDGETS: tuple[int, ...] = (100, 1000, 10000)

#: UCB1 exploration constant for the BTAI MCTS tree policy.
#: ``sqrt(2)`` is the classical UCB1 constant; it controls the trade-off
#: between exploring novel branches and exploiting the lowest-EFE arms,
#: and is the only knob in MCTS that materially changes the empirical
#: sample-complexity exponent the falsification gate measures.
BTAI_UCB_EXPLORATION: float = 2.0**0.5

#: Representative coupled operating point whose closed-form K=2 Bernoulli
#: posterior is the analytic reference the BTAI visitation posterior is
#: scored against. Matches the canonical sweep's unit-coupling point.
BTAI_REFERENCE_LAMBDA: float = 1.0

#: Decision horizon for the BTAI worked run. A single decision step
#: yields the cleanest per-step joint policy posterior — the observable
#: the head-to-head comparison is about.
BTAI_HORIZON: int = 1

#: Ising-ensemble knobs for the BTAI pymdp-grounded EFE landscape (the
#: K=2 unit-coupling reference ensemble). ``gamma`` is intentionally
#: shared with :data:`PYMDP_ENSEMBLE_GAMMA` so the BTAI run cannot
#: silently drift from the canonical ensemble precision.
BTAI_ENSEMBLE_COUPLING_AMPLITUDE: float = 1.0
BTAI_ENSEMBLE_PREFERENCE_STRENGTH: float = 1.0
BTAI_NUM_STREAMS: int = 2


# ---------------------------------------------------------------------------
# Adversarial-perturbation harness (§20 Q11) — central knobs
# ---------------------------------------------------------------------------

#: Pre-registered L^∞ perturbation budgets for the adversarial sweep.
#: Log-spaced 10⁻³ … 10⁰ over seven half-decade steps.
ADVERSARIAL_EPSILON_GRID: tuple[float, ...] = tuple(10.0 ** (-3.0 + 0.5 * step) for step in range(7))

#: Pre-registered λ values for the adversarial sweep. Matches the
#: revertibility sweep so the two harnesses can be cross-compared at
#: the same grid points.
ADVERSARIAL_LAMBDA_GRID: tuple[float, ...] = (0.0, 0.5, 1.0, 2.0, 4.0)

#: Default base seed for the adversarial sweep — used to initialize per
#: scenario the uniform and sparse adversaries; the analytical rank-one
#: adversary is deterministic given (q, J).
ADVERSARIAL_DEFAULT_SEED: int = 12345


# ---------------------------------------------------------------------------
# Sentinel λ values (used by the manuscript prose VAR substitutions)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Lightweight helpers
# ---------------------------------------------------------------------------


def grid_count(grid: FigureGrid) -> int:
    """Return ``grid.num`` — convenience for manuscript variable export."""
    return int(grid.num)


def figure_hyperparameter_summary() -> dict[str, object]:
    """Flat dict of every grid count + scalar.

    Consumed by `scripts/manuscript_variables.py` to populate the
    `[[VAR:...]]` namespace; the keys are stable and used directly
    inside `manuscript/*.md`.
    """
    return {
        # grid sizes
        "param_sweep_grid_points": grid_count(PARAMETER_SWEEP_LAMBDAS),
        "param_sweep_lambda_min": float(PARAMETER_SWEEP_LAMBDAS.start),
        "param_sweep_lambda_max": float(PARAMETER_SWEEP_LAMBDAS.stop),
        "coupling_tax_grid_points": grid_count(COUPLING_TAX_LAMBDAS),
        "coupling_tax_lambda_min": float(COUPLING_TAX_LAMBDAS.start),
        "coupling_tax_lambda_max": float(COUPLING_TAX_LAMBDAS.stop),
        "phase_diagram_grid_points": grid_count(PHASE_DIAGRAM_LAMBDAS),
        "phase_diagram_lambda_min": float(PHASE_DIAGRAM_LAMBDAS.start),
        "phase_diagram_lambda_max": float(PHASE_DIAGRAM_LAMBDAS.stop),
        "optimal_lambda_grid_points": grid_count(OPTIMAL_LAMBDA_DELTAS),
        "optimal_lambda_delta_min": float(OPTIMAL_LAMBDA_DELTAS.start),
        "optimal_lambda_delta_max": float(OPTIMAL_LAMBDA_DELTAS.stop),
        "schmidt_rank_grid_points": grid_count(SCHMIDT_RANK_LAMBDAS),
        "schmidt_rank_lambda_min": float(SCHMIDT_RANK_LAMBDAS.start),
        "schmidt_rank_lambda_max": float(SCHMIDT_RANK_LAMBDAS.stop),
        "phase_landscape_lambda_points": grid_count(PHASE_LANDSCAPE_LAMBDAS),
        "phase_landscape_lambda_min": float(PHASE_LANDSCAPE_LAMBDAS.start),
        "phase_landscape_lambda_max": float(PHASE_LANDSCAPE_LAMBDAS.stop),
        "phase_landscape_utility_points": grid_count(PHASE_LANDSCAPE_UTILITIES),
        "phase_landscape_utility_min": float(PHASE_LANDSCAPE_UTILITIES.start),
        "phase_landscape_utility_max": float(PHASE_LANDSCAPE_UTILITIES.stop),
        "log_weight_flow_grid_points": grid_count(LOG_WEIGHT_FLOW_LAMBDAS),
        "log_weight_flow_lambda_min": float(LOG_WEIGHT_FLOW_LAMBDAS.start),
        "log_weight_flow_lambda_max": float(LOG_WEIGHT_FLOW_LAMBDAS.stop),
        "kl_geodesic_grid_points": grid_count(KL_GEODESIC_LAMBDAS),
        "kl_geodesic_lambda_min": float(KL_GEODESIC_LAMBDAS.start),
        "kl_geodesic_lambda_max": float(KL_GEODESIC_LAMBDAS.stop),
        "lambda_star_utility_points": grid_count(LAMBDA_STAR_UTILITIES),
        "lambda_star_utility_min": float(LAMBDA_STAR_UTILITIES.start),
        "lambda_star_utility_max": float(LAMBDA_STAR_UTILITIES.stop),
        "lambda_star_gamma_points": grid_count(LAMBDA_STAR_GAMMAS),
        "lambda_star_gamma_min": float(LAMBDA_STAR_GAMMAS.start),
        "lambda_star_gamma_max": float(LAMBDA_STAR_GAMMAS.stop),
        # pymdp
        "pymdp_sweep_grid_points": grid_count(PYMDP_SWEEP_LAMBDAS),
        "pymdp_sweep_lambda_min": float(PYMDP_SWEEP_LAMBDAS.start),
        "pymdp_sweep_lambda_max": float(PYMDP_SWEEP_LAMBDAS.stop),
        "pymdp_rollout_steps": int(PYMDP_ROLLOUT_STEPS),
        "pymdp_rollout_seed": int(PYMDP_ROLLOUT_SEED),
        "pymdp_rollout_lambda": float(PYMDP_ROLLOUT_LAMBDA),
        "pymdp_ensemble_K": int(PYMDP_ENSEMBLE_K),
        "pymdp_ensemble_coupling_lambda": float(PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        "pymdp_ensemble_gamma": float(PYMDP_ENSEMBLE_GAMMA),
        "pymdp_sweep_observations": list(PYMDP_SWEEP_OBSERVATIONS),
        "pymdp_agent_policy_len": int(PYMDP_AGENT_POLICY_LEN),
        "pymdp_agent_inference_algo": str(PYMDP_AGENT_INFERENCE_ALGO),
        "pymdp_agent_num_iter": int(PYMDP_AGENT_NUM_ITER),
        "pymdp_agent_action_selection": str(PYMDP_AGENT_ACTION_SELECTION),
        "pymdp_agent_alpha": float(PYMDP_AGENT_ALPHA),
        "pymdp_agent_use_states_info_gain": bool(PYMDP_AGENT_USE_STATES_INFO_GAIN),
        "pymdp_agent_use_param_info_gain": bool(PYMDP_AGENT_USE_PARAM_INFO_GAIN),
        # global
        "figure_global_seed": int(FIGURE_GLOBAL_SEED),
        "tt_rank_profile_lambda": float(TT_RANK_PROFILE_LAMBDA),
        "spectral_rank_atol": float(SPECTRAL_RANK_ATOL),
        "joint_heatmap_lambda": float(JOINT_HEATMAP_LAMBDA),
        "archetype_dendrogram_lambda": float(ARCHETYPE_DENDROGRAM_LAMBDA),
        "montecarlo_mi_lambda": float(MONTECARLO_MI_LAMBDA),
        "montecarlo_mi_n": int(MONTECARLO_MI_N),
        "montecarlo_mi_seeds": int(MONTECARLO_MI_SEEDS),
        "montecarlo_mi_bias_tol": float(MONTECARLO_MI_BIAS_TOL),
        "coupling_graph_stream_count": int(COUPLING_GRAPH_STREAM_COUNT),
        "bernoulli_verification_tolerance": float(BERNOULLI_VERIFICATION_TOLERANCE),
        "param_sweep_agreement_tolerance": float(PARAMETER_SWEEP_AGREEMENT_TOLERANCE),
        "pymdp_marginal_agreement_tolerance": float(PYMDP_MARGINAL_AGREEMENT_TOLERANCE),
        "pymdp_tc_zero_tolerance": float(PYMDP_TC_ZERO_TOLERANCE),
        "pymdp_coupling_zero_tolerance": float(PYMDP_COUPLING_ZERO_TOLERANCE),
        "pymdp_entropy_add_tolerance": float(PYMDP_ENTROPY_ADD_TOLERANCE),
        "pymdp_decomposition_residual_tolerance": float(PYMDP_DECOMPOSITION_RESIDUAL_TOLERANCE),
        "pymdp_single_stream_float_tolerance": float(PYMDP_SINGLE_STREAM_FLOAT_TOLERANCE),
        "phase_lambda_c1": float(PHASE_LAMBDA_C1),
        "phase_lambda_c2": float(PHASE_LAMBDA_C2),
        "coupling_tax_probe_lambda": float(COUPLING_TAX_PROBE_LAMBDA),
        # multi-K, long-horizon, revertibility
        "multi_k_values": list(int(k) for k in MULTI_K_VALUES),
        "multi_k_sweep_grid_points": grid_count(MULTI_K_SWEEP_LAMBDAS),
        "multi_k_sweep_lambda_min": float(MULTI_K_SWEEP_LAMBDAS.start),
        "multi_k_sweep_lambda_max": float(MULTI_K_SWEEP_LAMBDAS.stop),
        "multi_k_sentinel_lambda": float(MULTI_K_SENTINEL_LAMBDA),
        "long_horizon_steps": int(LONG_HORIZON_STEPS),
        "long_horizon_lambda": float(LONG_HORIZON_LAMBDA),
        "long_horizon_seed": int(LONG_HORIZON_SEED),
        "long_horizon_replicate_seeds": list(int(s) for s in LONG_HORIZON_REPLICATE_SEEDS),
        "long_horizon_replicate_seed_count": len(LONG_HORIZON_REPLICATE_SEEDS),
        "long_horizon_tail_window": int(LONG_HORIZON_TAIL_WINDOW),
        "long_horizon_steady_state_tol": float(LONG_HORIZON_STEADY_STATE_TOL),
        "robustness_observation_contexts": [list(obs) for obs in ROBUSTNESS_OBSERVATION_CONTEXTS],
        "robustness_observation_context_count": len(ROBUSTNESS_OBSERVATION_CONTEXTS),
        "robustness_gammas": [float(x) for x in ROBUSTNESS_GAMMAS],
        "robustness_gamma_count": len(ROBUSTNESS_GAMMAS),
        "robustness_preference_strengths": [float(x) for x in ROBUSTNESS_PREFERENCE_STRENGTHS],
        "robustness_preference_strength_count": len(ROBUSTNESS_PREFERENCE_STRENGTHS),
        "robustness_coupling_scales": [float(x) for x in ROBUSTNESS_COUPLING_SCALES],
        "robustness_coupling_scale_count": len(ROBUSTNESS_COUPLING_SCALES),
        "robustness_interaction_families": list(ROBUSTNESS_INTERACTION_FAMILIES),
        "robustness_interaction_family_count": len(ROBUSTNESS_INTERACTION_FAMILIES),
        "robustness_sweep_grid_points": grid_count(ROBUSTNESS_SWEEP_LAMBDAS),
        "robustness_sweep_lambda_min": float(ROBUSTNESS_SWEEP_LAMBDAS.start),
        "robustness_sweep_lambda_max": float(ROBUSTNESS_SWEEP_LAMBDAS.stop),
        "coupling_ablation_variants": list(COUPLING_ABLATION_VARIANTS),
        "coupling_ablation_variant_count": len(COUPLING_ABLATION_VARIANTS),
        "coupling_ablation_kc_matrix": [list(row) for row in COUPLING_ABLATION_KC_MATRIX],
        "long_horizon_diagnostic_thresholds": [float(x) for x in LONG_HORIZON_DIAGNOSTIC_THRESHOLDS],
        "long_horizon_diagnostic_threshold_count": len(LONG_HORIZON_DIAGNOSTIC_THRESHOLDS),
        "revertibility_lambdas": [float(x) for x in REVERTIBILITY_LAMBDAS],
        "revertibility_tolerance": float(REVERTIBILITY_TOLERANCE),
        "revertibility_kl_identity_tolerance": float(REVERTIBILITY_KL_IDENTITY_TOLERANCE),
    }
