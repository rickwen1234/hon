"""Peng-style recursive cascade simulation."""

from __future__ import annotations

import random
from typing import Any

from .failure_rules import dependency_failures, simplex_failures
from .metrics import giant_component_ratio
from .peng_model import PengCascadeConfig, PengCascadeState


def initial_attack(nodes: list[Any], fraction: float, seed: int | None = None) -> set[Any]:
    rng = random.Random(seed)
    count = int(round(max(0.0, min(1.0, fraction)) * len(nodes)))
    selected = nodes[:]
    rng.shuffle(selected)
    return set(selected[:count])


def run_peng_cascade(state: PengCascadeState, config: PengCascadeConfig) -> list[dict[str, Any]]:
    if not state.failed_a and not state.failed_b:
        state.failed_a.update(initial_attack(list(state.graph_a.nodes()), config.initial_failure_fraction, config.seed))
    rows: list[dict[str, Any]] = []
    step = 0
    while True:
        rows.append({
            "step": step,
            "failed_A": len(state.failed_a),
            "failed_B": len(state.failed_b),
            "giant_A": giant_component_ratio(state.graph_a, state.failed_a),
            "giant_B": giant_component_ratio(state.graph_b, state.failed_b),
        })
        new_a: set[Any] = set()
        new_b: set[Any] = set()
        if config.simplex_failure:
            new_a.update(simplex_failures(state.triangles_a, state.failed_a))
            new_b.update(simplex_failures(state.triangles_b, state.failed_b))
        if config.dependency_failure:
            dep_a, dep_b = dependency_failures(state.dependencies, state.failed_a | new_a, state.failed_b | new_b)
            new_a.update(dep_a)
            new_b.update(dep_b)
        if not new_a and not new_b:
            break
        state.failed_a.update(new_a)
        state.failed_b.update(new_b)
        step += 1
    return rows
