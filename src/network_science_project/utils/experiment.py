"""Standard experiment output-directory helpers."""

from __future__ import annotations

import json
import os
from typing import Any


STANDARD_SUBDIRS = ("logs", "data", "figures", "metrics")


def prepare_output_dir(output_dir: str, config: dict[str, Any] | None = None) -> dict[str, str]:
    """Create a standard experiment output directory and save its config."""
    os.makedirs(output_dir, exist_ok=True)
    paths = {"root": output_dir}
    for name in STANDARD_SUBDIRS:
        path = os.path.join(output_dir, name)
        os.makedirs(path, exist_ok=True)
        paths[name] = path
    with open(os.path.join(output_dir, "config_used.json"), "w", encoding="utf-8") as handle:
        json.dump(config or {}, handle, indent=2, sort_keys=True, default=str)
    return paths


def write_summary(output_dir: str, summary: dict[str, Any]) -> None:
    """Write a standard experiment summary file."""
    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True, default=str)
