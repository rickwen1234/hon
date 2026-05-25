"""Utility helpers for multilayer network construction."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict


HON_LABEL_RE = re.compile(r"^[^|,\s]+(?:\|[^|,\s]+(?:[,.][^|,\s]+)*)?$")


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def json_default(value: Any) -> Any:
    try:
        import numpy as np

        if isinstance(value, (np.integer,)):
            return int(value)
        if isinstance(value, (np.floating,)):
            return float(value)
    except Exception:
        pass
    if isinstance(value, set):
        return sorted(value)
    return str(value)


def write_json(path: str, payload: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True, default=json_default)


def read_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def parse_kv_string(text: str) -> Dict[str, Any]:
    values: Dict[str, Any] = {}
    if not text:
        return values
    for part in text.split(","):
        if not part:
            continue
        key, _, raw = part.partition("=")
        raw = raw.strip()
        if raw.lower() in {"true", "false"}:
            value: Any = parse_bool(raw)
        else:
            try:
                value = int(raw)
            except ValueError:
                try:
                    value = float(raw)
                except ValueError:
                    value = raw
        values[key.strip()] = value
    return values


def is_hon_label(node: Any) -> bool:
    return isinstance(node, str) and bool(HON_LABEL_RE.match(node))


def normalize_triangle(nodes: tuple[Any, Any, Any]) -> tuple[Any, Any, Any]:
    return tuple(sorted(nodes, key=lambda item: str(item)))  # type: ignore[return-value]
