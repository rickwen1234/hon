# Memory-Weighted HON

This extension keeps the original HON workflow as the default and adds an optional memory-weighted rule extraction mode for timestamped sequential data.

## What Changes

Original HON extracts variable-order rules from raw transition counts. Memory-weighted HON keeps the same rule-search and network-wiring structure, but transition distributions can be built from weighted support:

- Older observations can decay.
- Repeated observations can reinforce a source-target memory trace.
- KL-divergence comparisons can use weighted transition probabilities.

When `weighting_mode="none"` or `--weighting-mode none`, the implementation uses the original raw-count behavior and original edge weights.

## Input Formats

Legacy trajectory format remains supported:

```text
TraceID Node1 Node2 Node3
```

Timestamped path format:

```text
TraceID Node1@timestamp Node2@timestamp Node3@timestamp
```

CSV event format:

```csv
trace_id,node_id,timestamp
t1,A,2026-01-01T00:00:00
t1,B,2026-01-01T00:05:00
```

Timestamps may be numeric or ISO datetime strings. Timestamped events are sorted within each trace before construction.

## Parameters

- `--weighting-mode`: `none`, `decay`, or `cogsnet`.
- `--decay-mode`: `none`, `exp`, `power`, or `linear`.
- `--lambda`: forgetting strength.
- `--mu`: reinforcement value for CogSNet-style updates.
- `--theta`: reset threshold for CogSNet-style updates.
- `--analysis-time`: reference time for decay weighting. Defaults to the maximum timestamp in the input.
- `--support-type`: `raw` or `weighted` support for the KL threshold.
- `--edge-weight-type`: `probability`, `weighted_support`, or `raw_support`.
- `--debug-weighted-rules`: writes a diagnostic rules CSV.

## Example Commands

Build original HON from legacy data:

```bash
python pyHON/main.py --input data/traces-simulated-mesh-v100000-t100-mo4.csv --output-network data/network.csv --output-rules data/rules.csv --max-order 2 --min-support 5
```

Build Decay-HON from timestamped path data:

```bash
python pyHON/main.py --input data/timestamped.txt --input-format timestamped_path --output-network data/decay_network.csv --output-rules data/decay_rules.csv --max-order 3 --min-support 1 --weighting-mode decay --decay-mode exp --lambda 0.1 --debug-weighted-rules
```

Compare FON, original HON, Decay-HON, and Cog-HON:

```bash
python experiments/build_memory_hon.py --input data/timestamped.txt --input-format timestamped_path --output-dir data/memory_runs --max-order 3 --min-support 1 --lambda 0.1 --mu 0.5 --theta 0.01
```

Run projected cascade robustness on generated edge files:

```bash
python experiments/cascade_on_hon.py --model FON=data/memory_runs/fon_network.csv --model HON=data/memory_runs/original_hon_network.csv --model Decay-HON=data/memory_runs/decay_hon_network.csv --model Cog-HON=data/memory_runs/cog_hon_network.csv --output data/memory_runs/cascade.csv --trials 20 --steps 20
```

## Model Differences

- Original HON: raw transition counts determine transition distributions and rule significance.
- Decay-HON: each observed transition contributes a forgetting weight based on the gap between its timestamp and `analysis_time`.
- Cog-HON: each `(source_path, target)` memory trace evolves chronologically through decay and reinforcement; final trace strength is used as weighted support.

## Important Scope Note

Ordered HON dependencies are not the same as simplicial-complex higher-order interactions. HON represents sequential, path-dependent transition rules. It does not assert simultaneous group interactions or simplex closure.
