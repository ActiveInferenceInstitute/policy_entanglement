"""Frozen dataclasses for robustness, ablation, and replicate sidecars."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RobustnessScenario:
    """One one-axis-at-a-time stress-test configuration."""

    scenario_id: str
    axis: str
    level: str
    observations: tuple[int, ...]
    gamma: float
    preference_strength: float
    coupling_scale: float


@dataclass(frozen=True)
class RobustnessRow:
    """One λ row from the robustness stress suite."""

    scenario_id: str
    axis: str
    level: str
    observations: tuple[int, ...]
    gamma: float
    preference_strength: float
    coupling_scale: float
    lam: float
    total_correlation: float
    joint_entropy: float
    marginal_entropy_sum: float
    coupling_term: float
    aligned_mass: float
    decomposition_lhs: float
    decomposition_rhs: float
    decomposition_residual: float


@dataclass(frozen=True)
class RobustnessScenarioSummary:
    """Per-scenario extrema and half-saturation summary."""

    scenario_id: str
    axis: str
    level: str
    tc_max: float
    tc_final: float
    lambda_half_saturation: float | None
    residual_max: float
    monotone_tc: bool


@dataclass(frozen=True)
class InteractionRobustnessScenario:
    """One targeted two-axis stress-test configuration."""

    scenario_id: str
    family: str
    level_a: str
    level_b: str
    observations: tuple[int, ...]
    gamma: float
    preference_strength: float
    coupling_scale: float
    variant: str = "aligned"


@dataclass(frozen=True)
class InteractionRobustnessRow:
    """One λ row from the appendix-only two-axis stress suite."""

    family: str
    scenario_id: str
    level_a: str
    level_b: str
    observations: tuple[int, ...]
    gamma: float
    preference_strength: float
    coupling_scale: float
    variant: str
    lam: float
    total_correlation: float
    joint_entropy: float
    marginal_entropy_sum: float
    coupling_term: float
    aligned_mass: float
    decomposition_lhs: float
    decomposition_rhs: float
    decomposition_residual: float


@dataclass(frozen=True)
class InteractionRobustnessSummary:
    """Per-scenario extrema for the two-axis stress suite."""

    family: str
    scenario_id: str
    level_a: str
    level_b: str
    tc_max: float
    tc_final: float
    residual_max: float
    monotone_tc: bool


@dataclass(frozen=True)
class CouplingAblationRow:
    """One λ row from the fixed coupling-ablation suite."""

    variant: str
    lam: float
    total_correlation: float
    joint_entropy: float
    marginal_entropy_sum: float
    coupling_term: float
    aligned_mass: float
    decomposition_lhs: float
    decomposition_rhs: float
    decomposition_residual: float


@dataclass(frozen=True)
class LongHorizonReplicateRecord:
    """Scalar summary for one long-horizon replicate seed."""

    seed: int
    habit_accumulation: bool
    tc_initial: float
    tc_final: float
    tc_mean: float
    tc_max: float
    tail_kl_window_max: float
    adjacent_kl_max: float


@dataclass(frozen=True)
class LongHorizonSeedDiagnostic:
    """Per-seed diagnostic row for long-horizon replicate interpretation."""

    seed: int
    habit_accumulation: bool
    tc_final: float
    tc_max: float
    tail_kl_window_max: float
    adjacent_kl_max: float
    margin_to_tolerance: float
    failure_mode: str


@dataclass(frozen=True)
class LongHorizonThresholdSensitivityRow:
    """Pass-rate sensitivity at one tail-window KL threshold."""

    threshold: float
    pass_rate: float
    pass_count: int
    fail_count: int
    ci_low: float
    ci_high: float


@dataclass(frozen=True)
class MarginalNullControlRow:
    """One fixed-marginal independence-control row.

    ``null_total_correlation`` is computed after replacing the
    entangled joint posterior with the product of its own marginals.
    That preserves each per-stream posterior while removing
    cross-stream dependence, so it is a compact negative control for
    the total-correlation signal.
    """

    lam: float
    original_total_correlation: float
    null_total_correlation: float
    original_aligned_mass: float
    null_aligned_mass: float
    tc_removed: float
    aligned_mass_shift: float


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
]
