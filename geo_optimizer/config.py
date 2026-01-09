"""Configuration utilities for GEO optimizer."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ProviderConfig:
    """Basic configuration for a single provider."""

    name: str
    endpoint: str
    latency_ms: float
    success_rate: float
    cost_per_1k_tokens: float
    region: str = "cn-mainland"
    supports_streaming: bool = True
    compliant: bool = True

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "ProviderConfig":
        return cls(**payload)


@dataclass
class RoutePolicy:
    """Routing knobs used to balance speed, reliability, and cost."""

    latency_weight: float = 0.5
    success_weight: float = 0.3
    cost_weight: float = 0.2


@dataclass
class OptimizerConfig:
    """Top-level configuration for the optimizer."""

    providers: List[ProviderConfig]
    policy: RoutePolicy
    enable_cache: bool = True
    cache_ttl_seconds: int = 120
    enable_compliance_checks: bool = True
    enable_rewrites: bool = True


DEFAULT_CONFIG = {
    "providers": [
        {
            "name": "doubao",
            "endpoint": "https://api.doubao.com/chat",
            "latency_ms": 220,
            "success_rate": 0.97,
            "cost_per_1k_tokens": 0.8,
            "supports_streaming": True,
        },
        {
            "name": "wenxinyiyan",
            "endpoint": "https://wenxin.baidu.com/chat",
            "latency_ms": 280,
            "success_rate": 0.95,
            "cost_per_1k_tokens": 0.6,
            "supports_streaming": True,
        },
        {
            "name": "tongyiqianwen",
            "endpoint": "https://dashscope.aliyuncs.com/chat",
            "latency_ms": 260,
            "success_rate": 0.96,
            "cost_per_1k_tokens": 0.7,
            "supports_streaming": True,
        },
    ],
    "policy": {"latency_weight": 0.45, "success_weight": 0.35, "cost_weight": 0.2},
    "enable_cache": True,
    "cache_ttl_seconds": 90,
    "enable_compliance_checks": True,
    "enable_rewrites": True,
}


def load_providers(path: Optional[Path]) -> List[ProviderConfig]:
    """Load provider definitions from JSON, falling back to defaults."""

    if path is None or not path.exists():
        raw = DEFAULT_CONFIG["providers"]
    else:
        raw = json.loads(path.read_text())
    return [ProviderConfig.from_dict(entry) for entry in raw]


def load_optimizer_config(path: Optional[Path]) -> OptimizerConfig:
    """Load optimizer configuration or fallback to defaults."""

    if path is None or not path.exists():
        config_raw = DEFAULT_CONFIG
    else:
        config_raw = json.loads(path.read_text())

    providers = [ProviderConfig.from_dict(entry) for entry in config_raw["providers"]]
    policy = RoutePolicy(**config_raw["policy"])

    return OptimizerConfig(
        providers=providers,
        policy=policy,
        enable_cache=config_raw.get("enable_cache", True),
        cache_ttl_seconds=config_raw.get("cache_ttl_seconds", 120),
        enable_compliance_checks=config_raw.get("enable_compliance_checks", True),
        enable_rewrites=config_raw.get("enable_rewrites", True),
    )
