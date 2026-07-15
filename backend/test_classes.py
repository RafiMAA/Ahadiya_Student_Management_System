import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    c = await db.fetch("SELECT id, grade, medium, gender_type FROM classes WHERE academic_year_id = (SELECT id FROM academic_years WHERE is_current = TRUE)")
    print(f"Current year classes ({len(c)}):")
    for r in c:
        print(dict(r))

asyncio.run(main())
