"""In-memory TTL cache for chat responses."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


class TTLCache:
    def __init__(self, ttl_seconds: int = 120):
        self.ttl = ttl_seconds
        self._store: Dict[str, CacheEntry] = {}

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry and entry.expires_at > time.time():
            return entry.value
        if entry:
            self._store.pop(key, None)
        return None

    def set(self, key: str, value: Any) -> None:
        self._store[key] = CacheEntry(value=value, expires_at=time.time() + self.ttl)

    def purge(self) -> None:
        now = time.time()
        expired = [key for key, entry in self._store.items() if entry.expires_at <= now]
        for key in expired:
            self._store.pop(key, None)


def build_cache(enabled: bool, ttl_seconds: int) -> Optional[TTLCache]:
    return TTLCache(ttl_seconds=ttl_seconds) if enabled else None
