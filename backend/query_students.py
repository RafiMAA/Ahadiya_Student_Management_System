import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    st = await db.fetch("SELECT id, full_name, current_class_id FROM students")
    for x in st:
        c = await db.fetchrow("SELECT academic_year_id, grade FROM classes WHERE id = $1", x['current_class_id'])
        y = await db.fetchrow("SELECT year_label FROM academic_years WHERE id = $1", c['academic_year_id']) if c else None
        print(x['full_name'], c['grade'] if c else None, y['year_label'] if y else None)

asyncio.run(main())
