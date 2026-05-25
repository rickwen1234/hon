"""Experiment helper for Peng-style cascade simulation."""

from __future__ import annotations

import os
from typing import Any

from network_science_project.cascade.metrics import giant_component_ratio
from network_science_project.cascade.io import load_peng_inputs, write_cascade_results
from network_science_project.cascade.peng_model import PengCascadeConfig, PengCascadeState
from network_science_project.cascade.simulation import run_peng_cascade
from network_science_project.multilayer import MultiLayerNetwork
from network_science_project.multilayer.cascade_adapter import export_peng_cascade_inputs
from network_science_project.utils.experiment import prepare_output_dir, write_summary


def run_from_input_dir(input_dir: str, output_csv: str, initial_failure_fraction: float = 0.1, seed: int | None = None):
    """Run one cascade from a prepared Peng input directory and write standardized results."""
    payload = load_peng_inputs(input_dir)
    state = PengCascadeState(
        graph_a=payload["graph_a"],
        graph_b=payload["graph_b"],
        triangles_a=payload["triangles_a"],
        triangles_b=payload["triangles_b"],
        dependencies=payload["dependencies"],
        failed_a=set(),
        failed_b=set(),
    )
    rows = run_peng_cascade(state, PengCascadeConfig(initial_failure_fraction=initial_failure_fraction, seed=seed))
    os.makedirs(os.path.dirname(output_csv) or ".", exist_ok=True)
    final = rows[-1] if rows else {"failed_A": 0, "failed_B": 0, "giant_A": 0.0, "giant_B": 0.0, "step": 0}
    result_rows = [{
        "model_name": "peng_cascade",
        "trial_id": 0,
        "removal_fraction": initial_failure_fraction,
        "S_A": final["giant_A"],
        "S_B": final["giant_B"],
        "failed_A": final["failed_A"],
        "failed_B": final["failed_B"],
        "cascade_steps": final["step"],
        "q": payload["config"].get("q", ""),
        "lambda": "",
        "mu": "",
        "theta": "",
    }]
    write_cascade_results(result_rows, output_csv)
    return result_rows


def _prepared_input_dir(input_dir: str, output_data_dir: str, layer_a: str, layer_b: str) -> str:
    if os.path.exists(os.path.join(input_dir, "layer_A_edges.csv")):
        return input_dir
    candidate = os.path.join(input_dir, "data")
    if os.path.exists(os.path.join(candidate, "metadata.json")):
        input_dir = candidate
    if os.path.exists(os.path.join(input_dir, "metadata.json")):
        mln = MultiLayerNetwork.load(input_dir)
        cascade_inputs = os.path.join(output_data_dir, "cascade_inputs")
        export_peng_cascade_inputs(mln, cascade_inputs, layer_a, layer_b)
        return cascade_inputs
    raise ValueError("Input directory is neither Peng cascade inputs nor a MultiLayerNetwork export: {0}".format(input_dir))


def run_peng_cascade_experiment(
    input_dir: str,
    output_dir: str,
    layer_a: str = "A",
    layer_b: str = "B",
    trials: int = 1,
    removal_fraction: float = 0.1,
    seed: int | None = None,
    config: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Run repeated Peng-style cascades and write standardized experiment outputs."""
    config_used = {
        "input_dir": input_dir,
        "layer_a": layer_a,
        "layer_b": layer_b,
        "trials": trials,
        "removal_fraction": removal_fraction,
        "seed": seed,
        **(config or {}),
    }
    paths = prepare_output_dir(output_dir, config_used)
    prepared = _prepared_input_dir(input_dir, paths["data"], layer_a, layer_b)
    payload = load_peng_inputs(prepared)
    q = payload["config"].get("q", "")
    result_rows: list[dict[str, Any]] = []
    for trial_id in range(trials):
        trial_seed = None if seed is None else seed + trial_id
        state = PengCascadeState(
            graph_a=payload["graph_a"].copy(),
            graph_b=payload["graph_b"].copy(),
            triangles_a=payload["triangles_a"],
            triangles_b=payload["triangles_b"],
            dependencies=payload["dependencies"],
            failed_a=set(),
            failed_b=set(),
        )
        trace = run_peng_cascade(
            state,
            PengCascadeConfig(
                layer_a=layer_a,
                layer_b=layer_b,
                initial_failure_fraction=removal_fraction,
                seed=trial_seed,
            ),
        )
        final = trace[-1]
        result_rows.append({
            "model_name": "peng_cascade",
            "trial_id": trial_id,
            "removal_fraction": removal_fraction,
            "S_A": final["giant_A"],
            "S_B": final["giant_B"],
            "failed_A": final["failed_A"],
            "failed_B": final["failed_B"],
            "cascade_steps": final["step"],
            "q": q,
            "lambda": "",
            "mu": "",
            "theta": "",
        })
    output_csv = os.path.join(paths["data"], "cascade_results.csv")
    write_cascade_results(result_rows, output_csv)
    if result_rows:
        summary = {
            "trials": trials,
            "mean_S_A": sum(float(row["S_A"]) for row in result_rows) / len(result_rows),
            "mean_S_B": sum(float(row["S_B"]) for row in result_rows) / len(result_rows),
            "results_csv": output_csv,
        }
    else:
        summary = {"trials": 0, "mean_S_A": 0.0, "mean_S_B": 0.0, "results_csv": output_csv}
    write_summary(output_dir, summary)
    return result_rows
