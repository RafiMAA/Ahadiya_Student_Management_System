import asyncio
import asyncpg
import os

from dotenv import load_dotenv
load_dotenv()

async def main():
    db_url = os.environ.get("SUPABASE_DB_URL")
    conn = await asyncpg.connect(db_url)
    with open("sql/004_trigram_indexes.sql", "r") as f:
        sql = f.read()
    await conn.execute(sql)
    await conn.close()
    print("Trigram indexes applied successfully!")

asyncio.run(main())
