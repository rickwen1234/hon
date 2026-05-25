"""Temporal weighting helpers for memory-aware HON rule extraction."""

from __future__ import division

from datetime import datetime
import math


def parse_timestamp(value):
    """Return a numeric timestamp from a number or ISO-like datetime string."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        pass

    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text).timestamp()
    except AttributeError:
        formats = (
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        )
        for fmt in formats:
            try:
                return (datetime.strptime(text, fmt) - datetime(1970, 1, 1)).total_seconds()
            except ValueError:
                pass
    except ValueError:
        pass
    raise ValueError("Cannot parse timestamp: {0}".format(value))


def decay_weight(delta_t, mode, lambda_, epsilon=1e-12):
    """Compute a stable forgetting weight for an elapsed time delta."""
    if delta_t is None:
        return 1.0
    delta_t = max(0.0, float(delta_t))
    lambda_ = max(0.0, float(lambda_))

    if mode == "none":
        return 1.0
    if mode == "exp":
        exponent = max(-745.0, -lambda_ * delta_t)
        return max(epsilon, math.exp(exponent))
    if mode == "power":
        return max(epsilon, max(1.0, delta_t) ** (-lambda_))
    if mode == "linear":
        return max(0.0, 1.0 - lambda_ * delta_t)
    raise ValueError("Unknown decay mode: {0}".format(mode))


def cogsnet_update(previous_weight, delta_t, mu, theta, lambda_, mode):
    """Apply CogSNet-style decay and reinforcement to one memory trace.

    The prior trace first decays according to ``mode``. If the decayed trace
    falls below ``theta`` it is reset to ``mu``; otherwise the new observation
    reinforces it with ``mu + decayed_weight * (1 - mu)``.
    """
    previous_weight = max(0.0, float(previous_weight or 0.0))
    mu = min(1.0, max(0.0, float(mu)))
    theta = max(0.0, float(theta))
    decayed = previous_weight * decay_weight(delta_t, mode, lambda_)
    if decayed < theta:
        return mu
    return mu + decayed * (1.0 - mu)
