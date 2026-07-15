import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    currents = await db.fetch("SELECT id, year_label, is_current FROM academic_years WHERE is_current = TRUE")
    print("All current years:")
    for c in currents:
        print(dict(c))
        
    all_y = await db.fetch("SELECT id, year_label, is_current FROM academic_years")
    print("All years:")
    for y in all_y:
        print(dict(y))
        
asyncio.run(main())
