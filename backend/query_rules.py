import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    # get 2027 rules
    y2027 = await db.fetchval("SELECT id FROM academic_years WHERE year_label = '2027'")
    rules = await db.fetch("SELECT * FROM promotion_rules WHERE academic_year_id = $1", y2027)
    
    print(f"2027 Rules count: {len(rules)}")
    
    # check if there's a rule for Grade 6 Sinhala Boys
    c6 = await db.fetchrow("SELECT id FROM classes WHERE grade=6 AND medium='Sinhala' AND gender_type='Boys' AND academic_year_id=$1", y2027)
    if c6:
        rule6 = await db.fetchrow("SELECT * FROM promotion_rules WHERE from_class_id=$1", c6['id'])
        print("Grade 6 Rule:", dict(rule6) if rule6 else "None")
        
    c10 = await db.fetchrow("SELECT id FROM classes WHERE grade=10 AND medium='Sinhala' AND gender_type='Boys' AND academic_year_id=$1", y2027)
    if c10:
        rule10 = await db.fetchrow("SELECT * FROM promotion_rules WHERE from_class_id=$1", c10['id'])
        print("Grade 10 Rule:", dict(rule10) if rule10 else "None")

asyncio.run(main())
