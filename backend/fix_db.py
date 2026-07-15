import asyncio
import asyncpg
from app.config import get_settings
from datetime import date

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    # Update attendance records where the current_class_id doesn't match attendance class_id 
    # but they are in the current academic year.
    await db.execute("""
        UPDATE attendance a
        SET class_id = s.current_class_id
        FROM students s
        WHERE a.student_id = s.id 
        AND a.class_id != s.current_class_id 
        AND s.current_class_id IS NOT NULL
        AND a.attendance_date = $1
    """, date(2026, 6, 21))

asyncio.run(main())
