"""Compatibility access to the legacy pyHON modules."""

from __future__ import annotations

import os
import sys


def ensure_pyhon_path() -> str:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    pyhon_dir = os.path.join(repo_root, "pyHON")
    if pyhon_dir not in sys.path:
        sys.path.insert(0, pyhon_dir)
    return pyhon_dir
