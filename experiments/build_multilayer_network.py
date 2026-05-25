"""Build and export a multilayer network."""

from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from multilayer import GeneratorSpec, MultiLayerNetwork
from multilayer.io import load_edge_list, load_hon_edge_list
from multilayer.utils import parse_bool, parse_kv_string


def _parse_layer(text: str, default_seed: int | None) -> tuple[str, str, dict]:
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


def _parse_dependency(text: str, default_seed: int | None) -> tuple[str, str, str, dict]:
    parts = text.split(":", 3)
    if len(parts) < 3:
        raise ValueError("Malformed dependency spec: {0}".format(text))
    tail = parts[3] if len(parts) > 3 else ""
    params = {"path": tail} if parts[2] == "from_file" and tail and "=" not in tail else parse_kv_string(tail)
    params.setdefault("seed", default_seed)
    return parts[0], parts[1], parts[2], params


def _parse_simplex(text: str, default_seed: int | None) -> tuple[str, str, dict]:
    parts = text.split(":", 2)
    if len(parts) < 2:
        raise ValueError("Malformed simplex spec: {0}".format(text))
    tail = parts[2] if len(parts) > 2 else ""
    params = {"path": tail} if parts[1] == "from_file" and tail and "=" not in tail else parse_kv_string(tail)
    params.setdefault("seed", default_seed)
    return parts[0], parts[1], params


def build_from_args(args: argparse.Namespace) -> MultiLayerNetwork:
    mln = MultiLayerNetwork(metadata={"created_by": "experiments/build_multilayer_network.py"})
    for layer_text in args.layer:
        name, kind, params = _parse_layer(layer_text, args.seed)
        if kind == "generated":
            spec = GeneratorSpec(
                model=params["model"],
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
            mln.add_layer(name, graph=load_edge_list(params["path"], directed=directed), graph_type="directed" if directed else "undirected", source="loaded", metadata={"path": params["path"]})
        elif kind == "hon_edge_list":
            directed = parse_bool(str(params.get("directed", "true")))
            mln.add_layer(name, graph=load_hon_edge_list(params["path"], directed=directed), graph_type="directed" if directed else "undirected", source="hon", metadata={"path": params["path"]})
        else:
            raise ValueError("Unknown layer kind: {0}".format(kind))
    for dep_text in args.dependency:
        a, b, mode, params = _parse_dependency(dep_text, args.seed)
        q = float(params.pop("q", 1.0))
        bidirectional = parse_bool(str(params.pop("bidirectional", "true")))
        mln.add_dependency(a, b, mode=mode, q=q, bidirectional=bidirectional, **params)
    for simplex_text in args.simplices:
        layer, mode, params = _parse_simplex(simplex_text, args.seed)
        mln.add_simplices(layer, mode=mode, **params)
    errors = mln.validate()
    if errors:
        raise ValueError("Validation failed:\n" + "\n".join(errors[:20]))
    return mln


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a generated or loaded multilayer network.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--layer", action="append", default=[], required=True)
    parser.add_argument("--dependency", action="append", default=[])
    parser.add_argument("--simplices", action="append", default=[])
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()
    mln = build_from_args(args)
    mln.export(args.output_dir)
    print("Exported multilayer network to {0}".format(args.output_dir))


if __name__ == "__main__":
    main()
