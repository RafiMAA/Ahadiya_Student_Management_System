import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    q = """
        SELECT t.id, t.full_name, t.contact, t.username, t.role, t.created_at,
               STRING_AGG('Grade ' || c.grade || ' ' || c.medium::TEXT || ' ' || c.gender_type::TEXT, ', ' ORDER BY c.grade) AS assigned_class_name
        FROM teachers t
        LEFT JOIN classes c ON c.teacher_id = t.id
            AND c.academic_year_id = (SELECT id FROM academic_years WHERE is_current = TRUE)
        GROUP BY t.id
    """
    try:
        rows = await db.fetch(q)
        print("Success, found rows:", len(rows))
    except Exception as e:
        print("Error:", e)

asyncio.run(main())
