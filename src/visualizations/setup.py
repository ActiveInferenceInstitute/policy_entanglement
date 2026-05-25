"""Common matplotlib / numpy setup hooks for figure scripts.

Provides a single :func:`deterministic_setup` that pins a headless
backend, fixes the RNG, and configures matplotlib for *accessible*
output: a colorblind-safe categorical palette (Okabe & Ito, 2008),
sequential colormaps that remain perceptually uniform when printed in
grayscale (``viridis`` / ``magma`` / ``cividis``), tight titles, and
slightly heavier default linewidths so curves remain legible at the
1-column journal width that the manuscript embeds figures into.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib

# Okabe & Ito (2008) — eight-color categorical palette designed to remain
# distinguishable for the most common forms of color vision deficiency.
# Used as the default `axes.prop_cycle` so every line / scatter color in
# the manuscript is colorblind-safe by construction.
COLORBLIND_PALETTE: tuple[str, ...] = (
    "#000000",  # black
    "#E69F00",  # orange
    "#56B4E9",  # sky blue
    "#009E73",  # bluish green
    "#F0E442",  # yellow
    "#0072B2",  # blue
    "#D55E00",  # vermillion
    "#CC79A7",  # reddish purple
)

# Sequential colormaps used across the heatmap suite.  All three are
# perceptually uniform and remain monotonic when printed in grayscale.
SEQUENTIAL_CMAP: str = "viridis"
SEQUENTIAL_ALT_CMAP: str = "magma"
DIVERGING_CMAP: str = "RdBu_r"


@dataclass(frozen=True)
class FigureStyle:
    """Publication figure sizing and typography constants.

    The plotting helpers use these values instead of ad hoc
    ``figsize=...`` / ``fontsize=...`` literals so dashboards, single
    panels, and long-horizon strips scale coherently in the PDF.
    """

    single: tuple[float, float] = (8.4, 5.2)
    wide: tuple[float, float] = (11.0, 5.2)
    two_panel: tuple[float, float] = (11.5, 5.4)
    dashboard_2x2: tuple[float, float] = (13.6, 9.2)
    dashboard_2x3: tuple[float, float] = (16.4, 9.8)
    strip_base_width: float = 5.6
    strip_per_stream_width: float = 4.1
    strip_height: float = 5.0
    # Font sizes bumped one notch for projector / single-column print
    # clarity. Test pins require title >= 14, tick >= 12, legend >= 10
    # (tests/test_visualizations.py); the values below preserve those
    # floors while widening headroom for axis-tick crowding.
    title_size: float = 16.0
    label_size: float = 14.0
    tick_size: float = 13.0
    legend_size: float = 11.0
    annotation_size: float = 10.5
    provenance_size: float = 9.0
    theorem_badge_size: float = 10.5

    def strip(self, n_streams: int) -> tuple[float, float]:
        """Width for per-stream heatmap strips plus one summary panel."""
        return (
            self.strip_base_width + self.strip_per_stream_width * max(int(n_streams), 1),
            self.strip_height,
        )


PUBLICATION_STYLE = FigureStyle()


def palette_color(index: int) -> str:
    """Return a deterministic colorblind-safe categorical color."""
    return COLORBLIND_PALETTE[int(index) % len(COLORBLIND_PALETTE)]


def deterministic_setup(
    *,
    seed: int = 0,
    dpi: int = 180,
    save_dpi: int = 360,
) -> None:
    """Set headless matplotlib backend, fix RNG, apply accessible rcParams.

    Idempotent: safe to call multiple times within the same process.

    Configures:
    * ``Agg`` backend (no display required, deterministic raster output).
    * Figure / save DPI for crisp rendering at the manuscript's column width.
    * Colourblind-safe categorical cycle (Okabe & Ito, 2008).
    * Default sequential colormap pinned to ``viridis``.
    * Title size and linewidth defaults tuned for the embedded figure size.

    Note (RedTeam Methods H1, 2026-05-20): this function does NOT seed
    the legacy ``np.random`` global RNG.  Every modern sampling path
    uses ``np.random.default_rng(seed)`` and threads its own ``Generator``
    explicitly — the legacy global seed is shared by neither layer and
    silently failed to protect samples that thought they were seeded.
    The ``seed`` parameter is preserved for API stability and is used by
    callers that build their own ``default_rng(seed)`` downstream.
    """
    matplotlib.use("Agg", force=False)
    import matplotlib.pyplot as plt
    from cycler import cycler

    _ = int(seed)  # kept for API stability; modern callers use default_rng
    plt.rcParams.update(
        {
            # Output resolution (bumped 170/300 → 180/360 — ultra-crisp print)
            "figure.dpi": int(dpi),
            "savefig.dpi": int(save_dpi),
            # Axes / labels
            "figure.figsize": (7.6, 5.0),
            "axes.grid": True,
            "axes.grid.which": "both",
            "grid.alpha": 0.24,
            "grid.linewidth": 0.7,
            "grid.color": "#9aa0a6",
            "axes.titlesize": PUBLICATION_STYLE.title_size,
            "axes.titleweight": "bold",
            "axes.titlepad": 12,
            "axes.labelsize": PUBLICATION_STYLE.label_size,
            "axes.labelpad": 8,
            "axes.linewidth": 1.1,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.prop_cycle": cycler(color=list(COLORBLIND_PALETTE)),
            # Tick + legend
            "xtick.labelsize": PUBLICATION_STYLE.tick_size,
            "ytick.labelsize": PUBLICATION_STYLE.tick_size,
            "xtick.major.width": 1.0,
            "ytick.major.width": 1.0,
            "xtick.minor.visible": True,
            "ytick.minor.visible": True,
            "xtick.minor.width": 0.6,
            "ytick.minor.width": 0.6,
            "legend.fontsize": PUBLICATION_STYLE.legend_size,
            "legend.frameon": False,
            "legend.handlelength": 2.2,
            "legend.borderaxespad": 0.7,
            # Lines + markers (slightly heavier so curves are visible at
            # 1-column width and remain readable when projected)
            "lines.linewidth": 2.4,
            "lines.markersize": 6.5,
            "lines.markeredgewidth": 1.0,
            # Default sequential colormap (overridable per-call).
            "image.cmap": SEQUENTIAL_CMAP,
            "image.interpolation": "nearest",
            # Font
            "font.size": 13.0,
            "font.family": "sans-serif",
            "figure.titlesize": PUBLICATION_STYLE.title_size,
            "figure.titleweight": "bold",
            # Save behavior
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.10,
            "savefig.facecolor": "white",
            "savefig.transparent": False,
        }
    )


def ensure_outdir(path: Path | str) -> Path:
    """Create the directory if missing and return the resolved Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
