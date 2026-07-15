import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    y2026 = await db.fetchrow("SELECT id FROM academic_years WHERE year_label = '2026'")
    y2027 = await db.fetchrow("SELECT id FROM academic_years WHERE year_label = '2027'")
    
    # Let's see the 2026 rule for Grade 10 Sinhala Boys
    g10_2026 = await db.fetchrow("SELECT id FROM classes WHERE grade=10 AND medium='Sinhala' AND gender_type='Boys' AND academic_year_id=$1", y2026["id"])
    if g10_2026:
        rule = await db.fetchrow("SELECT * FROM promotion_rules WHERE from_class_id=$1 AND academic_year_id=$2", g10_2026["id"], y2026["id"])
        print("2026 Rule:", dict(rule) if rule else None)
        
        if rule and rule["male_to_class_id"]:
            target_class = await db.fetchrow("SELECT grade, medium, gender_type FROM classes WHERE id=$1", rule["male_to_class_id"])
            print("2026 Target Class:", dict(target_class) if target_class else None)

    # Let's see the 2027 rule
    g10_2027 = await db.fetchrow("SELECT id FROM classes WHERE grade=10 AND medium='Sinhala' AND gender_type='Boys' AND academic_year_id=$1", y2027["id"])
    if g10_2027:
        rule27 = await db.fetchrow("SELECT * FROM promotion_rules WHERE from_class_id=$1 AND academic_year_id=$2", g10_2027["id"], y2027["id"])
        print("2027 Rule:", dict(rule27) if rule27 else None)

asyncio.run(main())
