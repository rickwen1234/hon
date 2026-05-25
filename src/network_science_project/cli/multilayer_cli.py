"""CLI for multilayer construction."""

from __future__ import annotations

import argparse

from network_science_project.experiments.build_multilayer import run_multilayer_experiment
from network_science_project.utils.config import load_config


def main() -> None:
    """Parse arguments and build a multilayer network."""
    parser = argparse.ArgumentParser(description="Build a multilayer network.")
    parser.add_argument("--config", default=None)
    parser.add_argument("--output-dir", default="outputs/demo_multilayer")
    parser.add_argument("--layer", action="append", default=[])
    parser.add_argument("--dependency", action="append", default=[])
    parser.add_argument("--simplices", action="append", default=[])
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    config = load_config(args.config) if args.config else {}
    layer_specs = args.layer or [
        "A:generated:poisson:n=100,mean_degree=8",
        "B:generated:scale_free:n=100,gamma=2.5,mean_degree=8",
    ]
    dependency_specs = args.dependency or ["A:B:random_matching:q=0.8"]
    simplex_specs = args.simplices or [
        "A:poisson_triangles:mean_triangle_degree=0.4",
        "B:poisson_triangles:mean_triangle_degree=0.4",
    ]
    run_multilayer_experiment(args.output_dir, layer_specs, dependency_specs, simplex_specs, args.seed, config)
    print("Wrote multilayer network to {0}".format(args.output_dir))
