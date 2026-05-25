"""Experiment helpers for multilayer network construction."""

from __future__ import annotations

from typing import Any

from network_science_project.multilayer import GeneratorSpec, MultiLayerNetwork
from network_science_project.multilayer.io import load_edge_list, load_hon_edge_list
from network_science_project.multilayer.utils import parse_bool, parse_kv_string
from network_science_project.utils.experiment import prepare_output_dir, write_summary


def build_demo_multilayer(output_dir: str, seed: int = 42) -> MultiLayerNetwork:
    """Build a deterministic two-layer demo network and export it."""
    mln = MultiLayerNetwork()
    mln.add_layer("A", generator=GeneratorSpec(model="poisson", n=100, mean_degree=8, seed=seed))
    mln.add_layer("B", generator=GeneratorSpec(model="scale_free", n=100, gamma=2.5, mean_degree=8, seed=seed + 1))
    mln.add_dependency("A", "B", mode="random_matching", q=0.8, seed=seed)
    mln.add_simplices("A", mode="poisson_triangles", mean_triangle_degree=0.4, seed=seed)
    mln.add_simplices("B", mode="poisson_triangles", mean_triangle_degree=0.4, seed=seed + 1)
    mln.export(output_dir)
    return mln


def parse_layer_spec(text: str, default_seed: int | None) -> tuple[str, str, dict[str, Any]]:
    """Parse a CLI layer spec into `(name, kind, params)`."""
    parts = text.split(":", 3)
    if len(parts) < 2:
        raise ValueError("Malformed layer spec: {0}".format(text))
    name = parts[0]
    if parts[1] == "generated":
        model = parts[2]
        params = parse_kv_string(parts[3] if len(parts) > 3 else "")
        params.setdefault("seed", default_seed)
        return name, "generated", {"model": model, **params}
    kind = parts[1]
    path = parts[2] if len(parts) > 2 else ""
    params = parse_kv_string(parts[3] if len(parts) > 3 else "")
    return name, kind, {"path": path, **params}


def parse_dependency_spec(text: str, default_seed: int | None) -> tuple[str, str, str, dict[str, Any]]:
    """Parse a CLI dependency spec into `(source_layer, target_layer, mode, params)`."""
    parts = text.split(":", 3)
    if len(parts) < 3:
        raise ValueError("Malformed dependency spec: {0}".format(text))
    tail = parts[3] if len(parts) > 3 else ""
    params = {"path": tail} if parts[2] == "from_file" and tail and "=" not in tail else parse_kv_string(tail)
    params.setdefault("seed", default_seed)
    return parts[0], parts[1], parts[2], params


def parse_simplex_spec(text: str, default_seed: int | None) -> tuple[str, str, dict[str, Any]]:
    """Parse a CLI simplex spec into `(layer, mode, params)`."""
    parts = text.split(":", 2)
    if len(parts) < 2:
        raise ValueError("Malformed simplex spec: {0}".format(text))
    tail = parts[2] if len(parts) > 2 else ""
    params = {"path": tail} if parts[1] == "from_file" and tail and "=" not in tail else parse_kv_string(tail)
    params.setdefault("seed", default_seed)
    return parts[0], parts[1], params


def build_multilayer_from_specs(
    layer_specs: list[str],
    dependency_specs: list[str] | None = None,
    simplex_specs: list[str] | None = None,
    seed: int | None = None,
) -> MultiLayerNetwork:
    """Build a multilayer network from CLI-style specs."""
    mln = MultiLayerNetwork(metadata={"seed": seed})
    for layer_text in layer_specs:
        name, kind, params = parse_layer_spec(layer_text, seed)
        if kind == "generated":
            spec = GeneratorSpec(
                model=str(params["model"]),
                n=int(params["n"]),
                mean_degree=params.get("mean_degree"),
                p=params.get("p"),
                m=params.get("m"),
                gamma=params.get("gamma"),
                seed=params.get("seed"),
                directed=bool(params.get("directed", False)),
            )
            mln.add_layer(name, generator=spec)
        elif kind == "edge_list":
            directed = parse_bool(str(params.get("directed", "false")))
            mln.add_layer(
                name,
                graph=load_edge_list(str(params["path"]), directed=directed),
                graph_type="directed" if directed else "undirected",
                source="loaded",
                metadata={"path": params["path"]},
            )
        elif kind == "hon_edge_list":
            directed = parse_bool(str(params.get("directed", "true")))
            mln.add_layer(
                name,
                graph=load_hon_edge_list(str(params["path"]), directed=directed),
                graph_type="directed" if directed else "undirected",
                source="hon",
                metadata={"path": params["path"]},
            )
        else:
            raise ValueError("Unknown layer kind: {0}".format(kind))
    for dep_text in dependency_specs or []:
        source, target, mode, params = parse_dependency_spec(dep_text, seed)
        q = float(params.pop("q", 1.0))
        bidirectional = parse_bool(str(params.pop("bidirectional", "true")))
        mln.add_dependency(source, target, mode=mode, q=q, bidirectional=bidirectional, **params)
    for simplex_text in simplex_specs or []:
        layer, mode, params = parse_simplex_spec(simplex_text, seed)
        mln.add_simplices(layer, mode=mode, **params)
    errors = mln.validate()
    if errors:
        raise ValueError("Validation failed:\n" + "\n".join(errors[:20]))
    return mln


def run_multilayer_experiment(
    output_dir: str,
    layer_specs: list[str],
    dependency_specs: list[str] | None = None,
    simplex_specs: list[str] | None = None,
    seed: int | None = None,
    config: dict[str, Any] | None = None,
) -> MultiLayerNetwork:
    """Build and export a multilayer experiment using the standard output layout."""
    config_used = {
        "seed": seed,
        "layers": layer_specs,
        "dependencies": dependency_specs or [],
        "simplices": simplex_specs or [],
        **(config or {}),
    }
    paths = prepare_output_dir(output_dir, config_used)
    mln = build_multilayer_from_specs(layer_specs, dependency_specs, simplex_specs, seed)
    mln.export(paths["data"])
    summary = mln.summary()
    write_summary(output_dir, summary)
    return mln
