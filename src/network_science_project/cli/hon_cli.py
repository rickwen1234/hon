"""CLI for HON construction."""

from __future__ import annotations

import argparse

from network_science_project.experiments.build_hon import BuildHonConfig, run, run_hon_experiment
from network_science_project.utils.config import load_config


def main() -> None:
    """Parse arguments and build a HON network."""
    parser = argparse.ArgumentParser(description="Build a HON network.")
    parser.add_argument("--config", default=None)
    parser.add_argument("--input", default=None)
    parser.add_argument("--output-dir", default="outputs/build_hon")
    parser.add_argument("--output-network", default=None)
    parser.add_argument("--output-rules", default=None)
    parser.add_argument("--max-order", type=int, default=5)
    parser.add_argument("--min-support", type=float, default=1.0)
    parser.add_argument("--input-format", default="auto")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    config = load_config(args.config) if args.config else {}
    input_path = args.input or config.get("input")
    if not input_path:
        parser.error("--input is required unless provided by --config")
    if args.output_network or args.output_rules:
        output_network = args.output_network or config.get("output_network") or args.output_dir + "/data/hon_edges.csv"
        output_rules = args.output_rules or config.get("output_rules") or args.output_dir + "/data/hon_rules.csv"
        run(BuildHonConfig(input_path, output_network, output_rules, args.max_order, args.min_support, args.input_format))
    else:
        run_hon_experiment(input_path, args.output_dir, args.max_order, args.min_support, args.input_format)
