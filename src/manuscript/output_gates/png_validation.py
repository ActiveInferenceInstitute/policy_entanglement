"""PNG artifact validation helpers."""

from __future__ import annotations

import json
import math
from pathlib import Path

from manuscript.output_gates._reporting import fail as report_fail
from manuscript.output_gates._reporting import ok as report_ok
from manuscript.output_gates.constants import (
    MIN_ANNOTATION_FONT_SIZE,
    MIN_AXIS_FONT_SIZE,
    MIN_FIGURE_HEIGHT,
    MIN_FIGURE_METADATA_SCHEMA_VERSION,
    MIN_FIGURE_WIDTH,
    MIN_LEGEND_FONT_SIZE,
    MIN_TICK_FONT_SIZE,
    MIN_TITLE_FONT_SIZE,
    PNG_HEADER,
    PROJECT_ROOT,
    VALID_UNCERTAINTY_SEMANTICS,
)
from manuscript.stale_patterns import STALE_FIGURE_REFERENCE_PATTERNS


def _finite(value: str | float) -> float:
    x = float(value)
    if not math.isfinite(x):
        raise ValueError(f"{value!r} is not finite")
    return x


def _decode_json_metadata(info: dict[str, str], path: Path, key: str) -> tuple[object | None, int]:
    """Decode a JSON-valued PNG metadata field."""
    if key not in info:
        report_fail(f"{path.name}: missing PNG metadata key {key}")
        return None, 1
    try:
        return json.loads(info[key]), 0
    except json.JSONDecodeError as exc:
        report_fail(f"{path.name}: metadata {key} is not valid JSON ({exc})")
        return None, 1


def check_png_semantic_metadata(path: Path, info: dict[str, str]) -> int:
    """Validate project PNG metadata beyond mere key presence."""
    failures = 0
    uncertainty = info.get("project.uncertainty_semantics", "")
    if uncertainty not in VALID_UNCERTAINTY_SEMANTICS:
        report_fail(
            f"{path.name}: project.uncertainty_semantics {uncertainty!r} not in {sorted(VALID_UNCERTAINTY_SEMANTICS)}"
        )
        failures += 1
    stats_obj, bad = _decode_json_metadata(info, path, "project.figure_statistics")
    failures += bad
    hyper_obj, bad = _decode_json_metadata(info, path, "project.hyperparameters")
    failures += bad
    if not isinstance(stats_obj, dict):
        report_fail(f"{path.name}: project.figure_statistics must decode to an object")
        failures += 1
    else:
        schema = int(stats_obj.get("schema_version", 0))
        if schema < MIN_FIGURE_METADATA_SCHEMA_VERSION:
            report_fail(
                f"{path.name}: figure_statistics schema_version {schema} < {MIN_FIGURE_METADATA_SCHEMA_VERSION}"
            )
            failures += 1
        axes = stats_obj.get("axes")
        if int(stats_obj.get("axes_count", 0)) < 1 or not isinstance(axes, list):
            report_fail(f"{path.name}: figure_statistics has no axes payload")
            failures += 1
        if not isinstance(stats_obj.get("figure_size_inches"), list):
            report_fail(f"{path.name}: figure_statistics missing figure_size_inches")
            failures += 1
        figure_texts = stats_obj.get("figure_texts")
        if isinstance(figure_texts, list):
            for entry in figure_texts:
                if not isinstance(entry, dict):
                    continue
                size = float(entry.get("fontsize") or 0.0)
                if size < MIN_ANNOTATION_FONT_SIZE:
                    report_fail(f"{path.name}: figure-level text font {size:g} pt < {MIN_ANNOTATION_FONT_SIZE:g} pt")
                    failures += 1
    if not isinstance(hyper_obj, dict):
        report_fail(f"{path.name}: project.hyperparameters must decode to an object")
        failures += 1
        hyper_obj = {}

    # Family-specific contracts: figures that summarize simulation
    # results must expose the hyperparameter knobs and a stats-box text
    # annotation in the captured figure metadata.
    stats = stats_obj if isinstance(stats_obj, dict) else {}
    axes_value = stats.get("axes")
    axes_payload: list[object] = axes_value if isinstance(axes_value, list) else []
    text_count = 0
    for ax in axes_payload:
        if isinstance(ax, dict):
            text_count += int(ax.get("text_count", 0))
            fonts = ax.get("font_sizes")
            if not isinstance(fonts, dict):
                report_fail(f"{path.name}: axis {ax.get('index', '?')} missing font_sizes metadata")
                failures += 1
                fonts = {}
            title = ax.get("title")
            if isinstance(title, str) and title.strip():
                size = float(fonts.get("title") or 0.0)
                if size < MIN_TITLE_FONT_SIZE:
                    report_fail(f"{path.name}: title font {size:g} pt < {MIN_TITLE_FONT_SIZE:g} pt")
                    failures += 1
            for label_key, size_key in (("xlabel", "xlabel"), ("ylabel", "ylabel")):
                label = ax.get(label_key)
                if isinstance(label, str) and label.strip():
                    size = float(fonts.get(size_key) or 0.0)
                    if size < MIN_AXIS_FONT_SIZE:
                        report_fail(f"{path.name}: {label_key} font {size:g} pt < {MIN_AXIS_FONT_SIZE:g} pt")
                        failures += 1
            for tick_key in ("xticklabels", "yticklabels"):
                tick_sizes = fonts.get(tick_key)
                if isinstance(tick_sizes, list) and tick_sizes:
                    smallest = min(float(v) for v in tick_sizes)
                    if smallest < MIN_TICK_FONT_SIZE:
                        report_fail(f"{path.name}: {tick_key} min font {smallest:g} pt < {MIN_TICK_FONT_SIZE:g} pt")
                        failures += 1
            legend_sizes = fonts.get("legend")
            if isinstance(legend_sizes, list) and legend_sizes:
                smallest = min(float(v) for v in legend_sizes)
                if smallest < MIN_LEGEND_FONT_SIZE:
                    report_fail(f"{path.name}: legend min font {smallest:g} pt < {MIN_LEGEND_FONT_SIZE:g} pt")
                    failures += 1
            text_sizes = fonts.get("texts")
            if isinstance(text_sizes, list):
                for entry in text_sizes:
                    if not isinstance(entry, dict):
                        continue
                    size = float(entry.get("fontsize") or 0.0)
                    if size < MIN_ANNOTATION_FONT_SIZE:
                        report_fail(f"{path.name}: annotation font {size:g} pt < {MIN_ANNOTATION_FONT_SIZE:g} pt")
                        failures += 1
            for key in ("title", "xlabel", "ylabel"):
                value = ax.get(key)
                if isinstance(value, str):
                    for pattern, replacement in STALE_FIGURE_REFERENCE_PATTERNS:
                        if pattern.search(value):
                            report_fail(f"{path.name}: stale figure reference {value!r}; use {replacement}")
                            failures += 1
            for key in ("legend_labels", "texts"):
                values = ax.get(key)
                if not isinstance(values, list):
                    continue
                for value in values:
                    if not isinstance(value, str):
                        continue
                    for pattern, replacement in STALE_FIGURE_REFERENCE_PATTERNS:
                        if pattern.search(value):
                            report_fail(f"{path.name}: stale figure reference {value!r}; use {replacement}")
                            failures += 1
    name = path.name
    required_hyper_by_prefix = {
        "pymdp_": {"K", "sweep_grid_points", "observations"},
        "long_horizon_": {"horizon", "tail_window", "steady_state_tol", "seed"},
        "multi_k_": {"K_values", "sweep_grid_points", "sweep_lambda_max"},
        "revertibility_": {"lambdas", "tolerance"},
        "robustness_": {"K", "robustness_observation_contexts", "robustness_gammas", "sweep_grid_points"},
        "interaction_": {"K", "robustness_interaction_families", "sweep_grid_points"},
        "coupling_ablation_": {"K", "variants", "sweep_grid_points"},
        "marginal_null_control_": {"K", "sweep_grid_points"},
    }
    for prefix, required_keys in required_hyper_by_prefix.items():
        if name.startswith(prefix):
            missing = required_keys - set(hyper_obj)
            if missing:
                report_fail(f"{path.name}: missing hyperparameter metadata keys {sorted(missing)}")
                failures += 1
            break
    stats_box_required = (
        name.startswith("multi_k_")
        or name.startswith("long_horizon_")
        or name.startswith("revertibility_")
        or name.startswith("robustness_")
        or name.startswith("interaction_")
        or name.startswith("coupling_ablation_")
        or name.startswith("marginal_null_control_")
        or name
        in {
            "pymdp_total_correlation_curve.png",
            "pymdp_free_energy_panel.png",
            "pymdp_summary_panel.png",
            "pymdp_vfe_decomposition.png",
            "pymdp_entropy_decomposition.png",
        }
    )
    if stats_box_required and text_count < 1:
        report_fail(f"{path.name}: expected at least one captured stats annotation")
        failures += 1
    return failures


def check_png(path: Path, *, optional: bool = False) -> int:
    if not path.exists():
        if optional:
            report_ok(f"(optional, not present): {path.name}")
            return 0
        report_fail(f"missing: {path}")
        return 1
    size = path.stat().st_size
    if size <= 0:
        report_fail(f"empty: {path}")
        return 1
    with path.open("rb") as fh:
        header = fh.read(8)
    if header != PNG_HEADER:
        report_fail(f"not a PNG: {path}")
        return 1
    try:
        from PIL import Image

        img = Image.open(path)
        width, height = img.size
        if width < MIN_FIGURE_WIDTH or height < MIN_FIGURE_HEIGHT:
            report_fail(f"{path.name}: dimensions {width}x{height} below {MIN_FIGURE_WIDTH}x{MIN_FIGURE_HEIGHT}")
            return 1
        info = {str(k): str(v) for k, v in img.info.items()}
        for key in (
            "project.source_script",
            "project.source_function",
            "project.uncertainty_semantics",
            "project.figure_statistics",
        ):
            if key not in info:
                report_fail(f"{path.name}: missing PNG metadata key {key}")
                return 1
        metadata_fail = check_png_semantic_metadata(path, info)
        if metadata_fail:
            return metadata_fail
        # Nonblank pixel-variance smoke test.
        extrema = img.convert("L").getextrema()
        if extrema[0] == extrema[1]:
            report_fail(f"{path.name}: blank image (flat pixel extrema {extrema})")
            return 1
    except ImportError:
        report_fail("PIL is required for PNG metadata / pixel validation")
        return 1
    except OSError as exc:
        report_fail(f"{path.name}: PIL could not read image: {exc}")
        return 1
    report_ok(f"{path.relative_to(PROJECT_ROOT)} ({size} bytes)")
    return 0
