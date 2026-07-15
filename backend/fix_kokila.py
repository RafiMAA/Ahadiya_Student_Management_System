import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    await db.execute("UPDATE students SET current_class_id = '8736d851-45d1-4e4d-9c9e-26930073a15f' WHERE full_name = 'kokila'")
    print("Fixed kokila!")

asyncio.run(main())
