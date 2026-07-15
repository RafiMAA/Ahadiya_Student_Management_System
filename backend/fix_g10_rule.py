import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    y2026 = await db.fetchrow("SELECT id FROM academic_years WHERE year_label = '2026'")
    y2027 = await db.fetchrow("SELECT id FROM academic_years WHERE year_label = '2027'")
    
    # Fix 2026
    c10_26 = await db.fetchrow("SELECT id FROM classes WHERE grade=10 AND medium='Sinhala' AND gender_type='Boys' AND academic_year_id=$1", y2026["id"])
    c11_26 = await db.fetchrow("SELECT id FROM classes WHERE grade=11 AND medium='Sinhala' AND gender_type='Boys' AND academic_year_id=$1", y2026["id"])
    
    if c10_26 and c11_26:
        await db.execute("UPDATE promotion_rules SET male_to_class_id = $1 WHERE from_class_id = $2", c11_26["id"], c10_26["id"])
        
    # Fix 2027
    c10_27 = await db.fetchrow("SELECT id FROM classes WHERE grade=10 AND medium='Sinhala' AND gender_type='Boys' AND academic_year_id=$1", y2027["id"])
    c11_27 = await db.fetchrow("SELECT id FROM classes WHERE grade=11 AND medium='Sinhala' AND gender_type='Boys' AND academic_year_id=$1", y2027["id"])
    
    if c10_27 and c11_27:
        await db.execute("UPDATE promotion_rules SET male_to_class_id = $1 WHERE from_class_id = $2", c11_27["id"], c10_27["id"])
        
    print("Fixed Grade 10 Sinhala Boys rules!")

asyncio.run(main())
