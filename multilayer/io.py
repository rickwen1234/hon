"""Load and save multilayer network files."""

from __future__ import annotations

import csv
import os
from typing import Any

import networkx as nx

from .utils import ensure_dir, read_json, write_json


def _read_rows(path: str) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as handle:
        sample = handle.read(2048)
        handle.seek(0)
        has_header = csv.Sniffer().has_header(sample) if sample.strip() else False
        if has_header:
            return [dict(row) for row in csv.DictReader(handle)]
        rows = []
        for row in csv.reader(handle):
            if row:
                rows.append({str(i): value for i, value in enumerate(row)})
        return rows


def _field(row: dict[str, str], names: list[str], fallback: str) -> str:
    for name in names:
        if name in row:
            return row[name]
    return row[fallback]


def load_edge_list(path: str, directed: bool = False) -> nx.Graph:
    G: nx.Graph = nx.DiGraph() if directed else nx.Graph()
    for row in _read_rows(path):
        source = _field(row, ["source", "from", "from_node"], "0")
        target = _field(row, ["target", "to", "to_node"], "1")
        weight = float(row.get("weight", row.get("2", 1.0)) or 1.0)
        attrs: dict[str, Any] = {"weight": weight}
        if "timestamp" in row:
            attrs["timestamp"] = row["timestamp"]
        G.add_edge(source, target, **attrs)
    G.graph["source"] = "loaded"
    G.graph["graph_type"] = "directed" if directed else "undirected"
    return G


def load_hon_edge_list(path: str, directed: bool = True) -> nx.Graph:
    G = load_edge_list(path, directed=directed)
    G.graph["source"] = "hon"
    return G


def load_dependency_list(path: str) -> dict[tuple[str, str], list[tuple[str, str, float]]]:
    deps: dict[tuple[str, str], list[tuple[str, str, float]]] = {}
    for row in _read_rows(path):
        source_layer = _field(row, ["source_layer"], "0")
        source_node = _field(row, ["source_node"], "1")
        target_layer = _field(row, ["target_layer"], "2")
        target_node = _field(row, ["target_node"], "3")
        weight = float(row.get("weight", row.get("4", 1.0)) or 1.0)
        deps.setdefault((source_layer, target_layer), []).append((source_node, target_node, weight))
    return deps


def load_simplex_list(path: str) -> dict[str, list[tuple[str, str, str]]]:
    simplices: dict[str, list[tuple[str, str, str]]] = {}
    for row in _read_rows(path):
        layer = _field(row, ["layer"], "0")
        n1 = _field(row, ["node1"], "1")
        n2 = _field(row, ["node2"], "2")
        n3 = _field(row, ["node3"], "3")
        simplices.setdefault(layer, []).append((n1, n2, n3))
    return simplices


def _write_edges(path: str, G: nx.Graph) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["source", "target", "weight"])
        for u, v, data in G.edges(data=True):
            writer.writerow([u, v, data.get("weight", 1.0)])


def _write_dependencies(path: str, source_layer: str, target_layer: str, deps: list[tuple[Any, Any, float]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["source_layer", "source_node", "target_layer", "target_node", "weight"])
        for source_node, target_node, weight in deps:
            writer.writerow([source_layer, source_node, target_layer, target_node, weight])


def _write_simplices(path: str, layer: str, triangles: list[tuple[Any, Any, Any]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["layer", "node1", "node2", "node3", "weight"])
        for n1, n2, n3 in triangles:
            writer.writerow([layer, n1, n2, n3, 1.0])


def save_multilayer_network(mln: object, output_dir: str) -> None:
    ensure_dir(output_dir)
    layers_dir = os.path.join(output_dir, "layers")
    deps_dir = os.path.join(output_dir, "dependencies")
    simplices_dir = os.path.join(output_dir, "simplices")
    ensure_dir(layers_dir)
    ensure_dir(deps_dir)
    ensure_dir(simplices_dir)

    for name, graph in mln.layers.items():
        _write_edges(os.path.join(layers_dir, "{0}_edges.csv".format(name)), graph)
    for (source_layer, target_layer), deps in mln.dependencies.items():
        _write_dependencies(
            os.path.join(deps_dir, "{0}__{1}_dependencies.csv".format(source_layer, target_layer)),
            source_layer,
            target_layer,
            deps,
        )
    for layer, triangles in mln.simplices.items():
        _write_simplices(os.path.join(simplices_dir, "{0}_triangles.csv".format(layer)), layer, triangles)

    write_json(os.path.join(output_dir, "metadata.json"), mln.metadata_for_export())
    write_json(os.path.join(output_dir, "summary.json"), mln.summary())


def load_multilayer_network(input_dir: str):
    from .core import MultiLayerNetwork

    mln = MultiLayerNetwork()
    metadata_path = os.path.join(input_dir, "metadata.json")
    metadata = read_json(metadata_path) if os.path.exists(metadata_path) else {}
    layers_meta = metadata.get("layers", {})
    layers_dir = os.path.join(input_dir, "layers")
    if os.path.isdir(layers_dir):
        for filename in os.listdir(layers_dir):
            if not filename.endswith("_edges.csv"):
                continue
            name = filename[: -len("_edges.csv")]
            layer_meta = layers_meta.get(name, {})
            directed = layer_meta.get("graph_type") == "directed"
            G = load_edge_list(os.path.join(layers_dir, filename), directed=directed)
            G.graph.update(layer_meta)
            mln.add_layer(name, graph=G, graph_type=layer_meta.get("graph_type", "directed" if directed else "undirected"), source=layer_meta.get("source", "loaded"), metadata=layer_meta.get("metadata", {}))

    deps_dir = os.path.join(input_dir, "dependencies")
    if os.path.isdir(deps_dir):
        for filename in os.listdir(deps_dir):
            if filename.endswith("_dependencies.csv"):
                for pair, deps in load_dependency_list(os.path.join(deps_dir, filename)).items():
                    mln.dependencies[pair] = deps

    simplices_dir = os.path.join(input_dir, "simplices")
    if os.path.isdir(simplices_dir):
        for filename in os.listdir(simplices_dir):
            if filename.endswith("_triangles.csv"):
                for layer, triangles in load_simplex_list(os.path.join(simplices_dir, filename)).items():
                    mln.simplices[layer] = triangles
    mln.metadata.update(metadata.get("metadata", {}))
    mln.metadata["_export_metadata"] = metadata
    return mln
