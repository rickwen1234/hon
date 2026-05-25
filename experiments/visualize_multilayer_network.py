"""Visualize an exported multilayer network."""

from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from multilayer import MultiLayerNetwork
from multilayer.visualization import (
    export_interactive_html,
    plot_dependency_matrix,
    plot_layer,
    plot_layer_summary,
    plot_multilayer_2d,
    plot_multilayer_3d,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create multilayer network figures.")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--modes", default="layer,multilayer2d,multilayer3d,dependency_matrix,summary,interactive_html")
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    mln = MultiLayerNetwork.load(args.input_dir)
    modes = {mode.strip() for mode in args.modes.split(",") if mode.strip()}
    if "layer" in modes:
        for layer, graph in mln.layers.items():
            plot_layer(graph, os.path.join(args.output_dir, "{0}_layer.png".format(layer)), title=layer)
    if "multilayer2d" in modes:
        plot_multilayer_2d(mln, os.path.join(args.output_dir, "multilayer_2d.png"))
    if "multilayer3d" in modes:
        plot_multilayer_3d(mln, os.path.join(args.output_dir, "multilayer_3d.html"))
    if "dependency_matrix" in modes:
        plot_dependency_matrix(mln, os.path.join(args.output_dir, "dependency_matrix.png"))
    if "summary" in modes:
        plot_layer_summary(mln, os.path.join(args.output_dir, "layer_summary.png"))
    if "interactive_html" in modes:
        export_interactive_html(mln, os.path.join(args.output_dir, "interactive_multilayer.html"))
    print("Wrote visualizations to {0}".format(args.output_dir))


if __name__ == "__main__":
    main()
