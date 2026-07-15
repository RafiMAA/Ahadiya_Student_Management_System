import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    st = await db.fetch("SELECT full_name, status, current_grade, current_class_id FROM students")
    print("All students:")
    for x in st:
        print(dict(x))

asyncio.run(main())
