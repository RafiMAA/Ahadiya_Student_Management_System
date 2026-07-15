import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    y2027 = await db.fetchrow("SELECT id FROM academic_years WHERE year_label = '2027'")
    if not y2027:
        print("2027 not found")
        return
        
    classes = await db.fetch("SELECT grade, medium, gender_type FROM classes WHERE academic_year_id = $1 ORDER BY grade", y2027["id"])
    print(f"Total 2027 classes: {len(classes)}")
    for c in classes:
        print(dict(c))
        
    rules = await db.fetch("SELECT count(*) FROM promotion_rules WHERE academic_year_id = $1", y2027["id"])
    print(f"Total 2027 rules: {rules[0]['count']}")

asyncio.run(main())
