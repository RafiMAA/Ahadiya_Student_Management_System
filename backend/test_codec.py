import asyncio
import asyncpg
import json
from app.config import get_settings

async def main():
    settings = get_settings()
    async def init_con(conn):
        await conn.set_type_codec(
            'jsonb',
            encoder=json.dumps,
            decoder=json.loads,
            schema='pg_catalog'
        )

    pool = await asyncpg.create_pool(dsn=settings.supabase_db_url, setup=init_con)
    async with pool.acquire() as conn:
        try:
            await conn.execute("INSERT INTO audit_logs (action, details, performed_by) VALUES ($1, $2, $3)", 
                "TEST_ACT", {"foo": "bar"}, "t0000000-0000-0000-0000-000000000001")
            print("SUCCESS without ::jsonb")
        except Exception as e:
            print("FAIL:", type(e).__name__, e)

asyncio.run(main())
