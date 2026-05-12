"""Kullanıcı CRUD işlemleri."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.crud_base import CRUDBase


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """Kullanıcı CRUD."""

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Email ile kullanıcı bul."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Username ile kullanıcı bul."""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()


user_crud = CRUDUser(User)
