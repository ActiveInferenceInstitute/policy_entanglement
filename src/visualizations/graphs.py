"""Graph-style figures: the coupling-potential interaction graph."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from numpy.typing import NDArray

ArrayF = NDArray[np.float64]

try:
    import networkx as nx  # type: ignore
    _HAS_NETWORKX = True
except ImportError:  # pragma: no cover - viz group missing
    _HAS_NETWORKX = False
    nx = None  # type: ignore

try:
    import seaborn  # type: ignore  # noqa: F401
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
    coupling_J: ArrayF,
    out_path: Path | str,
    threshold: float = 0.0,
) -> Path | None:
    """Render the pairwise coupling graph induced by `|J|`.

    Returns `None` (without raising) when `networkx` is unavailable, so
    figure scripts can run in environments lacking the optional `viz`
    group. Otherwise returns the saved figure path.
    """
    if not _HAS_NETWORKX:  # pragma: no cover - covered by `viz` group install
        return None
    import matplotlib.pyplot as plt

    K = coupling_J.ndim
    if K < 2:
        raise ValueError("plot_coupling_graph requires K ≥ 2")
    G = nx.Graph()
    for k in range(K):
        G.add_node(k, label=f"stream {k}")
    abs_J = np.abs(coupling_J)
    for i in range(K):
        for j in range(i + 1, K):
            other = tuple(a for a in range(K) if a not in (i, j))
            if other:
                w = float(np.sum(abs_J, axis=other).mean())
            else:
                w = float(abs_J.mean())
            if w >= threshold:
                G.add_edge(i, j, weight=w)
    if G.number_of_edges() == 0:
        # Add at least one weak edge so the figure is non-empty.
        G.add_edge(0, 1, weight=float(abs_J.mean()))
    pos = nx.circular_layout(G)
    weights = [G[u][v]["weight"] for u, v in G.edges()]
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    nx.draw_networkx_nodes(G, pos, node_color="steelblue", node_size=700, ax=ax)
    nx.draw_networkx_labels(G, pos, ax=ax, font_color="white", font_size=10)
    max_w = max(weights) if weights else 1.0
    nx.draw_networkx_edges(
        G, pos, ax=ax,
        width=[1.0 + 4.0 * w / max_w for w in weights],
        edge_color="gray",
    )
    edge_labels = {(u, v): f"{G[u][v]['weight']:.2f}" for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax, font_size=8)
    ax.set_title("Coupling-potential graph |J| (averaged across slots)")
    ax.set_axis_off()
    out = Path(out_path)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out
