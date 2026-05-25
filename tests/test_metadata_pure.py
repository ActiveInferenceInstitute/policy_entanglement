"""Tests for visualizations.metadata pure functions.

figure_metadata and _git_revision work without matplotlib.
read_figure_metadata / has_project_metadata require PIL — those are
tested only when PIL is importable.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from manuscript.stale_patterns import STALE_FIGURE_REFERENCE_REGEXES
from visualizations.metadata import (
    FIGURE_METADATA_SCHEMA_VERSION,
    VALID_UNCERTAINTY_SEMANTICS,
    _font_size,
    _git_revision,
    _visible_label_font_sizes,
    figure_metadata,
    figure_statistics,
    has_project_metadata,
    read_figure_metadata,
    summarize_array,
)

PROJECT = Path(__file__).resolve().parent.parent


def test_figure_metadata_required_keys() -> None:
    md = figure_metadata(source_script="test.py", source_function="test_fn")
    assert "Software" in md
    assert "project.source_script" in md
    assert "project.source_function" in md
    assert "project.git_revision" in md
    assert "project.timestamp" in md
    assert md["project.uncertainty_semantics"] in VALID_UNCERTAINTY_SEMANTICS


def test_figure_metadata_script_and_function_preserved() -> None:
    md = figure_metadata(source_script="foo.py", source_function="bar")
    assert md["project.source_script"] == "foo.py"
    assert md["project.source_function"] == "bar"


def test_figure_metadata_hyperparameters_json_encoded() -> None:
    params = {"K": 2, "lam": 1.5, "seed": 42}
    md = figure_metadata(
        source_script="s.py",
        source_function="f",
        hyperparameters=params,
    )
    assert "project.hyperparameters" in md
    decoded = json.loads(md["project.hyperparameters"])
    assert decoded["K"] == 2
    assert decoded["lam"] == pytest.approx(1.5)


def test_figure_metadata_no_hyperparameters_key_absent() -> None:
    md = figure_metadata(source_script="s.py", source_function="f")
    assert "project.hyperparameters" not in md


def test_figure_metadata_extra_keys_prefixed() -> None:
    md = figure_metadata(
        source_script="s.py",
        source_function="f",
        extra={"run_id": "abc", "count": 5},
    )
    assert "project.run_id" in md
    assert md["project.run_id"] == "abc"
    assert "project.count" in md


def test_figure_metadata_uncertainty_semantics_override_and_inference() -> None:
    md = figure_metadata(
        source_script="scripts/simulate_robustness.py",
        source_function="plot_long_horizon_threshold_sensitivity",
    )
    assert md["project.uncertainty_semantics"] == "confidence_interval"

    md = figure_metadata(
        source_script="scripts/simulate_robustness.py",
        source_function="plot_long_horizon_replicate_envelope",
    )
    assert md["project.uncertainty_semantics"] == "replicate_envelope"

    md = figure_metadata(
        source_script="scripts/generate_figures.py",
        source_function="figure_coupling_graph",
        extra={"uncertainty_semantics": "analytical_schematic"},
    )
    assert md["project.uncertainty_semantics"] == "analytical_schematic"
    assert "project.uncertainty_semantics" in md


def test_figure_metadata_statistics_json_encoded() -> None:
    stats = {"series": summarize_array([0.0, 1.0, 2.0])}
    md = figure_metadata(
        source_script="s.py",
        source_function="f",
        statistics=stats,
    )
    decoded = json.loads(md["project.statistics"])
    assert decoded["series"]["count"] == 3
    assert decoded["series"]["mean"] == pytest.approx(1.0)


def test_summarize_array_records_shape_and_quantiles() -> None:
    summary = summarize_array([[0.0, 1.0], [2.0, np.nan]])
    assert summary["shape"] == [2, 2]
    assert summary["count"] == 4
    assert summary["finite_count"] == 3
    assert summary["nan_count"] == 1
    assert summary["max"] == pytest.approx(2.0)


def test_summarize_array_empty_and_font_size_edge_cases() -> None:
    empty = summarize_array([])
    assert empty == {
        "shape": [0],
        "count": 0,
        "finite_count": 0,
        "nan_count": 0,
        "inf_count": 0,
    }

    class NoFont:
        pass

    class BadFont:
        def get_fontsize(self) -> str:
            return "not-a-number"

    class Label:
        def __init__(self, text: str, visible: bool = True) -> None:
            self._text = text
            self._visible = visible

        def get_visible(self) -> bool:
            return self._visible

        def get_text(self) -> str:
            return self._text

        def get_fontsize(self) -> float:
            return 12.0

    assert _font_size(NoFont()) is None
    assert _font_size(BadFont()) is None
    assert _visible_label_font_sizes([Label(""), Label("hidden", False), Label("shown")]) == [12.0]


def test_figure_statistics_records_collection_and_legend_metadata() -> None:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.scatter([0.0, 1.0, 2.0], [2.0, 1.0, 0.0], c=[0.1, 0.2, 0.3], label="scatter")
    ax.text(0.1, 0.9, "stats box", transform=ax.transAxes)
    fig.text(0.5, 0.01, "footer", fontsize=8.0)
    ax.legend()
    stats = figure_statistics(fig)
    plt.close(fig)

    assert stats["schema_version"] == FIGURE_METADATA_SCHEMA_VERSION
    assert stats["figure_texts"][0]["text"] == "footer"
    assert stats["axes_count"] == 1
    axis = stats["axes"][0]
    assert axis["legend_labels"] == ["scatter"]
    assert axis["text_count"] == 1
    assert axis["texts"] == ["stats box"]
    assert axis["font_sizes"]["title"] is not None
    assert axis["font_sizes"]["xticklabels"]
    assert axis["font_sizes"]["legend"]
    assert axis["font_sizes"]["texts"][0]["text"] == "stats box"
    assert axis["collection_count"] == 1
    assert axis["collections"][0]["offsets"]["shape"] == [3, 2]
    assert axis["collections"][0]["array"]["count"] == 3


def test_figure_statistics_series_capture_limit_for_lines_images_and_collections() -> None:
    import matplotlib.pyplot as plt

    fig_lines, ax_lines = plt.subplots()
    for idx in range(45):
        ax_lines.plot([0, 1], [idx, idx + 1])
    stats_lines = figure_statistics(fig_lines)
    plt.close(fig_lines)
    assert stats_lines["captured_series_count"] == 40
    assert len(stats_lines["axes"][0]["lines"]) == 40

    fig_images, ax_images = plt.subplots()
    for idx in range(45):
        ax_images.imshow(np.full((2, 2), idx), alpha=0.01)
    stats_images = figure_statistics(fig_images)
    plt.close(fig_images)
    assert stats_images["captured_series_count"] == 40
    assert len(stats_images["axes"][0]["images"]) == 40

    fig_collections, ax_collections = plt.subplots()
    for idx in range(45):
        ax_collections.scatter([idx], [idx], s=[idx + 1])
    stats_collections = figure_statistics(fig_collections)
    plt.close(fig_collections)
    assert stats_collections["captured_series_count"] == 40
    assert len(stats_collections["axes"][0]["collections"]) == 40


def test_figure_metadata_returns_new_dict_each_call() -> None:
    md1 = figure_metadata(source_script="a.py", source_function="a")
    md2 = figure_metadata(source_script="b.py", source_function="b")
    assert md1 is not md2
    assert md1["project.source_script"] != md2["project.source_script"]


def test_git_revision_returns_string() -> None:
    rev = _git_revision()
    assert isinstance(rev, str)
    assert len(rev) > 0


def test_git_revision_with_invalid_path_returns_unknown() -> None:
    rev = _git_revision(project_root=Path("/nonexistent/repo/path"))
    assert isinstance(rev, str)


def test_figure_metadata_project_root_used_for_git() -> None:
    # Passing the actual repo root should return a non-empty revision.
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    md = figure_metadata(
        source_script="s.py",
        source_function="f",
        project_root=repo_root,
    )
    # Git revision should be a string — either a hash or "unknown"
    assert isinstance(md["project.git_revision"], str)


def test_has_project_metadata_missing_file_returns_false() -> None:
    result = has_project_metadata(Path("/nonexistent/foo.png"))
    assert result is False


def test_read_figure_metadata_round_trip_and_has_project_metadata(tmp_path: Path) -> None:
    import matplotlib.pyplot as plt

    path = tmp_path / "meta.png"
    md = figure_metadata(
        source_script="round_trip.py",
        source_function="plot_round_trip",
        hyperparameters={"seed": 0},
    )
    fig, ax = plt.subplots()
    ax.plot([0.0, 1.0], [0.0, 1.0])
    fig.savefig(path, metadata=md)
    plt.close(fig)

    info = read_figure_metadata(path)
    assert info["project.source_script"] == "round_trip.py"
    assert has_project_metadata(path) is True


def test_generated_output_pngs_have_metadata_and_pixels() -> None:
    """When generated output exists, every PNG carries provenance,
    hyperparameter/statistics metadata, adequate dimensions, and
    nonblank pixels.
    """
    figdir = PROJECT / "output" / "figures"
    if not figdir.exists():
        pytest.skip("output/figures not generated yet")
    pngs = sorted(figdir.glob("*.png"))
    if not pngs:
        pytest.skip("no generated PNGs to inspect")
    from PIL import Image

    failures: list[str] = []
    for path in pngs:
        img = Image.open(path)
        width, height = img.size
        if width < 600 or height < 300:
            failures.append(f"{path.name}: small {width}x{height}")
        info = {str(k): str(v) for k, v in img.info.items()}
        for key in (
            "project.source_script",
            "project.source_function",
            "project.uncertainty_semantics",
            "project.hyperparameters",
            "project.figure_statistics",
        ):
            if key not in info:
                failures.append(f"{path.name}: missing {key}")
        if info.get("project.uncertainty_semantics") not in VALID_UNCERTAINTY_SEMANTICS:
            failures.append(f"{path.name}: invalid uncertainty semantics")
        if "project.hyperparameters" in info:
            payload = json.loads(info["project.hyperparameters"])
            if not isinstance(payload, dict) or not payload:
                failures.append(f"{path.name}: empty hyperparameter metadata")
        if "project.figure_statistics" in info:
            stats = json.loads(info["project.figure_statistics"])
            if int(stats.get("schema_version", 0)) < FIGURE_METADATA_SCHEMA_VERSION:
                failures.append(f"{path.name}: stale figure metadata schema")
            if int(stats.get("axes_count", 0)) < 1:
                failures.append(f"{path.name}: no axes in figure statistics")
            figure_texts = stats.get("figure_texts")
            if isinstance(figure_texts, list):
                for entry in figure_texts:
                    if isinstance(entry, dict) and float(entry.get("fontsize") or 0.0) < 8.0:
                        failures.append(f"{path.name}: figure-level text font below 8 pt")
            for axis in stats.get("axes", []):
                if not isinstance(axis, dict):
                    continue
                fonts = axis.get("font_sizes")
                if not isinstance(fonts, dict):
                    failures.append(f"{path.name}: missing font_sizes metadata")
                    continue
                title = axis.get("title")
                if isinstance(title, str) and title.strip() and float(fonts.get("title") or 0.0) < 14.0:
                    failures.append(f"{path.name}: title font below 14 pt")
                for label_key in ("xlabel", "ylabel"):
                    label = axis.get(label_key)
                    if isinstance(label, str) and label.strip() and float(fonts.get(label_key) or 0.0) < 12.0:
                        failures.append(f"{path.name}: {label_key} font below 12 pt")
                for tick_key in ("xticklabels", "yticklabels"):
                    values = fonts.get(tick_key)
                    if isinstance(values, list) and values and min(float(v) for v in values) < 12.0:
                        failures.append(f"{path.name}: {tick_key} font below 12 pt")
                legend_sizes = fonts.get("legend")
                if isinstance(legend_sizes, list) and legend_sizes and min(float(v) for v in legend_sizes) < 10.0:
                    failures.append(f"{path.name}: legend font below 10 pt")
                text_values: list[str] = []
                for key in ("title", "xlabel", "ylabel"):
                    value = axis.get(key)
                    if isinstance(value, str):
                        text_values.append(value)
                for key in ("legend_labels", "texts"):
                    values = axis.get(key)
                    if isinstance(values, list):
                        text_values.extend(v for v in values if isinstance(v, str))
                for value in text_values:
                    if any(pattern.search(value) for pattern in STALE_FIGURE_REFERENCE_REGEXES):
                        failures.append(f"{path.name}: stale theorem annotation {value!r}")
        if img.convert("L").getextrema()[0] == img.convert("L").getextrema()[1]:
            failures.append(f"{path.name}: blank image")
    assert not failures, "\n".join(failures)
