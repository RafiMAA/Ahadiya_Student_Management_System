"""One-off script to reset teacher passwords to proper bcrypt hashes."""
import asyncio
import asyncpg
import bcrypt

# ---  CONFIG  ---
DB_URL = "postgresql://postgres.ygeltuonvxnsrwnvbtvj:20031411Zearne66%40@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"
NEW_PASSWORD = "admin123"  # <-- change this to whatever you want
# ----------------


def hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


async def main():
    conn = await asyncpg.connect(DB_URL)

    rows = await conn.fetch("SELECT id, username, password_hash FROM teachers")
    print(f"\n--- Found {len(rows)} teachers ---")

    new_hash = hash_pw(NEW_PASSWORD)
    print(f"Generated new bcrypt hash: {new_hash}")
    print(f"Hash length: {len(new_hash)} (should be 60)\n")

    for r in rows:
        ph = r["password_hash"] or "(NULL)"
        is_valid = ph.startswith("$2") and len(ph) == 60
        print(f"  {r['username']:15s}  valid_hash={is_valid}  preview={ph[:30]}...")

        if not is_valid:
            await conn.execute(
                "UPDATE teachers SET password_hash = $1 WHERE id = $2",
                new_hash, r["id"],
            )
            print(f"    ✅ Fixed! New password: '{NEW_PASSWORD}'")

    await conn.close()
    print(f"\nDone! You can now login with password: '{NEW_PASSWORD}'")


if __name__ == "__main__":
    asyncio.run(main())
