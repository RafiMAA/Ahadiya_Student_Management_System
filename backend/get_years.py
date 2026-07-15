import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    rows = await db.fetch("SELECT id, year_label, is_current FROM academic_years ORDER BY year_label")
    for r in rows:
        print(dict(r))

asyncio.run(main())
