"""Small full-pipeline demo connecting multilayer, cascade, and visualization layers."""

from __future__ import annotations

import os

from network_science_project.experiments.build_multilayer import run_multilayer_experiment
from network_science_project.experiments.run_peng_cascade import run_peng_cascade_experiment
from network_science_project.visualization import plot_dependency_matrix, plot_layer_summary, plot_multilayer_2d
from network_science_project.utils.experiment import prepare_output_dir, write_summary


def run(output_dir: str = "outputs/full_pipeline_demo", seed: int = 42, config: dict | None = None) -> None:
    """Run a deterministic generated-layer to cascade to visualization demo."""
    paths = prepare_output_dir(output_dir, {"seed": seed, **(config or {})})
    multilayer_dir = os.path.join(paths["data"], "multilayer")
    cascade_dir = os.path.join(paths["data"], "cascade")
    layer_specs = [
        "A:generated:poisson:n=100,mean_degree=8",
        "B:generated:scale_free:n=100,gamma=2.5,mean_degree=8",
    ]
    dependency_specs = ["A:B:random_matching:q=0.8"]
    simplex_specs = [
        "A:poisson_triangles:mean_triangle_degree=0.4",
        "B:poisson_triangles:mean_triangle_degree=0.4",
    ]
    mln = run_multilayer_experiment(multilayer_dir, layer_specs, dependency_specs, simplex_specs, seed)
    cascade_rows = run_peng_cascade_experiment(multilayer_dir, cascade_dir, "A", "B", trials=3, seed=seed)
    plot_multilayer_2d(mln, os.path.join(paths["figures"], "multilayer_2d.png"))
    plot_dependency_matrix(mln, os.path.join(paths["figures"], "dependency_matrix.png"))
    plot_layer_summary(mln, os.path.join(paths["figures"], "layer_summary.png"))
    write_summary(output_dir, {
        "multilayer_dir": multilayer_dir,
        "cascade_dir": cascade_dir,
        "cascade_trials": len(cascade_rows),
    })
