"""Annotated joint-posterior figure: heatmap + marginals + residual."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from joint_dist import joint_marginals
from geometry import m_projection

ArrayF = NDArray[np.float64]


def plot_joint_heatmap_with_marginals(
    *,
    q: ArrayF,
    title: str,
    out_path: Path | str,
    xticklabels: Sequence[str] | None = None,
    yticklabels: Sequence[str] | None = None,
) -> Path:
    """Plot a 2D joint posterior with side marginals and a residual panel."""
    import matplotlib.pyplot as plt

    if q.ndim != 2:
        raise ValueError(
            f"plot_joint_heatmap_with_marginals requires K=2, got {q.ndim}"
        )
    out = Path(out_path)
    margs = joint_marginals(q)
    proj = m_projection(q)
    residual = q - proj

    fig = plt.figure(figsize=(7.5, 6.5))
    gs = fig.add_gridspec(
        2, 3,
        width_ratios=[5, 1, 0.3],
        height_ratios=[1, 5],
        wspace=0.05, hspace=0.05,
    )
    ax_top = fig.add_subplot(gs[0, 0])
    ax_main = fig.add_subplot(gs[1, 0], sharex=ax_top)
    ax_right = fig.add_subplot(gs[1, 1], sharey=ax_main)
    ax_resid = fig.add_subplot(gs[0, 1])

    im = ax_main.imshow(q, origin="lower", aspect="auto", cmap="viridis")
    ax_main.set_xlabel("Stream 0 policy index")
    ax_main.set_ylabel("Stream 1 policy index")
    if xticklabels is not None:
        ax_main.set_xticks(range(q.shape[1]))
        ax_main.set_xticklabels(xticklabels)
    if yticklabels is not None:
        ax_main.set_yticks(range(q.shape[0]))
        ax_main.set_yticklabels(yticklabels)

    ax_top.bar(range(q.shape[1]), margs[1], color="steelblue")
    ax_top.set_title(title)
    ax_top.set_ylabel("q_1")
    ax_top.tick_params(axis="x", labelbottom=False)

    ax_right.barh(range(q.shape[0]), margs[0], color="indianred")
    ax_right.set_xlabel("q_0")
    ax_right.tick_params(axis="y", labelleft=False)

    ax_resid.imshow(residual, origin="lower", aspect="auto", cmap="coolwarm")
    ax_resid.set_title("residual\nq − ∏ q^k", fontsize=8)
    ax_resid.tick_params(labelbottom=False, labelleft=False)

    cax = fig.add_subplot(gs[1, 2])
    fig.colorbar(im, cax=cax)

    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out
