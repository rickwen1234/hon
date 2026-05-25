from __future__ import annotations

import os
import sys
import unittest

import networkx as nx

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from multilayer.dependencies import generate_random_matching, generate_same_id_dependencies
from multilayer.simplices import triangles_from_graph


class DependencyAndSimplexTests(unittest.TestCase):
    def test_random_dependency_links_with_q(self) -> None:
        A = nx.path_graph(10)
        B = nx.path_graph(6)
        deps = generate_random_matching(A, B, q=0.5, seed=1)
        self.assertEqual(len(deps), 3)

    def test_same_id_dependency_links(self) -> None:
        A = nx.Graph()
        B = nx.Graph()
        A.add_nodes_from(["x", "y", "z"])
        B.add_nodes_from(["y", "z", "w"])
        deps = generate_same_id_dependencies(A, B)
        self.assertEqual(deps, [("y", "y", 1.0), ("z", "z", 1.0)])

    def test_triangles_from_known_graph(self) -> None:
        G = nx.Graph()
        G.add_edges_from([("a", "b"), ("b", "c"), ("a", "c"), ("c", "d")])
        self.assertEqual(triangles_from_graph(G), [("a", "b", "c")])


if __name__ == "__main__":
    unittest.main()
