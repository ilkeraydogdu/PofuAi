"""
Trendyol Marketplace API - Gerçek Implementasyon
Bu modül Trendyol'un resmi Marketplace API'sini kullanır.
API Dokümantasyonu: https://developers.trendyol.com/
"""

import requests
import json
import base64
import hashlib
import hmac
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class TrendyolMarketplaceAPI:
    """Trendyol Marketplace API Client"""
    
    def __init__(self, api_key: str, api_secret: str, supplier_id: str, sandbox: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.supplier_id = supplier_id
        self.sandbox = sandbox
        
        # API Base URLs
        if sandbox:
            self.base_url = "https://api.trendyol.com/sapigw"
        else:
            self.base_url = "https://api.trendyol.com/sapigw"  # Production URL aynı
            
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.session.auth = (self.api_key, self.api_secret)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'TrendyolMarketplace-Python-Client/1.0'
        })
        
        self.logger = logging.getLogger(__name__)

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, max_retries: int = 3) -> Dict:
        """API isteği yapar - gelişmiş hata yönetimi ile"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(max_retries):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, params=data, timeout=30)
                elif method.upper() == 'POST':
                    response = self.session.post(url, json=data, timeout=30)
                elif method.upper() == 'PUT':
                    response = self.session.put(url, json=data, timeout=30)
                elif method.upper() == 'DELETE':
                    response = self.session.delete(url, timeout=30)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                    
                response.raise_for_status()
                
                # JSON parse kontrolü
                try:
                    return response.json()
                except json.JSONDecodeError:
                    self.logger.warning(f"Invalid JSON response from Trendyol API: {response.text[:200]}")
                    return {"success": False, "error": "Invalid JSON response"}
                    
            except requests.exceptions.Timeout:
                self.logger.warning(f"Trendyol API timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                return {"success": False, "error": "Request timeout"}
                
            except requests.exceptions.ConnectionError:
                self.logger.warning(f"Trendyol API connection error (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return {"success": False, "error": "Connection error"}
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit
                    self.logger.warning(f"Trendyol API rate limit hit (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(5)  # Wait longer for rate limits
                        continue
                elif e.response.status_code >= 500:  # Server errors
                    self.logger.warning(f"Trendyol API server error {e.response.status_code} (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                
                self.logger.error(f"Trendyol API HTTP error: {e}")
                return {
                    "success": False, 
                    "error": f"HTTP {e.response.status_code}: {e.response.text[:200] if e.response else str(e)}"
                }
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Trendyol API request failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return {"success": False, "error": str(e)}
                
        return {"success": False, "error": "Max retries exceeded"}

    # ÜRÜN YÖNETİMİ
    def create_product(self, product_data: Dict) -> Dict:
        """Yeni ürün oluşturur"""
        endpoint = f"/suppliers/{self.supplier_id}/products"
        
        # Ürün verilerini Trendyol formatına çevir
        trendyol_product = {
            "items": [{
                "barcode": product_data.get("barcode"),
                "title": product_data.get("title"),
                "productMainId": product_data.get("product_main_id"),
                "brandId": product_data.get("brand_id"),
                "categoryId": product_data.get("category_id"),
                "quantity": product_data.get("quantity", 0),
                "stockCode": product_data.get("stock_code"),
                "dimensionalWeight": product_data.get("dimensional_weight", 0),
                "description": product_data.get("description"),
                "currencyType": product_data.get("currency_type", "TRY"),
                "listPrice": product_data.get("list_price"),
                "salePrice": product_data.get("sale_price"),
                "vatRate": product_data.get("vat_rate", 18),
                "cargoCompanyId": product_data.get("cargo_company_id", 10),
                "images": product_data.get("images", []),
                "attributes": product_data.get("attributes", [])
            }]
        }
        
        return self._make_request('POST', endpoint, trendyol_product)

    def update_product(self, product_data: Dict) -> Dict:
        """Ürün bilgilerini günceller"""
        endpoint = f"/suppliers/{self.supplier_id}/products"
        return self._make_request('POST', endpoint, product_data)

    def get_products(self, page: int = 0, size: int = 50) -> Dict:
        """Ürün listesini getirir"""
        endpoint = f"/suppliers/{self.supplier_id}/products"
        params = {"page": page, "size": size}
        return self._make_request('GET', endpoint, params)

    def get_product(self, barcode: str) -> Dict:
        """Tek ürün bilgisini getirir"""
        endpoint = f"/suppliers/{self.supplier_id}/products"
        params = {"barcode": barcode}
        return self._make_request('GET', endpoint, params)

    def update_stock_price(self, items: List[Dict]) -> Dict:
        """Stok ve fiyat günceller"""
        endpoint = f"/suppliers/{self.supplier_id}/products/price-and-inventory"
        
        data = {"items": items}
        return self._make_request('POST', endpoint, data)

    # SİPARİŞ YÖNETİMİ
    def get_orders(self, start_date: str = None, end_date: str = None, 
                   page: int = 0, size: int = 50, status: str = None) -> Dict:
        """Sipariş listesini getirir"""
        endpoint = f"/suppliers/{self.supplier_id}/orders"
        
        params = {
            "page": page,
            "size": size
        }
        
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if status:
            params["status"] = status
            
        return self._make_request('GET', endpoint, params)

    def get_order(self, order_number: str) -> Dict:
        """Tek sipariş bilgisini getirir"""
        endpoint = f"/suppliers/{self.supplier_id}/orders/{order_number}"
        return self._make_request('GET', endpoint)

    def update_order_status(self, order_number: str, status: str, 
                           tracking_number: str = None, invoice_number: str = None) -> Dict:
        """Sipariş durumunu günceller"""
        endpoint = f"/suppliers/{self.supplier_id}/orders/{order_number}/status"
        
        data = {"status": status}
        if tracking_number:
            data["trackingNumber"] = tracking_number
        if invoice_number:
            data["invoiceNumber"] = invoice_number
            
        return self._make_request('PUT', endpoint, data)

    def ship_order(self, order_number: str, tracking_number: str, 
                   cargo_company_id: int, invoice_number: str = None) -> Dict:
        """Siparişi kargoya verir"""
        endpoint = f"/suppliers/{self.supplier_id}/orders/{order_number}/ship"
        
        data = {
            "trackingNumber": tracking_number,
            "cargoCompanyId": cargo_company_id
        }
        
        if invoice_number:
            data["invoiceNumber"] = invoice_number
            
        return self._make_request('POST', endpoint, data)

    # KARGO YÖNETİMİ
    def get_cargo_companies(self) -> Dict:
        """Kargo firmalarını listeler"""
        endpoint = "/cargo-companies"
        return self._make_request('GET', endpoint)

    def get_shipment_packages(self, order_number: str) -> Dict:
        """Sipariş paket bilgilerini getirir"""
        endpoint = f"/suppliers/{self.supplier_id}/orders/{order_number}/shipment-packages"
        return self._make_request('GET', endpoint)

    # KATEGORİ VE MARKA
    def get_categories(self) -> Dict:
        """Kategori listesini getirir"""
        endpoint = "/product-categories"
        return self._make_request('GET', endpoint)

    def get_category_attributes(self, category_id: int) -> Dict:
        """Kategori özelliklerini getirir"""
        endpoint = f"/product-categories/{category_id}/attributes"
        return self._make_request('GET', endpoint)

    def get_brands(self) -> Dict:
        """Marka listesini getirir"""
        endpoint = "/brands"
        return self._make_request('GET', endpoint)

    def get_brand_by_name(self, name: str) -> Dict:
        """İsme göre marka arar"""
        endpoint = f"/brands/by-name"
        params = {"name": name}
        return self._make_request('GET', endpoint, params)

    # BATCH İŞLEMLER
    def check_batch_request_result(self, batch_request_id: str) -> Dict:
        """Batch işlem sonucunu kontrol eder"""
        endpoint = f"/suppliers/{self.supplier_id}/products/batch-requests/{batch_request_id}"
        return self._make_request('GET', endpoint)

    # WEBHOOK
    def get_webhook_url(self) -> Dict:
        """Webhook URL'ini getirir"""
        endpoint = f"/suppliers/{self.supplier_id}/webhook-url"
        return self._make_request('GET', endpoint)

    def set_webhook_url(self, webhook_url: str) -> Dict:
        """Webhook URL'ini ayarlar"""
        endpoint = f"/suppliers/{self.supplier_id}/webhook-url"
        data = {"url": webhook_url}
        return self._make_request('POST', endpoint, data)

    # RAPORLAMA
    def get_settlement_report(self, start_date: str, end_date: str) -> Dict:
        """Ödeme raporu getirir"""
        endpoint = f"/suppliers/{self.supplier_id}/finance/settlement-reports"
        params = {
            "startDate": start_date,
            "endDate": end_date
        }
        return self._make_request('GET', endpoint, params)

    def get_returns(self, start_date: str = None, end_date: str = None, 
                    page: int = 0, size: int = 50) -> Dict:
        """İade listesini getirir"""
        endpoint = f"/suppliers/{self.supplier_id}/returns"
        
        params = {"page": page, "size": size}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
            
        return self._make_request('GET', endpoint, params)

    # TEST FONKSİYONLARI
    def test_connection(self) -> Dict:
        """API bağlantısını test eder"""
        try:
            result = self.get_categories()
            if "categoryId" in str(result):
                return {
                    "success": True,
                    "message": "Trendyol API bağlantısı başarılı",
                    "api_key": self.api_key[:8] + "...",
                    "supplier_id": self.supplier_id,
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
                "message": f"Trendyol API bağlantı hatası: {str(e)}"
            }

    def get_supplier_info(self) -> Dict:
        """Satıcı bilgilerini getirir"""
        endpoint = f"/suppliers/{self.supplier_id}"
        return self._make_request('GET', endpoint)


# Örnek kullanım ve test fonksiyonları
def test_trendyol_api():
    """Trendyol API'sini test eder"""
    
    # Test credentials (gerçek projede environment variable'lardan alınmalı)
    api_key = "YOUR_API_KEY"
    api_secret = "YOUR_API_SECRET"
    supplier_id = "YOUR_SUPPLIER_ID"
    
    # API client oluştur
    trendyol = TrendyolMarketplaceAPI(
        api_key=api_key,
        api_secret=api_secret,
        supplier_id=supplier_id,
        sandbox=True
    )
    
    print("🔄 Trendyol API Bağlantı Testi...")
    connection_test = trendyol.test_connection()
    print(f"Bağlantı: {'✅ Başarılı' if connection_test['success'] else '❌ Başarısız'}")
    
    if connection_test['success']:
        print("\n📦 Ürün Listesi Testi...")
        products = trendyol.get_products(page=0, size=10)
        print(f"Ürün sayısı: {len(products.get('content', []))}")
        
        print("\n📋 Kategori Listesi Testi...")
        categories = trendyol.get_categories()
        print(f"Kategori sayısı: {len(categories.get('categoryTree', []))}")
        
        print("\n🏷️ Marka Listesi Testi...")
        brands = trendyol.get_brands()
        print(f"Marka sayısı: {len(brands.get('brands', []))}")
        
        print("\n📦 Sipariş Listesi Testi...")
        orders = trendyol.get_orders(page=0, size=10)
        print(f"Sipariş sayısı: {len(orders.get('content', []))}")


if __name__ == "__main__":
    test_trendyol_api()