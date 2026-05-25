"""HON edge-list and rule-list IO helpers."""

from __future__ import annotations

import csv
from typing import Any


def sequence_to_node(seq: tuple[str, ...]) -> str:
    curr = seq[-1]
    previous = list(seq[:-1])
    if not previous:
        return curr + "|"
    return curr + "|" + ".".join(reversed(previous))


def write_rules(rules: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        for source in rules:
            for target in rules[source]:
                handle.write(" ".join([" ".join(str(x) for x in source), "=>", str(target), str(rules[source][target])]) + "\n")


def write_network(network: dict, path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        for source in network:
            for target in network[source]:
                writer.writerow([sequence_to_node(source), sequence_to_node(target), network[source][target]])


def read_hon_edges(path: str) -> list[tuple[str, str, float]]:
    edges: list[tuple[str, str, float]] = []
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.reader(handle):
            if len(row) >= 2:
                weight = float(row[2]) if len(row) > 2 and row[2] else 1.0
                edges.append((row[0], row[1], weight))
    return edges
