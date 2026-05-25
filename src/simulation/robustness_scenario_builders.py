"""Scenario lists and ensemble builders for robustness sidecars."""

from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np
from numpy.typing import NDArray

from . import hyperparameters as H  # noqa: N812
from .builders import make_ising_ensemble
from .robustness_types import InteractionRobustnessScenario, RobustnessScenario
from .specs import CoupledEnsembleSpec

ArrayF = NDArray[np.float64]


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


def interaction_robustness_scenarios() -> tuple[InteractionRobustnessScenario, ...]:
    """Configured targeted two-axis robustness scenarios."""

    baseline_obs = tuple(int(x) for x in H.PYMDP_SWEEP_OBSERVATIONS)
    baseline_gamma = float(H.PYMDP_ENSEMBLE_GAMMA)
    baseline_pref = 1.0
    baseline_scale = float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA)
    out: list[InteractionRobustnessScenario] = []
    for obs in H.ROBUSTNESS_OBSERVATION_CONTEXTS:
        obs_tuple = tuple(int(x) for x in obs)
        for scale in H.ROBUSTNESS_COUPLING_SCALES:
            out.append(
                InteractionRobustnessScenario(
                    scenario_id=f"obs_{''.join(str(x) for x in obs_tuple)}_x_coupling_{_fmt_float(scale)}",
                    family="observation_x_coupling_scale",
                    level_a=f"obs=({obs_tuple[0]},{obs_tuple[1]})",
                    level_b=f"scale={float(scale):g}",
                    observations=obs_tuple,
                    gamma=baseline_gamma,
                    preference_strength=baseline_pref,
                    coupling_scale=float(scale),
                )
            )
    for gamma in H.ROBUSTNESS_GAMMAS:
        for pref in H.ROBUSTNESS_PREFERENCE_STRENGTHS:
            out.append(
                InteractionRobustnessScenario(
                    scenario_id=f"gamma_{_fmt_float(gamma)}_x_pref_{_fmt_float(pref)}",
                    family="gamma_x_preference_strength",
                    level_a=f"γ={float(gamma):g}",
                    level_b=f"pref={float(pref):g}",
                    observations=baseline_obs,
                    gamma=float(gamma),
                    preference_strength=float(pref),
                    coupling_scale=baseline_scale,
                )
            )
    for variant in H.COUPLING_ABLATION_VARIANTS:
        for scale in H.ROBUSTNESS_COUPLING_SCALES:
            out.append(
                InteractionRobustnessScenario(
                    scenario_id=f"{variant}_x_coupling_{_fmt_float(scale)}",
                    family="coupling_variant_x_coupling_scale",
                    level_a=str(variant).replace("_", " "),
                    level_b=f"scale={float(scale):g}",
                    observations=baseline_obs,
                    gamma=baseline_gamma,
                    preference_strength=baseline_pref,
                    coupling_scale=float(scale),
                    variant=str(variant),
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


__all__ = [
    "_fmt_float",
    "_product_of_marginals",
    "_spec_for_scenario",
    "_spec_for_variant",
    "coupling_ablation_spec",
    "interaction_robustness_scenarios",
    "robustness_scenarios",
]
