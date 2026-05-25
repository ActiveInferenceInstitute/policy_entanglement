"""Tests for robustness, ablation, and replicate sidecar helpers."""

from __future__ import annotations

import numpy as np
import pytest

from simulation import hyperparameters as H
from simulation.agents import pymdp_available
from simulation.long_horizon import LongHorizonResult
from simulation.metrics import half_saturation_lambda as _half_saturation
from simulation.robustness import (
    InteractionRobustnessScenario,
    MarginalNullControlRow,
    RobustnessScenario,
    coupling_ablation_spec,
    interaction_robustness_scenarios,
    long_horizon_seed_diagnostics,
    long_horizon_tc_envelope,
    long_horizon_threshold_pass_rates,
    long_horizon_threshold_sensitivity,
    long_horizon_threshold_sensitivity_summary,
    robustness_scenarios,
    run_coupling_ablation,
    run_interaction_robustness_suite,
    run_marginal_null_control,
    run_robustness_suite,
    summarize_coupling_ablation_rows,
    summarize_interaction_robustness_rows,
    summarize_long_horizon_replicates,
    summarize_marginal_null_control_rows,
    summarize_robustness_rows,
    wilson_score_interval,
)


def test_robustness_scenarios_are_one_axis_at_a_time() -> None:
    scenarios = robustness_scenarios()
    expected = (
        len(H.ROBUSTNESS_OBSERVATION_CONTEXTS)
        + len(H.ROBUSTNESS_GAMMAS)
        + len(H.ROBUSTNESS_PREFERENCE_STRENGTHS)
        + len(H.ROBUSTNESS_COUPLING_SCALES)
    )
    assert len(scenarios) == expected
    assert {s.axis for s in scenarios} == {"observation", "gamma", "preference", "coupling_scale"}
    assert len({s.scenario_id for s in scenarios}) == expected


def test_interaction_robustness_scenarios_are_targeted_two_axis_families() -> None:
    scenarios = interaction_robustness_scenarios()
    expected = (
        len(H.ROBUSTNESS_OBSERVATION_CONTEXTS) * len(H.ROBUSTNESS_COUPLING_SCALES)
        + len(H.ROBUSTNESS_GAMMAS) * len(H.ROBUSTNESS_PREFERENCE_STRENGTHS)
        + len(H.COUPLING_ABLATION_VARIANTS) * len(H.ROBUSTNESS_COUPLING_SCALES)
    )
    assert len(scenarios) == expected
    assert {s.family for s in scenarios} == set(H.ROBUSTNESS_INTERACTION_FAMILIES)
    assert len({s.scenario_id for s in scenarios}) == expected


@pytest.mark.skipif(not pymdp_available(), reason="pymdp 1.0.1 not installed")
def test_run_robustness_suite_small_grid_contract() -> None:
    lams = [0.0, 1.0]
    rows = run_robustness_suite(lams)
    summaries, flat = summarize_robustness_rows(rows)
    assert len(rows) == len(robustness_scenarios()) * len(lams)
    assert len(summaries) == len(robustness_scenarios())
    assert flat["robustness_null_coupling_tc_max"] <= H.PYMDP_TC_ZERO_TOLERANCE
    assert flat["robustness_decomposition_residual_max"] <= H.PYMDP_DECOMPOSITION_RESIDUAL_TOLERANCE
    for scenario_id in {r.scenario_id for r in rows}:
        group = sorted((r for r in rows if r.scenario_id == scenario_id), key=lambda r: r.lam)
        assert group[0].lam == pytest.approx(0.0)
        assert abs(group[0].total_correlation) <= H.PYMDP_TC_ZERO_TOLERANCE
        assert group[1].total_correlation + 1e-9 >= group[0].total_correlation


@pytest.mark.skipif(not pymdp_available(), reason="pymdp 1.0.1 not installed")
def test_run_interaction_robustness_suite_small_grid_contract() -> None:
    lams = [0.0, 1.0]
    rows = run_interaction_robustness_suite(lams)
    summaries, flat = summarize_interaction_robustness_rows(rows)
    scenarios = interaction_robustness_scenarios()
    assert len(rows) == len(scenarios) * len(lams)
    assert len(summaries) == len(scenarios)
    assert flat["interaction_robustness_family_count"] == float(len(H.ROBUSTNESS_INTERACTION_FAMILIES))
    assert flat["interaction_robustness_null_variant_tc_max"] <= H.PYMDP_TC_ZERO_TOLERANCE
    assert flat["interaction_robustness_decomposition_residual_max"] <= H.PYMDP_DECOMPOSITION_RESIDUAL_TOLERANCE
    for scenario_id in {r.scenario_id for r in rows}:
        group = sorted((r for r in rows if r.scenario_id == scenario_id), key=lambda r: r.lam)
        assert group[0].lam == pytest.approx(0.0)
        assert abs(group[0].total_correlation) <= H.PYMDP_TC_ZERO_TOLERANCE
        assert group[1].total_correlation + 1e-9 >= group[0].total_correlation


@pytest.mark.skipif(not pymdp_available(), reason="pymdp 1.0.1 not installed")
def test_run_robustness_suite_progress_callback_receives_all_scenarios() -> None:
    seen: list[tuple[int, int, str]] = []

    def _progress(idx: int, total: int, scenario: RobustnessScenario) -> None:
        seen.append((idx, total, scenario.scenario_id))

    rows = run_robustness_suite([0.0], progress_callback=_progress)
    assert len(rows) == len(robustness_scenarios())
    assert len(seen) == len(robustness_scenarios())
    assert seen[0][0] == 1
    assert seen[-1][1] == len(robustness_scenarios())


@pytest.mark.skipif(not pymdp_available(), reason="pymdp 1.0.1 not installed")
def test_run_interaction_robustness_progress_callback_receives_all_scenarios() -> None:
    seen: list[tuple[int, int, str]] = []

    def _progress(idx: int, total: int, scenario: InteractionRobustnessScenario) -> None:
        seen.append((idx, total, scenario.scenario_id))

    rows = run_interaction_robustness_suite([0.0], progress_callback=_progress)
    assert len(rows) == len(interaction_robustness_scenarios())
    assert len(seen) == len(interaction_robustness_scenarios())
    assert seen[0][0] == 1
    assert seen[-1][1] == len(interaction_robustness_scenarios())


def test_robustness_summaries_reject_empty_input() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        summarize_robustness_rows([])
    with pytest.raises(ValueError, match="non-empty"):
        summarize_interaction_robustness_rows([])


@pytest.mark.skipif(not pymdp_available(), reason="pymdp 1.0.1 not installed")
def test_coupling_ablation_small_grid_contract() -> None:
    rows = run_coupling_ablation([0.0, 1.0])
    summary = summarize_coupling_ablation_rows(rows)
    assert {r.variant for r in rows} == set(H.COUPLING_ABLATION_VARIANTS)
    assert summary["coupling_ablation_null_tc_max"] <= H.PYMDP_TC_ZERO_TOLERANCE
    assert summary["coupling_ablation_decomposition_residual_max"] <= H.PYMDP_DECOMPOSITION_RESIDUAL_TOLERANCE
    for variant in H.COUPLING_ABLATION_VARIANTS:
        group = [r for r in rows if r.variant == variant]
        assert len(group) == 2
        assert abs(group[0].total_correlation) <= H.PYMDP_TC_ZERO_TOLERANCE
        if variant != "null":
            assert max(r.total_correlation for r in group) > H.PYMDP_TC_ZERO_TOLERANCE


def test_coupling_ablation_rejects_unknown_variant_and_empty_summary() -> None:
    with pytest.raises(ValueError, match="unknown coupling ablation variant"):
        coupling_ablation_spec("not_a_variant")
    with pytest.raises(ValueError, match="non-empty"):
        summarize_coupling_ablation_rows([])


@pytest.mark.skipif(not pymdp_available(), reason="pymdp 1.0.1 not installed")
def test_marginal_null_control_removes_total_correlation_on_small_grid() -> None:
    rows = run_marginal_null_control([0.0, 1.0])
    summary = summarize_marginal_null_control_rows(rows)
    assert len(rows) == 2
    assert summary["robustness_null_control_max_tc"] <= H.PYMDP_TC_ZERO_TOLERANCE
    assert rows[0].original_total_correlation == pytest.approx(0.0, abs=H.PYMDP_TC_ZERO_TOLERANCE)
    assert rows[1].tc_removed > 0.0


def test_marginal_null_control_summary_is_pure_and_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        summarize_marginal_null_control_rows([])
    rows = [
        MarginalNullControlRow(
            lam=0.0,
            original_total_correlation=0.0,
            null_total_correlation=0.0,
            original_aligned_mass=0.5,
            null_aligned_mass=0.5,
            tc_removed=0.0,
            aligned_mass_shift=0.0,
        ),
        MarginalNullControlRow(
            lam=1.0,
            original_total_correlation=0.2,
            null_total_correlation=1e-16,
            original_aligned_mass=0.8,
            null_aligned_mass=0.5,
            tc_removed=0.2,
            aligned_mass_shift=0.3,
        ),
    ]
    summary = summarize_marginal_null_control_rows(rows)
    assert summary["robustness_null_control_row_count"] == pytest.approx(2.0)
    assert summary["robustness_null_control_max_tc"] == pytest.approx(1e-16)
    assert summary["robustness_null_control_tc_removed_max"] == pytest.approx(0.2)


def test_half_saturation_edge_cases() -> None:
    assert _half_saturation([], []) is None
    assert _half_saturation([0.0, 1.0], [0.0, 0.0]) is None
    assert _half_saturation([0.0, 1.0], [float("nan"), 0.0]) == pytest.approx(1.0)


def test_wilson_score_interval_brackets_observed_rate() -> None:
    lo, hi = wilson_score_interval(3, 5)
    assert 0.0 <= lo <= 0.6 <= hi <= 1.0
    with pytest.raises(ValueError, match="positive"):
        wilson_score_interval(0, 0)
    with pytest.raises(ValueError, match="successes"):
        wilson_score_interval(6, 5)


def _synthetic_long_horizon(seed: int, tcs: np.ndarray, *, habit: bool) -> LongHorizonResult:
    T = int(tcs.size)
    marg = np.tile(np.array([[0.6, 0.4]], dtype=np.float64), (T, 1))
    joint = np.stack([np.outer(row, row) for row in marg], axis=0)
    tail = (0.01, 0.02) if habit else (0.2, 0.22)
    return LongHorizonResult(
        T=T,
        lam=1.0,
        seed=seed,
        total_correlations=tcs.astype(np.float64),
        marginal_trajectories=(marg, marg),
        joint_trajectory=joint,
        tail_marginal_means=(marg.mean(axis=0), marg.mean(axis=0)),
        tail_kl_per_stream=tail,
        tail_kl_first_per_stream=tail,
        tail_kl_mean_per_stream=tail,
        tail_kl_max_per_stream=tail,
        adjacent_kl_mean_per_stream=tail,
        adjacent_kl_max_per_stream=tail,
        habit_accumulation=habit,
        steady_state_tol=0.15,
        tail_window=2,
    )


def test_long_horizon_replicate_summary_and_envelope_are_pure() -> None:
    results = [
        _synthetic_long_horizon(0, np.array([0.0, 0.1, 0.2]), habit=True),
        _synthetic_long_horizon(7, np.array([0.0, 0.2, 0.4]), habit=False),
    ]
    records, summary = summarize_long_horizon_replicates(results)
    envelope = long_horizon_tc_envelope(results)
    assert [r.seed for r in records] == [0, 7]
    assert summary["long_horizon_replicate_seed_count"] == 2.0
    assert summary["long_horizon_replicate_success_count"] == pytest.approx(1.0)
    assert summary["long_horizon_replicate_habit_pass_rate"] == pytest.approx(0.5)
    assert summary["long_horizon_replicate_habit_pass_rate_ci_low"] <= 0.5
    assert summary["long_horizon_replicate_habit_pass_rate_ci_high"] >= 0.5
    assert envelope["median"][-1] == pytest.approx(0.3)
    assert envelope["q25"][-1] == pytest.approx(0.25)
    assert envelope["q75"][-1] == pytest.approx(0.35)
    diagnostics = long_horizon_seed_diagnostics(results)
    rates = long_horizon_threshold_pass_rates(diagnostics, thresholds=[0.01, 0.03])
    sensitivity = long_horizon_threshold_sensitivity(diagnostics, thresholds=[0.01, 0.03])
    sensitivity_summary = long_horizon_threshold_sensitivity_summary(diagnostics, thresholds=[0.01, 0.03])
    assert [d.failure_mode for d in diagnostics] == ["passes", "tail_window_kl_above_tol"]
    assert diagnostics[0].margin_to_tolerance == pytest.approx(0.13)
    assert rates["long_horizon_replicate_pass_rate_tol_0_01"] == pytest.approx(0.0)
    assert rates["long_horizon_replicate_pass_rate_tol_0_03"] == pytest.approx(0.5)
    assert [(r.pass_count, r.fail_count) for r in sensitivity] == [(0, 2), (1, 1)]
    assert all(0.0 <= r.ci_low <= r.pass_rate <= r.ci_high <= 1.0 for r in sensitivity)
    assert sensitivity_summary["long_horizon_replicate_threshold_count"] == pytest.approx(2.0)
    assert sensitivity_summary["long_horizon_replicate_threshold_pass_rate_range"] == pytest.approx(0.5)


def test_long_horizon_tc_envelope_rejects_mismatched_horizon() -> None:
    a = _synthetic_long_horizon(0, np.array([0.0, 0.1]), habit=True)
    b = _synthetic_long_horizon(1, np.array([0.0, 0.1, 0.2]), habit=True)
    with pytest.raises(ValueError, match="same horizon"):
        long_horizon_tc_envelope([a, b])


def test_long_horizon_replicate_summaries_reject_empty_input() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        long_horizon_tc_envelope([])
    with pytest.raises(ValueError, match="non-empty"):
        summarize_long_horizon_replicates([])
    with pytest.raises(ValueError, match="non-empty"):
        long_horizon_seed_diagnostics([])
    with pytest.raises(ValueError, match="non-empty"):
        long_horizon_threshold_pass_rates([])
    with pytest.raises(ValueError, match="non-empty"):
        long_horizon_threshold_sensitivity([])
    with pytest.raises(ValueError, match="non-empty"):
        long_horizon_threshold_sensitivity_summary([])


@pytest.mark.parametrize(
    ("name", "submodule"),
    [
        ("CouplingAblationRow", "simulation.robustness_scenarios"),
        ("InteractionRobustnessRow", "simulation.robustness_scenarios"),
        ("InteractionRobustnessScenario", "simulation.robustness_scenarios"),
        ("InteractionRobustnessSummary", "simulation.robustness_scenarios"),
        ("LongHorizonReplicateRecord", "simulation.robustness_scenarios"),
        ("LongHorizonSeedDiagnostic", "simulation.robustness_scenarios"),
        ("LongHorizonThresholdSensitivityRow", "simulation.robustness_scenarios"),
        ("MarginalNullControlRow", "simulation.robustness_scenarios"),
        ("RobustnessRow", "simulation.robustness_scenarios"),
        ("RobustnessScenario", "simulation.robustness_scenarios"),
        ("RobustnessScenarioSummary", "simulation.robustness_scenarios"),
        ("coupling_ablation_spec", "simulation.robustness_scenarios"),
        ("interaction_robustness_scenarios", "simulation.robustness_scenarios"),
        ("robustness_scenarios", "simulation.robustness_scenarios"),
        ("run_robustness_suite", "simulation.robustness_one_axis"),
        ("summarize_robustness_rows", "simulation.robustness_one_axis"),
        ("run_interaction_robustness_suite", "simulation.robustness_interaction"),
        ("summarize_interaction_robustness_rows", "simulation.robustness_interaction"),
        ("run_coupling_ablation", "simulation.robustness_controls"),
        ("run_marginal_null_control", "simulation.robustness_controls"),
        ("summarize_coupling_ablation_rows", "simulation.robustness_controls"),
        ("summarize_marginal_null_control_rows", "simulation.robustness_controls"),
        ("run_long_horizon_replicates", "simulation.robustness_replicates"),
        ("long_horizon_replicate_record", "simulation.robustness_replicates"),
        ("long_horizon_seed_diagnostic", "simulation.robustness_replicates"),
        ("long_horizon_seed_diagnostics", "simulation.robustness_replicates"),
        ("long_horizon_tc_envelope", "simulation.robustness_replicates"),
        ("long_horizon_threshold_pass_rates", "simulation.robustness_replicates"),
        ("long_horizon_threshold_sensitivity", "simulation.robustness_replicates"),
        ("long_horizon_threshold_sensitivity_summary", "simulation.robustness_replicates"),
        ("summarize_long_horizon_replicates", "simulation.robustness_replicates"),
        ("wilson_score_interval", "simulation.robustness_stats"),
    ],
)
def test_facade_reexports_match_submodules(name: str, submodule: str) -> None:
    """Facade attributes must mirror their domain submodule source."""
    import importlib

    from simulation import robustness as facade

    mod = importlib.import_module(submodule)
    assert getattr(facade, name) is getattr(mod, name)


def test_facade_all_names_resolve() -> None:
    """Every ``__all__`` entry on the robustness facade must be importable."""
    from simulation import robustness as facade

    for name in facade.__all__:
        assert hasattr(facade, name), name
