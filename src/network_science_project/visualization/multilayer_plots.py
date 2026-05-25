"""Multilayer visualization functions."""

from __future__ import annotations

from ._legacy import ensure_legacy_multilayer_path

ensure_legacy_multilayer_path()

from multilayer.visualization import (  # noqa: E402
    export_interactive_html,
    plot_dependency_matrix,
    plot_multilayer_2d,
    plot_multilayer_3d,
)

__all__ = ["export_interactive_html", "plot_dependency_matrix", "plot_multilayer_2d", "plot_multilayer_3d"]
