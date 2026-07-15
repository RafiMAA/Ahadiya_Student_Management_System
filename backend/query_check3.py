import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    classes = await db.fetch("SELECT id, grade, medium, gender_type FROM classes")
    for c in classes:
        if str(c['id']) in ['55e1e633-c5b1-4f40-8d3d-33d007df1e86', 'c0000000-0000-0000-0000-000000000003']:
            print(f"{c['id']} -> Grade {c['grade']} {c['medium']} {c['gender_type']}")

asyncio.run(main())
