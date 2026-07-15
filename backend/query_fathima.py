import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    st = await db.fetchrow("SELECT status FROM students WHERE full_name = 'Fathima Zahra'")
    print(st['status'])

asyncio.run(main())
