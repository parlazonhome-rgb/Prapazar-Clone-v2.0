"""Trendyol API servisi."""
import base64
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx

from app.core.config import get_settings
from app.models.store import Store

settings = get_settings()


class TrendyolService:
    """Trendyol API entegrasyon servisi."""

    def __init__(self, store: Store):
        self.store = store
        self.base_url = store.base_url or settings.TRENDYOL_BASE_URL
        self.seller_id = store.seller_id
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
            "User-Agent": f"{self.seller_id} - SelfIntegration"
        }

    async def test_connection(self) -> dict:
        """API bağlantısını test et."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/suppliers/{self.seller_id}/products",
                    headers=self._get_headers(),
                    params={"size": 1},
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "message": "Trendyol API bağlantısı başarılı",
                        "store_info": {
                            "total_products": data.get("totalElements", 0),
                            "page": data.get("page", 0)
                        }
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

    async def get_products(
        self,
        page: int = 0,
        size: int = 50,
        approved: Optional[bool] = None
    ) -> dict:
        """Trendyol'dan ürünleri çek."""
        params = {"page": page, "size": size}
        if approved is not None:
            params["approved"] = str(approved).lower()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/suppliers/{self.seller_id}/products",
                headers=self._get_headers(),
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def create_product(self, product_data: dict) -> dict:
        """Trendyol'a ürün ekle."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/suppliers/{self.seller_id}/products",
                headers=self._get_headers(),
                json=product_data,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def update_product(self, barcode: str, product_data: dict) -> dict:
        """Trendyol'da ürün güncelle."""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/suppliers/{self.seller_id}/products",
                headers=self._get_headers(),
                json={"items": [{"barcode": barcode, **product_data}]},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def update_stock_and_price(
        self,
        barcode: str,
        quantity: int,
        sale_price: float,
        list_price: Optional[float] = None
    ) -> dict:
        """Stok ve fiyat güncelle."""
        data = {
            "items": [{
                "barcode": barcode,
                "quantity": quantity,
                "salePrice": sale_price,
                "listPrice": list_price or sale_price
            }]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/suppliers/{self.seller_id}/products/price-and-inventory",
                headers=self._get_headers(),
                json=data,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def get_orders(
        self,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 0,
        size: int = 50
    ) -> dict:
        """Siparişleri çek."""
        params = {"page": page, "size": size}
        if status:
            params["status"] = status
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/suppliers/{self.seller_id}/orders",
                headers=self._get_headers(),
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def update_tracking_number(
        self,
        package_id: str,
        cargo_provider: str,
        tracking_number: str
    ) -> dict:
        """Kargo takip numarası gönder."""
        data = {
            "lines": [],
            "params": {
                "cargoProvider": cargo_provider,
                "trackingNumber": tracking_number
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/suppliers/{self.seller_id}/shipment-packages/{package_id}",
                headers=self._get_headers(),
                json=data,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def get_brands(self, page: int = 0, size: int = 100) -> dict:
        """Markaları listele."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/brands",
                headers=self._get_headers(),
                params={"page": page, "size": size},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def get_categories(self) -> dict:
        """Kategorileri listele."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/product-categories",
                headers=self._get_headers(),
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def get_category_attributes(self, category_id: str) -> dict:
        """Kategori özelliklerini getir."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/product-categories/{category_id}/attributes",
                headers=self._get_headers(),
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    def map_product_to_trendyol(self, product, category_id: str) -> dict:
        """Ürünü Trendyol formatına dönüştür."""
        trendyol_product = {
            "barcode": product.barcode or product.sku,
            "title": product.title,
            "productMainId": product.sku,
            "brandId": 0,  # Marka ID'si
            "categoryId": int(category_id),
            "quantity": product.stock_quantity,
            "stockCode": product.sku,
            "dimensionalWeight": product.weight or 1,
            "description": product.description or "",
            "currencyType": "TRY",
            "listPrice": product.base_price,
            "salePrice": product.base_price,
            "vatRate": 18,
            "images": product.images or [],
            "attributes": [],
            "cargoCompanyId": 17  # Varsayılan kargo firması
        }

        if product.dimensions:
            trendyol_product.update({
                "width": product.dimensions.get("width", 0),
                "height": product.dimensions.get("height", 0),
                "depth": product.dimensions.get("depth", 0)
            })

        return trendyol_product
