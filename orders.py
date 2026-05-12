"""Kullanıcı şemaları."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Kullanıcı temel şema."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None


class UserCreate(UserBase):
    """Kullanıcı oluşturma şeması."""
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    """Kullanıcı güncelleme şeması."""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """Kullanıcı yanıt şeması."""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Kullanıcı giriş şeması."""
    username: str
    password: str


class Token(BaseModel):
    """Token yanıt şeması."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
