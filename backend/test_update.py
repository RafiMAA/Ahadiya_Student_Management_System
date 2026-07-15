import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    await db.execute("UPDATE academic_years SET year_label = '2025' WHERE is_current = TRUE")
    print("Updated to 2025")

asyncio.run(main())
