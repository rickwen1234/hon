"""Core multilayer network data model."""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

import networkx as nx

from . import dependencies as depgen
from . import generators, simplices
from .utils import is_hon_label


@dataclass
class LayerSpec:
    name: str
    graph: Optional[nx.Graph] = None
    graph_type: str = "undirected"
    source: str = "empty"
    node_mapping: Optional[dict[Any, Any]] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GeneratorSpec:
    model: str
    n: int
    mean_degree: Optional[float] = None
    p: Optional[float] = None
    m: Optional[int] = None
    gamma: Optional[float] = None
    seed: Optional[int] = None
    directed: bool = False


@dataclass
class DependencySpec:
    source_layer: str
    target_layer: str
    mode: str = "random_matching"
    q: float = 1.0
    bidirectional: bool = True
    seed: Optional[int] = None
    path: Optional[str] = None


@dataclass
class SimplexSpec:
    layer: str
    mode: str = "triangles_from_graph"
    mean_triangle_degree: Optional[float] = None
    count: Optional[int] = None
    path: Optional[str] = None
    seed: Optional[int] = None


@dataclass
class VisualizationConfig:
    layout: str = "spring"
    show_dependencies: bool = True
    show_simplices: bool = True
    sample_threshold: int = 5000
    seed: Optional[int] = 42


class MultiLayerNetwork:
    def __init__(self, metadata: Optional[dict[str, Any]] = None) -> None:
        self.layers: dict[str, nx.Graph] = {}
        self.layer_specs: dict[str, LayerSpec] = {}
        self.dependencies: dict[tuple[str, str], list[tuple[Any, Any, float]]] = {}
        self.dependency_specs: dict[tuple[str, str], DependencySpec] = {}
        self.simplices: dict[str, list[tuple[Any, Any, Any]]] = {}
        self.simplex_specs: dict[str, list[SimplexSpec]] = {}
        self.metadata: dict[str, Any] = metadata or {}

    def add_layer(self, name: str, graph: Optional[nx.Graph] = None, generator: Optional[GeneratorSpec] = None, graph_type: str = "undirected", **kwargs: Any) -> nx.Graph:
        source = kwargs.pop("source", "empty")
        metadata = kwargs.pop("metadata", {})
        if generator is not None:
            graph = generators.generate_from_spec(generator)
            graph_type = "directed" if generator.directed else "undirected"
            source = "generated"
            metadata = {**metadata, "generator": asdict(generator)}
        if graph is None:
            graph = nx.DiGraph() if graph_type == "directed" else nx.Graph()
        if graph_type == "directed" and not graph.is_directed():
            graph = nx.DiGraph(graph)
        elif graph_type == "undirected" and graph.is_directed():
            graph = nx.Graph(graph)
        graph.graph.setdefault("source", source)
        graph.graph.setdefault("graph_type", graph_type)
        graph.graph.update(metadata)
        self.layers[name] = graph
        self.layer_specs[name] = LayerSpec(name=name, graph=graph, graph_type=graph_type, source=source, node_mapping=kwargs.get("node_mapping"), metadata=metadata)
        return graph

    def remove_layer(self, name: str) -> None:
        self.layers.pop(name, None)
        self.layer_specs.pop(name, None)
        self.simplices.pop(name, None)
        self.simplex_specs.pop(name, None)
        for pair in list(self.dependencies):
            if name in pair:
                self.dependencies.pop(pair, None)
                self.dependency_specs.pop(pair, None)

    def get_layer(self, name: str) -> nx.Graph:
        return self.layers[name]

    def list_layers(self) -> list[str]:
        return list(self.layers.keys())

    def add_dependency(self, source_layer: str, target_layer: str, mode: str = "random_matching", q: float = 1.0, bidirectional: bool = True, **kwargs: Any) -> list[tuple[Any, Any, float]]:
        if source_layer not in self.layers or target_layer not in self.layers:
            raise ValueError("Dependency references missing layer")
        Ga, Gb = self.layers[source_layer], self.layers[target_layer]
        seed = kwargs.get("seed")
        if mode == "random_matching":
            deps = depgen.generate_random_matching(Ga, Gb, q, seed, bidirectional)
        elif mode == "same_id":
            deps = depgen.generate_same_id_dependencies(Ga, Gb, q, bidirectional)
        elif mode == "degree_assortative":
            deps = depgen.generate_degree_assortative_dependencies(Ga, Gb, q, seed, bidirectional)
        elif mode == "weight_based":
            deps = depgen.generate_weight_based_dependencies(Ga, Gb, q, kwargs.get("node_weight_attr", "weight"), seed)
        elif mode == "from_file":
            from .io import load_dependency_list

            loaded = load_dependency_list(kwargs["path"])
            deps = loaded.get((source_layer, target_layer), [])
        else:
            raise ValueError("Unknown dependency mode: {0}".format(mode))
        pair = (source_layer, target_layer)
        self.dependencies[pair] = deps
        self.dependency_specs[pair] = DependencySpec(source_layer, target_layer, mode, q, bidirectional, seed, kwargs.get("path"))
        return deps

    def add_simplices(self, layer: str, mode: str = "triangles_from_graph", **kwargs: Any) -> list[tuple[Any, Any, Any]]:
        if layer not in self.layers:
            raise ValueError("Simplex references missing layer")
        G = self.layers[layer]
        if mode == "triangles_from_graph":
            triangles = simplices.triangles_from_graph(G)
        elif mode == "cliques_k3":
            triangles = simplices.cliques_k3(G)
        elif mode == "poisson_triangles":
            triangles = simplices.poisson_triangle_simplices(G, kwargs.get("mean_triangle_degree", 0.1), kwargs.get("seed"))
        elif mode == "random_triangles":
            triangles = simplices.random_triangles(G, kwargs.get("count", 0), kwargs.get("seed"))
        elif mode == "from_file":
            from .io import load_simplex_list

            triangles = load_simplex_list(kwargs["path"]).get(layer, [])
        else:
            raise ValueError("Unknown simplex mode: {0}".format(mode))
        self.simplices[layer] = triangles
        self.simplex_specs.setdefault(layer, []).append(SimplexSpec(layer, mode, kwargs.get("mean_triangle_degree"), kwargs.get("count"), kwargs.get("path"), kwargs.get("seed")))
        return triangles

    def project_physical_graph(self, layer_name: Optional[str] = None, include_dependencies: bool = False) -> nx.Graph:
        graph = nx.Graph()
        layer_names = [layer_name] if layer_name else list(self.layers)
        for name in layer_names:
            G = self.layers[name]
            graph.add_nodes_from(((name, node), data) for node, data in G.nodes(data=True))
            graph.add_edges_from(((name, u), (name, v), data) for u, v, data in G.edges(data=True))
        if include_dependencies:
            for (a, b), deps in self.dependencies.items():
                if a in layer_names and b in layer_names:
                    for u, v, weight in deps:
                        graph.add_edge((a, u), (b, v), weight=weight, dependency=True)
        return graph

    def summary(self) -> dict[str, Any]:
        layers = {}
        for name, G in self.layers.items():
            undirected = nx.Graph(G)
            layers[name] = {
                "nodes": G.number_of_nodes(),
                "edges": G.number_of_edges(),
                "average_degree": (sum(dict(G.degree()).values()) / float(G.number_of_nodes())) if G.number_of_nodes() else 0.0,
                "clustering_coefficient": nx.average_clustering(undirected) if undirected.number_of_nodes() else 0.0,
                "connected_components": nx.number_connected_components(undirected) if undirected.number_of_nodes() else 0,
            }
        return {
            "number_of_layers": len(self.layers),
            "nodes_per_layer": {k: v["nodes"] for k, v in layers.items()},
            "edges_per_layer": {k: v["edges"] for k, v in layers.items()},
            "dependencies_per_layer_pair": {"{0}__{1}".format(*pair): len(deps) for pair, deps in self.dependencies.items()},
            "simplices_per_layer": {layer: len(items) for layer, items in self.simplices.items()},
            "average_degree_per_layer": {k: v["average_degree"] for k, v in layers.items()},
            "clustering_coefficient_per_layer": {k: v["clustering_coefficient"] for k, v in layers.items()},
            "connected_components_per_layer": {k: v["connected_components"] for k, v in layers.items()},
        }

    def validate(self, allow_multi_dependency: bool = False) -> list[str]:
        errors: list[str] = []
        for name, G in self.layers.items():
            if self.layer_specs.get(name, LayerSpec(name)).source == "generated" and G.number_of_nodes() == 0:
                errors.append("Generated layer {0} is empty".format(name))
            if self.layer_specs.get(name) and self.layer_specs[name].source == "hon":
                for node in G.nodes():
                    if not is_hon_label(node):
                        errors.append("Malformed HON label in {0}: {1}".format(name, node))
        for pair, spec in self.dependency_specs.items():
            if not 0.0 <= spec.q <= 1.0:
                errors.append("q outside [0,1] for {0}".format(pair))
        for (source_layer, target_layer), deps in self.dependencies.items():
            if source_layer not in self.layers or target_layer not in self.layers:
                errors.append("Dependency references missing layer {0}->{1}".format(source_layer, target_layer))
                continue
            seen = set()
            for source_node, target_node, _ in deps:
                if source_node not in self.layers[source_layer]:
                    errors.append("Dependency node missing: {0}:{1}".format(source_layer, source_node))
                if target_node not in self.layers[target_layer]:
                    errors.append("Dependency node missing: {0}:{1}".format(target_layer, target_node))
                if not allow_multi_dependency and (source_node, target_node) in seen:
                    errors.append("Duplicate dependency: {0}->{1}".format(source_node, target_node))
                seen.add((source_node, target_node))
        for layer, triangles in self.simplices.items():
            if layer not in self.layers:
                errors.append("Simplex references missing layer {0}".format(layer))
                continue
            for tri in triangles:
                if len(set(tri)) != 3:
                    errors.append("Malformed simplex with repeated nodes in {0}: {1}".format(layer, tri))
                for node in tri:
                    if node not in self.layers[layer]:
                        errors.append("Simplex node missing: {0}:{1}".format(layer, node))
        return errors

    def metadata_for_export(self) -> dict[str, Any]:
        return {
            "layers": {
                name: {
                    "graph_type": spec.graph_type,
                    "source": spec.source,
                    "node_mapping": spec.node_mapping,
                    "metadata": spec.metadata,
                }
                for name, spec in self.layer_specs.items()
            },
            "dependencies": {"{0}__{1}".format(*pair): asdict(spec) for pair, spec in self.dependency_specs.items()},
            "simplices": {layer: [asdict(spec) for spec in specs] for layer, specs in self.simplex_specs.items()},
            "metadata": self.metadata,
        }

    def export(self, output_dir: str) -> None:
        from .io import save_multilayer_network

        save_multilayer_network(self, output_dir)

    @classmethod
    def load(cls, input_dir: str) -> "MultiLayerNetwork":
        from .io import load_multilayer_network

        return load_multilayer_network(input_dir)

    def to_cascade_input(self, output_dir: str) -> None:
        from .cascade_adapter import export_peng_cascade_inputs

        if len(self.layers) < 2:
            raise ValueError("At least two layers are required for Peng cascade inputs")
        layer_a, layer_b = list(self.layers)[:2]
        export_peng_cascade_inputs(self, output_dir, layer_a, layer_b)
