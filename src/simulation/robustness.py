"""Reviewer-facing robustness, ablation, and replicate summaries.

Import from this module only — domain splits live in ``robustness_*``
submodules (see ``docs/_audit/ISA_20260525_robustness_cluster.md``).
``scripts/simulate_robustness.py`` remains a thin orchestrator; every row
is derived from real pymdp per-stream policy posteriors plus the
analytical coupling/decomposition layer.
"""

from __future__ import annotations

from .robustness_controls import (
    run_coupling_ablation,
    run_marginal_null_control,
    summarize_coupling_ablation_rows,
    summarize_marginal_null_control_rows,
)
from .robustness_interaction import (
    run_interaction_robustness_suite,
    summarize_interaction_robustness_rows,
)
from .robustness_one_axis import run_robustness_suite, summarize_robustness_rows
from .robustness_replicates import (
    long_horizon_replicate_record,
    long_horizon_seed_diagnostic,
    long_horizon_seed_diagnostics,
    long_horizon_tc_envelope,
    long_horizon_threshold_pass_rates,
    long_horizon_threshold_sensitivity,
    long_horizon_threshold_sensitivity_summary,
    run_long_horizon_replicates,
    summarize_long_horizon_replicates,
)
from .robustness_scenarios import (
    CouplingAblationRow,
    InteractionRobustnessRow,
    InteractionRobustnessScenario,
    InteractionRobustnessSummary,
    LongHorizonReplicateRecord,
    LongHorizonSeedDiagnostic,
    LongHorizonThresholdSensitivityRow,
    MarginalNullControlRow,
    RobustnessRow,
    RobustnessScenario,
    RobustnessScenarioSummary,
    coupling_ablation_spec,
    interaction_robustness_scenarios,
    robustness_scenarios,
)
from .robustness_stats import wilson_score_interval

__all__ = [
    "CouplingAblationRow",
    "InteractionRobustnessRow",
    "InteractionRobustnessScenario",
    "InteractionRobustnessSummary",
    "LongHorizonReplicateRecord",
    "LongHorizonSeedDiagnostic",
    "LongHorizonThresholdSensitivityRow",
    "MarginalNullControlRow",
    "RobustnessRow",
    "RobustnessScenario",
    "RobustnessScenarioSummary",
    "coupling_ablation_spec",
    "interaction_robustness_scenarios",
    "long_horizon_replicate_record",
    "long_horizon_seed_diagnostic",
    "long_horizon_seed_diagnostics",
    "long_horizon_threshold_pass_rates",
    "long_horizon_threshold_sensitivity",
    "long_horizon_threshold_sensitivity_summary",
    "long_horizon_tc_envelope",
    "robustness_scenarios",
    "run_coupling_ablation",
    "run_interaction_robustness_suite",
    "run_long_horizon_replicates",
    "run_marginal_null_control",
    "run_robustness_suite",
    "summarize_coupling_ablation_rows",
    "summarize_interaction_robustness_rows",
    "summarize_long_horizon_replicates",
    "summarize_marginal_null_control_rows",
    "summarize_robustness_rows",
    "wilson_score_interval",
]
