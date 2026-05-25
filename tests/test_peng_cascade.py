from __future__ import annotations

import os
import sys
import unittest

import networkx as nx

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from network_science_project.cascade.peng_model import PengCascadeConfig, PengCascadeState
from network_science_project.cascade.simulation import run_peng_cascade


class PengCascadeTests(unittest.TestCase):
    def test_dependency_and_simplex_failure_converges(self) -> None:
        graph_a = nx.Graph()
        graph_b = nx.Graph()
        graph_a.add_edges_from([("a", "b"), ("b", "c"), ("a", "c")])
        graph_b.add_edges_from([("x", "y"), ("y", "z"), ("x", "z")])
        state = PengCascadeState(
            graph_a=graph_a,
            graph_b=graph_b,
            triangles_a=[("a", "b", "c")],
            triangles_b=[("x", "y", "z")],
            dependencies=[("a", "x", 1.0)],
            failed_a={"a"},
            failed_b=set(),
        )
        rows = run_peng_cascade(state, PengCascadeConfig(initial_failure_fraction=0.0, seed=1))
        self.assertEqual(rows[-1]["failed_A"], 3)
        self.assertEqual(rows[-1]["failed_B"], 3)


if __name__ == "__main__":
    unittest.main()
