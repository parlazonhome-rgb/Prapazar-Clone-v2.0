"""PTT AVM API servisi."""
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx

from app.core.config import get_settings
from app.models.store import Store

settings = get_settings()


class PttAvmService:
    """PTT AVM API entegrasyon servisi (SOAP tabanlı)."""

    def __init__(self, store: Store):
        self.store = store
        self.username = store.api_key  # API Kullanıcı Adı
        self.password = store.api_secret  # API Şifre
        self.shop_id = store.seller_id  # Mağaza Kodu
        self.base_url = store.base_url or "https://ws.pttavm.com:93/service.svc"

    def _build_soap_envelope(self, method: str, body_content: str) -> str:
        """SOAP envelope oluştur."""
        return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema"
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <{method} xmlns="http://tempuri.org/">
      <userName>{self.username}</userName>
      <password>{self.password}</password>
      {body_content}
    </{method}>
  </soap:Body>
</soap:Envelope>"""

    async def test_connection(self) -> dict:
        """API bağlantısını test et."""
        try:
            body = self._build_soap_envelope("GetUserInfo", "")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Content-Type": "text/xml; charset=utf-8",
                        "SOAPAction": "http://tempuri.org/GetUserInfo"
                    },
                    content=body,
                    timeout=30.0
                )

                if response.status_code == 200 and "fault" not in response.text.lower():
                    return {
                        "success": True,
                        "message": "PTT AVM API bağlantısı başarılı",
                        "store_info": {"shop_id": self.shop_id}
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

    async def get_products(self, page: int = 0, size: int = 100) -> dict:
        """Ürünleri listele."""
        body_content = f"""
      <shopId>{self.shop_id}</shopId>
      <start>{page * size}</start>
      <end>{(page + 1) * size}</end>
        """
        body = self._build_soap_envelope("GetProducts", body_content)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers={
                    "Content-Type": "text/xml; charset=utf-8",
                    "SOAPAction": "http://tempuri.org/GetProducts"
                },
                content=body,
                timeout=30.0
            )
            response.raise_for_status()
            return {"xml_response": response.text}

    async def create_product(self, product_data: dict) -> dict:
        """Ürün ekle."""
        body_content = f"""
      <shopId>{self.shop_id}</shopId>
      <product>
        <barcode>{product_data.get('barcode', '')}</barcode>
        <productName>{product_data.get('title', '')}</productName>
        <productDescription>{product_data.get('description', '')}</productDescription>
        <price>{product_data.get('price', 0)}</price>
        <stock>{product_data.get('stock', 0)}</stock>
        <currencyType>TL</currencyType>
        <categoryId>{product_data.get('category_id', 0)}</categoryId>
        <brand>{product_data.get('brand', '')}</brand>
        <images>
          <image>{product_data.get('image', '')}</image>
        </images>
      </product>
        """
        body = self._build_soap_envelope("SaveProduct", body_content)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers={
                    "Content-Type": "text/xml; charset=utf-8",
                    "SOAPAction": "http://tempuri.org/SaveProduct"
                },
                content=body,
                timeout=30.0
            )
            response.raise_for_status()
            return {"xml_response": response.text}

    async def update_stock_and_price(
        self,
        barcode: str,
        quantity: int,
        price: float
    ) -> dict:
        """Stok ve fiyat güncelle."""
        body_content = f"""
      <shopId>{self.shop_id}</shopId>
      <barcode>{barcode}</barcode>
      <stock>{quantity}</stock>
      <price>{price}</price>
        """
        body = self._build_soap_envelope("UpdateProduct", body_content)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers={
                    "Content-Type": "text/xml; charset=utf-8",
                    "SOAPAction": "http://tempuri.org/UpdateProduct"
                },
                content=body,
                timeout=30.0
            )
            response.raise_for_status()
            return {"xml_response": response.text}

    async def get_orders(
        self,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> dict:
        """Siparişleri çek."""
        body_content = f"""
      <shopId>{self.shop_id}</shopId>
      <status>{status or 'all'}</status>
        """
        if start_date:
            body_content += f"<startDate>{start_date}</startDate>"
        if end_date:
            body_content += f"<endDate>{end_date}</endDate>"

        body = self._build_soap_envelope("GetOrders", body_content)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers={
                    "Content-Type": "text/xml; charset=utf-8",
                    "SOAPAction": "http://tempuri.org/GetOrders"
                },
                content=body,
                timeout=30.0
            )
            response.raise_for_status()
            return {"xml_response": response.text}

    async def update_tracking_number(
        self,
        order_id: str,
        cargo_company: str,
        tracking_number: str
    ) -> dict:
        """Kargo takip numarası gönder."""
        body_content = f"""
      <shopId>{self.shop_id}</shopId>
      <orderId>{order_id}</orderId>
      <cargoCompany>{cargo_company}</cargoCompany>
      <trackingNumber>{tracking_number}</trackingNumber>
        """
        body = self._build_soap_envelope("UpdateOrderStatus", body_content)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers={
                    "Content-Type": "text/xml; charset=utf-8",
                    "SOAPAction": "http://tempuri.org/UpdateOrderStatus"
                },
                content=body,
                timeout=30.0
            )
            response.raise_for_status()
            return {"xml_response": response.text}

    async def cancel_order(self, order_id: str, reason: str = "") -> dict:
        """Sipariş iptal et."""
        body_content = f"""
      <shopId>{self.shop_id}</shopId>
      <orderId>{order_id}</orderId>
      <reason>{reason or 'Satıcı tarafından iptal edildi'}</reason>
        """
        body = self._build_soap_envelope("CancelOrder", body_content)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers={
                    "Content-Type": "text/xml; charset=utf-8",
                    "SOAPAction": "http://tempuri.org/CancelOrder"
                },
                content=body,
                timeout=30.0
            )
            response.raise_for_status()
            return {"xml_response": response.text}

    def map_product_to_pttavm(self, product, category_id: str) -> dict:
        """Ürünü PTT AVM formatına dönüştür."""
        return {
            "barcode": product.barcode or product.sku,
            "title": product.title,
            "description": product.description or "",
            "price": product.base_price,
            "stock": product.stock_quantity,
            "category_id": category_id,
            "brand": product.brand or "",
            "image": product.main_image or (product.images[0] if product.images else "")
        }
