"""
Çiçeksepeti Marketplace API - Gerçek Implementasyon
Bu modül Çiçeksepeti'nin resmi API'sini kullanır.
API Dokümantasyonu: https://api.ciceksepeti.com/
"""

import requests
import json
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from urllib.parse import urlencode

class CiceksepetiMarketplaceAPI:
    """Çiçeksepeti Marketplace API Client"""
    
    def __init__(self, api_key: str = None, secret_key: str = None, merchant_id: str = None, sandbox: bool = None):
        # Import here to avoid circular imports
        from config.marketplace_config import get_marketplace_config
        
        # Use provided parameters or load from config
        config = get_marketplace_config('ciceksepeti')
        
        self.api_key = api_key or (config.api_key if config else 'demo_api_key')
        self.secret_key = secret_key or (config.api_secret if config else 'demo_secret_key')
        self.merchant_id = merchant_id or (config.supplier_id if config else 'demo_merchant_id')
        self.sandbox = sandbox if sandbox is not None else (config.sandbox if config else True)
        
        # API Base URLs
        if self.sandbox:
            self.base_url = "https://api-test.ciceksepeti.com/v1"
        else:
            self.base_url = "https://api.ciceksepeti.com/v1"
            
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Ciceksepeti-Python-Client/1.0'
        })
        
        self.logger = logging.getLogger(__name__)

    def _generate_signature(self, method: str, endpoint: str, timestamp: str, 
                           nonce: str, data: str = "") -> str:
        """API imzası oluşturur"""
        # İmza oluşturma string'i
        signature_string = f"{method}\n{endpoint}\n{timestamp}\n{nonce}\n{data}"
        
        # HMAC-SHA256 ile imzala
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            signature_string.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                     params: Optional[Dict] = None) -> Dict:
        """API isteği yapar"""
        url = f"{self.base_url}{endpoint}"
        
        # Timestamp ve nonce oluştur
        timestamp = str(int(datetime.now().timestamp()))
        nonce = hashlib.md5(f"{timestamp}{self.api_key}".encode()).hexdigest()
        
        # JSON data string'i
        json_data = json.dumps(data) if data else ""
        
        # İmza oluştur
        signature = self._generate_signature(method, endpoint, timestamp, nonce, json_data)
        
        # Headers
        headers = {
            'Authorization': f'CS-HMAC-SHA256 ApiKey={self.api_key}, Timestamp={timestamp}, Nonce={nonce}, Signature={signature}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Merchant-Id': self.merchant_id
        }
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response.raise_for_status()
            
            if response.content:
                return response.json()
            else:
                return {"success": True}
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Çiçeksepeti API request failed: {e}")
            if hasattr(e, 'response') and e.response:
                self.logger.error(f"Response: {e.response.text}")
            return {"success": False, "error": str(e)}

    # ÜRÜN YÖNETİMİ
    def create_product(self, product_data: Dict) -> Dict:
        """Yeni ürün oluşturur"""
        endpoint = "/products"
        
        # Çiçeksepeti ürün formatına çevir
        cs_product = {
            "name": product_data.get("name"),
            "description": product_data.get("description"),
            "categoryId": product_data.get("category_id"),
            "brandId": product_data.get("brand_id"),
            "sku": product_data.get("sku"),
            "barcode": product_data.get("barcode"),
            "price": product_data.get("price"),
            "discountPrice": product_data.get("discount_price"),
            "stock": product_data.get("stock", 0),
            "minStock": product_data.get("min_stock", 0),
            "status": product_data.get("status", "active"),  # active, inactive, draft
            "weight": product_data.get("weight", 0),
            "dimensions": {
                "width": product_data.get("width", 0),
                "height": product_data.get("height", 0),
                "depth": product_data.get("depth", 0)
            },
            "images": product_data.get("images", []),
            "attributes": product_data.get("attributes", {}),
            "seoTitle": product_data.get("seo_title"),
            "seoDescription": product_data.get("seo_description"),
            "tags": product_data.get("tags", []),
            "deliveryOptions": {
                "sameDay": product_data.get("same_day_delivery", False),
                "nextDay": product_data.get("next_day_delivery", True),
                "standardDelivery": product_data.get("standard_delivery", True),
                "specialDelivery": product_data.get("special_delivery", False)
            },
            "giftOptions": {
                "giftWrap": product_data.get("gift_wrap", True),
                "giftCard": product_data.get("gift_card", True),
                "personalMessage": product_data.get("personal_message", True)
            }
        }
        
        return self._make_request('POST', endpoint, cs_product)

    def update_product(self, product_id: str, product_data: Dict) -> Dict:
        """Ürün günceller"""
        endpoint = f"/products/{product_id}"
        return self._make_request('PUT', endpoint, product_data)

    def get_product(self, product_id: str) -> Dict:
        """Tek ürün bilgisini getirir"""
        endpoint = f"/products/{product_id}"
        return self._make_request('GET', endpoint)

    def get_products(self, page: int = 1, limit: int = 50, status: str = None,
                    category_id: str = None) -> Dict:
        """Ürün listesini getirir"""
        endpoint = "/products"
        
        params = {
            "page": page,
            "limit": limit
        }
        
        if status:
            params["status"] = status
        if category_id:
            params["categoryId"] = category_id
            
        return self._make_request('GET', endpoint, params=params)

    def delete_product(self, product_id: str) -> Dict:
        """Ürün siler"""
        endpoint = f"/products/{product_id}"
        return self._make_request('DELETE', endpoint)

    def update_stock(self, product_id: str, stock: int) -> Dict:
        """Ürün stoğunu günceller"""
        endpoint = f"/products/{product_id}/stock"
        
        data = {
            "stock": stock,
            "updatedAt": datetime.now().isoformat()
        }
        
        return self._make_request('PUT', endpoint, data)

    def update_price(self, product_id: str, price: float, discount_price: float = None) -> Dict:
        """Ürün fiyatını günceller"""
        endpoint = f"/products/{product_id}/price"
        
        data = {
            "price": price,
            "updatedAt": datetime.now().isoformat()
        }
        
        if discount_price:
            data["discountPrice"] = discount_price
            
        return self._make_request('PUT', endpoint, data)

    # SİPARİŞ YÖNETİMİ
    def get_orders(self, start_date: str = None, end_date: str = None,
                   status: str = None, page: int = 1, limit: int = 50) -> Dict:
        """Sipariş listesini getirir"""
        endpoint = "/orders"
        
        params = {
            "page": page,
            "limit": limit
        }
        
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if status:
            params["status"] = status
            
        return self._make_request('GET', endpoint, params=params)

    def get_order(self, order_id: str) -> Dict:
        """Tek sipariş bilgisini getirir"""
        endpoint = f"/orders/{order_id}"
        return self._make_request('GET', endpoint)

    def update_order_status(self, order_id: str, status: str, 
                           tracking_number: str = None, notes: str = None) -> Dict:
        """Sipariş durumunu günceller"""
        endpoint = f"/orders/{order_id}/status"
        
        data = {
            "status": status,  # preparing, shipped, delivered, cancelled
            "updatedAt": datetime.now().isoformat()
        }
        
        if tracking_number:
            data["trackingNumber"] = tracking_number
        if notes:
            data["notes"] = notes
            
        return self._make_request('PUT', endpoint, data)

    def ship_order(self, order_id: str, tracking_number: str, 
                   cargo_company: str, estimated_delivery: str = None) -> Dict:
        """Siparişi kargoya verir"""
        endpoint = f"/orders/{order_id}/ship"
        
        data = {
            "trackingNumber": tracking_number,
            "cargoCompany": cargo_company,
            "shippedAt": datetime.now().isoformat()
        }
        
        if estimated_delivery:
            data["estimatedDelivery"] = estimated_delivery
            
        return self._make_request('POST', endpoint, data)

    def cancel_order(self, order_id: str, reason: str, refund_amount: float = None) -> Dict:
        """Siparişi iptal eder"""
        endpoint = f"/orders/{order_id}/cancel"
        
        data = {
            "reason": reason,
            "cancelledAt": datetime.now().isoformat()
        }
        
        if refund_amount:
            data["refundAmount"] = refund_amount
            
        return self._make_request('POST', endpoint, data)

    # KATEGORİ YÖNETİMİ
    def get_categories(self, parent_id: str = None) -> Dict:
        """Kategori listesini getirir"""
        endpoint = "/categories"
        
        params = {}
        if parent_id:
            params["parentId"] = parent_id
            
        return self._make_request('GET', endpoint, params=params)

    def get_category(self, category_id: str) -> Dict:
        """Tek kategori bilgisini getirir"""
        endpoint = f"/categories/{category_id}"
        return self._make_request('GET', endpoint)

    def get_category_attributes(self, category_id: str) -> Dict:
        """Kategori özelliklerini getirir"""
        endpoint = f"/categories/{category_id}/attributes"
        return self._make_request('GET', endpoint)

    # MARKA YÖNETİMİ
    def get_brands(self, page: int = 1, limit: int = 100) -> Dict:
        """Marka listesini getirir"""
        endpoint = "/brands"
        
        params = {
            "page": page,
            "limit": limit
        }
        
        return self._make_request('GET', endpoint, params=params)

    def get_brand(self, brand_id: str) -> Dict:
        """Tek marka bilgisini getirir"""
        endpoint = f"/brands/{brand_id}"
        return self._make_request('GET', endpoint)

    def search_brands(self, query: str) -> Dict:
        """Marka arar"""
        endpoint = "/brands/search"
        params = {"q": query}
        return self._make_request('GET', endpoint, params=params)

    # KARGO YÖNETİMİ
    def get_cargo_companies(self) -> Dict:
        """Kargo firmalarını listeler"""
        endpoint = "/cargo/companies"
        return self._make_request('GET', endpoint)

    def get_delivery_options(self, city_code: str = None) -> Dict:
        """Teslimat seçeneklerini getirir"""
        endpoint = "/delivery/options"
        
        params = {}
        if city_code:
            params["cityCode"] = city_code
            
        return self._make_request('GET', endpoint, params=params)

    def calculate_shipping_cost(self, product_id: str, city_code: str, 
                               delivery_type: str = "standard") -> Dict:
        """Kargo ücreti hesaplar"""
        endpoint = "/shipping/calculate"
        
        data = {
            "productId": product_id,
            "cityCode": city_code,
            "deliveryType": delivery_type
        }
        
        return self._make_request('POST', endpoint, data)

    # KAMPANYA VE PROMOSYON YÖNETİMİ
    def get_campaigns(self, active_only: bool = True) -> Dict:
        """Kampanya listesini getirir"""
        endpoint = "/campaigns"
        
        params = {}
        if active_only:
            params["status"] = "active"
            
        return self._make_request('GET', endpoint, params=params)

    def create_discount(self, discount_data: Dict) -> Dict:
        """İndirim oluşturur"""
        endpoint = "/discounts"
        
        cs_discount = {
            "name": discount_data.get("name"),
            "description": discount_data.get("description"),
            "type": discount_data.get("type", "percentage"),  # percentage, fixed
            "value": discount_data.get("value"),
            "minOrderAmount": discount_data.get("min_order_amount", 0),
            "maxDiscountAmount": discount_data.get("max_discount_amount"),
            "startDate": discount_data.get("start_date"),
            "endDate": discount_data.get("end_date"),
            "productIds": discount_data.get("product_ids", []),
            "categoryIds": discount_data.get("category_ids", []),
            "usageLimit": discount_data.get("usage_limit"),
            "status": discount_data.get("status", "active")
        }
        
        return self._make_request('POST', endpoint, cs_discount)

    # ÖZEL GÜN YÖNETİMİ
    def get_special_occasions(self) -> Dict:
        """Özel günler listesini getirir"""
        endpoint = "/occasions"
        return self._make_request('GET', endpoint)

    def create_occasion_product(self, occasion_data: Dict) -> Dict:
        """Özel gün ürünü oluşturur"""
        endpoint = "/occasions/products"
        
        cs_occasion = {
            "productId": occasion_data.get("product_id"),
            "occasionId": occasion_data.get("occasion_id"),
            "specialPrice": occasion_data.get("special_price"),
            "availableFrom": occasion_data.get("available_from"),
            "availableTo": occasion_data.get("available_to"),
            "deliveryDates": occasion_data.get("delivery_dates", []),
            "giftMessage": occasion_data.get("gift_message", True),
            "giftWrap": occasion_data.get("gift_wrap", True)
        }
        
        return self._make_request('POST', endpoint, cs_occasion)

    # STOK VE ENVANTER
    def get_stock_movements(self, product_id: str = None, start_date: str = None,
                           end_date: str = None) -> Dict:
        """Stok hareketlerini getirir"""
        endpoint = "/stock/movements"
        
        params = {}
        if product_id:
            params["productId"] = product_id
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
            
        return self._make_request('GET', endpoint, params=params)

    def bulk_update_stock(self, stock_updates: List[Dict]) -> Dict:
        """Toplu stok güncelleme"""
        endpoint = "/stock/bulk-update"
        
        data = {
            "updates": stock_updates,
            "updatedAt": datetime.now().isoformat()
        }
        
        return self._make_request('POST', endpoint, data)

    # RAPORLAMA
    def get_sales_report(self, start_date: str, end_date: str, 
                        group_by: str = "day") -> Dict:
        """Satış raporu getirir"""
        endpoint = "/reports/sales"
        
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "groupBy": group_by  # day, week, month
        }
        
        return self._make_request('GET', endpoint, params=params)

    def get_product_performance(self, product_id: str, start_date: str, 
                               end_date: str) -> Dict:
        """Ürün performans raporu getirir"""
        endpoint = f"/reports/products/{product_id}/performance"
        
        params = {
            "startDate": start_date,
            "endDate": end_date
        }
        
        return self._make_request('GET', endpoint, params=params)

    def get_inventory_report(self) -> Dict:
        """Envanter raporu getirir"""
        endpoint = "/reports/inventory"
        return self._make_request('GET', endpoint)

    # MÜŞTERİ YÖNETİMİ
    def get_customers(self, page: int = 1, limit: int = 50) -> Dict:
        """Müşteri listesini getirir"""
        endpoint = "/customers"
        
        params = {
            "page": page,
            "limit": limit
        }
        
        return self._make_request('GET', endpoint, params=params)

    def get_customer(self, customer_id: str) -> Dict:
        """Tek müşteri bilgisini getirir"""
        endpoint = f"/customers/{customer_id}"
        return self._make_request('GET', endpoint)

    def get_customer_orders(self, customer_id: str) -> Dict:
        """Müşteri siparişlerini getirir"""
        endpoint = f"/customers/{customer_id}/orders"
        return self._make_request('GET', endpoint)

    # TEST FONKSİYONLARI
    def test_connection(self) -> Dict:
        """API bağlantısını test eder"""
        try:
            result = self.get_categories()
            if "categories" in result or result.get("success", True):
                return {
                    "success": True,
                    "message": "Çiçeksepeti API bağlantısı başarılı",
                    "api_key": self.api_key[:8] + "...",
                    "merchant_id": self.merchant_id,
                    "sandbox": self.sandbox
                }
            else:
                return {
                    "success": False,
                    "message": "API yanıtı beklenmedik format",
                    "response": result
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Çiçeksepeti API bağlantı hatası: {str(e)}"
            }

    def format_cs_datetime(self, dt: datetime) -> str:
        """Datetime'ı Çiçeksepeti API formatına çevirir"""
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    # YARDIMCI FONKSİYONLAR
    def validate_product_data(self, product_data: Dict) -> List[str]:
        """Ürün verilerini doğrular"""
        errors = []
        
        required_fields = ["name", "description", "category_id", "price", "sku"]
        for field in required_fields:
            if field not in product_data or not product_data[field]:
                errors.append(f"Gerekli alan eksik: {field}")
        
        if "price" in product_data and product_data["price"] <= 0:
            errors.append("Fiyat 0'dan büyük olmalı")
            
        if "stock" in product_data and product_data["stock"] < 0:
            errors.append("Stok negatif olamaz")
            
        return errors

    def get_occasion_by_date(self, date: str) -> Dict:
        """Tarihe göre özel günleri getirir"""
        occasions = self.get_special_occasions()
        
        if "occasions" in occasions:
            for occasion in occasions["occasions"]:
                if occasion.get("date") == date:
                    return occasion
                    
        return {"message": "Bu tarihte özel gün bulunamadı"}


# Örnek kullanım ve test fonksiyonları
def test_ciceksepeti_api():
    """Çiçeksepeti API'sini test eder"""
    
    # Test credentials (gerçek projede environment variable'lardan alınmalı)
    api_key = "YOUR_API_KEY"
    secret_key = "YOUR_SECRET_KEY"
    merchant_id = "YOUR_MERCHANT_ID"
    
    # API client oluştur
    cs = CiceksepetiMarketplaceAPI(
        api_key=api_key,
        secret_key=secret_key,
        merchant_id=merchant_id,
        sandbox=True
    )
    
    print("🔄 Çiçeksepeti API Bağlantı Testi...")
    connection_test = cs.test_connection()
    print(f"Bağlantı: {'✅ Başarılı' if connection_test['success'] else '❌ Başarısız'}")
    
    if connection_test['success']:
        print("\n📋 Kategori Listesi Testi...")
        categories = cs.get_categories()
        print(f"Kategori listesi alındı: {'✅' if 'categories' in categories else '❌'}")
        
        print("\n📦 Ürün Listesi Testi...")
        products = cs.get_products(limit=10)
        print(f"Ürün listesi alındı: {'✅' if 'products' in products else '❌'}")
        
        print("\n🏷️ Marka Listesi Testi...")
        brands = cs.get_brands(limit=10)
        print(f"Marka listesi alındı: {'✅' if 'brands' in brands else '❌'}")
        
        print("\n📋 Sipariş Listesi Testi...")
        orders = cs.get_orders(limit=10)
        print(f"Sipariş listesi alındı: {'✅' if 'orders' in orders else '❌'}")
        
        print("\n🎉 Özel Günler Testi...")
        occasions = cs.get_special_occasions()
        print(f"Özel günler alındı: {'✅' if 'occasions' in occasions else '❌'}")
        
        print("\n🚚 Kargo Firmaları Testi...")
        cargo_companies = cs.get_cargo_companies()
        print(f"Kargo firmaları alındı: {'✅' if 'companies' in cargo_companies else '❌'}")


if __name__ == "__main__":
    test_ciceksepeti_api()