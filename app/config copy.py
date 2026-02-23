"""
Buddhist Affairs MIS Dashboard - Configuration Settings
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from urllib.parse import quote_plus


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Buddhist Affairs MIS Dashboard"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database Configuration
    # Live DB on Railway — switch back to localhost / dbahrms-ranjith for local dev
    DB_HOST: str = "gondola.proxy.rlwy.net"
    DB_PORT: int = 22000
    DB_NAME: str = "dbahrms-new"
    DB_USER: str = "app_admin"
    DB_PASSWORD: str = "rX2SWDbFuM%25Qe3kBRzqnQ%26Ia"   # URL-encoded: % -> %25, & -> %26
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    
    @property
    def DATABASE_URL(self) -> str:
        """Generate async database URL"""
        # Password is already URL-encoded, use directly
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Generate sync database URL for migrations"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
