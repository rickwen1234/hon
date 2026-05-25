"""Sequential-data parsers for HON construction."""

from __future__ import annotations

from ._legacy import ensure_pyhon_path

ensure_pyhon_path()

from input_parser import read_sequential_data  # noqa: E402

__all__ = ["read_sequential_data"]
