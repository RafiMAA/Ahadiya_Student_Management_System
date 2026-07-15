import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    classes = await db.fetch("""
        SELECT c.id, c.grade, c.medium, c.gender_type, c.academic_year_id, ay.year_label, ay.is_current
        FROM classes c
        JOIN academic_years ay ON c.academic_year_id = ay.id
    """)
    class_map = {str(c['id']): dict(c) for c in classes}
    
    students = await db.fetch("SELECT id, full_name, current_class_id FROM students")
    for st in students:
        if st['current_class_id']:
            cid = str(st['current_class_id'])
            cinfo = class_map.get(cid)
            print(f"{st['full_name']} -> {cinfo['grade']} {cinfo['medium']} {cinfo['gender_type']} ({cinfo['year_label']}) [Current? {cinfo['is_current']}]")
        else:
            print(f"{st['full_name']} -> Unassigned")
            
asyncio.run(main())
