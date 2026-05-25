from __future__ import annotations

import os
import sys
import tempfile
import unittest
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from network_science_project.hon.network_wiring import build_network
from network_science_project.hon.io import sequence_to_node, write_network
from network_science_project.hon.rule_extraction import extract_rules
from network_science_project.hon._legacy import ensure_pyhon_path

ensure_pyhon_path()

import BuildNetwork


class HonRuleExtractionPackageTests(unittest.TestCase):
    def test_extract_first_order_rules_through_package_api(self) -> None:
        trajectories = [["t1", ["A", "B", "A", "C"]]]
        rules = extract_rules(trajectories, max_order=1, min_support=1)
        network = build_network(rules)
        self.assertIn(("A",), network)
        BuildNetwork.Graph = defaultdict(dict)

    def test_high_order_node_label_appears_for_path_dependent_data(self) -> None:
        trajectories = []
        for index in range(20):
            trajectories.append(["a{0}".format(index), ["A", "B", "C", "X"]])
            trajectories.append(["d{0}".format(index), ["D", "B", "C", "Y"]])
        rules = extract_rules(trajectories, max_order=3, min_support=1)
        network = build_network(rules)
        labels = set()
        for source in network:
            labels.add(sequence_to_node(source))
            for target in network[source]:
                labels.add(sequence_to_node(target))
        self.assertIn("B|A", labels)
        self.assertIn("C|B.A", labels)
        BuildNetwork.Graph = defaultdict(dict)


if __name__ == "__main__":
    unittest.main()
