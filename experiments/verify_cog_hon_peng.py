"""Verification harness for Cog-HON extraction and Peng-style cascades.

The script is intentionally self-contained and synthetic. It validates that the
optional Cog-HON path changes weighted supports/probabilities, then runs a small
two-layer cascade with same-layer triangle propagation and cross-layer
dependencies.
"""

from __future__ import annotations

import csv
import json
import os
import random
import sys
from typing import Dict, Iterable, List, Sequence, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PYHON = os.path.join(ROOT, "pyHON")
if PYHON not in sys.path:
    sys.path.insert(0, PYHON)

import BuildNetwork
import BuildRulesFastParameterFree as Rules


OUTPUT_DIR = os.path.join(ROOT, "outputs")
REPORT_PATH = os.path.join(OUTPUT_DIR, "verification_report.md")
METRICS_PATH = os.path.join(OUTPUT_DIR, "verification_metrics.json")
CASCADE_RESULTS_PATH = os.path.join(OUTPUT_DIR, "cascade_results.csv")


LayerState = Dict[str, Set[str]]
DependencyMap = Dict[Tuple[str, str], List[Tuple[str, str]]]


def timestamped_toy_trajectory() -> List[List[object]]:
    """Return toy data where recent A->C repeats should beat old A->B."""
    return [
        ["old", ["A", "B", "A", "B"], [1.0, 2.0, 3.0, 4.0]],
        ["recent1", ["A", "C"], [90.0, 100.0]],
        ["recent2", ["A", "C"], [91.0, 101.0]],
        ["recent3", ["A", "C"], [92.0, 102.0]],
    ]


def verify_cog_hon() -> Dict[str, object]:
    trajectory = timestamped_toy_trajectory()
    raw_rules = Rules.ExtractRules(trajectory, 1, 1, weighting_mode="none")
    raw_supports = dict(Rules.Count[("A",)])

    cog_rules = Rules.ExtractRules(
        trajectory,
        1,
        1,
        weighting_mode="cogsnet",
        decay_mode="exp",
        lambda_=0.1,
        mu=0.45,
        theta=0.01,
        analysis_time=102.0,
        output_diagnostics=True,
    )
    weighted_supports = dict(Rules.WeightedCount[("A",)])
    distribution_sums = {
        "|".join(source): sum(distribution.values())
        for source, distribution in Rules.Distribution.items()
    }
    network = BuildNetwork.BuildNetwork(cog_rules)

    raw_vs_weighted_differs = any(
        abs(weighted_supports.get(target, 0.0) - float(raw_supports.get(target, 0))) > 1e-9
        for target in set(raw_supports) | set(weighted_supports)
    )
    probabilities_sum_to_one = all(abs(total - 1.0) < 1e-9 for total in distribution_sums.values())
    recent_probability_higher = cog_rules[("A",)]["C"] > cog_rules[("A",)]["B"]

    return {
        "raw_supports_A": raw_supports,
        "weighted_supports_A": weighted_supports,
        "probabilities_A": dict(cog_rules[("A",)]),
        "distribution_sums": distribution_sums,
        "network_nodes": len(network),
        "network_edges": sum(len(network[source]) for source in network),
        "raw_vs_weighted_differs": raw_vs_weighted_differs,
        "probabilities_sum_to_one": probabilities_sum_to_one,
        "recent_probability_higher": recent_probability_higher,
        "passed": raw_vs_weighted_differs and probabilities_sum_to_one and recent_probability_higher,
    }


def build_two_layer_network(triangle_density: str = "high", q: float = 1.0) -> Tuple[LayerState, DependencyMap]:
    nodes_a = {"a1", "a2", "a3", "a4"}
    nodes_b = {"b1", "b2", "b3", "b4"}
    triangles_a = {("a1", "a2", "a3")}
    triangles_b = {("b1", "b2", "b3")}
    if triangle_density == "high":
        triangles_a.add(("a2", "a3", "a4"))
        triangles_b.add(("b2", "b3", "b4"))

    layers: LayerState = {
        "A_nodes": nodes_a,
        "B_nodes": nodes_b,
        "A_triangles": set(triangles_a),
        "B_triangles": set(triangles_b),
    }

    dependency: DependencyMap = {}
    pairs = [("a1", "b1"), ("a2", "b2"), ("a3", "b3"), ("a4", "b4")]
    for node_a, node_b in pairs:
        if _include_dependency(node_a, q):
            dependency.setdefault(("A", node_a), []).append(("B", node_b))
            dependency.setdefault(("B", node_b), []).append(("A", node_a))
    return layers, dependency


def _include_dependency(node_id: str, q: float) -> bool:
    if q >= 1.0:
        return True
    if q <= 0.0:
        return False
    rank = int(node_id[-1])
    return rank <= int(round(4 * q))


def simplex_failures(triangles: Iterable[Sequence[str]], failed: Set[str]) -> Set[str]:
    new_failed: Set[str] = set()
    for triangle in triangles:
        tri = set(triangle)
        if tri & failed:
            new_failed.update(tri - failed)
    return new_failed


def dependency_failures(dependencies: DependencyMap, failed_a: Set[str], failed_b: Set[str]) -> Tuple[Set[str], Set[str]]:
    new_a: Set[str] = set()
    new_b: Set[str] = set()
    for source in [("A", node) for node in failed_a] + [("B", node) for node in failed_b]:
        for layer, node in dependencies.get(source, []):
            if layer == "A" and node not in failed_a:
                new_a.add(node)
            if layer == "B" and node not in failed_b:
                new_b.add(node)
    return new_a, new_b


def run_peng_cascade(layers: LayerState, dependencies: DependencyMap, attacked_a: Set[str]) -> Dict[str, object]:
    failed_a = set(attacked_a)
    failed_b: Set[str] = set()
    steps: List[Dict[str, object]] = [{
        "step": 0,
        "cause": "initial attack",
        "new_A": sorted(attacked_a),
        "new_B": [],
    }]

    while True:
        before_a = set(failed_a)
        before_b = set(failed_b)

        new_a = simplex_failures(layers["A_triangles"], failed_a)
        new_b = simplex_failures(layers["B_triangles"], failed_b)
        if new_a or new_b:
            failed_a.update(new_a)
            failed_b.update(new_b)
            steps.append({"step": len(steps), "cause": "same-layer simplex", "new_A": sorted(new_a), "new_B": sorted(new_b)})

        dep_a, dep_b = dependency_failures(dependencies, failed_a, failed_b)
        if dep_a or dep_b:
            failed_a.update(dep_a)
            failed_b.update(dep_b)
            steps.append({"step": len(steps), "cause": "cross-layer dependency", "new_A": sorted(dep_a), "new_B": sorted(dep_b)})

        rec_a = simplex_failures(layers["A_triangles"], failed_a)
        rec_b = simplex_failures(layers["B_triangles"], failed_b)
        if rec_a or rec_b:
            failed_a.update(rec_a)
            failed_b.update(rec_b)
            steps.append({"step": len(steps), "cause": "recursive same-layer simplex", "new_A": sorted(rec_a), "new_B": sorted(rec_b)})

        if before_a == failed_a and before_b == failed_b:
            break

    nodes_a = layers["A_nodes"]
    nodes_b = layers["B_nodes"]
    return {
        "failed_A": sorted(failed_a),
        "failed_B": sorted(failed_b),
        "S_A": (len(nodes_a) - len(failed_a)) / float(len(nodes_a)),
        "S_B": (len(nodes_b) - len(failed_b)) / float(len(nodes_b)),
        "cascade_steps": len(steps),
        "steps": steps,
        "stopped_without_new_failures": True,
    }


def verify_peng_cascade() -> Dict[str, object]:
    layers, dependencies = build_two_layer_network("high", 1.0)
    result = run_peng_cascade(layers, dependencies, {"a1"})
    causes = [step["cause"] for step in result["steps"]]
    required_causes = [
        "initial attack",
        "same-layer simplex",
        "cross-layer dependency",
        "recursive same-layer simplex",
    ]
    propagated = all(cause in causes for cause in required_causes)
    stopped = bool(result["stopped_without_new_failures"])
    return {
        "result": result,
        "causes": causes,
        "required_causes": required_causes,
        "propagated": propagated,
        "stopped": stopped,
        "passed": propagated and stopped,
    }


def parameter_sensitivity() -> Dict[str, object]:
    low_q_layers, low_q_deps = build_two_layer_network("high", 0.2)
    high_q_layers, high_q_deps = build_two_layer_network("high", 1.0)
    low_q = run_peng_cascade(low_q_layers, low_q_deps, {"a1"})
    high_q = run_peng_cascade(high_q_layers, high_q_deps, {"a1"})

    low_density_layers, low_density_deps = build_two_layer_network("low", 1.0)
    high_density_layers, high_density_deps = build_two_layer_network("high", 1.0)
    low_density = run_peng_cascade(low_density_layers, low_density_deps, {"a1"})
    high_density = run_peng_cascade(high_density_layers, high_density_deps, {"a1"})

    low_q_failed = len(low_q["failed_A"]) + len(low_q["failed_B"])
    high_q_failed = len(high_q["failed_A"]) + len(high_q["failed_B"])
    low_density_failed = len(low_density["failed_A"]) + len(low_density["failed_B"])
    high_density_failed = len(high_density["failed_A"]) + len(high_density["failed_B"])

    return {
        "q_0_2_failed": low_q_failed,
        "q_1_0_failed": high_q_failed,
        "low_triangle_density_failed": low_density_failed,
        "high_triangle_density_failed": high_density_failed,
        "higher_q_monotonic": high_q_failed >= low_q_failed,
        "higher_triangle_density_monotonic": high_density_failed >= low_density_failed,
        "passed": high_q_failed >= low_q_failed and high_density_failed >= low_density_failed,
    }


def write_cascade_results(rows: List[Dict[str, object]]) -> None:
    fields = [
        "model_name",
        "trial_id",
        "removal_fraction",
        "S_A",
        "S_B",
        "failed_A",
        "failed_B",
        "cascade_steps",
        "q",
        "lambda",
        "mu",
        "theta",
    ]
    with open(CASCADE_RESULTS_PATH, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def generate_cascade_rows() -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for trial_id, q in enumerate([0.2, 1.0]):
        layers, dependencies = build_two_layer_network("high", q)
        result = run_peng_cascade(layers, dependencies, {"a1"})
        rows.append({
            "model_name": "PengToy",
            "trial_id": trial_id,
            "removal_fraction": 0.25,
            "S_A": result["S_A"],
            "S_B": result["S_B"],
            "failed_A": len(result["failed_A"]),
            "failed_B": len(result["failed_B"]),
            "cascade_steps": result["cascade_steps"],
            "q": q,
            "lambda": 0.1,
            "mu": 0.45,
            "theta": 0.01,
        })
    return rows


def validate_cascade_csv() -> Dict[str, object]:
    required = [
        "model_name",
        "trial_id",
        "removal_fraction",
        "S_A",
        "S_B",
        "failed_A",
        "failed_B",
        "cascade_steps",
        "q",
        "lambda",
        "mu",
        "theta",
    ]
    with open(CASCADE_RESULTS_PATH, newline="") as handle:
        reader = csv.DictReader(handle)
        present = reader.fieldnames or []
    missing = [field for field in required if field not in present]
    return {"required_columns": required, "present_columns": present, "missing_columns": missing, "passed": not missing}


def classify(cog: Dict[str, object], peng: Dict[str, object]) -> str:
    cog_ok = bool(cog["passed"])
    peng_ok = bool(peng["passed"])
    if cog_ok and peng_ok:
        return "PASS: Cog-HON + Peng cascade implemented"
    if cog_ok:
        return "PARTIAL: Cog-HON implemented but Peng cascade incomplete"
    if peng_ok:
        return "PARTIAL: Peng cascade implemented but Cog-HON incomplete"
    return "FAIL: only basic robustness simulation implemented"


def write_report(metrics: Dict[str, object]) -> None:
    lines = [
        "# Verification Report",
        "",
        "## Classification",
        "",
        metrics["classification"],
        "",
        "## Cog-HON Rule Extraction",
        "",
        "- Weighted supports differ from raw supports: `{}`".format(metrics["cog_hon"]["raw_vs_weighted_differs"]),
        "- Weighted transition probabilities sum to 1: `{}`".format(metrics["cog_hon"]["probabilities_sum_to_one"]),
        "- Recent repeated paths receive higher probability: `{}`".format(metrics["cog_hon"]["recent_probability_higher"]),
        "",
        "## Peng-Style Cascade",
        "",
        "- Required propagation causes observed: `{}`".format(metrics["peng_cascade"]["propagated"]),
        "- Cascade stopped after fixed point: `{}`".format(metrics["peng_cascade"]["stopped"]),
        "- Causes: `{}`".format(metrics["peng_cascade"]["causes"]),
        "",
        "## Parameter Sensitivity",
        "",
        "- q=0.2 failed nodes: `{}`".format(metrics["parameter_sensitivity"]["q_0_2_failed"]),
        "- q=1.0 failed nodes: `{}`".format(metrics["parameter_sensitivity"]["q_1_0_failed"]),
        "- Low triangle density failed nodes: `{}`".format(metrics["parameter_sensitivity"]["low_triangle_density_failed"]),
        "- High triangle density failed nodes: `{}`".format(metrics["parameter_sensitivity"]["high_triangle_density_failed"]),
        "",
        "## Output Validation",
        "",
        "- cascade_results.csv columns valid: `{}`".format(metrics["output_validation"]["passed"]),
    ]
    with open(REPORT_PATH, "w") as handle:
        handle.write("\n".join(lines) + "\n")


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cog = verify_cog_hon()
    peng = verify_peng_cascade()
    sensitivity = parameter_sensitivity()
    write_cascade_results(generate_cascade_rows())
    output_validation = validate_cascade_csv()
    classification = classify(cog, peng)

    metrics: Dict[str, object] = {
        "cog_hon": cog,
        "peng_cascade": peng,
        "parameter_sensitivity": sensitivity,
        "output_validation": output_validation,
        "classification": classification,
        "paths": {
            "verification_report": REPORT_PATH,
            "verification_metrics": METRICS_PATH,
            "cascade_results": CASCADE_RESULTS_PATH,
        },
    }
    with open(METRICS_PATH, "w") as handle:
        json.dump(metrics, handle, indent=2, sort_keys=True)
    write_report(metrics)
    print(classification)


if __name__ == "__main__":
    main()
