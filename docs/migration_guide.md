# Migration Guide

## Old Entry Points

Existing scripts remain available:

- `pyHON/main.py`
- `experiments/build_memory_hon.py`
- `experiments/cascade_on_hon.py`
- `experiments/build_multilayer_network.py`
- `experiments/visualize_multilayer_network.py`
- `experiments/run_multilayer_peng_cascade.py`

## New Entry Points

Prefer:

- `scripts/build_hon.py`
- `scripts/build_memory_hon.py`
- `scripts/build_multilayer_network.py`
- `scripts/visualize_multilayer_network.py`
- `scripts/run_peng_cascade.py`
- `scripts/run_full_pipeline.py`

After installing the package, prefer console commands:

- `ns-build-hon`
- `ns-build-memory-hon`
- `ns-build-multilayer`
- `ns-run-peng-cascade`
- `ns-run-full-pipeline`
- `ns-visualize-multilayer`
- `ns-summarize-results`

The `scripts/` files are deprecated compatibility wrappers and emit a deprecation warning.

## New Imports

Use package imports for new code:

```python
from network_science_project.hon import extract_rules, build_network
from network_science_project.multilayer import MultiLayerNetwork
from network_science_project.cascade import run_peng_cascade
```

The legacy `pyHON` package is retained as the compatibility implementation for HON algorithms.
