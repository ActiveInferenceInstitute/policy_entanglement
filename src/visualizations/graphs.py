"""Graph-style figures: the coupling-potential interaction graph."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from ._io import _save_with_metadata as _save
from .annotations import add_stats_box
from .setup import PUBLICATION_STYLE, palette_color

ArrayF = NDArray[np.float64]

try:
    import networkx as nx

    _HAS_NETWORKX = True
except ImportError:  # pragma: no cover - viz group missing
    _HAS_NETWORKX = False
    nx = None

try:
    import seaborn  # noqa: F401

    _HAS_SEABORN = True
except ImportError:  # pragma: no cover
    _HAS_SEABORN = False


def has_networkx() -> bool:
    """Return whether the optional `networkx` dependency is available."""
    return _HAS_NETWORKX


def has_seaborn() -> bool:
    """Return whether the optional `seaborn` dependency is available."""
    return _HAS_SEABORN


def plot_coupling_graph(
    *,
    coupling_j: ArrayF,
    out_path: Path | str,
    threshold: float = 0.0,
    metadata=None,
) -> Path | None:
    """Render the pairwise coupling graph induced by `|J|`.

    Returns `None` (without raising) when `networkx` is unavailable, so
    figure scripts can run in environments lacking the optional `viz`
    group. Otherwise returns the saved figure path.
    """
    if not _HAS_NETWORKX:  # pragma: no cover - covered by `viz` group install
        return None
    import matplotlib.pyplot as plt

    n_dims = coupling_j.ndim
    if n_dims < 2:
        raise ValueError("plot_coupling_graph requires K ≥ 2")
    graph = nx.Graph()
    for k in range(n_dims):
        graph.add_node(k, label=f"stream {k}")
    abs_j = np.abs(coupling_j)
    for i in range(n_dims):
        for j in range(i + 1, n_dims):
            other = tuple(a for a in range(n_dims) if a not in (i, j))
            w = float(np.sum(abs_j, axis=other).mean()) if other else float(abs_j.mean())
            if w >= threshold:
                graph.add_edge(i, j, weight=w)
    if graph.number_of_edges() == 0:
        # Add at least one weak edge so the figure is non-empty.
        graph.add_edge(0, 1, weight=float(abs_j.mean()))
    pos = nx.circular_layout(graph)
    weights = [graph[u][v]["weight"] for u, v in graph.edges()]
    fig, ax = plt.subplots(figsize=PUBLICATION_STYLE.single, constrained_layout=True)
    nx.draw_networkx_nodes(graph, pos, node_color=palette_color(5), node_size=900, ax=ax)
    nx.draw_networkx_labels(
        graph,
        pos,
        ax=ax,
        font_color="white",
        font_size=PUBLICATION_STYLE.tick_size,
        font_weight="bold",
    )
    max_w = max(weights) if weights else 1.0
    nx.draw_networkx_edges(
        graph,
        pos,
        ax=ax,
        width=[1.0 + 4.0 * w / max_w for w in weights],
        edge_color="#666666",
    )
    edge_labels = {(u, v): f"{graph[u][v]['weight']:.2f}" for u, v in graph.edges()}
    nx.draw_networkx_edge_labels(
        graph,
        pos,
        edge_labels=edge_labels,
        ax=ax,
        font_size=PUBLICATION_STYLE.annotation_size,
    )
    ax.set_title("Coupling-potential graph |J| (averaged across slots)")
    ax.set_axis_off()
    add_stats_box(
        ax,
        [
            f"streams={n_dims}, edges={graph.number_of_edges()}",
            f"threshold={threshold:.2f}",
            f"max edge weight={max_w:.3f}",
        ],
        loc="lower center",
    )
    out = Path(out_path)
    return _save(fig, out, metadata=metadata)
