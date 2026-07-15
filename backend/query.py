import asyncio
import asyncpg
from app.config import get_settings
import os

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    years = await db.fetch('SELECT id, year_label, is_current FROM academic_years ORDER BY year_label')
    print("Academic Years:")
    for y in years:
        print(dict(y))
        
    students = await db.fetch('SELECT id, full_name, current_class_id, current_grade FROM students')
    print("Students:")
    for s in students:
        print(dict(s))
        
    rules = await db.fetch('SELECT id, from_class_id, male_to_class_id, academic_year_id FROM promotion_rules')
    print("Rules:")
    for r in rules:
        print(dict(r))

asyncio.run(main())
