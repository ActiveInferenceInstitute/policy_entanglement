"""Output artifact validation gates for the Policy Entanglement project."""

from __future__ import annotations

from pathlib import Path

from manuscript.registry_facts import registry_structural_count_gates
from manuscript.variable_ranges import ANALYTICAL_VARIABLE_RANGES, merge_required_variables
from simulation import hyperparameters as H  # noqa: N812

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
SRC_DIR = PROJECT_ROOT / "src"


def registry_count_gates() -> dict[str, tuple[float, float]]:
    return registry_structural_count_gates(PROJECT_ROOT)


REQUIRED_FIGURES = [
    # Legacy 6 (manuscript core).
    "ising_mi_curve.png",
    "free_energy_curve.png",
    "coupling_tax_quadratic.png",
    "phase_diagram.png",
    "optimal_lambda.png",
    "schmidt_rank.png",
    # New visualizations subpackage figures.
    "phase_landscape.png",
    "schmidt_entropy_surface.png",
    "joint_heatmap_lambda2.png",
    "archetype_dendrogram.png",
    "tensor_train_rank_surface.png",
    "log_weight_flow.png",
    "kl_geodesic_simplex.png",
    "lambda_star_locus.png",
]

# Optional figures that exist only when their generator runs (sim / viz groups).
OPTIONAL_FIGURES = [
    "coupling_graph.png",
    "pymdp_total_correlation_curve.png",
    "pymdp_coupled_rollout.png",
    "pymdp_joint_lambda_0.00.png",
    "pymdp_joint_lambda_2.00.png",
    "pymdp_joint_lambda_4.00.png",
    "pymdp_free_energy_panel.png",
    "pymdp_vfe_decomposition.png",
    "pymdp_efe_under_posterior.png",
    "pymdp_entropy_decomposition.png",
    "pymdp_action_distribution.png",
    "pymdp_action_entropy.png",
    "pymdp_kl_to_lambda_zero.png",
    "pymdp_marginal_entropy_per_stream.png",
    "pymdp_summary_panel.png",
    # K>2 multi-K, long-horizon, revertibility (added in T1/T2/T3 Wave 1).
    "multi_k_total_correlation.png",
    "multi_k_aligned_mass.png",
    "multi_k_tt_rank_profile.png",
    "long_horizon_marginals.png",
    "long_horizon_steady_state.png",
    "revertibility_witness.png",
    "robustness_tc_envelopes.png",
    "robustness_half_saturation.png",
    "robustness_decomposition_residuals.png",
    "coupling_ablation_summary.png",
    "marginal_null_control_summary.png",
    "interaction_robustness_summary.png",
    "long_horizon_replicate_envelope.png",
    "long_horizon_seed_diagnostics.png",
    "long_horizon_threshold_sensitivity.png",
    # Shipped BTAI / adversarial worked-run figures: emitted by the
    # `simulate_btai` / `simulate_adversarial` parallel stages, so a
    # silent figure-generation failure in those stages is now caught.
    "btai_baseline.png",
    "adversarial_sweep.png",
    # Shipped GNN fifth-track round-trip figure (emitted by the `simulate_gnn`
    # stage), so a silent figure-generation failure in that stage is caught.
    "gnn_bernoulli_roundtrip.png",
]

GATE_SPECIFIC_RANGES: dict[str, tuple[float, float]] = {
    "pymdp_decomposition_residual_max": (0.0, float(H.PYMDP_DECOMPOSITION_RESIDUAL_TOLERANCE)),
    # Robustness / ablation / replicate sidecars
    "robustness_scenario_count": (
        float(
            len(H.ROBUSTNESS_OBSERVATION_CONTEXTS)
            + len(H.ROBUSTNESS_GAMMAS)
            + len(H.ROBUSTNESS_PREFERENCE_STRENGTHS)
            + len(H.ROBUSTNESS_COUPLING_SCALES)
        ),
        float(
            len(H.ROBUSTNESS_OBSERVATION_CONTEXTS)
            + len(H.ROBUSTNESS_GAMMAS)
            + len(H.ROBUSTNESS_PREFERENCE_STRENGTHS)
            + len(H.ROBUSTNESS_COUPLING_SCALES)
        ),
    ),
    "robustness_decomposition_residual_max": (0.0, float(H.PYMDP_DECOMPOSITION_RESIDUAL_TOLERANCE)),
    "robustness_null_coupling_tc_max": (0.0, float(H.PYMDP_TC_ZERO_TOLERANCE)),
    "coupling_ablation_variant_count": (
        float(len(H.COUPLING_ABLATION_VARIANTS)),
        float(len(H.COUPLING_ABLATION_VARIANTS)),
    ),
    "coupling_ablation_decomposition_residual_max": (0.0, float(H.PYMDP_DECOMPOSITION_RESIDUAL_TOLERANCE)),
    "coupling_ablation_null_tc_max": (0.0, float(H.PYMDP_TC_ZERO_TOLERANCE)),
    "robustness_null_control_max_tc": (0.0, float(H.PYMDP_TC_ZERO_TOLERANCE)),
    "robustness_null_control_tc_removed_max": (0.0, float("inf")),
    # RedTeam 2026-05-19 C3 — the DISCRIMINATING gate. `max_tc` (≈0) is
    # definitional for product-of-marginals (true for ANY q — unfailable
    # sanity); `tc_removed_max (0,inf)` is vacuous. This asserts the null
    # control removed essentially ALL the multi-information on the rows
    # that actually have coupling: min over rows with original_tc > 1e-6
    # of (tc_removed / original_tc) must be ≈ 1. A mis-marginalised
    # control (leaves coupling) or one that never exercises coupling
    # fails here.
    "robustness_null_control_tc_removed_fraction_min": (1.0 - 1e-6, 1.0 + 1e-6),
    "interaction_robustness_family_count": (
        float(len(H.ROBUSTNESS_INTERACTION_FAMILIES)),
        float(len(H.ROBUSTNESS_INTERACTION_FAMILIES)),
    ),
    "interaction_robustness_decomposition_residual_max": (0.0, float(H.PYMDP_DECOMPOSITION_RESIDUAL_TOLERANCE)),
    "interaction_robustness_null_variant_tc_max": (0.0, float(H.PYMDP_TC_ZERO_TOLERANCE)),
    "long_horizon_replicate_habit_pass_rate": (0.0, 1.0),
    "long_horizon_replicate_habit_pass_rate_ci_low": (0.0, 1.0),
    "long_horizon_replicate_habit_pass_rate_ci_high": (0.0, 1.0),
    "long_horizon_replicate_tail_kl_window_max": (0.0, float("inf")),
    "long_horizon_replicate_failure_count": (0.0, float(len(H.LONG_HORIZON_REPLICATE_SEEDS))),
    "long_horizon_replicate_threshold_count": (
        float(len(H.LONG_HORIZON_DIAGNOSTIC_THRESHOLDS)),
        float(len(H.LONG_HORIZON_DIAGNOSTIC_THRESHOLDS)),
    ),
    "long_horizon_replicate_threshold_pass_rate_min": (0.0, 1.0),
    "long_horizon_replicate_threshold_pass_rate_max": (0.0, 1.0),
    "long_horizon_replicate_threshold_pass_rate_range": (0.0, 1.0),
    # Pass-13 R1 — TT/MPS bond ranks. These bounds are MATHEMATICALLY
    # NECESSARY, not observed-value fits (which would be the C2 defect):
    # a tensor-train bond dimension is >= 1 by construction and, for a
    # chain of K binary (dim-2) streams, is bounded above by the maximal
    # cut dimension 2**floor(K/2) (K3 -> 2, K4/K5 -> 4). A run that
    # produced a rank outside [1, 2**floor(K/2)] would be structurally
    # impossible, so this gate fails closed on a corrupt sidecar without
    # pinning to the specific observed integer.
    "multi_k_K3_tt_rank_max_at_lambda_max": (1.0, 2.0),
    "multi_k_K4_tt_rank_max_at_lambda_max": (1.0, 4.0),
    "multi_k_K5_tt_rank_max_at_lambda_max": (1.0, 4.0),
    # ----------------------------------------------------------------
    # Pass-13 R1 — STRUCTURAL-SOURCE concordance pins. Each bound is the
    # hyperparameter STRUCTURAL DEFINITION (H.<grid>.num / len(H.<tuple>)
    # / H.<scalar>), NOT a hardcoded observed integer. This is the same
    # idiom already used above for robustness_scenario_count etc.: the
    # gate asserts the persisted manuscript value still equals its
    # generating constant (catches a desync / stale sidecar), which is
    # categorically different from the C2 defect (a bound derived from
    # the run's own output). If a grid is resized, both the generator
    # and this gate move together off the single H source of truth.
    "param_sweep_grid_points": (float(H.PARAMETER_SWEEP_LAMBDAS.num), float(H.PARAMETER_SWEEP_LAMBDAS.num)),
    "coupling_tax_grid_points": (float(H.COUPLING_TAX_LAMBDAS.num), float(H.COUPLING_TAX_LAMBDAS.num)),
    "phase_diagram_grid_points": (float(H.PHASE_DIAGRAM_LAMBDAS.num), float(H.PHASE_DIAGRAM_LAMBDAS.num)),
    "optimal_lambda_grid_points": (float(H.OPTIMAL_LAMBDA_DELTAS.num), float(H.OPTIMAL_LAMBDA_DELTAS.num)),
    "schmidt_rank_grid_points": (float(H.SCHMIDT_RANK_LAMBDAS.num), float(H.SCHMIDT_RANK_LAMBDAS.num)),
    "phase_landscape_lambda_points": (float(H.PHASE_LANDSCAPE_LAMBDAS.num), float(H.PHASE_LANDSCAPE_LAMBDAS.num)),
    "phase_landscape_utility_points": (float(H.PHASE_LANDSCAPE_UTILITIES.num), float(H.PHASE_LANDSCAPE_UTILITIES.num)),
    "log_weight_flow_grid_points": (float(H.LOG_WEIGHT_FLOW_LAMBDAS.num), float(H.LOG_WEIGHT_FLOW_LAMBDAS.num)),
    "kl_geodesic_grid_points": (float(H.KL_GEODESIC_LAMBDAS.num), float(H.KL_GEODESIC_LAMBDAS.num)),
    "lambda_star_utility_points": (float(H.LAMBDA_STAR_UTILITIES.num), float(H.LAMBDA_STAR_UTILITIES.num)),
    "lambda_star_gamma_points": (float(H.LAMBDA_STAR_GAMMAS.num), float(H.LAMBDA_STAR_GAMMAS.num)),
    "pymdp_sweep_grid_points": (float(H.PYMDP_SWEEP_LAMBDAS.num), float(H.PYMDP_SWEEP_LAMBDAS.num)),
    "pymdp_summary_n_lambda_points": (float(H.PYMDP_SWEEP_LAMBDAS.num), float(H.PYMDP_SWEEP_LAMBDAS.num)),
    "robustness_sweep_grid_points": (float(H.ROBUSTNESS_SWEEP_LAMBDAS.num), float(H.ROBUSTNESS_SWEEP_LAMBDAS.num)),
    "pymdp_rollout_steps": (float(H.PYMDP_ROLLOUT_STEPS), float(H.PYMDP_ROLLOUT_STEPS)),
    "long_horizon_steps": (float(H.LONG_HORIZON_STEPS), float(H.LONG_HORIZON_STEPS)),
    "long_horizon_tail_window": (float(H.LONG_HORIZON_TAIL_WINDOW), float(H.LONG_HORIZON_TAIL_WINDOW)),
    "coupling_graph_stream_count": (float(H.COUPLING_GRAPH_STREAM_COUNT), float(H.COUPLING_GRAPH_STREAM_COUNT)),
    "robustness_observation_context_count": (
        float(len(H.ROBUSTNESS_OBSERVATION_CONTEXTS)),
        float(len(H.ROBUSTNESS_OBSERVATION_CONTEXTS)),
    ),
    "robustness_gamma_count": (float(len(H.ROBUSTNESS_GAMMAS)), float(len(H.ROBUSTNESS_GAMMAS))),
    "robustness_preference_strength_count": (
        float(len(H.ROBUSTNESS_PREFERENCE_STRENGTHS)),
        float(len(H.ROBUSTNESS_PREFERENCE_STRENGTHS)),
    ),
    "robustness_coupling_scale_count": (
        float(len(H.ROBUSTNESS_COUPLING_SCALES)),
        float(len(H.ROBUSTNESS_COUPLING_SCALES)),
    ),
    "bernoulli_verification_lambdas_count": (
        float(len(H.BERNOULLI_VERIFICATION_LAMBDAS)),
        float(len(H.BERNOULLI_VERIFICATION_LAMBDAS)),
    ),
    "pymdp_ensemble_K": (float(H.PYMDP_ENSEMBLE_K), float(H.PYMDP_ENSEMBLE_K)),
    "revertibility_num_lambdas": (float(len(H.REVERTIBILITY_LAMBDAS)), float(len(H.REVERTIBILITY_LAMBDAS))),
    # Seeds are fixed reproducibility constants — pin exact to H.
    "figure_global_seed": (float(H.FIGURE_GLOBAL_SEED), float(H.FIGURE_GLOBAL_SEED)),
    "long_horizon_seed": (float(H.LONG_HORIZON_SEED), float(H.LONG_HORIZON_SEED)),
    "pymdp_rollout_seed": (float(H.PYMDP_ROLLOUT_SEED), float(H.PYMDP_ROLLOUT_SEED)),
    # Scan-derived declaration counts (parsed from the Lean tree / run_all
    # at generation time) are NOT hyperparameter constants, so pinning to
    # the observed integer WOULD be the C2 defect. Instead a DOMAIN-
    # NECESSARY loose bound: a built Lean project / scripts dir has >= 1
    # of each kind and the count is finite. Catches 0 / negative / parse-
    # failure garbage without fabricating a tight value the author owns.
    "lean_def_count": (1.0, 100000.0),
    "lean_theorem_count": (1.0, 100000.0),
    "lean_structure_count": (1.0, 100000.0),
    "lean_submodule_count": (1.0, 100000.0),
    "lean_total_declarations": (1.0, 100000.0),
    "run_all_script_count": (1.0, 100000.0),
    # lake build-job count for the boundary fragment — a build-output
    # scan, not a hyperparameter, so the observed integer would be C2.
    # Domain-necessary: a built Lean project emits >= 1 lake job, finite.
    "lean_lake_jobs_total": (1.0, 100000.0),
    # Shipped BTAI/adversarial worked-run observables
    # (scripts/simulate_btai.py, scripts/simulate_adversarial.py).
    # STRUCTURAL-SOURCE pins (== the H grid definitions) for the
    # grid/count/budget VARs — genuine drift detectors,
    # not C2 observed-value bounds. The pure empirical observables (KL,
    # exponent, empirical Lipschitz, max bound ratio) are deliberately NOT
    # range-pinned here (pinning to the run's own output would be the C2
    # defect); their discriminating gate is the independent recomputation +
    # negative control in tests/test_simulate_btai_adversarial.py.
    "adversarial_epsilon_grid_points": (
        float(len(H.ADVERSARIAL_EPSILON_GRID)),
        float(len(H.ADVERSARIAL_EPSILON_GRID)),
    ),
    "adversarial_lambda_grid_points": (
        float(len(H.ADVERSARIAL_LAMBDA_GRID)),
        float(len(H.ADVERSARIAL_LAMBDA_GRID)),
    ),
    "adversarial_adversary_classes": (3.0, 3.0),
    "adversarial_num_scenarios": (
        float(len(H.ADVERSARIAL_EPSILON_GRID) * len(H.ADVERSARIAL_LAMBDA_GRID) * 3),
        float(len(H.ADVERSARIAL_EPSILON_GRID) * len(H.ADVERSARIAL_LAMBDA_GRID) * 3),
    ),
    # A fraction is necessarily in [0, 1] (domain-necessary, math-necessary).
    "adversarial_bound_holds_fraction": (0.0, 1.0),
    "btai_num_budgets": (float(len(H.BTAI_DEFAULT_BUDGETS)), float(len(H.BTAI_DEFAULT_BUDGETS))),
    "btai_mcts_max_budget": (float(max(H.BTAI_DEFAULT_BUDGETS)), float(max(H.BTAI_DEFAULT_BUDGETS))),
    "btai_mcts_min_budget": (float(min(H.BTAI_DEFAULT_BUDGETS)), float(min(H.BTAI_DEFAULT_BUDGETS))),
    # Total correlation on two binary streams is necessarily in
    # [0, 2 ln 2] ≈ [0, 1.386] (sum of two binary marginal entropies).
    "btai_total_correlation_at_max_budget": (0.0, 1.4),
}

REQUIRED_VARIABLES = merge_required_variables(ANALYTICAL_VARIABLE_RANGES, GATE_SPECIFIC_RANGES)

# Pass-13 R1 — splice in the registry-derived structural-source pins
# (theorem_registry_count / theorem_status_*_count / theorem_proved_*_count).
# Computed live from labels.yaml so the gate tracks the registry source
# of truth, not a frozen integer.
REQUIRED_VARIABLES.update(registry_count_gates())

PNG_HEADER = b"\x89PNG\r\n\x1a\n"
MIN_FIGURE_WIDTH = 600
MIN_FIGURE_HEIGHT = 300
MIN_FIGURE_METADATA_SCHEMA_VERSION = 2
MIN_TITLE_FONT_SIZE = 14.0
MIN_AXIS_FONT_SIZE = 12.0
MIN_TICK_FONT_SIZE = 12.0
MIN_LEGEND_FONT_SIZE = 10.0
MIN_ANNOTATION_FONT_SIZE = 8.0
VALID_UNCERTAINTY_SEMANTICS = {
    "deterministic_grid",
    "canonical_seed",
    "replicate_envelope",
    "confidence_interval",
    "analytical_schematic",
}
