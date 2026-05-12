# ============================================
# VERİTABANI BAĞLANTISI
# ============================================

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from app.core.config import settings

# Asenkron motor oluştur
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=NullPool if settings.DEBUG else None,
    future=True
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Model tabanı
Base = declarative_base()


async def get_db():
    """Dependency: Her istek için yeni bir DB session oluşturur"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Uygulama başlangıcında tabloları oluşturur"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
