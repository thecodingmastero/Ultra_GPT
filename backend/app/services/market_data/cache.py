"""Simple in-memory TTL cache for market data responses.

Reduces redundant Finnhub API calls and improves latency for repeated
symbol lookups within the same process lifetime.
"""
from __future__ import annotations

import time
from threading import Lock
from typing import Any


class TTLCache:
    """Thread-safe dictionary cache where entries expire after *ttl* seconds."""

    def __init__(self, ttl: float = 60.0) -> None:
        self._ttl = ttl
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = Lock()

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if time.monotonic() > expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._store[key] = (value, time.monotonic() + self._ttl)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._store)
