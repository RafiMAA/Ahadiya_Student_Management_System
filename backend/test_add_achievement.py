import asyncio
import asyncpg
from app.config import get_settings

async def test():
    s = get_settings()
    conn = await asyncpg.connect(dsn=s.supabase_db_url)
    
    # get a student
    student = await conn.fetchrow("SELECT id FROM students LIMIT 1")
    if not student:
        print("No student")
        return
        
    year = await conn.fetchrow("SELECT id, year_label FROM academic_years WHERE is_current = TRUE")
    if not year:
        print("No year")
        return
        
    user = await conn.fetchrow("SELECT id FROM teachers LIMIT 1")
    
    # insert
    row = await conn.fetchrow(
        """INSERT INTO student_achievements (student_id, academic_year_id, grade, achievement_text, created_by)
           VALUES ($1, $2, $3, $4, $5) RETURNING *""",
        student["id"], year["id"], 1, "Test achievement", user["id"]
    )
    
    print(dict(row))
    await conn.close()

asyncio.run(test())
