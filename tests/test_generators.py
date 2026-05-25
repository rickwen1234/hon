from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from multilayer.generators import generate_poisson_graph, generate_scale_free_graph


class GeneratorTests(unittest.TestCase):
    def test_poisson_graph_uses_expected_metadata(self) -> None:
        G = generate_poisson_graph(30, 4, seed=1)
        self.assertEqual(G.number_of_nodes(), 30)
        self.assertEqual(G.graph["generator"]["model"], "poisson")

    def test_scale_free_graph_is_generated(self) -> None:
        G = generate_scale_free_graph(30, gamma=2.5, mean_degree=4, seed=2)
        self.assertEqual(G.number_of_nodes(), 30)
        self.assertEqual(G.graph["generator"]["model"], "scale_free")


if __name__ == "__main__":
    unittest.main()
