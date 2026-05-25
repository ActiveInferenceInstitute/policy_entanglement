"""KL geodesic + lambda-star locus visualizations."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from ._io import _save_with_metadata as _save
from .annotations import add_stats_box
from .setup import PUBLICATION_STYLE, SEQUENTIAL_CMAP, palette_color

ArrayF = NDArray[np.float64]
# Callers pass either Python lists or numpy float arrays as 1-D grids.
FloatGrid = Sequence[float] | NDArray[np.float64]


def plot_kl_geodesic_in_simplex(
    *,
    lams: FloatGrid,
    joints: Sequence[ArrayF],
    out_path: Path | str,
    metadata=None,
) -> Path:
    """Visualise the e-geodesic of K=2 joints `q_lam` projected onto a
    2-D coordinate plane spanned by the two summary statistics
    (alignment fraction, off-diagonal disparity).

    `joints` must be a sequence of `(2,2)` PMFs, one per `lams[i]`.
    The trace shows the geodesic departing the mean-field point
    (uniform alignment, zero disparity) at $\\lambda = 0$ and bending
    toward an archetypal corner as $|\\lambda|$ grows.
    """
    import matplotlib.pyplot as plt

    out = Path(out_path)
    if len(joints) != len(lams):
        raise ValueError(f"len(joints)={len(joints)} != len(lams)={len(lams)}")
    alignment = np.array([float(q[0, 0] + q[1, 1]) for q in joints], dtype=np.float64)
    disparity = np.array(
        [float(abs(q[0, 0] - q[1, 1]) + abs(q[0, 1] - q[1, 0])) for q in joints],
        dtype=np.float64,
    )
    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.single, constrained_layout=True)
    sc = ax.scatter(
        alignment,
        disparity,
        c=lams,
        cmap=SEQUENTIAL_CMAP,
        s=40,
        edgecolor="white",
        linewidth=0.5,
        zorder=3,
    )
    ax.plot(alignment, disparity, "-", color="#666666", linewidth=1.2, alpha=0.75, zorder=2)
    # Anchor MF point (alignment = 0.5, disparity = 0).
    ax.scatter(
        [0.5],
        [0.0],
        color=palette_color(6),
        s=80,
        marker="*",
        zorder=4,
        label=r"mean-field ($\lambda=0$)",
    )
    ax.set_xlabel("Aligned-corner mass  q(0,0) + q(1,1)")
    ax.set_ylabel("Off-diagonal disparity  |Δrow| + |Δcol|")
    ax.set_title("K=2 Ising joint: λ-traced e-geodesic in the 2-D summary plane")
    ax.set_xlim(0.0, 1.0)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left")
    fig.colorbar(sc, ax=ax, label="coupling λ")
    add_stats_box(
        ax,
        [
            f"lambda grid={len(lams)}",
            f"alignment range=[{float(np.min(alignment)):.3f}, {float(np.max(alignment)):.3f}]",
            f"max disparity={float(np.max(disparity)):.3f}",
        ],
        loc="lower right",
    )
    return _save(fig, out, metadata=metadata)


def plot_lambda_star_locus(
    *,
    utilities: FloatGrid,
    gammas: FloatGrid,
    lambda_star: ArrayF,
    out_path: Path | str,
    metadata=None,
) -> Path:
    """Heatmap of $\\lambda^\\star$ across $(\\mathrm{utility}, \\gamma)$.

    `lambda_star[i, j]` is the optimal coupling for the K=2 Ising toy
    at utility surplus `utilities[i]` and EFE precision `gammas[j]`.
    """
    import matplotlib.pyplot as plt

    out = Path(out_path)
    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.single, constrained_layout=True)
    extent = (
        float(gammas[0]),
        float(gammas[-1]),
        float(utilities[0]),
        float(utilities[-1]),
    )
    im = ax.imshow(
        lambda_star,
        origin="lower",
        aspect="auto",
        extent=extent,
        cmap="cividis",
    )
    ax.set_xlabel("Policy precision γ")
    ax.set_ylabel("Utility surplus Δ_util")
    ax.set_title(r"K=2 Ising: optimal coupling $\lambda^\star(\Delta_{\rm util}, \gamma)$")
    fig.colorbar(im, ax=ax, label=r"$\lambda^\star$")
    finite = lambda_star[np.isfinite(lambda_star)]
    if finite.size:
        add_stats_box(
            ax,
            [
                f"grid={len(utilities)}x{len(gammas)}",
                f"min={float(np.min(finite)):.3f}, max={float(np.max(finite)):.3f}",
                f"mean={float(np.mean(finite)):.3f}",
            ],
            loc="upper left",
        )
    return _save(fig, out, metadata=metadata)
