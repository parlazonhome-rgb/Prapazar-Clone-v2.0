"""Pazarama API servisi."""
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx

from app.core.config import get_settings
from app.models.store import Store

settings = get_settings()


class PazaramaService:
    """Pazarama API entegrasyon servisi."""

    def __init__(self, store: Store):
        self.store = store
        self.api_key = store.api_key
        self.api_secret = store.api_secret
        self.base_url = store.base_url or "https://isortagim.pazarama.com/api"
        self.token = None

    async def _get_token(self) -> str:
        """OAuth token al."""
        if self.token:
            return self.token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.api_key,
                    "client_secret": self.api_secret
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            self.token = data.get("access_token")
            return self.token

    async def _get_headers(self) -> dict:
        """API istek header'ları."""
        token = await self._get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def test_connection(self) -> dict:
        """API bağlantısını test et."""
        try:
            headers = await self._get_headers()

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/seller/profile",
                    headers=headers,
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "message": "Pazarama API bağlantısı başarılı",
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
        headers = await self._get_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/products",
                headers=headers,
                params={"page": page, "limit": size},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def create_product(self, product_data: dict) -> dict:
        """Ürün ekle."""
        headers = await self._get_headers()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/products",
                headers=headers,
                json=product_data,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def update_stock_and_price(
        self,
        product_id: str,
        quantity: int,
        price: float
    ) -> dict:
        """Stok ve fiyat güncelle."""
        headers = await self._get_headers()
        data = {
            "stock": quantity,
            "price": price
        }

        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/products/{product_id}/inventory",
                headers=headers,
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
        headers = await self._get_headers()
        params = {"page": page, "limit": size}
        if status:
            params["status"] = status

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/orders",
                headers=headers,
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
        headers = await self._get_headers()
        data = {
            "cargoCompany": cargo_company,
            "trackingNumber": tracking_number
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/orders/{order_id}/shipment",
                headers=headers,
                json=data,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def get_categories(self) -> dict:
        """Kategorileri listele."""
        headers = await self._get_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/categories",
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    def map_product_to_pazarama(self, product, category_id: str) -> dict:
        """Ürünü Pazarama formatına dönüştür."""
        return {
            "sellerSku": product.sku,
            "barcode": product.barcode or product.sku,
            "title": product.title,
            "description": product.description or "",
            "categoryId": category_id,
            "brand": product.brand or "",
            "price": product.base_price,
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
