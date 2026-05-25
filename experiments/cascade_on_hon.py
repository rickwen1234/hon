"""Random physical-node removal on projected HON edge files.

This is a lightweight robustness simulation layer. It reads one or more HON
edge CSV files, projects higher-order node labels back to physical node IDs,
and tracks the largest connected component after random removals.
"""

from __future__ import annotations

import argparse
import csv
import os
import random
from collections import deque
from typing import Deque, Dict, Iterable, List, Set, Tuple


Graph = Dict[str, Set[str]]


def physical_node(label: str) -> str:
    """Recover the physical node ID from a HON node label."""
    return label.split("|", 1)[0]


def read_projected_graph(path: str) -> Graph:
    """Read HON edge CSV and return an undirected physical projection."""
    graph: Graph = {}
    with open(path, newline="") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if len(row) < 2:
                continue
            source = physical_node(row[0].strip())
            target = physical_node(row[1].strip())
            if not source or not target:
                continue
            graph.setdefault(source, set()).add(target)
            graph.setdefault(target, set()).add(source)
    return graph


def largest_component_size(graph: Graph, removed: Set[str]) -> int:
    """Return largest connected component size after removing nodes."""
    visited: Set[str] = set()
    best = 0
    for start in graph:
        if start in removed or start in visited:
            continue
        size = 0
        queue: Deque[str] = deque([start])
        visited.add(start)
        while queue:
            node = queue.popleft()
            size += 1
            for neighbor in graph.get(node, set()):
                if neighbor in removed or neighbor in visited:
                    continue
                visited.add(neighbor)
                queue.append(neighbor)
        best = max(best, size)
    return best


def removal_fractions(steps: int) -> List[float]:
    if steps <= 0:
        return [0.0, 1.0]
    return [index / float(steps) for index in range(steps + 1)]


def simulate(graph: Graph, model_name: str, trials: int, steps: int, seed: int) -> List[dict]:
    nodes = sorted(graph.keys())
    total = float(len(nodes))
    rng = random.Random(seed)
    rows: List[dict] = []
    for trial_id in range(trials):
        order = nodes[:]
        rng.shuffle(order)
        for fraction in removal_fractions(steps):
            remove_count = int(round(fraction * len(nodes)))
            removed = set(order[:remove_count])
            giant = largest_component_size(graph, removed)
            ratio = 0.0 if total == 0 else giant / total
            rows.append({
                "removal_fraction": fraction,
                "remaining_giant_component_ratio": ratio,
                "model_name": model_name,
                "trial_id": trial_id,
            })
    return rows


def parse_model_arg(value: str) -> Tuple[str, str]:
    if "=" in value:
        name, path = value.split("=", 1)
        return name, path
    name = os.path.splitext(os.path.basename(value))[0]
    return name, value


def write_results(rows: Iterable[dict], path: str) -> None:
    fields = [
        "removal_fraction",
        "remaining_giant_component_ratio",
        "model_name",
        "trial_id",
    ]
    with open(path, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run random removal cascades on projected HON outputs.")
    parser.add_argument(
        "--model",
        action="append",
        required=True,
        help="Model edge file, either path.csv or name=path.csv. Repeat for FON/HON/Decay-HON/Cog-HON.",
    )
    parser.add_argument("--output", required=True)
    parser.add_argument("--trials", type=int, default=20)
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--seed", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    all_rows: List[dict] = []
    for model_index, model in enumerate(args.model):
        model_name, path = parse_model_arg(model)
        graph = read_projected_graph(path)
        all_rows.extend(simulate(graph, model_name, args.trials, args.steps, args.seed + model_index))
    write_results(all_rows, args.output)


if __name__ == "__main__":
    main()
