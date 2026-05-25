"""Smoke and coverage tests for robustness visualization helpers.

The publication path generates these figures from real pymdp outputs.
These tests use small synthetic records so plotting branches stay cheap
and deterministic under the full coverage gate.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np

from simulation.robustness import (
    CouplingAblationRow,
    InteractionRobustnessSummary,
    LongHorizonSeedDiagnostic,
    MarginalNullControlRow,
    RobustnessRow,
    RobustnessScenarioSummary,
)
from visualizations.robustness_plots import (
    plot_coupling_ablation_summary,
    plot_interaction_robustness_summary,
    plot_long_horizon_replicate_envelope,
    plot_long_horizon_seed_diagnostics,
    plot_long_horizon_threshold_sensitivity,
    plot_marginal_null_control_summary,
    plot_robustness_decomposition_residuals,
    plot_robustness_half_saturation,
    plot_robustness_tc_envelopes,
)

PNG_HEADER = b"\x89PNG\r\n\x1a\n"


def _assert_png(path: Path) -> None:
    assert path.exists(), f"missing: {path}"
    assert path.stat().st_size > 0, f"empty: {path}"
    with path.open("rb") as fh:
        assert fh.read(8) == PNG_HEADER


def _robustness_rows() -> list[RobustnessRow]:
    axes = {
        "observation": ["(0,0)", "(1,1)"],
        "gamma": ["0.5", "2"],
        "preference": ["0.5", "2"],
        "coupling_scale": ["0", "1.5"],
    }
    rows: list[RobustnessRow] = []
    for axis, levels in axes.items():
        for level_idx, level in enumerate(levels):
            scenario_id = f"{axis}_{level_idx}"
            for lam in (0.0, 1.0, 2.0):
                tc = (0.04 + 0.02 * level_idx) * lam
                if axis == "coupling_scale" and level == "0":
                    tc = 0.0
                rows.append(
                    RobustnessRow(
                        scenario_id=scenario_id,
                        axis=axis,
                        level=level,
                        observations=(0, 0),
                        gamma=1.0,
                        preference_strength=1.0,
                        coupling_scale=0.0 if level == "0" else 1.0,
                        lam=lam,
                        total_correlation=tc,
                        joint_entropy=1.0 - tc,
                        marginal_entropy_sum=1.0,
                        coupling_term=0.1 * lam,
                        aligned_mass=0.5 + 0.1 * lam,
                        decomposition_lhs=tc,
                        decomposition_rhs=tc,
                        decomposition_residual=1e-16 * (1 + level_idx),
                    )
                )
    return rows


def _robustness_summaries() -> list[RobustnessScenarioSummary]:
    summaries: list[RobustnessScenarioSummary] = []
    for scenario_id in sorted({row.scenario_id for row in _robustness_rows()}):
        group = [row for row in _robustness_rows() if row.scenario_id == scenario_id]
        summaries.append(
            RobustnessScenarioSummary(
                scenario_id=scenario_id,
                axis=group[0].axis,
                level=group[0].level,
                tc_max=max(row.total_correlation for row in group),
                tc_final=group[-1].total_correlation,
                lambda_half_saturation=1.0 if any(row.total_correlation > 0 for row in group) else None,
                residual_max=max(row.decomposition_residual for row in group),
                monotone_tc=True,
            )
        )
    return summaries


def _ablation_rows() -> list[CouplingAblationRow]:
    variants = ("aligned", "null", "anti_aligned", "heterogeneous_kc")
    rows: list[CouplingAblationRow] = []
    for variant_idx, variant in enumerate(variants):
        for lam in (0.0, 1.0, 2.0):
            tc = 0.0 if variant == "null" else (0.03 + 0.02 * variant_idx) * lam
            rows.append(
                CouplingAblationRow(
                    variant=variant,
                    lam=lam,
                    total_correlation=tc,
                    joint_entropy=1.0 - tc,
                    marginal_entropy_sum=1.0,
                    coupling_term=0.1 * lam,
                    aligned_mass=0.25 + 0.08 * variant_idx + 0.05 * lam,
                    decomposition_lhs=tc,
                    decomposition_rhs=tc,
                    decomposition_residual=1e-16,
                )
            )
    return rows


def _null_control_rows() -> list[MarginalNullControlRow]:
    return [
        MarginalNullControlRow(
            lam=lam,
            original_total_correlation=0.1 * lam,
            null_total_correlation=0.0,
            original_aligned_mass=0.5 + 0.1 * lam,
            null_aligned_mass=0.5,
            tc_removed=0.1 * lam,
            aligned_mass_shift=0.1 * lam,
        )
        for lam in (0.0, 1.0, 2.0)
    ]


def _interaction_summaries() -> list[InteractionRobustnessSummary]:
    families = (
        "observation_x_coupling_scale",
        "gamma_x_preference_strength",
        "coupling_variant_x_coupling_scale",
    )
    out: list[InteractionRobustnessSummary] = []
    for family_idx, family in enumerate(families):
        for i in range(3):
            out.append(
                InteractionRobustnessSummary(
                    family=family,
                    scenario_id=f"{family}_{i}",
                    level_a=f"a{i}",
                    level_b=f"b{i}",
                    tc_max=0.05 * (family_idx + 1) * (i + 1),
                    tc_final=0.04 * (family_idx + 1) * (i + 1),
                    residual_max=1e-16,
                    monotone_tc=True,
                )
            )
    return out


@dataclass(frozen=True)
class _FakeReplicate:
    T: int
    seed: int
    habit_accumulation: bool
    total_correlations: np.ndarray
    tail_kl_max_per_stream: tuple[float, ...]
    adjacent_kl_max_per_stream: tuple[float, ...]


def _replicates() -> list[_FakeReplicate]:
    return [
        _FakeReplicate(
            T=6,
            seed=seed,
            habit_accumulation=(seed != 7),
            total_correlations=np.linspace(0.05 + 0.01 * i, 0.35 + 0.02 * i, 6),
            tail_kl_max_per_stream=(0.01 + 0.001 * i, 0.012 + 0.001 * i),
            adjacent_kl_max_per_stream=(0.02 + 0.001 * i, 0.022 + 0.001 * i),
        )
        for i, seed in enumerate((0, 7, 13))
    ]


def _seed_diagnostics() -> list[LongHorizonSeedDiagnostic]:
    return [
        LongHorizonSeedDiagnostic(
            seed=0,
            habit_accumulation=True,
            tc_final=0.3,
            tc_max=0.35,
            tail_kl_window_max=0.04,
            adjacent_kl_max=0.02,
            margin_to_tolerance=0.11,
            failure_mode="passes",
        ),
        LongHorizonSeedDiagnostic(
            seed=7,
            habit_accumulation=False,
            tc_final=0.25,
            tc_max=0.32,
            tail_kl_window_max=0.19,
            adjacent_kl_max=0.05,
            margin_to_tolerance=-0.04,
            failure_mode="tail_window_kl_above_tol",
        ),
    ]


def test_plot_robustness_tc_envelopes_writes_png(tmp_path: Path) -> None:
    out = plot_robustness_tc_envelopes(
        _robustness_rows(),
        out_path=tmp_path / "robustness_tc.png",
        metadata={"test": "robustness"},
    )
    _assert_png(out)


def test_plot_robustness_half_saturation_writes_png(tmp_path: Path) -> None:
    out = plot_robustness_half_saturation(
        _robustness_summaries(),
        out_path=tmp_path / "half_saturation.png",
    )
    _assert_png(out)


def test_plot_robustness_decomposition_residuals_writes_png(tmp_path: Path) -> None:
    out = plot_robustness_decomposition_residuals(
        _robustness_summaries(),
        out_path=tmp_path / "residuals.png",
    )
    _assert_png(out)


def test_plot_coupling_ablation_summary_writes_png(tmp_path: Path) -> None:
    out = plot_coupling_ablation_summary(
        _ablation_rows(),
        out_path=tmp_path / "ablation.png",
    )
    _assert_png(out)


def test_plot_marginal_null_control_summary_writes_png(tmp_path: Path) -> None:
    out = plot_marginal_null_control_summary(
        _null_control_rows(),
        out_path=tmp_path / "null_control.png",
    )
    _assert_png(out)


def test_plot_interaction_robustness_summary_writes_png(tmp_path: Path) -> None:
    out = plot_interaction_robustness_summary(
        _interaction_summaries(),
        out_path=tmp_path / "interaction.png",
    )
    _assert_png(out)


def test_plot_long_horizon_replicate_envelope_writes_png(tmp_path: Path) -> None:
    out = plot_long_horizon_replicate_envelope(
        _replicates(),
        out_path=tmp_path / "replicates.png",
        metadata={"test": "replicates"},
    )
    _assert_png(out)


def test_plot_long_horizon_seed_diagnostics_writes_png(tmp_path: Path) -> None:
    out = plot_long_horizon_seed_diagnostics(
        _seed_diagnostics(),
        tolerance=0.15,
        out_path=tmp_path / "seed_diagnostics.png",
        metadata={"test": "seed_diagnostics"},
    )
    _assert_png(out)


def test_plot_long_horizon_threshold_sensitivity_writes_png(tmp_path: Path) -> None:
    out = plot_long_horizon_threshold_sensitivity(
        _seed_diagnostics(),
        thresholds=[0.05, 0.10, 0.15, 0.20],
        canonical_tolerance=0.15,
        out_path=tmp_path / "threshold_sensitivity.png",
        metadata={"test": "threshold_sensitivity"},
    )
    _assert_png(out)
