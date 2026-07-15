import asyncio
import asyncpg
from app.config import get_settings
from datetime import date

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    q = """
        SELECT a.status, a.class_id, s.current_class_id, s.full_name
        FROM attendance a 
        JOIN students s ON a.student_id = s.id 
        WHERE a.attendance_date = $1
    """
    rows = await db.fetch(q, date(2026, 6, 21))
    for r in rows:
        print(dict(r))

asyncio.run(main())
