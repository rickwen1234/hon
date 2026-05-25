"""CLI for summarizing result files."""

from __future__ import annotations

import argparse
import json
import os

from network_science_project.experiments.summarize_results import summarize_cascade_results
from network_science_project.utils.config import load_config
from network_science_project.utils.experiment import prepare_output_dir, write_summary


def main() -> None:
    """Parse arguments and summarize cascade results."""
    parser = argparse.ArgumentParser(description="Summarize network-science experiment results.")
    parser.add_argument("--config", default=None)
    parser.add_argument("--input", required=False)
    parser.add_argument("--output-dir", default="outputs/summary")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    config = load_config(args.config) if args.config else {}
    input_path = args.input or config.get("input")
    if not input_path:
        parser.error("--input is required unless provided by --config")
    prepare_output_dir(args.output_dir, {"input": input_path, "seed": args.seed, **config})
    summary = summarize_cascade_results(input_path)
    write_summary(args.output_dir, summary)
    with open(os.path.join(args.output_dir, "metrics", "summary.json"), "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
    print("Wrote summary to {0}".format(args.output_dir))
