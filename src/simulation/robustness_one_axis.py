"""One-axis-at-a-time robustness suite runners and summarizers."""

from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np
from numpy.typing import NDArray

from . import hyperparameters as H  # noqa: N812
from .metrics import aligned_hypercube_mass as _aligned_mass
from .metrics import half_saturation_lambda as _half_saturation
from .robustness_core import rows_for_spec
from .robustness_scenarios import (
    RobustnessRow,
    RobustnessScenario,
    RobustnessScenarioSummary,
    _spec_for_scenario,
    robustness_scenarios,
)

FloatGrid = Sequence[float] | NDArray[np.float64]


def run_robustness_suite(
    lams: FloatGrid | None = None,
    *,
    progress_callback: Callable[[int, int, RobustnessScenario], None] | None = None,
) -> list[RobustnessRow]:
    """Run the configured one-axis-at-a-time robustness suite."""

    grid = [float(x) for x in (H.ROBUSTNESS_SWEEP_LAMBDAS.values() if lams is None else lams)]
    scenarios = robustness_scenarios()
    rows: list[RobustnessRow] = []
    for idx, scenario in enumerate(scenarios, start=1):
        if progress_callback is not None:
            progress_callback(idx, len(scenarios), scenario)
        spec = _spec_for_scenario(scenario)
        for lam, q, tc, joint_h, marg_h, coupling_term, lhs, rhs, residual in rows_for_spec(
            spec,
            scenario.observations,
            grid,
        ):
            rows.append(
                RobustnessRow(
                    scenario_id=scenario.scenario_id,
                    axis=scenario.axis,
                    level=scenario.level,
                    observations=scenario.observations,
                    gamma=scenario.gamma,
                    preference_strength=scenario.preference_strength,
                    coupling_scale=scenario.coupling_scale,
                    lam=lam,
                    total_correlation=tc,
                    joint_entropy=joint_h,
                    marginal_entropy_sum=marg_h,
                    coupling_term=coupling_term,
                    aligned_mass=_aligned_mass(q),
                    decomposition_lhs=lhs,
                    decomposition_rhs=rhs,
                    decomposition_residual=residual,
                )
            )
    return rows


def summarize_robustness_rows(
    rows: Sequence[RobustnessRow],
) -> tuple[list[RobustnessScenarioSummary], dict[str, float]]:
    """Return per-scenario summaries plus flat manuscript variables."""

    if not rows:
        raise ValueError("rows must be non-empty")
    scenario_ids = sorted({r.scenario_id for r in rows})
    summaries: list[RobustnessScenarioSummary] = []
    for scenario_id in scenario_ids:
        group = sorted((r for r in rows if r.scenario_id == scenario_id), key=lambda r: r.lam)
        lams = [r.lam for r in group]
        tcs = [r.total_correlation for r in group]
        summaries.append(
            RobustnessScenarioSummary(
                scenario_id=scenario_id,
                axis=group[0].axis,
                level=group[0].level,
                tc_max=float(max(tcs)),
                tc_final=float(tcs[-1]),
                lambda_half_saturation=_half_saturation(lams, tcs),
                residual_max=float(max(r.decomposition_residual for r in group)),
                monotone_tc=all(tcs[i + 1] + 1e-10 >= tcs[i] for i in range(len(tcs) - 1)),
            )
        )
    finite_halves = [s.lambda_half_saturation for s in summaries if s.lambda_half_saturation is not None]
    null_rows = [r for r in rows if r.axis == "coupling_scale" and abs(r.coupling_scale) <= 1e-12]
    flat = {
        "robustness_scenario_count": float(len(summaries)),
        "robustness_row_count": float(len(rows)),
        "robustness_axis_count": float(len({s.axis for s in summaries})),
        "robustness_tc_max": float(max(r.total_correlation for r in rows)),
        "robustness_tc_mean_final": float(np.mean([s.tc_final for s in summaries])),
        "robustness_decomposition_residual_max": float(max(r.decomposition_residual for r in rows)),
        "robustness_monotone_scenario_count": float(sum(1 for s in summaries if s.monotone_tc)),
        "robustness_null_coupling_tc_max": float(max((r.total_correlation for r in null_rows), default=0.0)),
        "robustness_half_saturation_min": float(min(finite_halves, default=0.0)),
        "robustness_half_saturation_mean": float(np.mean(finite_halves)) if finite_halves else 0.0,
        "robustness_half_saturation_max": float(max(finite_halves, default=0.0)),
    }
    return summaries, flat
