"""Compatibility access to the legacy multilayer visualization implementation."""

from __future__ import annotations

import os
import sys


def ensure_legacy_multilayer_path() -> None:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
