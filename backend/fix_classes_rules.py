import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    y2026 = await db.fetchrow("SELECT id FROM academic_years WHERE year_label = '2026'")
    y2027 = await db.fetchrow("SELECT id FROM academic_years WHERE year_label = '2027'")
    if not y2026 or not y2027:
        print("Missing years")
        return
        
    old_year_id = y2026["id"]
    new_year_id = y2027["id"]
    
    # 1. Clone missing classes
    old_classes = await db.fetch("SELECT * FROM classes WHERE academic_year_id = $1", old_year_id)
    new_classes = await db.fetch("SELECT grade, medium, gender_type FROM classes WHERE academic_year_id = $1", new_year_id)
    
    new_sigs = {f"{nc['grade']}-{nc['medium']}-{nc['gender_type']}" for nc in new_classes}
    
    cloned = 0
    for oc in old_classes:
        sig = f"{oc['grade']}-{oc['medium']}-{oc['gender_type']}"
        if sig not in new_sigs:
            await db.execute(
                """INSERT INTO classes (grade, medium, gender_type, academic_year_id, teacher_id)
                   VALUES ($1, $2, $3, $4, $5)""",
                oc["grade"], oc["medium"], oc["gender_type"], new_year_id, oc.get("teacher_id")
            )
            cloned += 1
            new_sigs.add(sig)
    print(f"Cloned {cloned} missing classes.")
    
    # Re-fetch new classes to build complete map
    new_classes = await db.fetch("SELECT id, grade, medium, gender_type FROM classes WHERE academic_year_id = $1", new_year_id)
    new_class_by_sig = {f"{nc['grade']}-{nc['medium']}-{nc['gender_type']}": str(nc["id"]) for nc in new_classes}
    
    class_map = {}
    for oc in old_classes:
        sig = f"{oc['grade']}-{oc['medium']}-{oc['gender_type']}"
        if sig in new_class_by_sig:
            class_map[str(oc["id"])] = new_class_by_sig[sig]
            
    # 2. Clone missing rules
    old_rules = await db.fetch("SELECT * FROM promotion_rules WHERE academic_year_id = $1", old_year_id)
    rules_cloned = 0
    for r in old_rules:
        new_from = class_map.get(str(r["from_class_id"]))
        new_male = class_map.get(str(r["male_to_class_id"])) if r["male_to_class_id"] else None
        new_female = class_map.get(str(r["female_to_class_id"])) if r["female_to_class_id"] else None
        
        if new_from:
            exists = await db.fetchrow("SELECT id FROM promotion_rules WHERE from_class_id = $1 AND academic_year_id = $2", new_from, new_year_id)
            if not exists:
                await db.execute(
                    """INSERT INTO promotion_rules (from_class_id, male_to_class_id, female_to_class_id, academic_year_id)
                       VALUES ($1, $2, $3, $4)""",
                    new_from, new_male, new_female, new_year_id
                )
                rules_cloned += 1
                
    print(f"Cloned {rules_cloned} missing rules.")

asyncio.run(main())
