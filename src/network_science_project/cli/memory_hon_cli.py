"""CLI for memory-weighted HON experiments."""

from __future__ import annotations

import argparse

from network_science_project.experiments.build_memory_hon import run_memory_hon_experiment
from network_science_project.utils.config import load_config


def main() -> None:
    """Parse arguments and run memory-HON model construction."""
    parser = argparse.ArgumentParser(description="Build FON, HON, Decay-HON, and Cog-HON variants.")
    parser.add_argument("--config", default=None)
    parser.add_argument("--input", default=None)
    parser.add_argument("--output-dir", default="outputs/memory_hon")
    parser.add_argument("--max-order", type=int, default=5)
    parser.add_argument("--min-support", type=float, default=1.0)
    parser.add_argument("--weighting-mode", default="all", choices=["all", "none", "decay", "cogsnet"])
    parser.add_argument("--decay-mode", default="exp", choices=["none", "exp", "power", "linear"])
    parser.add_argument("--lambda", dest="lambda_", type=float, default=0.0)
    parser.add_argument("--mu", type=float, default=0.5)
    parser.add_argument("--theta", type=float, default=0.0)
    parser.add_argument("--analysis-time", default=None)
    parser.add_argument("--input-format", default="auto")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    config = load_config(args.config) if args.config else {}
    input_path = args.input or config.get("input")
    if not input_path:
        parser.error("--input is required unless provided by --config")
    run_memory_hon_experiment(
        input_path,
        args.output_dir,
        args.max_order,
        args.min_support,
        args.weighting_mode,
        args.decay_mode,
        args.lambda_,
        args.mu,
        args.theta,
        args.analysis_time,
        args.input_format,
        args.seed,
        config,
    )
    print("Wrote memory-HON outputs to {0}".format(args.output_dir))
