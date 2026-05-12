"""Sipariş CRUD işlemleri."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.order import Order
from app.models.order_item import OrderItem
from app.schemas.order import OrderCreate, OrderUpdate
from app.utils.crud_base import CRUDBase


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    """Sipariş CRUD."""

    async def get_with_items(self, db: AsyncSession, id: int) -> Optional[Order]:
        """Kalemleriyle birlikte sipariş getir."""
        result = await db.execute(
            select(Order)
            .options(joinedload(Order.items))
            .where(Order.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_store(
        self,
        db: AsyncSession,
        store_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> tuple[List[Order], int]:
        """Mağazaya göre siparişleri getir."""
        query = select(Order).where(Order.store_id == store_id)
        count_query = select(func.count(Order.id)).where(Order.store_id == store_id)

        if status:
            query = query.where(Order.status == status)
            count_query = count_query.where(Order.status == status)

        count_result = await db.execute(count_query)
        total = count_result.scalar()

        result = await db.execute(
            query
            .options(joinedload(Order.items))
            .offset(skip)
            .limit(limit)
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all(), total

    async def get_by_owner(
        self,
        db: AsyncSession,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> tuple[List[Order], int]:
        """Sahibine göre tüm siparişleri getir."""
        from app.models.store import Store

        query = select(Order).join(Store).where(Store.owner_id == owner_id)
        count_query = select(func.count(Order.id)).join(Store).where(Store.owner_id == owner_id)

        if status:
            query = query.where(Order.status == status)
            count_query = count_query.where(Order.status == status)

        if date_from:
            query = query.where(Order.created_at >= date_from)
            count_query = count_query.where(Order.created_at >= date_from)

        if date_to:
            query = query.where(Order.created_at <= date_to)
            count_query = count_query.where(Order.created_at <= date_to)

        count_result = await db.execute(count_query)
        total = count_result.scalar()

        result = await db.execute(
            query
            .options(joinedload(Order.items))
            .offset(skip)
            .limit(limit)
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all(), total

    async def get_today_orders(self, db: AsyncSession, owner_id: int) -> List[Order]:
        """Bugünkü siparişleri getir."""
        from app.models.store import Store
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        result = await db.execute(
            select(Order)
            .join(Store)
            .where(Store.owner_id == owner_id)
            .where(Order.created_at >= today)
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all()

    async def get_order_stats(self, db: AsyncSession, owner_id: int) -> dict:
        """Sipariş istatistikleri."""
        from app.models.store import Store

        total_result = await db.execute(
            select(func.count(Order.id))
            .join(Store)
            .where(Store.owner_id == owner_id)
        )
        total_orders = total_result.scalar()

        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_result = await db.execute(
            select(func.count(Order.id))
            .join(Store)
            .where(Store.owner_id == owner_id)
            .where(Order.created_at >= today)
        )
        today_orders = today_result.scalar()

        pending_result = await db.execute(
            select(func.count(Order.id))
            .join(Store)
            .where(Store.owner_id == owner_id)
            .where(Order.status.in_(["new", "confirmed", "preparing"]))
        )
        pending_orders = pending_result.scalar()

        revenue_result = await db.execute(
            select(func.sum(Order.total))
            .join(Store)
            .where(Store.owner_id == owner_id)
        )
        total_revenue = revenue_result.scalar() or 0

        return {
            "total_orders": total_orders,
            "today_orders": today_orders,
            "pending_orders": pending_orders,
            "total_revenue": float(total_revenue)
        }


order_crud = CRUDOrder(Order)
