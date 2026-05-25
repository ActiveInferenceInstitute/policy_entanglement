"""Robustness scenario dataclasses and ensemble builders."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from . import hyperparameters as H  # noqa: N812
from .builders import make_ising_ensemble
from .specs import CoupledEnsembleSpec

ArrayF = NDArray[np.float64]


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


def _fmt_float(value: float) -> str:
    """Stable identifier fragment for configured floating values."""

    return f"{float(value):g}".replace("-", "m").replace(".", "_")


def _product_of_marginals(marginals: Sequence[ArrayF]) -> ArrayF:
    """Outer product of a finite marginal PMF family."""

    if not marginals:
        raise ValueError("marginals must be non-empty")
    out = np.asarray(marginals[0], dtype=np.float64)
    for marginal in marginals[1:]:
        out = np.multiply.outer(out, np.asarray(marginal, dtype=np.float64))
    total = float(out.sum())
    if total <= 0.0:
        raise ValueError("product of marginals has non-positive mass")
    return (out / total).astype(np.float64)


def robustness_scenarios() -> tuple[RobustnessScenario, ...]:
    """Configured one-axis-at-a-time robustness scenarios.

    The suite deliberately avoids a full Cartesian grid.  Each row
    perturbs one axis away from the canonical pymdp sweep while holding
    the other axes at their baseline values.
    """

    baseline_obs = tuple(int(x) for x in H.PYMDP_SWEEP_OBSERVATIONS)
    baseline_gamma = float(H.PYMDP_ENSEMBLE_GAMMA)
    baseline_pref = 1.0
    baseline_scale = float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA)
    out: list[RobustnessScenario] = []
    for obs in H.ROBUSTNESS_OBSERVATION_CONTEXTS:
        obs_tuple = tuple(int(x) for x in obs)
        out.append(
            RobustnessScenario(
                scenario_id=f"obs_{''.join(str(x) for x in obs_tuple)}",
                axis="observation",
                level=f"({obs_tuple[0]},{obs_tuple[1]})",
                observations=obs_tuple,
                gamma=baseline_gamma,
                preference_strength=baseline_pref,
                coupling_scale=baseline_scale,
            )
        )
    for gamma in H.ROBUSTNESS_GAMMAS:
        out.append(
            RobustnessScenario(
                scenario_id=f"gamma_{_fmt_float(float(gamma))}",
                axis="gamma",
                level=f"{float(gamma):g}",
                observations=baseline_obs,
                gamma=float(gamma),
                preference_strength=baseline_pref,
                coupling_scale=baseline_scale,
            )
        )
    for pref in H.ROBUSTNESS_PREFERENCE_STRENGTHS:
        out.append(
            RobustnessScenario(
                scenario_id=f"pref_{_fmt_float(float(pref))}",
                axis="preference",
                level=f"{float(pref):g}",
                observations=baseline_obs,
                gamma=baseline_gamma,
                preference_strength=float(pref),
                coupling_scale=baseline_scale,
            )
        )
    for scale in H.ROBUSTNESS_COUPLING_SCALES:
        out.append(
            RobustnessScenario(
                scenario_id=f"coupling_{_fmt_float(float(scale))}",
                axis="coupling_scale",
                level=f"{float(scale):g}",
                observations=baseline_obs,
                gamma=baseline_gamma,
                preference_strength=baseline_pref,
                coupling_scale=float(scale),
            )
        )
    return tuple(out)


def _spec_for_scenario(scenario: RobustnessScenario) -> CoupledEnsembleSpec:
    """Build the K=2 Ising ensemble for a robustness scenario."""

    return make_ising_ensemble(
        coupling_amplitude=float(scenario.coupling_scale),
        preference_strength=float(scenario.preference_strength),
        num_streams=int(H.PYMDP_ENSEMBLE_K),
        gamma=float(scenario.gamma),
    )


def _make_heterogeneous_kc(
    scale: float,
    gamma: float,
    preference_strength: float = 1.0,
) -> CoupledEnsembleSpec:
    base = make_ising_ensemble(
        coupling_amplitude=scale,
        preference_strength=float(preference_strength),
        num_streams=int(H.PYMDP_ENSEMBLE_K),
        gamma=float(gamma),
    )
    kc = np.asarray(H.COUPLING_ABLATION_KC_MATRIX, dtype=np.float64)
    spec = CoupledEnsembleSpec(
        streams=base.streams,
        coupling_j=base.coupling_j,
        coupling_kc=kc,
        gamma=base.gamma,
    )
    spec.validate()
    return spec


def _make_ising(
    coupling_amplitude: float,
    *,
    preference_strength: float,
    gamma: float,
) -> CoupledEnsembleSpec:
    return make_ising_ensemble(
        coupling_amplitude=float(coupling_amplitude),
        preference_strength=float(preference_strength),
        num_streams=int(H.PYMDP_ENSEMBLE_K),
        gamma=float(gamma),
    )


_VARIANT_BUILDERS: dict[str, Callable[[float, float, float], CoupledEnsembleSpec]] = {
    "aligned": lambda scale, gamma, pref: _make_ising(scale, preference_strength=pref, gamma=gamma),
    "null": lambda scale, gamma, pref: _make_ising(0.0, preference_strength=pref, gamma=gamma),
    "anti_aligned": lambda scale, gamma, pref: _make_ising(-scale, preference_strength=pref, gamma=gamma),
    "heterogeneous_kc": _make_heterogeneous_kc,
}


def _spec_for_variant(
    *,
    variant: str,
    coupling_scale: float,
    gamma: float,
    preference_strength: float = 1.0,
) -> CoupledEnsembleSpec:
    """Build a K=2 Ising ensemble for a named coupling variant."""

    builder = _VARIANT_BUILDERS.get(str(variant))
    if builder is None:
        raise ValueError(f"unknown coupling ablation variant: {variant!r}")
    return builder(float(coupling_scale), float(gamma), float(preference_strength))


def coupling_ablation_spec(variant: str) -> CoupledEnsembleSpec:
    """Canonical K=2 ablation spec for one named variant."""

    return _spec_for_variant(
        variant=variant,
        coupling_scale=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
    )
