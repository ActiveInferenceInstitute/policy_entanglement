"""e-geodesic figure: log-weight flow lines vs λ (Theorem 6.4)."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

ArrayF = NDArray[np.float64]


def plot_log_weight_flow(
    *,
    lams: Sequence[float],
    log_weights: ArrayF,
    out_path: Path | str,
    pi_labels: Sequence[str] | None = None,
) -> Path:
    """Plot per-policy unnormalised log-weight as a function of `λ`.

    Each column of `log_weights[i, p]` is the log-weight of policy `p` at
    `lams[i]`. Theorem 6.4 says these are affine in λ.
    """
    import matplotlib.pyplot as plt

    out = Path(out_path)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    P = log_weights.shape[1]
    cmap = plt.get_cmap("tab10")
    for p in range(P):
        ax.plot(
            lams, log_weights[:, p],
            label=pi_labels[p] if pi_labels else f"π={p}",
            linewidth=1.5,
            color=cmap(p % 10),
        )
    ax.set_xlabel("Coupling λ")
    ax.set_ylabel("Unnormalised log-weight")
    ax.set_title("e-geodesic: log-weight is affine in λ (Theorem 6.4)")
    ax.legend(loc="best", fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out
