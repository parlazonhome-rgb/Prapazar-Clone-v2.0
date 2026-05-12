"""CRUD modülü."""
from app.crud.user import user_crud
from app.crud.store import store_crud
from app.crud.category import category_crud
from app.crud.product import product_crud
from app.crud.order import order_crud

__all__ = ["user_crud", "store_crud", "category_crud", "product_crud", "order_crud"]
