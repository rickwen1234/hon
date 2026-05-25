"""Cascade robustness metrics."""

from __future__ import annotations

from typing import Any

import networkx as nx


def largest_component_size(G: nx.Graph, failed: set[Any]) -> int:
    active = [node for node in G.nodes() if node not in failed]
    if not active:
        return 0
    subgraph = nx.Graph(G).subgraph(active)
    return max((len(component) for component in nx.connected_components(subgraph)), default=0)


def giant_component_ratio(G: nx.Graph, failed: set[Any]) -> float:
    total = G.number_of_nodes()
    return 0.0 if total == 0 else largest_component_size(G, failed) / float(total)
