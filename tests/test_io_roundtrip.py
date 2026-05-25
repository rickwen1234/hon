from __future__ import annotations

import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from network_science_project.multilayer import GeneratorSpec, MultiLayerNetwork


class IoRoundtripTests(unittest.TestCase):
    def test_multilayer_export_load_roundtrip_src_package(self) -> None:
        mln = MultiLayerNetwork()
        mln.add_layer("A", generator=GeneratorSpec(model="poisson", n=8, mean_degree=2, seed=1))
        mln.add_layer("B", generator=GeneratorSpec(model="scale_free", n=8, mean_degree=2, seed=2))
        mln.add_dependency("A", "B", q=0.5, seed=3)
        mln.add_simplices("A", mode="random_triangles", count=2, seed=4)
        with tempfile.TemporaryDirectory() as tmp:
            mln.export(tmp)
            loaded = MultiLayerNetwork.load(tmp)
            self.assertEqual(set(loaded.list_layers()), {"A", "B"})
            self.assertEqual(loaded.get_layer("A").number_of_nodes(), mln.get_layer("A").number_of_nodes())
            self.assertEqual(loaded.get_layer("B").number_of_edges(), mln.get_layer("B").number_of_edges())
            self.assertEqual(len(loaded.dependencies[("A", "B")]), len(mln.dependencies[("A", "B")]))
            self.assertEqual(len(loaded.simplices["A"]), len(mln.simplices["A"]))


if __name__ == "__main__":
    unittest.main()
