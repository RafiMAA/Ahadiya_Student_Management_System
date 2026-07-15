import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    y = await db.fetchrow("SELECT created_at FROM academic_years WHERE id = 'a0d7a438-e607-4c9e-9292-f82797e9a70f'")
    print("a0d7 created:", y['created_at'])

asyncio.run(main())
