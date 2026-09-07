"""Small Plotly trace/layout builders for dashboard panels."""

from __future__ import annotations

from typing import Any


def scatter_line(
    *,
    name: str,
    x: list[float],
    y: list[float],
    color: str,
    dash: str | None = None,
    yaxis: str | None = None,
    width: int | None = None,
) -> dict[str, Any]:
    line: dict[str, Any] = {"color": color}
    if dash:
        line["dash"] = dash
    if width is not None:
        line["width"] = width
    trace: dict[str, Any] = {
        "type": "scatter",
        "mode": "lines",
        "name": name,
        "x": x,
        "y": y,
        "line": line,
    }
    if yaxis:
        trace["yaxis"] = yaxis
    return trace


def scatter_markers(
    *,
    name: str,
    x: list[float],
    y: list[float],
    color: str | list[str],
    size: int = 6,
) -> dict[str, Any]:
    marker: dict[str, Any] = {"size": size}
    if isinstance(color, list):
        marker["color"] = color
    else:
        marker["color"] = color
    return {
        "type": "scatter",
        "mode": "markers" if "markers" not in name else "lines+markers",
        "name": name,
        "x": x,
        "y": y,
        "marker": marker,
    }


def heatmap(
    *,
    z: list[list[float]],
    x_labels: list[str],
    y_labels: list[str],
    colorscale: str = "Cividis",
) -> dict[str, Any]:
    return {
        "type": "heatmap",
        "z": z,
        "x": x_labels,
        "y": y_labels,
        "colorscale": colorscale,
        "showscale": True,
        "zmin": 0.0,
        "zmax": 1.0,
    }


def axis_layout(*, x_title: str, y_title: str, legend_y: float = -0.2) -> dict[str, Any]:
    return {
        "xaxis": {"title": x_title},
        "yaxis": {"title": y_title},
        "legend": {"orientation": "h", "y": legend_y},
    }
