"""Mağaza şemaları."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StoreBase(BaseModel):
    """Mağaza temel şema."""
    name: str = Field(..., min_length=1, max_length=200)
    platform: str = Field(..., pattern="^(trendyol|hepsiburada|n11|gittigidiyor|koctas|pazarama|pttavm|amazon)$")
    store_name: Optional[str] = None
    seller_id: Optional[str] = None
    base_url: Optional[str] = None
    commission_rate: float = Field(default=0.0, ge=0, le=100)
    sync_interval_minutes: int = Field(default=15, ge=5, le=1440)


class StoreCreate(StoreBase):
    """Mağaza oluşturma şeması."""
    api_key: str
    api_secret: str


class StoreUpdate(BaseModel):
    """Mağaza güncelleme şeması."""
    name: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    base_url: Optional[str] = None
    is_active: Optional[bool] = None
    commission_rate: Optional[float] = None
    sync_interval_minutes: Optional[int] = None


class StoreResponse(StoreBase):
    """Mağaza yanıt şeması."""
    id: int
    is_active: bool
    is_connected: bool
    last_sync_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    owner_id: int

    class Config:
        from_attributes = True


class StoreConnectionTest(BaseModel):
    """Mağaza bağlantı testi yanıtı."""
    success: bool
    message: str
    store_info: Optional[dict] = None
