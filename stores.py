"""Kategori şemaları."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    """Kategori temel şema."""
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    trendyol_category_id: Optional[str] = None
    hepsiburada_category_id: Optional[str] = None
    n11_category_id: Optional[str] = None
    gittigidiyor_category_id: Optional[str] = None
    koctas_category_id: Optional[str] = None
    pazarama_category_id: Optional[str] = None
    pttavm_category_id: Optional[str] = None
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    trendyol_category_id: Optional[str] = None
    hepsiburada_category_id: Optional[str] = None
    n11_category_id: Optional[str] = None
    gittigidiyor_category_id: Optional[str] = None
    koctas_category_id: Optional[str] = None
    pazarama_category_id: Optional[str] = None
    pttavm_category_id: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Kategori yanıt şeması."""
    id: int
    created_at: datetime
    updated_at: datetime
    owner_id: int
    children: List["CategoryResponse"] = []

    class Config:
        from_attributes = True


# Recursive model için forward reference
CategoryResponse.model_rebuild()
