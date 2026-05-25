# Multilayer Interface

The multilayer package manages graph layers, dependency links, and triangle simplices. It accepts ordinary graph edge lists and HON edge lists because HON outputs remain graph-compatible.

Main API:

```python
from network_science_project.multilayer import GeneratorSpec, MultiLayerNetwork

mln = MultiLayerNetwork()
mln.add_layer("A", generator=GeneratorSpec(model="poisson", n=100, mean_degree=8, seed=42))
mln.add_layer("B", generator=GeneratorSpec(model="scale_free", n=100, mean_degree=8, seed=43))
mln.add_dependency("A", "B", q=0.8, seed=42)
mln.add_simplices("A", mode="poisson_triangles", mean_triangle_degree=0.4, seed=42)
mln.export("outputs/demo_multilayer")
```

CLI example:

```powershell
ns-build-multilayer --output-dir outputs/mln_demo --layer A:generated:poisson:n=500,mean_degree=8 --layer B:generated:scale_free:n=500,gamma=2.5,mean_degree=8 --dependency A:B:random_matching:q=0.8 --simplices A:poisson_triangles:mean_triangle_degree=0.4 --simplices B:poisson_triangles:mean_triangle_degree=0.4 --seed 42
```

Supported generated layers include `poisson`, `erdos_renyi`, `scale_free`, `barabasi_albert`, and `configuration_powerlaw`. Dependency modes include `random_matching`, `same_id`, `from_file`, `degree_assortative`, and `weight_based`. Simplex modes include `triangles_from_graph`, `cliques_k3`, `poisson_triangles`, `random_triangles`, and `from_file`.
