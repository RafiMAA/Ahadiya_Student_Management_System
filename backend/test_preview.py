import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    y2027 = await db.fetchrow("SELECT id FROM academic_years WHERE year_label = '2027'")
    st = await db.fetch("SELECT s.full_name, c.grade, c.academic_year_id FROM students s JOIN classes c ON s.current_class_id = c.id WHERE c.academic_year_id = $1 AND s.status = 'Active'", y2027["id"])
    
    print("Students in 2027 classes:", [dict(x) for x in st])

asyncio.run(main())
