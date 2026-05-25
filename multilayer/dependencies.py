"""Dependency link generation across multilayer network layers."""

from __future__ import annotations

import random
from typing import Any, Optional

import networkx as nx


def _count_for_q(Ga: nx.Graph, Gb: nx.Graph, q: float) -> int:
    if not 0.0 <= q <= 1.0:
        raise ValueError("q must be in [0, 1]")
    return int(round(min(Ga.number_of_nodes(), Gb.number_of_nodes()) * q))


def generate_random_matching(
    layer_a_graph: nx.Graph,
    layer_b_graph: nx.Graph,
    q: float,
    seed: Optional[int] = None,
    bidirectional: bool = True,
) -> list[tuple[Any, Any, float]]:
    del bidirectional
    rng = random.Random(seed)
    count = _count_for_q(layer_a_graph, layer_b_graph, q)
    nodes_a = list(layer_a_graph.nodes())
    nodes_b = list(layer_b_graph.nodes())
    rng.shuffle(nodes_a)
    rng.shuffle(nodes_b)
    return [(a, b, 1.0) for a, b in zip(nodes_a[:count], nodes_b[:count])]


def generate_same_id_dependencies(
    layer_a_graph: nx.Graph,
    layer_b_graph: nx.Graph,
    q: float = 1.0,
    bidirectional: bool = True,
) -> list[tuple[Any, Any, float]]:
    del bidirectional
    common = sorted(set(layer_a_graph.nodes()).intersection(layer_b_graph.nodes()), key=lambda item: str(item))
    count = min(len(common), _count_for_q(layer_a_graph, layer_b_graph, q))
    return [(node, node, 1.0) for node in common[:count]]


def generate_degree_assortative_dependencies(
    layer_a_graph: nx.Graph,
    layer_b_graph: nx.Graph,
    q: float,
    seed: Optional[int] = None,
    bidirectional: bool = True,
) -> list[tuple[Any, Any, float]]:
    del seed, bidirectional
    count = _count_for_q(layer_a_graph, layer_b_graph, q)
    nodes_a = sorted(layer_a_graph.nodes(), key=lambda n: (layer_a_graph.degree(n), str(n)), reverse=True)
    nodes_b = sorted(layer_b_graph.nodes(), key=lambda n: (layer_b_graph.degree(n), str(n)), reverse=True)
    return [(a, b, 1.0) for a, b in zip(nodes_a[:count], nodes_b[:count])]


def generate_weight_based_dependencies(
    layer_a_graph: nx.Graph,
    layer_b_graph: nx.Graph,
    q: float,
    node_weight_attr: str,
    seed: Optional[int] = None,
) -> list[tuple[Any, Any, float]]:
    del seed
    count = _count_for_q(layer_a_graph, layer_b_graph, q)
    nodes_a = sorted(layer_a_graph.nodes(), key=lambda n: (layer_a_graph.nodes[n].get(node_weight_attr, 0), str(n)), reverse=True)
    nodes_b = sorted(layer_b_graph.nodes(), key=lambda n: (layer_b_graph.nodes[n].get(node_weight_attr, 0), str(n)), reverse=True)
    return [
        (a, b, float(layer_a_graph.nodes[a].get(node_weight_attr, 1.0) + layer_b_graph.nodes[b].get(node_weight_attr, 1.0)) / 2.0)
        for a, b in zip(nodes_a[:count], nodes_b[:count])
    ]
