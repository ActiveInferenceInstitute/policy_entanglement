"""Heatmaps over (λ, utility) — phase landscape and Schmidt entropy."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from ._io import _save_with_metadata as _save
from .annotations import ENTROPY_LABEL, LAMBDA_LABEL, add_stats_box
from .setup import PUBLICATION_STYLE, SEQUENTIAL_CMAP

ArrayF = NDArray[np.float64]
# Accept both plain Python sequences and numpy float arrays as 1-D
# grid inputs.  Scripts often pass ``H.PARAMETER_SWEEP_LAMBDAS.values()``
# which returns ``ndarray[float64]``; this union keeps mypy happy
# without a per-call ``cast``.
FloatGrid = Sequence[float] | NDArray[np.float64]


def plot_lambda_utility_heatmap(
    *,
    lams: FloatGrid,
    utilities: FloatGrid,
    score: ArrayF,
    title: str,
    cbar_label: str,
    out_path: Path | str,
    cmap: str = SEQUENTIAL_CMAP,
    metadata=None,
) -> Path:
    """Render a heatmap of `score[i, j]` over `(utility_i, lam_j)`."""
    import matplotlib.pyplot as plt

    out = Path(out_path)
    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.single, constrained_layout=True)
    extent = (
        float(lams[0]),
        float(lams[-1]),
        float(utilities[0]),
        float(utilities[-1]),
    )
    im = ax.imshow(
        score,
        origin="lower",
        aspect="auto",
        extent=extent,
        cmap=cmap,
        interpolation="nearest",
    )
    ax.set_xlabel(LAMBDA_LABEL)
    ax.set_ylabel(r"Utility surplus $\Delta_{\mathrm{util}}$")
    ax.set_title(title)
    fig.colorbar(im, ax=ax, label=cbar_label)
    finite = score[np.isfinite(score)]
    if finite.size:
        add_stats_box(
            ax,
            [
                f"grid={len(utilities)}x{len(lams)}",
                f"min={float(np.min(finite)):.3g}, max={float(np.max(finite)):.3g}",
                f"mean={float(np.mean(finite)):.3g}",
            ],
            loc="upper left",
        )
    return _save(fig, out, metadata=metadata)


def plot_schmidt_entropy_surface(
    *,
    lams: FloatGrid,
    utilities: FloatGrid,
    entropies: ArrayF,
    out_path: Path | str,
    metadata=None,
) -> Path:
    """Schmidt-entropy heatmap across `(λ, utility)`."""
    return plot_lambda_utility_heatmap(
        lams=lams,
        utilities=utilities,
        score=entropies,
        title=r"K=2 Ising: entanglement entropy $S_E(\lambda, \Delta_{\mathrm{util}})$",
        cbar_label=ENTROPY_LABEL,
        out_path=out_path,
        cmap="magma",
        metadata=metadata,
    )
