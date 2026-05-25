# Refactor Audit

## 1. Current Top-Level Folders

- `applications/`: standalone legacy scripts for HON PageRank and synthetic trajectory generation.
- `cl-HON/`: Common Lisp implementation of the original HON workflow.
- `data/`: small and medium HON inputs/outputs, including synthetic traces, rules, timestamped examples, and memory-HON example outputs.
- `data_porto_taxi/`: Porto taxi preprocessing scripts, trajectories, network edge lists, and geospatial files.
- `docs/`: recent documentation for memory-weighted HON and the multilayer interface.
- `experiments/`: research scripts for memory-HON construction, cascade experiments, multilayer construction, visualization, and verification.
- `figs/`: existing figures.
- `HONVis/`: separate visualization assets and data for HON visualization.
- `multilayer/`: recently added multilayer infrastructure package.
- `outputs/`: generated experiment outputs, verification reports, cascade results, and multilayer demo outputs.
- `papers/`: reference papers, slides, and dissertation material.
- `pyHON/`: legacy Python HON implementation plus Cog-HON/memory-weighted extensions.
- `tests/`: unit tests for memory-HON and multilayer functionality.
- `tutorial/`: tutorial code and synthetic tutorial data.

## 2. Current Scripts

- `applications/hon-pagerank.py`: appears to run PageRank on HON-style edge lists.
- `applications/synthesize-trace-mesh.py`: generates synthetic mesh trajectories.
- `data_porto_taxi/CleanPortugalData.py`: Porto taxi/geospatial preprocessing.
- `data_porto_taxi/PolicePOI.py`: police point-of-interest processing.
- `experiments/build_memory_hon.py`: builds FON, original HON, Decay-HON, and Cog-HON variants from timestamped data.
- `experiments/build_multilayer_network.py`: builds and exports generated or loaded multilayer networks.
- `experiments/cascade_on_hon.py`: runs projected cascade robustness experiments over HON-like edge lists.
- `experiments/demo_multilayer_pipeline.py`: small end-to-end multilayer demo.
- `experiments/run_multilayer_peng_cascade.py`: prepares Peng-style cascade input files from an exported multilayer network.
- `experiments/verify_cog_hon_peng.py`: verification workflow connecting Cog-HON outputs and Peng-style cascade metrics.
- `experiments/visualize_multilayer_network.py`: produces static and optional interactive multilayer visualizations.
- `pyHON/batch.py`, `pyHON/BatchBuildNetworks.py`: batch HON construction helpers.
- `pyHON/build-synthetic.py`: synthetic data generation/build helper.
- `pyHON/graph-diff.py`: graph comparison utility.
- `pyHON/main.py`: primary legacy HON/Cog-HON command-line entry point.
- `tutorial/code/3_1_buildhon.py`: tutorial HON construction example.
- `tutorial/code/dependencies/*.py`: tutorial-local copies of synthetic generation, rule extraction, and network rewiring logic.

## 3. Current Data Formats

- Legacy trajectory format: `TraceID Node1 Node2 Node3 ...`.
- Timestamped path format: `TraceID Node1@timestamp Node2@timestamp ...`.
- CSV event format: `trace_id,node_id,timestamp`.
- HON rule format: `PrevPrev Prev Curr => Target Probability`.
- HON network edge format: `from_node,to_node,weight`, where node labels can encode history as `Curr|Prev.PrevPrev` or variants with commas.
- Ordinary edge list: `source,target,weight`.
- Dependency list: `source_layer,source_node,target_layer,target_node,weight`.
- Triangle/simplex list: `layer,node1,node2,node3,weight`.
- Multilayer export format: `metadata.json`, `summary.json`, `layers/*_edges.csv`, `dependencies/*__*_dependencies.csv`, `simplices/*_triangles.csv`.
- Peng cascade adapter format: `layer_A_edges.csv`, `layer_B_edges.csv`, `layer_A_triangles.csv`, `layer_B_triangles.csv`, `dependency_links.csv`, `cascade_config.json`.
- Verification/cascade result tables: CSV result files plus JSON/Markdown summaries.

## 4. Existing Entry Points

- `python pyHON/main.py ...`
- `python experiments/build_memory_hon.py ...`
- `python experiments/cascade_on_hon.py ...`
- `python experiments/verify_cog_hon_peng.py ...`
- `python experiments/build_multilayer_network.py ...`
- `python experiments/visualize_multilayer_network.py ...`
- `python experiments/run_multilayer_peng_cascade.py ...`
- `python applications/synthesize-trace-mesh.py ...`
- tutorial scripts under `tutorial/code/`.

## 5. Current Dependencies

Observed imports include:

- Standard library: `argparse`, `csv`, `json`, `math`, `os`, `random`, `sys`, `tempfile`, `unittest`, `warnings`, `collections`, `dataclasses`, `typing`.
- Scientific/runtime: `networkx`, `numpy`, `matplotlib`.
- Optional visualization: `plotly`, `pyvis`.
- Legacy/geospatial/data scripts may use `pandas`, `geopandas`/GIS-related tooling depending on local environment.
- Common Lisp implementation requires SBCL/Quicklisp and `split-sequence`.

## 6. Duplicated Code

- HON rule extraction and network rewiring exist in `pyHON/` and again under `tutorial/code/dependencies/`.
- Synthetic trajectory generation exists in `applications/`, `pyHON/build-synthetic.py`, and tutorial dependencies.
- Edge-list loading/writing logic appears in HON scripts, multilayer IO, cascade scripts, and verification scripts.
- Cascade-like robustness code exists in `experiments/cascade_on_hon.py` and verification scripts rather than a reusable cascade package.
- Visualization functionality is split between `HONVis/` assets and `multilayer/visualization.py`.

## 7. Current Unclear Boundaries

- `pyHON/main.py` is both an algorithm module and a CLI.
- Experiment scripts add paths to `sys.path` and import directly from `pyHON`, which makes import boundaries fragile.
- Cascade code currently lives under `experiments/`, even though it represents dynamical model logic.
- Multilayer visualization is inside the `multilayer` package, mixing infrastructure and presentation.
- Generated outputs are committed or left beside source-like folders, making it hard to tell source from artifacts.
- The repo has both legacy source folders and newly added package-like folders at the same level.

## 8. Existing Tests

- `tests/test_memory_hon.py`: validates temporal weighting, CogSNet update behavior, weighted rule extraction, and HON network wiring.
- `tests/test_multilayer_core.py`: validates multilayer creation, generated layers, export/load, Peng adapter export, and HON-label validation.
- `tests/test_generators.py`: validates Poisson and scale-free graph generation.
- `tests/test_dependencies.py`: validates dependency generation and triangle detection.
- `tests/test_visualization_inputs.py`: validates visualization output creation and empty-layer handling.

## 9. Risk List

Files to avoid heavy modification unless explicitly required:

- `pyHON/BuildRules.py`: original algorithm translation.
- `pyHON/BuildRulesFastParameterFree.py`: current parameter-free and memory-weighted extraction logic.
- `pyHON/BuildRulesFastParameterFreeFreq.py`: frequency-mode rule extraction.
- `pyHON/BuildNetwork.py`: HON network wiring behavior and output semantics.
- `pyHON/main.py`: legacy command-line compatibility surface.
- `experiments/build_memory_hon.py`, `experiments/cascade_on_hon.py`, `experiments/verify_cog_hon_peng.py`: current research workflows that may encode experiment assumptions.
- `cl-HON/*`: original Common Lisp implementation.
- `tutorial/*`: educational material that may intentionally duplicate legacy algorithms.
- Existing data under `data/`, `data_porto_taxi/`, `HONVis/`, and `papers/`: should be treated as fixtures/reference material, not refactor targets.
