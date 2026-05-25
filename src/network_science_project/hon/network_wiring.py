"""HON network wiring API."""

from __future__ import annotations

from ._legacy import ensure_pyhon_path

ensure_pyhon_path()

import BuildNetwork as _network  # noqa: E402


def build_network(rules, edge_weight_type: str = "probability", rule_metadata=None):
    return _network.BuildNetwork(rules, edge_weight_type=edge_weight_type, rule_metadata=rule_metadata)
