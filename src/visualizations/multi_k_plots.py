"""Visualizations for the K>2 multi-K, long-horizon, and revertibility experiments.

All figure helpers in this module take pre-computed records (from
:mod:`simulation.multi_k_experiments` / :mod:`simulation.long_horizon`
/ :mod:`simulation.revertibility`) and emit a single PNG.  No
numerical work happens here — the data is fully pre-computed in
``src/simulation/``, this module owns I/O + matplotlib styling only.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

from ._io import _save_with_metadata as _save
from .annotations import add_stats_box, apply_lambda_axis
from .setup import PUBLICATION_STYLE, palette_color

ArrayF = NDArray[np.float64]


# ---------------------------------------------------------------------------
# T1 — K>2 ensemble experiments
# ---------------------------------------------------------------------------


def plot_multi_k_total_correlation(
    results_by_k: Mapping[int, Sequence],
    *,
    out_path: Path,
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """Multi-information vs λ for several K values overlaid.

    ``results_by_k`` maps each K (int) to a sequence of
    :class:`MultiKResult` records.  Each K is rendered as a separate
    colored curve so the manuscript figure can show how I(q_λ) scales
    with the number of streams.
    """
    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.single, constrained_layout=True)
    maxima: list[str] = []
    for K, results in sorted(results_by_k.items()):  # noqa: N806 — K = manuscript symbol.
        lams = [r.lam for r in results]
        tcs = [r.total_correlation for r in results]
        maxima.append(f"K={K} max={max(tcs):.3g}")
        ax.plot(lams, tcs, "o-", linewidth=2.0, markersize=5, label=f"K={K}")
    apply_lambda_axis(ax)
    ax.set_ylabel("Multi-information I(q_λ)  [nats]")
    ax.set_title("Multi-K ensemble: I(q_λ) vs coupling")
    ax.legend(loc="best")
    if results_by_k:
        n_grid = len(next(iter(results_by_k.values())))
        all_lams = [r.lam for rows in results_by_k.values() for r in rows]
        add_stats_box(
            ax,
            {
                "grid": n_grid,
                "λ range": f"{min(all_lams):.2g}–{max(all_lams):.2g}",
                "TC max": "; ".join(maxima),
            },
            loc="lower right",
        )
    return _save(fig, Path(out_path), metadata=metadata)


def plot_multi_k_tt_rank_profile(
    results_by_k: Mapping[int, Sequence],
    *,
    out_path: Path,
    lam_index: int = -1,
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """Tensor-train rank profile at one λ across the K-stream ensembles.

    For each K the figure shows the K-1 bond dimensions
    $(r_1, \\dots, r_{K-1})$ at the chosen ``lam_index``.  Useful as
    a low-rank-coupling witness for the §8 sparsity / TT rank claims.
    """
    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.single, constrained_layout=True)
    max_rank = 0
    rank_sums: list[str] = []
    for i, (K, results) in enumerate(sorted(results_by_k.items())):  # noqa: N806 — K = manuscript symbol.
        rec = results[lam_index]
        ranks = list(rec.tt_ranks)
        max_rank = max(max_rank, max(ranks) if ranks else 0)
        rank_sums.append(f"K={K} Σr={sum(ranks)}")
        cuts = list(range(1, len(ranks) + 1))
        ax.plot(
            cuts,
            ranks,
            "o-",
            color=palette_color(i),
            linewidth=2.0,
            markersize=6,
            label=f"K={K}, λ={rec.lam:.2f}",
        )
    ax.set_xlabel("TT cut index")
    ax.set_ylabel("Bond dimension")
    ax.set_title("Tensor-train rank profile across K")
    ax.legend(loc="best")
    add_stats_box(
        ax,
        {
            "max bond rank": max_rank,
            "rank sums": "; ".join(rank_sums),
        },
        loc="upper left",
    )
    return _save(fig, Path(out_path), metadata=metadata)


def plot_multi_k_aligned_mass(
    results_by_k: Mapping[int, Sequence],
    *,
    out_path: Path,
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """Mass on fully-aligned joint policies as a function of λ.

    A "coupling tax" diagnostic: high aligned mass at large λ shows
    that the entangled posterior is concentrating onto Ising-aligned
    archetypal modes.
    """
    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.single, constrained_layout=True)
    final_masses: list[str] = []
    for K, results in sorted(results_by_k.items()):  # noqa: N806 — K = manuscript symbol.
        lams = [r.lam for r in results]
        masses = [r.aligned_mass for r in results]
        final_masses.append(f"K={K} final={masses[-1]:.3g}")
        ax.plot(lams, masses, "s-", linewidth=2.0, markersize=5, label=f"K={K}")
    apply_lambda_axis(ax)
    ax.set_ylabel("Aligned-corner mass  q(0..0) + q(1..1)")
    ax.set_title("Aligned-mass concentration with coupling")
    ax.set_ylim(0.0, 1.05)
    ax.legend(loc="best")
    if results_by_k:
        add_stats_box(
            ax,
            {
                "K values": ", ".join(str(k) for k in sorted(results_by_k)),
                "final mass": "; ".join(final_masses),
            },
            loc="lower right",
        )
    return _save(fig, Path(out_path), metadata=metadata)


# ---------------------------------------------------------------------------
# T2 — long-horizon rollout
# ---------------------------------------------------------------------------


def plot_long_horizon_marginals(
    result,
    *,
    out_path: Path,
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """Per-stream marginal time-series plus the joint total-correlation curve.

    Shows the marginals as heatmaps (time on x-axis, policy index on
    y-axis) for each stream alongside a single TC curve at the right.
    """
    n_streams = len(result.marginal_trajectories)
    fig, axes = plt.subplots(
        1,
        n_streams + 1,
        figsize=PUBLICATION_STYLE.strip(n_streams),
        gridspec_kw={"width_ratios": [3] * n_streams + [4]},
        constrained_layout=True,
    )
    for k, marg in enumerate(result.marginal_trajectories):
        im = axes[k].imshow(marg.T, origin="lower", aspect="auto", cmap="cividis")
        axes[k].set_title(f"stream {k}: q_t^{k}")
        axes[k].set_xlabel("time t")
        axes[k].set_ylabel("policy idx")
        fig.colorbar(im, ax=axes[k], shrink=0.8)
    ax_tc = axes[-1]
    ax_tc.plot(
        np.arange(result.total_correlations.size),
        result.total_correlations,
        "o-",
        markersize=3.5,
        linewidth=2.0,
        color=palette_color(6),
    )
    ax_tc.set_xlabel("time t")
    ax_tc.set_ylabel("Total correlation I(q_t) [nats]")
    ax_tc.set_title(f"T={result.T}, λ={result.lam:.2f}")
    tail_window = getattr(result, "tail_window", None)
    add_stats_box(
        ax_tc,
        {
            "T": int(result.T),
            "seed": int(result.seed),
            "TC final": float(result.total_correlations[-1]),
            "TC mean": float(np.mean(result.total_correlations)),
            "tail window": tail_window if tail_window is not None else "n/a",
        },
        loc="lower right",
    )
    return _save(fig, Path(out_path), metadata=metadata)


def plot_long_horizon_steady_state(
    result,
    *,
    out_path: Path,
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """Trailing-window marginal mean per stream plus first/mean/max tail KL."""
    n_streams = len(result.tail_marginal_means)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=PUBLICATION_STYLE.two_panel, constrained_layout=True)
    for k, mean in enumerate(result.tail_marginal_means):
        ax1.plot(
            np.arange(len(mean)),
            mean,
            "o-",
            color=palette_color(k),
            linewidth=2.0,
            markersize=6,
            label=f"stream {k}",
        )
    ax1.set_xlabel("policy idx")
    ax1.set_ylabel("trailing-window mean q^k")
    ax1.set_title(f"Steady-state trailing-window marginals (T={result.T})")
    ax1.legend(loc="best")

    x = np.arange(n_streams)
    first_kls = list(getattr(result, "tail_kl_first_per_stream", result.tail_kl_per_stream))
    mean_kls = list(getattr(result, "tail_kl_mean_per_stream", result.tail_kl_per_stream))
    max_kls = list(getattr(result, "tail_kl_max_per_stream", result.tail_kl_per_stream))
    width = 0.24
    ax2.bar(x - width, first_kls, width=width, color=palette_color(5), alpha=0.85, label="first")
    ax2.bar(x, mean_kls, width=width, color=palette_color(2), alpha=0.85, label="mean")
    ax2.bar(x + width, max_kls, width=width, color=palette_color(1), alpha=0.85, label="max")
    ax2.axhline(
        result.steady_state_tol,
        color=palette_color(6),
        linestyle="--",
        linewidth=1.4,
        label=f"tol={result.steady_state_tol:.0e}",
    )
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"k={k}" for k in range(n_streams)])
    ax2.set_ylabel("tail-window KL vs mean")
    ax2.set_title(f"Habit accumulation: {'YES' if result.habit_accumulation else 'NO'}")
    ax2.legend(loc="best")
    add_stats_box(
        ax2,
        {
            "first max": max(float(v) for v in first_kls),
            "window max": max(float(v) for v in max_kls),
            "tol": float(result.steady_state_tol),
            "habit": "yes" if result.habit_accumulation else "no",
        },
        loc="upper right",
    )
    return _save(fig, Path(out_path), metadata=metadata)


# ---------------------------------------------------------------------------
# T3 — revertibility
# ---------------------------------------------------------------------------


def plot_revertibility_witness(
    records,
    *,
    out_path: Path,
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """Two-panel revertibility figure.

    Left: I(q_λ) and KL(q_λ ‖ m(q_λ)) overlaid (the two should agree
    pointwise; any visible divergence indicates a numerical bug).
    Right: max marginal-difference at each λ (should be at floating
    floor across the full grid).
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=PUBLICATION_STYLE.two_panel, constrained_layout=True)
    lams = [r.lam for r in records]
    # Is / KLs: I = multi-information, KL = KL divergence (manuscript symbols).
    Is = [r.multi_information for r in records]  # noqa: N806
    KLs = [r.kl_q_to_mproj for r in records]  # noqa: N806
    diffs = [r.marginal_max_abs_diff for r in records]

    ax1.plot(lams, Is, "o-", linewidth=2.0, markersize=5, color=palette_color(5), label="I(q_λ)")
    ax1.plot(lams, KLs, "s--", linewidth=1.8, markersize=5, color=palette_color(1), label="KL(q ‖ m(q))")
    apply_lambda_axis(ax1)
    ax1.set_ylabel("nats")
    ax1.set_title("KL identity witness: KL = I")
    ax1.legend(loc="best")

    ax2.plot(lams, diffs, "o-", linewidth=2.0, markersize=5, color=palette_color(3))
    apply_lambda_axis(ax2)
    ax2.set_ylabel("max |q^k − m(q)^k|")
    ax2.set_title("Marginal recovery (lower is better)")
    ax2.set_yscale("symlog", linthresh=1e-12)
    residuals = [abs(a - b) for a, b in zip(Is, KLs, strict=True)]
    add_stats_box(
        ax2,
        {
            "max |KL-I|": max(residuals),
            "max marg diff": max(diffs),
            "λ count": len(lams),
        },
        loc="upper right",
    )
    return _save(fig, Path(out_path), metadata=metadata)


__all__ = [
    "plot_long_horizon_marginals",
    "plot_long_horizon_steady_state",
    "plot_multi_k_aligned_mass",
    "plot_multi_k_total_correlation",
    "plot_multi_k_tt_rank_profile",
    "plot_revertibility_witness",
]
