"""Koçtaş API servisi."""
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx

from app.core.config import get_settings
from app.models.store import Store

settings = get_settings()


class KoctasService:
    """Koçtaş API entegrasyon servisi."""

    def __init__(self, store: Store):
        self.store = store
        self.api_key = store.api_key
        self.base_url = store.base_url or "https://api.koctas.com.tr/v1"

    def _get_headers(self) -> dict:
        """API istek header'ları."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Seller-Id": self.store.seller_id or ""
        }

    async def test_connection(self) -> dict:
        """API bağlantısını test et."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/seller/profile",
                    headers=self._get_headers(),
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "message": "Koçtaş API bağlantısı başarılı",
                        "store_info": data
                    }
                else:
                    return {
                        "success": False,
                        "message": f"API Hatası: {response.status_code} - {response.text}"
                    }
        except Exception as e:
            return {
                "success": False,
                "message": f"Bağlantı hatası: {str(e)}"
            }

    async def get_products(self, page: int = 1, size: int = 50) -> dict:
        """Ürünleri listele."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/products",
                headers=self._get_headers(),
                params={"page": page, "size": size},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def create_product(self, product_data: dict) -> dict:
        """Ürün ekle."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/products",
                headers=self._get_headers(),
                json=product_data,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def update_product(self, product_id: str, product_data: dict) -> dict:
        """Ürün güncelle."""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/products/{product_id}",
                headers=self._get_headers(),
                json=product_data,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def update_stock_and_price(
        self,
        product_id: str,
        quantity: int,
        price: float,
        sale_price: Optional[float] = None
    ) -> dict:
        """Stok ve fiyat güncelle."""
        data = {
            "stock": quantity,
            "price": price,
            "salePrice": sale_price or price
        }

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/products/{product_id}/inventory",
                headers=self._get_headers(),
                json=data,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def get_orders(
        self,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 50
    ) -> dict:
        """Siparişleri çek."""
        params = {"page": page, "size": size}
        if status:
            params["status"] = status

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/orders",
                headers=self._get_headers(),
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def update_tracking_number(
        self,
        order_id: str,
        cargo_company: str,
        tracking_number: str
    ) -> dict:
        """Kargo takip numarası gönder."""
        data = {
            "cargoCompany": cargo_company,
            "trackingNumber": tracking_number,
            "status": "shipped"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/orders/{order_id}/shipment",
                headers=self._get_headers(),
                json=data,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def cancel_order(self, order_id: str, reason: str = "") -> dict:
        """Sipariş iptal et."""
        data = {
            "reason": reason or "Satıcı tarafından iptal edildi"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/orders/{order_id}/cancel",
                headers=self._get_headers(),
                json=data,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def get_categories(self) -> dict:
        """Kategorileri listele."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/categories",
                headers=self._get_headers(),
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    def map_product_to_koctas(self, product, category_id: str) -> dict:
        """Ürünü Koçtaş formatına dönüştür."""
        return {
            "sellerSku": product.sku,
            "barcode": product.barcode or product.sku,
            "title": product.title,
            "description": product.description or "",
            "categoryId": category_id,
            "brand": product.brand or "",
            "price": product.base_price,
            "salePrice": product.base_price,
            "stock": product.stock_quantity,
            "vatRate": 18,
            "images": product.images or [],
            "attributes": [],
            "dimensions": {
                "width": product.dimensions.get("width", 0) if product.dimensions else 0,
                "height": product.dimensions.get("height", 0) if product.dimensions else 0,
                "depth": product.dimensions.get("depth", 0) if product.dimensions else 0,
                "weight": product.weight or 0
            }
        }
