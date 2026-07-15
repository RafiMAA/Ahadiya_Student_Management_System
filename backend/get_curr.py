import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    row = await db.fetchrow("SELECT * FROM academic_years WHERE is_current = TRUE")
    print(dict(row))

asyncio.run(main())
