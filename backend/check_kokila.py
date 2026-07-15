import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    c = await db.fetchrow("SELECT grade, medium, gender_type, academic_year_id FROM classes WHERE id = '55e1e633-c5b1-4f40-8d3d-33d007df1e86'")
    y = await db.fetchrow("SELECT year_label FROM academic_years WHERE id = $1", c['academic_year_id'])
    print(dict(c), dict(y))
    
    # Also check rules for this class
    rules = await db.fetchrow("SELECT * FROM promotion_rules WHERE from_class_id = '55e1e633-c5b1-4f40-8d3d-33d007df1e86'")
    print("Rule:", dict(rules) if rules else "None")

asyncio.run(main())
