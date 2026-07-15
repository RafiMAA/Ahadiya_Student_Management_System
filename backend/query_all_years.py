import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    y = await db.fetch("SELECT id, year_label, is_current, created_at FROM academic_years ORDER BY created_at")
    for r in y:
        print(r['id'], r['year_label'], r['is_current'], r['created_at'])

asyncio.run(main())
