"""Layer graph generators for multilayer networks."""

from __future__ import annotations

import math
import random
from typing import Optional

import networkx as nx


def _simple_graph(G: nx.Graph, directed: bool = False) -> nx.Graph:
    H: nx.Graph = nx.DiGraph() if directed else nx.Graph()
    H.add_nodes_from(G.nodes(data=True))
    H.add_edges_from((u, v, d) for u, v, d in G.edges(data=True) if u != v)
    H.graph.update(G.graph)
    return H


def _store_metadata(G: nx.Graph, model: str, **params: object) -> nx.Graph:
    G.graph["generator"] = {"model": model, **params}
    return G


def generate_erdos_renyi_graph(
    n: int,
    p: Optional[float] = None,
    mean_degree: Optional[float] = None,
    seed: Optional[int] = None,
    directed: bool = False,
) -> nx.Graph:
    if n < 0:
        raise ValueError("n must be non-negative")
    if p is None:
        if mean_degree is None:
            raise ValueError("Either p or mean_degree is required")
        p = 0.0 if n <= 1 else min(1.0, max(0.0, float(mean_degree) / float(n - 1)))
    G = nx.gnp_random_graph(n, p, seed=seed, directed=directed)
    return _store_metadata(G, "erdos_renyi", n=n, p=p, mean_degree=mean_degree, seed=seed, directed=directed)


def generate_poisson_graph(n: int, mean_degree: float, seed: Optional[int] = None, directed: bool = False) -> nx.Graph:
    G = generate_erdos_renyi_graph(n, mean_degree=mean_degree, seed=seed, directed=directed)
    G.graph["generator"]["model"] = "poisson"
    return G


def generate_barabasi_albert_graph(n: int, m: int = 3, seed: Optional[int] = None) -> nx.Graph:
    if n <= 0:
        G = nx.Graph()
    else:
        m = max(1, min(int(m), max(1, n - 1)))
        G = nx.barabasi_albert_graph(n, m, seed=seed)
    return _store_metadata(G, "barabasi_albert", n=n, m=m, seed=seed, directed=False)


def _powerlaw_degrees(n: int, gamma: float, mean_degree: Optional[float], seed: Optional[int]) -> list[int]:
    rng = random.Random(seed)
    if n <= 0:
        return []
    raw = [max(1, int(rng.paretovariate(max(0.1, gamma - 1.0)))) for _ in range(n)]
    max_degree = max(1, n - 1)
    if mean_degree:
        current = sum(raw) / float(n)
        scale = float(mean_degree) / current if current else 1.0
        raw = [max(1, min(max_degree, int(round(d * scale)))) for d in raw]
    degrees = [min(max_degree, d) for d in raw]
    if sum(degrees) % 2 == 1:
        degrees[0] = min(max_degree, degrees[0] + 1) if degrees[0] < max_degree else degrees[0] - 1
    return degrees


def generate_configuration_powerlaw_graph(
    n: int,
    gamma: float = 2.5,
    mean_degree: Optional[float] = None,
    seed: Optional[int] = None,
) -> nx.Graph:
    degrees = _powerlaw_degrees(n, gamma, mean_degree, seed)
    if not degrees:
        G = nx.Graph()
    else:
        M = nx.configuration_model(degrees, seed=seed)
        G = _simple_graph(M, directed=False)
        G.add_nodes_from(range(n))
    return _store_metadata(G, "configuration_powerlaw", n=n, gamma=gamma, mean_degree=mean_degree, seed=seed, directed=False)


def generate_scale_free_graph(
    n: int,
    gamma: float = 2.5,
    mean_degree: Optional[float] = None,
    seed: Optional[int] = None,
    directed: bool = False,
) -> nx.Graph:
    if directed:
        M = nx.scale_free_graph(n, seed=seed)
        G = _simple_graph(M, directed=True)
        return _store_metadata(G, "scale_free", n=n, gamma=gamma, mean_degree=mean_degree, seed=seed, directed=True)
    if mean_degree is not None:
        G = generate_configuration_powerlaw_graph(n, gamma=gamma, mean_degree=mean_degree, seed=seed)
        G.graph["generator"]["model"] = "scale_free"
        return G
    m = max(1, min(n - 1, int(round((mean_degree or 6) / 2.0)))) if n > 1 else 1
    G = generate_barabasi_albert_graph(n, m=m, seed=seed)
    G.graph["generator"]["model"] = "scale_free"
    G.graph["generator"]["gamma"] = gamma
    G.graph["generator"]["mean_degree"] = mean_degree
    return G


def generate_from_spec(spec: object) -> nx.Graph:
    model = getattr(spec, "model")
    if model == "poisson":
        return generate_poisson_graph(spec.n, spec.mean_degree or 1.0, spec.seed, spec.directed)
    if model == "erdos_renyi":
        return generate_erdos_renyi_graph(spec.n, spec.p, spec.mean_degree, spec.seed, spec.directed)
    if model == "scale_free":
        return generate_scale_free_graph(spec.n, spec.gamma or 2.5, spec.mean_degree, spec.seed, spec.directed)
    if model == "barabasi_albert":
        return generate_barabasi_albert_graph(spec.n, spec.m or 3, spec.seed)
    if model == "configuration_powerlaw":
        return generate_configuration_powerlaw_graph(spec.n, spec.gamma or 2.5, spec.mean_degree, spec.seed)
    raise ValueError("Unknown generator model: {0}".format(model))
