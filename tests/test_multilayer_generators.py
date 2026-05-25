from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from network_science_project.multilayer.generators import generate_poisson_graph


class MultilayerGeneratorPackageTests(unittest.TestCase):
    def test_generate_poisson_from_src_package(self) -> None:
        graph = generate_poisson_graph(12, 3, seed=1)
        self.assertEqual(graph.number_of_nodes(), 12)


if __name__ == "__main__":
    unittest.main()
