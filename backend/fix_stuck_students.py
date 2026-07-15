import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    y2026 = await db.fetchrow("SELECT id FROM academic_years WHERE year_label = '2026'")
    y2027 = await db.fetchrow("SELECT id FROM academic_years WHERE year_label = '2027'")
    
    # Get 2026 rules
    rules_2026 = await db.fetch("SELECT * FROM promotion_rules WHERE academic_year_id = $1", y2026["id"])
    rule_map = {str(r["from_class_id"]): r for r in rules_2026}
    
    # Map 2026 class IDs to equivalent 2027 class IDs
    c26 = await db.fetch("SELECT id, grade, medium, gender_type FROM classes WHERE academic_year_id = $1", y2026["id"])
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
        "SELECT s.*, c.grade as c_grade FROM students s JOIN classes c ON s.current_class_id = c.id WHERE c.academic_year_id = $1 AND s.status = 'Active'",
        y2026["id"]
    )
    
    print(f"Found {len(stuck_students)} stuck students.")
    
    promoted = 0
    for s in stuck_students:
        class_id = str(s["current_class_id"])
        
        target_uuid = None
        if class_id in rule_map:
            rule = rule_map[class_id]
            target_uuid = rule["male_to_class_id"] if s["gender"] == "Male" else rule["female_to_class_id"]
            
        if target_uuid and str(target_uuid) in class_map:
            final_target_id = class_map[str(target_uuid)]
            new_grade = s["current_grade"] + 1
            await db.execute(
                "UPDATE students SET current_class_id = $1, current_grade = $2 WHERE id = $3",
                final_target_id, new_grade, s["id"]
            )
            promoted += 1
            print(f"Promoted {s['full_name']} to class {final_target_id}")
        else:
            print(f"Could not promote {s['full_name']} (target_uuid: {target_uuid})")

    print(f"Successfully promoted {promoted} students to 2027!")

asyncio.run(main())
