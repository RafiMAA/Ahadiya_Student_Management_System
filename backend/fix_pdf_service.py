import asyncio
import asyncpg
from app.config import get_settings

async def main():
    s = get_settings()
    db = await asyncpg.create_pool(s.supabase_db_url)
    
    # Read pdf_service.py
    with open('app/services/pdf_service.py', 'r') as f:
        content = f.read()
        
    if "current_class_id = $1" in content:
        print("Found current_class_id query in pdf_service.py")
        
asyncio.run(main())
