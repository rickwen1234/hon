# Architecture

The refactored package uses a `src/` layout:

- `network_science_project.hon`: sequential-data parsing, HON/Cog-HON rule extraction, HON network wiring, and diagnostics.
- `network_science_project.multilayer`: layer management, generated layers, dependency links, simplices, validation, import/export, and Peng input preparation.
  - `network_science_project.multilayer.strength`: shared event-driven strength updates for nodes, links, higher-order simplices, and inter-layer dependencies.
- `network_science_project.cascade`: Peng-style failure propagation and robustness metrics.
- `network_science_project.visualization`: plotting and presentation outputs.
- `network_science_project.experiments`: reproducible workflows that connect packages.
- `network_science_project.cli`: argparse dispatch only.

Legacy folders remain available for backward compatibility. New code should prefer imports from `network_science_project`.

## Responsibility Diagram

```mermaid
flowchart LR
  HON["hon: sequence parsing, rule extraction, network wiring"]
  ML["multilayer: layers, dependencies, simplices, dynamic strengths, export"]
  CAS["cascade: Peng failure dynamics and metrics"]
  VIS["visualization: plots and figures"]
  EXP["experiments: reproducible pipelines"]
  CLI["cli: argparse dispatch"]
  HON --> EXP
  ML --> EXP
  CAS --> EXP
  VIS --> EXP
  CLI --> EXP
```

## Import Direction

```mermaid
flowchart TD
  CLI --> EXP
  EXP --> HON
  EXP --> ML
  EXP --> CAS
  EXP --> VIS
  VIS --> ML
  VIS --> CASIO["cascade.io / CSV readers"]
  CAS --> MLREAD["prepared multilayer inputs"]
```

Forbidden boundaries:

- `hon` must not import `multilayer`, `cascade`, or `visualization`.
- `multilayer` must not import `hon`, `cascade`, or `visualization`.
- `cascade` must not import `hon` or `visualization`.
- `visualization` must not run simulations or generate networks.
