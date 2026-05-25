"""CLI for full demo pipeline."""

from __future__ import annotations

import argparse

from network_science_project.experiments.run_full_pipeline import run
from network_science_project.utils.config import load_config


def main() -> None:
    """Parse arguments and run the full demo pipeline."""
    parser = argparse.ArgumentParser(description="Run the full demo pipeline.")
    parser.add_argument("--config", default=None)
    parser.add_argument("--output-dir", default="outputs/full_pipeline_demo")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    config = load_config(args.config) if args.config else {}
    run(args.output_dir, args.seed, config)
    print("Wrote full pipeline outputs to {0}".format(args.output_dir))
