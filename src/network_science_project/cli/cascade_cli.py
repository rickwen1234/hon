"""CLI for Peng-style cascade simulation."""

from __future__ import annotations

import argparse

from network_science_project.experiments.run_peng_cascade import run_peng_cascade_experiment
from network_science_project.utils.config import load_config


def main() -> None:
    """Parse arguments and run Peng-style cascade trials."""
    parser = argparse.ArgumentParser(description="Run a Peng-style cascade from prepared inputs.")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--layer-a", default="A")
    parser.add_argument("--layer-b", default="B")
    parser.add_argument("--config", default=None)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--trials", type=int, default=1)
    parser.add_argument("--removal-fraction", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()
    config = load_config(args.config) if args.config else {}
    run_peng_cascade_experiment(
        args.input_dir,
        args.output_dir,
        args.layer_a,
        args.layer_b,
        args.trials,
        args.removal_fraction,
        args.seed,
        config,
    )
    print("Wrote cascade outputs to {0}".format(args.output_dir))
