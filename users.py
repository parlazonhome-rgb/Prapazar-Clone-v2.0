"""Sipariş şemaları."""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class OrderItemBase(BaseModel):
    """Sipariş kalemi temel şema."""
    product_name: str
    product_sku: Optional[str] = None
    product_barcode: Optional[str] = None
    variant_info: Optional[str] = None
    unit_price: float
    quantity: int
    total_price: float
    product_id: Optional[int] = None


class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    """Sipariş temel şema."""
    order_number: str
    platform_order_id: Optional[str] = None
    platform_order_number: Optional[str] = None
    status: str = "new"
    platform_status: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    shipping_address: Optional[Dict[str, Any]] = None
    billing_address: Optional[Dict[str, Any]] = None
    subtotal: float = 0.0
    shipping_cost: float = 0.0
    discount: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    commission_amount: float = 0.0
    cargo_company: Optional[str] = None
    tracking_number: Optional[str] = None
    customer_note: Optional[str] = None
    internal_note: Optional[str] = None
    store_id: int


class OrderCreate(OrderBase):
    items: List[OrderItemBase]


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    cargo_company: Optional[str] = None
    tracking_number: Optional[str] = None
    internal_note: Optional[str] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


class OrderResponse(OrderBase):
    """Sipariş yanıt şeması."""
    id: int
    shipped_at: Optional[datetime]
    delivered_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Sipariş listesi yanıtı."""
    items: List[OrderResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ShipmentUpdate(BaseModel):
    """Kargo bilgisi güncelleme."""
    cargo_company: str
    tracking_number: str
    items: List[int]  # OrderItem ID'leri
