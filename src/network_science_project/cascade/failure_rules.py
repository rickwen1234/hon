"""Failure propagation rules for Peng-style cascades."""

from __future__ import annotations

from typing import Any


def simplex_failures(triangles: list[tuple[Any, Any, Any]], failed: set[Any]) -> set[Any]:
    """Propagate failure within triangles.

    If any node in a triangle has failed, all nodes in that simplex are marked
    failed. This implements a conservative recursive same-layer simplex rule.
    """
    new_failed: set[Any] = set()
    for triangle in triangles:
        if any(node in failed for node in triangle):
            new_failed.update(triangle)
    return new_failed - failed


def dependency_failures(
    dependencies: list[tuple[Any, Any, float]],
    failed_a: set[Any],
    failed_b: set[Any],
) -> tuple[set[Any], set[Any]]:
    new_a: set[Any] = set()
    new_b: set[Any] = set()
    for node_a, node_b, _ in dependencies:
        if node_a in failed_a and node_b not in failed_b:
            new_b.add(node_b)
        if node_b in failed_b and node_a not in failed_a:
            new_a.add(node_a)
    return new_a, new_b

# unused feature, but could be useful for future work on higher-order simplices
def high_order_simplex_failures(simplexes: list[tuple[Any, ...]], failed: set[Any], critical_failure: float = 0.0) -> set[Any]:
    """Propagate failure within simplices of any order.

    If enough nodes in a simplex have failed, all nodes in that simplex are marked
    failed. This implements a conservative recursive same-layer simplex rule.
    """
    new_failed: set[Any] = set()
    for simplex in simplexes:
        if sum(node in failed for node in simplex) >= critical_failure * len(simplex):
            new_failed.update(simplex)
    return new_failed - failed


