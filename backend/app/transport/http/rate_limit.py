"""Rate limiting: per-route and global limits, cooldown on exceed.

Storage:
- Global/per-route counters: in-memory backend of the `limits` library (used by
  slowapi). Key = client identifier (by default IP from get_remote_address).
  Stored per process; with multiple workers each has its own view (no shared state).
- Cooldown state: in-memory dict `_cooldown_until` (key = IP, value = monotonic
  timestamp until which the client is blocked). Expired entries are removed on
  next get_retry_after() for that key.

Performance:
- Lookups/updates are O(1). Memory grows with number of distinct IPs that have
  hit the limit or are in cooldown; after cooldown expires the key is removed.
- Under very high concurrency (many distinct IPs), consider moving slowapi
  storage to Redis (Limiter(..., storage_uri=settings.REDIS_URI)) and
  cooldown to Redis as well, so that memory stays bounded and state is shared
  across workers.
"""
from __future__ import annotations

import time
from typing import MutableMapping

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_GLOBAL],
)

_cooldown_until: MutableMapping[str, float] = {}

PER_ROUTE_LIMIT = settings.RATE_LIMIT_PER_ROUTE


def set_cooldown(key: str) -> None:
    _cooldown_until[key] = time.monotonic() + settings.RATE_LIMIT_COOLDOWN_SECONDS


def get_retry_after(key: str) -> int | None:
    until = _cooldown_until.get(key)
    if until is None:
        return None
    now = time.monotonic()
    if now >= until:
        del _cooldown_until[key]
        return None
    return max(1, int(until - now))
