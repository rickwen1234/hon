"""Experiment helper for building HON networks."""

from __future__ import annotations

import os
from dataclasses import dataclass

from network_science_project.hon._legacy import ensure_pyhon_path
from network_science_project.utils.experiment import prepare_output_dir, write_summary

ensure_pyhon_path()

import main as pyhon_main  # noqa: E402


@dataclass
class BuildHonConfig:
    input: str
    output_network: str
    output_rules: str
    max_order: int = 5
    min_support: float = 1.0
    input_format: str = "auto"


def run(config: BuildHonConfig) -> None:
    """Build a HON network from a config object."""
    os.makedirs(os.path.dirname(config.output_network) or ".", exist_ok=True)
    rules, _ = pyhon_main.BuildHON(
        config.input,
        config.output_network,
        max_order=config.max_order,
        min_support=config.min_support,
        input_format=config.input_format,
    )
    pyhon_main.DumpRules(rules, config.output_rules)


def run_hon_experiment(
    input_path: str,
    output_dir: str,
    max_order: int = 5,
    min_support: float = 1.0,
    input_format: str = "auto",
) -> dict:
    """Build a HON network using the standard experiment output layout."""
    paths = prepare_output_dir(output_dir, {
        "input": input_path,
        "max_order": max_order,
        "min_support": min_support,
        "input_format": input_format,
    })
    output_network = os.path.join(paths["data"], "hon_edges.csv")
    output_rules = os.path.join(paths["data"], "hon_rules.csv")
    run(BuildHonConfig(input_path, output_network, output_rules, max_order, min_support, input_format))
    summary = {"output_network": output_network, "output_rules": output_rules}
    write_summary(output_dir, summary)
    return summary
