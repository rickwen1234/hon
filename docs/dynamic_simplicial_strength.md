# Dynamic Simplicial Strength

`network_science_project.multilayer.strength` defines the shared state update
layer for activity-enhanced HON links, simplicial interactions, and inter-layer
dependency strengths.

## Event Model

Events use one form:

```text
e(simplex, t, signal)
```

- `simplex`: node, edge, 2-simplex, or higher-order simplex.
- `t`: event time.
- `signal > 0`: activity or reinforcement.
- `signal < 0`: failure or negative trigger.

The state variable `s_x(t)` is recoverable. If strength falls below an active
threshold it is inactive for that step, but it can be strengthened by later
positive events.

## Update Rule

For each affected simplex, the previous strength is first decayed:

```text
s(t-) = s(t_last) * f(t - t_last)
```

Positive events reinforce:

```text
s(t) = mu_eff + s(t-) * (1 - mu_eff)
```

Negative events weaken:

```text
s(t) = s(t-) * (1 - eta_eff)
```

`mu_eff` and `eta_eff` are scaled by event magnitude and any dimensional
coupling factor.

## Event Scope

The same scope applies to positive and negative events:

- `exact`: only the supplied simplex.
- `faces`: the simplex and lower-dimensional non-node faces.
- `nodes`: the simplex and its nodes.
- `closure`: the simplex, all faces, and all nodes.

The default design target is `closure`.

## Dimension Discount

When an event propagates from a higher-order simplex to a lower-dimensional
face, its coupling is discounted:

```text
coupling = rho^(dim_source - dim_target)
```

For example, with `rho = 0.5`, a triangle event reaches edges with `0.5` and
nodes with `0.25`.

## Inter-Layer Strength Schemes

The module assigns per-link inter-layer strengths without changing dependency
topology:

- `peng_constant`: every dependency receives `q_global`.
- `random_strength`: strengths are sampled around `q_global` with spread
  controlled by `sigma`.
- `fixed_strength`: strengths come from dependency records or a fixed value.

`q_global` remains the global expected link influence control. It is not mixed
with topology density.
