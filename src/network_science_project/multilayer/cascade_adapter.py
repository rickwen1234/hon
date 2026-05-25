"""Adapters from MultiLayerNetwork to Peng-style cascade inputs."""

from __future__ import annotations

import csv
import os
from typing import Any

from .utils import ensure_dir, write_json


def _write_edges(path: str, G: Any) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["source", "target", "weight"])
        for u, v, data in G.edges(data=True):
            writer.writerow([u, v, data.get("weight", 1.0)])


def _write_triangles(path: str, triangles: list[tuple[Any, Any, Any]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["node1", "node2", "node3", "weight"])
        for n1, n2, n3 in triangles:
            writer.writerow([n1, n2, n3, 1.0])


def export_peng_cascade_inputs(mln: Any, output_dir: str, layer_a: str, layer_b: str) -> None:
    ensure_dir(output_dir)
    if layer_a not in mln.layers or layer_b not in mln.layers:
        raise ValueError("Peng cascade export requires existing layer_a and layer_b")
    _write_edges(os.path.join(output_dir, "layer_A_edges.csv"), mln.layers[layer_a])
    _write_edges(os.path.join(output_dir, "layer_B_edges.csv"), mln.layers[layer_b])
    _write_triangles(os.path.join(output_dir, "layer_A_triangles.csv"), mln.simplices.get(layer_a, []))
    _write_triangles(os.path.join(output_dir, "layer_B_triangles.csv"), mln.simplices.get(layer_b, []))

    deps = mln.dependencies.get((layer_a, layer_b), [])
    if not deps:
        deps = [(b, a, w) for b, a, w in mln.dependencies.get((layer_b, layer_a), [])]
    with open(os.path.join(output_dir, "dependency_links.csv"), "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["source_node", "target_node", "weight"])
        for source_node, target_node, weight in deps:
            writer.writerow([source_node, target_node, weight])

    spec = mln.dependency_specs.get((layer_a, layer_b)) or mln.dependency_specs.get((layer_b, layer_a))
    q = spec.q if spec else (len(deps) / float(min(mln.layers[layer_a].number_of_nodes(), mln.layers[layer_b].number_of_nodes()) or 1))
    write_json(
        os.path.join(output_dir, "cascade_config.json"),
        {
            "layer_a": layer_a,
            "layer_b": layer_b,
            "q": q,
            "n_A": mln.layers[layer_a].number_of_nodes(),
            "n_B": mln.layers[layer_b].number_of_nodes(),
            "edge_type": "ordinary_or_hon_edge_list",
            "simplex_type": "triangle",
            "notes": "Prepared inputs for Peng-style two-layer partially interdependent cascade simulation.",
        },
    )
