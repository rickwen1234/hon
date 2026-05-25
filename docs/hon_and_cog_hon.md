# HON and Cog-HON

HON construction reads sequential trajectories, extracts variable-order transition rules, and wires those rules into an edge-list network representation compatible with ordinary graph analysis.

Cog-HON and decay-HON extend rule extraction by weighting timestamped observations. The package keeps this behavior in `network_science_project.hon` while preserving the legacy `pyHON` entry points.

Use:

```powershell
ns-build-hon --input examples\toy_sequences.csv --output-dir outputs\toy_hon --max-order 2 --min-support 1
```

Memory-weighted example:

```powershell
ns-build-memory-hon --input examples\toy_timestamped_sequences.csv --input-format csv_events --output-dir outputs\toy_cog_hon --weighting-mode all --max-order 3 --min-support 1 --lambda 0.1 --mu 0.5 --theta 0.01
```
