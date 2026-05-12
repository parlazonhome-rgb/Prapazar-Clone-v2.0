"""Uygulama yapılandırma ayarları."""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Uygulama ayarları."""

    # App
    APP_NAME: str = "Prapazar Clone"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", 8000))

    # Database - Render PostgreSQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/prapazar_db")

    # Redis - Render Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS - Render frontend URL'si
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,https://prapazar-frontend.onrender.com")

    # Trendyol
    TRENDYOL_API_KEY: str = os.getenv("TRENDYOL_API_KEY", "")
    TRENDYOL_API_SECRET: str = os.getenv("TRENDYOL_API_SECRET", "")
    TRENDYOL_BASE_URL: str = "https://api.trendyol.com/sapigw"

    # Hepsiburada
    HEPSIBURADA_API_KEY: str = os.getenv("HEPSIBURADA_API_KEY", "")
    HEPSIBURADA_API_SECRET: str = os.getenv("HEPSIBURADA_API_SECRET", "")
    HEPSIBURADA_BASE_URL: str = "https://mpop.hepsiburada.com/api"

    # N11
    N11_API_KEY: str = os.getenv("N11_API_KEY", "")
    N11_API_SECRET: str = os.getenv("N11_API_SECRET", "")
    N11_BASE_URL: str = "https://api.n11.com/ws"

    # Koçtaş
    KOCTAS_API_KEY: str = os.getenv("KOCTAS_API_KEY", "")
    KOCTAS_BASE_URL: str = "https://api.koctas.com.tr/v1"

    # Pazarama
    PAZARAMA_API_KEY: str = os.getenv("PAZARAMA_API_KEY", "")
    PAZARAMA_API_SECRET: str = os.getenv("PAZARAMA_API_SECRET", "")
    PAZARAMA_BASE_URL: str = "https://isortagim.pazarama.com/api"

    # PTT AVM
    PTTAVM_API_KEY: str = os.getenv("PTTAVM_API_KEY", "")
    PTTAVM_API_SECRET: str = os.getenv("PTTAVM_API_SECRET", "")
    PTTAVM_BASE_URL: str = "https://ws.pttavm.com:93/service.svc"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Ayarları önbellekten al."""
    return Settings()
