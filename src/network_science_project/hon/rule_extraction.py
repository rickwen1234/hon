"""Rule extraction API for original HON and memory-weighted Cog-HON."""

from __future__ import annotations

from typing import Any

from ._legacy import ensure_pyhon_path

ensure_pyhon_path()

import BuildRulesFastParameterFree as _rules  # noqa: E402


def extract_rules(
    trajectories: list,
    max_order: int,
    min_support: float,
    weighting_mode: str = "none",
    decay_mode: str = "exp",
    lambda_: float = 0.0,
    mu: float = 0.5,
    theta: float = 0.0,
    analysis_time: Any = None,
    support_type: str = "raw",
    output_diagnostics: bool = False,
):
    return _rules.ExtractRules(
        trajectories,
        max_order,
        min_support,
        weighting_mode=weighting_mode,
        decay_mode=decay_mode,
        lambda_=lambda_,
        mu=mu,
        theta=theta,
        analysis_time=analysis_time,
        support_type=support_type,
        output_diagnostics=output_diagnostics,
    )


def latest_rule_metadata() -> dict:
    return _rules.RuleMetadata


def latest_rule_diagnostics() -> list:
    return _rules.RuleDiagnostics
