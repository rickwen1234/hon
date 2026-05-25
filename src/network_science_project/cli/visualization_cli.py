"""CLI for multilayer visualization."""

from __future__ import annotations

import argparse
import os

from network_science_project.multilayer import MultiLayerNetwork
from network_science_project.utils.config import load_config
from network_science_project.utils.experiment import prepare_output_dir, write_summary
from network_science_project.visualization import (
    export_interactive_html,
    plot_dependency_matrix,
    plot_layer,
    plot_layer_summary,
    plot_multilayer_2d,
    plot_multilayer_3d,
)


def _resolve_multilayer_dir(input_dir: str) -> str:
    if os.path.exists(os.path.join(input_dir, "metadata.json")):
        return input_dir
    data_dir = os.path.join(input_dir, "data")
    if os.path.exists(os.path.join(data_dir, "metadata.json")):
        return data_dir
    return input_dir


def main() -> None:
    """Parse arguments and generate multilayer visualizations."""
    parser = argparse.ArgumentParser(description="Visualize an exported multilayer network.")
    parser.add_argument("--config", default=None)
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", default="outputs/visualize_multilayer")
    parser.add_argument("--modes", default="multilayer2d,multilayer3d,dependency_matrix,summary")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    config = load_config(args.config) if args.config else {}
    if os.path.basename(os.path.normpath(args.output_dir)).lower() == "figures":
        experiment_root = os.path.dirname(os.path.normpath(args.output_dir)) or "."
        paths = prepare_output_dir(experiment_root, {"input_dir": args.input_dir, "modes": args.modes, "seed": args.seed, **config})
        figure_dir = args.output_dir
        os.makedirs(figure_dir, exist_ok=True)
    else:
        paths = prepare_output_dir(args.output_dir, {"input_dir": args.input_dir, "modes": args.modes, "seed": args.seed, **config})
        figure_dir = paths["figures"]
    mln = MultiLayerNetwork.load(_resolve_multilayer_dir(args.input_dir))
    modes = {mode.strip() for mode in args.modes.split(",") if mode.strip()}
    if "layer" in modes:
        for layer, graph in mln.layers.items():
            plot_layer(graph, os.path.join(figure_dir, "{0}_layer.png".format(layer)), title=layer)
    if "multilayer2d" in modes:
        plot_multilayer_2d(mln, os.path.join(figure_dir, "multilayer_2d.png"))
    if "multilayer3d" in modes:
        plot_multilayer_3d(mln, os.path.join(figure_dir, "multilayer_3d.html"))
    if "dependency_matrix" in modes:
        plot_dependency_matrix(mln, os.path.join(figure_dir, "dependency_matrix.png"))
    if "summary" in modes:
        plot_layer_summary(mln, os.path.join(figure_dir, "layer_summary.png"))
    if "interactive_html" in modes:
        export_interactive_html(mln, os.path.join(figure_dir, "interactive_multilayer.html"))
    write_summary(paths["root"], {"figures_dir": figure_dir, "modes": sorted(modes)})
    print("Wrote visualizations to {0}".format(args.output_dir))
