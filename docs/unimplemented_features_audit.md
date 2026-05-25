# Unimplemented Feature Audit

This audit checks the current `src/network_science_project` implementation
against the expected project behavior discussed for temporal HON links,
simplicial interactions, and Peng-style multilayer cascades.

## Implemented

- Memory-aware HON rule extraction exists through the legacy-backed HON wrapper.
  It supports `none`, `decay`, and `cogsnet` weighting modes, multiple decay
  functions, weighted support, and diagnostics.
- Basic multilayer network construction exists for generated layers, edge-list
  layers, HON edge-list layers, dependency links, triangle simplices, validation,
  export, and import.
- Peng-style cascade baseline exists for two layers with initial node failure,
  same-layer triangle propagation, binary cross-layer dependency propagation,
  and giant-component metrics.
- `network_science_project.multilayer.strength` now provides an independent
  recoverable strength state for event-driven node, edge, simplex, and
  inter-layer dependency strengths.

## Partially Implemented

- 2-simplex support is limited to triangles. Triangle generation, detection, IO,
  visualization, and cascade propagation exist, but simplex weights are written
  as `1.0` and ignored by the cascade rule.
- Inter-layer dependencies store a `weight` field, and `from_file` can read it,
  but current cascade propagation ignores that field.
- Dependency generation supports several topology modes:
  `random_matching`, `same_id`, `degree_assortative`, `weight_based`, and
  `from_file`. Most generated modes still assign dependency strength `1.0`.
- The new dynamic strength module supports `peng_constant`, `random_strength`,
  and `fixed_strength`, but this has not yet been wired into multilayer build
  specs, exported files, or the cascade simulation.

## Not Yet Integrated

- Peng cascade does not yet use threshold strength triggering. It still treats
  every dependency link as a deterministic binary failure channel.
- `q` is still used by dependency generation as topology density in
  `MultiLayerNetwork.add_dependency`. It is not yet separated into:
  - dependency topology density, and
  - Peng-style global expected link influence.
- The cascade config does not yet carry `theta_active`, `mu`, `eta`, `lambda`,
  `decay_mode`, `event_scope`, `rho`, or inter-layer strength scheme settings.
- Event streams `e(simplex, t, signal)` are not yet parsed from files, exported,
  or consumed by HON/multilayer/cascade workflows.
- HON temporal strengthening has its own CogSNet/decay implementation and does
  not yet reuse `multilayer.strength`.
- CLI commands do not expose dynamic strength options or event-input files.

## Not Implemented

- Higher-dimensional simplex storage is not generalized beyond 2-simplex
  triangles. Current IO schemas and `MultiLayerNetwork.simplices` assume
  triples.
- Higher-dimensional simplex generators are not implemented.
- Higher-dimensional simplex visualization is not implemented.
- Higher-dimensional simplex cascade propagation is not integrated. There is an
  older `high_order_simplex_failures` helper in `cascade.failure_rules`, but it
  is not used by the simulation or exposed through input formats.
- Recoverable inactive dependencies are not yet represented in the cascade
  runtime. Current dependencies do not decay, weaken, or recover during
  simulation.
- Fixed-strength and random-strength inter-layer schemes are not yet available
  from CLI/config specs.
- Strength-triggered negative events from cascade failures are not yet emitted
  back into the dynamic strength state.

## Legacy Documentation Gaps

- The root README still contains original `pyHON` documentation that says some
  Python preprocessing filters are not implemented:
  `min-length-of-trajectory`, `max-length-of-trajectory`, `filter-bots`, and
  configurable `distance-method`. These appear to be legacy notes, not features
  in the refactored `src` package.
- The refactor report explicitly says deeper cleanup of legacy HON internals is
  future work.

## Environment Blocker

- Local verification is blocked because the current `python` and `py` commands
  point to an unusable Windows Store Python installation. Tests could not be
  executed in this environment.
