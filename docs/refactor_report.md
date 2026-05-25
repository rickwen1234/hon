# Refactor Report

## 1. Summary

The repository now uses a `src`-layout package named `network_science_project`. Scientific concerns are separated into:

- `hon`: HON/Cog-HON parsing, rule extraction, network wiring, IO, and diagnostics.
- `multilayer`: multilayer graph structure, generators, dependencies, simplices, validation, IO, and Peng input export.
- `cascade`: Peng-style two-layer failure propagation, metrics, and result IO.
- `visualization`: static and optional interactive plotting.
- `experiments`: reproducible workflows connecting the modules.
- `cli`: argparse entry points only.

Legacy folders remain in place for compatibility.

## 2. Files Moved

Functionality was moved or mirrored into:

- `src/network_science_project/hon/`
- `src/network_science_project/multilayer/`
- `src/network_science_project/cascade/`
- `src/network_science_project/visualization/`
- `src/network_science_project/experiments/`
- `src/network_science_project/cli/`
- `src/network_science_project/utils/`

The original `pyHON/` implementation is preserved and wrapped rather than rewritten.

## 3. Files Renamed

No legacy algorithm file was renamed. New package modules use clearer names such as `rule_extraction.py`, `network_wiring.py`, `failure_rules.py`, and `simulation.py`.

## 4. Backward-Compatible Wrappers

Wrappers were added under `scripts/`:

- `build_hon.py`
- `build_memory_hon.py`
- `build_multilayer_network.py`
- `visualize_multilayer_network.py`
- `run_peng_cascade.py`
- `run_full_pipeline.py`
- `summarize_results.py`

They emit deprecation warnings and call the new CLI modules.

## 5. Public APIs

Key imports:

```python
from network_science_project.hon import extract_rules, build_network
from network_science_project.multilayer import MultiLayerNetwork, GeneratorSpec
from network_science_project.cascade import PengCascadeConfig, run_peng_cascade
from network_science_project.visualization import plot_multilayer_2d
```

## 6. CLI Commands

Defined in `pyproject.toml`:

- `ns-build-hon`
- `ns-build-memory-hon`
- `ns-build-multilayer`
- `ns-run-peng-cascade`
- `ns-run-full-pipeline`
- `ns-visualize-multilayer`
- `ns-summarize-results`

## 7. Test Results

The full test suite was run with:

```powershell
python -m unittest discover -s tests -p 'test*.py'
```

Result after this refactor:

```text
Ran 33 tests in 0.884s
OK
```

Structure verifier:

```text
PASS: project structure is clean
```

Verified CLI examples:

```powershell
ns-build-multilayer --output-dir outputs\mln_demo_refactor --layer A:generated:poisson:n=500,mean_degree=8 --layer B:generated:scale_free:n=500,gamma=2.5,mean_degree=8 --dependency A:B:random_matching:q=0.8 --simplices A:poisson_triangles:mean_triangle_degree=0.4 --simplices B:poisson_triangles:mean_triangle_degree=0.4 --seed 42
ns-run-peng-cascade --input-dir outputs\mln_demo_refactor --layer-a A --layer-b B --output-dir outputs\mln_demo_refactor\cascade --trials 20 --seed 42
ns-visualize-multilayer --input-dir outputs\mln_demo_refactor --output-dir outputs\mln_demo_refactor\figures --modes multilayer2d,multilayer3d,dependency_matrix,summary --seed 42
ns-run-full-pipeline --config configs\demo_full_pipeline.yaml --output-dir outputs\full_demo_refactor --seed 42
```

## 8. Known Limitations

- HON algorithms are wrapped from `pyHON` to preserve behavior; deeper internal cleanup remains future work.
- The Peng cascade implementation is a clean reusable baseline, not a claim of complete reproduction of every Peng et al. simulation variant.
- Optional visualization backends such as Plotly and PyVis are used only when installed.

## 9. Next Recommended Step

Move legacy experiment-specific logic from `experiments/verify_cog_hon_peng.py` and `experiments/cascade_on_hon.py` into reusable package functions, then leave those files as thin compatibility wrappers.
