# Peng-Style Cascade

The cascade package represents the dynamical robustness layer. It consumes prepared two-layer inputs:

- `layer_A_edges.csv`
- `layer_B_edges.csv`
- `layer_A_triangles.csv`
- `layer_B_triangles.csv`
- `dependency_links.csv`
- `cascade_config.json`

The simulation applies initial node failure, same-layer triangle propagation, and cross-layer dependency propagation recursively until convergence.

`q` is the dependency density: the fraction of nodes in the smaller layer receiving dependency links.

Outputs use `S_A` and `S_B` for the remaining giant-component ratios in layer A and layer B.

Use:

```powershell
ns-run-peng-cascade --input-dir outputs\mln_demo --layer-a A --layer-b B --output-dir outputs\mln_demo\cascade --trials 20 --seed 42
```
