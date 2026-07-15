import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    y2026 = await db.fetchrow("SELECT id FROM academic_years WHERE year_label = '2026'")
    y2027 = await db.fetchrow("SELECT id FROM academic_years WHERE year_label = '2027'")
    
    print("2026 G11 Sinhala Classes:")
    c26 = await db.fetch("SELECT grade, medium, gender_type FROM classes WHERE grade=11 AND medium='Sinhala' AND academic_year_id=$1", y2026["id"])
    for c in c26: print(dict(c))

    print("2027 G11 Sinhala Classes:")
    c27 = await db.fetch("SELECT grade, medium, gender_type FROM classes WHERE grade=11 AND medium='Sinhala' AND academic_year_id=$1", y2027["id"])
    for c in c27: print(dict(c))

asyncio.run(main())
