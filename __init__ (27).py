"""Ürün CRUD işlemleri."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from typing import List, Optional

from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.product_platform import ProductPlatform
from app.schemas.product import ProductCreate, ProductUpdate
from app.utils.crud_base import CRUDBase


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    """Ürün CRUD."""

    async def get_with_relations(self, db: AsyncSession, id: int) -> Optional[Product]:
        """İlişkileriyle birlikte ürün getir."""
        result = await db.execute(
            select(Product)
            .options(
                joinedload(Product.variants),
                joinedload(Product.platforms).joinedload(ProductPlatform.store)
            )
            .where(Product.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_owner(
        self,
        db: AsyncSession,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[Product], int]:
        """Sahibine göre ürünleri getir."""
        query = select(Product).where(Product.owner_id == owner_id)
        count_query = select(func.count(Product.id)).where(Product.owner_id == owner_id)

        if search:
            query = query.where(
                (Product.title.ilike(f"%{search}%")) | 
                (Product.sku.ilike(f"%{search}%"))
            )
            count_query = count_query.where(
                (Product.title.ilike(f"%{search}%")) | 
                (Product.sku.ilike(f"%{search}%"))
            )

        if category_id:
            query = query.where(Product.category_id == category_id)
            count_query = count_query.where(Product.category_id == category_id)

        if is_active is not None:
            query = query.where(Product.is_active == is_active)
            count_query = count_query.where(Product.is_active == is_active)

        count_result = await db.execute(count_query)
        total = count_result.scalar()

        result = await db.execute(
            query
            .options(joinedload(Product.variants), joinedload(Product.platforms))
            .offset(skip)
            .limit(limit)
            .order_by(Product.created_at.desc())
        )
        return result.scalars().all(), total

    async def get_by_sku(self, db: AsyncSession, sku: str, owner_id: int) -> Optional[Product]:
        """SKU ile ürün bul."""
        result = await db.execute(
            select(Product)
            .where(Product.sku == sku)
            .where(Product.owner_id == owner_id)
        )
        return result.scalar_one_or_none()

    async def get_low_stock(self, db: AsyncSession, owner_id: int) -> List[Product]:
        """Düşük stoklu ürünleri getir."""
        result = await db.execute(
            select(Product)
            .where(Product.owner_id == owner_id)
            .where(Product.stock_quantity <= Product.stock_alert_level)
            .where(Product.is_active == True)
        )
        return result.scalars().all()


product_crud = CRUDProduct(Product)
