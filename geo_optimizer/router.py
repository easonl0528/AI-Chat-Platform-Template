"""Routing logic that scores providers by latency, reliability, and cost."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from .config import ProviderConfig, RoutePolicy


@dataclass
class RouteDecision:
    provider: ProviderConfig
    score: float
    reason: str


def score_provider(provider: ProviderConfig, policy: RoutePolicy) -> float:
    latency_component = 1 / (provider.latency_ms + 1)
    success_component = provider.success_rate
    cost_component = 1 / (provider.cost_per_1k_tokens + 0.001)

    return (
        latency_component * policy.latency_weight
        + success_component * policy.success_weight
        + cost_component * policy.cost_weight
    )


def choose_provider(providers: Iterable[ProviderConfig], policy: RoutePolicy) -> Optional[RouteDecision]:
    best: Optional[RouteDecision] = None
    for provider in providers:
        if not provider.compliant:
            continue
        score = score_provider(provider, policy)
        reason = (
            f"latency={provider.latency_ms}ms, success_rate={provider.success_rate}, "
            f"cost={provider.cost_per_1k_tokens}/1k"
        )
        decision = RouteDecision(provider=provider, score=score, reason=reason)
        if best is None or decision.score > best.score:
            best = decision
    return best
