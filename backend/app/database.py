import json
import asyncpg
from app.config import get_settings

_pool: asyncpg.Pool | None = None


async def init_con(conn):
    await conn.set_type_codec(
        'jsonb',
        encoder=json.dumps,
        decoder=json.loads,
        schema='pg_catalog'
    )
    await conn.set_type_codec(
        'json',
        encoder=json.dumps,
        decoder=json.loads,
        schema='pg_catalog'
    )


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        settings = get_settings()
        _pool = await asyncpg.create_pool(
            dsn=settings.supabase_db_url,
            min_size=2,
            max_size=10,
            command_timeout=30,
            statement_cache_size=0,  # Supabase uses PgBouncer — no prepared statements
            setup=init_con
        )
    return _pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def get_db() -> asyncpg.Pool:
    """FastAPI dependency that returns the connection pool."""
    return await get_pool()
