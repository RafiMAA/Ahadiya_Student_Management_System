import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    y = await db.fetch("SELECT id, year_label, is_current FROM academic_years")
    for r in y:
        print(dict(r))

asyncio.run(main())
