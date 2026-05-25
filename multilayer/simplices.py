"""Triangle simplex detection and generation."""

from __future__ import annotations

import random
import warnings
from typing import Any, Optional

import networkx as nx

from .utils import normalize_triangle


def triangles_from_graph(G: nx.Graph) -> list[tuple[Any, Any, Any]]:
    if G.number_of_nodes() < 3:
        warnings.warn("Graph has fewer than three nodes; no triangles possible.", RuntimeWarning)
        return []
    H = nx.Graph(G)
    triangles: set[tuple[Any, Any, Any]] = set()
    for node in H:
        neighbors = list(H.neighbors(node))
        for i, u in enumerate(neighbors):
            for v in neighbors[i + 1 :]:
                if H.has_edge(u, v):
                    triangles.add(normalize_triangle((node, u, v)))
    if not triangles and H.number_of_edges() < 3:
        warnings.warn("Graph is too sparse for closed triangles.", RuntimeWarning)
    return sorted(triangles, key=lambda tri: tuple(str(x) for x in tri))


def cliques_k3(G: nx.Graph) -> list[tuple[Any, Any, Any]]:
    if G.number_of_nodes() < 3:
        warnings.warn("Graph has fewer than three nodes; no k=3 cliques possible.", RuntimeWarning)
        return []
    triangles = {
        normalize_triangle(tuple(clique))
        for clique in nx.enumerate_all_cliques(nx.Graph(G))
        if len(clique) == 3
    }
    return sorted(triangles, key=lambda tri: tuple(str(x) for x in tri))


def random_triangles(G: nx.Graph, count: int, seed: Optional[int] = None) -> list[tuple[Any, Any, Any]]:
    nodes = list(G.nodes())
    if len(nodes) < 3:
        warnings.warn("Graph has fewer than three nodes; no random triangles possible.", RuntimeWarning)
        return []
    rng = random.Random(seed)
    triangles: set[tuple[Any, Any, Any]] = set()
    attempts = 0
    max_attempts = max(100, count * 20)
    while len(triangles) < count and attempts < max_attempts:
        attempts += 1
        tri = normalize_triangle(tuple(rng.sample(nodes, 3)))
        if len(set(tri)) == 3:
            triangles.add(tri)
    return sorted(triangles, key=lambda tri: tuple(str(x) for x in tri))


def poisson_triangle_simplices(
    G: nx.Graph,
    mean_triangle_degree: float,
    seed: Optional[int] = None,
) -> list[tuple[Any, Any, Any]]:
    nodes = list(G.nodes())
    if len(nodes) < 3:
        warnings.warn("Graph has fewer than three nodes; no Poisson triangles possible.", RuntimeWarning)
        return []
    rng = random.Random(seed)
    try:
        import numpy as np

        prng = np.random.default_rng(seed)
        counts = prng.poisson(mean_triangle_degree, len(nodes)).tolist()
    except Exception:
        lam = max(0.0, float(mean_triangle_degree))
        counts = [max(0, int(round(rng.expovariate(1.0 / lam)))) if lam else 0 for _ in nodes]
    stubs: list[Any] = []
    for node, stub_count in zip(nodes, counts):
        stubs.extend([node] * int(stub_count))
    rng.shuffle(stubs)
    triangles: set[tuple[Any, Any, Any]] = set()
    while len(stubs) >= 3:
        tri_nodes = [stubs.pop(), stubs.pop(), stubs.pop()]
        if len(set(tri_nodes)) != 3:
            continue
        triangles.add(normalize_triangle(tuple(tri_nodes)))
    return sorted(triangles, key=lambda tri: tuple(str(x) for x in tri))
