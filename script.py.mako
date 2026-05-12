# ============================================
# UYGULAMA KONFİGÜRASYONU
# ============================================

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Uygulama ayarları"""

    # Uygulama
    APP_NAME: str = "PazaryeriEntegrasyon"
    DEBUG: bool = False
    SECRET_KEY: str = "degistir-bu-anahtari"

    # Veritabanı
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 saat

    # API URL'leri
    TRENDYOL_API_BASE: str = "https://api.trendyol.com/sapigw"
    HEPSIBURADA_API_BASE: str = "https://mpop.hepsiburada.com/api"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Ayarları cache'le"""
    return Settings()


settings = get_settings()
