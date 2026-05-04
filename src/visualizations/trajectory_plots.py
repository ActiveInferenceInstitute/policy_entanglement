"""Rollout trajectory figure: per-stream marginal time-series + total
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

ArrayF = NDArray[np.float64]


def plot_rollout_marginals(
    *,
    marginals_per_stream: Sequence[ArrayF],
    titles: Sequence[str],
    total_correlations: ArrayF,
    out_path: Path | str,
) -> Path:
    """Render per-stream marginal time-series side-by-side with the
    coupled total-correlation curve.  Each marginal is a `(T, |Pi^k|)`
    matrix shown as a heatmap.
    """
    import matplotlib.pyplot as plt
    out = Path(out_path)
    K = len(marginals_per_stream)
    if K < 1:
        raise ValueError("marginals_per_stream must be non-empty")
    fig, axes = plt.subplots(
        1, K + 1, figsize=(4 + 3 * K, 3.2),
        gridspec_kw={"width_ratios": [3] * K + [4]},
    )
    # `subplots(1, n)` returns a 1-D ndarray when n>1 and a single Axes when n==1;
    # K + 1 ≥ 2 here so axes is always indexable.
    for k, (M, t) in enumerate(zip(marginals_per_stream, titles)):
        im = axes[k].imshow(M.T, origin="lower", aspect="auto", cmap="cividis")
        axes[k].set_title(t)
        axes[k].set_xlabel("time t")
        axes[k].set_ylabel("policy idx")
        fig.colorbar(im, ax=axes[k], shrink=0.8)
    ax_tc = axes[-1]
    ax_tc.plot(total_correlations, "o-", markersize=3, linewidth=1.5, color="crimson")
    ax_tc.set_xlabel("time t")
    ax_tc.set_ylabel("Total correlation I(q_t)  [nats]")
    ax_tc.set_title("Coupled-ensemble total correlation")
    ax_tc.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out
