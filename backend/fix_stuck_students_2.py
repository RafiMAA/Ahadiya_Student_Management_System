import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    y2027 = await db.fetchrow("SELECT id FROM academic_years WHERE year_label = '2027'")
    
    # Map 2026 classes to 2027 classes
    c26 = await db.fetch("SELECT id, grade, medium, gender_type FROM classes WHERE academic_year_id IN (SELECT id FROM academic_years WHERE year_label = '2026')")
    c27 = await db.fetch("SELECT id, grade, medium, gender_type FROM classes WHERE academic_year_id = $1", y2027["id"])
    
    class_map = {} # old_target_id -> new_target_id
    for old_c in c26:
        for new_c in c27:
            if (old_c["grade"] == new_c["grade"] and 
                old_c["medium"] == new_c["medium"] and 
                old_c["gender_type"] == new_c["gender_type"]):
                class_map[str(old_c["id"])] = str(new_c["id"])
                break
                
    stuck_students = await db.fetch(
        "SELECT s.*, c.grade as c_grade FROM students s JOIN classes c ON s.current_class_id = c.id WHERE c.academic_year_id IN (SELECT id FROM academic_years WHERE year_label = '2026') AND s.status = 'Active'"
    )
    
    print(f"Found {len(stuck_students)} stuck students.")
    
    # We don't even need the rules, we know we want to PROMOTE them +1 grade!
    promoted = 0
    for s in stuck_students:
        old_grade = s["current_grade"]
        new_grade = old_grade + 1
        
        # find the 2027 class for their NEW grade
        # Wait! The target class for Grade 10 Sinhala Boys is Grade 11 Sinhala Boys
        target_class_2027 = None
        for nc in c27:
            if nc["grade"] == new_grade and nc["medium"] == s["medium"] and nc["gender_type"] == "Boys" if s["gender"] == "Male" else "Girls":
                target_class_2027 = str(nc["id"])
                break
                
        # If it's a mixed class... gender_type might be 'Mixed'
        if not target_class_2027:
            for nc in c27:
                if nc["grade"] == new_grade and nc["medium"] == s["medium"] and nc["gender_type"] == "Mixed":
                    target_class_2027 = str(nc["id"])
                    break
        
        if target_class_2027:
            await db.execute(
                "UPDATE students SET current_class_id = $1, current_grade = $2 WHERE id = $3",
                target_class_2027, new_grade, s["id"]
            )
            promoted += 1
            print(f"Promoted {s['full_name']} to class {target_class_2027}")
        else:
            print(f"Could not promote {s['full_name']}")

    print(f"Successfully promoted {promoted} students to 2027!")

asyncio.run(main())
