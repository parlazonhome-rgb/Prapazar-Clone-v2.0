"""Prapazar Clone - Ana Uygulama."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import get_settings
from app.api.router import api_router
from app.db.database import create_tables

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama yaşam döngüsü."""
    # Startup
    await create_tables()
    print("✅ Veritabanı tabloları oluşturuldu")
    yield
    # Shutdown
    print("👋 Uygulama kapatılıyor")


app = FastAPI(
    title=settings.APP_NAME,
    description="Pazaryeri entegrasyon sistemi - Trendyol, Hepsiburada, N11, Koçtaş, Pazarama, PTT AVM",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - Render domain'leri
origins = settings.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Router
app.include_router(api_router, prefix="/api/v1")

# Health check
@app.get("/health")
async def health_check():
    """Sağlık kontrolü."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": "2.0.0",
        "platforms": ["trendyol", "hepsiburada", "n11", "koctas", "pazarama", "pttavm"]
    }


@app.get("/")
async def root():
    """Ana sayfa."""
    return {
        "app": settings.APP_NAME,
        "version": "2.0.0",
        "docs": "/docs",
        "api": "/api/v1",
        "health": "/health",
        "platforms": {
            "trendyol": "✅",
            "hepsiburada": "✅",
            "n11": "✅",
            "koctas": "✅",
            "pazarama": "✅",
            "pttavm": "✅"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
