"""Senkronizasyon görevleri."""
from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "prapazar",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.sync_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Istanbul",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    worker_prefetch_multiplier=1,
)


def get_platform_service(store):
    """Platforma göre servis döndür."""
    from app.services.platforms.trendyol import TrendyolService
    from app.services.platforms.hepsiburada import HepsiburadaService
    from app.services.platforms.n11 import N11Service
    from app.services.platforms.koctas import KoctasService
    from app.services.platforms.pazarama import PazaramaService
    from app.services.platforms.pttavm import PttAvmService

    services = {
        "trendyol": TrendyolService,
        "hepsiburada": HepsiburadaService,
        "n11": N11Service,
        "koctas": KoctasService,
        "pazarama": PazaramaService,
        "pttavm": PttAvmService,
    }
    service_class = services.get(store.platform)
    if not service_class:
        raise ValueError(f"Desteklenmeyen platform: {store.platform}")
    return service_class(store)


@celery_app.task(bind=True, max_retries=3)
def sync_store_products(self, store_id: int):
    """Mağaza ürünlerini senkronize et."""
    import asyncio
    from datetime import datetime
    from app.db.database import AsyncSessionLocal
    from app.crud.store import store_crud
    from app.crud.product import product_crud
    from app.models.product_platform import ProductPlatform

    async def _sync():
        async with AsyncSessionLocal() as db:
            store = await store_crud.get(db, id=store_id)
            if not store or not store.is_connected:
                return {"status": "error", "message": "Mağaza bulunamadı veya bağlı değil"}

            try:
                service = get_platform_service(store)

                if store.platform in ["trendyol", "hepsiburada", "koctas", "pazarama"]:
                    # REST API tabanlı platformlar
                    page = 0
                    while True:
                        if store.platform == "trendyol":
                            result = await service.get_products(page=page, size=50)
                            products = result.get("content", [])
                            total_pages = result.get("totalPages", 1)
                        elif store.platform == "hepsiburada":
                            result = await service.get_products(offset=page * 50, limit=50)
                            products = result.get("items", [])
                            total_pages = 999  # Manuel kontrol
                        elif store.platform == "koctas":
                            result = await service.get_products(page=page + 1, size=50)
                            products = result.get("items", [])
                            total_pages = result.get("totalPages", 1)
                        elif store.platform == "pazarama":
                            result = await service.get_products(page=page + 1, size=50)
                            products = result.get("items", [])
                            total_pages = result.get("totalPages", 1)
                        else:
                            break

                        if not products:
                            break

                        for p in products:
                            sku = p.get("stockCode") or p.get("sku") or p.get("sellerSku")
                            existing = await product_crud.get_by_sku(
                                db, sku=sku, owner_id=store.owner_id
                            )

                            if existing:
                                platform = next(
                                    (pp for pp in existing.platforms if pp.store_id == store.id),
                                    None
                                )
                                if platform:
                                    platform.platform_product_id = str(p.get("id", ""))
                                    platform.platform_stock = p.get("quantity", p.get("stock", 0))
                                    platform.platform_price = p.get("salePrice", p.get("price", 0))
                                    platform.sync_status = "synced"
                                    platform.last_sync_at = datetime.utcnow()
                            else:
                                new_product = {
                                    "sku": sku,
                                    "barcode": p.get("barcode", ""),
                                    "title": p.get("title", p.get("name", "")),
                                    "description": p.get("description", ""),
                                    "base_price": p.get("salePrice", p.get("price", 0)),
                                    "stock_quantity": p.get("quantity", p.get("stock", 0)),
                                    "brand": p.get("brand", ""),
                                    "images": p.get("images", []),
                                    "owner_id": store.owner_id,
                                    "is_active": True
                                }
                                created = await product_crud.create(db, obj_in=new_product)

                                platform_data = {
                                    "product_id": created.id,
                                    "store_id": store.id,
                                    "platform_product_id": str(p.get("id", "")),
                                    "platform_sku": sku,
                                    "platform_price": p.get("salePrice", p.get("price", 0)),
                                    "platform_stock": p.get("quantity", p.get("stock", 0)),
                                    "status": "active",
                                    "sync_status": "synced",
                                    "last_sync_at": datetime.utcnow()
                                }
                                db.add(ProductPlatform(**platform_data))

                        await db.commit()
                        page += 1

                        if page >= total_pages or len(products) < 50:
                            break

                elif store.platform in ["n11", "pttavm"]:
                    # SOAP API tabanlı platformlar
                    # XML parsing gerekli - basit implementasyon
                    result = await service.get_products(page=0, size=100)
                    # XML parsing burada yapılmalı
                    pass

                store.last_sync_at = datetime.utcnow()
                await db.commit()

                return {"status": "success", "message": f"{store.name} senkronizasyonu tamamlandı"}

            except Exception as e:
                await db.rollback()
                raise self.retry(exc=e, countdown=60)

    return asyncio.run(_sync())


@celery_app.task(bind=True, max_retries=3)
def sync_store_orders(self, store_id: int):
    """Mağaza siparişlerini senkronize et."""
    import asyncio
    from datetime import datetime, timedelta
    from app.db.database import AsyncSessionLocal
    from app.crud.store import store_crud
    from app.models.order import Order
    from app.models.order_item import OrderItem

    async def _sync():
        async with AsyncSessionLocal() as db:
            store = await store_crud.get(db, id=store_id)
            if not store or not store.is_connected:
                return {"status": "error", "message": "Mağaza bulunamadı veya bağlı değil"}

            try:
                service = get_platform_service(store)

                if store.platform in ["trendyol", "hepsiburada", "koctas", "pazarama"]:
                    start_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")

                    page = 0
                    while True:
                        if store.platform == "trendyol":
                            result = await service.get_orders(start_date=start_date, page=page, size=50)
                            orders = result.get("content", [])
                            total_pages = result.get("totalPages", 1)
                        elif store.platform == "hepsiburada":
                            result = await service.get_orders(offset=page * 50, limit=50)
                            orders = result.get("items", [])
                            total_pages = 999
                        elif store.platform == "koctas":
                            result = await service.get_orders(page=page + 1, size=50)
                            orders = result.get("items", [])
                            total_pages = result.get("totalPages", 1)
                        elif store.platform == "pazarama":
                            result = await service.get_orders(page=page + 1, size=50)
                            orders = result.get("items", [])
                            total_pages = result.get("totalPages", 1)
                        else:
                            break

                        if not orders:
                            break

                        for o in orders:
                            order_number = o.get("orderNumber") or o.get("orderNumber")

                            from sqlalchemy import select
                            existing_result = await db.execute(
                                select(Order).where(Order.platform_order_number == str(order_number))
                            )
                            existing = existing_result.scalar_one_or_none()

                            if not existing:
                                items = []
                                lines = o.get("lines", o.get("items", []))
                                for line in lines:
                                    items.append({
                                        "product_name": line.get("productName", line.get("name", "")),
                                        "product_sku": line.get("merchantSku", line.get("sku", "")),
                                        "product_barcode": line.get("barcode", ""),
                                        "variant_info": "",
                                        "unit_price": line.get("price", 0),
                                        "quantity": line.get("quantity", 1),
                                        "total_price": line.get("amount", line.get("totalPrice", 0))
                                    })

                                new_order = {
                                    "order_number": f"{store.platform.upper()[:2]}-{order_number}",
                                    "platform_order_id": str(o.get("id", "")),
                                    "platform_order_number": str(order_number),
                                    "status": "new",
                                    "platform_status": o.get("status", ""),
                                    "customer_name": o.get("customerFirstName", "") + " " + o.get("customerLastName", ""),
                                    "customer_email": o.get("customerEmail", ""),
                                    "customer_phone": o.get("customerPhone", ""),
                                    "shipping_address": o.get("shipmentAddress", {}),
                                    "billing_address": o.get("invoiceAddress", {}),
                                    "subtotal": o.get("totalPrice", 0),
                                    "shipping_cost": o.get("cargoPayment", 0),
                                    "total": o.get("totalAmount", 0),
                                    "store_id": store.id,
                                }

                                order = Order(**{k: v for k, v in new_order.items() if k != "items"})
                                db.add(order)
                                await db.flush()

                                for item_data in items:
                                    item = OrderItem(**item_data, order_id=order.id)
                                    db.add(item)

                        await db.commit()
                        page += 1

                        if page >= total_pages or len(orders) < 50:
                            break

                return {"status": "success", "message": f"{store.name} sipariş senkronizasyonu tamamlandı"}

            except Exception as e:
                await db.rollback()
                raise self.retry(exc=e, countdown=60)

    return asyncio.run(_sync())


@celery_app.task
def sync_single_product(product_id: int, store_id: int):
    """Tek ürünü pazaryerine gönder."""
    import asyncio
    from app.db.database import AsyncSessionLocal
    from app.crud.product import product_crud
    from app.crud.store import store_crud
    from app.models.product_platform import ProductPlatform

    async def _sync():
        async with AsyncSessionLocal() as db:
            product = await product_crud.get_with_relations(db, id=product_id)
            store = await store_crud.get(db, id=store_id)

            if not product or not store or not store.is_connected:
                return {"status": "error", "message": "Ürün veya mağaza bulunamadı"}

            platform = next(
                (pp for pp in product.platforms if pp.store_id == store_id),
                None
            )

            try:
                service = get_platform_service(store)
                category_id = ""

                if product.category:
                    category_map = {
                        "trendyol": product.category.trendyol_category_id,
                        "hepsiburada": product.category.hepsiburada_category_id,
                        "n11": product.category.n11_category_id,
                        "koctas": product.category.koctas_category_id,
                        "pazarama": product.category.pazarama_category_id,
                        "pttavm": product.category.pttavm_category_id,
                    }
                    category_id = category_map.get(store.platform, "")

                if store.platform == "trendyol":
                    trendyol_product = service.map_product_to_trendyol(product, category_id or "0")
                    if platform and platform.platform_product_id:
                        await service.update_product(product.barcode or product.sku, trendyol_product)
                    else:
                        result = await service.create_product(trendyol_product)

                elif store.platform == "hepsiburada":
                    hb_product = service.map_product_to_hepsiburada(product, category_id or "")
                    result = await service.create_product(hb_product)

                elif store.platform == "n11":
                    n11_product = service.map_product_to_n11(product, category_id or "0")
                    result = await service.create_product(n11_product)

                elif store.platform == "koctas":
                    koctas_product = service.map_product_to_koctas(product, category_id or "")
                    result = await service.create_product(koctas_product)

                elif store.platform == "pazarama":
                    pazarama_product = service.map_product_to_pazarama(product, category_id or "")
                    result = await service.create_product(pazarama_product)

                elif store.platform == "pttavm":
                    pttavm_product = service.map_product_to_pttavm(product, category_id or "")
                    result = await service.create_product(pttavm_product)

                if not platform:
                    platform = ProductPlatform(
                        product_id=product.id,
                        store_id=store.id,
                        sync_status="synced"
                    )
                    db.add(platform)
                else:
                    platform.sync_status = "synced"

                platform.last_sync_at = datetime.utcnow()
                await db.commit()

                return {"status": "success", "message": "Ürün senkronize edildi"}

            except Exception as e:
                if platform:
                    platform.sync_status = "failed"
                    platform.last_sync_error = str(e)
                await db.commit()
                return {"status": "error", "message": str(e)}

    return asyncio.run(_sync())


@celery_app.task
def update_order_status(order_id: int, new_status: str):
    """Sipariş durumunu pazaryerinde güncelle."""
    pass


@celery_app.task
def send_shipment_info(order_id: int, cargo_company: str, tracking_number: str):
    """Kargo bilgisini pazaryerine gönder."""
    pass


@celery_app.task
def cancel_platform_order(order_id: int):
    """Siparişi pazaryerinde iptal et."""
    pass


@celery_app.task
def sync_all_stores():
    """Tüm mağazaları senkronize et."""
    import asyncio
    from app.db.database import AsyncSessionLocal
    from app.crud.store import store_crud

    async def _sync_all():
        async with AsyncSessionLocal() as db:
            stores = await store_crud.get_active_stores(db)
            for store in stores:
                if store.is_connected:
                    sync_store_products.delay(store.id)
                    sync_store_orders.delay(store.id)

    asyncio.run(_sync_all())
