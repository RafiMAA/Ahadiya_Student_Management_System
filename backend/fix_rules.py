import asyncio
import asyncpg
from app.config import get_settings
import os

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    # get 2026 and 2027 ids
    y2026 = await db.fetchrow("SELECT id FROM academic_years WHERE year_label = '2026'")
    y2027 = await db.fetchrow("SELECT id FROM academic_years WHERE year_label = '2027'")
    if not y2026 or not y2027:
        print("Missing years")
        return
        
    old_year_id = y2026["id"]
    new_year_id = y2027["id"]
    
    # build class map
    old_classes = await db.fetch("SELECT id, grade, medium, gender_type FROM classes WHERE academic_year_id = $1", old_year_id)
    new_classes = await db.fetch("SELECT id, grade, medium, gender_type FROM classes WHERE academic_year_id = $1", new_year_id)
    
    new_class_by_sig = {f"{nc['grade']}-{nc['medium']}-{nc['gender_type']}": str(nc["id"]) for nc in new_classes}
    class_map = {}
    for oc in old_classes:
        sig = f"{oc['grade']}-{oc['medium']}-{oc['gender_type']}"
        if sig in new_class_by_sig:
            class_map[str(oc["id"])] = new_class_by_sig[sig]
            
    # get old rules
    old_rules = await db.fetch("SELECT * FROM promotion_rules WHERE academic_year_id = $1", old_year_id)
    
    for r in old_rules:
        new_from = class_map.get(str(r["from_class_id"]))
        new_male = class_map.get(str(r["male_to_class_id"])) if r["male_to_class_id"] else None
        new_female = class_map.get(str(r["female_to_class_id"])) if r["female_to_class_id"] else None
        
        if new_from:
            # check if exists
            exists = await db.fetchrow("SELECT id FROM promotion_rules WHERE from_class_id = $1 AND academic_year_id = $2", new_from, new_year_id)
            if not exists:
                await db.execute(
                    """INSERT INTO promotion_rules (from_class_id, male_to_class_id, female_to_class_id, academic_year_id)
                       VALUES ($1, $2, $3, $4)""",
                    new_from, new_male, new_female, new_year_id
                )
    print("Rules cloned!")

asyncio.run(main())
