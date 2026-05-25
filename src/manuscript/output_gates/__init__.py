"""Output artifact validation gates for the Policy Entanglement project."""

from __future__ import annotations

import sys

from manuscript.output_gates.artifact_validators import validate_figures, validate_variables
from manuscript.output_gates.constants import (
    MIN_ANNOTATION_FONT_SIZE,
    MIN_AXIS_FONT_SIZE,
    MIN_FIGURE_HEIGHT,
    MIN_FIGURE_METADATA_SCHEMA_VERSION,
    MIN_FIGURE_WIDTH,
    MIN_LEGEND_FONT_SIZE,
    MIN_TICK_FONT_SIZE,
    MIN_TITLE_FONT_SIZE,
    OPTIONAL_FIGURES,
    OUTPUT_DIR,
    PNG_HEADER,
    PROJECT_ROOT,
    REQUIRED_FIGURES,
    REQUIRED_VARIABLES,
    SRC_DIR,
    registry_count_gates,
)
from manuscript.output_gates.pymdp_validators import (
    validate_coupling_ablation,
    validate_free_energy_bundle,
    validate_interaction_robustness,
    validate_long_horizon,
    validate_long_horizon_replicates,
    validate_long_horizon_seed_diagnostics,
    validate_long_horizon_threshold_sensitivity,
    validate_marginal_null_control,
    validate_multi_k_sweep,
    validate_revertibility,
    validate_robustness_suite,
    validate_run_log,
    validate_sweep,
)
from manuscript.stale_patterns import STALE_FIGURE_REFERENCE_PATTERNS


def _registry_structural_count_gates():
    return registry_count_gates()


def main() -> int:
    total = 0
    total += validate_figures()
    total += validate_variables()
    total += validate_sweep()
    total += validate_free_energy_bundle()
    total += validate_multi_k_sweep()
    total += validate_long_horizon()
    total += validate_revertibility()
    total += validate_robustness_suite()
    total += validate_coupling_ablation()
    total += validate_marginal_null_control()
    total += validate_interaction_robustness()
    total += validate_long_horizon_replicates()
    total += validate_long_horizon_seed_diagnostics()
    total += validate_long_horizon_threshold_sensitivity()
    total += validate_run_log()
    print()
    if total == 0:
        print("All output validations passed.")
        return 0
    print(f"FAILED: {total} issue(s)", file=sys.stderr)
    return 1


__all__ = [
    "MIN_ANNOTATION_FONT_SIZE",
    "MIN_AXIS_FONT_SIZE",
    "MIN_FIGURE_HEIGHT",
    "MIN_FIGURE_METADATA_SCHEMA_VERSION",
    "MIN_FIGURE_WIDTH",
    "MIN_LEGEND_FONT_SIZE",
    "MIN_TICK_FONT_SIZE",
    "MIN_TITLE_FONT_SIZE",
    "OPTIONAL_FIGURES",
    "OUTPUT_DIR",
    "PNG_HEADER",
    "PROJECT_ROOT",
    "REQUIRED_FIGURES",
    "REQUIRED_VARIABLES",
    "SRC_DIR",
    "STALE_FIGURE_REFERENCE_PATTERNS",
    "main",
    "validate_coupling_ablation",
    "validate_figures",
    "validate_free_energy_bundle",
    "validate_interaction_robustness",
    "validate_long_horizon",
    "validate_long_horizon_replicates",
    "validate_long_horizon_seed_diagnostics",
    "validate_long_horizon_threshold_sensitivity",
    "validate_marginal_null_control",
    "validate_multi_k_sweep",
    "validate_revertibility",
    "validate_robustness_suite",
    "validate_run_log",
    "validate_sweep",
    "validate_variables",
]
