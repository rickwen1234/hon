"""Cascade-result plotting functions."""

from __future__ import annotations

from ._legacy import ensure_legacy_multilayer_path

ensure_legacy_multilayer_path()

from multilayer.visualization import plot_cascade_results  # noqa: E402

__all__ = ["plot_cascade_results"]
