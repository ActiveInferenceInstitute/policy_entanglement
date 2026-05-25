"""Reviewer-facing robustness, ablation, and replicate summaries.

The helpers in this module keep the empirical stress tests in ``src/``
so ``scripts/simulate_robustness.py`` remains a thin orchestrator.
Every row is derived from real pymdp per-stream policy posteriors plus
the analytical coupling/decomposition layer; no mocks or synthetic
posteriors enter the publication path.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np
from numpy.typing import NDArray

from lean.coupling import entangled_posterior
from lean.decomposition import (
    entanglement_decomposition_rhs,
    free_energy_against_entangled_prior,
)
from lean.free_energy import shannon_entropy, total_correlation
from lean.joint_dist import joint_marginals

from . import hyperparameters as H  # noqa: N812 — H = hyperparameters (manuscript convention).
from .inference import per_stream_policy_posterior
from .long_horizon import LongHorizonResult, long_horizon_rollout
from .metrics import aligned_hypercube_mass as _aligned_mass
from .metrics import half_saturation_lambda as _half_saturation
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
    _fmt_float,
    _product_of_marginals,
    _spec_for_scenario,
    _spec_for_variant,
    coupling_ablation_spec,
    robustness_scenarios,
)
from .robustness_stats import _z_95_two_sided, wilson_score_interval
from .specs import CoupledEnsembleSpec

ArrayF = NDArray[np.float64]
FloatGrid = Sequence[float] | NDArray[np.float64]


def _rows_for_spec(
    spec: CoupledEnsembleSpec,
    observations: Sequence[int],
    lams: Sequence[float],
) -> list[tuple[float, ArrayF, float, float, float, float, float, float, float]]:
    """Shared λ-loop for robustness and ablation rows.

    Returns tuples of ``(λ, q, TC, H(q), sum H(q^k), λ<J>, lhs, rhs,
    residual)``.  The per-stream pymdp posterior is computed once per
    spec/observation pair; the decomposition uses zero per-stream G
    because pymdp has already baked EFE into that posterior.
    """

    spec.validate()
    mf = per_stream_policy_posterior(spec, observations)
    zero_g = [np.zeros_like(m, dtype=np.float64) for m in mf]
    out: list[tuple[float, ArrayF, float, float, float, float, float, float, float]] = []
    for lam_value in lams:
        lam = float(lam_value)
        q = entangled_posterior(
            mf_prior=mf,
            per_stream_G=zero_g,
            coupling_j=spec.coupling_j,
            coupling_kc=spec.coupling_kc,
            gamma=spec.gamma,
            lam=lam,
        )
        margs = joint_marginals(q)
        joint_entropy = shannon_entropy(q.reshape(-1))
        marginal_entropy_sum = float(sum(shannon_entropy(m) for m in margs))
        coupling_term = float(lam) * float(np.sum(q * spec.coupling_j))
        lhs = free_energy_against_entangled_prior(
            q,
            mf,
            zero_g,
            spec.coupling_j,
            spec.coupling_kc,
            spec.gamma,
            lam,
        )
        rhs = entanglement_decomposition_rhs(
            q,
            mf,
            zero_g,
            spec.coupling_j,
            spec.coupling_kc,
            spec.gamma,
            lam,
        ).total
        out.append(
            (
                lam,
                np.asarray(q, dtype=np.float64),
                float(total_correlation(q)),
                float(joint_entropy),
                float(marginal_entropy_sum),
                float(coupling_term),
                float(lhs),
                float(rhs),
                float(abs(lhs - rhs)),
            )
        )
    return out


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
        for lam, q, tc, joint_h, marg_h, coupling_term, lhs, rhs, residual in _rows_for_spec(
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
        for lam, q, tc, joint_h, marg_h, coupling_term, lhs, rhs, residual in _rows_for_spec(
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


def run_coupling_ablation(lams: FloatGrid | None = None) -> list[CouplingAblationRow]:
    """Run the four configured coupling-ablation variants."""

    grid = [float(x) for x in (H.ROBUSTNESS_SWEEP_LAMBDAS.values() if lams is None else lams)]
    rows: list[CouplingAblationRow] = []
    observations = tuple(int(x) for x in H.PYMDP_SWEEP_OBSERVATIONS)
    for variant in H.COUPLING_ABLATION_VARIANTS:
        spec = coupling_ablation_spec(variant)
        for lam, q, tc, joint_h, marg_h, coupling_term, lhs, rhs, residual in _rows_for_spec(
            spec,
            observations,
            grid,
        ):
            rows.append(
                CouplingAblationRow(
                    variant=variant,
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


def run_marginal_null_control(lams: FloatGrid | None = None) -> list[MarginalNullControlRow]:
    """Run a fixed-marginal independence control for the canonical sweep."""

    grid = [float(x) for x in (H.ROBUSTNESS_SWEEP_LAMBDAS.values() if lams is None else lams)]
    spec = coupling_ablation_spec("aligned")
    observations = tuple(int(x) for x in H.PYMDP_SWEEP_OBSERVATIONS)
    rows: list[MarginalNullControlRow] = []
    for lam, q, tc, _joint_h, _marg_h, _coupling_term, _lhs, _rhs, _residual in _rows_for_spec(
        spec,
        observations,
        grid,
    ):
        null_q = _product_of_marginals(joint_marginals(q))
        null_tc = float(total_correlation(null_q))
        original_mass = _aligned_mass(q)
        null_mass = _aligned_mass(null_q)
        rows.append(
            MarginalNullControlRow(
                lam=float(lam),
                original_total_correlation=float(tc),
                null_total_correlation=null_tc,
                original_aligned_mass=original_mass,
                null_aligned_mass=null_mass,
                tc_removed=float(tc - null_tc),
                aligned_mass_shift=float(original_mass - null_mass),
            )
        )
    return rows


def summarize_coupling_ablation_rows(rows: Sequence[CouplingAblationRow]) -> dict[str, float]:
    """Flat manuscript-variable summary for the ablation suite."""

    if not rows:
        raise ValueError("rows must be non-empty")
    variants = sorted({r.variant for r in rows})
    lambda_zero_rows = [r for r in rows if abs(r.lam) <= 1e-12]
    final_rows = [max((r for r in rows if r.variant == variant), key=lambda r: r.lam) for variant in variants]
    flat: dict[str, float] = {
        "coupling_ablation_variant_count": float(len(variants)),
        "coupling_ablation_row_count": float(len(rows)),
        "coupling_ablation_decomposition_residual_max": float(max(r.decomposition_residual for r in rows)),
        "coupling_ablation_lambda_zero_tc_max": float(
            max((r.total_correlation for r in lambda_zero_rows), default=0.0)
        ),
        "coupling_ablation_aligned_mass_shift": float(
            max(r.aligned_mass for r in final_rows) - min(r.aligned_mass for r in final_rows)
        ),
    }
    for variant in variants:
        group = [r for r in rows if r.variant == variant]
        key = variant.replace("-", "_")
        flat[f"coupling_ablation_{key}_tc_max"] = float(max(r.total_correlation for r in group))
        flat[f"coupling_ablation_{key}_aligned_mass_at_lambda_max"] = float(
            max(group, key=lambda r: r.lam).aligned_mass
        )
    return flat


def summarize_marginal_null_control_rows(rows: Sequence[MarginalNullControlRow]) -> dict[str, float]:
    """Flat manuscript-variable summary for the fixed-marginal null control."""

    if not rows:
        raise ValueError("rows must be non-empty")
    return {
        "robustness_null_control_row_count": float(len(rows)),
        "robustness_null_control_max_tc": float(max(r.null_total_correlation for r in rows)),
        "robustness_null_control_tc_removed_max": float(max(r.tc_removed for r in rows)),
        "robustness_null_control_aligned_mass_shift_max": float(max(abs(r.aligned_mass_shift) for r in rows)),
        "robustness_null_control_original_tc_max": float(max(r.original_total_correlation for r in rows)),
        # RedTeam 2026-05-19 C3 — the DISCRIMINATING metric. Over rows
        # that actually carry coupling (original_tc > 1e-6), the fraction
        # of multi-information the null control removes must be ≈ 1; the
        # min across them is gated to [1−1e-6, 1+1e-6]. A control that
        # leaves coupling (mis-marginalised) yields a fraction < 1; if no
        # row carries coupling the metric is 0.0 → also fails (the
        # control never exercised what it claims to neutralise). This is
        # the quantity `tc_removed_max (0,inf)` failed to constrain.
        "robustness_null_control_tc_removed_fraction_min": float(
            min(
                (r.tc_removed / r.original_total_correlation for r in rows if r.original_total_correlation > 1e-6),
                default=0.0,
            )
        ),
    }


def run_long_horizon_replicates(
    seeds: Sequence[int] | None = None,
    *,
    progress_callback: Callable[[int, int, int], None] | None = None,
) -> list[LongHorizonResult]:
    """Run long-horizon replicate sidecars for configured seeds."""

    seed_values = [int(seed) for seed in (H.LONG_HORIZON_REPLICATE_SEEDS if seeds is None else seeds)]
    results: list[LongHorizonResult] = []
    for idx, seed in enumerate(seed_values, start=1):
        if progress_callback is not None:
            progress_callback(idx, len(seed_values), seed)
        results.append(
            long_horizon_rollout(
                coupling_lambda_gen=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
                gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
                num_streams=int(H.PYMDP_ENSEMBLE_K),
                horizon=int(H.LONG_HORIZON_STEPS),
                lam=float(H.LONG_HORIZON_LAMBDA),
                seed=seed,
                tail_window=int(H.LONG_HORIZON_TAIL_WINDOW),
                steady_state_tol=float(H.LONG_HORIZON_STEADY_STATE_TOL),
            )
        )
    return results


def long_horizon_replicate_record(result: LongHorizonResult) -> LongHorizonReplicateRecord:
    """Scalar summary for one long-horizon replicate."""

    return LongHorizonReplicateRecord(
        seed=int(result.seed),
        habit_accumulation=bool(result.habit_accumulation),
        tc_initial=float(result.total_correlations[0]),
        tc_final=float(result.total_correlations[-1]),
        tc_mean=float(np.mean(result.total_correlations)),
        tc_max=float(np.max(result.total_correlations)),
        tail_kl_window_max=float(max(result.tail_kl_max_per_stream)),
        adjacent_kl_max=float(max(result.adjacent_kl_max_per_stream)),
    )


def long_horizon_seed_diagnostic(result: LongHorizonResult) -> LongHorizonSeedDiagnostic:
    """Interpret one replicate against the configured tail-window tolerance."""

    tail_kl = float(max(result.tail_kl_max_per_stream))
    steady_state_tol = float(getattr(result, "steady_state_tol", H.LONG_HORIZON_STEADY_STATE_TOL))
    margin = steady_state_tol - tail_kl
    return LongHorizonSeedDiagnostic(
        seed=int(result.seed),
        habit_accumulation=bool(result.habit_accumulation),
        tc_final=float(result.total_correlations[-1]),
        tc_max=float(np.max(result.total_correlations)),
        tail_kl_window_max=tail_kl,
        adjacent_kl_max=float(max(result.adjacent_kl_max_per_stream)),
        margin_to_tolerance=margin,
        failure_mode="passes" if result.habit_accumulation else "tail_window_kl_above_tol",
    )


def long_horizon_seed_diagnostics(results: Sequence[LongHorizonResult]) -> list[LongHorizonSeedDiagnostic]:
    """Return per-seed long-horizon diagnostic rows."""

    if not results:
        raise ValueError("results must be non-empty")
    return [long_horizon_seed_diagnostic(result) for result in results]


def long_horizon_threshold_pass_rates(
    records: Sequence[LongHorizonSeedDiagnostic],
    thresholds: Sequence[float] | None = None,
) -> dict[str, float]:
    """Pass-rate sensitivity under alternative tail-window KL thresholds."""

    rows = long_horizon_threshold_sensitivity(records, thresholds)
    return {f"long_horizon_replicate_pass_rate_tol_{_fmt_float(r.threshold)}": r.pass_rate for r in rows}


def long_horizon_threshold_sensitivity(
    records: Sequence[LongHorizonSeedDiagnostic],
    thresholds: Sequence[float] | None = None,
) -> list[LongHorizonThresholdSensitivityRow]:
    """Structured pass-rate sensitivity under tail-window KL thresholds."""

    if not records:
        raise ValueError("records must be non-empty")
    probes = [float(x) for x in (H.LONG_HORIZON_DIAGNOSTIC_THRESHOLDS if thresholds is None else thresholds)]
    rows: list[LongHorizonThresholdSensitivityRow] = []
    for threshold in probes:
        pass_count = int(sum(1 for r in records if r.tail_kl_window_max <= threshold))
        total = len(records)
        ci_low, ci_high = wilson_score_interval(pass_count, total)
        rows.append(
            LongHorizonThresholdSensitivityRow(
                threshold=threshold,
                pass_rate=float(pass_count / total),
                pass_count=pass_count,
                fail_count=int(total - pass_count),
                ci_low=ci_low,
                ci_high=ci_high,
            )
        )
    return rows


def long_horizon_threshold_sensitivity_summary(
    records: Sequence[LongHorizonSeedDiagnostic],
    thresholds: Sequence[float] | None = None,
) -> dict[str, float]:
    """Compact summary of pass-rate sensitivity across thresholds."""

    rows = long_horizon_threshold_sensitivity(records, thresholds)
    rates = [r.pass_rate for r in rows]
    return {
        "long_horizon_replicate_threshold_count": float(len(rows)),
        "long_horizon_replicate_threshold_pass_rate_min": float(min(rates)),
        "long_horizon_replicate_threshold_pass_rate_max": float(max(rates)),
        "long_horizon_replicate_threshold_pass_rate_range": float(max(rates) - min(rates)),
    }


def long_horizon_tc_envelope(results: Sequence[LongHorizonResult]) -> dict[str, list[float]]:
    """Quantile envelope over replicate total-correlation trajectories."""

    if not results:
        raise ValueError("results must be non-empty")
    horizon = int(results[0].T)
    for result in results:
        if int(result.T) != horizon:
            raise ValueError("all replicate results must share the same horizon")
    arr = np.stack([np.asarray(r.total_correlations, dtype=np.float64) for r in results], axis=0)
    return {
        "t": [float(x) for x in range(horizon)],
        "q25": [float(x) for x in np.quantile(arr, 0.25, axis=0)],
        "median": [float(x) for x in np.quantile(arr, 0.50, axis=0)],
        "q75": [float(x) for x in np.quantile(arr, 0.75, axis=0)],
        "min": [float(x) for x in np.min(arr, axis=0)],
        "max": [float(x) for x in np.max(arr, axis=0)],
    }


def summarize_long_horizon_replicates(
    results: Sequence[LongHorizonResult],
) -> tuple[list[LongHorizonReplicateRecord], dict[str, float]]:
    """Per-seed records plus flat manuscript-variable summary."""

    if not results:
        raise ValueError("results must be non-empty")
    records = [long_horizon_replicate_record(result) for result in results]
    diagnostics = long_horizon_seed_diagnostics(results)
    success_count = int(sum(1 for r in records if r.habit_accumulation))
    pass_rate = float(success_count / len(records))
    ci_low, ci_high = wilson_score_interval(success_count, len(records))
    finals = np.array([r.tc_final for r in records], dtype=np.float64)
    flat = {
        "long_horizon_replicate_seed_count": float(len(records)),
        "long_horizon_replicate_success_count": float(success_count),
        "long_horizon_replicate_habit_pass_rate": pass_rate,
        "long_horizon_replicate_habit_pass_rate_ci_low": ci_low,
        "long_horizon_replicate_habit_pass_rate_ci_high": ci_high,
        "long_horizon_replicate_habit_pass_rate_ci_z": _z_95_two_sided(),
        "long_horizon_replicate_tc_final_mean": float(np.mean(finals)),
        "long_horizon_replicate_tc_final_min": float(np.min(finals)),
        "long_horizon_replicate_tc_final_max": float(np.max(finals)),
        "long_horizon_replicate_tail_kl_window_max": float(max(r.tail_kl_window_max for r in records)),
        "long_horizon_replicate_adjacent_kl_max": float(max(r.adjacent_kl_max for r in records)),
        "long_horizon_replicate_failure_count": float(sum(1 for r in diagnostics if not r.habit_accumulation)),
        "long_horizon_replicate_margin_to_tol_min": float(min(r.margin_to_tolerance for r in diagnostics)),
        "long_horizon_replicate_margin_to_tol_mean": float(np.mean([r.margin_to_tolerance for r in diagnostics])),
    }
    flat.update(long_horizon_threshold_pass_rates(diagnostics))
    flat.update(long_horizon_threshold_sensitivity_summary(diagnostics))
    return records, flat


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
    "long_horizon_seed_diagnostic",
    "long_horizon_seed_diagnostics",
    "long_horizon_replicate_record",
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
