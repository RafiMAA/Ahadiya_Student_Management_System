"""
Simple TTL (time-to-live) in-memory cache.

Used to avoid repeated round trips to Supabase for slow-changing data
like student counts, teacher counts, and the current academic year.
"""

import time
from typing import Any

_cache: dict[str, tuple[Any, float]] = {}

DEFAULT_TTL = 60  # seconds


def cache_get(key: str) -> Any | None:
    """Return cached value if it exists and hasn't expired, else None."""
    entry = _cache.get(key)
    if entry is None:
        return None
    value, expires_at = entry
    if time.monotonic() > expires_at:
        _cache.pop(key, None)
        return None
    return value


def cache_set(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    """Store a value in the cache with a TTL in seconds."""
    _cache[key] = (value, time.monotonic() + ttl)


def cache_invalidate(*keys: str) -> None:
    """Remove one or more keys from the cache."""
    for key in keys:
        _cache.pop(key, None)


def cache_invalidate_prefix(prefix: str) -> None:
    """Remove all keys that start with the given prefix."""
    to_remove = [k for k in _cache if k.startswith(prefix)]
    for k in to_remove:
        del _cache[k]


# Convenience keys
TOTAL_STUDENTS = "total_students"
TOTAL_TEACHERS = "total_teachers"
TOTAL_CLASSES = "total_classes"
CURRENT_YEAR = "current_academic_year"
TOTAL_ALUMNIS = "total_alumnis"
