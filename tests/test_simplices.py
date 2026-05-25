from __future__ import annotations

import os
import sys
import unittest

import networkx as nx

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from network_science_project.multilayer.simplices import triangles_from_graph


class SimplexPackageTests(unittest.TestCase):
    def test_triangle_detection(self) -> None:
        graph = nx.Graph()
        graph.add_edges_from([("a", "b"), ("b", "c"), ("a", "c")])
        self.assertEqual(triangles_from_graph(graph), [("a", "b", "c")])


if __name__ == "__main__":
    unittest.main()
