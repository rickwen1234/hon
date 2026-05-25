from __future__ import annotations

from collections import defaultdict
import csv
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from network_science_project.experiments.build_hon import run_hon_experiment
from network_science_project.experiments.build_memory_hon import run_memory_hon_experiment
from network_science_project.experiments.build_multilayer import run_multilayer_experiment
from network_science_project.experiments.run_full_pipeline import run as run_full_pipeline
from network_science_project.experiments.run_peng_cascade import run_peng_cascade_experiment
from network_science_project.experiments.summarize_results import summarize_cascade_results
from network_science_project.hon._legacy import ensure_pyhon_path
from network_science_project.multilayer import MultiLayerNetwork

ensure_pyhon_path()
import BuildNetwork


class ExperimentLayerTests(unittest.TestCase):
    def tearDown(self) -> None:
        BuildNetwork.Graph = defaultdict(dict)

    def _write_sequence_file(self, tmp: str) -> str:
        path = os.path.join(tmp, "toy_sequences.txt")
        lines = []
        for index in range(8):
            lines.append("a{0} A B C X".format(index))
            lines.append("d{0} D B C Y".format(index))
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines))
        return path

    def _write_timestamped_events(self, tmp: str) -> str:
        path = os.path.join(tmp, "toy_timestamped.csv")
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["trace_id", "node_id", "timestamp"])
            writer.writerow(["t1", "A", "1"])
            writer.writerow(["t1", "B", "2"])
            writer.writerow(["t1", "A", "9"])
            writer.writerow(["t1", "C", "10"])
        return path

    def assert_standard_output_layout(self, output_dir: str) -> None:
        self.assertTrue(os.path.exists(os.path.join(output_dir, "config_used.json")))
        self.assertTrue(os.path.isdir(os.path.join(output_dir, "logs")))
        self.assertTrue(os.path.isdir(os.path.join(output_dir, "data")))
        self.assertTrue(os.path.isdir(os.path.join(output_dir, "figures")))
        self.assertTrue(os.path.isdir(os.path.join(output_dir, "metrics")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "summary.json")))

    def test_run_hon_experiment_writes_standard_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sequence_path = self._write_sequence_file(tmp)
            output_dir = os.path.join(tmp, "hon")
            summary = run_hon_experiment(sequence_path, output_dir, max_order=3, min_support=1)
            self.assert_standard_output_layout(output_dir)
            self.assertTrue(os.path.exists(summary["output_network"]))
            with open(summary["output_network"], encoding="utf-8") as handle:
                self.assertIn("C|B.A", handle.read())

    def test_run_memory_hon_experiment_writes_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            input_path = self._write_timestamped_events(tmp)
            output_dir = os.path.join(tmp, "memory")
            summaries = run_memory_hon_experiment(
                input_path,
                output_dir,
                max_order=2,
                min_support=1,
                weighting_mode="decay",
                decay_mode="exp",
                lambda_=0.5,
                input_format="csv_events",
                seed=1,
            )
            self.assert_standard_output_layout(output_dir)
            self.assertEqual([item["name"] for item in summaries], ["decay_hon"])
            self.assertTrue(os.path.exists(os.path.join(output_dir, "metrics", "decay_hon_weighted_rules.csv")))

    def test_run_multilayer_experiment_export_reload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = os.path.join(tmp, "mln")
            mln = run_multilayer_experiment(
                output_dir,
                ["A:generated:poisson:n=20,mean_degree=4", "B:generated:scale_free:n=20,mean_degree=4"],
                ["A:B:random_matching:q=0.5"],
                ["A:random_triangles:count=2", "B:random_triangles:count=2"],
                seed=2,
            )
            self.assert_standard_output_layout(output_dir)
            loaded = MultiLayerNetwork.load(os.path.join(output_dir, "data"))
            self.assertEqual(loaded.get_layer("A").number_of_nodes(), mln.get_layer("A").number_of_nodes())
            self.assertEqual(len(loaded.dependencies[("A", "B")]), 10)

    def test_run_peng_cascade_experiment_and_summarize(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mln_dir = os.path.join(tmp, "mln")
            run_multilayer_experiment(
                mln_dir,
                ["A:generated:poisson:n=12,mean_degree=3", "B:generated:scale_free:n=12,mean_degree=3"],
                ["A:B:random_matching:q=0.5"],
                ["A:random_triangles:count=1", "B:random_triangles:count=1"],
                seed=3,
            )
            cascade_dir = os.path.join(tmp, "cascade")
            rows = run_peng_cascade_experiment(mln_dir, cascade_dir, "A", "B", trials=3, seed=4)
            self.assert_standard_output_layout(cascade_dir)
            self.assertEqual(len(rows), 3)
            results_csv = os.path.join(cascade_dir, "data", "cascade_results.csv")
            summary = summarize_cascade_results(results_csv)
            self.assertIn("final_giant_A", summary)

    def test_run_full_pipeline_writes_data_and_figures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = os.path.join(tmp, "full")
            run_full_pipeline(output_dir, seed=5)
            self.assert_standard_output_layout(output_dir)
            self.assertTrue(os.path.exists(os.path.join(output_dir, "figures", "multilayer_2d.png")))
            self.assertTrue(os.path.exists(os.path.join(output_dir, "data", "cascade", "data", "cascade_results.csv")))


if __name__ == "__main__":
    unittest.main()
