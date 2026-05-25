"""Rollout trajectory figure: per-stream marginal time-series + total"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from ._io import _save_with_metadata as _save
from .annotations import add_stats_box
from .setup import PUBLICATION_STYLE, SEQUENTIAL_ALT_CMAP, palette_color

ArrayF = NDArray[np.float64]


def plot_rollout_marginals(
    *,
    marginals_per_stream: Sequence[ArrayF],
    titles: Sequence[str],
    total_correlations: ArrayF,
    out_path: Path | str,
    metadata=None,
) -> Path:
    """Render per-stream marginal time-series side-by-side with the
    coupled total-correlation curve.  Each marginal is a `(T, |Pi^k|)`
    matrix shown as a heatmap.
    """
    import matplotlib.pyplot as plt

    out = Path(out_path)
    n_streams = len(marginals_per_stream)
    if n_streams < 1:
        raise ValueError("marginals_per_stream must be non-empty")
    if len(total_correlations) < 1:
        raise ValueError("total_correlations must be non-empty")
    fig, axes = plt.subplots(
        1,
        n_streams + 1,
        figsize=PUBLICATION_STYLE.strip(n_streams),
        gridspec_kw={"width_ratios": [3] * n_streams + [4]},
        constrained_layout=True,
    )
    # `subplots(1, n)` returns a 1-D ndarray when n>1 and a single Axes when n==1;
    # n_streams + 1 ≥ 2 here so axes is always indexable.
    for k, (marginal_t, t) in enumerate(
        zip(marginals_per_stream, titles, strict=True),
    ):
        im = axes[k].imshow(marginal_t.T, origin="lower", aspect="auto", cmap=SEQUENTIAL_ALT_CMAP)
        axes[k].set_title(t)
        axes[k].set_xlabel("time t")
        axes[k].set_ylabel("policy idx")
        fig.colorbar(im, ax=axes[k], shrink=0.8)
    ax_tc = axes[-1]
    ax_tc.plot(total_correlations, "o-", markersize=4, linewidth=2.0, color=palette_color(6))
    ax_tc.set_xlabel("time t")
    ax_tc.set_ylabel("Total correlation I(q_t)  [nats]")
    ax_tc.set_title("Coupled-ensemble total correlation")
    ax_tc.grid(alpha=0.3)
    add_stats_box(
        ax_tc,
        [
            f"T={len(total_correlations)}",
            f"max TC={float(np.max(total_correlations)):.4f}",
            f"final TC={float(total_correlations[-1]):.4f}",
        ],
        loc="upper right",
    )
    return _save(fig, out, metadata=metadata)
