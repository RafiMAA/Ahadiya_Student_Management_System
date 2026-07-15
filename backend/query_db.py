import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    y = await db.fetch("SELECT * FROM academic_years")
    print(y)

asyncio.run(main())
