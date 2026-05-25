"""Visualization helpers for multilayer networks."""

from __future__ import annotations

import csv
import os
import warnings
from typing import Any, Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import networkx as nx


MAX_DRAW_NODES = 5000


def _drawable_graph(G: nx.Graph, threshold: int = MAX_DRAW_NODES) -> nx.Graph:
    if G.number_of_nodes() <= threshold:
        return G
    warnings.warn("Graph has more than {0} nodes; drawing a sampled subgraph.".format(threshold), RuntimeWarning)
    nodes = list(G.nodes())[:threshold]
    return G.subgraph(nodes).copy()


def _layout(G: nx.Graph, seed: int = 42) -> dict[Any, tuple[float, float]]:
    if G.number_of_nodes() == 0:
        return {}
    if G.number_of_nodes() >= 300:
        raw = nx.random_layout(nx.Graph(G), seed=seed)
        return {node: (float(coords[0]), float(coords[1])) for node, coords in raw.items()}
    return nx.spring_layout(nx.Graph(G), seed=seed)


def plot_layer(G: nx.Graph, output_path: str, title: Optional[str] = None, communities: Optional[dict[Any, Any]] = None, node_size_by: Optional[str] = None) -> None:
    H = _drawable_graph(G)
    fig, ax = plt.subplots(figsize=(8, 6))
    pos = _layout(H)
    if H.number_of_nodes() == 0:
        ax.text(0.5, 0.5, "Empty layer", ha="center", va="center")
    else:
        colors = [communities.get(n, 0) if communities else 0 for n in H.nodes()]
        sizes = [50 + 20 * float(H.nodes[n].get(node_size_by, 1)) if node_size_by else 80 for n in H.nodes()]
        nx.draw_networkx_edges(H, pos, ax=ax, alpha=0.25, width=0.8)
        nx.draw_networkx_nodes(H, pos, ax=ax, node_color=colors, node_size=sizes, cmap="tab20")
    ax.set_title(title or "Layer")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def _multilayer_positions(mln: Any) -> dict[tuple[str, Any], tuple[float, float]]:
    positions: dict[tuple[str, Any], tuple[float, float]] = {}
    layer_names = list(mln.layers)
    for idx, layer in enumerate(layer_names):
        H = _drawable_graph(mln.layers[layer])
        pos = _layout(H, seed=42 + idx)
        y_offset = -float(idx) * 2.5
        for node, (x, y) in pos.items():
            positions[(layer, node)] = (x, y + y_offset)
    return positions


def plot_multilayer_2d(mln: Any, output_path: str, layout: str = "spring", show_dependencies: bool = True, show_simplices: bool = True) -> None:
    del layout
    fig, ax = plt.subplots(figsize=(10, max(5, 2.5 * max(1, len(mln.layers)))))
    positions = _multilayer_positions(mln)
    if not mln.layers:
        ax.text(0.5, 0.5, "No layers", ha="center", va="center")
    for layer, G in mln.layers.items():
        H = _drawable_graph(G)
        layer_pos = {n: positions[(layer, n)] for n in H.nodes() if (layer, n) in positions}
        nx.draw_networkx_edges(H, layer_pos, ax=ax, alpha=0.25, width=0.8)
        nx.draw_networkx_nodes(H, layer_pos, ax=ax, node_size=45, label=layer)
        if layer_pos:
            y = sum(p[1] for p in layer_pos.values()) / len(layer_pos)
            ax.text(-1.25, y, layer, fontsize=11, fontweight="bold", va="center")
        if show_simplices:
            for tri in mln.simplices.get(layer, [])[:1000]:
                if all((layer, n) in positions for n in tri):
                    poly = Polygon([positions[(layer, n)] for n in tri], closed=True, alpha=0.08, color="tab:orange")
                    ax.add_patch(poly)
    if show_dependencies:
        for (a, b), deps in mln.dependencies.items():
            for u, v, _ in deps[:3000]:
                if (a, u) in positions and (b, v) in positions:
                    ax.plot([positions[(a, u)][0], positions[(b, v)][0]], [positions[(a, u)][1], positions[(b, v)][1]], "--", color="black", alpha=0.12, linewidth=0.7)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def plot_multilayer_3d(mln: Any, output_path: str, show_dependencies: bool = True, show_simplices: bool = True) -> None:
    try:
        import plotly.graph_objects as go

        traces = []
        positions2d = _multilayer_positions(mln)
        z_for = {layer: idx for idx, layer in enumerate(mln.layers)}
        for layer, G in mln.layers.items():
            edge_x, edge_y, edge_z = [], [], []
            for u, v in _drawable_graph(G).edges():
                if (layer, u) in positions2d and (layer, v) in positions2d:
                    x1, y1 = positions2d[(layer, u)]
                    x2, y2 = positions2d[(layer, v)]
                    z = z_for[layer]
                    edge_x += [x1, x2, None]
                    edge_y += [y1, y2, None]
                    edge_z += [z, z, None]
            traces.append(go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode="lines", line=dict(width=2), name="{0} edges".format(layer)))
            xs, ys, zs, text = [], [], [], []
            for node in _drawable_graph(G).nodes():
                if (layer, node) in positions2d:
                    x, y = positions2d[(layer, node)]
                    xs.append(x)
                    ys.append(y)
                    zs.append(z_for[layer])
                    text.append(str(node))
            traces.append(go.Scatter3d(x=xs, y=ys, z=zs, mode="markers", marker=dict(size=3), text=text, name=layer))
        if show_dependencies:
            xs, ys, zs = [], [], []
            for (a, b), deps in mln.dependencies.items():
                for u, v, _ in deps[:3000]:
                    if (a, u) in positions2d and (b, v) in positions2d:
                        x1, y1 = positions2d[(a, u)]
                        x2, y2 = positions2d[(b, v)]
                        xs += [x1, x2, None]
                        ys += [y1, y2, None]
                        zs += [z_for[a], z_for[b], None]
            traces.append(go.Scatter3d(x=xs, y=ys, z=zs, mode="lines", line=dict(width=1, dash="dash"), name="dependencies"))
        fig = go.Figure(data=traces)
        fig.write_html(output_path)
    except Exception:
        if not output_path.lower().endswith(".png"):
            output_path = os.path.splitext(output_path)[0] + ".png"
        fig = plt.figure(figsize=(9, 7))
        ax = fig.add_subplot(111, projection="3d")
        positions2d = _multilayer_positions(mln)
        z_for = {layer: idx for idx, layer in enumerate(mln.layers)}
        for layer, G in mln.layers.items():
            for u, v in _drawable_graph(G).edges():
                if (layer, u) in positions2d and (layer, v) in positions2d:
                    x1, y1 = positions2d[(layer, u)]
                    x2, y2 = positions2d[(layer, v)]
                    ax.plot([x1, x2], [y1, y2], [z_for[layer], z_for[layer]], alpha=0.25)
        fig.tight_layout()
        fig.savefig(output_path, dpi=160)
        plt.close(fig)


def plot_dependency_matrix(mln: Any, output_path: str) -> None:
    layers = list(mln.layers)
    matrix = [[len(mln.dependencies.get((a, b), [])) for b in layers] for a in layers]
    fig, ax = plt.subplots(figsize=(6, 5))
    image = ax.imshow(matrix, cmap="Blues")
    ax.set_xticks(range(len(layers)), layers, rotation=45, ha="right")
    ax.set_yticks(range(len(layers)), layers)
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            ax.text(j, i, str(value), ha="center", va="center")
    fig.colorbar(image, ax=ax)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def plot_layer_summary(mln: Any, output_path: str) -> None:
    summary = mln.summary()
    layers = list(mln.layers)
    nodes = [summary["nodes_per_layer"].get(layer, 0) for layer in layers]
    edges = [summary["edges_per_layer"].get(layer, 0) for layer in layers]
    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(layers))
    ax.bar([i - 0.2 for i in x], nodes, width=0.4, label="nodes")
    ax.bar([i + 0.2 for i in x], edges, width=0.4, label="edges")
    ax.set_xticks(list(x), layers)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def plot_cascade_results(results_csv: str, output_path: str) -> None:
    with open(results_csv, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    fig, ax = plt.subplots(figsize=(8, 5))
    if rows:
        keys = [k for k in rows[0] if k.lower() not in {"step", "time"}]
        x_key = "step" if "step" in rows[0] else ("time" if "time" in rows[0] else None)
        x = [float(row[x_key]) if x_key else idx for idx, row in enumerate(rows)]
        for key in keys:
            ax.plot(x, [float(row[key]) for row in rows], label=key)
        ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def export_interactive_html(mln: Any, output_path: str) -> None:
    try:
        from pyvis.network import Network

        net = Network(height="750px", width="100%")
        for layer, G in mln.layers.items():
            for node in G.nodes():
                net.add_node("{0}:{1}".format(layer, node), label=str(node), group=layer)
            for u, v in G.edges():
                net.add_edge("{0}:{1}".format(layer, u), "{0}:{1}".format(layer, v))
        for (a, b), deps in mln.dependencies.items():
            for u, v, _ in deps:
                net.add_edge("{0}:{1}".format(a, u), "{0}:{1}".format(b, v), dashes=True, color="#555555")
        net.write_html(output_path)
    except Exception:
        with open(output_path, "w", encoding="utf-8") as handle:
            handle.write("<html><body><h1>Interactive visualization unavailable</h1><p>Install pyvis to export interactive multilayer HTML.</p></body></html>")
