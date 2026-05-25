"""Spectral-structure figures: archetype dendrogram, TT-rank surface."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from ._io import _save_with_metadata as _save
from .annotations import add_stats_box
from .setup import DIVERGING_CMAP, PUBLICATION_STYLE, SEQUENTIAL_ALT_CMAP, palette_color

ArrayF = NDArray[np.float64]


def plot_archetype_dendrogram(
    *,
    weights: Sequence[float],
    overlap_matrix: ArrayF,
    out_path: Path | str,
    metadata=None,
) -> Path:
    """Bar chart of Schmidt weights + heatmap of pairwise archetype overlap."""
    import matplotlib.pyplot as plt

    out = Path(out_path)
    n_archetypes = len(weights)
    fig, axes = plt.subplots(
        1,
        2,
        figsize=PUBLICATION_STYLE.two_panel,
        gridspec_kw={"width_ratios": [1, 2]},
        constrained_layout=True,
    )
    axes[0].bar(range(n_archetypes), weights, color=palette_color(1))
    axes[0].set_xticks(range(n_archetypes))
    axes[0].set_xticklabels([f"α={i}" for i in range(n_archetypes)])
    axes[0].set_ylabel("Schmidt weight s_α")
    axes[0].set_title("Archetype weights")

    add_stats_box(
        axes[0],
        [
            f"archetypes={n_archetypes}",
            f"weight sum={float(np.sum(weights)):.3f}",
            f"max weight={float(np.max(weights)):.3f}",
        ],
        loc="upper right",
    )

    im = axes[1].imshow(overlap_matrix, vmin=0.0, vmax=1.0, cmap=DIVERGING_CMAP)
    axes[1].set_title("Pairwise archetype overlap")
    axes[1].set_xticks(range(n_archetypes))
    axes[1].set_yticks(range(n_archetypes))
    fig.colorbar(im, ax=axes[1], shrink=0.85)

    return _save(fig, out, metadata=metadata)


def plot_tensor_train_rank_surface(
    *,
    k_values: Sequence[int],
    rank_profiles: Sequence[Sequence[int]],
    out_path: Path | str,
    metadata=None,
) -> Path:
    """Show TT-rank profiles across multiple stream counts `K`.

    Each row in `rank_profiles` is `[r_1, r_2, ..., r_{K-1}]` for one
    `K`; rows are padded to the longest profile with NaN so the heatmap
    shape is rectangular.
    """
    import matplotlib.pyplot as plt

    out = Path(out_path)
    k_max = max(len(p) for p in rank_profiles)
    mat = np.full((len(k_values), k_max), np.nan, dtype=np.float64)
    for i, prof in enumerate(rank_profiles):
        for j, r in enumerate(prof):
            mat[i, j] = float(r)
    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.single, constrained_layout=True)
    im = ax.imshow(mat, origin="lower", aspect="auto", cmap=SEQUENTIAL_ALT_CMAP)
    ax.set_xticks(range(k_max))
    ax.set_xticklabels([f"cut {j + 1}" for j in range(k_max)])
    ax.set_yticks(range(len(k_values)))
    ax.set_yticklabels([f"K={k}" for k in k_values])
    ax.set_title("Tensor-train rank profiles across stream counts K")
    fig.colorbar(im, ax=ax, label="bond rank r_j")
    finite = mat[np.isfinite(mat)]
    if finite.size:
        add_stats_box(
            ax,
            [
                f"K values={','.join(str(k) for k in k_values)}",
                f"max rank={int(np.max(finite))}",
                f"profile width={k_max}",
            ],
            loc="upper left",
        )
    return _save(fig, out, metadata=metadata)
