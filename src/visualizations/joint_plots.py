"""Annotated joint-posterior figure: heatmap + marginals + residual."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from lean.geometry import m_projection
from lean.joint_dist import joint_marginals

from ._io import _save_with_metadata as _save
from .annotations import add_stats_box
from .setup import DIVERGING_CMAP, PUBLICATION_STYLE, SEQUENTIAL_CMAP, palette_color

ArrayF = NDArray[np.float64]


def plot_joint_heatmap_with_marginals(
    *,
    q: ArrayF,
    title: str,
    out_path: Path | str,
    xticklabels: Sequence[str] | None = None,
    yticklabels: Sequence[str] | None = None,
    metadata=None,
) -> Path:
    """Plot a 2D joint posterior with side marginals and a residual panel."""
    import matplotlib.pyplot as plt

    if q.ndim != 2:
        raise ValueError(f"plot_joint_heatmap_with_marginals requires K=2, got {q.ndim}")
    out = Path(out_path)
    margs = joint_marginals(q)
    proj = m_projection(q)
    residual = q - proj

    fig = plt.figure(figsize=PUBLICATION_STYLE.dashboard_2x2, constrained_layout=True)
    gs = fig.add_gridspec(
        2,
        3,
        width_ratios=[5, 1, 0.3],
        height_ratios=[1, 5],
        wspace=0.05,
        hspace=0.05,
    )
    ax_top = fig.add_subplot(gs[0, 0])
    ax_main = fig.add_subplot(gs[1, 0], sharex=ax_top)
    ax_right = fig.add_subplot(gs[1, 1], sharey=ax_main)
    ax_resid = fig.add_subplot(gs[0, 1])

    im = ax_main.imshow(q, origin="lower", aspect="auto", cmap=SEQUENTIAL_CMAP)
    ax_main.set_xlabel("Stream 0 policy index")
    ax_main.set_ylabel("Stream 1 policy index")
    if xticklabels is not None:
        ax_main.set_xticks(range(q.shape[1]))
        ax_main.set_xticklabels(xticklabels)
    if yticklabels is not None:
        ax_main.set_yticks(range(q.shape[0]))
        ax_main.set_yticklabels(yticklabels)

    ax_top.bar(range(q.shape[1]), margs[1], color=palette_color(5))
    ax_top.set_title(title)
    ax_top.set_ylabel("q_1")
    ax_top.tick_params(axis="x", labelbottom=False)

    ax_right.barh(range(q.shape[0]), margs[0], color=palette_color(6))
    ax_right.set_xlabel("q_0")
    ax_right.tick_params(axis="y", labelleft=False)

    ax_resid.imshow(residual, origin="lower", aspect="auto", cmap=DIVERGING_CMAP)
    ax_resid.set_title("residual\nq - product marginals", fontsize=PUBLICATION_STYLE.title_size)
    ax_resid.tick_params(labelbottom=False, labelleft=False)

    with np.errstate(divide="ignore", invalid="ignore"):
        log_ratio = np.where(q > 0.0, np.log(q / proj), 0.0)
    total_correlation = float(np.sum(np.where(q > 0.0, q * log_ratio, 0.0)))
    add_stats_box(
        ax_main,
        [
            f"shape={q.shape[0]}x{q.shape[1]}",
            f"TC={total_correlation:.4f} nats",
            f"max |residual|={float(np.max(np.abs(residual))):.3g}",
        ],
        loc="upper left",
    )

    cax = fig.add_subplot(gs[1, 2])
    fig.colorbar(im, cax=cax)

    return _save(fig, out, metadata=metadata)
