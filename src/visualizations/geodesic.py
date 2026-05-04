"""KL geodesic + lambda-star locus visualisations.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

ArrayF = NDArray[np.float64]


def plot_kl_geodesic_in_simplex(
    *,
    lams: Sequence[float],
    joints: Sequence[ArrayF],
    out_path: Path | str,
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
        raise ValueError(
            f"len(joints)={len(joints)} != len(lams)={len(lams)}"
        )
    alignment = np.array(
        [float(q[0, 0] + q[1, 1]) for q in joints], dtype=np.float64
    )
    disparity = np.array(
        [float(abs(q[0, 0] - q[1, 1]) + abs(q[0, 1] - q[1, 0])) for q in joints],
        dtype=np.float64,
    )
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    sc = ax.scatter(
        alignment, disparity, c=lams,
        cmap="viridis", s=40, edgecolor="white", linewidth=0.5, zorder=3,
    )
    ax.plot(alignment, disparity, "-", color="gray", linewidth=1.0, alpha=0.6, zorder=2)
    # Anchor MF point (alignment = 0.5, disparity = 0).
    ax.scatter(
        [0.5], [0.0], color="red", s=80, marker="*", zorder=4,
        label=r"mean-field ($\lambda=0$)",
    )
    ax.set_xlabel("Aligned-corner mass  q(0,0) + q(1,1)")
    ax.set_ylabel("Off-diagonal disparity  |Δrow| + |Δcol|")
    ax.set_title("K=2 Ising joint: λ-traced e-geodesic in the 2-D summary plane")
    ax.set_xlim(0.0, 1.0)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left")
    fig.colorbar(sc, ax=ax, label="coupling λ")
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_lambda_star_locus(
    *,
    utilities: Sequence[float],
    gammas: Sequence[float],
    lambda_star: ArrayF,
    out_path: Path | str,
) -> Path:
    """Heatmap of $\\lambda^\\star$ across $(\\mathrm{utility}, \\gamma)$.

    `lambda_star[i, j]` is the optimal coupling for the K=2 Ising toy
    at utility surplus `utilities[i]` and EFE precision `gammas[j]`.
    """
    import matplotlib.pyplot as plt

    out = Path(out_path)
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    extent = (
        float(gammas[0]), float(gammas[-1]),
        float(utilities[0]), float(utilities[-1]),
    )
    im = ax.imshow(
        lambda_star, origin="lower", aspect="auto",
        extent=extent, cmap="cividis",
    )
    ax.set_xlabel("Policy precision γ")
    ax.set_ylabel("Utility surplus Δ_util")
    ax.set_title(r"K=2 Ising: optimal coupling $\lambda^\star(\Delta_{\rm util}, \gamma)$")
    fig.colorbar(im, ax=ax, label=r"$\lambda^\star$")
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out
