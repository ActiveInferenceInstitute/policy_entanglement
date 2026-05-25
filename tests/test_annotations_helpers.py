"""Coverage for visualization annotation helpers."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from visualizations.annotations import (
    add_claim_strength_tag,
    add_mean_field_baseline,
    add_saturation_marker,
    add_tolerance_band,
)


def test_annotation_helpers_draw_on_axes() -> None:
    fig, ax = plt.subplots(figsize=(4, 3))
    add_mean_field_baseline(ax, 0.0, label="MF baseline")
    add_tolerance_band(ax, 0.5, 0.1, label="tol")
    add_saturation_marker(ax, 1.0, 0.2)
    for kind in ("empirical", "witness", "hypothesis", "analytical", "unknown"):
        add_claim_strength_tag(ax, kind, loc="upper right")
    for loc in ("upper left", "lower right", "lower left", "bogus"):
        add_claim_strength_tag(ax, "empirical", loc=loc)
    plt.close(fig)
