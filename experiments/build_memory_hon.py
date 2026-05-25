"""Build FON, original HON, Decay-HON, and Cog-HON on one dataset."""

from __future__ import division

import argparse
from collections import defaultdict
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PYHON_DIR = os.path.join(REPO_ROOT, "pyHON")
if PYHON_DIR not in sys.path:
    sys.path.insert(0, PYHON_DIR)

import BuildRulesFastParameterFree
import main as pyhon_main


def parse_args():
    parser = argparse.ArgumentParser(description="Compare memory-weighted HON construction modes.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--max-order", type=int, default=5)
    parser.add_argument("--min-support", type=float, default=1)
    parser.add_argument("--weighting-mode", default="all",
                        choices=["all", "none", "decay", "cogsnet"])
    parser.add_argument("--decay-mode", default="exp", choices=["none", "exp", "power", "linear"])
    parser.add_argument("--lambda", dest="lambda_", type=float, default=0.0)
    parser.add_argument("--mu", type=float, default=0.5)
    parser.add_argument("--theta", type=float, default=0.0)
    parser.add_argument("--analysis-time", default=None)
    parser.add_argument("--input-format", default="auto",
                        choices=["auto", "legacy", "timestamped_path", "csv_events", "csv", "events"])
    return parser.parse_args()


def selected_modes(requested):
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


def summarize_rules(rules):
    counts = defaultdict(int)
    weighted = defaultdict(float)
    for source in rules:
        order = len(source)
        counts[order] += len(rules[source])
        for target in rules[source]:
            metadata = BuildRulesFastParameterFree.RuleMetadata.get((source, target), {})
            weighted[order] += metadata.get("weighted_support", 0.0)
    avg_weighted = {}
    for order in counts:
        avg_weighted[order] = weighted[order] / counts[order] if counts[order] else 0.0
    return counts, avg_weighted


def edge_distribution(network):
    weights = []
    for source in network:
        for target in network[source]:
            weights.append(float(network[source][target]))
    if not weights:
        return {"min": 0.0, "max": 0.0, "mean": 0.0}
    return {
        "min": min(weights),
        "max": max(weights),
        "mean": sum(weights) / len(weights),
    }


def run_mode(args, name, max_order, weighting_mode):
    output_network = os.path.join(args.output_dir, name + "_network.csv")
    diagnostics = os.path.join(args.output_dir, name + "_weighted_rules.csv")
    rules, network = pyhon_main.BuildHON(
        args.input,
        output_network,
        max_order=max_order or args.max_order,
        min_support=args.min_support,
        weighting_mode=weighting_mode,
        decay_mode=args.decay_mode,
        lambda_=args.lambda_,
        mu=args.mu,
        theta=args.theta,
        analysis_time=args.analysis_time,
        input_format=args.input_format,
        support_type="raw",
        debug_weighted_rules=(weighting_mode != "none"),
        diagnostics_file=diagnostics if weighting_mode != "none" else None,
        edge_weight_type="probability",
    )
    rule_counts, avg_weighted = summarize_rules(rules)
    return {
        "name": name,
        "nodes": len(network),
        "edges": sum(len(network[source]) for source in network),
        "rules_by_order": dict(rule_counts),
        "avg_weighted_support_by_order": avg_weighted,
        "edge_weights": edge_distribution(network),
        "output_network": output_network,
    }


def main():
    args = parse_args()
    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir)
    for name, max_order, weighting_mode in selected_modes(args.weighting_mode):
        summary = run_mode(args, name, max_order, weighting_mode)
        print(summary["name"])
        print("  nodes: {0}".format(summary["nodes"]))
        print("  edges: {0}".format(summary["edges"]))
        print("  rules_by_order: {0}".format(summary["rules_by_order"]))
        print("  avg_weighted_support_by_order: {0}".format(summary["avg_weighted_support_by_order"]))
        print("  edge_weights: {0}".format(summary["edge_weights"]))
        print("  output_network: {0}".format(summary["output_network"]))


if __name__ == "__main__":
    main()
