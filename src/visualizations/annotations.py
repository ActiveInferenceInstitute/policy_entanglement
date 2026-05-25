"""Shared annotation helpers for the figure suite.

Every figure in this manuscript draws from a small, common set of
visual conventions: a coupling-parameter axis labeled $\\lambda$,
optional theorem pinned in the corner, a footer carrying the
generating script + git rev for at-a-glance reproducibility checking,
and a consistent grid style.  Hand-rolling these per figure leads to
    drift; this module centralizes them.

Each helper accepts a Matplotlib :class:`Axes` (or :class:`Figure`)
and mutates it in place; nothing is returned, by convention.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, cast

from .setup import PUBLICATION_STYLE

# Standard math-mode label strings used across the figure suite.
LAMBDA_LABEL = r"Coupling $\lambda$"
LAMBDA_MATH = r"$\lambda$"
UTILITY_LABEL = r"Utility surplus $\Delta_{\mathrm{util}}/\Delta_{\max}$"
GAMMA_LABEL = r"EFE precision $\gamma$"
FREE_ENERGY_LABEL = r"Free energy $F[q_\lambda]$  [nats]"
MI_LABEL = r"Mutual information $I(\lambda)$  [nats]"
TOTAL_CORRELATION_LABEL = r"Total correlation $I(q_\lambda)$  [nats]"
ENTROPY_LABEL = r"Schmidt entropy $S_E(\lambda)$  [nats]"


def apply_lambda_axis(ax: Any, *, label: str | None = None) -> None:
    """Pin the x-axis to the standard $\\lambda$ label and add a faint grid.

    Use as the *last* x-axis touch in any figure that plots quantities
    against $\\lambda$ so spacing is uniform across the manuscript.
    """
    ax.set_xlabel(label or LAMBDA_LABEL)
    ax.grid(True, alpha=0.3, linewidth=0.6)


def pin_theorem(ax: Any, label: str, *, loc: str = "upper right") -> None:
    """Place a small badge in the corner naming the theorem the figure
    witnesses (e.g. ``"Thm 9.1"``, ``"Prop 7.1"``).  Lets a reader hop
    from any figure to its load-bearing claim in one glance.
    """
    bbox_args = dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#888", alpha=0.85, linewidth=0.6)
    anchors = {
        "upper right": (0.98, 0.97, "right", "top"),
        "upper left": (0.02, 0.97, "left", "top"),
        "lower right": (0.98, 0.03, "right", "bottom"),
        "lower left": (0.02, 0.03, "left", "bottom"),
    }
    x, y, ha, va = anchors.get(loc, anchors["upper right"])
    ax.text(
        x,
        y,
        label,
        transform=ax.transAxes,
        ha=ha,
        va=va,
        fontsize=PUBLICATION_STYLE.theorem_badge_size,
        color="#333",
        bbox=bbox_args,
    )


def add_provenance_footer(
    fig: Any, *, script: str, function: str, hyperparameters: Mapping[str, Any] | None = None
) -> None:
    """Place a one-line provenance footer below the axes.

    The footer is intentionally muted so it does not compete with the
    figure content, but is large enough that a reader inspecting an
    output PNG can locate the script + function without opening the
    PNG metadata.
    """
    bits = [f"{script}::{function}"]
    if hyperparameters:
        # Compact "k=v, k=v" rendering of a few hyperparameters
        joined = ", ".join(f"{k}={v}" for k, v in list(hyperparameters.items())[:4])
        if joined:
            bits.append(joined)
    text = "  ·  ".join(bits)
    fig.text(
        0.5,
        0.005,
        text,
        ha="center",
        va="bottom",
        fontsize=PUBLICATION_STYLE.provenance_size,
        color="#999",
        style="italic",
    )


def mark_critical_lambdas(
    ax: Any, lambdas: Any, *, labels: tuple[str, ...] | None = None, colors: tuple[str, ...] | None = None
) -> None:
    """Drop dashed vertical lines at one or more critical $\\lambda$ values
    with optional labels.  Used in phase / coupling-tax / convexity
    plots to call out the regime boundaries.
    """
    default_color = "#888"
    for i, lam in enumerate(lambdas):
        c = colors[i] if colors and i < len(colors) else default_color
        ax.axvline(float(lam), color=c, linestyle="--", linewidth=1.2, alpha=0.85)
        if labels and i < len(labels):
            ax.text(
                float(lam),
                ax.get_ylim()[1],
                f" {labels[i]}",
                fontsize=PUBLICATION_STYLE.annotation_size,
                color=c,
                ha="left",
                va="top",
            )


def add_stats_box(
    ax: Any,
    lines: Mapping[str, Any] | Sequence[tuple[str, Any]] | Sequence[str],
    *,
    loc: str = "lower right",
) -> None:
    """Add a compact statistics box to an axis.

    ``lines`` may be a mapping or an ordered sequence of ``(label,
    value)`` pairs, or already formatted strings. Values are rendered
    with short numeric formatting and are intended for derived plot
    metadata such as grid size, extrema, residual maxima, and
    tolerances.
    """
    items: list[tuple[str, Any] | str] = (
        list(lines.items()) if isinstance(lines, Mapping) else list(cast(Sequence[tuple[str, Any] | str], lines))
    )

    def _fmt(value: Any) -> str:
        if isinstance(value, float):
            if abs(value) >= 1e3 or (0 < abs(value) < 1e-2):
                return f"{value:.2e}"
            return f"{value:.3g}"
        return str(value)

    rendered: list[str] = []
    for item in items:
        if isinstance(item, str):
            rendered.append(item)
        else:
            label, value = item
            rendered.append(f"{label}: {_fmt(value)}")
    text = "\n".join(rendered)
    anchors = {
        "lower right": (0.98, 0.03, "right", "bottom"),
        "lower left": (0.02, 0.03, "left", "bottom"),
        "upper right": (0.98, 0.97, "right", "top"),
        "upper left": (0.02, 0.97, "left", "top"),
    }
    x, y, ha, va = anchors.get(loc, anchors["lower right"])
    ax.text(
        x,
        y,
        text,
        transform=ax.transAxes,
        ha=ha,
        va=va,
        fontsize=PUBLICATION_STYLE.annotation_size,
        color="#333",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#777", alpha=0.88, linewidth=0.7),
    )


def add_mean_field_baseline(ax: Any, value: float = 0.0, *, label: str | None = None) -> None:
    """Draw a horizontal dashed line at the mean-field baseline value.

    Convention across the manuscript: a horizontal dashed grey line at
    ``y = value`` (typically ``0`` for total correlation, log-weight,
    or KL residual figures) marks where the strict per-stream mean-field
    sits — making the "departure from mean-field" visually unambiguous.
    """
    ax.axhline(
        float(value),
        color="#666",
        linestyle=(0, (4, 3)),
        linewidth=1.0,
        alpha=0.7,
        zorder=0,
    )
    if label:
        ax.text(
            0.01,
            float(value),
            label,
            transform=ax.get_yaxis_transform(),
            ha="left",
            va="bottom",
            fontsize=PUBLICATION_STYLE.annotation_size,
            color="#666",
            alpha=0.85,
            style="italic",
        )


def add_tolerance_band(
    ax: Any,
    center: float,
    half_width: float,
    *,
    color: str = "#56B4E9",
    label: str | None = None,
) -> None:
    """Shade a horizontal tolerance band ``[center - hw, center + hw]`` across the axis.

    Used to depict numerical tolerances (e.g. ``REVERTIBILITY_TOLERANCE``)
    or analytical envelopes (e.g. ``±sqrt(N)`` Monte-Carlo
    concentration). The band is faint by design so curves overplotted
    on top remain readable.
    """
    lo, hi = float(center) - float(half_width), float(center) + float(half_width)
    ax.axhspan(lo, hi, color=color, alpha=0.14, zorder=0, label=label)


def add_saturation_marker(ax: Any, lam_half: float, value_at_half: float, *, label: str = r"$\lambda_{1/2}$") -> None:
    """Mark a half-saturation coupling value on a $\\lambda$-vs-$I$ axis.

    Combines a vertical dashed line at ``lam_half`` with a small badge
    showing ``(λ_half, I_half)``. Useful on
    :data:`pymdp_total_correlation_curve` and equivalent figures.
    """
    ax.axvline(
        float(lam_half),
        color="#D55E00",
        linestyle="--",
        linewidth=1.0,
        alpha=0.85,
        zorder=1,
    )
    ax.plot(
        [float(lam_half)],
        [float(value_at_half)],
        marker="o",
        color="#D55E00",
        markersize=PUBLICATION_STYLE.annotation_size,
        zorder=3,
    )
    ax.annotate(
        f"{label} ≈ {float(lam_half):.3f}\nI = {float(value_at_half):.4f} nats",
        xy=(float(lam_half), float(value_at_half)),
        xytext=(8, -10),
        textcoords="offset points",
        fontsize=PUBLICATION_STYLE.annotation_size,
        color="#D55E00",
        ha="left",
        va="top",
        bbox=dict(
            boxstyle="round,pad=0.2",
            facecolor="white",
            edgecolor="#D55E00",
            alpha=0.9,
            linewidth=0.7,
        ),
    )


def add_claim_strength_tag(ax: Any, kind: str, *, loc: str = "lower left") -> None:
    """Pin a small claim-strength tag on a figure axis.

    ``kind`` is one of ``"empirical"``, ``"witness"``, ``"hypothesis"``,
    ``"analytical"`` — matching the claim-strength legend at §S7.1. The
    tag color is consistent across the manuscript: green for
    ``empirical``, blue for ``witness``, amber for ``hypothesis``, slate
    for ``analytical``.
    """
    palette = {
        "empirical": ("#009E73", "white"),
        "witness": ("#0072B2", "white"),
        "hypothesis": ("#E69F00", "black"),
        "analytical": ("#444444", "white"),
    }
    fg, bg = palette.get(kind.lower(), ("#444", "white"))
    anchors = {
        "upper right": (0.98, 0.96, "right", "top"),
        "upper left": (0.02, 0.96, "left", "top"),
        "lower right": (0.98, 0.04, "right", "bottom"),
        "lower left": (0.02, 0.04, "left", "bottom"),
    }
    x, y, ha, va = anchors.get(loc, anchors["lower left"])
    ax.text(
        x,
        y,
        f"claim: {kind.lower()}",
        transform=ax.transAxes,
        ha=ha,
        va=va,
        fontsize=PUBLICATION_STYLE.theorem_badge_size,
        color=bg,
        bbox=dict(
            boxstyle="round,pad=0.25",
            facecolor=fg,
            edgecolor=fg,
            alpha=0.92,
            linewidth=0.6,
        ),
    )
