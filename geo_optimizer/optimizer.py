"""High-level orchestrator combining routing, compliance, and caching."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Dict, Optional

from .cache import TTLCache, build_cache
from .compliance import ComplianceResult, run_compliance_pipeline
from .config import OptimizerConfig, ProviderConfig
from .router import RouteDecision, choose_provider


@dataclass
class OptimizerOutput:
    decision: RouteDecision
    prompt: str
    compliance: ComplianceResult
    cached: bool
    cached_response: Optional[str]


class GeoOptimizer:
    def __init__(self, config: OptimizerConfig):
        self.config = config
        self.cache = build_cache(config.enable_cache, config.cache_ttl_seconds)

    def _cache_key(self, prompt: str) -> str:
        fingerprint = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        return f"prompt:{fingerprint}"

    def run(self, prompt: str) -> OptimizerOutput:
        compliance = run_compliance_pipeline(prompt, enable_rewrite=self.config.enable_rewrites)
        if compliance.rejected:
            raise ValueError("Prompt rejected by compliance policy")

        routed = choose_provider(self.config.providers, self.config.policy)
        if routed is None:
            raise ValueError("No compliant providers available")

        cached_response: Optional[str] = None
        cached = False
        if self.cache:
            cached_response = self.cache.get(self._cache_key(compliance.filtered_text))
            cached = cached_response is not None

        return OptimizerOutput(
            decision=routed,
            prompt=compliance.filtered_text,
            compliance=compliance,
            cached=cached,
            cached_response=cached_response,
        )

    def record_response(self, prompt: str, response: str) -> None:
        if self.cache:
            self.cache.set(self._cache_key(prompt), response)
