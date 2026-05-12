"""Hepsiburada API servisi."""
import base64
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx

from app.core.config import get_settings
from app.models.store import Store

settings = get_settings()


class HepsiburadaService:
    """Hepsiburada API entegrasyon servisi."""

    def __init__(self, store: Store):
        self.store = store
        self.base_url = store.base_url or settings.HEPSIBURADA_BASE_URL
        self.api_key = store.api_key
        self.api_secret = store.api_secret
        self.auth_header = self._get_auth_header()

    def _get_auth_header(self) -> str:
        """Basic Auth header oluştur."""
        credentials = f"{self.api_key}:{self.api_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def _get_headers(self) -> dict:
        """API istek header'ları."""
        return {
            "Authorization": self.auth_header,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def test_connection(self) -> dict:
        """API bağlantısını test et."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/products/merchantid/{self.store.seller_id}",
                    headers=self._get_headers(),
                    params={"offset": 0, "limit": 1},
                    timeout=30.0
                )

                if response.status_code in [200, 201]:
                    return {
                        "success": True,
                        "message": "Hepsiburada API bağlantısı başarılı",
                        "store_info": {"status": "connected"}
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

    async def get_products(self, offset: int = 0, limit: int = 50) -> dict:
        """Hepsiburada'dan ürünleri çek."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/products/merchantid/{self.store.seller_id}",
                headers=self._get_headers(),
                params={"offset": offset, "limit": limit},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def create_product(self, product_data: dict) -> dict:
        """Hepsiburada'ya ürün ekle."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/products/import",
                headers=self._get_headers(),
                json={"items": [product_data]},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def update_stock_and_price(
        self,
        merchant_id: str,
        sku: str,
        quantity: int,
        price: float
    ) -> dict:
        """Stok ve fiyat güncelle."""
        data = {
            "items": [{
                "merchantId": merchant_id,
                "sku": sku,
                "availableStock": quantity,
                "price": price
            }]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/inventory-uploads",
                headers=self._get_headers(),
                json=data,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def get_orders(
        self,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 50
    ) -> dict:
        """Siparişleri çek."""
        params = {"offset": offset, "limit": limit}
        if status:
            params["status"] = status

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/orders/merchantid/{self.store.seller_id}",
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
            "trackingNumber": tracking_number
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/orders/merchantid/{self.store.seller_id}/ordernumber/{order_id}/cargo",
                headers=self._get_headers(),
                json=data,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    def map_product_to_hepsiburada(self, product, category_id: str) -> dict:
        """Ürünü Hepsiburada formatına dönüştür."""
        hb_product = {
            "merchantId": self.store.seller_id,
            "sku": product.sku,
            "name": product.title,
            "description": product.description or "",
            "categoryId": category_id,
            "price": product.base_price,
            "availableStock": product.stock_quantity,
            "vatRate": 18,
            "images": product.images or [],
            "attributes": [],
            "barcode": product.barcode or product.sku,
            "brand": product.brand or "",
            "dimensions": {
                "width": product.dimensions.get("width", 0) if product.dimensions else 0,
                "height": product.dimensions.get("height", 0) if product.dimensions else 0,
                "depth": product.dimensions.get("depth", 0) if product.dimensions else 0,
                "weight": product.weight or 0
            }
        }
        return hb_product
