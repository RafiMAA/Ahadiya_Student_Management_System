import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    records = await db.fetch("SELECT * FROM attendance")
    print(f"Total attendance records: {len(records)}")
    for r in records:
        print(dict(r))

    print("Students in DB:")
    students = await db.fetch("SELECT id, full_name, current_class_id FROM students")
    for st in students:
        print(dict(st))
        
asyncio.run(main())
