from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    supabase_db_url: str = "postgresql://postgres:password@localhost:5432/postgres"

    # JWT
    jwt_secret: str = "change-me-to-a-32-char-minimum-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30  # 30 min — shorter TTL since auth is pure-JWT (no DB revocation check)

    # PDF
    pdf_school_name: str = "Ahadiya School"

    # CORS
    cors_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
