"""Ürün şemaları."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProductVariantBase(BaseModel):
    """Varyant temel şema."""
    sku: str
    barcode: Optional[str] = None
    attributes: Dict[str, str] = {}
    price: float = Field(default=0.0, ge=0)
    stock_quantity: int = Field(default=0, ge=0)
    images: List[str] = []
    is_active: bool = True


class ProductVariantCreate(ProductVariantBase):
    pass


class ProductVariantResponse(ProductVariantBase):
    id: int
    product_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductPlatformBase(BaseModel):
    """Ürün-Pazaryeri temel şema."""
    store_id: int
    platform_price: float = Field(default=0.0, ge=0)
    platform_sale_price: Optional[float] = None
    platform_stock: int = Field(default=0, ge=0)
    status: str = "draft"


class ProductPlatformCreate(ProductPlatformBase):
    pass


class ProductPlatformResponse(ProductPlatformBase):
    id: int
    product_id: int
    platform_product_id: Optional[str]
    platform_sku: Optional[str]
    platform_listing_url: Optional[str]
    sync_status: str
    last_sync_at: Optional[datetime]
    last_sync_error: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    """Ürün temel şema."""
    sku: str = Field(..., min_length=1, max_length=100)
    barcode: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    short_description: Optional[str] = None
    purchase_price: float = Field(default=0.0, ge=0)
    base_price: float = Field(default=0.0, ge=0)
    stock_quantity: int = Field(default=0, ge=0)
    stock_alert_level: int = Field(default=5, ge=0)
    brand: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[Dict[str, float]] = None
    images: List[str] = []
    main_image: Optional[str] = None
    has_variants: bool = False
    variant_attributes: List[Dict[str, Any]] = []
    is_active: bool = True
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    tags: List[str] = []
    category_id: Optional[int] = None


class ProductCreate(ProductBase):
    variants: List[ProductVariantCreate] = []
    platforms: List[ProductPlatformCreate] = []


class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    barcode: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    purchase_price: Optional[float] = None
    base_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    stock_alert_level: Optional[int] = None
    brand: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[Dict[str, float]] = None
    images: Optional[List[str]] = None
    main_image: Optional[str] = None
    has_variants: Optional[bool] = None
    variant_attributes: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    tags: Optional[List[str]] = None
    category_id: Optional[int] = None


class ProductResponse(ProductBase):
    """Ürün yanıt şeması."""
    id: int
    is_approved: bool
    created_at: datetime
    updated_at: datetime
    owner_id: int
    variants: List[ProductVariantResponse] = []
    platforms: List[ProductPlatformResponse] = []

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Ürün listesi yanıtı."""
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BulkProductUpdate(BaseModel):
    """Toplu ürün güncelleme."""
    product_ids: List[int]
    field: str  # price, stock, is_active
    value: Any


class BulkPlatformSync(BaseModel):
    """Toplu platform senkronizasyonu."""
    product_ids: List[int]
    store_ids: List[int]
