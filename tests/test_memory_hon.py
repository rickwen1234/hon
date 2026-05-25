"""Lightweight validation tests for memory-weighted HON."""

from __future__ import annotations

import math
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PYHON = os.path.join(ROOT, "pyHON")
if PYHON not in sys.path:
    sys.path.insert(0, PYHON)

import BuildNetwork
import BuildRulesFastParameterFree as Rules
from temporal_weighting import cogsnet_update, decay_weight


class TemporalWeightingTests(unittest.TestCase):
    def test_decay_weight_modes(self) -> None:
        self.assertEqual(decay_weight(10, "none", 0.5), 1.0)
        self.assertAlmostEqual(decay_weight(2, "exp", 0.5), math.exp(-1.0))
        self.assertAlmostEqual(decay_weight(4, "power", 0.5), 0.5)
        self.assertAlmostEqual(decay_weight(2, "linear", 0.25), 0.5)

    def test_cogsnet_reinforces_and_forgets(self) -> None:
        first = cogsnet_update(0.0, None, 0.4, 0.0, 0.1, "exp")
        second = cogsnet_update(first, 1.0, 0.4, 0.0, 0.1, "exp")
        after_gap = cogsnet_update(second, 100.0, 0.4, 0.0, 0.1, "exp")
        self.assertGreater(second, first)
        self.assertLess(after_gap, second)


class MemoryHonRuleTests(unittest.TestCase):
    def test_weighting_none_matches_expected_first_order_counts(self) -> None:
        trajectory = [
            ["t1", ["A", "B", "A", "C"]],
            ["t2", ["A", "B", "C"]],
        ]
        rules = Rules.ExtractRules(trajectory, 1, 1, weighting_mode="none")
        self.assertEqual(Rules.Count[("A",)]["B"], 2)
        self.assertEqual(Rules.Count[("A",)]["C"], 1)
        self.assertAlmostEqual(rules[("A",)]["B"], 2.0 / 3.0)
        self.assertAlmostEqual(rules[("A",)]["C"], 1.0 / 3.0)

    def test_recent_events_have_larger_exponential_decay_weight(self) -> None:
        trajectory = [["t1", ["A", "B", "A", "C"], [1.0, 2.0, 9.0, 10.0]]]
        Rules.ExtractRules(
            trajectory,
            1,
            1,
            weighting_mode="decay",
            decay_mode="exp",
            lambda_=0.5,
            analysis_time=10.0,
        )
        self.assertLess(Rules.WeightedCount[("A",)]["B"], Rules.WeightedCount[("A",)]["C"])

    def test_weighted_transition_probabilities_sum_to_one(self) -> None:
        trajectory = [
            ["t1", ["A", "B", "A", "C"], [1.0, 2.0, 9.0, 10.0]],
            ["t2", ["B", "A", "D"], [3.0, 4.0, 11.0]],
        ]
        Rules.ExtractRules(
            trajectory,
            2,
            1,
            weighting_mode="decay",
            decay_mode="exp",
            lambda_=0.1,
            analysis_time=11.0,
        )
        for source, distribution in Rules.Distribution.items():
            self.assertAlmostEqual(sum(distribution.values()), 1.0)

    def test_max_order_one_builds_first_order_network(self) -> None:
        trajectory = [["t1", ["A", "B", "A", "C"]]]
        rules = Rules.ExtractRules(trajectory, 1, 1, weighting_mode="none")
        network = BuildNetwork.BuildNetwork(rules)
        self.assertTrue(network)
        for source in network:
            self.assertEqual(len(source), 1)
            for target in network[source]:
                self.assertEqual(len(target), 1)


if __name__ == "__main__":
    unittest.main()
