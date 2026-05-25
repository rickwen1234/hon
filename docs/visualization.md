# Visualization

Visualization is separate from construction and simulation. It reads graph-like outputs and writes figures:

- layer plots,
- 2D multilayer plots,
- 3D multilayer plots when supported,
- dependency matrices,
- cascade result plots.

Existing compatibility script:

```powershell
ns-visualize-multilayer --input-dir outputs\mln_demo --output-dir outputs\mln_demo\figures --modes multilayer2d,multilayer3d,dependency_matrix,summary
```

When optional 3D/interactive libraries are unavailable, visualization falls back to static outputs or explanatory HTML instead of crashing.
