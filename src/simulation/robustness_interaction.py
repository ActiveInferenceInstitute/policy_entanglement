"""Two-axis interaction robustness suite runners and summarizers."""

from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np
from numpy.typing import NDArray

from . import hyperparameters as H  # noqa: N812
from .metrics import aligned_hypercube_mass as _aligned_mass
from .robustness_core import rows_for_spec
from .robustness_scenarios import (
    InteractionRobustnessRow,
    InteractionRobustnessScenario,
    InteractionRobustnessSummary,
    _spec_for_variant,
    interaction_robustness_scenarios,
)

FloatGrid = Sequence[float] | NDArray[np.float64]


def run_interaction_robustness_suite(
    lams: FloatGrid | None = None,
    *,
    progress_callback: Callable[[int, int, InteractionRobustnessScenario], None] | None = None,
) -> list[InteractionRobustnessRow]:
    """Run the targeted two-axis robustness suite."""

    grid = [float(x) for x in (H.ROBUSTNESS_SWEEP_LAMBDAS.values() if lams is None else lams)]
    scenarios = interaction_robustness_scenarios()
    rows: list[InteractionRobustnessRow] = []
    for idx, scenario in enumerate(scenarios, start=1):
        if progress_callback is not None:
            progress_callback(idx, len(scenarios), scenario)
        spec = _spec_for_variant(
            variant=scenario.variant,
            coupling_scale=scenario.coupling_scale,
            gamma=scenario.gamma,
            preference_strength=scenario.preference_strength,
        )
        for lam, q, tc, joint_h, marg_h, coupling_term, lhs, rhs, residual in rows_for_spec(
            spec,
            scenario.observations,
            grid,
        ):
            rows.append(
                InteractionRobustnessRow(
                    family=scenario.family,
                    scenario_id=scenario.scenario_id,
                    level_a=scenario.level_a,
                    level_b=scenario.level_b,
                    observations=scenario.observations,
                    gamma=scenario.gamma,
                    preference_strength=scenario.preference_strength,
                    coupling_scale=scenario.coupling_scale,
                    variant=scenario.variant,
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


def summarize_interaction_robustness_rows(
    rows: Sequence[InteractionRobustnessRow],
) -> tuple[list[InteractionRobustnessSummary], dict[str, float]]:
    """Per-scenario summaries plus flat variables for two-axis stress tests."""

    if not rows:
        raise ValueError("rows must be non-empty")
    scenario_ids = sorted({r.scenario_id for r in rows})
    summaries: list[InteractionRobustnessSummary] = []
    for scenario_id in scenario_ids:
        group = sorted((r for r in rows if r.scenario_id == scenario_id), key=lambda r: r.lam)
        tcs = [r.total_correlation for r in group]
        summaries.append(
            InteractionRobustnessSummary(
                family=group[0].family,
                scenario_id=scenario_id,
                level_a=group[0].level_a,
                level_b=group[0].level_b,
                tc_max=float(max(tcs)),
                tc_final=float(tcs[-1]),
                residual_max=float(max(r.decomposition_residual for r in group)),
                monotone_tc=all(tcs[i + 1] + 1e-10 >= tcs[i] for i in range(len(tcs) - 1)),
            )
        )
    null_variant_rows = [r for r in rows if r.family == "coupling_variant_x_coupling_scale" and r.variant == "null"]
    flat = {
        "interaction_robustness_family_count": float(len({s.family for s in summaries})),
        "interaction_robustness_scenario_count": float(len(summaries)),
        "interaction_robustness_row_count": float(len(rows)),
        "interaction_robustness_tc_max": float(max(r.total_correlation for r in rows)),
        "interaction_robustness_decomposition_residual_max": float(max(r.decomposition_residual for r in rows)),
        "interaction_robustness_monotone_scenario_count": float(sum(1 for s in summaries if s.monotone_tc)),
        "interaction_robustness_null_variant_tc_max": float(
            max((r.total_correlation for r in null_variant_rows), default=0.0)
        ),
    }
    for family in sorted({s.family for s in summaries}):
        family_summaries = [s for s in summaries if s.family == family]
        flat[f"interaction_{family}_scenario_count"] = float(len(family_summaries))
        flat[f"interaction_{family}_tc_max"] = float(max(s.tc_max for s in family_summaries))
    return summaries, flat
