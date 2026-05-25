"""End-to-end demo for the multilayer network interface."""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from multilayer import GeneratorSpec, MultiLayerNetwork
from multilayer.cascade_adapter import export_peng_cascade_inputs
from multilayer.visualization import plot_dependency_matrix, plot_layer_summary, plot_multilayer_2d, plot_multilayer_3d


def main() -> None:
    output_dir = os.path.join(ROOT, "outputs", "mln_demo")
    figures_dir = os.path.join(output_dir, "figures")
    cascade_dir = os.path.join(output_dir, "cascade_inputs")
    os.makedirs(figures_dir, exist_ok=True)
    mln = MultiLayerNetwork()
    mln.add_layer("A", generator=GeneratorSpec(model="poisson", n=100, mean_degree=8, seed=42))
    mln.add_layer("B", generator=GeneratorSpec(model="scale_free", n=100, gamma=2.5, mean_degree=8, seed=43))
    mln.add_dependency("A", "B", mode="random_matching", q=0.8, seed=42)
    mln.add_simplices("A", mode="poisson_triangles", mean_triangle_degree=0.4, seed=42)
    mln.add_simplices("B", mode="poisson_triangles", mean_triangle_degree=0.4, seed=43)
    mln.export(output_dir)
    plot_multilayer_2d(mln, os.path.join(figures_dir, "multilayer_2d.png"))
    plot_multilayer_3d(mln, os.path.join(figures_dir, "multilayer_3d.html"))
    plot_dependency_matrix(mln, os.path.join(figures_dir, "dependency_matrix.png"))
    plot_layer_summary(mln, os.path.join(figures_dir, "layer_summary.png"))
    export_peng_cascade_inputs(mln, cascade_dir, "A", "B")
    print("Demo outputs written to {0}".format(output_dir))


if __name__ == "__main__":
    main()
