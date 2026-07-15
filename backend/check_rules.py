import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    # get 2030 rules
    y = await db.fetchrow("SELECT id FROM academic_years WHERE year_label = '2030'")
    rules = await db.fetch("""
        SELECT pr.*, 
               f.grade, f.medium, f.gender_type,
               m.grade as m_g, m.medium as m_m, m.gender_type as m_gt,
               fe.grade as f_g, fe.medium as f_m, fe.gender_type as f_gt
        FROM promotion_rules pr
        JOIN classes f ON pr.from_class_id = f.id
        LEFT JOIN classes m ON pr.male_to_class_id = m.id
        LEFT JOIN classes fe ON pr.female_to_class_id = fe.id
        WHERE pr.academic_year_id = $1
    """, y["id"])
    
    for r in rules:
        if r['grade'] >= 5 and r['grade'] <= 10 and r['medium'] == 'Sinhala':
            print(f"Grade {r['grade']} Sinhala {r['gender_type']} -> Male To: {r['m_g']} {r['m_m']} {r['m_gt']}, Female To: {r['f_g']} {r['f_m']} {r['f_gt']}")

asyncio.run(main())
