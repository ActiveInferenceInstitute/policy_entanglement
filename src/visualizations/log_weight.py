"""e-geodesic figure: log-weight flow lines vs λ (Theorem 7.4)."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from ._io import _save_with_metadata as _save
from .annotations import add_stats_box, apply_lambda_axis, pin_theorem
from .setup import PUBLICATION_STYLE, palette_color

ArrayF = NDArray[np.float64]
# Callers pass either Python lists or numpy float arrays as 1-D grids.
FloatGrid = Sequence[float] | NDArray[np.float64]


def plot_log_weight_flow(
    *,
    lams: FloatGrid,
    log_weights: ArrayF,
    out_path: Path | str,
    pi_labels: Sequence[str] | None = None,
    metadata=None,
) -> Path:
    """Plot per-policy unnormalized log-weight as a function of `λ`.

    Each column of `log_weights[i, p]` is the log-weight of policy `p` at
    `lams[i]`. Theorem 7.4 says these are affine in λ.
    """
    import matplotlib.pyplot as plt

    out = Path(out_path)
    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.single, constrained_layout=True)
    n_policies = log_weights.shape[1]
    for p in range(n_policies):
        ax.plot(
            lams,
            log_weights[:, p],
            label=pi_labels[p] if pi_labels else f"$\\pi={p}$",
            linewidth=2.0,
            color=palette_color(p),
        )
    ax.set_ylabel(r"Unnormalized log-weight $\log \mathcal{E}_\lambda(\pi)$")
    ax.set_title(r"e-geodesic: every policy's log-weight is affine in $\lambda$")
    ax.legend(loc="best", fontsize=PUBLICATION_STYLE.legend_size, title="policy")
    apply_lambda_axis(ax)
    pin_theorem(ax, "Thm 7.4", loc="lower right")
    lam_arr = np.asarray(lams, dtype=np.float64)
    if lam_arr.size == 0:
        raise ValueError("lams must be non-empty")
    if lam_arr.size >= 2:
        residuals = []
        for p in range(n_policies):
            coeff = np.polyfit(lam_arr, log_weights[:, p], deg=1)
            fitted = np.polyval(coeff, lam_arr)
            residuals.append(float(np.max(np.abs(log_weights[:, p] - fitted))))
        max_residual = max(residuals)
    else:
        max_residual = 0.0
    add_stats_box(
        ax,
        [
            f"policies={n_policies}, lambda grid={len(lam_arr)}",
            f"range=[{float(lam_arr[0]):.2f}, {float(lam_arr[-1]):.2f}]",
            f"max affine residual={max_residual:.2e}",
        ],
        loc="upper left",
    )
    return _save(fig, out, metadata=metadata)
