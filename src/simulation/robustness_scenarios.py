"""Robustness scenario types and builders — stable import path."""

from __future__ import annotations

from .robustness_scenario_builders import (
    _fmt_float,
    _product_of_marginals,
    _spec_for_scenario,
    _spec_for_variant,
    coupling_ablation_spec,
    interaction_robustness_scenarios,
    robustness_scenarios,
)
from .robustness_types import (
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
)

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
    "_fmt_float",
    "_product_of_marginals",
    "_spec_for_scenario",
    "_spec_for_variant",
    "coupling_ablation_spec",
    "interaction_robustness_scenarios",
    "robustness_scenarios",
]
