"""Result summary helpers."""

from __future__ import annotations

import csv


def summarize_cascade_results(path: str) -> dict[str, float]:
    """Summarize the final cascade giant-component ratios."""
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return {"final_giant_A": 0.0, "final_giant_B": 0.0}
    final = rows[-1]
    value_a = final.get("S_A", final.get("giant_A", 0.0))
    value_b = final.get("S_B", final.get("giant_B", 0.0))
    return {"final_giant_A": float(value_a), "final_giant_B": float(value_b)}
