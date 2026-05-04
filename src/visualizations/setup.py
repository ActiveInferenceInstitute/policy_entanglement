"""Common matplotlib / numpy setup hooks for figure scripts."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np


def deterministic_setup(
    *, seed: int = 0, dpi: int = 150, save_dpi: int = 200
) -> None:
    """Set headless matplotlib backend, fix RNG, and apply common rcParams.

    Idempotent: safe to call multiple times within the same process.
    """
    matplotlib.use("Agg", force=False)
    import matplotlib.pyplot as plt

    np.random.seed(int(seed))
    plt.rcParams.update({
        "figure.dpi": int(dpi),
        "savefig.dpi": int(save_dpi),
        "axes.grid": False,
        "axes.titlesize": "medium",
    })


def ensure_outdir(path: Path | str) -> Path:
    """Create the directory if missing and return the resolved Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
