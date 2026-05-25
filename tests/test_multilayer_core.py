from __future__ import annotations

import os
import sys
import tempfile
import unittest

import networkx as nx

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from multilayer import GeneratorSpec, MultiLayerNetwork
from multilayer.cascade_adapter import export_peng_cascade_inputs


class MultiLayerCoreTests(unittest.TestCase):
    def test_create_empty_multilayer_network(self) -> None:
        mln = MultiLayerNetwork()
        self.assertEqual(mln.list_layers(), [])
        self.assertEqual(mln.validate(), [])

    def test_add_generated_poisson_layer(self) -> None:
        mln = MultiLayerNetwork()
        G = mln.add_layer("A", generator=GeneratorSpec(model="poisson", n=20, mean_degree=4, seed=1))
        self.assertEqual(G.number_of_nodes(), 20)
        self.assertEqual(mln.summary()["number_of_layers"], 1)

    def test_export_and_load_multilayer_network(self) -> None:
        mln = MultiLayerNetwork()
        mln.add_layer("A", generator=GeneratorSpec(model="poisson", n=10, mean_degree=2, seed=1))
        mln.add_layer("B", generator=GeneratorSpec(model="scale_free", n=10, mean_degree=2, seed=2))
        mln.add_dependency("A", "B", q=0.5, seed=3)
        mln.add_simplices("A", mode="random_triangles", count=2, seed=4)
        with tempfile.TemporaryDirectory() as tmp:
            mln.export(tmp)
            loaded = MultiLayerNetwork.load(tmp)
            self.assertEqual(set(loaded.list_layers()), {"A", "B"})
            self.assertTrue(os.path.exists(os.path.join(tmp, "summary.json")))

    def test_export_peng_cascade_inputs(self) -> None:
        mln = MultiLayerNetwork()
        mln.add_layer("A", generator=GeneratorSpec(model="poisson", n=8, mean_degree=2, seed=1))
        mln.add_layer("B", generator=GeneratorSpec(model="scale_free", n=8, mean_degree=2, seed=2))
        mln.add_dependency("A", "B", q=0.5, seed=3)
        with tempfile.TemporaryDirectory() as tmp:
            export_peng_cascade_inputs(mln, tmp, "A", "B")
            self.assertTrue(os.path.exists(os.path.join(tmp, "layer_A_edges.csv")))
            self.assertTrue(os.path.exists(os.path.join(tmp, "cascade_config.json")))

    def test_hon_layer_accepts_hon_labels(self) -> None:
        G = nx.DiGraph()
        G.add_edge("B|A", "C|B,A", weight=0.7)
        mln = MultiLayerNetwork()
        mln.add_layer("HON", graph=G, graph_type="directed", source="hon")
        self.assertEqual(mln.validate(), [])


if __name__ == "__main__":
    unittest.main()
