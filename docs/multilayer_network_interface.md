# Multilayer Network Interface

## Purpose

The `multilayer` package adds an optional interface for building, loading, exporting, and visualizing multilayer networks without changing the existing HON, Cog-HON, or cascade scripts.

It supports:

- ordinary graph layers from edge lists,
- HON/Cog-HON layers from HON edge lists,
- generated Poisson/Erdos-Renyi and scale-free layers,
- cross-layer dependency links with dependency strength `q`,
- triangle simplices for Peng-style cascade inputs,
- static and optional interactive visualizations.

## Layer Types

An ordinary graph layer is a standard NetworkX graph with edges such as:

```csv
source,target,weight
A,B,1.0
```

A HON layer is also an ordinary edge list, but node labels can encode path history:

```csv
from_node,to_node,weight
B|A,"C|B,A",0.72
```

A simplex layer is not a separate graph. It is a triangle list attached to one graph layer:

```csv
layer,node1,node2,node3,weight
A,u,v,w,1.0
```

## Dependency Strength `q`

`q` is the fraction of nodes in the smaller layer that receive dependency links. For example, if layer A has 100 nodes, layer B has 80 nodes, and `q=0.5`, then 40 dependency links are generated.

Supported dependency modes:

- `random_matching`
- `same_id`
- `from_file`
- `degree_assortative`
- `weight_based`

## Generated Layers

Poisson networks are implemented as Erdos-Renyi graphs with:

```text
p = mean_degree / (n - 1)
```

Scale-free networks use NetworkX `scale_free_graph` for directed layers. Undirected scale-free layers use a Barabasi-Albert graph or a configuration power-law graph when `mean_degree` is provided.

## File Formats

Ordinary edge list:

```csv
source,target,weight,timestamp
u,v,1.0,2026-01-01T00:00:00
```

HON edge list:

```csv
from_node,to_node,weight
B|A,"C|B,A",0.72
```

Dependency list:

```csv
source_layer,source_node,target_layer,target_node,weight
A,u,B,v,1.0
```

Triangle simplex list:

```csv
layer,node1,node2,node3,weight
A,u,v,w,1.0
```

## CLI Examples

Build a Peng-style two-layer generated network:

```powershell
python experiments\build_multilayer_network.py `
  --output-dir outputs\mln_demo `
  --layer A:generated:poisson:n=1000,mean_degree=8 `
  --layer B:generated:scale_free:n=1000,gamma=2.5,mean_degree=8 `
  --dependency A:B:random_matching:q=0.8 `
  --simplices A:poisson_triangles:mean_triangle_degree=0.4 `
  --simplices B:poisson_triangles:mean_triangle_degree=0.4 `
  --seed 42
```

Build a mixed network with one real HON layer and one generated layer:

```powershell
python experiments\build_multilayer_network.py `
  --output-dir outputs\mln_real `
  --layer A:edge_list:data\layer_A_edges.csv:directed=false `
  --layer B:hon_edge_list:outputs\cog_hon_edges.csv:directed=true `
  --dependency A:B:from_file:data\dependency_links.csv `
  --simplices A:from_file:data\A_triangles.csv `
  --simplices B:triangles_from_graph
```

Visualize an exported network:

```powershell
python experiments\visualize_multilayer_network.py `
  --input-dir outputs\mln_demo `
  --output-dir outputs\mln_demo\figures `
  --modes layer,multilayer2d,multilayer3d,dependency_matrix,summary,interactive_html
```

Prepare Peng cascade inputs:

```powershell
python experiments\run_multilayer_peng_cascade.py `
  --input-dir outputs\mln_demo `
  --layer-a A `
  --layer-b B `
  --cascade-output-dir outputs\mln_demo\cascade_inputs
```

## Export Layout

`mln.export(output_dir)` writes:

```text
output_dir/
  metadata.json
  summary.json
  layers/
    A_edges.csv
    B_edges.csv
  dependencies/
    A__B_dependencies.csv
  simplices/
    A_triangles.csv
    B_triangles.csv
```

## Peng Cascade Handoff

`export_peng_cascade_inputs` writes:

```text
layer_A_edges.csv
layer_B_edges.csv
layer_A_triangles.csv
layer_B_triangles.csv
dependency_links.csv
cascade_config.json
```

This adapter prepares clean inputs only. It does not replace or rewrite an existing Peng cascade simulation.
