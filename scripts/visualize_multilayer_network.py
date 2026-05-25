"""Deprecated wrapper for ns-visualize-multilayer."""

from __future__ import annotations

import os
import sys
import warnings

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from network_science_project.cli.visualization_cli import main


if __name__ == "__main__":
    warnings.warn("scripts/visualize_multilayer_network.py is deprecated; use ns-visualize-multilayer.", DeprecationWarning)
    main()
