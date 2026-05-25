"""Data model for Peng-style two-layer cascade experiments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import networkx as nx


@dataclass
class PengCascadeConfig:
    layer_a: str = "A"
    layer_b: str = "B"
    initial_failure_fraction: float = 0.1
    seed: int | None = None
    simplex_failure: bool = True
    dependency_failure: bool = True


@dataclass
class PengCascadeState:
    graph_a: nx.Graph
    graph_b: nx.Graph
    triangles_a: list[tuple[Any, Any, Any]]
    triangles_b: list[tuple[Any, Any, Any]]
    dependencies: list[tuple[Any, Any, float]]
    failed_a: set[Any]
    failed_b: set[Any]
