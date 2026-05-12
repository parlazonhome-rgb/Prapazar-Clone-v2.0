"""Mağaza CRUD işlemleri."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.store import Store
from app.schemas.store import StoreCreate, StoreUpdate
from app.utils.crud_base import CRUDBase


class CRUDStore(CRUDBase[Store, StoreCreate, StoreUpdate]):
    """Mağaza CRUD."""

    async def get_by_owner(
        self, 
        db: AsyncSession, 
        owner_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Store]:
        """Sahibine göre mağazaları getir."""
        result = await db.execute(
            select(Store)
            .where(Store.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_platform(
        self,
        db: AsyncSession,
        owner_id: int,
        platform: str
    ) -> List[Store]:
        """Platforma göre mağazaları getir."""
        result = await db.execute(
            select(Store)
            .where(Store.owner_id == owner_id)
            .where(Store.platform == platform)
        )
        return result.scalars().all()

    async def get_active_stores(self, db: AsyncSession) -> List[Store]:
        """Aktif mağazaları getir."""
        result = await db.execute(
            select(Store).where(Store.is_active == True)
        )
        return result.scalars().all()


store_crud = CRUDStore(Store)
