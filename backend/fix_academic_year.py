import asyncio
import asyncpg
from app.config import get_settings
from datetime import date

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    # set 2027 start_date to today
    await db.execute("UPDATE academic_years SET start_date = $1 WHERE year_label = '2027'", date.today())
    print("Fixed 2027 start date!")

asyncio.run(main())
