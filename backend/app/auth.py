from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
import asyncpg

from app.config import get_settings
from app.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.jwt_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: asyncpg.Pool = Depends(get_db),
) -> dict:
    """Extract and validate the current user from JWT token."""
    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    row = await db.fetchrow(
        """
        SELECT t.id, t.full_name, t.username, t.contact, t.address, t.role, t.status,
               ('Grade ' || c.grade || ' ' || c.medium::TEXT || ' ' || c.gender_type::TEXT) AS assigned_class
        FROM teachers t
        LEFT JOIN classes c ON c.teacher_id = t.id
            AND c.academic_year_id = (SELECT id FROM academic_years WHERE is_current = TRUE)
        WHERE t.id = $1
        """,
        user_id,
    )
    if not row:
        raise HTTPException(status_code=401, detail="User not found")
    if row["status"] == "Inactive":
        raise HTTPException(status_code=403, detail="Account is inactive")

    return {
        "id": str(row["id"]),
        "full_name": row["full_name"],
        "username": row["username"],
        "contact": row["contact"],
        "address": row["address"],
        "role": row["role"],
        "assigned_class": row["assigned_class"],
    }


def require_role(*roles: str):
    """Dependency factory that requires the user to have one of the specified roles."""
    async def checker(user: dict = Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(roles)}",
            )
        return user
    return checker


# Convenience dependencies
require_admin = require_role("Principal", "Admin", "Super Admin")
require_principal = require_role("Principal")
require_super_admin = require_role("Super Admin")
require_any_auth = require_role("Principal", "Admin", "Teacher", "Super Admin")
