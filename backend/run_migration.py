"""Run a SQL migration file against the database."""
import asyncio
import asyncpg
import sys
import os

# Load env manually
from dotenv import load_dotenv
load_dotenv()

async def run_migration(sql_file: str):
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        print("ERROR: SUPABASE_DB_URL not set in .env")
        sys.exit(1)

    with open(sql_file, 'r') as f:
        sql = f.read()

    conn = await asyncpg.connect(db_url)
    try:
        await conn.execute(sql)
        print(f"✅ Migration {sql_file} executed successfully!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)
    finally:
        await conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_migration.py <sql_file>")
        sys.exit(1)
    asyncio.run(run_migration(sys.argv[1]))
