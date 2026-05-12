"""N11 API servisi."""
import hashlib
import base64
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx

from app.core.config import get_settings
from app.models.store import Store

settings = get_settings()


class N11Service:
    """N11 API entegrasyon servisi (SOAP/XML tabanlı)."""

    def __init__(self, store: Store):
        self.store = store
        self.api_key = store.api_key
        self.api_secret = store.api_secret
        self.base_url = store.base_url or "https://api.n11.com/ws"

    def _get_auth(self) -> dict:
        """Kimlik doğrulama bilgileri."""
        return {
            "appKey": self.api_key,
            "appSecret": self.api_secret
        }

    def _build_soap_envelope(self, method: str, body_content: str) -> str:
        """SOAP envelope oluştur."""
        auth = self._get_auth()
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ns="http://www.n11.com/ws/schemas">
   <soapenv:Header/>
   <soapenv:Body>
      <ns:{method}Request>
         <auth>
            <appKey>{auth['appKey']}</appKey>
            <appSecret>{auth['appSecret']}</appSecret>
         </auth>
         {body_content}
      </ns:{method}Request>
   </soapenv:Body>
</soapenv:Envelope>"""

    async def test_connection(self) -> dict:
        """API bağlantısını test et."""
        try:
            # N11'de basit bir istek ile test
            body = self._build_soap_envelope("GetTopLevelCategories", "")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/CategoryService.wsdl",
                    headers={"Content-Type": "text/xml; charset=utf-8"},
                    content=body,
                    timeout=30.0
                )

                if response.status_code == 200 and "fault" not in response.text.lower():
                    return {
                        "success": True,
                        "message": "N11 API bağlantısı başarılı",
                        "store_info": {"status": "connected"}
                    }
                else:
                    return {
                        "success": False,
                        "message": f"API Hatası: {response.status_code}"
                    }
        except Exception as e:
            return {
                "success": False,
                "message": f"Bağlantı hatası: {str(e)}"
            }

    async def get_categories(self) -> dict:
        """Kategorileri listele."""
        body = self._build_soap_envelope("GetTopLevelCategories", "")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/CategoryService.wsdl",
                headers={"Content-Type": "text/xml; charset=utf-8"},
                content=body,
                timeout=30.0
            )
            response.raise_for_status()
            return {"xml_response": response.text}

    async def get_products(self, page: int = 0, size: int = 100) -> dict:
        """Ürünleri listele."""
        body_content = f"""
         <pagingData>
            <currentPage>{page}</currentPage>
            <pageSize>{size}</pageSize>
         </pagingData>
        """
        body = self._build_soap_envelope("GetProductList", body_content)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/ProductService.wsdl",
                headers={"Content-Type": "text/xml; charset=utf-8"},
                content=body,
                timeout=30.0
            )
            response.raise_for_status()
            return {"xml_response": response.text}

    async def create_product(self, product_data: dict) -> dict:
        """Ürün ekle."""
        # N11 ürün yapısı
        body_content = f"""
         <product>
            <productSellerCode>{product_data.get('sku')}</productSellerCode>
            <title>{product_data.get('title')}</title>
            <subtitle></subtitle>
            <description>{product_data.get('description', '')}</description>
            <category>
               <id>{product_data.get('category_id', 0)}</id>
            </category>
            <price>{product_data.get('price', 0)}</price>
            <currencyType>1</currencyType>
            <stockItems>
               <stockItem>
                  <sellerStockCode>{product_data.get('sku')}</sellerStockCode>
                  <quantity>{product_data.get('stock', 0)}</quantity>
               </stockItem>
            </stockItems>
            <images>
               <image>
                  <url>{product_data.get('image', '')}</url>
                  <order>1</order>
               </image>
            </images>
         </product>
        """
        body = self._build_soap_envelope("SaveProduct", body_content)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/ProductService.wsdl",
                headers={"Content-Type": "text/xml; charset=utf-8"},
                content=body,
                timeout=30.0
            )
            response.raise_for_status()
            return {"xml_response": response.text}

    async def update_stock_and_price(self, sku: str, quantity: int, price: float) -> dict:
        """Stok ve fiyat güncelle."""
        body_content = f"""
         <product>
            <id></id>
            <productSellerCode>{sku}</productSellerCode>
            <price>{price}</price>
            <stockItems>
               <stockItem>
                  <sellerStockCode>{sku}</sellerStockCode>
                  <quantity>{quantity}</quantity>
               </stockItem>
            </stockItems>
         </product>
        """
        body = self._build_soap_envelope("UpdateProduct", body_content)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/ProductService.wsdl",
                headers={"Content-Type": "text/xml; charset=utf-8"},
                content=body,
                timeout=30.0
            )
            response.raise_for_status()
            return {"xml_response": response.text}

    async def get_orders(self, status: Optional[str] = None, page: int = 0, size: int = 100) -> dict:
        """Siparişleri çek."""
        status_filter = f"<status>{status}</status>" if status else ""
        body_content = f"""
         <searchData>
            {status_filter}
         </searchData>
         <pagingData>
            <currentPage>{page}</currentPage>
            <pageSize>{size}</pageSize>
         </pagingData>
        """
        body = self._build_soap_envelope("OrderList", body_content)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/OrderService.wsdl",
                headers={"Content-Type": "text/xml; charset=utf-8"},
                content=body,
                timeout=30.0
            )
            response.raise_for_status()
            return {"xml_response": response.text}

    async def update_order_status(self, order_id: str, status: str) -> dict:
        """Sipariş durumu güncelle."""
        body_content = f"""
         <orderRequest>
            <id>{order_id}</id>
         </orderRequest>
        """

        method_map = {
            "shipped": "MakeShipment",
            "delivered": "DeliverDispute",
            "cancelled": "RejectDispute"
        }
        method = method_map.get(status, "DetailOrder")

        body = self._build_soap_envelope(method, body_content)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/OrderService.wsdl",
                headers={"Content-Type": "text/xml; charset=utf-8"},
                content=body,
                timeout=30.0
            )
            response.raise_for_status()
            return {"xml_response": response.text}

    def map_product_to_n11(self, product, category_id: str) -> dict:
        """Ürünü N11 formatına dönüştür."""
        return {
            "sku": product.sku,
            "title": product.title,
            "description": product.description or "",
            "category_id": int(category_id) if category_id else 0,
            "price": product.base_price,
            "stock": product.stock_quantity,
            "image": product.main_image or (product.images[0] if product.images else "")
        }
