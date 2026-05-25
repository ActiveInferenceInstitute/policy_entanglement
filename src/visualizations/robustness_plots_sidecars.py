"""Ablation, interaction, and long-horizon robustness publication plots."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from simulation.robustness import (
    long_horizon_tc_envelope,
    long_horizon_threshold_sensitivity,
    summarize_long_horizon_replicates,
)

from ._io import _save_with_metadata as _save
from .annotations import add_stats_box, apply_lambda_axis
from .robustness_plots_one_axis import _group_by
from .setup import PUBLICATION_STYLE, palette_color


def plot_coupling_ablation_summary(
    rows: Sequence[Any],
    *,
    out_path: Path,
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """Two-panel ablation summary: TC and aligned mass by variant."""

    fig, (ax_tc, ax_mass) = plt.subplots(1, 2, figsize=PUBLICATION_STYLE.two_panel, constrained_layout=True)
    by_variant = _group_by(rows, "variant")
    final_masses: list[str] = []
    for i, (variant, group_raw) in enumerate(sorted(by_variant.items())):
        group = sorted(group_raw, key=lambda r: r.lam)
        lams = [r.lam for r in group]
        tcs = [r.total_correlation for r in group]
        masses = [r.aligned_mass for r in group]
        color = palette_color(i)
        label = variant.replace("_", " ")
        ax_tc.plot(lams, tcs, "o-", color=color, linewidth=2.0, markersize=5, label=label)
        ax_mass.plot(lams, masses, "s-", color=color, linewidth=2.0, markersize=5, label=label)
        final_masses.append(f"{variant}={masses[-1]:.3g}")
    apply_lambda_axis(ax_tc)
    ax_tc.set_ylabel("Total correlation I(q_λ) [nats]")
    ax_tc.set_title("Coupling-ablation TC")
    ax_tc.legend(loc="best")
    apply_lambda_axis(ax_mass)
    ax_mass.set_ylabel("Aligned-corner mass")
    ax_mass.set_title("Archetypal-mass shift")
    ax_mass.set_ylim(0.0, 1.05)
    ax_mass.legend(loc="best")
    add_stats_box(
        ax_tc,
        {
            "variants": len(by_variant),
            "max TC": max((r.total_correlation for r in rows), default=0.0),
            "max residual": max((r.decomposition_residual for r in rows), default=0.0),
        },
        loc="lower right",
    )
    add_stats_box(ax_mass, {"final mass": "; ".join(final_masses)}, loc="lower right")
    return _save(fig, Path(out_path), metadata=metadata)


def plot_marginal_null_control_summary(
    rows: Sequence[Any],
    *,
    out_path: Path,
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """Fixed-marginal independence control for the canonical robustness sweep."""

    ordered = sorted(rows, key=lambda r: r.lam)
    lams = [float(r.lam) for r in ordered]
    original_tc = [float(r.original_total_correlation) for r in ordered]
    null_tc = [float(r.null_total_correlation) for r in ordered]
    original_mass = [float(r.original_aligned_mass) for r in ordered]
    null_mass = [float(r.null_aligned_mass) for r in ordered]

    fig, (ax_tc, ax_mass) = plt.subplots(1, 2, figsize=PUBLICATION_STYLE.two_panel, constrained_layout=True)
    ax_tc.plot(lams, original_tc, "o-", color=palette_color(0), linewidth=2.1, markersize=5, label="entangled joint")
    ax_tc.plot(lams, null_tc, "s--", color=palette_color(6), linewidth=2.1, markersize=5, label="product of marginals")
    apply_lambda_axis(ax_tc)
    ax_tc.set_ylabel("Total correlation I(q_λ) [nats]")
    ax_tc.set_title("Fixed-marginal TC control")
    ax_tc.legend(loc="best")
    ax_mass.plot(
        lams,
        original_mass,
        "o-",
        color=palette_color(2),
        linewidth=2.1,
        markersize=5,
        label="entangled joint",
    )
    ax_mass.plot(
        lams,
        null_mass,
        "s--",
        color=palette_color(5),
        linewidth=2.1,
        markersize=5,
        label="product of marginals",
    )
    apply_lambda_axis(ax_mass)
    ax_mass.set_ylabel("Aligned-corner mass")
    ax_mass.set_title("Archetypal mass under control")
    ax_mass.set_ylim(0.0, 1.05)
    ax_mass.legend(loc="best")
    add_stats_box(
        ax_tc,
        {
            "rows": len(ordered),
            "max null TC": max(null_tc, default=0.0),
            "max TC removed": max((float(r.tc_removed) for r in ordered), default=0.0),
        },
        loc="upper left",
    )
    add_stats_box(
        ax_mass,
        {
            "max mass shift": max((abs(float(r.aligned_mass_shift)) for r in ordered), default=0.0),
        },
        loc="lower right",
    )
    fig.suptitle("Marginal-preserving null control")
    return _save(fig, Path(out_path), metadata=metadata)


def plot_interaction_robustness_summary(
    summaries: Sequence[Any],
    *,
    out_path: Path,
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """Appendix summary for targeted two-axis robustness interactions."""

    family_order = (
        "observation_x_coupling_scale",
        "gamma_x_preference_strength",
        "coupling_variant_x_coupling_scale",
    )
    family_titles = {
        "observation_x_coupling_scale": "Observation × coupling scale",
        "gamma_x_preference_strength": "Precision γ × preference",
        "coupling_variant_x_coupling_scale": "Coupling variant × scale",
    }
    fig, axes = plt.subplots(1, 3, figsize=PUBLICATION_STYLE.dashboard_2x3, constrained_layout=True)
    for idx, family in enumerate(family_order):
        ax = axes[idx]
        group = sorted((s for s in summaries if s.family == family), key=lambda s: (s.level_a, s.level_b))
        x = np.arange(len(group))
        heights = [float(s.tc_max) for s in group]
        colors = [palette_color(idx + j) for j in range(len(group))]
        ax.bar(x, heights, color=colors, alpha=0.86)
        ax.set_xticks(x)
        ax.set_xticklabels([f"{s.level_a}\n{s.level_b}" for s in group], rotation=70, ha="right")
        ax.set_ylabel("max total correlation [nats]")
        ax.set_title(family_titles[family])
        add_stats_box(
            ax,
            {
                "scenarios": len(group),
                "max TC": max(heights, default=0.0),
                "max residual": max((s.residual_max for s in group), default=0.0),
            },
            loc="upper left",
        )
    fig.suptitle("Appendix stress tests: targeted two-axis interactions")
    return _save(fig, Path(out_path), metadata=metadata)


def plot_long_horizon_replicate_envelope(
    results: Sequence[Any],
    *,
    out_path: Path,
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """Quantile envelope for long-horizon replicate TC trajectories."""

    envelope = long_horizon_tc_envelope(results)
    records, summary = summarize_long_horizon_replicates(results)
    t = np.asarray(envelope["t"], dtype=np.float64)
    q25 = np.asarray(envelope["q25"], dtype=np.float64)
    median = np.asarray(envelope["median"], dtype=np.float64)
    q75 = np.asarray(envelope["q75"], dtype=np.float64)
    lo = np.asarray(envelope["min"], dtype=np.float64)
    hi = np.asarray(envelope["max"], dtype=np.float64)

    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.wide, constrained_layout=True)
    ax.fill_between(t, lo, hi, color=palette_color(2), alpha=0.14, label="min–max")
    ax.fill_between(t, q25, q75, color=palette_color(2), alpha=0.28, label="IQR")
    ax.plot(t, median, color=palette_color(5), linewidth=2.3, label="median TC")
    ax.set_xlabel("time t")
    ax.set_ylabel("Total correlation I(q_t) [nats]")
    ax.set_title("Long-horizon robustness: replicate TC envelope")
    ax.legend(loc="best")
    add_stats_box(
        ax,
        {
            "seeds": len(records),
            "pass rate": summary["long_horizon_replicate_habit_pass_rate"],
            "final TC mean": summary["long_horizon_replicate_tc_final_mean"],
            "tail KL max": summary["long_horizon_replicate_tail_kl_window_max"],
        },
        loc="lower right",
    )
    return _save(fig, Path(out_path), metadata=metadata)


def plot_long_horizon_seed_diagnostics(
    diagnostics: Sequence[Any],
    *,
    tolerance: float,
    out_path: Path,
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """Per-seed tail-window diagnostics for long-horizon robustness."""

    ordered = sorted(diagnostics, key=lambda r: r.seed)
    seeds = [str(r.seed) for r in ordered]
    x = np.arange(len(ordered))
    tail = [float(r.tail_kl_window_max) for r in ordered]
    adj = [float(r.adjacent_kl_max) for r in ordered]
    tc_final = [float(r.tc_final) for r in ordered]
    colors = [palette_color(3 if r.habit_accumulation else 6) for r in ordered]

    fig, (ax_kl, ax_tc) = plt.subplots(1, 2, figsize=PUBLICATION_STYLE.two_panel, constrained_layout=True)
    ax_kl.bar(x - 0.18, tail, width=0.36, color=colors, alpha=0.88, label="tail-window KL")
    ax_kl.bar(x + 0.18, adj, width=0.36, color=palette_color(2), alpha=0.62, label="max adjacent KL")
    ax_kl.axhline(float(tolerance), color=palette_color(6), linestyle="--", linewidth=1.7, label="habit threshold")
    ax_kl.set_xticks(x)
    ax_kl.set_xticklabels(seeds)
    ax_kl.set_xlabel("seed")
    ax_kl.set_ylabel("KL divergence [nats]")
    ax_kl.set_title("Tail-window and adjacent-step KL")
    ax_kl.legend(loc="best")
    ax_tc.bar(x, tc_final, color=colors, alpha=0.88)
    ax_tc.set_xticks(x)
    ax_tc.set_xticklabels(seeds)
    ax_tc.set_xlabel("seed")
    ax_tc.set_ylabel("final total correlation [nats]")
    ax_tc.set_title("Final TC by seed")
    add_stats_box(
        ax_kl,
        {
            "seeds": len(ordered),
            "pass rate": np.mean([1.0 if r.habit_accumulation else 0.0 for r in ordered]) if ordered else 0.0,
            "max tail KL": max(tail, default=0.0),
        },
        loc="upper left",
    )
    add_stats_box(
        ax_tc,
        {
            "TC mean": np.mean(tc_final) if tc_final else 0.0,
            "TC range": max(tc_final, default=0.0) - min(tc_final, default=0.0),
        },
        loc="upper left",
    )
    fig.suptitle("Long-horizon seed diagnostics")
    return _save(fig, Path(out_path), metadata=metadata)


def plot_long_horizon_threshold_sensitivity(
    diagnostics: Sequence[Any],
    *,
    thresholds: Sequence[float],
    canonical_tolerance: float,
    out_path: Path,
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """Pass-rate sensitivity across tail-window KL thresholds."""

    rows = long_horizon_threshold_sensitivity(diagnostics, thresholds)
    x = np.asarray([r.threshold for r in rows], dtype=np.float64)
    rates = np.asarray([r.pass_rate for r in rows], dtype=np.float64)
    ci_low = np.asarray([r.ci_low for r in rows], dtype=np.float64)
    ci_high = np.asarray([r.ci_high for r in rows], dtype=np.float64)
    labels = [f"{r.pass_count}/{r.pass_count + r.fail_count}" for r in rows]

    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.wide, constrained_layout=True)
    bars = ax.bar(x, rates, width=0.028, color=palette_color(5), alpha=0.84, label="pass rate")
    ax.errorbar(
        x,
        rates,
        yerr=np.vstack([rates - ci_low, ci_high - rates]),
        fmt="o-",
        color=palette_color(0),
        ecolor=palette_color(0),
        elinewidth=1.3,
        capsize=4,
        linewidth=2.0,
        markersize=5.5,
        label="Wilson 95% CI",
    )
    ax.axvline(
        float(canonical_tolerance),
        color=palette_color(6),
        linestyle="--",
        linewidth=1.8,
        label="canonical threshold",
    )
    for bar, label in zip(bars, labels, strict=True):
        ax.text(
            float(bar.get_x() + bar.get_width() / 2.0),
            min(float(bar.get_height()) + 0.035, 1.02),
            label,
            ha="center",
            va="bottom",
            fontsize=PUBLICATION_STYLE.annotation_size,
        )
    ax.set_xlabel("tail-window KL threshold")
    ax.set_ylabel("habit-accumulation pass rate")
    ax.set_ylim(0.0, 1.08)
    ax.set_title("Long-horizon threshold sensitivity")
    ax.legend(loc="lower right")
    canonical_passes = next(
        (r.pass_count for r in rows if abs(float(r.threshold) - float(canonical_tolerance)) <= 1e-12),
        "see dashed line",
    )
    add_stats_box(
        ax,
        {
            "thresholds": len(rows),
            "pass-rate range": float(np.max(rates) - np.min(rates)) if rates.size else 0.0,
            "canonical passes": canonical_passes,
            "CI method": "Wilson",
        },
        loc="upper left",
    )
    return _save(fig, Path(out_path), metadata=metadata)


__all__ = [
    "plot_coupling_ablation_summary",
    "plot_interaction_robustness_summary",
    "plot_long_horizon_replicate_envelope",
    "plot_long_horizon_seed_diagnostics",
    "plot_long_horizon_threshold_sensitivity",
    "plot_marginal_null_control_summary",
]
