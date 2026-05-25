"""Deprecated wrapper for ns-run-peng-cascade."""

from __future__ import annotations

import os
import sys
import warnings

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from network_science_project.cli.cascade_cli import main


if __name__ == "__main__":
    warnings.warn("scripts/run_peng_cascade.py is deprecated; use ns-run-peng-cascade.", DeprecationWarning)
    main()
