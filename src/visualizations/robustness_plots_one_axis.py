"""One-axis robustness stress-test publication plots."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from ._io import _save_with_metadata as _save
from .annotations import add_stats_box, apply_lambda_axis
from .setup import PUBLICATION_STYLE, palette_color


def _group_by(rows: Sequence[Any], key: str) -> dict[str, list[Any]]:
    out: dict[str, list[Any]] = {}
    for row in rows:
        out.setdefault(str(getattr(row, key)), []).append(row)
    return out


def plot_robustness_tc_envelopes(
    rows: Sequence[Any],
    *,
    out_path: Path,
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """TC curves for every one-axis robustness perturbation."""

    fig, axes = plt.subplots(2, 2, figsize=PUBLICATION_STYLE.dashboard_2x2, constrained_layout=True)
    axis_order = ("observation", "gamma", "preference", "coupling_scale")
    axis_titles = {
        "observation": "Observation contexts",
        "gamma": "Precision γ",
        "preference": "Preference strength",
        "coupling_scale": "Coupling scale",
    }
    max_tc = 0.0
    max_resid = 0.0
    for ax_idx, axis_name in enumerate(axis_order):
        ax = axes.flat[ax_idx]
        axis_rows = [r for r in rows if r.axis == axis_name]
        by_scenario = _group_by(axis_rows, "scenario_id")
        for i, (scenario_id, group_raw) in enumerate(sorted(by_scenario.items())):
            group = sorted(group_raw, key=lambda r: r.lam)
            lams = [r.lam for r in group]
            tcs = [r.total_correlation for r in group]
            max_tc = max(max_tc, max(tcs, default=0.0))
            max_resid = max(max_resid, max((r.decomposition_residual for r in group), default=0.0))
            label = str(group[0].level) if group else scenario_id
            ax.plot(
                lams,
                tcs,
                "o-",
                linewidth=1.9,
                markersize=4.5,
                color=palette_color(i),
                label=label,
            )
        apply_lambda_axis(ax)
        ax.set_ylabel("Total correlation I(q_λ) [nats]")
        ax.set_title(axis_titles[axis_name])
        ax.legend(loc="best", ncol=2 if axis_name == "observation" else 1)
        add_stats_box(
            ax,
            {
                "scenarios": len(by_scenario),
                "max TC": max((r.total_correlation for r in axis_rows), default=0.0),
                "max residual": max((r.decomposition_residual for r in axis_rows), default=0.0),
            },
            loc="lower right",
        )
    fig.suptitle("Robustness stress tests: total-correlation envelopes")
    return _save(fig, Path(out_path), metadata=metadata)


def plot_robustness_half_saturation(
    summaries: Sequence[Any],
    *,
    out_path: Path,
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """Scenario-level half-saturation λ bars."""

    ordered = sorted(summaries, key=lambda s: (s.axis, s.scenario_id))
    labels = [f"{s.axis}: {s.level}" for s in ordered]
    values = [float(s.lambda_half_saturation) if s.lambda_half_saturation is not None else 0.0 for s in ordered]
    colors = [palette_color(("observation", "gamma", "preference", "coupling_scale").index(s.axis)) for s in ordered]

    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.wide, constrained_layout=True)
    y = np.arange(len(ordered))
    ax.barh(y, values, color=colors, alpha=0.86)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Half-saturation coupling λ₁/₂")
    ax.set_title("Robustness stress tests: half-saturation sensitivity")
    finite = [v for v, s in zip(values, ordered, strict=True) if s.lambda_half_saturation is not None]
    add_stats_box(
        ax,
        {
            "finite scenarios": len(finite),
            "min λ₁/₂": min(finite, default=0.0),
            "max λ₁/₂": max(finite, default=0.0),
        },
        loc="lower right",
    )
    return _save(fig, Path(out_path), metadata=metadata)


def plot_robustness_decomposition_residuals(
    summaries: Sequence[Any],
    *,
    out_path: Path,
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """Maximum decomposition residual per robustness scenario."""

    ordered = sorted(summaries, key=lambda s: (s.axis, s.scenario_id))
    x = np.arange(len(ordered))
    residuals = [float(s.residual_max) for s in ordered]
    colors = [palette_color(("observation", "gamma", "preference", "coupling_scale").index(s.axis)) for s in ordered]

    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.wide, constrained_layout=True)
    ax.scatter(x, residuals, s=58, color=colors, edgecolor="white", linewidth=0.7)
    ax.plot(x, residuals, color="#555555", alpha=0.45, linewidth=1.0)
    ax.set_xticks(x)
    ax.set_xticklabels([s.scenario_id for s in ordered], rotation=35, ha="right")
    ax.set_ylabel("max |LHS − RHS|")
    ax.set_title("Robustness stress tests: decomposition residuals")
    ax.set_yscale("symlog", linthresh=1e-15)
    add_stats_box(
        ax,
        {
            "scenarios": len(ordered),
            "max residual": max(residuals, default=0.0),
            "monotone TC": sum(1 for s in ordered if s.monotone_tc),
        },
        loc="upper right",
    )
    return _save(fig, Path(out_path), metadata=metadata)


__all__ = [
    "plot_robustness_decomposition_residuals",
    "plot_robustness_half_saturation",
    "plot_robustness_tc_envelopes",
]
