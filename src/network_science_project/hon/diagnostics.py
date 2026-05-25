"""Diagnostic output helpers for weighted HON rules."""

from __future__ import annotations

import csv


RULE_DIAGNOSTIC_FIELDS = [
    "order",
    "source_path",
    "target",
    "probability",
    "raw_support",
    "weighted_support",
    "base_weighted_support",
    "kl_divergence",
    "threshold",
    "first_timestamp",
    "last_timestamp",
    "weighting_mode",
]


def write_rule_diagnostics(rows: list[dict], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RULE_DIAGNOSTIC_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
