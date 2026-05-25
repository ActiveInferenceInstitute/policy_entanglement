"""Shared I/O helpers for the visualizations subpackage.

Private to ``src/visualizations``; not exported from the package
``__init__``.  The save helper centralizes the
``tight_layout → savefig(metadata=...) → close → return path`` pattern
used by every plot helper that emits a PNG.
"""

from __future__ import annotations

import json
import warnings
from collections.abc import Mapping
from pathlib import Path

import matplotlib.pyplot as plt

from .metadata import figure_statistics


def _save_with_metadata(
    fig,
    out_path: Path,
    *,
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """Tight-layout, save with PNG ``tEXt`` metadata, close figure, return path."""
    out_path = Path(out_path)
    if not fig.get_constrained_layout():
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="This figure includes Axes that are not compatible with tight_layout.*",
                category=UserWarning,
            )
            fig.tight_layout()
    md = dict(metadata or {})
    md.setdefault(
        "project.figure_statistics",
        json.dumps(figure_statistics(fig), separators=(",", ":"), default=str),
    )
    fig.savefig(out_path, bbox_inches="tight", metadata=md)
    plt.close(fig)
    return out_path
