"""
Buddhist Affairs MIS Dashboard - Configuration Settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator
from functools import lru_cache
from typing import Optional
from pathlib import Path

# Resolve .env relative to this file: backend/app/config.py → backend/.env
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    """
    Application settings.
    Values are loaded in priority order:
      1. Actual environment variables (Railway injects these automatically)
      2. .env file (local development fallback)
      3. Default values defined below (only for non-sensitive settings)
    """

    # Application
    APP_NAME: str = "Buddhist Affairs MIS Dashboard"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Database ─────────────────────────────────────────────
    # Individual fields are optional when DATABASE_URL / DATABASE_URL_OVERRIDE
    # is supplied (Railway Postgres plugin injects DATABASE_URL automatically).
    DB_HOST: Optional[str] = Field(None, description="PostgreSQL host")
    DB_PORT: int = Field(5432, description="PostgreSQL port")
    DB_NAME: Optional[str] = Field(None, description="PostgreSQL database name")
    DB_USER: Optional[str] = Field(None, description="PostgreSQL user")
    DB_PASSWORD: Optional[str] = Field(None, description="PostgreSQL password")

    # Full URL override — Railway Postgres plugin sets DATABASE_URL automatically
    DATABASE_URL_OVERRIDE: Optional[str] = Field(None, alias="DATABASE_URL", validation_alias="DATABASE_URL")

    @model_validator(mode="after")
    def check_db_config(self) -> "Settings":
        """Ensure either DATABASE_URL or individual DB fields are provided."""
        if not self.DATABASE_URL_OVERRIDE:
            missing = [f for f in ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD")
                       if not getattr(self, f)]
            if missing:
                raise ValueError(
                    f"Missing required database config. Set DATABASE_URL or these env vars: {', '.join(missing)}"
                )
        return self

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"

    # ── CORS ──────────────────────────────────────────────────
    # Comma-separated list.  On Railway, set this to your frontend URL(s).
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173,https://dba-report-fe-production.up.railway.app,https://reports.dbagovlk.com"

    # ── Auth credentials ──────────────────────────────────────
    # MUST be supplied via Railway env vars / .env — no hardcoded defaults here
    AUTH_USERNAME: str = Field(..., description="Dashboard login username — set via env var")
    AUTH_PASSWORD: str = Field(..., description="Dashboard login password — set via env var")

    # ── JWT ───────────────────────────────────────────────────
    # SECRET_KEY must be a strong random string — MUST be set via env var
    SECRET_KEY: str = Field(..., description="JWT signing secret — set via env var; generate with: python -c \"import secrets; print(secrets.token_hex(32))\"")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours

    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS origins as a list, splitting on commas."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def async_database_url(self) -> str:
        """Async URL used by SQLAlchemy / asyncpg."""
        if self.DATABASE_URL_OVERRIDE:
            url = self.DATABASE_URL_OVERRIDE
            # Normalise postgres:// → postgresql+asyncpg://
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://") and "+asyncpg" not in url:
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def sync_database_url(self) -> str:
        """Sync URL used by Alembic / migrations."""
        if self.DATABASE_URL_OVERRIDE:
            url = self.DATABASE_URL_OVERRIDE
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            # Strip +asyncpg if present
            url = url.replace("+asyncpg", "")
            return url
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # Keep legacy property names so existing code doesn't break
    @property
    def DATABASE_URL(self) -> str:
        return self.async_database_url

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return self.sync_database_url

    # pydantic-settings v2 config (replaces deprecated inner class Config)
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # ignore unknown env vars silently
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()

