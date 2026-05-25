"""Validation helpers for multilayer networks."""

from __future__ import annotations

from typing import Any


def validate_multilayer_network(mln: Any, allow_multi_dependency: bool = False) -> list[str]:
    return mln.validate(allow_multi_dependency=allow_multi_dependency)
