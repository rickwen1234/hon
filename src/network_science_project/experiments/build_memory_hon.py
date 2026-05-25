"""Experiment helpers for memory-weighted HON comparison."""

from __future__ import annotations

import os
from collections import defaultdict
from typing import Any

from network_science_project.hon._legacy import ensure_pyhon_path
from network_science_project.utils.experiment import prepare_output_dir, write_summary

ensure_pyhon_path()

import BuildRulesFastParameterFree  # noqa: E402
import main as pyhon_main  # noqa: E402


def selected_modes(requested: str) -> list[tuple[str, int | None, str]]:
    """Return memory-HON modes requested by a CLI/config value."""
    modes = [
        ("fon", 1, "none"),
        ("original_hon", None, "none"),
        ("decay_hon", None, "decay"),
        ("cog_hon", None, "cogsnet"),
    ]
    if requested == "all":
        return modes
    if requested == "none":
        return modes[:2]
    return [mode for mode in modes if mode[2] == requested]


def summarize_rules(rules: dict) -> tuple[dict[int, int], dict[int, float]]:
    """Summarize rule counts and weighted support by order."""
    counts: dict[int, int] = defaultdict(int)
    weighted: dict[int, float] = defaultdict(float)
    for source in rules:
        order = len(source)
        counts[order] += len(rules[source])
        for target in rules[source]:
            metadata = BuildRulesFastParameterFree.RuleMetadata.get((source, target), {})
            weighted[order] += metadata.get("weighted_support", 0.0)
    return dict(counts), {order: weighted[order] / counts[order] for order in counts if counts[order]}


def run_memory_hon_experiment(
    input_path: str,
    output_dir: str,
    max_order: int = 5,
    min_support: float = 1.0,
    weighting_mode: str = "all",
    decay_mode: str = "exp",
    lambda_: float = 0.0,
    mu: float = 0.5,
    theta: float = 0.0,
    analysis_time: Any = None,
    input_format: str = "auto",
    seed: int | None = None,
    config: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Build FON, HON, Decay-HON, and Cog-HON variants with standard outputs."""
    config_used = {
        "input": input_path,
        "max_order": max_order,
        "min_support": min_support,
        "weighting_mode": weighting_mode,
        "decay_mode": decay_mode,
        "lambda": lambda_,
        "mu": mu,
        "theta": theta,
        "analysis_time": analysis_time,
        "input_format": input_format,
        "seed": seed,
        **(config or {}),
    }
    paths = prepare_output_dir(output_dir, config_used)
    summaries: list[dict[str, Any]] = []
    for name, mode_max_order, mode_weighting in selected_modes(weighting_mode):
        output_network = os.path.join(paths["data"], name + "_network.csv")
        diagnostics = os.path.join(paths["metrics"], name + "_weighted_rules.csv")
        rules, network = pyhon_main.BuildHON(
            input_path,
            output_network,
            max_order=mode_max_order or max_order,
            min_support=min_support,
            weighting_mode=mode_weighting,
            decay_mode=decay_mode,
            lambda_=lambda_,
            mu=mu,
            theta=theta,
            analysis_time=analysis_time,
            input_format=input_format,
            support_type="raw",
            debug_weighted_rules=(mode_weighting != "none"),
            diagnostics_file=diagnostics if mode_weighting != "none" else None,
            edge_weight_type="probability",
        )
        rule_counts, avg_weighted = summarize_rules(rules)
        summaries.append({
            "name": name,
            "nodes": len(network),
            "edges": sum(len(network[source]) for source in network),
            "rules_by_order": rule_counts,
            "avg_weighted_support_by_order": avg_weighted,
            "output_network": output_network,
        })
    write_summary(output_dir, {"models": summaries})
    return summaries
