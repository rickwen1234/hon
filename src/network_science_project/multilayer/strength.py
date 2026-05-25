"""Dynamic strength state for simplex-based activity and failure events."""

from __future__ import annotations

import itertools
import math
import random
from dataclasses import dataclass
from typing import Any, Iterable, Literal, Mapping, Sequence

SimplexKey = tuple[Any, ...]
EventScope = Literal["exact", "faces", "nodes", "closure"]
DecayMode = Literal["none", "exp", "power", "linear"]
StrengthScheme = Literal["peng_constant", "random_strength", "fixed_strength"]
RandomDistribution = Literal["normal", "uniform"]


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, float(value)))


def normalize_simplex(simplex: Sequence[Any]) -> SimplexKey:
    """Return a stable unordered key for a simplex."""
    if not simplex:
        raise ValueError("simplex must contain at least one element")
    key = tuple(sorted(tuple(simplex), key=lambda item: (str(type(item)), str(item))))
    if len(set(key)) != len(key):
        raise ValueError("simplex cannot contain repeated elements")
    return key


def simplex_dimension(simplex: Sequence[Any]) -> int:
    return len(simplex) - 1


def decay_factor(delta_t: float | None, mode: DecayMode = "exp", lambda_: float = 0.0) -> float:
    """Compute a bounded monotone decay factor."""
    if delta_t is None:
        return 1.0
    delta_t = max(0.0, float(delta_t))
    lambda_ = max(0.0, float(lambda_))
    if mode == "none":
        return 1.0
    if mode == "exp":
        return math.exp(max(-745.0, -lambda_ * delta_t))
    if mode == "power":
        return max(1.0, delta_t) ** (-lambda_)
    if mode == "linear":
        return max(0.0, 1.0 - lambda_ * delta_t)
    raise ValueError("Unknown decay mode: {0}".format(mode))


def impacted_simplices(
    simplex: Sequence[Any],
    scope: EventScope = "closure",
    rho: float = 1.0,
) -> list[tuple[SimplexKey, float]]:
    """Return impacted simplices with dimension-discounted coupling factors."""
    source = normalize_simplex(simplex)
    source_dim = simplex_dimension(source)
    rho = _clamp01(rho)

    if scope == "exact":
        keys = [source]
    elif scope == "nodes":
        keys = [source, *[(node,) for node in source]]
    elif scope == "faces":
        keys = [source]
        for size in range(2, len(source)):
            keys.extend(normalize_simplex(face) for face in itertools.combinations(source, size))
    elif scope == "closure":
        keys = []
        for size in range(1, len(source) + 1):
            keys.extend(normalize_simplex(face) for face in itertools.combinations(source, size))
    else:
        raise ValueError("Unknown event scope: {0}".format(scope))

    unique = sorted(set(keys), key=lambda key: (len(key), tuple(str(item) for item in key)))
    return [
        (key, rho ** max(0, source_dim - simplex_dimension(key)))
        for key in unique
    ]


@dataclass(frozen=True)
class StrengthEvent:
    simplex: SimplexKey
    time: float
    signal: float


@dataclass
class StrengthConfig:
    mu: float = 0.5
    eta: float = 0.5
    theta_active: float = 0.0
    lambda_: float = 0.0
    decay_mode: DecayMode = "exp"
    event_scope: EventScope = "closure"
    rho: float = 1.0
    initial_strength: float = 0.0


class StrengthState:
    """Track recoverable strengths for nodes, edges, and higher-order simplices."""

    def __init__(
        self,
        config: StrengthConfig | None = None,
        strengths: Mapping[Sequence[Any], float] | None = None,
        last_times: Mapping[Sequence[Any], float] | None = None,
    ) -> None:
        self.config = config or StrengthConfig()
        self.strengths: dict[SimplexKey, float] = {}
        self.last_times: dict[SimplexKey, float] = {}
        for simplex, strength in (strengths or {}).items():
            key = normalize_simplex(simplex)
            self.strengths[key] = _clamp01(strength)
        for simplex, time in (last_times or {}).items():
            self.last_times[normalize_simplex(simplex)] = float(time)

    def get_strength(self, simplex: Sequence[Any], at_time: float | None = None) -> float:
        key = normalize_simplex(simplex)
        strength = self.strengths.get(key, _clamp01(self.config.initial_strength))
        if at_time is None:
            return strength
        previous_time = self.last_times.get(key)
        return _clamp01(strength * decay_factor(
            None if previous_time is None else float(at_time) - previous_time,
            self.config.decay_mode,
            self.config.lambda_,
        ))

    def is_active(self, simplex: Sequence[Any], at_time: float | None = None) -> bool:
        return self.get_strength(simplex, at_time) >= _clamp01(self.config.theta_active)

    def apply_event(self, event: StrengthEvent) -> dict[SimplexKey, float]:
        if event.signal == 0:
            return {}
        changed: dict[SimplexKey, float] = {}
        magnitude = _clamp01(abs(event.signal))
        for key, coupling in impacted_simplices(event.simplex, self.config.event_scope, self.config.rho):
            decayed = self.get_strength(key, at_time=event.time)
            if event.signal > 0:
                effective_mu = _clamp01(self.config.mu * magnitude * coupling)
                updated = effective_mu + decayed * (1.0 - effective_mu)
            else:
                effective_eta = _clamp01(self.config.eta * magnitude * coupling)
                updated = decayed * (1.0 - effective_eta)
            self.strengths[key] = _clamp01(updated)
            self.last_times[key] = float(event.time)
            changed[key] = self.strengths[key]
        return changed

    def apply_events(self, events: Iterable[StrengthEvent]) -> None:
        for event in sorted(events, key=lambda item: item.time):
            self.apply_event(event)


@dataclass(frozen=True)
class InterlayerStrengthConfig:
    scheme: StrengthScheme = "peng_constant"
    q_global: float = 1.0
    sigma: float = 0.0
    distribution: RandomDistribution = "normal"
    seed: int | None = None
    fixed_value: float | None = None


def assign_interlayer_strengths(
    dependencies: Iterable[Sequence[Any]],
    config: InterlayerStrengthConfig,
) -> list[tuple[Any, Any, float]]:
    """Assign recoverable per-edge strengths without changing dependency topology."""
    rng = random.Random(config.seed)
    q_global = _clamp01(config.q_global)
    sigma = max(0.0, float(config.sigma))
    assigned: list[tuple[Any, Any, float]] = []
    for dependency in dependencies:
        if len(dependency) < 2:
            raise ValueError("dependency must include at least source and target nodes")
        source, target = dependency[0], dependency[1]
        if config.scheme == "peng_constant":
            strength = q_global
        elif config.scheme == "fixed_strength":
            strength = dependency[2] if len(dependency) >= 3 else config.fixed_value
            if strength is None:
                raise ValueError("fixed_strength requires dependency weight or fixed_value")
        elif config.scheme == "random_strength":
            if config.distribution == "normal":
                strength = rng.gauss(q_global, sigma)
            elif config.distribution == "uniform":
                strength = rng.uniform(q_global - sigma, q_global + sigma)
            else:
                raise ValueError("Unknown random distribution: {0}".format(config.distribution))
        else:
            raise ValueError("Unknown interlayer strength scheme: {0}".format(config.scheme))
        assigned.append((source, target, _clamp01(float(strength))))
    return assigned
