import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    date = '2026-06-21'
    q = """
        SELECT a.status, a.class_id, s.current_class_id, s.id
        FROM attendance a 
        JOIN classes c ON a.class_id = c.id 
        JOIN students s ON a.student_id = s.id 
        WHERE a.attendance_date = $1 AND c.academic_year_id = (SELECT id FROM academic_years WHERE is_current = TRUE)
    """
    rows = await db.fetch(q, date)
    print("Without filtering current_class_id:")
    for r in rows:
        print(dict(r))
        
    q2 = """
        SELECT a.status, a.class_id, s.current_class_id 
        FROM attendance a 
        JOIN classes c ON a.class_id = c.id 
        JOIN students s ON a.student_id = s.id AND s.current_class_id = a.class_id
        WHERE a.attendance_date = $1 AND c.academic_year_id = (SELECT id FROM academic_years WHERE is_current = TRUE)
    """
    rows2 = await db.fetch(q2, date)
    print("With filtering current_class_id:")
    for r in rows2:
        print(dict(r))

asyncio.run(main())
