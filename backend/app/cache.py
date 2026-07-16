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
CURRENT_YEAR_ID = "current_academic_year_id"
TOTAL_ALUMNIS = "total_alumnis"
USER_PREFIX = "user:"


async def get_current_year_id(db) -> str | None:
    """Return the current academic year UUID, using cache to avoid repeated subqueries."""
    cached = cache_get(CURRENT_YEAR_ID)
    if cached is not None:
        return cached
    year_id = await db.fetchval("SELECT id FROM academic_years WHERE is_current = TRUE")
    if year_id is not None:
        cache_set(CURRENT_YEAR_ID, year_id, ttl=300)  # 5 min — rarely changes
    return year_id
