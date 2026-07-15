import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    st = await db.fetchrow("SELECT created_at FROM students WHERE full_name = 'kokila'")
    print("kokila created:", st['created_at'])

asyncio.run(main())
