from __future__ import annotations

import math
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from network_science_project.hon.temporal_weighting import decay_weight
from network_science_project.hon.rule_extraction import extract_rules, latest_rule_metadata


class TemporalWeightingPackageTests(unittest.TestCase):
    def test_decay_weight_reexport(self) -> None:
        self.assertAlmostEqual(decay_weight(2, "exp", 0.5), math.exp(-1.0))

    def test_cog_hon_weighted_support_differs_from_raw(self) -> None:
        trajectories = [["t1", ["A", "B", "A", "C"], [1.0, 2.0, 9.0, 10.0]]]
        extract_rules(
            trajectories,
            max_order=1,
            min_support=1,
            weighting_mode="decay",
            decay_mode="exp",
            lambda_=0.5,
            analysis_time=10.0,
            output_diagnostics=True,
        )
        metadata = latest_rule_metadata()
        self.assertLess(metadata[(("A",), "B")]["weighted_support"], metadata[(("A",), "B")]["raw_support"])
        self.assertGreater(metadata[(("A",), "C")]["weighted_support"], metadata[(("A",), "B")]["weighted_support"])


if __name__ == "__main__":
    unittest.main()
