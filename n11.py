# ============================================
# VERİTABANI MODELLERİ (SQLAlchemy ORM)
# ============================================

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class User(Base):
    """Kullanıcılar"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # İlişkiler
    stores = relationship("Store", back_populates="user", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="user", cascade="all, delete-orphan")


class Store(Base):
    """Pazaryeri Mağazaları"""
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    platform = Column(String(50), nullable=False)  # trendyol, hepsiburada, n11, gg
    api_key = Column(Text)
    api_secret = Column(Text)
    seller_id = Column(String(255))
    is_active = Column(Boolean, default=True)
    last_sync_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # İlişkiler
    user = relationship("User", back_populates="stores")
    listings = relationship("ProductListing", back_populates="store", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="store", cascade="all, delete-orphan")
    sync_logs = relationship("SyncLog", back_populates="store", cascade="all, delete-orphan")


class Product(Base):
    """Ana Ürünler (Sizin Envanteriniz)"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sku = Column(String(255), unique=True, nullable=False, index=True)
    barcode = Column(String(255))
    title = Column(String(500), nullable=False)
    description = Column(Text)
    brand = Column(String(255))
    category_id = Column(Integer)
    base_price = Column(Numeric(10, 2), nullable=False)
    base_stock = Column(Integer, nullable=False, default=0)
    images = Column(JSON, default=list)
    attributes = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # İlişkiler
    user = relationship("User", back_populates="products")
    listings = relationship("ProductListing", back_populates="product", cascade="all, delete-orphan")


class ProductListing(Base):
    """Pazaryeri Ürün Eşleştirmeleri"""
    __tablename__ = "product_listings"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    platform_product_id = Column(String(255))  # Trendyol'daki ürün ID
    platform_sku = Column(String(255))
    platform_price = Column(Numeric(10, 2))
    platform_stock = Column(Integer)
    commission_rate = Column(Numeric(5, 2), default=0)
    listing_status = Column(String(50), default="pending")  # pending, active, inactive, error
    last_sync_at = Column(DateTime(timezone=True))
    sync_error = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Unique constraint
    __table_args__ = (UniqueConstraint('product_id', 'store_id', name='uq_product_store'),)

    # İlişkiler
    product = relationship("Product", back_populates="listings")
    store = relationship("Store", back_populates="listings")


class Order(Base):
    """Siparişler"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    platform_order_id = Column(String(255), nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    order_number = Column(String(255))
    customer_name = Column(String(255))
    customer_phone = Column(String(50))
    customer_address = Column(Text)
    total_amount = Column(Numeric(10, 2))
    currency = Column(String(10), default="TRY")
    status = Column(String(50), default="Created")
    cargo_company = Column(String(100))
    tracking_number = Column(String(255))
    order_date = Column(DateTime(timezone=True))
    raw_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # İlişkiler
    store = relationship("Store", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """Sipariş Ürünleri"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))
    listing_id = Column(Integer, ForeignKey("product_listings.id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2))
    total_price = Column(Numeric(10, 2))

    # İlişkiler
    order = relationship("Order", back_populates="items")


class SyncLog(Base):
    """Senkronizasyon Logları"""
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    sync_type = Column(String(50), nullable=False)  # products, orders, stock, price
    status = Column(String(50), nullable=False)  # success, error, partial
    items_processed = Column(Integer, default=0)
    items_failed = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # İlişkiler
    store = relationship("Store", back_populates="sync_logs")


class CategoryMapping(Base):
    """Kategori Eşleştirmeleri"""
    __tablename__ = "category_mappings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    internal_category = Column(String(255), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    platform_category_id = Column(String(255), nullable=False)
    platform_category_name = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint('internal_category', 'store_id', name='uq_category_store'),)


class PriceRule(Base):
    """Fiyat Kuralları"""
    __tablename__ = "price_rules"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    rule_name = Column(String(255))
    rule_type = Column(String(50))  # percentage, fixed_amount
    value = Column(Numeric(10, 2))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
