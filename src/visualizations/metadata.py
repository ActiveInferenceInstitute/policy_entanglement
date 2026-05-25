"""Reproducibility-metadata helpers for matplotlib PNG output.

Every figure emitted by the project carries a tEXt-chunk metadata
block: source script, generating function, hyperparameter snapshot
(JSON), git revision (when available), ISO timestamp.  Inspect with::

    exiftool output/figures/foo.png

or programmatically::

    from PIL import Image
    Image.open("output/figures/foo.png").info

The metadata is keyed under stable strings prefixed with ``project.``
to avoid collision with Matplotlib's defaults.
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

_ISO_FMT = "iso8601_utc_milliseconds"
_MAX_AUTOSTAT_SERIES = 40
FIGURE_METADATA_SCHEMA_VERSION = 2

VALID_UNCERTAINTY_SEMANTICS = frozenset(
    {
        "deterministic_grid",
        "canonical_seed",
        "replicate_envelope",
        "confidence_interval",
        "analytical_schematic",
    }
)


def _font_size(value: Any) -> float | None:
    """Return an artist font size as float, if available."""

    getter = getattr(value, "get_fontsize", None)
    if not callable(getter):
        return None
    try:
        return float(getter())
    except (TypeError, ValueError):
        return None


def _visible_label_font_sizes(labels: Any) -> list[float]:
    """Font sizes for visible, non-empty tick/text labels."""

    out: list[float] = []
    for label in labels:
        if not getattr(label, "get_visible", lambda: True)():
            continue
        text = getattr(label, "get_text", lambda: "")()
        if not str(text).strip():
            continue
        size = _font_size(label)
        if size is not None:
            out.append(size)
    return out


def _git_revision(project_root: Path | None = None) -> str:
    """Return the current `git rev-parse HEAD` short hash, or
    ``"unknown"`` if the project is not a git repo or git is missing.
    """
    cwd = str(project_root) if project_root else None
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2.0,
            cwd=cwd,
            check=False,
        )
        rev = result.stdout.strip()
        return rev or "unknown"
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def summarize_array(values: Any) -> dict[str, Any]:
    """Return JSON-safe descriptive stats for a numeric array-like value."""
    arr = np.asarray(values)
    shape = tuple(int(s) for s in arr.shape)
    if arr.size == 0:
        return {
            "shape": list(shape),
            "count": 0,
            "finite_count": 0,
            "nan_count": 0,
            "inf_count": 0,
        }
    flat = arr.astype(float, copy=False).reshape(-1)
    finite = flat[np.isfinite(flat)]
    summary: dict[str, Any] = {
        "shape": list(shape),
        "count": int(flat.size),
        "finite_count": int(finite.size),
        "nan_count": int(np.isnan(flat).sum()),
        "inf_count": int(np.isinf(flat).sum()),
    }
    if finite.size:
        summary.update(
            {
                "min": float(np.min(finite)),
                "max": float(np.max(finite)),
                "mean": float(np.mean(finite)),
                "std": float(np.std(finite)),
                "median": float(np.median(finite)),
                "q05": float(np.quantile(finite, 0.05)),
                "q95": float(np.quantile(finite, 0.95)),
            }
        )
    return summary


def figure_statistics(fig: Any) -> dict[str, Any]:
    """Extract compact layout and data statistics from a Matplotlib figure.

    The payload is intentionally summary-only.  It captures axes counts,
    limits, line-series summaries, and image-array summaries without
    embedding the full plotted data in PNG metadata.
    """
    axes_payload: list[dict[str, Any]] = []
    series_seen = 0
    for ax_idx, ax in enumerate(getattr(fig, "axes", [])):
        ax_payload: dict[str, Any] = {
            "index": int(ax_idx),
            "title": ax.get_title(),
            "xlabel": ax.get_xlabel(),
            "ylabel": ax.get_ylabel(),
            "xlim": [float(v) for v in ax.get_xlim()],
            "ylim": [float(v) for v in ax.get_ylim()],
            "line_count": len(ax.lines),
            "image_count": len(ax.images),
            "collection_count": len(ax.collections),
            "text_count": len(ax.texts),
            "legend_labels": [text.get_text() for text in (ax.get_legend().get_texts() if ax.get_legend() else [])],
            "lines": [],
            "images": [],
            "collections": [],
            "texts": [text.get_text() for text in ax.texts],
            "font_sizes": {
                "title": _font_size(ax.title),
                "xlabel": _font_size(ax.xaxis.label),
                "ylabel": _font_size(ax.yaxis.label),
                "xticklabels": _visible_label_font_sizes(ax.get_xticklabels()),
                "yticklabels": _visible_label_font_sizes(ax.get_yticklabels()),
                "legend": _visible_label_font_sizes(ax.get_legend().get_texts() if ax.get_legend() else []),
                "texts": [
                    {"text": text.get_text(), "fontsize": _font_size(text)}
                    for text in ax.texts
                    if text.get_text().strip()
                ],
            },
        }
        for line_idx, line in enumerate(ax.lines):
            if series_seen >= _MAX_AUTOSTAT_SERIES:
                break
            ax_payload["lines"].append(
                {
                    "index": int(line_idx),
                    "label": line.get_label(),
                    "x": summarize_array(line.get_xdata()),
                    "y": summarize_array(line.get_ydata()),
                }
            )
            series_seen += 1
        for image_idx, image in enumerate(ax.images):
            if series_seen >= _MAX_AUTOSTAT_SERIES:
                break
            ax_payload["images"].append(
                {
                    "index": int(image_idx),
                    "array": summarize_array(image.get_array()),
                }
            )
            series_seen += 1
        for collection_idx, collection in enumerate(ax.collections):
            if series_seen >= _MAX_AUTOSTAT_SERIES:
                break
            collection_payload: dict[str, Any] = {
                "index": int(collection_idx),
                "type": type(collection).__name__,
            }
            get_offsets = getattr(collection, "get_offsets", None)
            if callable(get_offsets):
                offsets = get_offsets()
                if np.asarray(offsets).size:
                    collection_payload["offsets"] = summarize_array(offsets)
            get_array = getattr(collection, "get_array", None)
            if callable(get_array):
                arr = get_array()
                if arr is not None and np.asarray(arr).size:
                    collection_payload["array"] = summarize_array(arr)
            get_sizes = getattr(collection, "get_sizes", None)
            if callable(get_sizes):
                sizes = get_sizes()
                if np.asarray(sizes).size:
                    collection_payload["sizes"] = summarize_array(sizes)
            ax_payload["collections"].append(collection_payload)
            series_seen += 1
        axes_payload.append(ax_payload)

    width, height = fig.get_size_inches()
    figure_texts = [
        {"text": text.get_text(), "fontsize": _font_size(text)}
        for text in getattr(fig, "texts", [])
        if text.get_text().strip()
    ]
    return {
        "schema_version": FIGURE_METADATA_SCHEMA_VERSION,
        "figure_size_inches": [float(width), float(height)],
        "dpi": float(fig.dpi),
        "axes_count": len(getattr(fig, "axes", [])),
        "figure_texts": figure_texts,
        "captured_series_count": int(series_seen),
        "series_capture_limit": _MAX_AUTOSTAT_SERIES,
        "axes": axes_payload,
    }


def figure_metadata(
    *,
    source_script: str,
    source_function: str,
    hyperparameters: Mapping[str, Any] | None = None,
    statistics: Mapping[str, Any] | None = None,
    uncertainty_semantics: str | None = None,
    extra: Mapping[str, Any] | None = None,
    project_root: Path | None = None,
) -> dict[str, str]:
    """Build the reproducibility-metadata dict for `savefig(metadata=...)`.

    PNG tEXt values must be strings, so non-string payloads are
    JSON-encoded.  Returns a *new* dict on every call.
    """
    extra_payload = dict(extra or {})
    inferred_uncertainty = uncertainty_semantics or str(extra_payload.pop("uncertainty_semantics", "") or "")
    if not inferred_uncertainty:
        inferred_uncertainty = _infer_uncertainty_semantics(
            source_script=source_script,
            source_function=source_function,
        )
    md: dict[str, str] = {
        "Software": "matplotlib (project: actinf_policy_entanglement_lean)",
        "project.source_script": str(source_script),
        "project.source_function": str(source_function),
        "project.git_revision": _git_revision(project_root),
        "project.timestamp_format": _ISO_FMT,
        "project.timestamp": _now_iso(),
        "project.uncertainty_semantics": inferred_uncertainty,
    }
    if hyperparameters:
        md["project.hyperparameters"] = json.dumps(
            dict(hyperparameters),
            separators=(",", ":"),
            default=str,
        )
    if statistics:
        md["project.statistics"] = json.dumps(
            dict(statistics),
            separators=(",", ":"),
            default=str,
        )
    if extra_payload:
        for k, v in extra_payload.items():
            md[f"project.{k}"] = json.dumps(v, separators=(",", ":"), default=str) if not isinstance(v, str) else v
    return md


def _infer_uncertainty_semantics(*, source_script: str, source_function: str) -> str:
    """Infer a conservative uncertainty class for generated figures.

    Figure producers may override this with ``uncertainty_semantics``.
    The fallback keeps older callers schema-complete without implying
    stochastic uncertainty where none was computed.
    """
    marker = f"{source_script}::{source_function}".lower()
    if "threshold_sensitivity" in marker:
        return "confidence_interval"
    if "replicate" in marker or "seed_diagnostics" in marker:
        return "replicate_envelope"
    if "rollout" in marker or "simulate_long_horizon.py" in marker:
        return "canonical_seed"
    if "coupling_graph" in marker:
        return "analytical_schematic"
    return "deterministic_grid"


def read_figure_metadata(png_path: Path) -> dict[str, str]:
    """Read the tEXt-chunk metadata back from a PNG.

    Lazy-imports PIL so the helper is dependency-free for callers
    that do not need it.
    """
    from PIL import Image  # noqa: WPS433

    img = Image.open(png_path)
    # Image.info contains tEXt chunks as plain strings.
    return {str(k): str(v) for k, v in img.info.items()}


def has_project_metadata(png_path: Path) -> bool:
    """True iff the PNG carries our `project.*` reproducibility tEXt."""
    try:
        info = read_figure_metadata(png_path)
    except (OSError, ImportError):
        return False
    return any(k.startswith("project.") for k in info)
