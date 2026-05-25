"""IO for Peng-style cascade inputs and results."""

from __future__ import annotations

import csv
import json
import os
from typing import Any

import networkx as nx


def read_edge_file(path: str) -> nx.Graph:
    G = nx.Graph()
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames:
            for row in reader:
                source = row.get("source") or row.get("from_node")
                target = row.get("target") or row.get("to_node")
                if source is not None and target is not None:
                    G.add_edge(source, target, weight=float(row.get("weight") or 1.0))
        else:
            handle.seek(0)
            for row in csv.reader(handle):
                if len(row) >= 2:
                    G.add_edge(row[0], row[1], weight=float(row[2]) if len(row) > 2 and row[2] else 1.0)
    return G


def read_triangles(path: str) -> list[tuple[Any, Any, Any]]:
    if not os.path.exists(path):
        return []
    triangles = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            n1 = row.get("node1")
            n2 = row.get("node2")
            n3 = row.get("node3")
            if n1 is not None and n2 is not None and n3 is not None:
                triangles.append((n1, n2, n3))
    return triangles


def read_dependencies(path: str) -> list[tuple[Any, Any, float]]:
    if not os.path.exists(path):
        return []
    deps = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            source = row.get("source_node") or row.get("node_a")
            target = row.get("target_node") or row.get("node_b")
            if source is not None and target is not None:
                deps.append((source, target, float(row.get("weight") or 1.0)))
    return deps


def load_peng_inputs(input_dir: str) -> dict[str, Any]:
    config_path = os.path.join(input_dir, "cascade_config.json")
    config = {}
    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as handle:
            config = json.load(handle)
    return {
        "config": config,
        "graph_a": read_edge_file(os.path.join(input_dir, "layer_A_edges.csv")),
        "graph_b": read_edge_file(os.path.join(input_dir, "layer_B_edges.csv")),
        "triangles_a": read_triangles(os.path.join(input_dir, "layer_A_triangles.csv")),
        "triangles_b": read_triangles(os.path.join(input_dir, "layer_B_triangles.csv")),
        "dependencies": read_dependencies(os.path.join(input_dir, "dependency_links.csv")),
    }


def write_cascade_results(rows: list[dict[str, Any]], path: str) -> None:
    """Write standardized cascade result rows."""
    fields = [
        "model_name",
        "trial_id",
        "removal_fraction",
        "S_A",
        "S_B",
        "failed_A",
        "failed_B",
        "cascade_steps",
        "q",
        "lambda",
        "mu",
        "theta",
    ]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
