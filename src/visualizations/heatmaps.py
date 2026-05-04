"""Heatmaps over (λ, utility) — phase landscape and Schmidt entropy."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

ArrayF = NDArray[np.float64]


def plot_lambda_utility_heatmap(
    *,
    lams: Sequence[float],
    utilities: Sequence[float],
    score: ArrayF,
    title: str,
    cbar_label: str,
    out_path: Path | str,
    cmap: str = "viridis",
) -> Path:
    """Render a heatmap of `score[i, j]` over `(utility_i, lam_j)`."""
    import matplotlib.pyplot as plt

    out = Path(out_path)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    extent = (
        float(lams[0]), float(lams[-1]),
        float(utilities[0]), float(utilities[-1]),
    )
    im = ax.imshow(
        score,
        origin="lower",
        aspect="auto",
        extent=extent,
        cmap=cmap,
    )
    ax.set_xlabel("Coupling λ")
    ax.set_ylabel("Utility")
    ax.set_title(title)
    fig.colorbar(im, ax=ax, label=cbar_label)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_schmidt_entropy_surface(
    *,
    lams: Sequence[float],
    utilities: Sequence[float],
    entropies: ArrayF,
    out_path: Path | str,
) -> Path:
    """Schmidt-entropy heatmap across `(λ, utility)`."""
    return plot_lambda_utility_heatmap(
        lams=lams,
        utilities=utilities,
        score=entropies,
        title="K=2 Ising: entanglement entropy S_E(λ, utility)",
        cbar_label="S_E(q_λ)  [nats]",
        out_path=out_path,
        cmap="magma",
    )
