"""Spectral-structure figures: archetype dendrogram, TT-rank surface."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

ArrayF = NDArray[np.float64]


def plot_archetype_dendrogram(
    *,
    weights: Sequence[float],
    overlap_matrix: ArrayF,
    out_path: Path | str,
) -> Path:
    """Bar chart of Schmidt weights + heatmap of pairwise archetype overlap."""
    import matplotlib.pyplot as plt

    out = Path(out_path)
    R = len(weights)
    fig, axes = plt.subplots(
        1, 2, figsize=(8, 3.6),
        gridspec_kw={"width_ratios": [1, 2]},
    )
    axes[0].bar(range(R), weights, color="goldenrod")
    axes[0].set_xticks(range(R))
    axes[0].set_xticklabels([f"α={i}" for i in range(R)])
    axes[0].set_ylabel("Schmidt weight s_α")
    axes[0].set_title("Archetype weights")

    im = axes[1].imshow(overlap_matrix, vmin=0.0, vmax=1.0, cmap="coolwarm")
    axes[1].set_title("Pairwise archetype overlap")
    axes[1].set_xticks(range(R))
    axes[1].set_yticks(range(R))
    fig.colorbar(im, ax=axes[1], shrink=0.85)

    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_tensor_train_rank_surface(
    *,
    K_values: Sequence[int],
    rank_profiles: Sequence[Sequence[int]],
    out_path: Path | str,
) -> Path:
    """Show TT-rank profiles across multiple stream counts `K`.

    Each row in `rank_profiles` is `[r_1, r_2, ..., r_{K-1}]` for one
    `K`; rows are padded to the longest profile with NaN so the heatmap
    shape is rectangular.
    """
    import matplotlib.pyplot as plt
    out = Path(out_path)
    K_max = max(len(p) for p in rank_profiles)
    M = np.full((len(K_values), K_max), np.nan, dtype=np.float64)
    for i, prof in enumerate(rank_profiles):
        for j, r in enumerate(prof):
            M[i, j] = float(r)
    fig, ax = plt.subplots(figsize=(6.5, 3.5))
    im = ax.imshow(M, origin="lower", aspect="auto", cmap="plasma")
    ax.set_xticks(range(K_max))
    ax.set_xticklabels([f"cut {j+1}" for j in range(K_max)])
    ax.set_yticks(range(len(K_values)))
    ax.set_yticklabels([f"K={k}" for k in K_values])
    ax.set_title("Tensor-train rank profiles across stream counts K")
    fig.colorbar(im, ax=ax, label="bond rank r_j")
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out
