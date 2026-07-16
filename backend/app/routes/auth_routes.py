from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg

from app.database import get_db
from app.auth import verify_password, create_access_token, get_current_user, hash_password
from app.models import LoginRequest, LoginResponse, UserProfile, ProfileUpdateRequest

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: asyncpg.Pool = Depends(get_db)):
    row = await db.fetchrow(
        "SELECT id, full_name, username, password_hash, role, status FROM teachers WHERE username = $1",
        body.username,
    )
    if not row:
        raise HTTPException(
            status_code=401, detail="Invalid username or password")
    if row["status"] == "Inactive":
        raise HTTPException(status_code=403, detail="Account is inactive")
    if not verify_password(body.password, row["password_hash"]):
        raise HTTPException(
            status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": str(row["id"]), "role": row["role"]})

    # Audit log
    await db.execute(
        "INSERT INTO audit_logs (action, details, performed_by) VALUES ($1, $2, $3)",
        "USER_LOGIN",
        {"username": row["username"]},
        row["id"],
    )

    return LoginResponse(
        access_token=token,
        role=row["role"],
        teacher_id=str(row["id"]),
        full_name=row["full_name"],
    )


@router.post("/logout")
async def logout(user: dict = Depends(get_current_user)):
    # Stateless JWT — client discards token. Log the action.
    return {"message": "Logged out successfully"}


@router.post("/refresh")
async def refresh_token(user: dict = Depends(get_current_user)):
    """Issue a fresh JWT using the current token's claims. No DB hit."""
    token = create_access_token({"sub": user["id"], "role": user["role"]})
    return {"access_token": token}


@router.get("/me", response_model=UserProfile)
async def get_me(
    user: dict = Depends(get_current_user),
    db: asyncpg.Pool = Depends(get_db),
):
    """Fetch the full user profile — this is the one endpoint that hits the DB for user details."""
    from app.cache import get_current_year_id
    year_id = await get_current_year_id(db)

    row = await db.fetchrow(
        """
        SELECT t.id, t.full_name, t.username, t.contact, t.address, t.role,
               ('Grade ' || c.grade || ' ' || c.medium::TEXT || ' ' || c.gender_type::TEXT) AS assigned_class
        FROM teachers t
        LEFT JOIN classes c ON c.teacher_id = t.id AND c.academic_year_id = $2
        WHERE t.id = $1
        """,
        user["id"], year_id,
    )
    if not row:
        raise HTTPException(status_code=401, detail="User not found")

    return UserProfile(
        id=str(row["id"]),
        full_name=row["full_name"],
        username=row["username"],
        contact=row["contact"],
        address=row["address"],
        role=row["role"],
        assigned_class=row["assigned_class"],
    )


@router.put("/profile", response_model=UserProfile)
async def update_profile(
    body: ProfileUpdateRequest,
    user: dict = Depends(get_current_user),
    db: asyncpg.Pool = Depends(get_db),
):
    updates = []
    values = []
    idx = 1
    
    if body.full_name is not None:
        updates.append(f"full_name = ${idx}")
        values.append(body.full_name)
        idx += 1
    if body.contact is not None:
        updates.append(f"contact = ${idx}")
        values.append(body.contact)
        idx += 1
    if body.address is not None:
        updates.append(f"address = ${idx}")
        values.append(body.address)
        idx += 1
    if body.username is not None:
        # Check uniqueness
        existing = await db.fetchval("SELECT id FROM teachers WHERE username = $1 AND id != $2", body.username, user["id"])
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
        updates.append(f"username = ${idx}")
        values.append(body.username)
        idx += 1
    if body.password is not None and body.password.strip():
        updates.append(f"password_hash = ${idx}")
        values.append(hash_password(body.password))
        idx += 1
        
    if not updates:
        # No changes — return current profile
        from app.cache import get_current_year_id
        year_id = await get_current_year_id(db)
        row = await db.fetchrow(
            """SELECT t.id, t.full_name, t.username, t.contact, t.address, t.role,
                      ('Grade ' || c.grade || ' ' || c.medium::TEXT || ' ' || c.gender_type::TEXT) AS assigned_class
               FROM teachers t
               LEFT JOIN classes c ON c.teacher_id = t.id AND c.academic_year_id = $2
               WHERE t.id = $1""",
            user["id"], year_id,
        )
        return UserProfile(
            id=str(row["id"]), full_name=row["full_name"], username=row["username"],
            contact=row["contact"], address=row["address"], role=row["role"],
            assigned_class=row["assigned_class"],
        )
        
    values.append(user["id"])
    query = f"UPDATE teachers SET {', '.join(updates)} WHERE id = ${idx} RETURNING id, full_name, username, contact, address, role"
    
    row = await db.fetchrow(query, *values)
    
    await db.execute(
        "INSERT INTO audit_logs (action, details, performed_by) VALUES ($1, $2, $3)",
        "PROFILE_UPDATED",
        {"updates": [k.split(" =")[0] for k in updates]},
        user["id"]
    )

    # Fetch assigned_class separately
    from app.cache import get_current_year_id
    year_id = await get_current_year_id(db)
    assigned_class = await db.fetchval(
        "SELECT ('Grade ' || grade || ' ' || medium::TEXT || ' ' || gender_type::TEXT) FROM classes WHERE teacher_id = $1 AND academic_year_id = $2",
        row["id"], year_id,
    )
    
    return UserProfile(
        id=str(row["id"]),
        full_name=row["full_name"],
        username=row["username"],
        contact=row["contact"],
        address=row["address"],
        role=row["role"],
        assigned_class=assigned_class,
    )
