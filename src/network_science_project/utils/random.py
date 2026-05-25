"""Randomness helpers."""

from __future__ import annotations

import random
from typing import Optional


def make_rng(seed: Optional[int] = None) -> random.Random:
    return random.Random(seed)
