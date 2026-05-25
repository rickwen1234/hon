from __future__ import annotations

import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from multilayer import GeneratorSpec, MultiLayerNetwork
from multilayer.visualization import plot_dependency_matrix, plot_layer, plot_layer_summary, plot_multilayer_2d


class VisualizationInputTests(unittest.TestCase):
    def test_visualization_functions_create_files(self) -> None:
        mln = MultiLayerNetwork()
        mln.add_layer("A", generator=GeneratorSpec(model="poisson", n=12, mean_degree=2, seed=1))
        mln.add_layer("B", generator=GeneratorSpec(model="scale_free", n=12, mean_degree=2, seed=2))
        mln.add_dependency("A", "B", q=0.5, seed=3)
        with tempfile.TemporaryDirectory() as tmp:
            plot_layer(mln.layers["A"], os.path.join(tmp, "layer.png"))
            plot_multilayer_2d(mln, os.path.join(tmp, "multilayer_2d.png"))
            plot_dependency_matrix(mln, os.path.join(tmp, "dependency_matrix.png"))
            plot_layer_summary(mln, os.path.join(tmp, "layer_summary.png"))
            for filename in ["layer.png", "multilayer_2d.png", "dependency_matrix.png", "layer_summary.png"]:
                self.assertTrue(os.path.exists(os.path.join(tmp, filename)))

    def test_empty_layers_do_not_crash_visualization(self) -> None:
        mln = MultiLayerNetwork()
        mln.add_layer("empty")
        with tempfile.TemporaryDirectory() as tmp:
            plot_layer(mln.layers["empty"], os.path.join(tmp, "empty.png"))
            plot_multilayer_2d(mln, os.path.join(tmp, "empty_mln.png"))
            self.assertTrue(os.path.exists(os.path.join(tmp, "empty.png")))
            self.assertTrue(os.path.exists(os.path.join(tmp, "empty_mln.png")))


if __name__ == "__main__":
    unittest.main()
